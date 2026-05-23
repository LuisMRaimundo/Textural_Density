"""
Score-level temporal analysis (Phase 6).

``analyze_score`` groups timed events into vertical slices and reuses
``calculate_metrics`` for each slice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Union

from core.converters import (
    analysis_config_from_input,
    vertical_slice_to_legacy_lists,
)
from core.models import (
    AnalysisConfig,
    InstrumentEvent,
    MetricResult,
    ScoreAnalysisResult,
    VerticalSlice,
    VerticalSliceAnalysis,
)
from core.temporal import (
    TemporalMode,
    events_have_timing,
    group_events_into_slices,
    summarize_time_series,
)
from core.pipeline import calculate_metrics
from error_handler import InputError


def _default_analysis_options() -> dict[str, Any]:
    from core.defaults import RESEARCH_ANALYSIS_DEFAULTS

    return dict(RESEARCH_ANALYSIS_DEFAULTS)


def vertical_slice_to_input_data(
    vertical_slice: VerticalSlice,
    base_options: dict[str, Any],
) -> dict[str, Any]:
    """Build legacy calculate_metrics input from a vertical slice."""
    notas, dinamicas, instrumentos, numeros = vertical_slice_to_legacy_lists(vertical_slice)
    data = dict(base_options)
    data.update(
        {
            "notes": notas,
            "dynamics": dinamicas,
            "instruments": instrumentos,
            "num_instruments": numeros,
        }
    )
    onsets = [ev.onset for ev in vertical_slice.events]
    offsets = [ev.offset for ev in vertical_slice.events]
    durations = [ev.duration for ev in vertical_slice.events]
    part_ids = [ev.part_id for ev in vertical_slice.events]
    if any(v is not None for v in onsets):
        data["onsets"] = onsets
    if any(v is not None for v in offsets):
        data["offsets"] = offsets
    if any(v is not None for v in durations):
        data["durations"] = durations
    if any(v is not None for v in part_ids):
        data["part_ids"] = part_ids
    return data


def _metric_from_scalar(name: str, value: float, **kwargs: Any) -> MetricResult:
    return MetricResult(name=name, value=float(value), **kwargs)


def _build_slice_analysis(
    vertical_slice: VerticalSlice,
    resultados: dict[str, Any],
) -> VerticalSliceAnalysis:
    density = resultados.get("density", {})
    meta = resultados.get("metric_metadata", {})
    subindices = resultados.get("density_subindices", {})
    composite_val = float(density.get("total", 0.0))
    return VerticalSliceAnalysis(
        slice=vertical_slice,
        metrics={
            "density.total": _metric_from_scalar(
                "density.total",
                composite_val,
                source_type="metadata_proxy",
                validation_status="heuristic",
                confidence="medium",
                interpretation="Composite density at this vertical slice instant.",
            ),
            "density.interval": _metric_from_scalar(
                "density.interval",
                float(density.get("interval", 0.0)),
            ),
            "density.instrument": _metric_from_scalar(
                "density.instrument",
                float(density.get("instrument", 0.0)),
            ),
        },
        subindices=subindices,
        composite_density=_metric_from_scalar(
            "density.total",
            composite_val,
            source_type="metadata_proxy",
            validation_status="heuristic",
            confidence="medium",
        ),
        warnings=list(meta.get("warnings", [])),
        assumptions=list(meta.get("assumptions", [])),
    )


def load_timed_events_from_path(
    path: str | Path,
) -> tuple[list[InstrumentEvent], dict[str, Any], list[str]]:
    """Load timed events and analysis options from XML or MIDI."""
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Score file not found: {path}")
    suffix = filepath.suffix.lower()
    if suffix in (".xml", ".musicxml"):
        from xml_loader import parse_xml_to_events

        return parse_xml_to_events(str(filepath))
    if suffix in (".mid", ".midi"):
        from midi_loader import parse_midi_to_events

        return parse_midi_to_events(str(filepath))
    raise InputError(
        f"Unsupported score format: {suffix}. Use .xml or .mid/.midi.",
        field="source_path",
    )


def analyze_score(
    source: Union[str, Path, dict[str, Any], list[InstrumentEvent]],
    config: AnalysisConfig | dict[str, Any] | None = None,
) -> ScoreAnalysisResult:
    """
    Analyze a score or timed event list into temporal vertical slices.

    Args:
        source: File path (.xml / .mid), legacy input dict (single slice),
            or list of timed InstrumentEvent objects.
        config: Optional AnalysisConfig or options dict merged with file settings.

    Returns:
        ScoreAnalysisResult with per-slice analyses and time series.
    """
    warnings: list[str] = []
    assumptions: list[str] = [
        "Score analysis uses symbolic/metadata proxies — not measured acoustics.",
    ]
    base_options = _default_analysis_options()
    events: list[InstrumentEvent]
    source_path: str | None = None

    if isinstance(source, (str, Path)):
        source_path = str(source)
        events, file_options, load_warnings = load_timed_events_from_path(source)
        warnings.extend(load_warnings)
        base_options.update(file_options)
    elif isinstance(source, list):
        events = list(source)
    elif isinstance(source, dict):
        from core.converters import legacy_input_to_vertical_slice

        vertical_slice = legacy_input_to_vertical_slice(source)
        events = vertical_slice.events
        base_options.update(
            {k: v for k, v in source.items() if k not in ("notes", "dynamics", "instruments", "num_instruments")}
        )
    else:
        raise InputError(
            "source must be a file path, legacy input dict, or list[InstrumentEvent]",
            field="source",
        )

    if config is not None:
        if isinstance(config, AnalysisConfig):
            analysis_config = config
            base_options.update(
                {
                    "weight_factor": config.weight_factor,
                }
            )
        else:
            analysis_config = analysis_config_from_input({**base_options, **config})
            base_options.update(config)
    else:
        analysis_config = analysis_config_from_input(base_options)

    temporal_mode: TemporalMode = "event_boundary"
    if isinstance(config, dict):
        mode_val = config.get("temporal_mode", temporal_mode)
        if mode_val in ("event_boundary", "instantaneous"):
            temporal_mode = mode_val
    elif analysis_config.temporal_config:
        mode_val = analysis_config.temporal_config.get("mode", temporal_mode)
        if mode_val in ("event_boundary", "instantaneous"):
            temporal_mode = mode_val

    slices = group_events_into_slices(events, mode=temporal_mode)
    if len(slices) == 1 and not events_have_timing(events):
        assumptions.append(
            "Input has no onset/offset metadata; treated as a single vertical slice."
        )

    slice_analyses: list[VerticalSliceAnalysis] = []
    time_series: list[dict[str, Any]] = []

    for vertical_slice in slices:
        input_data = vertical_slice_to_input_data(vertical_slice, base_options)
        resultados, _, _ = calculate_metrics(input_data)
        slice_analysis = _build_slice_analysis(vertical_slice, resultados)
        slice_analyses.append(slice_analysis)

        density = resultados.get("density", {})
        sub = resultados.get("density_subindices", {})
        time_series.append(
            {
                "time": vertical_slice.time,
                "duration": vertical_slice.duration,
                "slice_id": vertical_slice.slice_id,
                "event_count": len(vertical_slice.events),
                "density_total": float(density.get("total", 0.0)),
                "density_interval": float(density.get("interval", 0.0)),
                "density_instrument": float(density.get("instrument", 0.0)),
                "density_weighted": float(density.get("weighted", 0.0)),
                "player_weighted_count": sub.get("event_count", {})
                .get("raw", {})
                .get("player_weighted_count"),
            }
        )

    summary_stats = summarize_time_series(time_series)
    global_summary = {
        "slice_count": _metric_from_scalar(
            "slice_count",
            summary_stats.get("slice_count", len(slice_analyses)),
            source_type="score_derived",
            validation_status="verified_only",
            confidence="high",
            interpretation="Number of vertical slices in temporal analysis.",
        ),
    }
    for key, val in summary_stats.items():
        if key == "slice_count":
            continue
        global_summary[key] = _metric_from_scalar(
            key,
            val,
            source_type="score_derived",
            validation_status="verified_only",
            confidence="medium",
            interpretation=f"Summary statistic of {key} across slices.",
        )

    return ScoreAnalysisResult(
        source_path=source_path,
        slices=slice_analyses,
        time_series=time_series,
        global_summary=global_summary,
        config=analysis_config,
        warnings=warnings,
        assumptions=assumptions,
    )
