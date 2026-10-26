"""Score claims against the simulator's ground truth. No LLM judge anywhere."""

from __future__ import annotations

import numpy as np

from .mechanisms import EDGES, TASK_TYPES

CONFIDENT = 0.8


def p_present(claim: dict) -> float:
    c = float(claim.get("confidence", 0.5))
    return c if claim.get("present") else 1.0 - c


def score(claims: dict, truth: dict, task_type: str) -> dict:
    correct = {e: bool(claims[e]["present"]) == bool(truth[e]) for e in EDGES}
    tp = sum(claims[e]["present"] and truth[e] for e in EDGES)
    fp = sum(claims[e]["present"] and not truth[e] for e in EDGES)
    fn = sum((not claims[e]["present"]) and truth[e] for e in EDGES)
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 1.0
    brier = float(np.mean([(p_present(claims[e]) - float(truth[e])) ** 2 for e in EDGES]))
    conf_wrong = sum((not correct[e]) and claims[e]["confidence"] >= CONFIDENT for e in EDGES)
    trap_edge = TASK_TYPES[task_type].confound_edge
    out = {
        "exact": float(all(correct.values())),
        "edge_acc": float(np.mean(list(correct.values()))),
        "f1": float(f1),
        "brier": brier,
        "confident_wrong": int(conf_wrong),
        "edge_correct": {e: bool(v) for e, v in correct.items()},
    }
    if trap_edge is not None:
        out["fell_for_trap"] = bool(claims[trap_edge]["present"])
    return out
