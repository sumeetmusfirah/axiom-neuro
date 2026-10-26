"""Decide what to run next. Enforces the gates; implements the adaptive stopping rule.

Order of work:
  setup     fit ERP CORE -> precompute oracle -> freeze tasks   (once)
  baselines random / scripted / oracle on every task and track
  llm       every model x track x label, one seed at a time across all tasks;
            seeds keep being added to a cell until its Brier-score 95% CI is tight enough
  waves     once the above is empty: a fresh task wave is frozen on schedule and every
            agent runs on it once (see waves.py)
"""

from __future__ import annotations

import json
import math
from collections import defaultdict

import numpy as np

from . import ledger as L
from . import studies as S
from . import waves as W
from .agents.baselines import ORACLE_CACHE
from .params import FITTED_PATH, load_params
from .tasks import is_frozen, load_tasks


def bio_ready() -> bool:
    from .bio.data import CELLS_PATH, GRAPH_PATH
    from .bio.lab import BIO_MANIFEST
    return CELLS_PATH.exists() and GRAPH_PATH.exists() and BIO_MANIFEST.exists()


def setup_needed(cfg: dict | None = None) -> list[str]:
    steps = []
    if cfg and cfg.get("bio", {}).get("enabled") and not bio_ready():
        steps.append("bio")
    p = load_params()
    if not FITTED_PATH.exists():
        steps.append("fit")
    if not ORACLE_CACHE.exists() or json.loads(ORACLE_CACHE.read_text()).get("params_source") != p.source:
        steps.append("oracle")
    if not is_frozen():
        steps.append("freeze")
    return steps


def baseline_gate(rows: list[dict]) -> dict:
    by = defaultdict(list)
    for r in L.ok_rows(rows):
        if r["agent"] in ("random", "scripted", "oracle") and r["track"] == "synthetic":
            by[r["agent"]].append(r["scores"]["brier"])
    means = {a: (round(float(np.mean(v)), 4) if v else None) for a, v in by.items()}
    # Brier: lower is better. Design quality must order random > scripted >= oracle.
    ok = all(means.get(a) is not None for a in ("random", "scripted", "oracle")) and \
        means["random"] > means["scripted"] >= means["oracle"]
    return {"passed": bool(ok), "metric": "brier (lower is better)", "means": means}


def gates(cfg: dict, rows: list[dict]) -> dict:
    g = cfg["gates"]
    p = load_params()
    out = {
        "fit_validated": {"passed": (p.validation_passed or not g["require_fit_validated"]),
                          "params_source": p.source},
        "tasks_frozen": {"passed": (is_frozen() and W.all_frozen()) or not g["require_frozen_tasks"]},
        "baseline_order": baseline_gate(L.primary(rows)),
    }
    if not g["require_baseline_order"]:
        out["baseline_order"]["passed"] = True
    return out


def _halfwidth(xs: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 1.0
    return 1.96 * float(np.std(xs, ddof=1)) / math.sqrt(n)


def pending_items(cfg: dict, rows: list[dict]) -> tuple[list[dict], dict]:
    g = gates(cfg, rows)
    if not (g["fit_validated"]["passed"] and g["tasks_frozen"]["passed"]):
        return [], g
    tasks = load_tasks()
    done, _ = L.status(rows, cfg["automation"]["max_error_retries"])
    tracks, labels = cfg["tracks"]["enabled"], cfg["labels"]["enabled"]
    items = []

    for seed in range(cfg["baselines"]["seeds"]):
        for agent in cfg["baselines"]["agents"]:
            for track in tracks:
                for t in tasks:
                    k = L.item_key(t.task_id, agent, "none", track, "named", seed)
                    if k not in done:
                        items.append({"key": k, "task_id": t.task_id, "agent": agent, "model": "none",
                                      "track": track, "labels": "named", "seed": seed, "est_min": 0.3})
    bio_on = cfg.get("bio", {}).get("enabled") and bio_ready()
    bio_tasks = []
    if bio_on:
        from .bio.lab import load_bio_tasks
        bio_tasks = load_bio_tasks()
        for seed in range(cfg["baselines"]["seeds"]):
            for agent in ("random", "scripted"):
                for t in bio_tasks:
                    k = L.item_key(t.task_id, agent, "none", "sachs", "named", seed)
                    if k not in done:
                        items.append({"key": k, "task_id": t.task_id, "agent": agent, "model": "none",
                                      "track": "sachs", "labels": "named", "seed": seed, "est_min": 0.1,
                                      "domain": "bio"})
    if not g["baseline_order"]["passed"]:
        return items, g
    studies = S.pending(cfg, done, tasks, bio_tasks if bio_on else [])
    if items:
        return studies + items + W.pending(cfg, rows, done), g

    sc = cfg["seeds"]
    ok = L.ok_rows(L.primary(rows))
    cells = [(track, tasks, "neuro") for track in tracks] + ([("sachs", bio_tasks, "bio")] if bio_on else [])
    for m in cfg["llm"]["models"]:
        for track, track_tasks, domain in cells:
            for lab in labels:
                cell = [r for r in ok if r["model"] == m["name"] and r["track"] == track and r["labels"] == lab]
                for seed in range(sc["max_seeds"]):
                    keys = [L.item_key(t.task_id, "llm", m["name"], track, lab, seed) for t in track_tasks]
                    missing = [(t, k) for t, k in zip(track_tasks, keys) if k not in done]
                    if missing:
                        items += [{"key": k, "task_id": t.task_id, "agent": "llm", "model": m["name"],
                                   "track": track, "labels": lab, "seed": seed, "domain": domain,
                                   "est_min": m["minutes_per_episode"]} for t, k in missing]
                        break  # one seed at a time per cell
                    if seed + 1 >= sc["min_seeds"] and \
                            _halfwidth([r["scores"]["brier"] for r in cell]) <= sc["ci_halfwidth_target"]:
                        break  # precise enough: stop adding seeds to this cell
    return studies + items + W.pending(cfg, rows, done), g


# Execution order only (what gets run is unchanged): author studies first, then the headline cell,
# so the leaderboard fills before the secondary tracks. Alphabetical order ran "sachs" and "abstract" first.
TRACK_RANK = {"synthetic": 0, "semisynthetic": 1, "sachs": 2}
LABEL_RANK = {"named": 0, "abstract": 1}


def _priority(it: dict) -> tuple:
    return (0 if it.get("study") else 1, bool(it.get("wave")), it["seed"], TRACK_RANK.get(it["track"], 9),
            LABEL_RANK.get(it["labels"], 9), it["task_id"], it["agent"])


def make_plan(cfg: dict, rows: list[dict]) -> dict:
    items, g = pending_items(cfg, rows)
    auto = cfg["automation"]
    cap_min = auto["shard_hours"] * 60
    by_model = defaultdict(list)
    for it in items:
        by_model[it["model"]].append(it)
    shards = []
    for model, its in by_model.items():
        # Author studies first: they are the experiments the author is waiting on.
        its.sort(key=_priority)
        cur, used = [], 0.0
        for it in its:
            if cur and used + it["est_min"] > cap_min:
                shards.append({"model": model, "items": cur})
                cur, used = [], 0.0
            cur.append(it)
            used += it["est_min"]
        if cur:
            shards.append({"model": model, "items": cur})
    # Round-robin across models so every model advances each run.
    queues = defaultdict(list)
    for s in shards:
        queues[s["model"]].append(s)
    ordered = []
    while any(queues.values()) and len(ordered) < auto["max_shards_per_run"]:
        for m in list(queues):
            if queues[m] and len(ordered) < auto["max_shards_per_run"]:
                ordered.append(queues[m].pop(0))
    for i, s in enumerate(ordered):
        s["shard"] = i
    n_wave = sum(1 for it in items if it.get("wave"))
    setup = setup_needed(cfg)
    if not setup and g["baseline_order"]["passed"] and W.due(cfg, len(items) - n_wave, n_wave) is not None:
        setup.append("wave")
    return {
        "gates": g,
        "setup": setup,
        "n_pending_wave": n_wave,
        "n_pending_total": len(items),
        "shards": ordered,
        "matrix": [{"shard": s["shard"], "model": s["model"]} for s in ordered],
    }
