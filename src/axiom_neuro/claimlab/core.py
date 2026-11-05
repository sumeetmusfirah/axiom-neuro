"""Claim labs: real tabular data, a sampling budget, and claims with known answers.

A claim lab gives the agent a population it can only see by buying samples from named sources
(all people, or a stratum such as "women" or "people who reoffended"). It analyses what it bought
with a few free tools, then states, for each candidate claim, whether it is true and how sure it is.

Every claim is an estimand with a threshold, e.g. "P(high risk | not rearrested, group A) minus the
same for group B is above 0.10". Its truth is fixed from the full data (or from planted parameters
on semi-synthetic tracks) when tasks are frozen, so scoring needs no judge. The same estimands, run
on only the agent's own samples, give the ideal analysis of its own data.

Traps are claims where the obvious analysis gives the wrong answer: a confounded association read as
an effect, an unweighted survey estimate, a base rate read off a stratified sample, a reversed gap.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

ACTIONS = ("sample", "summarize", "regress", "submit")
MIN_N, MAX_N = 50, 800



def _w(df: pd.DataFrame, weight: str | None, weighted: bool) -> np.ndarray:
    if weighted and weight and weight in df:
        w = df[weight].to_numpy(float)
        return w / w.mean()
    return np.ones(len(df))


def _filter(df: pd.DataFrame, where: dict | None) -> pd.DataFrame:
    for k, v in (where or {}).items():
        df = df[df[k] == v]
    return df


def wmean(x: np.ndarray, w: np.ndarray) -> tuple[float, float]:
    """Weighted mean and its standard error (Kish effective sample size)."""
    if len(x) == 0:
        return float("nan"), float("inf")
    m = float(np.average(x, weights=w))
    n_eff = w.sum() ** 2 / (w ** 2).sum()
    var = float(np.average((x - m) ** 2, weights=w))
    return m, float(np.sqrt(var / max(n_eff - 1, 1)))


def mean_of(df, var, where=None, weight=None, weighted=False):
    d = _filter(df, where)
    return wmean(d[var].to_numpy(float), _w(d, weight, weighted))


def gap(df, var, by, a, b, where=None, weight=None, weighted=False):
    """mean(var | by=a) - mean(var | by=b), within `where`."""
    d = _filter(df, where)
    ma, sa = mean_of(d[d[by] == a], var, None, weight, weighted)
    mb, sb = mean_of(d[d[by] == b], var, None, weight, weighted)
    return ma - mb, float(np.hypot(sa, sb))


def ols(df, outcome, predictors, weight=None, weighted=False):
    """Weighted least squares with HC1 robust standard errors. Returns {name: (coef, se)}."""
    d = df[[outcome, *predictors] + ([weight] if weight and weight in df else [])].dropna()
    X = np.column_stack([np.ones(len(d))] + [d[p].to_numpy(float) for p in predictors])
    y = d[outcome].to_numpy(float)
    w = _w(d, weight, weighted)
    k = X.shape[1]
    if len(d) <= k + 1:
        return {p: (float("nan"), float("inf")) for p in predictors}
    sw = np.sqrt(w)
    Xw, yw = X * sw[:, None], y * sw
    xtx_inv = np.linalg.pinv(Xw.T @ Xw)
    beta = xtx_inv @ Xw.T @ yw
    resid = yw - Xw @ beta
    meat = (Xw * resid[:, None]).T @ (Xw * resid[:, None])
    cov = xtx_inv @ meat @ xtx_inv * len(d) / (len(d) - k)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    return {p: (float(beta[i + 1]), float(se[i + 1])) for i, p in enumerate(predictors)}


def estimate(df: pd.DataFrame, est: dict, weight: str | None) -> tuple[float, float]:
    kind = est["kind"]
    wtd = est.get("weighted", False)
    if kind == "mean":
        return mean_of(df, est["var"], est.get("where"), weight, wtd)
    if kind == "gap":
        return gap(df, est["var"], est["by"], est["a"], est["b"], est.get("where"), weight, wtd)
    if kind == "coef":
        return ols(_filter(df, est.get("where")), est["outcome"], est["predictors"], weight, wtd)[est["target"]]
    if kind == "coefdiff":  # coefficient among where_a minus the same among where_b
        a = ols(_filter(df, est["where_a"]), est["outcome"], est["predictors"], weight, wtd)[est["target"]]
        b = ols(_filter(df, est["where_b"]), est["outcome"], est["predictors"], weight, wtd)[est["target"]]
        return a[0] - b[0], float(np.hypot(a[1], b[1]))
    raise ValueError(kind)


def describe(est: dict, op: str, thr: float, names: dict) -> str:
    """Plain wording of a claim from its estimand, used for the abstract-label track."""
    def cond(w):
        return " and ".join(f"{names[k]} = {v}" for k, v in (w or {}).items())
    where = f" among rows with {cond(est['where'])}" if est.get("where") else ""
    pop = " in the population the data represent" if est.get("weighted") else ""
    rel = {">": f"is greater than {thr:g}", "<": f"is less than {thr:g}", "abs<": f"is within ±{thr:g} of zero"}[op]
    k = est["kind"]
    if k == "mean":
        return f"The mean of {names[est['var']]}{where}{pop} {rel}."
    if k == "gap":
        return (f"The mean of {names[est['var']]} when {names[est['by']]} = {est['a']}, minus the mean when "
                f"{names[est['by']]} = {est['b']}{where}{pop}, {rel}.")
    preds = ", ".join(names[p] for p in est["predictors"])
    if k == "coef":
        return f"In a regression of {names[est['outcome']]} on {preds}{where}{pop}, the coefficient on {names[est['target']]} {rel}."
    return (f"The coefficient on {names[est['target']]} in a regression of {names[est['outcome']]} on {preds}, among rows "
            f"with {cond(est['where_a'])}, minus the same coefficient among rows with {cond(est['where_b'])}{pop}, {rel}.")


def prob_true(value: float, se: float, op: str, thr: float) -> float:
    """Probability the claim holds, treating the estimate as normal(value, se)."""
    if not np.isfinite(value) or not np.isfinite(se):
        return 0.5
    se = max(se, 1e-9)
    if op == ">":
        return float(stats.norm.sf((thr - value) / se))
    if op == "<":
        return float(stats.norm.cdf((thr - value) / se))
    if op == "abs<":
        return float(stats.norm.cdf((thr - value) / se) - stats.norm.cdf((-thr - value) / se))
    raise ValueError(op)


def holds(value: float, op: str, thr: float) -> bool:
    return {">": value > thr, "<": value < thr, "abs<": abs(value) < thr}[op]



@dataclass
class ClaimTask:
    task_id: str
    seed: int
    claims: dict  # cid -> {"named", "est", "op", "thr", "truth", "trap"}; abstract wording comes from est
    budget: int
    plant: dict = field(default_factory=dict)  # semi-synthetic parameters, if any
    task_type: str = "claims"
    split: str = "train"

    def truth(self) -> dict:
        return {c: bool(v["truth"]) for c, v in self.claims.items()}

    def to_json(self) -> dict:
        return {"task_id": self.task_id, "seed": self.seed, "claims": self.claims, "budget": self.budget,
                "plant": self.plant}

    @classmethod
    def from_json(cls, d: dict) -> "ClaimTask":
        return cls(d["task_id"], d["seed"], d["claims"], d["budget"], d.get("plant", {}))


def freeze(tasks: list[ClaimTask], manifest, sha_path) -> str:
    text = "".join(json.dumps(t.to_json(), sort_keys=True) + "\n" for t in tasks)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(text)
    h = hashlib.sha256(text.encode()).hexdigest()
    sha_path.write_text(h + "\n")
    return h


def load(manifest) -> list[ClaimTask]:
    return [ClaimTask.from_json(json.loads(l)) for l in manifest.read_text().splitlines() if l.strip()]



@dataclass
class Episode:
    task_id: str
    actions: list = field(default_factory=list)
    spent: int = 0
    submitted: dict | None = None
    edges_claimed: int = 0  # number of claims answered (named for compatibility with the ledger)


class ClaimLab:
    """One episode. `spec` is a domain module (health, ethics) that supplies the data and wording."""
    ACTIONS = ACTIONS
    BUDGET_UNIT = "rows"

    def __init__(self, spec, task: ClaimTask, labels: str = "named", run_seed: int = 0):
        self.spec, self.task, self.labels = spec, task, labels
        self.frame = spec.frame(task)
        self.vars = spec.VARIABLES  # internal -> (named label, abstract label, description)
        self.names = {v: (t[0] if labels == "named" else t[1]) for v, t in self.vars.items()}
        self.inv = {n: v for v, n in self.names.items()}
        self.values = spec.value_labels(labels)  # internal var -> {internal value: shown value}
        self.rng = np.random.default_rng([task.seed, run_seed])
        self.used: dict[str, set] = {s: set() for s in spec.SOURCES}
        self.datasets: dict[str, pd.DataFrame] = {}
        self.episode = Episode(task.task_id)

    @property
    def remaining(self) -> int:
        return self.task.budget - self.episode.spent

    def _source_text(self, s: str) -> str:
        named, abstract = self.spec.SOURCES[s][:2]
        return named if self.labels == "named" else abstract

    def _claim_text(self, c: str) -> str:
        v = self.task.claims[c]
        return v["named"] if self.labels == "named" else describe(v["est"], v["op"], v["thr"], self.names)

    def protocol(self) -> str:
        oh = self.spec.OVERHEAD
        return f"""
Reply with ONE JSON object per turn: {{"thought": "<one or two sentences>", "action": "<name>", "args": {{...}}}}

Actions and their args:
  sample     {{"source": "<id>", "n": 300}}       buy n rows ({MIN_N}-{MAX_N}) from a source (spends budget)
  summarize  {{"datasets": ["D1"], "variable": "<var>", "by": "<var or null>", "where": {{"<var>": <value>}}, "weighted": false}}
             mean (for 0/1 variables: proportion) with standard error, overall or per group
  regress    {{"datasets": ["D1"], "outcome": "<var>", "predictors": ["<var>", ...], "where": {{}}, "weighted": false}}
             least squares with robust standard errors (0/1 outcomes give a linear probability model)
  submit     {{"claims": {{"C1": {{"true": true, "confidence": 0.8}}, ... every claim ...}}}}
             confidence = your probability (0.5-1.0) that your true/false call is right.
Each sample costs n + {oh}. Analysis is free. "weighted" uses survey weights where the data have them.
Submit before turns run out.""".strip()

    def briefing(self) -> str:
        srcs = "\n".join(f"  {s}: {self._source_text(s)}" for s in self.spec.SOURCES)
        vs = "\n".join(f"  {self.names[v]}: {self._var_desc(v)}" for v in self.vars)
        claims = "\n".join(f"  {c}: {self._claim_text(c)}" for c in self.task.claims)
        return "\n".join([
            self.spec.intro(self.labels), "",
            "Sources you can sample from:", srcs, "",
            "Variables in every row:", vs, "",
            f"Budget: {self.task.budget} rows.", "",
            "Decide whether each claim is true of the whole population the sources come from:", claims,
        ])

    def _var_desc(self, v: str) -> str:
        desc = self.vars[v][2 if self.labels == "named" else 3]
        vals = self.values.get(v)
        if vals:
            desc += " (values: " + ", ".join(str(x) for x in vals.values()) + ")"
        return desc

    def _var(self, name) -> str:
        if name in self.inv:
            return self.inv[name]
        raise ValueError(f"unknown variable {name}; use {list(self.inv)}")

    def _val(self, var: str, shown):
        for internal, s in self.values.get(var, {}).items():
            if s == shown or str(s) == str(shown):
                return internal
        return shown

    def _where(self, where) -> dict:
        if not where:
            return {}
        if not isinstance(where, dict):
            raise ValueError("where must be an object like {\"<var>\": <value>}")
        return {self._var(k): self._val(self._var(k), v) for k, v in where.items()}

    def _ds(self, ids) -> pd.DataFrame:
        ids = [ids] if isinstance(ids, str) else (ids or [])
        if not ids:
            raise ValueError(f"name at least one dataset; available: {list(self.datasets)}")
        out = []
        for i in ids:
            if i not in self.datasets:
                raise ValueError(f"unknown dataset {i}; available: {list(self.datasets)}")
            out.append(self.datasets[i])
        return pd.concat(out)

    def step(self, action: str, args: dict) -> dict:
        args = args or {}
        try:
            obs = self._step(action, args)
        except (ValueError, KeyError, TypeError) as exc:
            obs = {"error": str(exc)}
        self.episode.actions.append({"action": action, "args": args, "obs": obs, "spent": self.episode.spent})
        return obs

    def _step(self, action: str, args: dict) -> dict:
        if self.episode.submitted is not None:
            return {"error": "already submitted"}
        if action == "sample":
            s = str(args.get("source"))
            if s not in self.spec.SOURCES:
                return {"error": f"unknown source {s}; use {list(self.spec.SOURCES)}"}
            n = int(args.get("n", 300))
            if not MIN_N <= n <= MAX_N:
                return {"error": f"n must be {MIN_N}-{MAX_N}"}
            cost = n + self.spec.OVERHEAD
            if cost > self.remaining:
                return {"error": f"costs {cost}; only {self.remaining} left"}
            mask = self.spec.SOURCES[s][2](self.frame)
            pool = self.frame.index[mask].difference(list(self.used[s]))
            if len(pool) < n:
                return {"error": f"only {len(pool)} unused rows left in {s}"}
            idx = self.rng.choice(pool, n, replace=False)
            self.used[s].update(idx.tolist())
            did = f"D{len(self.datasets) + 1}"
            self.datasets[did] = self.frame.loc[idx]
            self.episode.spent += cost
            return {"dataset": did, "source": s, "rows": n, "remaining_budget": self.remaining}
        if action == "summarize":
            df = self._ds(args.get("datasets"))
            var = self._var(args.get("variable"))
            df = _filter(df, self._where(args.get("where")))
            wtd = bool(args.get("weighted", False))
            by = args.get("by")
            if by:
                b = self._var(by)
                out = {}
                for g, d in df.groupby(b):
                    m, se = mean_of(d, var, None, self.spec.WEIGHT, wtd)
                    out[str(self.values.get(b, {}).get(g, g))] = {"mean": round(m, 4), "se": round(se, 4), "n": len(d)}
                return {"by": by, "groups": out}
            m, se = mean_of(df, var, None, self.spec.WEIGHT, wtd)
            return {"mean": round(m, 4), "se": round(se, 4), "n": len(df)}
        if action == "regress":
            df = self._ds(args.get("datasets"))
            y = self._var(args.get("outcome"))
            preds = [self._var(p) for p in (args.get("predictors") or [])]
            preds = [p for p in dict.fromkeys(preds) if p != y]
            if not preds:
                return {"error": "name at least one predictor"}
            df = _filter(df, self._where(args.get("where")))
            res = ols(df, y, preds, self.spec.WEIGHT, bool(args.get("weighted", False)))
            out = {}
            for p, (b, se) in res.items():
                pv = float(2 * stats.norm.sf(abs(b / se))) if se and np.isfinite(se) and se > 0 else 1.0
                out[self.names[p]] = {"coef": round(b, 4), "se": round(se, 4), "p": float(f"{pv:.3g}")}
            return {"n": len(df), "coefficients": out}
        if action == "submit":
            return self.submit(args.get("claims", {}))
        return {"error": f"unknown action {action}; valid: {list(ACTIONS)}"}

    def submit(self, claims: dict) -> dict:
        claims = claims if isinstance(claims, dict) else {}
        self.episode.edges_claimed = sum(c in claims for c in self.task.claims)
        clean = {}
        for c in self.task.claims:
            v = claims.get(c, {})
            v = v if isinstance(v, dict) else {}
            try:
                conf = float(v.get("confidence", 0.5))
            except (TypeError, ValueError):
                conf = 0.5
            clean[c] = {"present": bool(v.get("true", v.get("present", False))),
                        "confidence": float(np.clip(conf, 0, 1))}
        self.episode.submitted = clean
        return {"ok": True}



def reference_claims(spec, task: ClaimTask, datasets: dict) -> dict:
    """Each claim's estimand computed on exactly the rows the agent bought, nothing else."""
    df = pd.concat(datasets.values()) if datasets else None
    out = {}
    for c, v in task.claims.items():
        p = 0.5 if df is None or len(df) < 20 else prob_true(*estimate(df, v["est"], spec.WEIGHT), v["op"], v["thr"])
        p = float(np.clip(p, 0.02, 0.98))
        out[c] = {"present": p > 0.5, "confidence": round(max(p, 1 - p), 3)}
    return out


def run_random(lab: ClaimLab, seed: int) -> None:
    rng = np.random.default_rng([lab.task.seed, seed, 11])
    while lab.remaining >= MIN_N + lab.spec.OVERHEAD:
        n = int(min(rng.choice([150, 300, 500]), lab.remaining - lab.spec.OVERHEAD, MAX_N))
        if "error" in lab.step("sample", {"source": str(rng.choice(list(lab.spec.SOURCES))), "n": n}):
            break
    lab.submit({c: {"true": v["present"], "confidence": v["confidence"]}
                for c, v in reference_claims(lab.spec, lab.task, lab.datasets).items()})


def run_scripted(lab: ClaimLab, seed: int) -> None:
    """Spend the whole budget on the unstratified source, then analyse it."""
    while lab.remaining >= MIN_N + lab.spec.OVERHEAD:
        n = int(min(MAX_N, lab.remaining - lab.spec.OVERHEAD))
        if "error" in lab.step("sample", {"source": "all", "n": n}):
            break
    lab.submit({c: {"true": v["present"], "confidence": v["confidence"]}
                for c, v in reference_claims(lab.spec, lab.task, lab.datasets).items()})


def score(claims: dict, task: ClaimTask) -> dict:
    truth = task.truth()
    correct = {c: claims[c]["present"] == truth[c] for c in truth}
    p = {c: (claims[c]["confidence"] if claims[c]["present"] else 1 - claims[c]["confidence"]) for c in truth}
    out = {
        "exact": float(all(correct.values())),
        "edge_acc": float(np.mean(list(correct.values()))),
        "brier": float(np.mean([(p[c] - truth[c]) ** 2 for c in truth])),
        "confident_wrong": int(sum((not correct[c]) and claims[c]["confidence"] >= 0.8 for c in truth)),
        "edge_correct": correct,
    }
    traps = [c for c in truth if task.claims[c].get("trap")]
    out["fell_for_trap"] = bool(any(not correct[c] for c in traps))
    for kind in sorted({task.claims[c]["trap"] for c in traps}):
        cs = [c for c in traps if task.claims[c]["trap"] == kind]
        out[f"wrong_{kind}"] = float(np.mean([not correct[c] for c in cs]))
    return out
