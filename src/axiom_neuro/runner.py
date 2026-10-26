"""Execute one shard of a plan under a wall-clock budget. Every episode is written as it
finishes, so a killed job loses at most the episode in flight."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import analysis as A
from .agents import baselines as B
from .agents.llm import OllamaClient, run_llm
from .env import LabEnv
from .mechanisms import TASK_TYPES
from .params import REPO, load_params
from .scoring import score
from .tasks import MANIFEST_SHA, load_tasks

TRANSCRIPTS = REPO / "results" / "transcripts"


def _confound_handled(env: LabEnv) -> bool | None:
    tt = env.task.task_type
    acts = env.episode.actions
    if tt in ("practice_confound", "stim_main"):
        return any(not d.design.order_confounded() and "S" in d.design.factors
                   for d in env.collected()[1:])
    if tt in ("blink_artifact", "neural_theta"):
        return any(a["action"] == "artifact_check"
                   or (a["action"] == "regress" and a["args"].get("exclude_blinks"))
                   or (a["action"] == "design_experiment" and a["args"].get("ica"))
                   for a in acts)
    return None


def _llm_client(item, cfg, client_factory):
    llm = cfg["llm"]
    return (client_factory or (lambda m: OllamaClient(
        m, llm["temperature"], llm["num_predict"], llm["request_timeout_s"])))(item["model"])


_DIGESTS: dict[str, str | None] = {}


def _digest(client) -> str | None:
    model = getattr(client, "model", None)
    if model not in _DIGESTS:
        _DIGESTS[model] = client.digest() if hasattr(client, "digest") else None
    return _DIGESTS[model]


def _save_transcript(item, extra, actions) -> str:
    h = hashlib.sha1(item["key"].encode()).hexdigest()[:16]
    out = TRANSCRIPTS / item["model"].replace(":", "_") / f"{h}.json.gz"
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wt") as f:
        json.dump({"key": item["key"], "messages": extra["transcript"], "actions": actions}, f, default=str)
    return str(out.relative_to(REPO))


def run_bio_item(item: dict, task, cfg: dict, client_factory=None) -> dict:
    from .bio import lab as BL
    env = BL.BioLab(task, item["labels"], run_seed=item["seed"])
    extra = {}
    if item["agent"] == "random":
        BL.run_random(env, item["seed"])
    elif item["agent"] == "scripted":
        BL.run_scripted(env, item["seed"])
    elif item["agent"] == "llm":
        client = _llm_client(item, cfg, client_factory)
        extra = run_llm(env, client, item["seed"], cfg["llm"]["max_turns"])
        extra["model_digest"] = _digest(client)
    else:
        raise ValueError(f"agent {item['agent']} not available in the bio lab")
    s = BL.score_bio(env.episode.submitted, task)
    s_ref = BL.score_bio(BL.reference_claims(task, env.datasets), task)
    row = {"scores": s, "ideal_on_own_data": {k: s_ref[k] for k in ("exact", "edge_acc", "brier")},
           "n_experiments": len(env.datasets), "budget_spent": env.episode.spent, "confound_handled": None,
           "edges_claimed": env.episode.edges_claimed, "claims": env.episode.submitted,
           "edge_kinds": task.kinds}
    if item["agent"] == "llm":
        row.update({"turns": extra["turns"], "parse_failures": extra["parse_failures"],
                    "submitted": extra["submitted"], "model_digest": extra["model_digest"],
                    "transcript": _save_transcript(item, extra, env.episode.actions)})
    return row


def run_item(item: dict, task, params, cfg: dict, client_factory=None) -> dict:
    if item.get("domain") == "bio":
        return run_bio_item(item, task, cfg, client_factory)
    env = LabEnv(task, params, item["track"], item["labels"], run_seed=item["seed"])
    extra = {}
    if item["agent"] == "random":
        B.run_random(env, item["seed"])
    elif item["agent"] == "scripted":
        B.run_scripted(env, item["seed"])
    elif item["agent"] == "oracle":
        B.run_oracle(env, item["seed"])
    elif item["agent"] == "llm":
        client = _llm_client(item, cfg, client_factory)
        extra = run_llm(env, client, item["seed"], cfg["llm"]["max_turns"])
        extra["model_digest"] = _digest(client)
    else:
        raise ValueError(f"unknown agent {item['agent']}")

    truth = task.mechanism.truth()
    claims = env.episode.submitted
    s = score(claims, truth, task.task_type)
    # Analysis oracle on the agent's own data: separates bad experiments from bad analysis.
    s_ideal = score(A.ideal_claims(env.collected()), truth, task.task_type)
    row = {
        "scores": s,
        "ideal_on_own_data": {k: s_ideal[k] for k in ("exact", "edge_acc", "brier")},
        "n_experiments": len(env.collected()) - 1,
        "budget_spent": env.episode.spent,
        "confound_handled": _confound_handled(env),
        "edges_claimed": env.episode.edges_claimed,
        "claims": claims,
    }
    if item["agent"] == "llm":
        row.update({"turns": extra["turns"], "parse_failures": extra["parse_failures"],
                    "submitted": extra["submitted"], "model_digest": extra["model_digest"]})
        row["transcript"] = _save_transcript(item, extra, env.episode.actions)
    return row


def run_shard(plan: dict, shard: int, out_path: Path, budget_min: float, cfg: dict,
              client_factory=None) -> dict:
    t0 = time.monotonic()
    params = load_params()
    tasks = {t.task_id: t for t in load_tasks()}
    if any(it.get("domain") == "bio" for s in plan["shards"] for it in s["items"]):
        from .bio.lab import load_bio_tasks
        tasks.update({t.task_id: t for t in load_bio_tasks()})
    if any(it.get("wave") for s in plan["shards"] for it in s["items"]):
        from .waves import wave_tasks
        tasks.update({t.task_id: t for ts in wave_tasks().values() for t in ts})
    sh = next(s for s in plan["shards"] if s["shard"] == shard)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_sha = MANIFEST_SHA.read_text().strip() if MANIFEST_SHA.exists() else None
    stats = {"ok": 0, "error": 0, "skipped_for_time": 0}
    with out_path.open("a") as f:
        for item in sh["items"]:
            elapsed_min = (time.monotonic() - t0) / 60
            if elapsed_min + 1.5 * item["est_min"] > budget_min:
                stats["skipped_for_time"] += 1
                continue
            started = time.monotonic()
            base = {k: item[k] for k in ("key", "task_id", "agent", "model", "track", "labels", "seed")}
            t = tasks[item["task_id"]]
            if item.get("wave"):
                base["wave"] = item["wave"]
            base.update({"domain": item.get("domain", "neuro"), "task_type": t.task_type,
                         "split": t.split if item.get("domain") == "bio" else TASK_TYPES[t.task_type].split,
                         "attempt_id": uuid.uuid4().hex[:12],
                         "params_source": params.source, "manifest_sha": manifest_sha,
                         "git_sha": os.environ.get("GITHUB_SHA", "local")})
            try:
                row = run_item(item, tasks[item["task_id"]], params, cfg, client_factory)
                base.update(row, status="ok")
                stats["ok"] += 1
            except Exception as exc:  # recorded and retried by a later run, up to the cap
                base.update(status="error", error=f"{type(exc).__name__}: {exc}",
                            trace=traceback.format_exc()[-2000:])
                stats["error"] += 1
            base["duration_s"] = round(time.monotonic() - started, 2)
            base["finished_at"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(base, sort_keys=True, default=str) + "\n")
            f.flush()
    return stats
