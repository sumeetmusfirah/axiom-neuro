"""The parts that keep the study going: replication waves, model intake, leaderboard."""

import shutil
import tomllib
from datetime import date

from axiom_neuro import intake as I
from axiom_neuro import ledger as L
from axiom_neuro import report as R
from axiom_neuro import waves as W
from axiom_neuro.config import CONFIG, load_config

CFG = load_config()


def test_waves_are_fresh_and_deterministic():
    a, b = W.build_wave(CFG, 1), W.build_wave(CFG, 1)
    assert [t.to_json() for t in a] == [t.to_json() for t in b]
    assert all(t.task_id.startswith("w01-") for t in a)
    assert len(a) == 6 * CFG["waves"]["instances_per_type"]
    other = W.build_wave(CFG, 2)
    assert {t.seed for t in a}.isdisjoint({t.seed for t in other})


def test_wave_is_due_only_when_idle_and_spaced(tmp_path, monkeypatch):
    monkeypatch.setattr(W, "WAVES", tmp_path)
    monkeypatch.setattr(W, "INDEX", tmp_path / "index.json")
    d0 = date(2027, 1, 1)
    assert W.due(CFG, primary_pending=5, wave_pending=0, today=d0) is None
    assert W.due(CFG, 0, 0, d0) == 1
    W.freeze_wave(CFG, 1, d0)
    assert W.all_frozen() and len(W.load_wave(1)) == 30
    assert W.due(CFG, 0, 3, date(2027, 6, 1)) is None          # wave 1 still running
    assert W.due(CFG, 0, 0, date(2027, 1, 10)) is None         # too soon
    assert W.due(CFG, 0, 0, date(2027, 2, 1)) == 2
    items = W.pending(CFG, [], set())
    n_models = len(CFG["llm"]["models"])
    assert sum(it["agent"] == "llm" for it in items) == 30 * n_models * len(CFG["waves"]["labels"])
    assert all(it["wave"] == 1 for it in items)


def test_wave_rows_never_enter_primary_results():
    rows = [{"key": "a", "status": "ok"}, {"key": "b", "status": "ok", "wave": 1}]
    assert [r["key"] for r in L.primary(rows)] == ["a"]


def test_intake_adds_next_available_candidate(tmp_path):
    cfg = dict(CFG)
    fake = {"phi4-mini:3.8b": None, "llama3.1:8b": {"gb": 4.9, "digest": "46e0c10c039e" + "0" * 52}}
    pick = I.next_candidate(cfg, queued=0, info=lambda n: fake.get(n, {"gb": 99, "digest": "x"}))
    assert pick[0]["name"] == "llama3.1:8b"
    assert I.next_candidate(cfg, queued=10**6, info=lambda n: None) is None
    p = tmp_path / "experiment.toml"
    shutil.copy(CONFIG, p)
    I.add_to_config(I.model_line(*pick, today=date(2027, 1, 4)), p)
    models = tomllib.loads(p.read_text())["llm"]["models"]
    assert models[-1] == {"name": "llama3.1:8b", "params_b": 8.0, "minutes_per_episode": 12,
                          "added": "2027-01-04", "digest": "46e0c10c039e"}
    assert len(models) == len(CFG["llm"]["models"]) + 1


def test_leaderboard_replaces_only_its_block(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(f"intro\n{R.BOARD_START}\nold\n{R.BOARD_END}\noutro\n")
    summ = {"scripted|synthetic|named": {"agent": "scripted", "track": "synthetic", "labels": "named", "n": 3,
                                         "brier": 0.05, "brier_lo": 0.04, "brier_hi": 0.06, "trap_rate": 0.1}}
    R.write_leaderboard(R.leaderboard(CFG, summ), "2027-01-01", readme)
    text = readme.read_text()
    assert text.startswith("intro\n") and text.endswith(f"{R.BOARD_END}\noutro\n")
    assert "old" not in text and "scripted (reference)" in text


def test_plan_runs_the_headline_cell_first():
    from axiom_neuro.planner import _priority
    items = [{"seed": 0, "track": t, "labels": lab, "task_id": "x", "agent": "llm"}
             for t in ("sachs", "semisynthetic", "synthetic") for lab in ("abstract", "named")]
    items.append({"seed": 0, "track": "synthetic", "labels": "named", "task_id": "w01-x", "agent": "llm", "wave": 1})
    order = sorted(items, key=_priority)
    assert (order[0]["track"], order[0]["labels"]) == ("synthetic", "named") and not order[0].get("wave")
    assert order[-1].get("wave") == 1


def test_first_completed_attempt_counts_and_duplicates_are_paired():
    a = {"key": "k", "status": "ok", "finished_at": "2026-10-26T01", "v": "first"}
    b = {"key": "k", "status": "ok", "finished_at": "2026-10-26T02", "v": "second"}
    assert [r["v"] for r in L.ok_rows([b, a])] == ["first"]
    assert [(x["v"], y["v"]) for x, y in L.duplicate_pairs([b, a])] == [("first", "second")]
