"""Claim labs (exploratory, added 2026-11-04): real data, a sampling budget, claims with known answers.

Each lab is a module with NAME (config key and ledger `domain`), TRACK (ledger `track`), the data,
wording and tasks. The planner and runner treat every lab here alike.
"""

from __future__ import annotations

from . import core, ethics, health

LABS = {m.NAME: m for m in (health, ethics)}
BY_TRACK = {m.TRACK: m for m in LABS.values()}


def enabled(cfg: dict) -> list:
    return [m for name, m in LABS.items() if cfg.get("labs", {}).get(name, {}).get("enabled")]


def ready(m) -> bool:
    """Frozen and untouched: the manifest's hash matches the committed one. Committed data (health) must be
    present; runtime-fetched data (ethics) is downloaded on first use."""
    import hashlib
    if not (m.MANIFEST.exists() and m.SHA.exists()):
        return False
    if hashlib.sha256(m.MANIFEST.read_bytes()).hexdigest() != m.SHA.read_text().strip():
        return False
    return m.DATA.exists() or m.NAME != "health"


def setup(m, cfg: dict) -> str:
    c = cfg["labs"][m.NAME]
    m.fetch()
    return core.freeze(m.build_tasks(c["seed"], c["n_tasks"]), m.MANIFEST, m.SHA)


_TASKS: dict = {}


def tasks(m) -> list[core.ClaimTask]:
    if m.NAME not in _TASKS:
        _TASKS[m.NAME] = core.load(m.MANIFEST)
    return _TASKS[m.NAME]


def run_item(m, item: dict, task: core.ClaimTask, run_llm_fn) -> dict:
    """One episode in a claim lab. run_llm_fn(env) runs a language-model agent and returns its extras."""
    env = core.ClaimLab(m, task, item["labels"], run_seed=item["seed"])
    extra = {}
    if item["agent"] == "random":
        core.run_random(env, item["seed"])
    elif item["agent"] == "scripted":
        core.run_scripted(env, item["seed"])
    elif item["agent"] == "llm":
        extra = run_llm_fn(env)
    else:
        raise ValueError(f"agent {item['agent']} not available in the {m.NAME} lab")
    s = core.score(env.episode.submitted, task)
    s_ref = core.score(core.reference_claims(m, task, env.datasets), task)
    return {"scores": s, "ideal_on_own_data": {k: s_ref[k] for k in ("exact", "edge_acc", "brier")},
            "n_experiments": len(env.datasets), "budget_spent": env.episode.spent, "confound_handled": None,
            "edges_claimed": env.episode.edges_claimed, "claims": env.episode.submitted,
            "sources": [a["args"].get("source") for a in env.episode.actions if a["action"] == "sample"],
            "used_weights": any(bool(a["args"].get("weighted")) for a in env.episode.actions),
            "claim_ids": {c: v["id"] for c, v in task.claims.items()}, **extra}
