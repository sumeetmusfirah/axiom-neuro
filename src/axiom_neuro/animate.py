"""Animated episode replays: what the evidence said at each step vs what the agent claimed.

Episodes are replayed deterministically (same task seed, same run seed, same actions),
so the evidence panel is recomputed exactly, never approximated.
"""

from __future__ import annotations

import gzip
import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

from . import analysis as A  # noqa: E402
from . import ledger as L  # noqa: E402
from .env import LabEnv  # noqa: E402
from .figures import BLUE, GRAY, GRID, INK, INK2, ORANGE, SURFACE  # noqa: E402
from .mechanisms import EDGES  # noqa: E402
from .params import REPO, load_params  # noqa: E402
from .tasks import load_tasks  # noqa: E402

OUT = REPO / "site" / "animations"


def replay(row: dict, actions: list[dict]):
    """Yield (step_label, env snapshot data) after each action, re-executing the episode."""
    task = {t.task_id: t for t in load_tasks()}[row["task_id"]]
    env = LabEnv(task, load_params(), row["track"], row["labels"], run_seed=row["seed"])
    frames = [("Pilot data D0", A.ideal_claims(env.collected()), env.remaining, None)]
    for a in actions:
        env.step(a["action"], a["args"])
        text = f"{a['action']}  " + json.dumps(a["args"])[:90]
        frames.append((text, A.ideal_claims(env.collected()), env.remaining, a.get("thought", "")))
        if a["action"] == "submit":
            break
    return task, env, frames


def animate(row: dict, out: Path, actions: list[dict] | None = None) -> Path:
    if actions is None:
        actions = json.loads(gzip.open(REPO / row["transcript"], "rt").read())["actions"]
    task, env, frames = replay(row, actions)
    truth = task.mechanism.truth()
    claims = row["claims"]
    budget = task.budget
    fig = plt.figure(figsize=(9.6, 5.4), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], height_ratios=[1, 0.14], hspace=0.45, wspace=0.28)
    ax_e, ax_log, ax_b = fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, :])
    n_frames = len(frames) + 2  # hold on the verdict

    def draw(k):
        i = min(k, len(frames) - 1)
        label, ev, remaining, thought = frames[i]
        final = k >= len(frames)
        for ax in (ax_e, ax_log, ax_b):
            ax.clear()
            ax.set_facecolor(SURFACE)
        # Evidence panel: ideal-analyst probability that each edge exists, given data so far.
        ys = range(len(EDGES))
        for y, e in zip(ys, EDGES):
            c = ev[e]
            p = c["confidence"] if c["present"] else 1 - c["confidence"]
            ax_e.barh(y, p, height=0.55, color=BLUE if c["identified"] else GRAY, alpha=0.9)
            ax_e.plot(1.0 if truth[e] else 0.0, y, marker="|", ms=16, mew=2.2, color=INK)
            if final:
                cl = claims[e]
                cp = cl["confidence"] if cl["present"] else 1 - cl["confidence"]
                ax_e.plot(cp, y, "D", ms=8, color=ORANGE, mec=SURFACE, mew=1.2)
        ax_e.set_yticks(list(ys), EDGES, color=INK)
        ax_e.invert_yaxis()
        ax_e.set_xlim(0, 1.02)
        ax_e.axvline(0.5, color=GRID, lw=0.8)
        ax_e.set_xlabel("P(edge exists)", color=INK2)
        ax_e.set_title("Evidence (blue)" + (" vs claim (orange)" if final else ""),
                       loc="left", fontsize=10, color=INK, fontweight="bold")
        ax_e.grid(axis="x", color=GRID, lw=0.6)
        for s in ("top", "right", "left"):
            ax_e.spines[s].set_visible(False)
        # Log panel
        ax_log.axis("off")
        ax_log.set_title(row["model"], loc="left", fontsize=10, color=INK, fontweight="bold", pad=16)
        ax_log.text(0, 1.0, f"task {row['task_id']} · {row['track']} track", transform=ax_log.transAxes,
                    fontsize=8.5, color=INK2)
        lines = [f[0] for f in frames[: i + 1]][-9:]
        for j, ln in enumerate(lines):
            ax_log.text(0, 0.88 - j * 0.09, textwrap.shorten(ln, 58), transform=ax_log.transAxes,
                        fontsize=8.5, family="monospace", color=INK if j == len(lines) - 1 else INK2)
        if thought and not final:
            ax_log.text(0, 0.02, "“" + textwrap.shorten(thought, 120) + "”", transform=ax_log.transAxes,
                        fontsize=8.5, style="italic", color=INK2, wrap=True)
        if final:
            s = row["scores"]
            ax_log.text(0, 0.02, f"Verdict: {sum(s['edge_correct'].values())}/6 edges right · Brier {s['brier']:.3f}"
                        + (" · fell for the trap" if s.get("fell_for_trap") else ""),
                        transform=ax_log.transAxes, fontsize=9.5, color=INK, fontweight="bold")
        # Budget bar
        spent = budget - remaining
        ax_b.barh(0, budget, color=GRID, height=0.6)
        ax_b.barh(0, spent, color=BLUE, height=0.6)
        ax_b.set_xlim(0, budget)
        ax_b.set_yticks([])
        ax_b.set_xlabel(f"Budget spent: {spent:.1f} of {budget:.0f} participant-hours", color=INK2, fontsize=9)
        for s in ("top", "right", "left"):
            ax_b.spines[s].set_visible(False)

    fig.text(0.5, 0.005, "Black tick = ground truth (right = edge exists). Grey bar = not identifiable from the data yet.",
             ha="center", fontsize=8, color=INK2)
    anim = FuncAnimation(fig, draw, frames=n_frames, interval=1400)
    out.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out, writer=PillowWriter(fps=0.8))
    plt.close(fig)
    return out


def pick_episodes(rows: list[dict], per_model: int = 1) -> list[dict]:
    """Most instructive episodes: confound tasks, longest action sequences first."""
    llm = [r for r in L.ok_rows(rows) if r["agent"] == "llm" and r.get("transcript")]
    out = []
    for m in sorted({r["model"] for r in llm}):
        mine = [r for r in llm if r["model"] == m and r["task_type"] in ("practice_confound", "blink_artifact")]
        mine.sort(key=lambda r: (-r.get("n_experiments", 0), r["key"]))
        out += mine[:per_model]
    return out


# A careful reference episode on the practice trap. Shown until model episodes exist, and
# labelled as a scripted reference everywhere it appears: the thoughts are the script's, not a model's.
DEMO_SCRIPT = [
    ("order_check", {"dataset": "D0"},
     "The pilot sped up under stimulation. Was the active block always second?"),
    ("design_experiment", {"factors": ["L", "S"], "assignment": "within", "order": "counterbalanced",
                           "n_participants": 24, "trials_per_cell": 80, "eeg": True, "ica": True},
     "Counterbalance the order and cross load with stimulation, with EEG and artifact correction."),
    ("regress", {"datasets": ["D1"], "outcome": "rt", "predictors": ["L", "S", "SxL", "practice"]},
     "Estimate load, stimulation, their interaction and practice together."),
    ("artifact_check", {"dataset": "D1"}, "Check whether any theta effect survives without blinks."),
]


def demo(out: Path | None = None) -> Path | None:
    from .scoring import score
    try:
        task = next(t for t in load_tasks() if t.task_type == "practice_confound")
    except (FileNotFoundError, StopIteration):
        return None
    env = LabEnv(task, load_params(), "synthetic", "named", run_seed=0)
    actions = []
    for name, args, thought in DEMO_SCRIPT:
        env.step(name, args)
        actions.append({"action": name, "args": args, "thought": thought})
    claims = A.ideal_claims(env.collected())
    sub_args = {"edges": {e: {"present": c["present"], "confidence": c["confidence"]} for e, c in claims.items()}}
    env.step("submit", sub_args)
    actions.append({"action": "submit", "args": sub_args, "thought": "Submit what the data support."})
    row = {"task_id": task.task_id, "track": "synthetic", "labels": "named", "seed": 0,
           "model": "scripted reference agent", "claims": env.episode.submitted,
           "scores": score(env.episode.submitted, task.mechanism.truth(), task.task_type)}
    return animate(row, out or OUT / "demo_reference.gif", actions)


def build_all() -> list[str]:
    paths = []
    d = demo()
    if d:
        paths.append(str(d.relative_to(REPO)))
    for r in pick_episodes(L.primary(L.read_rows())):
        if not (REPO / r["transcript"]).exists():
            continue
        p = animate(r, OUT / f"episode_{r['model'].replace(':', '_')}_{r['task_id']}.gif")
        paths.append(str(p.relative_to(REPO)))
    model_paths = [p for p in paths if "demo_reference" not in p]
    if model_paths:  # stable name for the README / project page hero
        import shutil
        shutil.copy(REPO / model_paths[0], OUT / "episode.gif")
    return paths
