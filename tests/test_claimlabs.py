import json

from axiom_neuro import claimlab as CL
from axiom_neuro.agents.llm import run_llm
from axiom_neuro.claimlab import core, ethics, health


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)

    def chat(self, messages, seed, actions=None):
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


def test_frozen_manifests_match_and_load():
    for m in CL.LABS.values():
        assert CL.ready(m), m.NAME
        ts = CL.tasks(m)
        assert len(ts) == 20 and all(len(t.claims) == 6 for t in ts)


def test_planted_truth_agrees_with_full_population():
    f = health.base_frame()
    for t in CL.tasks(health)[:5]:
        fr = health.plant(f, t.plant, t.seed)
        for c in t.claims.values():
            val = core.estimate(fr, c["est"], health.WEIGHT)[0]
            assert core.holds(val, c["op"], c["thr"]) == c["truth"], (t.task_id, c["id"])


def test_compas_matches_propublica():
    f = ethics.frame()
    assert len(f) == 5278  # ProPublica's filtered Black + white sample
    fpr = core.estimate(f, ethics.POOL["fpr_gap"][1], None)[0]
    assert 0.15 < fpr < 0.25  # ~45% vs ~23% labelled higher risk among non-reoffenders


def test_weights_trap_is_real():
    t = next(t for t in CL.tasks(health) if any(c["trap"] == "weights" for c in t.claims.values()))
    fr = health.frame(t)
    c = next(c for c in t.claims.values() if c["trap"] == "weights")
    unweighted = core.mean_of(fr, "exposure", None, health.WEIGHT, False)[0]
    assert core.holds(unweighted, c["op"], c["thr"]) != c["truth"]  # the unweighted answer is wrong


def test_lab_actions_and_baselines():
    for m in CL.LABS.values():
        t = CL.tasks(m)[0]
        lab = core.ClaimLab(m, t, "abstract", 0)
        b = lab.briefing()
        assert "Black" not in b and "systolic" not in b  # abstract labels hide the domain
        obs = lab.step("sample", {"source": "all", "n": 300})
        assert obs["dataset"] == "D1" and lab.remaining == t.budget - 300 - m.OVERHEAD
        y = "Y"
        assert "groups" in lab.step("summarize", {"datasets": ["D1"], "variable": y, "by": lab.names[list(m.VARIABLES)[0]]})
        pred = lab.names[list(m.VARIABLES)[1]]
        assert "coefficients" in lab.step("regress", {"datasets": ["D1"], "outcome": y, "predictors": [pred]})
        assert "error" in lab.step("sample", {"source": "nowhere", "n": 100})
        for agent, fn in (("random", core.run_random), ("scripted", core.run_scripted)):
            lab2 = core.ClaimLab(m, t, "named", 1)
            fn(lab2, 1)
            s = core.score(lab2.episode.submitted, t)
            assert 0 <= s["brier"] <= 1 and "fell_for_trap" in s


def test_scripted_beats_random_on_average():
    for m in CL.LABS.values():
        ts = CL.tasks(m)[:8]
        def mean_brier(fn):
            out = []
            for t in ts:
                lab = core.ClaimLab(m, t, "named", 0)
                fn(lab, 0)
                out.append(core.score(lab.episode.submitted, t)["brier"])
            return sum(out) / len(out)
        assert mean_brier(core.run_scripted) < mean_brier(core.run_random), m.NAME


def test_llm_episode_in_claim_lab():
    t = CL.tasks(ethics)[0]
    lab = core.ClaimLab(ethics, t, "named", 0)
    replies = [
        json.dumps({"thought": "draw", "action": "sample", "args": {"source": "all", "n": 400}}),
        json.dumps({"thought": "look", "action": "summarize",
                    "args": {"datasets": ["D1"], "variable": "rearrested_2y", "by": "black"}}),
        json.dumps({"thought": "done", "action": "submit",
                    "args": {"claims": {c: {"true": True, "confidence": 0.6} for c in t.claims}}}),
    ]
    out = run_llm(lab, FakeClient(replies), seed=0, max_turns=6)
    assert out["submitted"] and lab.episode.edges_claimed == 6
    assert "rows" in out["transcript"][3]["content"]  # budget unit for claim labs


def test_planner_queues_claim_lab_baselines():
    from axiom_neuro.config import load_config
    from axiom_neuro import planner
    items, _ = planner.pending_items(load_config(), [])
    tracks = {i["track"] for i in items if i.get("domain") in ("health", "ethics")}
    assert tracks == {"nhanes", "compas"}
