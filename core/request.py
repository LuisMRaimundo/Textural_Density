"""
Strict typed analysis request boundary.

Unknown analytical keys are rejected (extra=forbid semantics).
Removed legacy keys raise InputError via input_validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from core.input_validation import validate_no_removed_options
from core.quantity_scaling import validate_quantity
from error_handler import InputError

ALLOWED_REQUEST_KEYS = frozenset(
    {
        "notes",
        "dynamics",
        "instruments",
        "num_instruments",
        "weight_factor",
        "onsets",
        "offsets",
        "durations",
        "part_ids",
    }
)


@dataclass(frozen=True)
class AnalysisRequest:
    """Canonical typed input for vertical-slice analysis."""

    notes: tuple[str, ...]
    dynamics: tuple[str, ...]
    instruments: tuple[str, ...]
    num_instruments: tuple[int, ...]
    weight_factor: float = 0.5
    onsets: tuple[float, ...] | None = None
    offsets: tuple[float, ...] | None = None
    durations: tuple[float, ...] | None = None
    part_ids: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        if not self.notes:
            raise InputError("Notes are required.")
        n = len(self.notes)
        if not (len(self.dynamics) == len(self.instruments) == len(self.num_instruments) == n):
            raise InputError("Notes, dynamics, instruments and quantities must have the same length.")
        for optional in (self.onsets, self.offsets, self.durations, self.part_ids):
            if optional is not None and len(optional) != n:
                raise InputError("Optional timing/part lists must match notes length when provided.")
        for qty in self.num_instruments:
            validate_quantity(qty)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> AnalysisRequest:
        validate_no_removed_options(dict(data))
        unknown = set(data.keys()) - ALLOWED_REQUEST_KEYS
        if unknown:
            raise InputError(
                f"Unknown analytical keys rejected: {', '.join(sorted(unknown))}. "
                "Use AnalysisRequest fields only."
            )
        return cls(
            notes=tuple(str(x) for x in data["notes"]),
            dynamics=tuple(str(x) for x in data["dynamics"]),
            instruments=tuple(str(x) for x in data["instruments"]),
            num_instruments=tuple(int(validate_quantity(x)) for x in data["num_instruments"]),
            weight_factor=float(data.get("weight_factor", 0.5)),
            onsets=_optional_float_tuple(data, "onsets"),
            offsets=_optional_float_tuple(data, "offsets"),
            durations=_optional_float_tuple(data, "durations"),
            part_ids=_optional_str_tuple(data, "part_ids"),
        )

    def to_pipeline_dict(self) -> dict[str, Any]:
        """Dict for internal pipeline/converters (strict field set only)."""
        out: dict[str, Any] = {
            "notes": list(self.notes),
            "dynamics": list(self.dynamics),
            "instruments": list(self.instruments),
            "num_instruments": list(self.num_instruments),
            "weight_factor": self.weight_factor,
        }
        if self.onsets is not None:
            out["onsets"] = list(self.onsets)
        if self.offsets is not None:
            out["offsets"] = list(self.offsets)
        if self.durations is not None:
            out["durations"] = list(self.durations)
        if self.part_ids is not None:
            out["part_ids"] = list(self.part_ids)
        return out


def _optional_float_tuple(data: Mapping[str, Any], key: str) -> tuple[float, ...] | None:
    if key not in data or data[key] is None:
        return None
    return tuple(float(x) for x in data[key])


def _optional_str_tuple(data: Mapping[str, Any], key: str) -> tuple[str, ...] | None:
    if key not in data or data[key] is None:
        return None
    return tuple(str(x) for x in data[key])
