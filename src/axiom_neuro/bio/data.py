"""Real single-cell signalling data: Sachs et al. (2005), via Zenodo record 7681811 (CC BY 4.0).

Eleven phosphoproteins/phospholipids measured by flow cytometry in human CD4+ T cells under
nine conditions. Reagent targets follow Sachs et al. (2005, Science 308:523), Table 1, and
standard pharmacology (U0126 is a MEK inhibitor, LY294002 a PI3K inhibitor, PMA a PKC
activator, G06976 a PKC inhibitor, beta2cAMP a PKA activator).

The Zenodo bundle also ships five ICAM-2 + inhibitor files that its own description labels
"simulated dataset"; they are excluded so that every observation is a real cell.
"""

from __future__ import annotations

import io
import json
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from ..params import REPO

ZENODO = "https://zenodo.org/records/7681811/files/sachs.zip?download=1"
CELLS_PATH = REPO / "data" / "sachs_cells.csv.gz"
GRAPH_PATH = REPO / "data" / "sachs_ground_truth.json"

PROTEINS = ("Raf", "Mek", "Plcg", "PIP2", "PIP3", "Erk", "Akt", "PKA", "PKC", "P38", "Jnk")

# id -> (file, description, target, effect, context)
CONDITIONS = {
    "baseline":        ("cd3cd28.csv",          "CD3/CD28 stimulation", None, None, "cd3cd28"),
    "icam2":           ("cd3cd28_icam2.csv",    "CD3/CD28 + ICAM-2 co-stimulation", None, None, "cd3cd28"),
    "akt_inhibitor":   ("cd3cd28_aktinhib.csv", "CD3/CD28 + AKT inhibitor", "Akt", "inhibits activity", "cd3cd28"),
    "g06976":          ("cd3cd28_g0076.csv",    "CD3/CD28 + G06976", "PKC", "inhibits activity", "cd3cd28"),
    "psitectorigenin": ("cd3cd28_psitect.csv",  "CD3/CD28 + Psitectorigenin", "PIP2", "inhibits", "cd3cd28"),
    "u0126":           ("cd3cd28_u0126.csv",    "CD3/CD28 + U0126", "Mek", "inhibits activity", "cd3cd28"),
    "ly294002":        ("cd3cd28_ly.csv",       "CD3/CD28 + LY294002", "PIP3", "inhibits production (PI3K)", "cd3cd28"),
    "pma":             ("pma.csv",              "PMA alone (no CD3/CD28)", "PKC", "activates", "none"),
    "b2camp":          ("b2camp.csv",           "beta2cAMP alone (no CD3/CD28)", "PKA", "activates", "none"),
}


def fetch(cells_path: Path = CELLS_PATH, graph_path: Path = GRAPH_PATH) -> dict:
    with urllib.request.urlopen(ZENODO, timeout=120) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    names = {Path(n).name: n for n in z.namelist()}
    frames = []
    for cid, (fname, *_rest) in CONDITIONS.items():
        df = pd.read_csv(z.open(names[fname]))
        df.columns = [c.strip().strip('"') for c in df.columns]
        if tuple(df.columns) != PROTEINS:
            raise RuntimeError(f"{fname}: unexpected columns {list(df.columns)}")
        df.insert(0, "condition", cid)
        frames.append(df)
    cells = pd.concat(frames, ignore_index=True)
    gt = pd.read_csv(z.open(names["GroundTruth.csv"]))
    edges = sorted(f"{a.strip()}->{b.strip()}" for a, b in zip(gt["from"], gt["to"]))
    cells_path.parent.mkdir(parents=True, exist_ok=True)
    cells.to_csv(cells_path, index=False, compression="gzip")
    graph_path.write_text(json.dumps({"source": "Zenodo 7681811 GroundTruth.csv (Sachs et al. 2005 consensus)",
                                      "edges": edges}, indent=2))
    return {"cells": len(cells), "per_condition": cells["condition"].value_counts().to_dict(), "edges": len(edges)}


_CACHE: dict = {}


def load_cells(path: Path = CELLS_PATH) -> pd.DataFrame:
    """Log-transformed intensities (flow cytometry is roughly log-normal)."""
    if "cells" not in _CACHE:
        raw = pd.read_csv(path)
        logged = raw.copy()
        logged[list(PROTEINS)] = np.log(raw[list(PROTEINS)].clip(lower=0.1))
        _CACHE["cells"] = logged
    return _CACHE["cells"]


def load_graph(path: Path = GRAPH_PATH) -> frozenset:
    return frozenset(json.loads(path.read_text())["edges"])
