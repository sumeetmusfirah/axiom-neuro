"""Simulator nuisance parameters: defaults until ERP CORE has been fitted, then fitted values."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FITTED_PATH = REPO / "data" / "fitted_params.json"
TRIALS_PATH = REPO / "data" / "erpcore_trials.csv.gz"


@dataclass
class SimParams:
    # Ex-Gaussian RT on correct trials (ms): population mean / between-subject SD of mu
    rt_mu: float = 420.0
    rt_mu_sd: float = 50.0
    rt_sigma: float = 40.0
    rt_tau: float = 80.0
    # Flanker congruency effect (incongruent - congruent)
    cong_rt: float = 50.0
    cong_rt_sd: float = 15.0
    # Accuracy on the logit scale
    acc_logit: float = 3.0
    acc_logit_sd: float = 0.6
    cong_acc_logit: float = -1.0
    # Between-subject spread of every injected effect, as a fraction of its size
    slope_sd_frac: float = 0.3
    # EEG: frontal theta (log power) and blinks
    theta_sd_between: float = 0.3
    theta_sd_within: float = 0.5
    theta_sd_within_sd: float = 0.08  # participants differ in EEG noise level
    blink_rate: float = 0.12
    blink_logit_sd: float = 0.8
    blink_theta_gain: float = 0.8
    ica_removal: float = 0.9
    # Trials with no usable response
    missing_rate: float = 0.02
    # Bookkeeping
    source: str = "default-unfitted"
    validation_passed: bool = False

    def to_json(self) -> dict:
        return asdict(self)


def load_params(path: Path = FITTED_PATH) -> SimParams:
    if not path.exists():
        return SimParams()
    d = json.loads(path.read_text())
    known = {k: v for k, v in d.get("params", d).items() if k in SimParams.__dataclass_fields__}
    p = SimParams(**known)
    p.source = d.get("source", "erpcore")
    p.validation_passed = bool(d.get("validation", {}).get("passed", False))
    return p
