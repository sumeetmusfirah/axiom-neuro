"""Axiom-Ethics: algorithmic fairness on real COMPAS risk scores (ProPublica, Broward County, 2013-2014).

Rows are real defendants: COMPAS risk label, two-year rearrest, race, sex, age, prior count and charge
degree, filtered as in ProPublica's analysis and restricted to Black and white defendants. ProPublica's
terms do not allow redistributing the raw file, so it is downloaded at runtime and never committed;
only the frozen claims (and their truth values) are.

Every claim's truth is computed from the full data when tasks are frozen. The claims cover the facts
the fairness debate turned on: error-rate gaps, calibration within risk levels, base rates, the gap
after adjustment for record and age, and age and sex effects. Traps: a reversed gap, a base rate read
off a stratified sample (sources include "rearrested" and "not rearrested" strata), and "the gap is
explained by prior record".
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..params import REPO
from . import core

NAME, TRACK = "ethics", "compas"
URL = "https://raw.githubusercontent.com/propublica/compas-analysis/master/compas-scores-two-years.csv"
DATA = REPO / "data" / "compas_two_years.csv.gz"  # gitignored: ProPublica terms forbid redistribution
MANIFEST = REPO / "tasks" / "ethics_manifest.jsonl"
SHA = REPO / "tasks" / "ETHICS_MANIFEST.sha256"
BUDGET, OVERHEAD = 2000, 100
WEIGHT = None
CLAIMS_PER_TASK = 6

VARIABLES = {
    "black": ("black", "G", "1 = Black defendant, 0 = white defendant", "a 0/1 group attribute"),
    "female": ("female", "X1", "1 = female, 0 = male", "a 0/1 attribute"),
    "age": ("age", "X2", "age in years", "a numeric attribute"),
    "under_25": ("age_under_25", "X3", "1 = younger than 25", "a 0/1 attribute"),
    "priors": ("prior_count", "X4", "number of prior offences", "a numeric attribute"),
    "felony": ("felony_charge", "X5", "1 = current charge is a felony, 0 = misdemeanour", "a 0/1 attribute"),
    "high_risk": ("high_risk_label", "S", "1 = COMPAS labelled the person medium or high risk", "a 0/1 score flag"),
    "reoffended": ("rearrested_2y", "Y", "1 = rearrested within two years", "the 0/1 outcome"),
}

SOURCES = {
    "all": ("a random draw from all defendants", "a random draw from all rows", lambda f: np.ones(len(f), bool)),
    "black": ("Black defendants only", "rows with G = 1", lambda f: f["black"] == 1),
    "white": ("white defendants only", "rows with G = 0", lambda f: f["black"] == 0),
    "rearrested": ("people rearrested within two years", "rows with Y = 1", lambda f: f["reoffended"] == 1),
    "not_rearrested": ("people not rearrested within two years", "rows with Y = 0", lambda f: f["reoffended"] == 0),
    "women": ("women only", "rows with X1 = 1", lambda f: f["female"] == 1),
}

ADJ = ["black", "age", "priors", "female", "felony"]

POOL = {  # id: (named wording, estimand, op, threshold, trap)
    "fpr_gap": ("Among people who were NOT rearrested, Black defendants were labelled medium/high risk more "
                "often than white defendants, by more than 10 percentage points.",
                {"kind": "gap", "var": "high_risk", "by": "black", "a": 1, "b": 0, "where": {"reoffended": 0}},
                ">", 0.10, None),
    "fpr_reversed": ("Among people who were NOT rearrested, white defendants were labelled medium/high risk more "
                     "often than Black defendants, by more than 10 percentage points.",
                     {"kind": "gap", "var": "high_risk", "by": "black", "a": 0, "b": 1, "where": {"reoffended": 0}},
                     ">", 0.10, "reversed"),
    "fnr_gap": ("Among people who WERE rearrested, white defendants were labelled low risk more often than Black "
                "defendants, by more than 10 percentage points.",
                {"kind": "gap", "var": "high_risk", "by": "black", "a": 1, "b": 0, "where": {"reoffended": 1}},
                ">", 0.10, None),
    "base_rate_gap": ("Black defendants were rearrested within two years more often than white defendants, "
                      "by more than 5 percentage points.",
                      {"kind": "gap", "var": "reoffended", "by": "black", "a": 1, "b": 0}, ">", 0.05, None),
    "base_rate_all": ("More than 55% of all defendants were rearrested within two years.",
                      {"kind": "mean", "var": "reoffended"}, ">", 0.55, "selection"),
    "calibrated_high": ("Among people labelled medium/high risk, Black and white defendants were rearrested at "
                        "rates within 10 percentage points of each other.",
                        {"kind": "gap", "var": "reoffended", "by": "black", "a": 1, "b": 0, "where": {"high_risk": 1}},
                        "abs<", 0.10, None),
    "calibrated_low": ("Among people labelled low risk, Black and white defendants were rearrested at rates within "
                       "10 percentage points of each other.",
                       {"kind": "gap", "var": "reoffended", "by": "black", "a": 1, "b": 0, "where": {"high_risk": 0}},
                       "abs<", 0.10, None),
    "explained_by_record": ("Once age, prior count, sex and charge degree are held fixed, Black and white "
                            "defendants are labelled medium/high risk at rates within 3 percentage points.",
                            {"kind": "coef", "outcome": "high_risk", "predictors": ADJ, "target": "black"},
                            "abs<", 0.03, "confounded"),
    "gap_remains": ("Holding age, prior count, sex and charge degree fixed, Black defendants are still more than "
                    "5 percentage points more likely to be labelled medium/high risk.",
                    {"kind": "coef", "outcome": "high_risk", "predictors": ADJ, "target": "black"}, ">", 0.05,
                    "confounded"),
    "women_overpredicted": ("Among people labelled medium/high risk, women were rearrested less often than men, "
                            "by more than 5 percentage points.",
                            {"kind": "gap", "var": "reoffended", "by": "female", "a": 0, "b": 1, "where": {"high_risk": 1}},
                            ">", 0.05, None),
    "youth_label": ("Defendants under 25 were labelled medium/high risk more often than older defendants, by more "
                    "than 20 percentage points.",
                    {"kind": "gap", "var": "high_risk", "by": "under_25", "a": 1, "b": 0}, ">", 0.20, None),
    "priors_gap_large": ("Black defendants had more than 3 more prior offences on average than white defendants.",
                         {"kind": "gap", "var": "priors", "by": "black", "a": 1, "b": 0}, ">", 3.0, None),
    # stricter thresholds: the same facts, but the claim is false
    "fnr_gap_large": ("Among people who WERE rearrested, white defendants were labelled low risk more often than "
                      "Black defendants, by more than 30 percentage points.",
                      {"kind": "gap", "var": "high_risk", "by": "black", "a": 1, "b": 0, "where": {"reoffended": 1}},
                      ">", 0.30, None),
    "base_rate_gap_large": ("Black defendants were rearrested within two years more often than white defendants, "
                            "by more than 20 percentage points.",
                            {"kind": "gap", "var": "reoffended", "by": "black", "a": 1, "b": 0}, ">", 0.20, None),
    "youth_label_large": ("Defendants under 25 were labelled medium/high risk more often than older defendants, by "
                          "more than 30 percentage points.",
                          {"kind": "gap", "var": "high_risk", "by": "under_25", "a": 1, "b": 0}, ">", 0.30, None),
    "base_rate_all_40": ("More than 40% of all defendants were rearrested within two years.",
                         {"kind": "mean", "var": "reoffended"}, ">", 0.40, "selection"),
}
MARGIN = {"priors_gap_large": 0.5}  # others: 0.02 on proportions / coefficients


def intro(labels: str) -> str:
    if labels == "named":
        return ("You are auditing COMPAS, a criminal risk-assessment tool, using records of real defendants from "
                "Broward County, Florida (2013-2014). Each row has the tool's risk label, whether the person was "
                "rearrested within two years, and their demographics and record. Some sources are restricted to "
                "particular groups of people.")
    return ("You are auditing a scoring rule using real records. Each row has the rule's 0/1 flag S, a 0/1 "
            "outcome Y and some attributes, including a group attribute G. Some sources are restricted to "
            "particular kinds of rows.")


def value_labels(labels: str) -> dict:
    return {}


# ----------------------------------------------------------------------------- data

def fetch(path=DATA) -> dict:
    raw = pd.read_csv(URL)
    d = raw[(raw["days_b_screening_arrest"].between(-30, 30)) & (raw["is_recid"] != -1)
            & (raw["c_charge_degree"] != "O") & (raw["score_text"] != "N/A")
            & raw["race"].isin(["African-American", "Caucasian"])]
    out = pd.DataFrame({
        "black": (d["race"] == "African-American").astype(int),
        "female": (d["sex"] == "Female").astype(int),
        "age": d["age"].astype(int),
        "under_25": (d["age"] < 25).astype(int),
        "priors": d["priors_count"].astype(int),
        "felony": (d["c_charge_degree"] == "F").astype(int),
        "high_risk": (d["score_text"] != "Low").astype(int),
        "reoffended": d["two_year_recid"].astype(int),
    }).reset_index(drop=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False, compression="gzip")
    return {"defendants": len(out)}


_CACHE: dict = {}


def frame(task: core.ClaimTask | None = None) -> pd.DataFrame:
    if "f" not in _CACHE:
        if not DATA.exists():
            fetch()
        _CACHE["f"] = pd.read_csv(DATA)
    return _CACHE["f"]


# ----------------------------------------------------------------------------- tasks

def full_pool() -> dict:
    f = frame()
    out = {}
    for k, (named, est, op, thr, trap) in POOL.items():
        val = core.estimate(f, est, None)[0]
        if abs(abs(val) - thr) < MARGIN.get(k, 0.02) if op == "abs<" else abs(val - thr) < MARGIN.get(k, 0.02):
            raise RuntimeError(f"claim {k} is too close to its threshold on the full data ({val:.3f} vs {thr})")
        out[k] = {"named": named, "est": est, "op": op, "thr": thr, "trap": trap,
                  "truth": core.holds(val, op, thr), "value_full": round(float(val), 4)}
    return out


def build_tasks(seed: int, n: int) -> list[core.ClaimTask]:
    pool = full_pool()
    traps = [k for k, v in pool.items() if v["trap"]]
    plain = [k for k, v in pool.items() if not v["trap"]]
    rng = np.random.default_rng(seed)
    tasks = []
    for i in range(n):
        pick = list(rng.choice(traps, 2, replace=False)) + list(rng.choice(plain, CLAIMS_PER_TASK - 2, replace=False))
        rng.shuffle(pick)
        tasks.append(core.ClaimTask(f"ethics-{i:02d}", int(rng.integers(0, 2**31 - 1)),
                                    {f"C{j + 1}": {**pool[k], "id": k} for j, k in enumerate(pick)}, BUDGET))
    return tasks
