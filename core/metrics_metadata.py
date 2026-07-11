"""
Epistemic labelling and structured metric metadata (Phase 3).

Symbolic and metadata-proxy outputs are labelled with source type,
validation status, and confidence. Textural Density does not implement auditory or
psychoacoustic modelling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from config import DYNAMIC_LEVELS, MAX_DENS_GLOBAL, USE_LOG_COMPRESSION
from core.quantity_scaling import (
    COHERENT_PHASE_LOCKED_ADDITION_ASSUMED,
    QUANTITY_PRESSURE_GAIN_FORMULA,
    QUANTITY_POWER_GAIN_FORMULA,
    QUANTITY_SCALING_MODEL,
    quantity_scaling_metadata,
)
from core.defaults import (
    METRIC_SCHEMA_VERSION,
    is_score_only_config,
)
from core.hash_utils import config_hash, input_hash_from_dict
from core.models import AnalysisConfig, MetricResult, VerticalSlice
from instrumentos.gpr_dynamic_interpolation import MEASURED_SUPPORT, tail_saturation_info
from instrumentos.registry import resolve_profile
from instrumentos.violin_sordina_diagnostics import (
    AUDIT_FLAG_CRITICAL,
    AUDIT_FLAG_HIGH,
    input_implies_violin_sordina,
    summarize_compare_flags,
)


def _instrument_density_epistemics(
    vertical_slice: VerticalSlice,
) -> tuple[str, str, list[str], list[str]]:
    """
    Return (source_type, validation_status, assumptions, warnings) for instrument density.
    """
    has_gpr = False
    has_coarse = False
    assumptions: list[str] = []
    warnings: list[str] = []

    for event in vertical_slice.events:
        profile = resolve_profile(event.instrument_name)
        if profile is None or profile.instrument_id == "unknown":
            has_coarse = True
            continue
        if profile.module_name:
            has_gpr = True
            if profile.profile_status in ("literature_derived", "literature_informed", "empirical_source", "empirical_profile"):
                assumptions.append(
                    f"Instrument '{event.instrument_name}' uses externally sourced acoustic "
                    f"metadata via instrumentos/{profile.module_name}.py (GPR interpolation)."
                )
        else:
            has_coarse = True

    if has_gpr:
        source_type = "external_acoustic_metadata"
        validation = "partially_calibrated" if not has_coarse else "heuristic"
        assumptions.append(
            "Instrument density applies pre-loaded external acoustic metadata to notated "
            "pitch and dynamic markings; the pipeline does not analyse audio waveforms."
        )
    else:
        source_type = "metadata_proxy"
        validation = "heuristic"
        assumptions.append(
            "No GPR acoustic tables for this slice; instrument density uses coarse "
            "register/dynamic fallback metadata only."
        )
        warnings.append(
            "Instrument density relies on coarse fallback profiles without external acoustic tables."
        )

    # Deduplicate while preserving order
    assumptions = list(dict.fromkeys(assumptions))
    warnings = list(dict.fromkeys(warnings))
    return source_type, validation, assumptions, warnings


# Normalisation constants documented in metadata (not hidden)
WEIGHTED_DI_MAX = 100.0
WEIGHTED_DV_MAX = 10.0


@dataclass
class MetricAssemblyContext:
    """Inputs required to label metrics after numeric computation."""

    vertical_slice: VerticalSlice
    config: AnalysisConfig
    interval_density_raw: float
    interval_density_reported: float
    instrument_density: float
    weighted_density: float
    refined_density: float
    total_density: float
    total_density_pre_log: Optional[float]
    sonic_mass: float
    absolute_density: float
    harmonic_ratio: float
    complexity: float
    spectral_moments: dict[str, Any]
    chroma_vector: Any
    texture: dict[str, Any]
    timbre: dict[str, Any]
    orchestration: dict[str, Any]
    amplitude_semitones: float
    cohesion_factor: float
    complexity_factor: float
    dynamic_boost: float
    pitch_aggregation: dict[str, Any] | None = None
    extra_warnings: list[str] = field(default_factory=list)
    extra_assumptions: list[str] = field(default_factory=list)


def metric_result_to_dict(result: MetricResult) -> dict[str, Any]:
    """JSON-serializable representation of a MetricResult."""
    payload: dict[str, Any] = {
        "name": result.name,
        "value": _serialize_value(result.value),
        "source_type": result.source_type,
        "validation_status": result.validation_status,
        "confidence": result.confidence,
        "interpretation": result.interpretation,
        "warnings": list(result.warnings),
        "assumptions": list(result.assumptions),
    }
    if result.unit is not None:
        payload["unit"] = result.unit
    if result.raw_value is not None:
        payload["raw_value"] = _serialize_value(result.raw_value)
    if result.normalized_value is not None:
        payload["normalized_value"] = float(result.normalized_value)
    if result.range is not None:
        payload["range"] = [float(result.range[0]), float(result.range[1])]
    return payload


def _serialize_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return float(value)
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    return value


def collect_slice_warnings(
    vertical_slice: VerticalSlice,
    config: AnalysisConfig,
) -> tuple[list[str], list[str]]:
    """Return (warnings, assumptions) from score-event inspection."""
    warnings: list[str] = []
    assumptions: list[str] = []

    known_dynamics = {d.lower() for d in (DYNAMIC_LEVELS or [])}

    for event in vertical_slice.events:
        dyn = (event.dynamic or "").lower()
        if dyn and dyn not in known_dynamics:
            warnings.append(
                f"Unknown dynamic '{event.dynamic}' at event {event.event_id}; "
                "mapped to 'mf' for instrument density."
            )
        profile = resolve_profile(event.instrument_name)
        if profile is not None and profile.module_name:
            tail = tail_saturation_info(dyn)
            if tail is not None:
                warnings.append(
                    f"Instrument '{event.instrument_name}' dynamic "
                    f"'{tail['requested_level']}' at event {event.event_id} is outside "
                    f"measured support {tuple(MEASURED_SUPPORT)}; boundary "
                    f"'{tail['boundary_level']}', ratio {tail['ratio']}^{tail['steps']}. "
                    "Dynamic level outside measured support; saturated extrapolation applied."
                )
        if profile is None:
            warnings.append(
                f"Instrument '{event.instrument_name}' has no registry profile; "
                "modelling uses generic coarse proxy."
            )
        elif profile.profile_status in ("coarse_default", "symbolic_default"):
            warnings.append(
                f"Instrument '{event.instrument_name}' uses symbolic_default profile "
                f"(uncertainty={profile.uncertainty})."
            )
            for w in profile.missing_data_warnings:
                if w not in warnings:
                    warnings.append(w)
        elif profile.uncertainty == "high":
            warnings.append(
                f"Instrument '{event.instrument_name}' profile has high uncertainty."
            )
        if event.family == "unknown":
            warnings.append(
                f"Unknown instrument family for '{event.instrument_name}'."
            )
        if input_implies_violin_sordina(event.instrument_name):
            profile_id = profile.instrument_id if profile is not None else None
            if profile_id != "violino_sordina":
                warnings.append(
                    "Input appears to request violin con sordina, but it did not "
                    "resolve to the violin_sordina profile."
                )

    if len(vertical_slice.events) < 2:
        warnings.append(
            "Fewer than two simultaneous events; interval compactness is zero or unstable."
        )

    assumptions.append(
        "Dynamics (p, mf, ff, …) are symbolic score markings; numeric weights are modelling assumptions."
    )
    assumptions.append(
        "Where instrument modules exist, density uses externally sourced sparse acoustic "
        "amplitude tables (GPR interpolation), not live audio analysis."
    )
    assumptions.append(
        "This analysis uses score/information input only — no audio waveforms were analysed at runtime."
    )

    return warnings, assumptions


def build_metric_metadata(context: MetricAssemblyContext) -> dict[str, Any]:
    """Build full metric_metadata block for results dict."""
    slice_warnings, slice_assumptions = collect_slice_warnings(
        context.vertical_slice, context.config
    )
    global_warnings = slice_warnings + list(context.extra_warnings)
    global_assumptions = slice_assumptions + list(context.extra_assumptions)

    metrics: dict[str, MetricResult] = {}

    score_only = is_score_only_config(context.config)

    metrics["density.interval"] = MetricResult(
        name="density.interval",
        value=float(context.interval_density_reported),
        raw_value=float(context.interval_density_raw),
        normalized_value=float(context.interval_density_reported),
        unit="dimensionless",
        source_type="score_derived",
        validation_status="verified_only",
        confidence="medium",
        interpretation=(
            "Interval compactness over distinct aggregated pitch bins only; "
            "exact unison doublings excluded from vertical interval structure."
        ),
        assumptions=[
            "Lambda calibrated against consonance ratings; symbolic pitch-distance model only.",
            "Pitch bins aggregated by exact MIDI (microtonal tolerance); unison pairs not counted.",
        ],
        warnings=[],
    )

    inst_source, inst_validation, inst_assumptions, inst_metric_warnings = (
        _instrument_density_epistemics(context.vertical_slice)
    )

    metrics["density.instrument"] = MetricResult(
        name="density.instrument",
        value=float(context.instrument_density),
        unit="dimensionless",
        source_type=inst_source,  # type: ignore[arg-type]
        validation_status=inst_validation,  # type: ignore[arg-type]
        confidence="medium",
        interpretation=(
            "Pressure-equivalent instrument density via incoherent RSS: "
            "sqrt(sum(qty_i × one_player_density_i²)). "
            "One-player density from GPR acoustic metadata × single dynamic lookup."
        ),
        assumptions=inst_assumptions + [
            "Quantity scaling model: incoherent source addition (not phase-locked N²).",
            "Qty affects pressure-equivalent density, not pitch-structure metrics.",
        ],
        warnings=inst_metric_warnings,
    )

    metrics["density.weighted"] = MetricResult(
        name="density.weighted",
        value=float(context.weighted_density),
        unit="dimensionless",
        source_type="metadata_proxy",
        validation_status="heuristic",
        confidence="medium",
        interpretation="Linear blend of instrument and interval density after min-max normalisation.",
        assumptions=[
            f"Normalisation uses DI_max={WEIGHTED_DI_MAX}, DV_max={WEIGHTED_DV_MAX}.",
            "Weighted density uses linear blend only (no power-law compression).",
        ],
        warnings=[
            f"Normalisation constants DI_max={WEIGHTED_DI_MAX}, DV_max={WEIGHTED_DV_MAX} are theoretical.",
        ],
    )

    metrics["density.refined"] = MetricResult(
        name="density.refined",
        value=float(context.refined_density),
        raw_value=float(context.interval_density_reported),
        unit="dimensionless",
        source_type="score_derived",
        validation_status="verified_only",
        confidence="medium",
        interpretation=(
            "Vertical pitch-structure density from distinct pitch bins "
            "(interval compactness, registral compactness, symbolic entropy, harmonicity). "
            "Zero when distinct_pitch_count < 2. Alias: density.pitch_structure."
        ),
    )

    metrics["density.pitch_structure"] = MetricResult(
        name="density.pitch_structure",
        value=float(context.refined_density),
        unit="dimensionless",
        source_type="score_derived",
        validation_status="verified_only",
        confidence="medium",
        interpretation=metrics["density.refined"].interpretation,
    )

    total_assumptions = [
        "Composite = pitch_structure_density × sqrt(sonic_mass) / MAX_DENS_GLOBAL.",
        f"Complexity factor (in pitch structure): {context.complexity_factor:.4f}.",
        f"Dynamic mass boost sqrt(sonic_mass): {context.dynamic_boost:.4f}.",
        f"Normalised by MAX_DENS_GLOBAL={MAX_DENS_GLOBAL}.",
    ]
    if USE_LOG_COMPRESSION:
        total_assumptions.append(
            f"log10(1+x) compression applied (USE_LOG_COMPRESSION=True); "
            f"pre-log value≈{context.total_density_pre_log}."
        )

    metrics["density.total"] = MetricResult(
        name="density.total",
        value=float(context.total_density),
        raw_value=context.total_density_pre_log,
        normalized_value=float(context.total_density),
        unit="dimensionless",
        source_type="metadata_proxy",
        validation_status="heuristic",
        confidence="medium",
        interpretation="Composite heuristic score; not a validated perceptual density index.",
        assumptions=total_assumptions,
    )

    metrics["density.sonic_mass"] = MetricResult(
        name="density.sonic_mass",
        value=float(context.sonic_mass),
        unit="dimensionless",
        source_type="symbolic_metadata",
        validation_status="verified_only",
        confidence="medium",
        interpretation=(
            "Symbolic orchestration mass: sum(qty_i × one_player_density_i). "
            "Linear player-count scaling; not loudness, SPL, or measured ensemble loudness."
        ),
        assumptions=[
            "Dynamic applied once via instrument-module lookup (not doubled in mass formula).",
            "Incoherent source addition; mass scales linearly with player count.",
        ],
    )

    metrics["density.absolute"] = MetricResult(
        name="density.absolute",
        value=float(context.absolute_density),
        unit="dimensionless",
        source_type="score_derived",
        validation_status="theoretical",
        confidence="medium",
        interpretation="Weighted density × log(1 + event count) reference scalar.",
    )

    metrics["additional_metrics.harmonic_ratio"] = MetricResult(
        name="additional_metrics.harmonic_ratio",
        value=float(context.harmonic_ratio),
        unit="ratio",
        source_type="metadata_proxy",
        validation_status="heuristic",
        confidence="low",
        interpretation="Harmonic-template match on symbolic pitch/weight arrays — not measured harmonicity.",
    )

    metrics["additional_metrics.complexity"] = MetricResult(
        name="additional_metrics.complexity",
        value=float(context.complexity),
        unit="dimensionless",
        source_type="metadata_proxy",
        validation_status="heuristic",
        confidence="medium",
        interpretation="1 + ln(1 + spectral entropy) from symbolic spectral weights.",
    )

    centroid_hz = context.spectral_moments.get("centroid", {}).get("frequency", 0)
    metrics["spectral_moments.centroid"] = MetricResult(
        name="spectral_moments.centroid",
        value=centroid_hz,
        unit="Hz",
        source_type="metadata_proxy",
        validation_status="heuristic",
        confidence="low",
        interpretation=(
            "Estimated spectral centroid from symbolic MIDI→Hz and instrument-density weights."
        ),
        warnings=["Not measured from an audio spectrum."],
    )

    chroma_val = context.chroma_vector
    metrics["additional_metrics.chroma_vector"] = MetricResult(
        name="additional_metrics.chroma_vector",
        value=_serialize_value(chroma_val),
        unit="probability_mass",
        source_type="score_derived",
        validation_status="verified_only",
        confidence="high",
        interpretation="Pitch-class distribution from symbolic pitches.",
    )

    player_count = 0
    if context.pitch_aggregation:
        player_count = int(
            context.pitch_aggregation.get(
                "player_count",
                context.pitch_aggregation.get("total_player_count", 0),
            )
        )

    return {
        "score_only_mode": score_only,
        "metric_schema_version": METRIC_SCHEMA_VERSION,
        "validation_status": "verified_only",
        "config_hash": config_hash(context.config),
        "metrics": {k: metric_result_to_dict(v) for k, v in metrics.items()},
        "warnings": global_warnings,
        "assumptions": global_assumptions,
        "quantity_scaling": quantity_scaling_metadata(player_count=player_count),
        "quantity_scaling_model": QUANTITY_SCALING_MODEL,
        "quantity_power_gain_formula": QUANTITY_POWER_GAIN_FORMULA,
        "quantity_pressure_gain_formula": QUANTITY_PRESSURE_GAIN_FORMULA,
        "coherent_phase_locked_addition_assumed": COHERENT_PHASE_LOCKED_ADDITION_ASSUMED,
        "normalization": {
            "MAX_DENS_GLOBAL": MAX_DENS_GLOBAL,
            "USE_LOG_COMPRESSION": USE_LOG_COMPRESSION,
            "WEIGHTED_DI_MAX": WEIGHTED_DI_MAX,
            "WEIGHTED_DV_MAX": WEIGHTED_DV_MAX,
        },
    }


def attach_metric_metadata(
    resultados: dict[str, Any],
    context: MetricAssemblyContext,
    *,
    input_data: dict[str, Any] | None = None,
    software_version: str | None = None,
) -> dict[str, Any]:
    """Add metric_metadata to results dict in place and return it."""
    meta = build_metric_metadata(context)
    if context.pitch_aggregation:
        meta["pitch_aggregation"] = context.pitch_aggregation
        lookup_trace = context.pitch_aggregation.get("instrument_lookup_trace") or []
        if lookup_trace:
            meta["instrument_lookup_trace"] = lookup_trace
            flagged = [
                row
                for row in lookup_trace
                if row.get("audit_flag") in (AUDIT_FLAG_HIGH, AUDIT_FLAG_CRITICAL)
            ]
            if flagged:
                meta["violin_sordina_arco_audit_flags"] = flagged
        if any(row.get("module_name") == "violin_sordina" for row in lookup_trace):
            meta["violin_sordina_arco_table_summary"] = summarize_compare_flags()
    if input_data is not None:
        meta["input_hash"] = input_hash_from_dict(input_data)
    if software_version:
        meta["software_version"] = software_version
    resultados["metric_metadata"] = meta
    return resultados
