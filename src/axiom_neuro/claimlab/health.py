"""Axiom-Health: semi-synthetic epidemiology on real NHANES 2017-2018 adults (CDC, public domain).

Real rows: age, sex, body mass index, family income-to-poverty ratio, race/ethnicity group, measured
systolic blood pressure and the survey's examination weights. NHANES oversamples some groups, so an
unweighted average of the file is not a population estimate.

Each task plants a hypothetical exposure E on those real people, with known strength of confounding
(by age, BMI and the oversampled group) and a known effect on blood pressure, which may differ by sex
or be zero. Real blood pressure is the outcome's baseline, so the noise, skew and covariate structure
are the real population's. Claims ask about E's effect, its unadjusted association, its population
prevalence, effect modification by sex, and one real fact (BMI and blood pressure).
"""

from __future__ import annotations

import io
import urllib.request

import numpy as np
import pandas as pd

from ..params import REPO
from . import core

NAME, TRACK = "health", "nhanes"
DATA = REPO / "data" / "nhanes_2017_adults.csv.gz"
MANIFEST = REPO / "tasks" / "health_manifest.jsonl"
SHA = REPO / "tasks" / "HEALTH_MANIFEST.sha256"
BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/"
BUDGET, OVERHEAD = 2400, 100
WEIGHT = "weight"

VARIABLES = {  # internal: (named, abstract, description named, description abstract)
    "age": ("age", "X1", "age in years", "a numeric attribute"),
    "female": ("female", "X2", "1 = female, 0 = male", "a 0/1 attribute"),
    "bmi": ("bmi", "X3", "body mass index (kg/m²)", "a numeric attribute"),
    "income_ratio": ("income_ratio", "X4", "family income divided by the poverty line", "a numeric attribute"),
    "group": ("black_hispanic_asian", "X5", "1 = non-Hispanic Black, Hispanic or non-Hispanic Asian", "a 0/1 attribute"),
    "age60": ("age_60_plus", "X6", "1 = age 60 or older", "a 0/1 attribute"),
    "exposure": ("exposure_E", "X7", "1 = exposed to E, a hypothetical exposure", "a 0/1 attribute"),
    "sbp": ("systolic_bp", "Y", "systolic blood pressure (mmHg)", "the numeric outcome"),
}

SOURCES = {  # id: (named, abstract, row mask)
    "all": ("a random draw from all adults in the survey file", "a random draw from all rows",
            lambda f: np.ones(len(f), bool)),
    "women": ("women only", "rows with X2 = 1", lambda f: f["female"] == 1),
    "men": ("men only", "rows with X2 = 0", lambda f: f["female"] == 0),
    "age_60_plus": ("adults aged 60 or older", "rows with X6 = 1", lambda f: f["age60"] == 1),
    "under_60": ("adults under 60", "rows with X6 = 0", lambda f: f["age60"] == 0),
    "black_hispanic_asian": ("non-Hispanic Black, Hispanic or Asian adults", "rows with X5 = 1",
                             lambda f: f["group"] == 1),
}

ADJUST = ["exposure", "age", "bmi", "female", "group"]
# (beta, gamma): no effect (twice as likely), a uniform +5 mmHg, or +2 in men and +8 in women
EFFECTS = [(0.0, 0.0), (0.0, 0.0), (5.0, 0.0), (2.0, 6.0)]


def intro(labels: str) -> str:
    if labels == "named":
        return ("You are an epidemiologist with access to a US national health survey of adults (NHANES). "
                "The survey oversamples some groups, so every row carries a survey weight; weighted analyses "
                "describe the adult population, unweighted ones describe the survey file. Exposure E is "
                "hypothetical; everything else about the people is real.")
    return ("You study a population through a survey file. The file over-represents some kinds of rows, so "
            "every row carries a weight; weighted analyses describe the population, unweighted ones describe "
            "the file.")


def value_labels(labels: str) -> dict:
    return {}


# ----------------------------------------------------------------------------- data

def fetch(path=DATA) -> dict:
    def xpt(name):
        with urllib.request.urlopen(BASE + name, timeout=120) as r:
            return pd.read_sas(io.BytesIO(r.read()), format="xport")
    demo = xpt("DEMO_J.xpt")[["SEQN", "RIDAGEYR", "RIAGENDR", "RIDRETH3", "INDFMPIR", "WTMEC2YR"]]
    bmx = xpt("BMX_J.xpt")[["SEQN", "BMXBMI"]]
    bpx = xpt("BPX_J.xpt")[["SEQN", "BPXSY1"]]
    d = demo.merge(bmx, on="SEQN").merge(bpx, on="SEQN").dropna()
    d = d[(d["RIDAGEYR"] >= 20) & (d["WTMEC2YR"] > 0)]
    out = pd.DataFrame({
        "age": d["RIDAGEYR"].astype(int),
        "female": (d["RIAGENDR"] == 2).astype(int),
        "bmi": d["BMXBMI"].round(1),
        "income_ratio": d["INDFMPIR"].round(2),
        "group": d["RIDRETH3"].isin([1, 2, 4, 6]).astype(int),  # Mexican American, other Hispanic, NH Black, NH Asian
        "sbp_real": d["BPXSY1"].astype(float),
        "weight": d["WTMEC2YR"].round(1),
    }).reset_index(drop=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False, compression="gzip")
    return {"adults": len(out)}


_CACHE: dict = {}


def base_frame() -> pd.DataFrame:
    if "base" not in _CACHE:
        f = pd.read_csv(DATA)
        f["age60"] = (f["age"] >= 60).astype(int)
        _CACHE["base"] = f
    return _CACHE["base"]


def plant(base: pd.DataFrame, p: dict, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng([seed, 7])
    z = lambda c: (base[c] - base[c].mean()) / base[c].std()
    logit = -0.9 + p["c_age"] * z("age") + p["c_bmi"] * z("bmi") + p["c_group"] * (base["group"] - 0.5)
    f = base.copy()
    f["exposure"] = (rng.random(len(f)) < 1 / (1 + np.exp(-logit))).astype(int)
    f["sbp"] = (f["sbp_real"] + p["beta"] * f["exposure"] + p["gamma"] * f["exposure"] * f["female"]
                + rng.normal(0, 3, len(f))).round(1)
    return f


def frame(task: core.ClaimTask) -> pd.DataFrame:
    key = ("task", task.task_id, task.seed)
    if key not in _CACHE:
        _CACHE[key] = plant(base_frame(), task.plant, task.seed)
    return _CACHE[key]


# ----------------------------------------------------------------------------- tasks

def _claims(f: pd.DataFrame, p: dict, rng) -> dict | None:
    """The six claims of one task, or None if any is too close to its threshold to have a clear answer."""
    w = WEIGHT
    share_f = core.mean_of(f, "female", None, w, True)[0]
    effect = p["beta"] + p["gamma"] * share_f
    pw = core.mean_of(f, "exposure", None, w, True)[0]
    pu = core.mean_of(f, "exposure", None, w, False)[0]
    if p["c_group"] != 0:  # threshold between the file's and the population's prevalence
        thr_prev, trap_prev = round((pw + pu) / 2, 3), "weights"
    else:
        thr_prev, trap_prev = round(pw + rng.choice([-0.08, 0.08]), 3), None
    thr_bmi = float(rng.choice([0.15, 0.45]))
    out = {
        "causal": {
            "named": "Exposure E raises systolic blood pressure by more than 2 mmHg on average, holding age, "
                     "BMI, sex and group fixed (in the adult population).",
            "est": {"kind": "coef", "outcome": "sbp", "predictors": ADJUST, "target": "exposure", "weighted": True},
            "op": ">", "thr": 2.0, "truth": effect > 2.0,
            "trap": "confounded" if effect <= 2.0 and (p["c_age"] or p["c_bmi"]) else None},
        "naive": {
            "named": "Without any adjustment, exposed adults have systolic blood pressure more than 2 mmHg "
                     "higher than unexposed adults (in the adult population).",
            "est": {"kind": "gap", "var": "sbp", "by": "exposure", "a": 1, "b": 0, "weighted": True},
            "op": ">", "thr": 2.0, "trap": None},
        "prevalence": {
            "named": f"More than {thr_prev:.1%} of US adults are exposed to E.",
            "est": {"kind": "mean", "var": "exposure", "weighted": True},
            "op": ">", "thr": thr_prev, "trap": trap_prev},
        "modification": {
            "named": "E's effect on systolic blood pressure is at least 2 mmHg larger in women than in men "
                     "(adjusting for age, BMI and group; in the adult population).",
            "est": {"kind": "coefdiff", "outcome": "sbp", "predictors": ["exposure", "age", "bmi", "group"],
                    "target": "exposure", "where_a": {"female": 1}, "where_b": {"female": 0}, "weighted": True},
            "op": ">", "thr": 2.0, "truth": p["gamma"] > 2.0, "trap": None},
        "age_link": {
            "named": "Adults aged 60 or older are more than 5 percentage points more likely to be exposed to E "
                     "than adults under 60 (in the adult population).",
            "est": {"kind": "gap", "var": "exposure", "by": "age60", "a": 1, "b": 0, "weighted": True},
            "op": ">", "thr": 0.05, "trap": None},
        "bmi_real": {
            "named": "Holding age fixed, each extra BMI unit goes with more than 0.2 mmHg higher systolic blood "
                     "pressure (in the adult population).".replace("0.2", f"{thr_bmi:g}"),
            "est": {"kind": "coef", "outcome": "sbp", "predictors": ["bmi", "age"], "target": "bmi", "weighted": True},
            "op": ">", "thr": thr_bmi, "trap": None},
    }
    margins = {"causal": 0.8, "naive": 0.8, "prevalence": 0.015, "modification": 0.8, "age_link": 0.025, "bmi_real": 0.08}
    for k, c in out.items():
        val = core.estimate(f, c["est"], w)[0]
        full = core.holds(val, c["op"], c["thr"])
        if "truth" in c and bool(c["truth"]) != full:
            return None  # planted truth and full-population estimate disagree: draw again
        if abs(val - c["thr"]) < margins[k]:
            return None
        c["truth"], c["value_full"] = bool(full), round(float(val), 4)
    return out


def build_tasks(seed: int, n: int) -> list[core.ClaimTask]:
    rng = np.random.default_rng(seed)
    base = base_frame()
    tasks = []
    while len(tasks) < n:
        beta, gamma = EFFECTS[int(rng.integers(len(EFFECTS)))]
        p = {"c_age": float(rng.choice([0.0, 1.0])), "c_bmi": float(rng.choice([0.0, 0.6])),
             "c_group": float(rng.choice([0.0, 1.5, -1.5])), "beta": beta, "gamma": gamma}
        tseed = int(rng.integers(0, 2**31 - 1))
        claims = _claims(plant(base, p, tseed), p, rng)
        if claims is None:
            continue
        order = list(claims)
        rng.shuffle(order)
        tasks.append(core.ClaimTask(f"health-{len(tasks):02d}", tseed,
                                    {f"C{i + 1}": {**claims[k], "id": k} for i, k in enumerate(order)},
                                    BUDGET, p))
    return tasks
