"""Fit the simulator's nuisance parameters to the ERP CORE flanker (ERN) task.

Data: Kappenman et al. (2021) ERP CORE, NeuroImage 225:117465, N = 40, OSF.
Downloaded through hu-neuro-pipeline's get_erpcore('ERN').

Event codes follow the MNE-BIDS-Pipeline ERP CORE configuration:
  stimulus 11/12 = compatible (congruent) left/right, 21/22 = incompatible left/right
  response 111, 121, 212, 222 = correct; 112, 122, 211, 221 = incorrect
The fit asserts behavioural sanity (accuracy, congruency effects); if the mapping
were wrong, those checks fail loudly instead of producing a silently bad simulator.

Validation: 5-fold cross-validation over participants. Each fold's parameters are fitted
without that fold's participants, then simulated participants are compared with them; every
real participant is held out exactly once. The final parameters are fitted on all 40.
(An earlier contiguous split, 1-30 vs 31-40, failed on the congruency effect because the two
ID ranges differ; see PREREGISTRATION.md, deviations log.)
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from ..design import Design
from ..mechanisms import EDGES, Mechanism
from ..params import FITTED_PATH, TRIALS_PATH, SimParams
from ..simulator import generate

STIM_CONGRUENT = {11: 1, 12: 1, 21: 0, 22: 0}
RESP_CORRECT = {111: 1, 121: 1, 212: 1, 222: 1, 112: 0, 122: 0, 211: 0, 221: 0}
MAX_RT_S = 1.5
THETA_BAND = (4.0, 8.0)
THETA_WIN_S = (0.0, 0.6)
BLINK_WIN_S = (-0.2, 0.8)
BLINK_UV = 100e-6
N_FOLDS = 5
FOLD_SEED = 20261025


def _pick(raw, wanted: list[str]) -> str | None:
    lower = {c.lower(): c for c in raw.ch_names}
    for w in wanted:
        if w.lower() in lower:
            return lower[w.lower()]
    return None


def subject_trials(set_file: str, events_file: str, subject: str) -> pd.DataFrame:
    import mne
    from scipy.signal import hilbert

    ev = pd.read_csv(events_file, sep="\t")
    ev = ev[pd.to_numeric(ev["value"], errors="coerce").notna()].copy()
    ev["value"] = ev["value"].astype(int)
    ev = ev.sort_values("onset").reset_index(drop=True)

    trials = []
    for i, r in ev.iterrows():
        if r["value"] not in STIM_CONGRUENT:
            continue
        rt, correct = np.nan, np.nan
        for j in range(i + 1, len(ev)):
            v, t = ev.at[j, "value"], ev.at[j, "onset"]
            if v in STIM_CONGRUENT or t - r["onset"] > MAX_RT_S:
                break
            if v in RESP_CORRECT:
                rt, correct = (t - r["onset"]) * 1000.0, float(RESP_CORRECT[v])
                break
        trials.append({"onset": float(r["onset"]), "congruent": STIM_CONGRUENT[r["value"]],
                       "rt": rt, "correct": correct})
    df = pd.DataFrame(trials)
    df["trial"] = np.arange(len(df))
    df["subject"] = subject

    raw = mne.io.read_raw_eeglab(set_file, preload=True, verbose="error")
    sf = raw.info["sfreq"]
    fcz = _pick(raw, ["FCz", "Cz", "Fz"])
    eog = _pick(raw, ["VEOG_lower", "VEOG", "Fp1", "FP1"])
    if fcz is None or eog is None:
        raise RuntimeError(f"{subject}: missing channels (have {raw.ch_names[:10]}...)")
    th = raw.copy().pick([fcz]).filter(*THETA_BAND, verbose="error").get_data()[0]
    power = np.abs(hilbert(th)) ** 2
    blink_sig = raw.copy().pick([eog]).filter(0.1, 15.0, verbose="error").get_data()[0]
    n = len(power)
    theta, blink = [], []
    for onset in df["onset"]:
        s = int(round(onset * sf))
        a, b = s + int(THETA_WIN_S[0] * sf), s + int(THETA_WIN_S[1] * sf)
        c, d = max(0, s + int(BLINK_WIN_S[0] * sf)), min(n, s + int(BLINK_WIN_S[1] * sf))
        theta.append(float(np.log(power[a:b].mean())) if 0 <= a < b <= n else np.nan)
        seg = blink_sig[c:d]
        blink.append(int(len(seg) > 0 and np.ptp(seg) > BLINK_UV))
    df["theta"] = theta
    df["blink"] = blink
    return df[["subject", "trial", "congruent", "rt", "correct", "theta", "blink"]]


def _logit(p):
    p = np.clip(p, 1e-3, 1 - 1e-3)
    return np.log(p / (1 - p))


def subject_summary(g: pd.DataFrame) -> dict:
    ok = g[(g["correct"] == 1) & g["rt"].notna()]
    nb = g[g["blink"] == 0]
    return {
        "mean_rt": ok["rt"].mean(),
        "cong_effect": ok.loc[ok["congruent"] == 0, "rt"].mean() - ok.loc[ok["congruent"] == 1, "rt"].mean(),
        "accuracy": g["correct"].mean(),
        "blink_rate": g["blink"].mean(),
        "theta_sd_within": nb["theta"].std(),
    }


def fit_params(trials: pd.DataFrame) -> SimParams:
    mus, sigmas, taus, cong, acc_c, acc_i, blink, th_mean, th_sd, gain, miss = ([] for _ in range(11))
    for _, g in trials.groupby("subject"):
        ok = g[(g["correct"] == 1) & g["rt"].notna()]
        c = ok.loc[ok["congruent"] == 1, "rt"].to_numpy()
        m, sd, sk = c.mean(), c.std(ddof=1), stats.skew(c)
        tau = sd * (max(sk, 0.05) / 2.0) ** (1 / 3)
        mus.append(m - tau)
        taus.append(tau)
        sigmas.append(np.sqrt(max(sd ** 2 - tau ** 2, (0.2 * sd) ** 2)))
        cong.append(ok.loc[ok["congruent"] == 0, "rt"].mean() - m)
        resp = g[g["correct"].notna()]
        acc_c.append(_logit(resp.loc[resp["congruent"] == 1, "correct"].mean()))
        acc_i.append(_logit(resp.loc[resp["congruent"] == 0, "correct"].mean()))
        blink.append(_logit(g["blink"].mean()))
        nb, yb = g[g["blink"] == 0]["theta"], g[g["blink"] == 1]["theta"]
        th_mean.append(nb.mean())
        th_sd.append(nb.std())
        if len(yb) >= 5:
            gain.append(yb.mean() - nb.mean())
        miss.append(g["rt"].isna().mean())
    base = SimParams()
    return replace(
        base,
        rt_mu=float(np.mean(mus)), rt_mu_sd=float(np.std(mus, ddof=1)),
        rt_sigma=float(np.median(sigmas)), rt_tau=float(np.median(taus)),
        cong_rt=float(np.mean(cong)), cong_rt_sd=float(np.std(cong, ddof=1)),
        acc_logit=float(np.mean(acc_c)), acc_logit_sd=float(np.std(acc_c, ddof=1)),
        cong_acc_logit=float(np.mean(np.array(acc_i) - np.array(acc_c))),
        theta_sd_between=float(np.std(th_mean, ddof=1)), theta_sd_within=float(np.mean(th_sd)),
        theta_sd_within_sd=float(np.std(th_sd, ddof=1)),
        blink_rate=float(1 / (1 + np.exp(-np.mean(blink)))), blink_logit_sd=float(np.std(blink, ddof=1)),
        blink_theta_gain=float(np.mean(gain)) if gain else base.blink_theta_gain,
        missing_rate=float(np.mean(miss)), source="erpcore-ern",
    )


def sanity(trials: pd.DataFrame) -> list[str]:
    """Behavioural checks that catch a wrong event-code mapping."""
    problems = []
    acc = trials["correct"].mean()
    if not 0.75 <= acc <= 0.99:
        problems.append(f"overall accuracy {acc:.3f} outside 0.75-0.99")
    ok = trials[(trials["correct"] == 1)]
    ce = ok.loc[ok["congruent"] == 0, "rt"].mean() - ok.loc[ok["congruent"] == 1, "rt"].mean()
    if not ce > 10:
        problems.append(f"congruency RT effect {ce:.1f} ms not positive")
    ae = trials.loc[trials["congruent"] == 1, "correct"].mean() - trials.loc[trials["congruent"] == 0, "correct"].mean()
    if not ae > 0:
        problems.append(f"congruency accuracy effect {ae:.3f} not positive")
    return problems


def _simulate_summaries(params: SimParams, held: pd.DataFrame, n_sim: int, seed: int) -> pd.DataFrame:
    n_trials = int(held.groupby("subject").size().median())
    per_cell = int(np.clip(n_trials // 2, 20, 200))
    null = Mechanism("validation", frozenset(), {e: 0.0 for e in EDGES} | {"L->B": 1.0})
    d = Design(["S"], {"L": 0}, "within", "counterbalanced", n_sim, per_cell, True, False)
    d.validate()
    data = generate(d, null, params, np.random.default_rng(seed), "synthetic", id_prefix="v")
    return pd.DataFrame([subject_summary(g) for _, g in data.groupby("subject")])


def compare(real: pd.DataFrame, sim: pd.DataFrame) -> dict:
    checks, passed = {}, True
    for col in real.columns:
        r, s = real[col].dropna(), sim[col].dropna()
        pooled = np.sqrt((r.var(ddof=1) + s.var(ddof=1)) / 2) or 1.0
        d = float((s.mean() - r.mean()) / pooled)
        ks_p = float(stats.ks_2samp(r, s).pvalue)
        ok = abs(d) < 0.5 and ks_p > 0.01
        passed &= ok
        checks[col] = {"real_mean": float(r.mean()), "sim_mean": float(s.mean()), "d": round(d, 3),
                       "ks_p": round(ks_p, 4), "passed": bool(ok)}
    return {"passed": bool(passed), "checks": checks}


def validate_cv(trials: pd.DataFrame, n_sim_per_fold: int = 96, return_frames: bool = False):
    """5-fold CV posterior-predictive check over participants."""
    subjects = np.array(sorted(trials["subject"].unique()))
    folds = np.array_split(np.random.default_rng(FOLD_SEED).permutation(subjects), N_FOLDS)
    reals, sims = [], []
    for k, held_ids in enumerate(folds):
        train = trials[~trials["subject"].isin(held_ids)]
        held = trials[trials["subject"].isin(held_ids)]
        reals.append(pd.DataFrame([subject_summary(g) for _, g in held.groupby("subject")]))
        sims.append(_simulate_summaries(fit_params(train), held, n_sim_per_fold, seed=k + 1))
    real_all, sim_all = pd.concat(reals, ignore_index=True), pd.concat(sims, ignore_index=True)
    if return_frames:
        return real_all, sim_all
    out = compare(real_all, sim_all)
    out.update({"method": f"{N_FOLDS}-fold cross-validation over participants",
                "folds": [sorted(map(str, f)) for f in folds],
                "n_heldout": int(len(subjects)), "n_sim_participants": int(n_sim_per_fold * N_FOLDS),
                "criteria": "|d| < 0.5 and KS p > 0.01 for every summary"})
    return out


def validate(params: SimParams, held: pd.DataFrame, n_sim: int = 96, seed: int = 1) -> dict:
    """Single-split check (kept for the deviations log; the gate uses validate_cv)."""
    real = pd.DataFrame([subject_summary(g) for _, g in held.groupby("subject")])
    # Match the real session length: two null "cells" of half the real trial count each.
    n_trials = int(held.groupby("subject").size().median())
    per_cell = int(np.clip(n_trials // 2, 20, 200))
    null = Mechanism("validation", frozenset(), {e: 0.0 for e in EDGES} | {"L->B": 1.0})
    rng = np.random.default_rng(seed)
    d = Design(["S"], {"L": 0}, "within", "counterbalanced", n_sim, per_cell, True, False)
    d.validate()
    data = generate(d, null, params, rng, "synthetic", id_prefix="v")
    sims = [subject_summary(g) for _, g in data.groupby("subject")]
    sim = pd.DataFrame(sims)
    checks, passed = {}, True
    for col in real.columns:
        r, s = real[col].dropna(), sim[col].dropna()
        pooled = np.sqrt((r.var(ddof=1) + s.var(ddof=1)) / 2) or 1.0
        d = float((s.mean() - r.mean()) / pooled)
        ks_p = float(stats.ks_2samp(r, s).pvalue)
        ok = abs(d) < 0.5 and ks_p > 0.01
        passed &= ok
        checks[col] = {"real_mean": float(r.mean()), "sim_mean": float(s.mean()), "d": round(d, 3),
                       "ks_p": round(ks_p, 4), "passed": bool(ok)}
    return {"passed": bool(passed), "n_heldout": int(len(real)), "n_sim_participants": int(len(sim)),
            "criteria": "|d| < 0.5 and KS p > 0.01 for every summary", "checks": checks}


def run(n_participants: int = 40, out_params: Path = FITTED_PATH, out_trials: Path = TRIALS_PATH) -> dict:
    from pipeline.datasets import get_erpcore

    files = get_erpcore("ERN", participants=n_participants)
    frames = []
    for set_file, log_file in zip(sorted(files["raw_files"]), sorted(files["log_files"])):
        sid = Path(set_file).name.split("_")[0]
        frames.append(subject_trials(set_file, log_file, sid))
    trials = pd.concat(frames, ignore_index=True)
    problems = sanity(trials)
    if problems:
        raise RuntimeError("ERP CORE sanity checks failed: " + "; ".join(problems))
    subjects = sorted(trials["subject"].unique())
    validation = validate_cv(trials)
    contiguous = validate(fit_params(trials[trials["subject"].isin(subjects[:30])]),
                          trials[trials["subject"].isin(subjects[30:])])
    params = fit_params(trials)  # final parameters use every participant
    params.validation_passed = validation["passed"]
    out_trials.parent.mkdir(parents=True, exist_ok=True)
    trials.to_csv(out_trials, index=False, float_format="%.4f", compression="gzip")
    payload = {
        "source": "erpcore-ern",
        "dataset": "ERP CORE (Kappenman et al., 2021, NeuroImage 225:117465), ERN flanker task",
        "doi": "10.18115/D5JW4R",
        "fit_participants": subjects, "heldout_participants": subjects,
        "params": params.to_json(), "validation": validation,
        "superseded_contiguous_split_validation": {"split": "fit 1-30, held-out 31-40",
                                                   "passed": contiguous["passed"], "checks": contiguous["checks"]},
    }
    out_params.write_text(json.dumps(payload, indent=2))
    return payload
