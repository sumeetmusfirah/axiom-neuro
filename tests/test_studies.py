import json

from axiom_neuro import ledger as L
from axiom_neuro import runner, studies as S
from axiom_neuro.config import load_config
from axiom_neuro.mechanisms import EDGES
from axiom_neuro.params import SimParams
from axiom_neuro.tasks import build_tasks

TASKS = build_tasks(11, 1, 30.0)

BODY = """### Question

Does telling models to counterbalance stop the practice trap?

### Hypothesis

Fewer trap claims than the main study.

### Models

llama3.2:3b, qwen3:4b

### Tracks

synthetic

### Labels

named

### Task types

practice_confound, stim_main

### Instruction

Always counterbalance block order.

### Max turns

16

### Temperature

_No response_

### Budget participant hours

_No response_

### Seeds

2
"""


def _use(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "STUDIES", tmp_path / "studies")
    monkeypatch.setattr(S, "OUT", tmp_path / "out")
    (tmp_path / "studies").mkdir()


def test_issue_form_becomes_a_valid_study(tmp_path, monkeypatch):
    _use(tmp_path, monkeypatch)
    sid, text = S.from_issue(BODY, 7, "Experiment: counterbalance")
    assert sid.startswith("s007-does-telling-models")
    (S.STUDIES / f"{sid}.toml").write_text(text)
    s = S.get(sid)
    assert s["models"] == ["llama3.2:3b", "qwen3:4b"] and s["seeds"] == 2 and s["issue"] == 7
    assert s["task_types"] == ["practice_confound", "stim_main"]
    assert s["change"] == {"max_turns": 16, "instruction": "Always counterbalance block order."}


def test_study_items_have_their_own_keys_and_stay_out_of_primary(tmp_path, monkeypatch):
    _use(tmp_path, monkeypatch)
    sid, text = S.from_issue(BODY, 7, "")
    (S.STUDIES / f"{sid}.toml").write_text(text)
    items = S.pending(load_config(), set(), TASKS, [])
    # 2 models x 2 task types x 1 instance x 2 seeds
    assert len(items) == 8 and all(i["study"] == sid and f"llm@{sid}" in i["key"] for i in items)
    rows = [{"key": "a", "study": sid}, {"key": "b"}, {"key": "c", "wave": 1}]
    assert [r["key"] for r in L.primary(rows)] == ["b"]


class Recorder:
    def __init__(self):
        self.model, self.system, self.turns = "fake", None, 0

    def chat(self, messages, seed, actions=None):
        self.system = messages[0]["content"]
        self.turns += 1
        return json.dumps({"thought": "t", "action": "submit",
                           "args": {"edges": {e: {"present": False, "confidence": 0.6} for e in EDGES}}})


def test_runner_applies_the_study_change(tmp_path, monkeypatch):
    _use(tmp_path, monkeypatch)
    (S.STUDIES / "s001-x.toml").write_text(
        'id = "s001-x"\nquestion = "q"\nmodels = ["fake"]\n[change]\ninstruction = "Count to ten."\n'
        'budget_participant_hours = 60\n')
    monkeypatch.setattr(runner, "_save_transcript", lambda *a: "t")
    rec = Recorder()
    item = {"key": "k", "task_id": TASKS[0].task_id, "agent": "llm", "model": "fake", "track": "synthetic",
            "labels": "named", "seed": 0, "study": "s001-x"}
    row = runner.run_item(item, TASKS[0], SimParams(), load_config(), lambda m: rec)
    assert "Count to ten." in rec.system and row["submitted"]
    assert runner._with_budget(TASKS[0], item).budget == 60 and TASKS[0].budget == 30.0


def test_report_pairs_study_with_main_study(tmp_path, monkeypatch):
    _use(tmp_path, monkeypatch)
    (S.STUDIES / "s002-y.toml").write_text('id = "s002-y"\nquestion = "q"\nmodels = ["m"]\n')
    monkeypatch.setattr(S, "_tasks", lambda: TASKS)
    rows = []
    for t in TASKS:
        for study, brier in ((None, 0.20), ("s002-y", 0.10)):
            r = {"key": f"{t.task_id}|{study}", "status": "ok", "task_id": t.task_id, "agent": "llm", "model": "m",
                 "track": "synthetic", "labels": "named", "task_type": t.task_type,
                 "scores": {"brier": brier}, "ideal_on_own_data": {"brier": 0.05}}
            if study:
                r["study"] = study
            rows.append(r)
    cfg = load_config()
    cfg["llm"]["models"].append({"name": "m", "params_b": 1, "minutes_per_episode": 1})
    res = S.report(rows, cfg)[0]
    c = res["cells"][0]
    assert res["complete"] and round(c["diff"], 6) == -0.1 and c["verdict"] == "better"
    assert "Difference" in (S.OUT / "s002-y.md").read_text()
