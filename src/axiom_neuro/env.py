"""The lab environment an agent acts in: starter data, a budget, actions, and an episode log."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np

from . import analysis as A
from .design import Design, DesignError
from .mechanisms import EDGES, EDGE_TEXT, TASK_TYPES, VAR_TEXT
from .params import SimParams
from .simulator import generate
from .tasks import Task

ACTIONS = ("design_experiment", "describe", "regress", "order_check", "artifact_check", "submit")


@dataclass
class Episode:
    task_id: str
    actions: list = field(default_factory=list)
    spent: float = 0.0
    submitted: dict | None = None
    edges_claimed: int = 0


class LabEnv:
    def __init__(self, task: Task, params: SimParams, track: str = "synthetic",
                 labels: str = "named", run_seed: int = 0):
        self.task = task
        self.params = params
        self.track = track
        self.labels = labels
        self.rng = np.random.default_rng([task.seed, run_seed])
        self.datasets: dict[str, A.Dataset] = {}
        self.episode = Episode(task.task_id)
        tt = TASK_TYPES[task.task_type]
        st = tt.starter
        starter = Design(list(st.factors), dict(st.fixed), st.assignment, st.order,
                         st.n_participants, st.trials_per_cell, st.eeg, st.ica)
        starter.validate()
        self._add(starter, note=st.note, charge=False)

    # ------------------------------------------------------------------ helpers
    @property
    def remaining(self) -> float:
        return round(self.task.budget - self.episode.spent, 3)

    def _add(self, design: Design, note: str = "", charge: bool = True) -> A.Dataset:
        did = f"D{len(self.datasets)}"
        data = generate(design, self.task.mechanism, self.params, self.rng, self.track, id_prefix=f"{did}_")
        ds = A.Dataset(did, design, data)
        self.datasets[did] = ds
        if charge:
            self.episode.spent = round(self.episode.spent + design.cost(), 3)
        return ds

    def _pool(self, ids) -> "A.pd.DataFrame":
        ids = [ids] if isinstance(ids, str) else list(ids or [])
        missing = [i for i in ids if i not in self.datasets]
        if not ids or missing:
            raise ValueError(f"unknown dataset ids {missing or ids}; available: {list(self.datasets)}")
        return A.pd.concat([self.datasets[i].data for i in ids], ignore_index=True)

    # ------------------------------------------------------------------ public API
    def briefing(self) -> str:
        v, e = VAR_TEXT[self.labels], EDGE_TEXT[self.labels]
        d0 = self.datasets["D0"]
        lines = [
            "You are the principal investigator of a cognitive-neuroscience lab.",
            "Your job: find out which causal relations below are real, by running experiments and analysing data.",
            "",
            "Variables:",
            *[f"  {k}: {t}" for k, t in v.items()],
            "",
            "Candidate causal edges (you must judge every one):",
            *[f"  {k}: {t}" for k, t in e.items()],
            "",
            f"Budget: {self.task.budget} participant-hours. Each experiment costs participants x session length.",
            "Designs: factors to vary (subset of L, S); fixed levels for the rest; assignment within|between;",
            "order fixed|counterbalanced; n_participants 2-96; trials_per_cell 20-200; eeg true|false; ica true|false.",
            "",
            f"Existing pilot data D0 ({TASK_TYPES[self.task.task_type].starter.note if self.labels == 'named' else 'pilot study'}):",
            f"  design: {json.dumps(d0.design.to_json())}",
            f"  summary: {json.dumps(A.describe(d0.data))}",
        ]
        return "\n".join(lines)

    def cost_of(self, design_dict: dict) -> float:
        return Design.from_dict(design_dict).cost()

    def step(self, action: str, args: dict) -> dict:
        """Execute one action. Always returns a JSON-able observation; never raises."""
        args = args or {}
        try:
            obs = self._step(action, args)
        except (DesignError, ValueError, KeyError, TypeError) as exc:
            obs = {"error": str(exc)}
        self.episode.actions.append({"action": action, "args": args, "obs": obs,
                                     "spent": self.episode.spent})
        return obs

    def _step(self, action: str, args: dict) -> dict:
        if self.episode.submitted is not None:
            return {"error": "already submitted"}
        if action == "design_experiment":
            design = Design.from_dict(args)
            cost = design.cost()
            if cost > self.remaining + 1e-9:
                return {"error": f"design costs {cost} participant-hours; only {self.remaining} left"}
            ds = self._add(design)
            return {"dataset": ds.id, "cost": cost, "remaining_budget": self.remaining,
                    "summary": A.describe(ds.data)}
        if action == "describe":
            return {"summary": A.describe(self._pool(args.get("datasets")))}
        if action == "regress":
            outcome = args.get("outcome", "rt")
            terms = [t for t in args.get("predictors", ["L"]) if t != "congruent"]
            bad = [t for t in terms if t not in ("L", "S", "SxL", "practice")]
            if bad:
                return {"error": f"unknown predictors {bad}; use L, S, SxL, practice"}
            fit = A.regress(self._pool(args.get("datasets")), outcome, terms,
                            exclude_blinks=bool(args.get("exclude_blinks", False)))
            if fit is None:
                return {"error": "model not estimable on these data (no variation or no rows)"}
            dropped = [t for t in terms if t not in fit.names]
            return {"n_participants": fit.n_subjects, "rows": fit.n_rows, "coefficients": fit.table(),
                    "not_estimable": dropped}
        if action == "order_check":
            return A.order_check(self.datasets[args.get("dataset", "D0")])
        if action == "artifact_check":
            return A.artifact_check(self.datasets[args.get("dataset", "D0")])
        if action == "submit":
            return self.submit(args.get("edges", {}))
        return {"error": f"unknown action {action}; valid: {list(ACTIONS)}"}

    def submit(self, edges: dict) -> dict:
        clean = {}
        if isinstance(edges, dict):
            self.episode.edges_claimed = sum(e in edges for e in EDGES)
        for e in EDGES:
            c = edges.get(e, {}) if isinstance(edges, dict) else {}
            if not isinstance(c, dict):
                c = {}
            present = bool(c.get("present", False))
            try:
                conf = float(c.get("confidence", 0.5))
            except (TypeError, ValueError):
                conf = 0.5
            clean[e] = {"present": present, "confidence": float(np.clip(conf, 0.0, 1.0))}
        self.episode.submitted = clean
        return {"ok": True}

    def collected(self) -> list[A.Dataset]:
        return list(self.datasets.values())
