"""The frozen task set. Deterministic from the config seed; its hash is committed."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .mechanisms import TASK_TYPES, Mechanism, sample_mechanism
from .params import REPO

MANIFEST = REPO / "tasks" / "manifest.jsonl"
MANIFEST_SHA = REPO / "tasks" / "MANIFEST.sha256"


@dataclass
class Task:
    task_id: str
    task_type: str
    split: str
    seed: int
    budget: float
    mechanism: Mechanism

    def to_json(self) -> dict:
        return {"task_id": self.task_id, "task_type": self.task_type, "split": self.split,
                "seed": self.seed, "budget": self.budget, "mechanism": self.mechanism.to_json()}

    @classmethod
    def from_json(cls, d: dict) -> "Task":
        return cls(d["task_id"], d["task_type"], d["split"], d["seed"], d["budget"],
                   Mechanism.from_json(d["mechanism"]))


def build_tasks(seed: int, instances_per_type: int, budget: float) -> list[Task]:
    ss = np.random.SeedSequence(seed)
    tasks = []
    for t_name in sorted(TASK_TYPES):
        children = ss.spawn(1)[0].spawn(instances_per_type)
        for i, child in enumerate(children):
            rng = np.random.default_rng(child)
            mech = sample_mechanism(t_name, rng)
            task_seed = int(rng.integers(0, 2**31 - 1))
            tasks.append(Task(f"{t_name}-{i:02d}", t_name, TASK_TYPES[t_name].split, task_seed, budget, mech))
    return tasks


def _serialize(tasks: list[Task]) -> str:
    return "".join(json.dumps(t.to_json(), sort_keys=True) + "\n" for t in tasks)


def manifest_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def freeze(tasks: list[Task], path: Path = MANIFEST, sha_path: Path = MANIFEST_SHA) -> str:
    text = _serialize(tasks)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    h = manifest_hash(text)
    sha_path.write_text(h + "\n")
    return h


def load_tasks(path: Path = MANIFEST) -> list[Task]:
    return [Task.from_json(json.loads(line)) for line in path.read_text().splitlines() if line.strip()]


def is_frozen(path: Path = MANIFEST, sha_path: Path = MANIFEST_SHA) -> bool:
    if not (path.exists() and sha_path.exists()):
        return False
    return manifest_hash(path.read_text()) == sha_path.read_text().strip()
