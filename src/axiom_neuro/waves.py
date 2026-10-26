"""Replication waves: fresh task sets, frozen on a schedule, run by the same engine.

The preregistered study runs on one frozen task set (wave 0). Once its queue is empty, the
engine freezes a new wave of never-seen task instances every `min_days_between` days and runs
every model on it once. This answers two questions the frozen set alone cannot:

  - Do the rankings replicate on new instances drawn from the same hypothesis family?
  - Does a published task set leak into later results (published tasks vs fresh ones)?

Each wave's seed is fixed in advance (`tasks.seed + 1000 * wave`), so a wave's content is
decided by the config, not by when it happens to be frozen. Only the freeze date is clock time.
"""

from __future__ import annotations

import json
from datetime import date

from . import ledger as L
from .params import REPO
from .tasks import Task, build_tasks, freeze, is_frozen, load_tasks

WAVES = REPO / "tasks" / "waves"
INDEX = WAVES / "index.json"


def wave_seed(cfg: dict, wave: int) -> int:
    return cfg["tasks"]["seed"] + 1000 * wave


def _paths(wave: int):
    return WAVES / f"w{wave:02d}.jsonl", WAVES / f"w{wave:02d}.sha256"


def index() -> list[dict]:
    return json.loads(INDEX.read_text()) if INDEX.exists() else []


def all_frozen() -> bool:
    return all(is_frozen(*_paths(w["wave"])) for w in index())


def load_wave(wave: int) -> list[Task]:
    return load_tasks(_paths(wave)[0])


def wave_tasks() -> dict[int, list[Task]]:
    return {w["wave"]: load_wave(w["wave"]) for w in index()}


def build_wave(cfg: dict, wave: int) -> list[Task]:
    wc = cfg["waves"]
    tasks = build_tasks(wave_seed(cfg, wave), wc["instances_per_type"], cfg["tasks"]["budget_participant_hours"])
    for t in tasks:
        t.task_id = f"w{wave:02d}-{t.task_id}"
    return tasks


def pending(cfg: dict, rows: list[dict], done: set) -> list[dict]:
    """Work items for every frozen wave: reference agents, then each model once per track x label."""
    wc = cfg.get("waves", {})
    if not wc.get("enabled"):
        return []
    items = []
    for wave, tasks in wave_tasks().items():
        for t in tasks:
            for agent in wc["reference_agents"]:
                for track in wc["tracks"]:
                    k = L.item_key(t.task_id, agent, "none", track, "named", 0)
                    if k not in done:
                        items.append({"key": k, "task_id": t.task_id, "agent": agent, "model": "none",
                                      "track": track, "labels": "named", "seed": 0, "est_min": 0.3,
                                      "wave": wave})
            for m in cfg["llm"]["models"]:
                for track in wc["tracks"]:
                    for lab in wc["labels"]:
                        k = L.item_key(t.task_id, "llm", m["name"], track, lab, 0)
                        if k not in done:
                            items.append({"key": k, "task_id": t.task_id, "agent": "llm", "model": m["name"],
                                          "track": track, "labels": lab, "seed": 0, "wave": wave,
                                          "est_min": m["minutes_per_episode"]})
    return items


def due(cfg: dict, primary_pending: int, wave_pending: int, today: date | None = None) -> int | None:
    """The next wave number if one should be frozen now, else None."""
    wc = cfg.get("waves", {})
    if not wc.get("enabled") or primary_pending or wave_pending:
        return None
    idx = index()
    if len(idx) >= wc["max_waves"]:
        return None
    today = today or date.today()
    if idx and (today - date.fromisoformat(idx[-1]["frozen_on"])).days < wc["min_days_between"]:
        return None
    return (idx[-1]["wave"] + 1) if idx else 1


def freeze_wave(cfg: dict, wave: int, today: date | None = None) -> dict:
    idx = index()
    if any(w["wave"] == wave for w in idx):
        raise ValueError(f"wave {wave} is already frozen")
    tasks = build_wave(cfg, wave)
    path, sha_path = _paths(wave)
    sha = freeze(tasks, path, sha_path)
    entry = {"wave": wave, "seed": wave_seed(cfg, wave), "n_tasks": len(tasks),
             "frozen_on": (today or date.today()).isoformat(), "sha256": sha}
    INDEX.write_text(json.dumps(idx + [entry], indent=2) + "\n")
    return entry
