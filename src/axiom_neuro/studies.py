"""Studies: experiments the author decides on after the preregistration, run by the same engine.

A study is one TOML file in ``studies/``. It names the question, the models, which slice of the
frozen task set to use, and what to change (turns, temperature, budget, or an extra instruction).
The file is committed before any of its episodes run, so its commit is its registration.

Study rows carry ``study = <id>`` and a distinct ledger key, so they never enter the preregistered
analysis. Each study is compared with the primary rows of the same model, track, labels and tasks:
the paired per-task difference in Brier score, with a bootstrap CI over tasks.
"""

from __future__ import annotations

import json
import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from . import ledger as L
from .params import REPO

STUDIES = REPO / "studies"
OUT = REPO / "results" / "studies"
KNOBS = {"max_turns", "temperature", "budget_participant_hours", "instruction"}


def slug(text: str, n: int = 40) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:n].strip("-") or "study"


def load_all() -> list[dict]:
    out = []
    for p in sorted(STUDIES.glob("*.toml")) if STUDIES.exists() else []:
        s = tomllib.loads(p.read_text())
        s.setdefault("id", p.stem)
        out.append(validate(s))
    return out


def validate(s: dict) -> dict:
    for k in ("id", "question", "models"):
        if not s.get(k):
            raise ValueError(f"study {s.get('id', '?')}: missing {k}")
    s.setdefault("tracks", ["synthetic"])
    s.setdefault("labels", ["named"])
    s.setdefault("task_types", [])
    s.setdefault("seeds", 1)
    s.setdefault("change", {})
    bad = set(s["change"]) - KNOBS
    if bad:
        raise ValueError(f"study {s['id']}: unknown change {sorted(bad)}; allowed {sorted(KNOBS)}")
    return s


def models_for(s: dict, cfg: dict) -> list[dict]:
    known = {m["name"]: m for m in cfg["llm"]["models"]}
    names = list(known) if s["models"] in ("all", ["all"]) else s["models"]
    # A model not in the main config still runs (e.g. testing a new one); size it like the slowest.
    slow = max((m["minutes_per_episode"] for m in known.values()), default=10)
    return [known.get(n, {"name": n, "params_b": None, "minutes_per_episode": slow}) for n in names]


def key(s: dict, task_id: str, model: str, track: str, labels: str, seed: int) -> str:
    return L.item_key(task_id, f"llm@{s['id']}", model, track, labels, seed)


def pending(cfg: dict, done: set, tasks: list, bio_tasks: list) -> list[dict]:
    items = []
    for s in load_all():
        for m in models_for(s, cfg):
            for track in s["tracks"]:
                pool = bio_tasks if track == "sachs" else tasks
                if s["task_types"]:
                    pool = [t for t in pool if t.task_type in s["task_types"]]
                for lab in s["labels"]:
                    for seed in range(s["seeds"]):
                        for t in pool:
                            k = key(s, t.task_id, m["name"], track, lab, seed)
                            if k not in done:
                                items.append({"key": k, "task_id": t.task_id, "agent": "llm", "model": m["name"],
                                              "track": track, "labels": lab, "seed": seed, "study": s["id"],
                                              "domain": "bio" if track == "sachs" else "neuro",
                                              "est_min": m["minutes_per_episode"]})
    return items


def get(study_id: str) -> dict:
    return next(s for s in load_all() if s["id"] == study_id)


# ---------- analysis ----------

def _boot(diffs: list[float], n: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    import numpy as np
    d = np.asarray(diffs, float)
    rng = np.random.default_rng(seed)
    means = d[rng.integers(0, len(d), (n, len(d)))].mean(axis=1)
    return float(d.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _by_task(rows, fn):
    acc: dict[str, list[float]] = {}
    for r in rows:
        acc.setdefault(r["task_id"], []).append(fn(r))
    return {k: sum(v) / len(v) for k, v in acc.items()}


def analyse(s: dict, rows: list[dict], cfg: dict) -> dict:
    ok = L.ok_rows(rows)
    mine = [r for r in ok if r.get("study") == s["id"]]
    expected = len(pending(cfg, set(), _tasks(), _bio_tasks(s)))
    cells = []
    for m in models_for(s, cfg):
        for track in s["tracks"]:
            for lab in s["labels"]:
                arm = [r for r in mine if r["model"] == m["name"] and r["track"] == track and r["labels"] == lab]
                base = [r for r in L.primary(ok) if r["agent"] == "llm" and r["model"] == m["name"]
                        and r["track"] == track and r["labels"] == lab and not r.get("study")]
                a = _by_task(arm, lambda r: r["scores"]["brier"])
                b = _by_task(base, lambda r: r["scores"]["brier"])
                shared = sorted(set(a) & set(b))
                cell = {"model": m["name"], "track": track, "labels": lab, "n_study": len(arm),
                        "study_brier": sum(a.values()) / len(a) if a else None,
                        "n_tasks_paired": len(shared)}
                if len(shared) >= 5:
                    est, lo, hi = _boot([a[t] - b[t] for t in shared])
                    cell.update(baseline_brier=sum(b[t] for t in shared) / len(shared), diff=est, lo=lo, hi=hi,
                                verdict=("better" if hi < 0 else "worse" if lo > 0 else "no clear difference"))
                traps = [r for r in arm if r["task_type"] in ("practice_confound", "blink_artifact")]
                if traps:
                    cell["fell_for_trap"] = sum(bool(r["scores"].get("fell_for_trap")) for r in traps) / len(traps)
                ideal = [r["ideal_on_own_data"]["brier"] for r in arm if "ideal_on_own_data" in r]
                if ideal and a:
                    cell["analysis_error"] = cell["study_brier"] - sum(ideal) / len(ideal)
                cells.append(cell)
    return {"id": s["id"], "question": s["question"], "hypothesis": s.get("hypothesis", ""),
            "change": s["change"], "issue": s.get("issue"), "n_done": len(mine), "n_expected": expected,
            # Done when every episode ran and every cell that has a main-study counterpart is paired.
            "complete": len(mine) >= expected > 0 and all(
                "diff" in c for c in cells if c["model"] in {m["name"] for m in cfg["llm"]["models"]}),
            "cells": cells}


def _tasks():
    from .tasks import load_tasks
    return load_tasks()


def _bio_tasks(s: dict):
    if "sachs" not in s["tracks"]:
        return []
    from .bio.lab import load_bio_tasks
    return load_bio_tasks()


def _f(x, nd=3):
    return "–" if x is None else f"{x:+.{nd}f}" if isinstance(x, float) and x < 0 else f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def markdown(res: dict) -> str:
    ch = ", ".join(f"`{k} = {v!r}`" for k, v in res["change"].items()) or "nothing (replication)"
    md = [f"# Study {res['id']}", "", f"**Question.** {res['question']}", ""]
    if res["hypothesis"]:
        md += [f"**Hypothesis (registered before any episode ran).** {res['hypothesis']}", ""]
    md += [f"**Change from the main study.** {ch}", "",
           f"**Progress.** {res['n_done']} of {res['n_expected']} episodes"
           + (" — complete." if res["complete"] else " — still running."), "",
           "Brier is the mean edge Brier score (lower is better). Difference = study minus the main study's "
           "episodes for the same model, track, labels and tasks; 95% CI by bootstrap over tasks.", "",
           "| Model | Track | Labels | n | Study Brier | Main-study Brier | Difference [95% CI] | Verdict | Fell for trap | Analysis error |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in res["cells"]:
        diff = f"{_f(c['diff'])} [{_f(c['lo'])}, {_f(c['hi'])}]" if "diff" in c else "– (no paired baseline yet)"
        md.append(f"| {c['model']} | {c['track']} | {c['labels']} | {c['n_study']} | {_f(c['study_brier'])} | "
                  f"{_f(c.get('baseline_brier'))} | {diff} | {c.get('verdict', '–')} | "
                  f"{_f(c.get('fell_for_trap'), 2)} | {_f(c.get('analysis_error'))} |")
    md += ["", "Exploratory: decided after the preregistration and kept out of every preregistered test."]
    return "\n".join(md) + "\n"


def report(rows: list[dict] | None = None, cfg: dict | None = None) -> list[dict]:
    from .config import load_config
    rows = L.read_rows() if rows is None else rows
    cfg = cfg or load_config()
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for s in load_all():
        res = analyse(s, rows, cfg)
        (OUT / f"{s['id']}.md").write_text(markdown(res))
        results.append(res)
    index = [{k: r[k] for k in ("id", "question", "issue", "n_done", "n_expected", "complete")} for r in results]
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    return results


def from_issue(body: str, number: int, title: str) -> tuple[str, str]:
    """Turn a GitHub issue-form body into a study file. Returns (study_id, toml_text)."""
    fields: dict[str, str] = {}
    for block in re.split(r"^### ", body, flags=re.M)[1:]:
        head, _, val = block.partition("\n")
        val = val.strip()
        fields[head.strip().lower()] = "" if val == "_No response_" else val

    def listf(name, default):
        v = fields.get(name, "")
        items = [x.strip() for x in re.split(r"[,\n]", v) if x.strip() and x.strip() != "-"]
        return [re.sub(r"^- \[x\] ", "", x, flags=re.I) for x in items if not x.lower().startswith("- [ ]")] or default

    question = fields.get("question") or title
    sid = f"s{number:03d}-{slug(question, 32)}"
    models = listf("models", ["all"])
    change: dict = {}
    for k, cast in (("max_turns", int), ("temperature", float), ("budget_participant_hours", float)):
        v = fields.get(k.replace("_", " "), "")
        if v:
            change[k] = cast(v)
    if fields.get("instruction"):
        change["instruction"] = fields["instruction"]
    task_types = [t for t in listf("task types", []) if t != "all"]
    lines = [f'# Registered from issue #{number} on {datetime.now(timezone.utc).date()}, before any episode ran.',
             f"id = {json.dumps(sid)}", f"issue = {number}", f"question = {json.dumps(question)}",
             f"hypothesis = {json.dumps(fields.get('hypothesis', ''))}",
             f"models = {json.dumps(models if models != ['all'] else 'all')}",
             f"tracks = {json.dumps(listf('tracks', ['synthetic']))}",
             f"labels = {json.dumps(listf('labels', ['named']))}",
             f"task_types = {json.dumps(task_types)}",
             f"seeds = {int(fields.get('seeds') or 1)}", "", "[change]"]
    lines += [f"{k} = {json.dumps(v)}" for k, v in change.items()]
    text = "\n".join(lines) + "\n"
    validate(tomllib.loads(text))
    return sid, text
