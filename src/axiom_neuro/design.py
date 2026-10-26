"""Experiment designs an agent can request, their validation, and their cost."""

from __future__ import annotations

import itertools
from dataclasses import asdict, dataclass, field

FACTORS = ("L", "S")
SECONDS_PER_TRIAL = 2.5
SETUP_HOURS = 0.25
EEG_SETUP_HOURS = 0.25
EEG_TIME_FACTOR = 1.5


class DesignError(ValueError):
    pass


@dataclass
class Design:
    factors: list = field(default_factory=lambda: ["L"])
    fixed: dict = field(default_factory=dict)  # level for any factor not varied
    assignment: str = "within"  # within | between
    order: str = "counterbalanced"  # fixed | counterbalanced (within only)
    n_participants: int = 16
    trials_per_cell: int = 80
    eeg: bool = False
    ica: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Design":
        try:
            design = cls(
                factors=list(d.get("factors", ["L"])),
                fixed={k: int(v) for k, v in dict(d.get("fixed", {})).items()},
                assignment=str(d.get("assignment", "within")),
                order=str(d.get("order", "counterbalanced")),
                n_participants=int(d.get("n_participants", 16)),
                trials_per_cell=int(d.get("trials_per_cell", 80)),
                eeg=bool(d.get("eeg", False)),
                ica=bool(d.get("ica", False)),
            )
        except (TypeError, ValueError) as exc:
            raise DesignError(f"malformed design: {exc}") from exc
        design.validate()
        return design

    def validate(self) -> None:
        if not self.factors or any(f not in FACTORS for f in self.factors):
            raise DesignError(f"factors must be a non-empty subset of {list(FACTORS)}")
        if len(set(self.factors)) != len(self.factors):
            raise DesignError("factors repeated")
        for f in FACTORS:
            if f not in self.factors:
                self.fixed.setdefault(f, 0)
            if f in self.fixed and self.fixed[f] not in (0, 1):
                raise DesignError("fixed levels must be 0 or 1")
        self.fixed = {k: v for k, v in self.fixed.items() if k not in self.factors}
        if self.assignment not in ("within", "between"):
            raise DesignError("assignment must be 'within' or 'between'")
        if self.order not in ("fixed", "counterbalanced"):
            raise DesignError("order must be 'fixed' or 'counterbalanced'")
        if not 2 <= self.n_participants <= 96:
            raise DesignError("n_participants must be between 2 and 96")
        if not 20 <= self.trials_per_cell <= 200:
            raise DesignError("trials_per_cell must be between 20 and 200")
        if self.ica and not self.eeg:
            raise DesignError("ica requires eeg")

    def cells(self) -> list[dict]:
        """Canonical cell order: level 0 before level 1 (sham first, low load first)."""
        out = []
        for levels in itertools.product((0, 1), repeat=len(self.factors)):
            cell = dict(self.fixed)
            cell.update(dict(zip(self.factors, levels)))
            out.append(cell)
        return out

    def cost(self) -> float:
        """Participant-hours."""
        n_cells_each = len(self.cells()) if self.assignment == "within" else 1
        task_h = n_cells_each * self.trials_per_cell * SECONDS_PER_TRIAL / 3600.0
        if self.eeg:
            task_h *= EEG_TIME_FACTOR
        per = SETUP_HOURS + (EEG_SETUP_HOURS if self.eeg else 0.0) + task_h
        return round(self.n_participants * per, 3)

    def order_confounded(self) -> bool:
        """True when a varied factor's level is perfectly tied to session position."""
        return self.assignment == "within" and self.order == "fixed" and len(self.cells()) > 1

    def to_json(self) -> dict:
        return asdict(self)
