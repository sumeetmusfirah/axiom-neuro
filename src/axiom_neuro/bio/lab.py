"""Axiom-Bio: a signalling lab on real single cells (Sachs et al. 2005).

Each task asks about six candidate directed edges among the eleven measured molecules.
Candidates mix true edges of the consensus graph with three kinds of tempting falsehoods:
  reversed     the true edge points the other way
  indirect     X reaches Y only through another molecule
  confounded   X and Y share an upstream regulator but neither reaches the other
An agent buys real cells from the conditions it chooses (within a budget) and analyses them.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

from ..params import REPO
from .data import CONDITIONS, PROTEINS, load_cells, load_graph

BIO_MANIFEST = REPO / "tasks" / "bio_manifest.jsonl"
BUDGET_CELLS = 2400
MAX_CELLS_PER_RUN = 800
CONDITION_OVERHEAD = 100  # cells' worth of cost per condition run: discourages scattershot sampling
ACTIONS = ("run_condition", "describe", "compare", "correlate", "submit")


# ----------------------------------------------------------------------------- graph helpers

def _reach(edges: frozenset) -> dict[str, set]:
    adj = {p: set() for p in PROTEINS}
    for e in edges:
        a, b = e.split("->")
        adj[a].add(b)
    reach = {}
    for p in PROTEINS:
        seen, stack = set(), list(adj[p])
        while stack:
            q = stack.pop()
            if q not in seen:
                seen.add(q)
                stack.extend(adj[q])
        reach[p] = seen
    return reach


def classify_pairs(edges: frozenset) -> dict[str, list[str]]:
    reach = _reach(edges)
    out = {"true": sorted(edges), "reversed": [], "indirect": [], "confounded": []}
    for a, b in itertools.permutations(PROTEINS, 2):
        e = f"{a}->{b}"
        if e in edges:
            continue
        if f"{b}->{a}" in edges:
            out["reversed"].append(e)
        elif b in reach[a]:
            out["indirect"].append(e)
        elif a not in reach[b] and any(a in reach[c] and b in reach[c] for c in PROTEINS):
            out["confounded"].append(e)
    return out


@dataclass
class BioTask:
    task_id: str
    seed: int
    candidates: list  # six directed edges
    kinds: dict  # edge -> true | reversed | indirect | confounded
    budget: int = BUDGET_CELLS
    task_type: str = "bio_signalling"
    split: str = "train"

    def truth(self) -> dict:
        return {e: self.kinds[e] == "true" for e in self.candidates}

    def to_json(self) -> dict:
        return {"task_id": self.task_id, "seed": self.seed, "candidates": self.candidates,
                "kinds": self.kinds, "budget": self.budget}

    @classmethod
    def from_json(cls, d: dict) -> "BioTask":
        return cls(d["task_id"], d["seed"], d["candidates"], d["kinds"], d["budget"])


def build_bio_tasks(seed: int, n: int) -> list[BioTask]:
    pairs = classify_pairs(load_graph())
    rng = np.random.default_rng(seed)
    tasks = []
    for i in range(n):
        n_true = int(rng.integers(2, 4))
        pick = list(rng.choice(pairs["true"], n_true, replace=False))
        for kind in ("reversed", "indirect", "confounded"):
            pool = [e for e in pairs[kind] if e not in pick]
            pick.append(str(rng.choice(pool)))
        rest = [e for k in ("reversed", "indirect", "confounded") for e in pairs[k] if e not in pick]
        while len(pick) < 6:
            pick.append(str(rng.choice(rest)))
            rest = [e for e in rest if e not in pick]
        rng.shuffle(pick)
        kinds = {e: next(k for k in ("true", "reversed", "indirect", "confounded") if e in pairs[k]) for e in pick}
        tasks.append(BioTask(f"bio-{i:02d}", int(rng.integers(0, 2**31 - 1)), list(pick), kinds))
    return tasks


# ----------------------------------------------------------------------------- analysis

def _names(labels: str) -> dict:
    return {p: (p if labels == "named" else f"M{i + 1}") for i, p in enumerate(PROTEINS)}


def partial_spearman(df: pd.DataFrame, x: str, y: str, given: list[str]) -> tuple[float, float, int]:
    r = df[[x, y, *given]].rank()
    if given:
        Z = np.column_stack([np.ones(len(r)), r[given].to_numpy()])
        rx = r[x] - Z @ np.linalg.lstsq(Z, r[x], rcond=None)[0]
        ry = r[y] - Z @ np.linalg.lstsq(Z, r[y], rcond=None)[0]
    else:
        rx, ry = r[x] - r[x].mean(), r[y] - r[y].mean()
    rho = float(np.corrcoef(rx, ry)[0, 1])
    n = len(r)
    t = rho * np.sqrt(max(n - 2 - len(given), 1) / max(1 - rho ** 2, 1e-9))
    p = float(2 * stats.t.sf(abs(t), max(n - 2 - len(given), 1)))
    return rho, p, n


def shift(a: pd.DataFrame, b: pd.DataFrame, protein: str) -> tuple[float, float]:
    """Median log-intensity shift b - a, and Mann-Whitney p."""
    d = float(b[protein].median() - a[protein].median())
    p = float(stats.mannwhitneyu(a[protein], b[protein]).pvalue)
    return d, p


def reference_claims(task: BioTask, datasets: dict[str, pd.DataFrame]) -> dict:
    """A careful but simple analyst. For X->Y:
      intervention evidence: a condition targeting X (with its matched CD3/CD28 context available)
                             shifts Y  -> X is upstream of Y (directly or not)
      directness: partial correlation of X and Y given all other molecules, in context-matched data
    Without any targeting condition, orientation is unidentified (confidence 0.5)."""
    by_cond: dict[str, list] = {}
    for d in datasets.values():
        by_cond.setdefault(d["condition"].iloc[0], []).append(d)
    pooled = {c: pd.concat(v) for c, v in by_cond.items()}
    obs = pd.concat([pooled[c] for c in ("baseline", "icam2") if c in pooled]) if \
        any(c in pooled for c in ("baseline", "icam2")) else None
    claims = {}
    for e in task.candidates:
        x, y = e.split("->")
        evidence = []
        if "baseline" in pooled:
            for c, (_f, _d, target, _eff, context) in CONDITIONS.items():
                if target == x and c in pooled and context == "cd3cd28":
                    d, p = shift(pooled["baseline"], pooled[c], y)
                    evidence.append(abs(d) > 0.2 and p < 0.001)
        reverse = []
        if "baseline" in pooled:
            for c, (_f, _d, target, _eff, context) in CONDITIONS.items():
                if target == y and c in pooled and context == "cd3cd28":
                    d, p = shift(pooled["baseline"], pooled[c], x)
                    reverse.append(abs(d) > 0.2 and p < 0.001)
        direct = None
        if obs is not None and len(obs) > 50:
            others = [p for p in PROTEINS if p not in (x, y)]
            rho, p, _ = partial_spearman(obs, x, y, others)
            direct = abs(rho) > 0.1 and p < 0.001
        if evidence:
            upstream = any(evidence)
            if not upstream:
                post = 0.2
            elif direct is None:
                post = 0.6
            else:
                post = 0.85 if direct else 0.3
        elif reverse and any(reverse):
            post = 0.15  # Y drives X: X->Y unlikely
        elif direct is not None:
            post = 0.55 if direct else 0.2
        else:
            post = 0.5
        claims[e] = {"present": post > 0.5, "confidence": round(max(post, 1 - post), 3)}
    return claims


# ----------------------------------------------------------------------------- environment

@dataclass
class BioEpisode:
    task_id: str
    actions: list = field(default_factory=list)
    spent: int = 0
    submitted: dict | None = None
    edges_claimed: int = 0


class BioLab:
    ACTIONS = ACTIONS

    def __init__(self, task: BioTask, labels: str = "named", run_seed: int = 0):
        self.task = task
        self.labels = labels
        self.names = _names(labels)
        self.inv = {v: k for k, v in self.names.items()}
        self.rng = np.random.default_rng([task.seed, run_seed])
        self.cells = load_cells()
        self.used: dict[str, set] = {c: set() for c in CONDITIONS}
        self.datasets: dict[str, pd.DataFrame] = {}
        self.episode = BioEpisode(task.task_id)

    @property
    def remaining(self) -> int:
        return self.task.budget - self.episode.spent

    def _cond_text(self, c: str) -> str:
        _f, desc, target, effect, _ctx = CONDITIONS[c]
        if self.labels == "abstract":
            desc = desc.replace("CD3/CD28", "standard stimulation")
            for reagent in ("AKT inhibitor", "G06976", "Psitectorigenin", "U0126", "LY294002", "PMA", "beta2cAMP",
                            "ICAM-2"):
                desc = desc.replace(reagent, "a compound" if reagent != "ICAM-2" else "a co-stimulus")
        return desc + (f"; {effect} {self.names[target]}" if target else "")

    def protocol(self) -> str:
        return f"""
Reply with ONE JSON object per turn: {{"thought": "<one or two sentences>", "action": "<name>", "args": {{...}}}}

Actions and their args:
  run_condition  {{"condition": "<id>", "n_cells": 400}}     buy real cells from a condition (spends budget)
  describe       {{"datasets": ["C1"]}}                      median log-intensity of every molecule
  compare        {{"dataset_a": "C1", "dataset_b": "C2"}}    median shift (b - a) per molecule, Mann-Whitney p
  correlate      {{"datasets": ["C1"], "x": "<mol>", "y": "<mol>", "given": ["<mol>", ...]}}  (partial) Spearman
  submit         {{"edges": {{"<X>-><Y>": {{"present": true, "confidence": 0.8}}, ... all six candidates ...}}}}
                 confidence = your probability (0.5-1.0) that your present/absent call is right.
Each condition run costs n_cells + {CONDITION_OVERHEAD}. Analysis is free. Submit before turns run out.""".strip()

    def briefing(self) -> str:
        n = self.names
        conds = "\n".join(f"  {c}: {self._cond_text(c)}" for c in CONDITIONS)
        cands = "\n".join(f"  {self._edge_out(e)}" for e in self.task.candidates)
        intro = ("You run a single-cell signalling lab. Flow cytometry measures 11 phospho-proteins and "
                 "phospholipids in human CD4+ T cells." if self.labels == "named" else
                 "You run a single-cell lab. An instrument measures 11 molecules in individual cells.")
        return "\n".join([
            intro,
            "Decide, for each candidate below, whether X DIRECTLY regulates Y (an arrow in the signalling network, "
            "not a path through another measured molecule, and not merely a shared upstream regulator).",
            "", f"Molecules: {', '.join(n[p] for p in PROTEINS)}", "",
            "Conditions you can buy cells from:", conds, "",
            f"Budget: {self.task.budget} cells. Values are log intensities.", "",
            "Candidate edges (judge every one):", cands,
        ])

    def _edge_out(self, e: str) -> str:
        a, b = e.split("->")
        return f"{self.names[a]}->{self.names[b]}"

    def _edge_in(self, e: str) -> str:
        a, b = (s.strip() for s in e.split("->"))
        return f"{self.inv.get(a, a)}->{self.inv.get(b, b)}"

    def _mol(self, m: str) -> str:
        if m in self.inv:
            return self.inv[m]
        raise ValueError(f"unknown molecule {m}; use {list(self.inv)}")

    def _rename(self, df: pd.DataFrame) -> dict:
        return {self.names[p]: round(float(v), 3) for p, v in df[list(PROTEINS)].median().items()}

    def step(self, action: str, args: dict) -> dict:
        args = args or {}
        try:
            obs = self._step(action, args)
        except (ValueError, KeyError, TypeError) as exc:
            obs = {"error": str(exc)}
        self.episode.actions.append({"action": action, "args": args, "obs": obs, "spent": self.episode.spent})
        return obs

    def _ds(self, i: str) -> pd.DataFrame:
        if i in self.datasets:
            return self.datasets[i]
        # Accept a condition name as an alias for the latest dataset bought from it:
        # the benchmark measures scientific judgement, not bookkeeping of dataset ids.
        for did in reversed(list(self.datasets)):
            if self.datasets[did]["condition"].iloc[0] == i:
                return self.datasets[did]
        raise ValueError(f"unknown dataset {i}; available: {list(self.datasets)} "
                         f"(or the name of a condition you have already run)")

    def _step(self, action: str, args: dict) -> dict:
        if self.episode.submitted is not None:
            return {"error": "already submitted"}
        if action == "run_condition":
            c = str(args.get("condition"))
            if c not in CONDITIONS:
                return {"error": f"unknown condition {c}; use {list(CONDITIONS)}"}
            n = int(args.get("n_cells", 400))
            if not 50 <= n <= MAX_CELLS_PER_RUN:
                return {"error": f"n_cells must be 50-{MAX_CELLS_PER_RUN}"}
            cost = n + CONDITION_OVERHEAD
            if cost > self.remaining:
                return {"error": f"costs {cost}; only {self.remaining} left"}
            pool = self.cells.index[self.cells["condition"] == c].difference(list(self.used[c]))
            if len(pool) < n:
                return {"error": f"only {len(pool)} unused cells left in {c}"}
            idx = self.rng.choice(pool, n, replace=False)
            self.used[c].update(idx.tolist())
            did = f"C{len(self.datasets) + 1}"
            self.datasets[did] = self.cells.loc[idx]
            self.episode.spent += cost
            return {"dataset": did, "condition": c, "cells": n, "remaining_budget": self.remaining,
                    "median_log_intensity": self._rename(self.datasets[did])}
        if action == "describe":
            ids = args.get("datasets") or []
            ids = [ids] if isinstance(ids, str) else ids
            return {i: self._rename(self._ds(i)) for i in ids}
        if action == "compare":
            a, b = self._ds(args.get("dataset_a")), self._ds(args.get("dataset_b"))
            out = {}
            for p in PROTEINS:
                d, pv = shift(a, b, p)
                out[self.names[p]] = {"shift": round(d, 3), "p": float(f"{pv:.3g}")}
            return {"shift_b_minus_a": out}
        if action == "correlate":
            ids = args.get("datasets") or []
            ids = [ids] if isinstance(ids, str) else ids
            df = pd.concat([self._ds(i) for i in ids])
            x, y = self._mol(args.get("x")), self._mol(args.get("y"))
            given = list(dict.fromkeys(g for g in (self._mol(g) for g in args.get("given") or []) if g not in (x, y)))
            rho, p, n = partial_spearman(df, x, y, given)
            return {"rho": round(rho, 3), "p": float(f"{p:.3g}"), "n_cells": n}
        if action == "submit":
            return self.submit(args.get("edges", {}))
        return {"error": f"unknown action {action}; valid: {list(ACTIONS)}"}

    def submit(self, edges: dict) -> dict:
        given = {}
        if isinstance(edges, dict):
            for k, v in edges.items():
                try:
                    given[self._edge_in(str(k))] = v
                except Exception:
                    continue
        self.episode.edges_claimed = sum(e in given for e in self.task.candidates)
        clean = {}
        for e in self.task.candidates:
            c = given.get(e, {})
            c = c if isinstance(c, dict) else {}
            try:
                conf = float(c.get("confidence", 0.5))
            except (TypeError, ValueError):
                conf = 0.5
            clean[e] = {"present": bool(c.get("present", False)), "confidence": float(np.clip(conf, 0, 1))}
        self.episode.submitted = clean
        return {"ok": True}


# ----------------------------------------------------------------------------- reference agents

def run_random(lab: BioLab, seed: int) -> None:
    rng = np.random.default_rng([lab.task.seed, seed, 11])
    while lab.remaining >= 50 + CONDITION_OVERHEAD:
        n = int(min(rng.choice([150, 300, 500]), lab.remaining - CONDITION_OVERHEAD))
        lab.step("run_condition", {"condition": str(rng.choice(list(CONDITIONS))), "n_cells": n})
    lab.step("submit", {"edges": {lab._edge_out(e): c for e, c in reference_claims(lab.task, lab.datasets).items()}})


def run_scripted(lab: BioLab, seed: int) -> None:
    """Baseline plus one context-matched condition per targeted molecule in the candidates."""
    targets = {e.split("->")[0] for e in lab.task.candidates} | {e.split("->")[1] for e in lab.task.candidates}
    plan = ["baseline"] + [c for c, v in CONDITIONS.items() if v[2] in targets and v[4] == "cd3cd28"]
    per = max(50, min(MAX_CELLS_PER_RUN, lab.task.budget // len(plan) - CONDITION_OVERHEAD))
    for c in plan:
        lab.step("run_condition", {"condition": c, "n_cells": per})
    lab.step("submit", {"edges": {lab._edge_out(e): c for e, c in reference_claims(lab.task, lab.datasets).items()}})


def score_bio(claims: dict, task: BioTask) -> dict:
    truth = task.truth()
    correct = {e: claims[e]["present"] == truth[e] for e in task.candidates}
    p = {e: (claims[e]["confidence"] if claims[e]["present"] else 1 - claims[e]["confidence"]) for e in truth}
    out = {
        "exact": float(all(correct.values())),
        "edge_acc": float(np.mean(list(correct.values()))),
        "brier": float(np.mean([(p[e] - truth[e]) ** 2 for e in truth])),
        "confident_wrong": int(sum((not correct[e]) and claims[e]["confidence"] >= 0.8 for e in truth)),
        "edge_correct": correct,
    }
    for kind in ("reversed", "indirect", "confounded"):
        es = [e for e in task.candidates if task.kinds[e] == kind]
        if es:
            out[f"claimed_{kind}"] = float(np.mean([claims[e]["present"] for e in es]))
    out["fell_for_trap"] = bool(any(claims[e]["present"] for e in task.candidates if task.kinds[e] != "true"))
    return out


def freeze_bio(tasks: list[BioTask]) -> str:
    import hashlib
    text = "".join(json.dumps(t.to_json(), sort_keys=True) + "\n" for t in tasks)
    BIO_MANIFEST.write_text(text)
    h = hashlib.sha256(text.encode()).hexdigest()
    (REPO / "tasks" / "BIO_MANIFEST.sha256").write_text(h + "\n")
    return h


def load_bio_tasks() -> list[BioTask]:
    return [BioTask.from_json(json.loads(l)) for l in BIO_MANIFEST.read_text().splitlines() if l.strip()]
