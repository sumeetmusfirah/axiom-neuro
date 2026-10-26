"""Generate trial-level data for a design under a hidden mechanism.

Two backends share one interface:

* ``synthetic``      every number comes from the parametric model (fitted to ERP CORE).
* ``semisynthetic``  each simulated participant is a real ERP CORE participant: their real
                     RTs, errors, theta and blinks, with the task's known effects injected on top.
                     Real noise, real heterogeneity, real artifacts, known ground truth.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from .design import Design
from .mechanisms import Mechanism, practice_curve
from .params import TRIALS_PATH, SimParams

ACC_PER_MS = 0.01  # 50 ms slower ~ -0.5 on the accuracy logit


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def _logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def _schedule(design: Design, subj_index: int) -> list[dict]:
    """Ordered list of cells (blocks) this participant does."""
    cells = design.cells()
    if design.assignment == "between":
        return [cells[subj_index % len(cells)]]
    if design.order == "fixed" or len(cells) == 1:
        return cells
    k = subj_index % len(cells)
    return cells[k:] + cells[:k]  # cyclic Latin-square rotation


def _skeleton(design: Design, subj_index: int, subject_id: str) -> pd.DataFrame:
    blocks = _schedule(design, subj_index)
    t = design.trials_per_cell
    rows = []
    for b, cell in enumerate(blocks):
        trial = np.arange(t)
        rows.append(pd.DataFrame({
            "subject": subject_id,
            "L": cell["L"],
            "S": cell["S"],
            "block": b,
            "trial": trial,
            "pos": (b + trial / t) / len(blocks),
        }))
    return pd.concat(rows, ignore_index=True)


def _subject_slopes(mech: Mechanism, params: SimParams, rng: np.random.Generator) -> dict:
    frac = params.slope_sd_frac
    return {k: v * (1.0 + frac * rng.standard_normal()) for k, v in mech.effects.items() if k != "L->B"}


def _rt_shift(df: pd.DataFrame, b: dict) -> np.ndarray:
    L, S = df["L"].to_numpy(), df["S"].to_numpy()
    return (
        b["L->Y"] * L
        + b["S->Y"] * S
        + b["SxL->Y"] * S * L
        + b["P->Y"] * practice_curve(df["pos"].to_numpy())
    )


def _blink_prob(base: float, L: np.ndarray, mult: float) -> np.ndarray:
    return np.clip(base * np.where(L == 1, mult, 1.0), 0.0, 0.95)


def _synthetic_subject(df, mech, params, rng):
    n = len(df)
    b = _subject_slopes(mech, params, rng)
    shift = _rt_shift(df, b)
    cong = rng.integers(0, 2, n)
    mu_i = params.rt_mu + params.rt_mu_sd * rng.standard_normal()
    cong_i = params.cong_rt + params.cong_rt_sd * rng.standard_normal()
    rt = (mu_i + cong * cong_i + shift
          + params.rt_sigma * rng.standard_normal(n)
          + rng.exponential(params.rt_tau, n))
    acc_i = params.acc_logit + params.acc_logit_sd * rng.standard_normal()
    correct = (rng.random(n) < _sigmoid(acc_i + cong * params.cong_acc_logit - ACC_PER_MS * shift)).astype(float)
    df = df.assign(congruent=1 - cong, rt=np.round(rt, 1), correct=correct)
    base_blink = float(_sigmoid(_logit(params.blink_rate) + params.blink_logit_sd * rng.standard_normal()))
    theta_i = params.theta_sd_between * rng.standard_normal()
    noise_i = max(0.15, params.theta_sd_within + params.theta_sd_within_sd * rng.standard_normal())
    blink = (rng.random(n) < _blink_prob(base_blink, df["L"].to_numpy(), mech.effects["L->B"])).astype(int)
    theta = (theta_i + b["L->T"] * df["L"].to_numpy()
             + noise_i * rng.standard_normal(n)
             + blink * params.blink_theta_gain)
    return df.assign(theta=theta, blink=blink, _gain=params.blink_theta_gain)


@lru_cache(maxsize=2)
def _real_trials(path: str) -> dict[str, pd.DataFrame]:
    t = pd.read_csv(path)
    out = {}
    for sid, g in t.groupby("subject"):
        g = g.sort_values("trial").reset_index(drop=True)
        ok = g["correct"].eq(1) & g["rt"].notna()
        # Remove each real participant's own drift so practice is only what the task injects.
        if ok.sum() > 10:
            x = g.loc[ok, "trial"].to_numpy(float)
            slope = np.polyfit(x, g.loc[ok, "rt"].to_numpy(float), 1)[0]
            g["rt"] = g["rt"] - slope * (g["trial"] - g["trial"].mean())
        out[str(sid)] = g
    return out


def _semisynthetic_subject(df, mech, params, rng, real: pd.DataFrame):
    n = len(df)
    b = _subject_slopes(mech, params, rng)
    shift = _rt_shift(df, b)
    pick = real.iloc[rng.integers(0, len(real), n)].reset_index(drop=True)
    acc_i = float(np.clip(pick["correct"].mean(), 0.5, 0.995))
    target = _sigmoid(_logit(acc_i) - ACC_PER_MS * shift)
    correct = pick["correct"].to_numpy(float).copy()
    u = rng.random(n)
    down = (target < acc_i) & (correct == 1) & (u < (acc_i - target) / acc_i)
    up = (target > acc_i) & (correct == 0) & (u < (target - acc_i) / (1 - acc_i))
    correct[down], correct[up] = 0.0, 1.0
    correct[pick["rt"].isna().to_numpy()] = np.nan
    blink = pick["blink"].to_numpy(int).copy()
    gain_real = (pick.loc[pick["blink"] == 1, "theta"].mean() - pick.loc[pick["blink"] == 0, "theta"].mean())
    gain = float(gain_real) if np.isfinite(gain_real) else params.blink_theta_gain
    theta = pick["theta"].to_numpy(float) + b["L->T"] * df["L"].to_numpy()
    mult = mech.effects["L->B"]
    if mult != 1.0:
        r = float(np.clip(pick["blink"].mean(), 0.01, 0.95))  # some real participants blink on ~every trial
        q = max(min(r * mult, 0.95) - r, 0.0) / (1 - r)
        add = (df["L"].to_numpy() == 1) & (blink == 0) & (rng.random(n) < q)
        blink[add] = 1
        theta[add] += gain
    return df.assign(
        congruent=pick["congruent"].to_numpy(int),
        rt=np.round(pick["rt"].to_numpy(float) + shift, 1),
        correct=correct, theta=theta, blink=blink, _gain=gain,
    )


def generate(
    design: Design,
    mech: Mechanism,
    params: SimParams,
    rng: np.random.Generator,
    track: str = "synthetic",
    id_prefix: str = "p",
    trials_path: Path = TRIALS_PATH,
) -> pd.DataFrame:
    """Trial-level data for one experiment. Columns the agent never sees start with '_'."""
    real = None
    if track == "semisynthetic":
        if not Path(trials_path).exists():
            raise FileNotFoundError("semisynthetic track needs data/erpcore_trials.csv.gz (run the fit job)")
        real_by_subj = _real_trials(str(trials_path))
        real_ids = list(real_by_subj)
        order = rng.permutation(len(real_ids))
    frames = []
    for i in range(design.n_participants):
        df = _skeleton(design, i, f"{id_prefix}{i:03d}")
        if track == "synthetic":
            df = _synthetic_subject(df, mech, params, rng)
        else:
            real = real_by_subj[real_ids[order[i % len(real_ids)]]]
            df = _semisynthetic_subject(df, mech, params, rng, real)
        miss = rng.random(len(df)) < params.missing_rate
        df.loc[miss, ["rt", "correct"]] = np.nan
        frames.append(df)
    data = pd.concat(frames, ignore_index=True)
    if design.eeg:
        if design.ica:
            data["theta"] = data["theta"] - params.ica_removal * data["blink"] * data["_gain"]
    else:
        data = data.drop(columns=["theta", "blink"])
    return data.drop(columns=["_gain"])
