"""Provenance records for instrument acoustic metadata tables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

InstrumentSourceType = Literal[
    "external_acoustic_metadata",
    "literature_derived",
    "coarse_default",
]

UncertaintyLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class InstrumentSource:
    source_type: InstrumentSourceType
    citation: str
    source_url_or_identifier: str | None
    extraction_method: str
    dynamic_levels: tuple[str, ...]
    pitch_range: tuple[int, int]
    uncertainty: UncertaintyLevel
    version: str
