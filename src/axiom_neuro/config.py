from __future__ import annotations

import tomllib
from pathlib import Path

from .params import REPO

CONFIG = REPO / "configs" / "experiment.toml"


def load_config(path: Path = CONFIG) -> dict:
    return tomllib.loads(path.read_text())
