"""Statistics: cluster-robust regression, the ideal analyst, and the agent's analysis tools.

The ideal analyst knows the hypothesis family (including the practice-curve shape) and
applies a careful scientist's rules: it never trusts an effect estimated from data whose
design ties that factor to session order, and it reads theta only from blink-free trials.
It is the "analysis oracle": given any data, it shows what the best possible claim was.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from .design import Design
from .mechanisms import EDGES, practice_curve

UNIDENTIFIED = 0.5


@dataclass
class Dataset:
    id: str
    design: Design
    data: pd.DataFrame


@dataclass
class Fit:
    names: list
    beta: np.ndarray
    se: np.ndarray
    n_subjects: int
    n_rows: int

    def t(self, name: str) -> float:
        i = self.names.index(name)
        return float(self.beta[i] / self.se[i]) if self.se[i] > 0 else 0.0

    def z(self, name: str) -> float:
        """t converted to a z-equivalent with G-1 df, so few participants mean less confidence."""
        t = self.t(name)
        df = max(self.n_subjects - 1, 1)
        return float(np.sign(t) * stats.norm.isf(stats.t.sf(abs(t), df)))

    def table(self) -> list[dict]:
        out = []
        for i, n in enumerate(self.names):
            t = self.beta[i] / self.se[i] if self.se[i] > 0 else 0.0
            p = 2 * stats.t.sf(abs(t), max(self.n_subjects - 1, 1))
            out.append({"term": n, "estimate": round(float(self.beta[i]), 4),
                        "se": round(float(self.se[i]), 4), "t": round(float(t), 2), "p": float(f"{p:.3g}")})
        return out


def ols_cluster(y: np.ndarray, X: np.ndarray, groups: np.ndarray, names: list) -> Fit | None:
    """OLS with CR1 cluster-robust SEs by participant. Drops constant/collinear columns."""
    keep = [0] + [j for j in range(1, X.shape[1]) if np.std(X[:, j]) > 1e-9]
    X, names = X[:, keep], [names[j] for j in keep]
    rank = np.linalg.matrix_rank(X)
    while rank < X.shape[1]:  # drop the last collinear column until full rank
        X, names = X[:, :-1], names[:-1]
        rank = np.linalg.matrix_rank(X)
    n, k = X.shape
    ug = np.unique(groups)
    G = len(ug)
    if n <= k or G < 2:
        return None
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = y - X @ beta
    meat = np.zeros((k, k))
    idx = pd.Series(np.arange(n)).groupby(groups).indices
    for g in ug:
        rows = idx[g]
        s = X[rows].T @ u[rows]
        meat += np.outer(s, s)
    c = (G / (G - 1)) * ((n - 1) / (n - k))
    V = c * XtX_inv @ meat @ XtX_inv
    return Fit(names, beta, np.sqrt(np.clip(np.diag(V), 0, None)), G, n)


def bic_posterior(t: float, n: int) -> float:
    """P(effect present) from the BIC approximation to the Bayes factor, prior 0.5."""
    log_bf10 = (t * t - np.log(max(n, 2))) / 2.0
    return float(np.clip(1.0 / (1.0 + np.exp(-log_bf10)), 0.01, 0.99))


def _design_matrix(df: pd.DataFrame, terms: list[str], time_basis: str):
    cols = {"intercept": np.ones(len(df))}
    for term in terms:
        if term == "L":
            cols["L"] = df["L"].to_numpy(float)
        elif term == "S":
            cols["S"] = df["S"].to_numpy(float)
        elif term == "SxL":
            cols["SxL"] = (df["S"] * df["L"]).to_numpy(float)
        elif term == "practice":
            pos = df["pos"].to_numpy(float)
            cols["practice"] = practice_curve(pos) if time_basis == "curve" else pos
        elif term == "congruent":
            cols["congruent"] = df["congruent"].to_numpy(float)
        else:
            raise ValueError(f"unknown term {term}")
    names = list(cols)
    return np.column_stack([cols[n] for n in names]), names


def _rows_for(df: pd.DataFrame, outcome: str, exclude_blinks: bool) -> pd.DataFrame:
    if outcome == "rt":
        d = df[(df["correct"] == 1) & df["rt"].notna()]
    elif outcome == "accuracy":
        d = df[df["correct"].notna()]
    elif outcome in ("theta", "blink"):
        if outcome not in df:
            return df.iloc[0:0]
        d = df[df[outcome].notna()]
    else:
        raise ValueError("outcome must be rt, accuracy, theta or blink")
    if exclude_blinks and "blink" in d:
        d = d[d["blink"] == 0]
    return d


def regress(df: pd.DataFrame, outcome: str, terms: list[str], exclude_blinks=False,
            time_basis: str = "linear") -> Fit | None:
    d = _rows_for(df, outcome, exclude_blinks)
    if len(d) == 0:
        return None
    y_col = {"rt": "rt", "accuracy": "correct", "theta": "theta", "blink": "blink"}[outcome]
    if outcome in ("rt", "accuracy") and "congruent" not in terms:
        terms = terms + ["congruent"]
    X, names = _design_matrix(d, terms, time_basis)
    return ols_cluster(d[y_col].to_numpy(float), X, d["subject"].to_numpy(), names)


# --------------------------------------------------------------------------- ideal analyst

def _varies(df: pd.DataFrame, col: str, where=None) -> bool:
    d = df if where is None else df[where(df)]
    return len(d) > 0 and d[col].nunique() > 1


def ideal_claims(datasets: list[Dataset]) -> dict[str, dict]:
    """Best-possible claims from the data collected so far."""
    claims = {e: {"present": False, "confidence": UNIDENTIFIED, "identified": False} for e in EDGES}

    def put(edge, post, identified=True):
        claims[edge] = {"present": post > 0.5, "confidence": round(post if post > 0.5 else 1 - post, 4),
                        "identified": identified}

    clean = [d.data for d in datasets if not d.design.order_confounded()]
    allY = pd.concat([d.data for d in datasets], ignore_index=True)
    cleanY = pd.concat(clean, ignore_index=True) if clean else allY.iloc[0:0]

    # Performance edges: estimated from order-clean data only.
    if len(cleanY):
        s_at_l0 = _varies(cleanY, "S", lambda d: d["L"] == 0)
        s_at_l1 = _varies(cleanY, "S", lambda d: d["L"] == 1)
        terms = ["L", "S", "practice"] + (["SxL"] if s_at_l0 and s_at_l1 else [])
        fit = regress(cleanY, "rt", terms, time_basis="curve")
        if fit is not None:
            if "L" in fit.names:
                put("L->Y", bic_posterior(fit.z("L"), fit.n_subjects))
            if "S" in fit.names:
                post = bic_posterior(fit.z("S"), fit.n_subjects)
                if s_at_l0:
                    put("S->Y", post)
                    if s_at_l1 and "SxL" in fit.names:
                        put("SxL->Y", bic_posterior(fit.z("SxL"), fit.n_subjects))
                elif post < 0.5:  # S tested only at high load and it did nothing: rules out both
                    put("S->Y", post)
                    put("SxL->Y", post)
    # Practice: within-block position varies in every design, so all data can speak to it,
    # but only with the stimulation/load cells controlled.
    fitP = regress(cleanY if len(cleanY) else allY, "rt", ["L", "S", "practice"], time_basis="curve")
    if fitP is not None and "practice" in fitP.names:
        put("P->Y", bic_posterior(fitP.z("practice"), fitP.n_subjects))

    eeg = [d.data for d in datasets if d.design.eeg and "theta" in d.data]
    if eeg:
        E = pd.concat(eeg, ignore_index=True)
        if _varies(E, "L"):
            fb = regress(E, "blink", ["L"])
            if fb is not None and "L" in fb.names:
                put("L->B", bic_posterior(fb.z("L"), fb.n_subjects))
            ft = regress(E, "theta", ["L"], exclude_blinks=True)
            if ft is not None and "L" in ft.names:
                put("L->T", bic_posterior(ft.z("L"), ft.n_subjects))
    return claims


# --------------------------------------------------------------------------- agent tools

def describe(df: pd.DataFrame) -> list[dict]:
    keys = ["L", "S"]
    rows = []
    for (l, s), g in df.groupby(keys):
        ok = g[(g["correct"] == 1) & g["rt"].notna()]
        r = {"L": int(l), "S": int(s), "n_participants": int(g["subject"].nunique()),
             "mean_rt_correct_ms": round(float(ok["rt"].mean()), 1),
             "accuracy": round(float(g["correct"].mean()), 4)}
        if "theta" in g:
            r["mean_theta"] = round(float(g["theta"].mean()), 4)
        rows.append(r)
    return rows


def order_check(ds: Dataset) -> dict:
    df = ds.data
    out = {"order_confounded_by_design": ds.design.order_confounded()}
    for f in ("L", "S"):
        if df[f].nunique() > 1:
            out[f"corr_{f}_with_session_position"] = round(float(np.corrcoef(df[f], df["pos"])[0, 1]), 3)
    first = df[df["block"] == 0]
    ok = first[(first["correct"] == 1) & first["rt"].notna()]
    if len(ok) > 20:
        early = ok[ok["trial"] < ok["trial"].quantile(0.25)]["rt"].mean()
        late = ok[ok["trial"] > ok["trial"].quantile(0.75)]["rt"].mean()
        out["first_block_rt_change_early_to_late_ms"] = round(float(late - early), 1)
    return out


def artifact_check(ds: Dataset) -> dict:
    df = ds.data
    if "blink" not in df:
        return {"error": "no EEG/EOG recorded in this dataset"}
    out = {"ica_applied": ds.design.ica,
           "blink_rate_by_L": {int(k): round(float(v), 4) for k, v in df.groupby("L")["blink"].mean().items()}}
    if df["L"].nunique() > 1:
        def diff(d):
            m = d.groupby("L")["theta"].mean()
            return round(float(m.get(1, np.nan) - m.get(0, np.nan)), 4)
        out["theta_high_minus_low_load_all_trials"] = diff(df)
        out["theta_high_minus_low_load_blink_free_trials"] = diff(df[df["blink"] == 0])
    return out
