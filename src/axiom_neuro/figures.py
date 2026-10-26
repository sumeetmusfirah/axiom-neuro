"""Paper + site figures, computed from the ledger and the ERP CORE fit. Never hand-edited.

Style: thin marks, hairline recessive grid, identity carried by axis labels (not colour)
wherever possible. Two-series figures use the validated pair blue #2a78d6 / orange #eb6834
(adjacent CVD dE 24.7, normal-vision dE 33.6 on the light surface).
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import ledger as L  # noqa: E402
from .config import load_config  # noqa: E402
from .params import FITTED_PATH, REPO, TRIALS_PATH  # noqa: E402

OUT = REPO / "site" / "figures"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#a3a29d"
TRACK_COLOR = {"synthetic": BLUE, "semisynthetic": ORANGE}
TRACK_NAME = {"synthetic": "Synthetic (fitted simulator)", "semisynthetic": "Semi-synthetic (real ERP CORE trials)"}
BASELINES = ("random", "scripted", "oracle")

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "axes.titlelocation": "left", "legend.frameon": False, "xtick.major.size": 0, "ytick.major.size": 0,
})


def _save(fig, name: str) -> list[str]:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("png", "pdf"):
        p = OUT / f"{name}.{ext}"
        fig.savefig(p, dpi=200, bbox_inches="tight")
        paths.append(str(p.relative_to(REPO)))
    plt.close(fig)
    return paths


def _label(r) -> str:
    return r["agent"] if r["agent"] != "llm" else r["model"]


def _boot(values_by_task: dict, n=2000, seed=0):
    v = np.array([np.mean(x) for x in values_by_task.values()])
    if len(v) == 0:
        return np.nan, np.nan, np.nan
    bs = np.random.default_rng(seed).choice(v, (n, len(v))).mean(1)
    return v.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5)


def _cells(rows, metric, labels="named"):
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["labels"] != labels:
            continue
        by[(_label(r), r["track"])][r["task_id"]].append(metric(r))
    return {k: _boot(v) for k, v in by.items()}


def _order(names, cfg):
    llm = [m["name"] for m in cfg["llm"]["models"]]
    return [n for n in [*BASELINES, *llm] if n in names]


def fig_agents(rows, cfg):
    """Primary metric: mean edge Brier score, per agent, both tracks."""
    cells = _cells(rows, lambda r: r["scores"]["brier"])
    if not cells:
        return []
    names = _order({k[0] for k in cells}, cfg)
    fig, ax = plt.subplots(figsize=(6.4, 0.42 * len(names) + 1.3))
    for j, track in enumerate(("synthetic", "semisynthetic")):
        for i, n in enumerate(names):
            if (n, track) not in cells:
                continue
            m, lo, hi = cells[(n, track)]
            y = i + (j - 0.5) * 0.24
            ax.plot([lo, hi], [y, y], color=TRACK_COLOR[track], lw=1.5, solid_capstyle="round")
            ax.plot(m, y, "o", ms=6, color=TRACK_COLOR[track], mec=SURFACE, mew=1.5, label=TRACK_NAME[track])
    n_base = sum(n in BASELINES for n in names)
    if n_base:  # quiet band behind the reference agents
        ax.axhspan(-0.5, n_base - 0.5, color="#f0efec", zorder=0, lw=0)
    ax.set_yticks(range(len(names)), names)
    ax.invert_yaxis()
    ax.set_xlabel("Mean edge Brier score (lower is better), 95% CI over tasks")
    ax.set_title("How well each scientist recovered the hidden mechanism")
    ax.grid(axis="y", visible=False)
    h, l = ax.get_legend_handles_labels()
    keep = dict(zip(l, h))
    ax.legend(keep.values(), keep.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=9)
    return _save(fig, "fig_agents")


def fig_decomposition(rows, cfg):
    """Design vs analysis: the agent's own claims vs the ideal analyst on the agent's own data."""
    own = _cells(rows, lambda r: r["scores"]["brier"])
    ideal = _cells(rows, lambda r: r["ideal_on_own_data"]["brier"])
    names = [n for n in _order({k[0] for k in own}, cfg) if n not in BASELINES]
    if not names:
        return []
    oracle = own.get(("oracle", "synthetic"), (np.nan,))[0]
    fig, ax = plt.subplots(figsize=(6.4, 0.5 * len(names) + 1.4))
    for i, n in enumerate(names):
        a, b = own.get((n, "synthetic"), (np.nan,))[0], ideal.get((n, "synthetic"), (np.nan,))[0]
        ax.plot([b, a], [i, i], color=GRAY, lw=1.5, zorder=1)
        ax.plot(a, i, "o", ms=7, color=BLUE, mec=SURFACE, mew=1.5, zorder=2, label="Model's own claims" if i == 0 else None)
        ax.plot(b, i, "o", ms=7, color=ORANGE, mec=SURFACE, mew=1.5, zorder=2,
                label="Ideal analysis of the model's own data" if i == 0 else None)
    if np.isfinite(oracle):
        ax.axvline(oracle, color=INK2, lw=0.8)
        ax.text(oracle, -0.7, " oracle design + ideal analysis", color=INK2, fontsize=8, va="bottom")
    ax.set_yticks(range(len(names)), names)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Mean edge Brier score, synthetic track (lower is better)")
    ax.set_title("Analysis error (blue to orange) vs design error (orange to the oracle line)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=9)
    return _save(fig, "fig_decomposition")


def fig_traps(rows, cfg):
    """How often each scientist claimed the confounded effect, per confound task."""
    by = defaultdict(list)
    for r in rows:
        if "fell_for_trap" in r["scores"] and r["labels"] == "named" and r["track"] == "synthetic":
            by[(_label(r), r["task_type"])].append(float(r["scores"]["fell_for_trap"]))
    if not by:
        return []
    names = _order({k[0] for k in by}, cfg)
    tasks = [("practice_confound", "Practice confound: claimed stimulation works", BLUE),
             ("blink_artifact", "Blink artifact: claimed load changes theta", ORANGE)]
    fig, ax = plt.subplots(figsize=(6.4, 0.42 * len(names) + 1.3))
    for j, (t, lab, c) in enumerate(tasks):
        for i, n in enumerate(names):
            v = by.get((n, t))
            if v:
                ax.plot(np.mean(v), i + (j - 0.5) * 0.3, "o", ms=6, color=c, mec=SURFACE, mew=1.5,
                        label=lab if i == 0 else None)
    ax.set_xlim(-0.03, 1.03)
    ax.set_yticks(range(len(names)), names)
    ax.set_ylim(len(names) - 0.5, -0.5)  # inverted, with room for the offset markers
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Fraction of episodes that fell for the trap")
    ax.set_title("Falling for planted confounds")
    h, l = ax.get_legend_handles_labels()
    keep = dict(zip(l, h))
    ax.legend(keep.values(), keep.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=1, fontsize=9)
    return _save(fig, "fig_traps")


def fig_scale(rows, cfg):
    sizes = {m["name"]: m["params_b"] for m in cfg["llm"]["models"]}
    cells = _cells(rows, lambda r: r["scores"]["brier"])
    pts = [(sizes[n], *cells[(n, "synthetic")], n) for n in sizes if (n, "synthetic") in cells]
    if len(pts) < 2:
        return []
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    for x, m, lo, hi, n in pts:
        ax.plot([x, x], [lo, hi], color=BLUE, lw=1.5)
        ax.plot(x, m, "o", ms=7, color=BLUE, mec=SURFACE, mew=1.5)
        ax.annotate(n, (x, m), xytext=(6, 0), textcoords="offset points", fontsize=8, color=INK, va="center")
    ax.set_xscale("log")
    x_left = min(p[0] for p in pts) * 0.85
    for name in ("scripted", "random"):
        if (name, "synthetic") in cells:
            v = cells[(name, "synthetic")][0]
            ax.axhline(v, color=INK2, lw=0.8)
            ax.text(x_left, v, f"{name} baseline", fontsize=8, color=INK2, va="bottom")
    ax.set_xlabel("Parameters (billions, log scale)")
    ax.set_ylabel("Mean edge Brier (lower is better)")
    ax.set_title("Does scientific judgement improve with model size?")
    return _save(fig, "fig_scale")


def fig_bio(rows, cfg):
    """Axiom-Bio: the same model with real molecule names vs abstract labels (recall vs inference)."""
    bio = [r for r in rows if r.get("domain") == "bio"]
    if not bio:
        return []
    named = _cells(bio, lambda r: r["scores"]["brier"], labels="named")
    abstract = _cells(bio, lambda r: r["scores"]["brier"], labels="abstract")
    names = _order({k[0] for k in named} | {k[0] for k in abstract}, cfg)
    fig, ax = plt.subplots(figsize=(6.4, 0.45 * len(names) + 1.4))
    for i, n in enumerate(names):
        a = named.get((n, "sachs"))
        b = abstract.get((n, "sachs"))
        if a and b:
            ax.plot([a[0], b[0]], [i, i], color=GRAY, lw=1.5, zorder=1)
        if a:
            ax.plot(a[0], i, "o", ms=7, color=BLUE, mec=SURFACE, mew=1.5, zorder=2, label="Real molecule names")
        if b:
            ax.plot(b[0], i, "o", ms=7, color=ORANGE, mec=SURFACE, mew=1.5, zorder=2, label="Abstract labels (M1-M11)")
    n_base = sum(n in BASELINES for n in names)
    if n_base:
        ax.axhspan(-0.5, n_base - 0.5, color="#f0efec", zorder=0, lw=0)
    ax.axvline(0.25, color=INK2, lw=0.8)
    ax.text(0.25, 0.02, " always 50% (0.25)", color=INK2, fontsize=8, va="bottom",
            transform=ax.get_xaxis_transform())
    ax.set_yticks(range(len(names)), names)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Mean edge Brier score on real Sachs cells (lower is better)")
    ax.set_title("Recall or inference? Blue to orange is what names are worth")
    h, l = ax.get_legend_handles_labels()
    keep = dict(zip(l, h))
    ax.legend(keep.values(), keep.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=9)
    return _save(fig, "fig_bio")


def fig_validation():
    """Simulator vs held-out real ERP CORE participants, on every fitted summary."""
    if not (FITTED_PATH.exists() and TRIALS_PATH.exists()):
        return []
    from .erpcore.fit import validate_cv

    fit = json.loads(FITTED_PATH.read_text())
    real, sim = validate_cv(pd.read_csv(TRIALS_PATH), return_frames=True)
    cols = [("mean_rt", "Mean RT, correct (ms)"), ("cong_effect", "Congruency effect (ms)"),
            ("accuracy", "Accuracy"), ("blink_rate", "Large VEOG deflection rate"), ("theta_sd_within", "Theta SD within")]
    fig, axes = plt.subplots(1, len(cols), figsize=(11, 2.4))
    for ax, (c, title) in zip(axes, cols):
        ax.hist(sim[c].dropna(), bins=18, color=GRAY, alpha=0.55, density=True, label=f"Simulated ({len(sim)})")
        top = ax.get_ylim()[1]
        jitter = np.random.default_rng(0).uniform(0.04, 0.16, len(real)) * top
        ax.plot(real[c], jitter, "o", ms=4.5, color=BLUE, mec=SURFACE, mew=0.8, alpha=0.9,
                label=f"Held-out real ({len(real)}, 5-fold CV)")
        chk = fit["validation"]["checks"].get(c, {})
        ax.set_title(title, fontsize=9)
        ax.text(0.02, 0.92, f"d = {chk.get('d', float('nan')):+.2f}", transform=ax.transAxes, fontsize=8, color=INK2)
        ax.set_yticks([])
        ax.grid(False)
    axes[0].legend(loc="upper center", bbox_to_anchor=(2.9, -0.22), ncol=2, fontsize=9)
    status = "passed" if fit["validation"]["passed"] else "FAILED"
    fig.suptitle(f"The simulator reproduces held-out ERP CORE participants (validation {status})",
                 x=0.06, ha="left", fontsize=11, fontweight="bold", color=INK, y=1.06)
    return _save(fig, "fig_validation")


def _subject_effect(df, factor: str, outcome: str, exclude_blinks: bool = False):
    """Per-participant difference (factor=1 minus factor=0), mean and 95% CI across participants."""
    d = df[df["blink"] == 0] if exclude_blinks else df
    m = d.groupby(["subject", factor])[outcome].mean().unstack()
    diff = (m[1] - m[0]).dropna()
    half = 1.96 * diff.std(ddof=1) / np.sqrt(len(diff))
    return float(diff.mean()), float(half)


def fig_trap_mechanics(rows=None, cfg=None) -> list[str]:
    """How each planted trap works, computed live from the simulator (no ledger needed).

    For each trap task and its mirror: the effect the pilot suggests, and the effect a careful
    experiment recovers. The pilot is identical within a pair; only the truth differs.
    """
    from .env import LabEnv
    from .params import load_params
    from .tasks import load_tasks
    try:
        tasks = load_tasks()
    except FileNotFoundError:
        return []
    params = load_params()
    first = {}
    for t in tasks:
        first.setdefault(t.task_type, t)
    careful_s = {"factors": ["S"], "fixed": {"L": 1}, "assignment": "within", "order": "counterbalanced",
                 "n_participants": 32, "trials_per_cell": 80, "eeg": False, "ica": False}
    careful_l = {"factors": ["L"], "fixed": {"S": 0}, "assignment": "within", "order": "counterbalanced",
                 "n_participants": 32, "trials_per_cell": 80, "eeg": True, "ica": True}
    panels = [
        ("Practice disguised as stimulation", "Speed-up from active stimulation (ms)", "S", "rt", -1,
         [("practice_confound", "truth: no effect"), ("stim_main", "truth: real effect")],
         ("Pilot: active block always second", "Counterbalanced experiment"), careful_s, False),
        ("Blinks disguised as brain activity", "Load effect on frontal theta (a.u.)", "L", "theta", 1,
         [("blink_artifact", "truth: no effect"), ("neural_theta", "truth: real effect")],
         ("Pilot: no artifact correction", "New experiment with ICA"), careful_l, False),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, (title, xlabel, factor, outcome, sign, pair, (lab_a, lab_b), careful, blink) in zip(axes, panels):
        ys, labels = [], []
        for k, (tt, truth_note) in enumerate(pair):
            if tt not in first:
                continue
            env = LabEnv(first[tt], params, "synthetic", "named", run_seed=0)
            pilot = env.collected()[0].data
            if blink:
                est = [_subject_effect(pilot, factor, outcome), _subject_effect(pilot, factor, outcome, True)]
            else:
                env.step("design_experiment", careful)
                est = [_subject_effect(pilot, factor, outcome), _subject_effect(env.collected()[-1].data, factor, outcome)]
            for j, ((m, h), color, lab) in enumerate(zip(est, (GRAY, BLUE), (lab_a, lab_b))):
                y = k * 3 + j
                ax.errorbar(sign * m, y, xerr=h, fmt="o", color=color, ms=7, capsize=0, lw=2)
                ys.append(y)
                labels.append(f"{lab}")
            ax.text(1.0, k * 3 + 0.5, truth_note, transform=ax.get_yaxis_transform(), ha="right", va="center",
                    fontsize=8.5, color=INK2, style="italic")
        ax.axvline(0, color=INK, lw=0.8)
        ax.set_yticks(ys, labels, fontsize=9)
        ax.invert_yaxis()
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.grid(axis="y", visible=False)
    fig.text(0.06, -0.06, "Each panel: the trap task (top pair) and its held-out mirror (bottom pair) open with the same kind of pilot. "
             "Grey = what the pilot shows; blue = what a careful analysis shows. 95% CIs across simulated participants.",
             fontsize=8.5, color=INK2, ha="left", wrap=True)
    fig.tight_layout(w_pad=4)
    return _save(fig, "fig_trap_mechanics")


def build_all() -> list[str]:
    cfg = load_config()
    rows = L.ok_rows(L.primary(L.read_rows()))
    out = []
    for f in (fig_agents, fig_decomposition, fig_traps, fig_scale, fig_bio):
        out += f(rows, cfg)
    out += fig_validation()
    out += fig_trap_mechanics()
    return out
