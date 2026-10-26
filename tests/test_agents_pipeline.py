import json

import pytest

from axiom_neuro import ledger as L
from axiom_neuro import planner
from axiom_neuro.agents import baselines as B
from axiom_neuro.agents.llm import parse_action, run_llm
from axiom_neuro.env import LabEnv
from axiom_neuro.mechanisms import EDGES
from axiom_neuro.params import SimParams
from axiom_neuro.scoring import score
from axiom_neuro.tasks import build_tasks

TASKS = build_tasks(11, 1, 30.0)


class FakeClient:
    """Replays a fixed script of replies; the last reply repeats."""

    def __init__(self, replies):
        self.replies = list(replies)

    def chat(self, messages, seed, actions=None):
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


def _submit_all(present=True):
    return json.dumps({"thought": "done", "action": "submit",
                       "args": {"edges": {e: {"present": present, "confidence": 0.7} for e in EDGES}}})


def test_parse_action_handles_reasoning_and_rejects_garbage():
    a, args, _ = parse_action('<think>hmm</think>{"thought":"x","action":"describe","args":{"datasets":["D0"]}}')
    assert a == "describe" and args == {"datasets": ["D0"]}
    with pytest.raises(ValueError):
        parse_action('{"action":"fly","args":{}}')


def test_llm_episode_runs_and_scores():
    env = LabEnv(TASKS[0], SimParams(), "synthetic", "named", 0)
    design = json.dumps({"thought": "test", "action": "design_experiment", "args": B.SCRIPTED})
    out = run_llm(env, FakeClient(["not json", design, _submit_all()]), seed=0, max_turns=6)
    assert out["submitted"] and out["parse_failures"] == 1
    assert len(env.collected()) == 2
    s = score(env.episode.submitted, TASKS[0].mechanism.truth(), TASKS[0].task_type)
    assert 0 <= s["brier"] <= 1 and env.episode.edges_claimed == 6


def test_llm_without_submit_is_flagged():
    env = LabEnv(TASKS[0], SimParams(), "synthetic", "abstract", 0)
    describe = json.dumps({"thought": "t", "action": "describe", "args": {"datasets": ["D0"]}})
    out = run_llm(env, FakeClient([describe]), seed=0, max_turns=3)
    assert not out["submitted"] and env.episode.submitted is not None


def test_budget_is_enforced():
    env = LabEnv(TASKS[0], SimParams(), "synthetic", "named", 0)
    obs = env.step("design_experiment", B.SCRIPTED | {"n_participants": 96, "trials_per_cell": 200})
    assert "error" in obs and env.episode.spent == 0


def test_baselines_run_on_every_task():
    for t in TASKS:
        for fn in (B.run_random, B.run_scripted):
            env = LabEnv(t, SimParams(), "synthetic", "named", 0)
            fn(env, 0)
            assert env.episode.submitted is not None


def test_ledger_collect_is_idempotent(tmp_path):
    inc, led = tmp_path / "incoming", tmp_path / "ledger.jsonl"
    inc.mkdir()
    rows = [{"key": "a", "attempt_id": "1", "status": "ok"}, {"key": "b", "attempt_id": "2", "status": "error"}]
    (inc / "s0.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert L.collect(inc, led) == 2
    assert L.collect(inc, led) == 0
    done, errors = L.status(L.read_rows(led), max_errors=1)
    assert done == {"a", "b"}


def test_planner_blocks_llm_until_baselines_ordered(monkeypatch):
    cfg = {"gates": {"require_fit_validated": True, "require_baseline_order": True, "require_frozen_tasks": True},
           "tracks": {"enabled": ["synthetic"]}, "labels": {"enabled": ["named"]},
           "baselines": {"agents": ["random", "scripted", "oracle"], "seeds": 1},
           "llm": {"models": [{"name": "m", "params_b": 1, "minutes_per_episode": 5}]},
           "seeds": {"min_seeds": 1, "max_seeds": 3, "ci_halfwidth_target": 0.01},
           "automation": {"max_error_retries": 3, "shard_hours": 5.0, "max_shards_per_run": 8}}
    monkeypatch.setattr(planner, "load_tasks", lambda: TASKS)
    good = {"fit_validated": {"passed": True}, "tasks_frozen": {"passed": True}}
    monkeypatch.setattr(planner, "gates", lambda c, r: good | {"baseline_order": planner.baseline_gate(r)})

    items, _ = planner.pending_items(cfg, [])
    assert {i["agent"] for i in items} == {"random", "scripted", "oracle"}

    def row(agent, brier, task):
        return {"key": L.item_key(task, agent, "none", "synthetic", "named", 0), "status": "ok", "agent": agent,
                "track": "synthetic", "scores": {"brier": brier}, "model": "none", "labels": "named"}
    bad = [row(a, b, t.task_id) for t in TASKS for a, b in [("random", 0.1), ("scripted", 0.2), ("oracle", 0.2)]]
    items, g = planner.pending_items(cfg, bad)
    assert items == [] and not g["baseline_order"]["passed"]  # wrong order: nothing runs

    ok = [row(a, b, t.task_id) for t in TASKS for a, b in [("random", 0.3), ("scripted", 0.2), ("oracle", 0.1)]]
    items, g = planner.pending_items(cfg, ok)
    assert g["baseline_order"]["passed"] and {i["agent"] for i in items} == {"llm"}
    assert {i["seed"] for i in items} == {0}  # one seed at a time


def test_bio_lab_end_to_end():
    from axiom_neuro.bio.lab import BioLab, build_bio_tasks, run_scripted, score_bio, classify_pairs
    from axiom_neuro.bio.data import load_graph
    pairs = classify_pairs(load_graph())
    assert not set(pairs["reversed"]) & set(pairs["true"])
    t = build_bio_tasks(5, 2)[0]
    assert len(t.candidates) == 6 and 2 <= sum(t.truth().values()) <= 3
    lab = BioLab(t, "abstract", 0)
    assert "Raf" not in lab.briefing()  # abstract labels hide molecule names
    obs = lab.step("run_condition", {"condition": "baseline", "n_cells": 300})
    assert obs["dataset"] == "C1" and lab.remaining == t.budget - 400
    assert "rho" in lab.step("correlate", {"datasets": ["baseline"], "x": "M1", "y": "M2", "given": ["M1", "M3"]})
    assert "error" in lab.step("run_condition", {"condition": "baseline", "n_cells": 5000})
    lab2 = BioLab(t, "named", 0)
    run_scripted(lab2, 0)
    s = score_bio(lab2.episode.submitted, t)
    assert 0 <= s["brier"] <= 1 and "fell_for_trap" in s
