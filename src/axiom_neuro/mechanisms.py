"""The hypothesis family: which causal edges exist, and the task types built from them.

Variables
    L  working-memory load (0 = low, 1 = high)
    S  stimulation (0 = sham, 1 = active tES)
    P  practice / time-on-task (session position, 0..1)
    Y  flanker performance (RT on correct trials, accuracy)
    T  frontal theta power (EEG)
    B  blink rate (EOG)

An agent must claim, for every edge, whether it is present and how confident it is.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

EDGES: tuple[str, ...] = ("L->Y", "S->Y", "SxL->Y", "P->Y", "L->T", "L->B")

EDGE_TEXT = {
    "named": {
        "L->Y": "working-memory load changes flanker performance",
        "S->Y": "tES stimulation changes performance at low AND high load (main effect)",
        "SxL->Y": "the stimulation effect on performance depends on load (interaction)",
        "P->Y": "practice / time-on-task changes performance",
        "L->T": "load changes frontal theta power (a genuine neural effect)",
        "L->B": "load changes blink rate",
    },
    "abstract": {
        "L->Y": "Factor A changes Measure 1",
        "S->Y": "Factor B changes Measure 1 at both levels of Factor A (main effect)",
        "SxL->Y": "the effect of Factor B on Measure 1 depends on Factor A (interaction)",
        "P->Y": "the time index changes Measure 1",
        "L->T": "Factor A changes Measure 2 (genuine effect, not an artifact)",
        "L->B": "Factor A changes Measure 3 (event rate)",
    },
}

VAR_TEXT = {
    "named": {
        "L": "working-memory load (0 = low, 1 = high)",
        "S": "tES stimulation over DLPFC (0 = sham, 1 = active)",
        "P": "practice / time-on-task (position in the session)",
        "Y": "flanker performance: RT on correct trials (ms) and accuracy",
        "T": "frontal theta power at FCz (log units), only if EEG is recorded",
        "B": "blinks, from the EOG channel recorded with EEG",
    },
    "abstract": {
        "L": "Factor A (levels 0 and 1)",
        "S": "Factor B (levels 0 and 1)",
        "P": "time index (position in the session)",
        "Y": "Measure 1: response time on correct trials (ms) and accuracy",
        "T": "Measure 2 (continuous signal), only if the sensor is recorded",
        "B": "Measure 3: discrete events detected by the sensor",
    },
}


@dataclass(frozen=True)
class StarterDesign:
    """The pilot data every task opens with. Some are deliberately confounded."""

    factors: tuple[str, ...]
    fixed: dict
    assignment: str
    order: str
    n_participants: int
    trials_per_cell: int
    eeg: bool
    ica: bool
    note: str


@dataclass(frozen=True)
class TaskType:
    name: str
    edges: frozenset
    split: str  # "train" or "heldout"
    starter: StarterDesign
    trap: str  # what a careless scientist concludes from the starter data
    confound_edge: str | None = None  # edge the trap tempts the agent to claim falsely
    tags: tuple = field(default_factory=tuple)


_S_FIXED_ORDER = StarterDesign(
    factors=("S",), fixed={"L": 1}, assignment="within", order="fixed",
    n_participants=12, trials_per_cell=80, eeg=False, ica=False,
    note="pilot: sham block always first, then active block; high load only",
)
_S_LOW_LOAD = StarterDesign(
    factors=("S",), fixed={"L": 0}, assignment="within", order="counterbalanced",
    n_participants=12, trials_per_cell=80, eeg=False, ica=False,
    note="pilot: sham vs active, counterbalanced; low load only",
)
_L_EEG = StarterDesign(
    factors=("L",), fixed={"S": 0}, assignment="within", order="counterbalanced",
    n_participants=12, trials_per_cell=80, eeg=True, ica=False,
    note="pilot: low vs high load with EEG, no artifact correction; sham only",
)

TASK_TYPES: dict[str, TaskType] = {
    t.name: t
    for t in [
        TaskType("load_only", frozenset({"L->Y", "P->Y"}), "train", _S_LOW_LOAD,
                 trap="stimulation does nothing anywhere (true here)", tags=("null",)),
        TaskType("interaction", frozenset({"L->Y", "SxL->Y", "P->Y"}), "train", _S_LOW_LOAD,
                 trap="stimulation does nothing (it only works under high load)",
                 confound_edge=None, tags=("hidden-interaction",)),
        TaskType("practice_confound", frozenset({"L->Y", "P->Y"}), "train", _S_FIXED_ORDER,
                 trap="stimulation helps (it is practice: active always came second)",
                 confound_edge="S->Y", tags=("confound",)),
        TaskType("blink_artifact", frozenset({"L->Y", "L->B", "P->Y"}), "train", _L_EEG,
                 trap="load raises frontal theta (it is blinks contaminating the EEG)",
                 confound_edge="L->T", tags=("confound", "artifact")),
        # Held-out: never used to tune prompts or tools. Same starters, opposite truths.
        TaskType("stim_main", frozenset({"L->Y", "S->Y", "P->Y"}), "heldout", _S_FIXED_ORDER,
                 trap="stimulation helps (true here, but the pilot cannot show it)",
                 tags=("mirror:practice_confound",)),
        TaskType("neural_theta", frozenset({"L->Y", "L->T", "P->Y"}), "heldout", _L_EEG,
                 trap="theta change is an artifact (it is genuine here)",
                 tags=("mirror:blink_artifact",)),
    ]
}


@dataclass
class Mechanism:
    """A concrete task instance: which edges exist, and how big each effect is."""

    task_type: str
    edges: frozenset
    effects: dict  # effect sizes in natural units; 0.0 for absent edges

    def truth(self) -> dict[str, bool]:
        return {e: (e in self.edges) for e in EDGES}

    def to_json(self) -> dict:
        return {"task_type": self.task_type, "edges": sorted(self.edges), "effects": self.effects}

    @classmethod
    def from_json(cls, d: dict) -> "Mechanism":
        return cls(d["task_type"], frozenset(d["edges"]), dict(d["effects"]))


def sample_mechanism(task_type: str, rng: np.random.Generator) -> Mechanism:
    """Draw effect sizes for a task instance. Directions are fixed; magnitudes vary.

    RT effects are in ms (negative = faster). Sizes are chosen to be detectable
    with a reasonable design inside the budget, but not with the starter pilot alone.
    """
    tt = TASK_TYPES[task_type]
    e = set(tt.edges)
    # Practice is a coin flip everywhere except the task whose trap depends on it,
    # so "P->Y present" is never a free answer.
    if task_type != "practice_confound":
        e.discard("P->Y")
        if rng.random() < 0.5:
            e.add("P->Y")
    effects = {
        "L->Y": float(rng.uniform(25, 60)) if "L->Y" in e else 0.0,          # load slows RT
        "S->Y": -float(rng.uniform(15, 35)) if "S->Y" in e else 0.0,         # stim speeds RT
        "SxL->Y": -float(rng.uniform(25, 50)) if "SxL->Y" in e else 0.0,     # only at high load
        "P->Y": -float(rng.uniform(30, 60)) if "P->Y" in e else 0.0,         # practice speeds RT
        "L->T": float(rng.uniform(0.15, 0.35)) if "L->T" in e else 0.0,      # log-theta units
        "L->B": float(rng.uniform(1.8, 3.0)) if "L->B" in e else 1.0,        # blink-rate multiplier
    }
    return Mechanism(task_type, frozenset(e), effects)


def practice_curve(pos: np.ndarray) -> np.ndarray:
    """Learning curve over session position 0..1: most of the gain comes early.

    Nonlinear on purpose, so a linear time covariate cannot fully remove a
    practice confound; only a counterbalanced or between-subjects design can.
    """
    k = 0.25
    return (1.0 - np.exp(-pos / k)) / (1.0 - np.exp(-1.0 / k))
