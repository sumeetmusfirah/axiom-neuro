import json

import numpy as np
import pandas as pd
import pytest

from axiom_neuro import analysis as A
from axiom_neuro.design import Design, DesignError
from axiom_neuro.mechanisms import EDGES, TASK_TYPES, Mechanism, sample_mechanism
from axiom_neuro.params import SimParams
from axiom_neuro.simulator import generate
from axiom_neuro.tasks import build_tasks, freeze, is_frozen, load_tasks

P = SimParams()


def mech(**effects):
    base = {e: 0.0 for e in EDGES} | {"L->B": 1.0}
    base.update({k.replace("_", "->").replace("SxL->Y", "SxL->Y"): v for k, v in effects.items()})
    present = frozenset(k for k, v in base.items() if (v != 0.0 and k != "L->B") or (k == "L->B" and v != 1.0))
    return Mechanism("test", present, base)


FULL = {"factors": ["L", "S"], "assignment": "within", "order": "counterbalanced",
        "n_participants": 48, "trials_per_cell": 120, "eeg": True, "ica": False}


def test_design_cost_and_validation():
    d = Design.from_dict({"factors": ["L"], "n_participants": 10, "trials_per_cell": 80})
    assert d.cost() == pytest.approx(10 * (0.25 + 2 * 80 * 2.5 / 3600), abs=1e-3)
    assert d.fixed == {"S": 0}
    with pytest.raises(DesignError):
        Design.from_dict({"factors": ["X"]})
    with pytest.raises(DesignError):
        Design.from_dict({"factors": ["L"], "ica": True})
    assert Design.from_dict({"factors": ["S"], "order": "fixed"}).order_confounded()
    assert not Design.from_dict({"factors": ["S"], "assignment": "between", "order": "fixed"}).order_confounded()


def test_counterbalancing_balances_order():
    d = Design.from_dict({"factors": ["S"], "n_participants": 20})
    x = generate(d, mech(), P, np.random.default_rng(0))
    first = x[x["block"] == 0].groupby("subject")["S"].first()
    assert first.mean() == pytest.approx(0.5)


def test_load_effect_recovered():
    x = generate(Design.from_dict(FULL), mech(L_Y=50.0), P, np.random.default_rng(1))
    fit = A.regress(x, "rt", ["L", "S"])
    est = fit.table()[fit.names.index("L")]["estimate"]
    assert 35 < est < 65


def test_ica_removes_blink_contamination():
    m = mech(**{"L->B": 3.0})
    raw = generate(Design.from_dict(FULL), m, P, np.random.default_rng(2))
    clean = generate(Design.from_dict(FULL | {"ica": True}), m, P, np.random.default_rng(2))
    d_raw = raw.groupby("L")["theta"].mean().diff().iloc[-1]
    d_clean = clean.groupby("L")["theta"].mean().diff().iloc[-1]
    assert d_raw > 0.05 and abs(d_clean) < abs(d_raw) / 3


def test_ideal_analyst_recovers_and_respects_identifiability():
    rng = np.random.default_rng(3)
    for name in TASK_TYPES:
        m = sample_mechanism(name, rng)
        ds = A.Dataset("D1", Design.from_dict(FULL | {"ica": True, "n_participants": 64}),
                       generate(Design.from_dict(FULL | {"ica": True, "n_participants": 64}), m, P, rng))
        claims = A.ideal_claims([ds])
        truth = m.truth()
        # Large clean experiment: every TRUE effect must be found.
        assert all(claims[e]["present"] for e in EDGES if truth[e]), name
    # Order-confounded data only: stimulation edges stay unidentified.
    d = Design.from_dict({"factors": ["S"], "fixed": {"L": 1}, "order": "fixed", "n_participants": 24})
    claims = A.ideal_claims([A.Dataset("D0", d, generate(d, mech(P_Y=-50.0), P, rng))])
    assert claims["S->Y"]["confidence"] == 0.5 and not claims["S->Y"]["identified"]


def test_null_t_statistics_are_calibrated():
    rng = np.random.default_rng(4)
    d = Design.from_dict(FULL | {"n_participants": 24, "trials_per_cell": 60})
    ts = [A.regress(generate(d, mech(), P, rng), "rt", ["S"]).z("S") for _ in range(40)]
    assert 0.6 < np.std(ts) < 1.5


def test_task_manifest_is_deterministic_and_freezable(tmp_path):
    a = build_tasks(7, 2, 30.0)
    b = build_tasks(7, 2, 30.0)
    assert [t.to_json() for t in a] == [t.to_json() for t in b]
    assert len(a) == 2 * len(TASK_TYPES)
    assert all(t.mechanism.edges >= frozenset({"P->Y"}) for t in a if t.task_type == "practice_confound")
    man, sha = tmp_path / "m.jsonl", tmp_path / "m.sha"
    freeze(a, man, sha)
    assert is_frozen(man, sha)
    assert [t.to_json() for t in load_tasks(man)] == [t.to_json() for t in a]
    man.write_text(man.read_text().replace("practice", "practise", 1))
    assert not is_frozen(man, sha)


def test_semisynthetic_uses_real_substrate(tmp_path):
    rng = np.random.default_rng(5)
    rows = []
    for s in range(5):
        for t in range(200):
            rows.append({"subject": f"sub-{s}", "trial": t, "congruent": t % 2, "rt": 400 + 30 * s + rng.normal(0, 40),
                         "correct": float(rng.random() < 0.9), "theta": -23 + rng.normal(0, 0.5),
                         "blink": int(rng.random() < 0.15)})
    path = tmp_path / "trials.csv.gz"
    pd.DataFrame(rows).to_csv(path, index=False, compression="gzip")
    d = Design.from_dict(FULL | {"n_participants": 10})
    x = generate(d, mech(L_Y=60.0), P, rng, track="semisynthetic", trials_path=path)
    assert x["theta"].mean() < -20  # real theta scale carried through
    fit = A.regress(x, "rt", ["L"])
    assert fit.table()[fit.names.index("L")]["estimate"] > 30


def test_committed_manifest_matches_config():
    """If the task set is frozen, it must be exactly what the config regenerates."""
    from axiom_neuro.config import load_config
    from axiom_neuro.tasks import MANIFEST, MANIFEST_SHA
    if not MANIFEST.exists():
        pytest.skip("task set not frozen yet")
    cfg = load_config()["tasks"]
    regen = build_tasks(cfg["seed"], cfg["instances_per_type"], cfg["budget_participant_hours"])
    frozen = load_tasks()
    assert [(t.task_id, t.seed, sorted(t.mechanism.edges)) for t in regen] == \
        [(t.task_id, t.seed, sorted(t.mechanism.edges)) for t in frozen]
    # Effect sizes may differ in the last bit across CPU architectures (ARM vs x86 FMA);
    # the frozen file, not regeneration, is what runs and is hashed.
    for a, b in zip(regen, frozen):
        for k, v in a.mechanism.effects.items():
            assert v == pytest.approx(b.mechanism.effects[k], rel=1e-9, abs=1e-12)
    assert is_frozen()


def test_report_and_hypotheses_run_on_fake_rows():
    from axiom_neuro.report import hypotheses, summarize
    from axiom_neuro.config import load_config
    rows = []
    for i, t in enumerate(build_tasks(3, 1, 30.0)):
        for agent, model in [("scripted", "none"), ("llm", "qwen3:4b")]:
            claims = {e: {"present": True, "confidence": 0.7} for e in EDGES}
            rows.append({"key": f"{t.task_id}|{agent}|{model}", "status": "ok", "agent": agent, "model": model,
                         "track": "synthetic", "labels": "named", "task_id": t.task_id, "task_type": t.task_type,
                         "split": TASK_TYPES[t.task_type].split, "claims": claims,
                         "scores": {"exact": 0.0, "edge_acc": 0.5, "brier": 0.2 + 0.1 * (agent == "llm"),
                                    "confident_wrong": 0, "fell_for_trap": True},
                         "ideal_on_own_data": {"exact": 0.5, "edge_acc": 0.8, "brier": 0.15}})
    summ = summarize(rows)
    hyp = {h["id"]: h for h in hypotheses(load_config(), summ, rows)}
    assert hyp["H1"]["status"] == "evaluated" and hyp["H2"]["status"] == "evaluated"
