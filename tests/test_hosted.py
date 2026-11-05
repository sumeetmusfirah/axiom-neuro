import json

from axiom_neuro import ledger as L
from axiom_neuro import planner
from axiom_neuro.agents.llm import QuotaExhausted
from axiom_neuro.config import load_config


def test_no_key_means_no_hosted_work(monkeypatch):
    monkeypatch.delenv("AXIOM_HOSTED", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    p = planner.make_plan(load_config(), L.read_rows())
    assert not any(m["hosted"] for m in p["matrix"])


def test_key_queues_one_hosted_episode_per_run(monkeypatch):
    monkeypatch.setenv("AXIOM_HOSTED", "1")
    cfg = load_config()
    p = planner.make_plan(cfg, L.read_rows())
    hosted = [s for s in p["shards"] if s["model"] == "hosted"]
    assert len(hosted) == 1 and len(hosted[0]["items"]) == cfg["hosted"]["episodes_per_run"]
    assert all(it["hosted"] for it in hosted[0]["items"])


def test_quota_stop_writes_nothing(monkeypatch, tmp_path):
    from axiom_neuro import runner
    monkeypatch.setenv("AXIOM_HOSTED", "1")
    cfg = load_config()
    plan = planner.make_plan(cfg, L.read_rows())
    shard = next(s for s in plan["shards"] if s["model"] == "hosted")

    class Quota:
        model = "x"

        def chat(self, *a, **k):
            raise QuotaExhausted("free-models-per-day")

    out = tmp_path / "s.jsonl"
    stats = runner.run_shard(plan, shard["shard"], out, 60, cfg, client_factory=lambda m: Quota())
    assert "quota_stopped" in stats
    assert not out.exists() or out.read_text().strip() == ""
