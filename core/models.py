"""
Score-event data models for Simultaneity Density Analyser.

All metrics derived from these structures are score-/information-based unless
explicitly labelled otherwise in later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Union

SourceType = Literal[
    "score_derived",
    "symbolic_metadata",
    "external_acoustic_metadata",
    "metadata_proxy",
    "calibrated_proxy",
    "empirical",
    "legacy_proxy",
]

ValidationStatus = Literal[
    "theoretical",
    "verified_only",
    "partially_calibrated",
    "externally_validated",
    "heuristic",
    "score_validated",
    "partially_score_validated",
    "legacy_proxy",
    "unvalidated",
]

ConfidenceLevel = Literal["high", "medium", "low"]


@dataclass
class Pitch:
    """Symbolic pitch with optional microtonal offset."""

    midi: float
    note_name: Optional[str] = None
    cents_offset: float = 0.0
    frequency_hz: Optional[float] = None
    spelling: Optional[str] = None
    pitch_class: Optional[int] = None

    def __post_init__(self) -> None:
        if self.pitch_class is None:
            self.pitch_class = int(round(self.midi)) % 12


@dataclass
class InstrumentEvent:
    """One sounding event in a vertical slice."""

    instrument_id: str
    instrument_name: str
    family: str
    sounding_pitch: Pitch
    player_count: int = 1
    dynamic: Optional[str] = None
    dynamic_weight: Optional[float] = None
    event_id: Optional[str] = None
    written_pitch: Optional[Pitch] = None
    articulation: Optional[str] = None
    technique: Optional[str] = None
    mute: Optional[str] = None
    harmonic_type: Optional[str] = None
    playing_position: Optional[str] = None
    register_label: Optional[str] = None
    onset: Optional[float] = None
    offset: Optional[float] = None
    duration: Optional[float] = None
    voice_id: Optional[str] = None
    staff_id: Optional[str] = None
    part_id: Optional[str] = None
    source_measure: Optional[str] = None
    source_beat: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerticalSlice:
    """Simultaneous collection of instrument events at one symbolic moment."""

    events: list[InstrumentEvent]
    slice_id: Optional[str] = None
    time: Optional[float] = None
    duration: Optional[float] = None
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisConfig:
    """Analysis options for strictly symbolic score analysis."""

    weight_factor: float = 0.5
    interval_model_config: dict[str, Any] = field(default_factory=dict)
    orchestration_config: dict[str, Any] = field(default_factory=dict)
    normalization_config: dict[str, Any] = field(default_factory=dict)
    temporal_config: dict[str, Any] = field(default_factory=dict)
    validation_config: dict[str, Any] = field(default_factory=dict)
    reporting_config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_input_dict(cls, data: dict[str, Any]) -> AnalysisConfig:
        from core.defaults import RESEARCH_ANALYSIS_DEFAULTS

        d = {**RESEARCH_ANALYSIS_DEFAULTS, **data}
        return cls(
            weight_factor=float(d.get("weight_factor", 0.5)),
        )


@dataclass
class MetricResult:
    """Structured metric output with epistemic metadata (populated in Phase 3)."""

    name: str
    value: Union[float, int, dict, list]
    unit: Optional[str] = None
    raw_value: Optional[Union[float, int, dict, list]] = None
    normalized_value: Optional[float] = None
    range: Optional[tuple[float, float]] = None
    source_type: SourceType = "score_derived"
    validation_status: ValidationStatus = "verified_only"
    confidence: ConfidenceLevel = "medium"
    interpretation: str = ""
    warnings: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


@dataclass
class VerticalSliceAnalysis:
    slice: VerticalSlice
    metrics: dict[str, MetricResult] = field(default_factory=dict)
    subindices: dict[str, MetricResult] = field(default_factory=dict)
    composite_density: Optional[MetricResult] = None
    warnings: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


@dataclass
class ScoreAnalysisResult:
    source_path: Optional[str] = None
    slices: list[VerticalSliceAnalysis] = field(default_factory=list)
    time_series: Optional[list[dict[str, Any]]] = None
    global_summary: dict[str, MetricResult] = field(default_factory=dict)
    config: Optional[AnalysisConfig] = None
    warnings: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
