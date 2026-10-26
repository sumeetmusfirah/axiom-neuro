"""Reference agents. Each picks designs; the ideal analyst makes the claims.

Holding the analyst fixed means the gap between these baselines is purely about
experiment choice: random < scripted (textbook factorial) < oracle (simulation-optimal).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .. import analysis as A
from ..design import Design, DesignError
from ..env import LabEnv
from ..mechanisms import TASK_TYPES, sample_mechanism
from ..params import REPO, SimParams
from ..tasks import Task

ORACLE_CACHE = REPO / "results" / "oracle_designs.json"

SCRIPTED = {"factors": ["L", "S"], "assignment": "within", "order": "counterbalanced",
            "n_participants": 24, "trials_per_cell": 80, "eeg": True, "ica": True}


def _random_design(rng: np.random.Generator) -> dict:
    factors = [["L"], ["S"], ["L", "S"]][rng.integers(3)]
    eeg = bool(rng.integers(2))
    return {
        "factors": factors,
        "fixed": {f: int(rng.integers(2)) for f in ("L", "S") if f not in factors},
        "assignment": ["within", "between"][rng.integers(2)],
        "order": ["fixed", "counterbalanced"][rng.integers(2)],
        "n_participants": int(rng.choice([8, 12, 16, 24, 32, 48])),
        "trials_per_cell": int(rng.choice([40, 80, 120, 160])),
        "eeg": eeg,
        "ica": eeg and bool(rng.integers(2)),
    }


def run_random(env: LabEnv, seed: int) -> None:
    rng = np.random.default_rng([env.task.seed, seed, 7])
    for _ in range(40):  # attempts; stops when nothing affordable is drawn
        d = _random_design(rng)
        try:
            if env.cost_of(d) <= env.remaining:
                env.step("design_experiment", d)
        except DesignError:
            continue
        if env.remaining < 2:
            break
    _ideal_submit(env)


def run_scripted(env: LabEnv, seed: int) -> None:
    env.step("design_experiment", SCRIPTED)
    _ideal_submit(env)


def run_oracle(env: LabEnv, seed: int) -> None:
    designs = load_oracle_designs()
    key = TASK_TYPES[env.task.task_type].starter.note
    env.step("design_experiment", designs[key]["design"])
    _ideal_submit(env)


def _ideal_submit(env: LabEnv) -> None:
    claims = A.ideal_claims(env.collected())
    env.step("submit", {"edges": {e: {"present": c["present"], "confidence": c["confidence"]}
                                  for e, c in claims.items()}})


# ------------------------------------------------------------------ oracle precompute

def candidate_designs(budget: float) -> list[dict]:
    out = []
    shapes = [(["L"], {"S": 0}), (["L"], {"S": 1}), (["S"], {"L": 0}), (["S"], {"L": 1}), (["L", "S"], {})]
    for factors, fixed in shapes:
        for assignment in ("within", "between"):
            for n in (8, 16, 24, 32, 48, 64):
                for trials in (40, 80, 160):
                    for eeg in (False, True):
                        d = {"factors": factors, "fixed": fixed, "assignment": assignment,
                             "order": "counterbalanced", "n_participants": n,
                             "trials_per_cell": trials, "eeg": eeg, "ica": eeg}
                        try:
                            if Design.from_dict(json.loads(json.dumps(d))).cost() <= budget:
                                out.append(d)
                        except DesignError:
                            pass
    return out


def precompute_oracle(params: SimParams, budget: float, sims_per_type: int = 8,
                      seed: int = 0, path: Path = ORACLE_CACHE) -> dict:
    """For each starter, the single design that minimises the ideal analyst's expected
    Brier score (the preregistered primary metric) over every task type sharing that
    starter (P->Y coin flip included)."""
    from ..scoring import score
    groups: dict[str, list[str]] = {}
    for name, tt in TASK_TYPES.items():
        groups.setdefault(tt.starter.note, []).append(name)
    result = {}
    cands = candidate_designs(budget)
    for note, types in groups.items():
        rng = np.random.default_rng(seed)
        worlds = []
        for t in types:
            for _ in range(sims_per_type):
                worlds.append((sample_mechanism(t, rng), int(rng.integers(0, 2**31 - 1))))
        best, best_score, best_exact = None, float("inf"), 0.0
        for d in cands:
            brier, hits = 0.0, 0.0
            for mech, s in worlds:
                task = Task("oracle", mech.task_type, "train", s, budget, mech)
                env = LabEnv(task, params, "synthetic", "named", run_seed=s)
                env.step("design_experiment", d)
                claims = A.ideal_claims(env.collected())
                sc = score(claims, mech.truth(), mech.task_type)
                brier += sc["brier"]
                hits += sc["exact"]
            mean_brier = brier / len(worlds)
            if mean_brier < best_score - 1e-12:
                best, best_score, best_exact = d, mean_brier, hits / len(worlds)
        result[note] = {"design": best, "expected_brier": round(best_score, 4),
                        "expected_exact": round(best_exact, 4), "task_types": types}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"budget": budget, "sims_per_type": sims_per_type,
                                "params_source": params.source, "designs": result}, indent=2))
    return result


def load_oracle_designs(path: Path = ORACLE_CACHE) -> dict:
    if not path.exists():
        raise FileNotFoundError("oracle designs not computed; run `axiom oracle`")
    return json.loads(path.read_text())["designs"]
