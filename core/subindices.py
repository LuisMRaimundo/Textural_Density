"""
Interpretable vertical-density subindices (Phase 5).

Decomposes the composite density score into score-derived and metadata-proxy
components computed from notated/input symbolic events only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from config import (
    COMPOSITE_HARMONIC_DAMPING,
    DEFAULT_REGISTER_BANDS,
    MAX_DENS_GLOBAL,
    USE_LOG_COMPRESSION,
)
from core.models import AnalysisConfig, VerticalSlice
from core.construct_metadata import attach_construct_records
from core.registral_density import register_band_occupancy, register_entropy
from core.temporal import resolve_event_duration


def _subindex_entry(
    *,
    raw: float | int | dict[str, Any],
    normalized: Optional[float] = None,
    source_type: str = "score_derived",
    validation_status: str = "verified_only",
    confidence: str = "medium",
    interpretation: str = "",
    unit: str = "dimensionless",
    warnings: Optional[list[str]] = None,
    assumptions: Optional[list[str]] = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "raw": raw,
        "source_type": source_type,
        "validation_status": validation_status,
        "confidence": confidence,
        "interpretation": interpretation,
        "unit": unit,
        "warnings": list(warnings or []),
        "assumptions": list(assumptions or []),
    }
    if normalized is not None:
        entry["normalized"] = float(normalized)
    return entry


@dataclass
class SubindexContext:
    """Inputs for vertical-density subindex assembly."""

    vertical_slice: VerticalSlice
    config: AnalysisConfig
    interval_compactness_raw: float
    interval_compactness_reported: float
    pitch_span_semitones: float
    sonic_mass: float
    harmonic_ratio: float
    chroma_vector: Any
    texture: dict[str, Any]
    timbre: dict[str, Any]
    orchestration: dict[str, Any]
    refined_density: float
    total_density: float
    total_density_pre_log: float
    cohesion_factor: float
    complexity_factor: float
    dynamic_boost: float
    pitch_aggregation: dict[str, Any] | None = None
    register_bands: dict[str, tuple[int, int]] = field(
        default_factory=lambda: dict(DEFAULT_REGISTER_BANDS)
    )


def build_density_subindices(context: SubindexContext) -> dict[str, Any]:
    """Build interpretable subindices block for results dict."""
    events = context.vertical_slice.events
    agg = context.pitch_aggregation or {}
    if agg.get("pitch_bins"):
        midis = [float(b["midi"]) for b in agg["pitch_bins"]]
    else:
        midis = [float(ev.sounding_pitch.midi) for ev in events]
    player_counts = [max(1, int(ev.player_count)) for ev in events]

    event_count = len(events)
    distinct_pitch_count = int(agg.get("distinct_pitch_count", len(midis)))
    doubling_count = int(agg.get("doubling_count", max(0, event_count - distinct_pitch_count)))
    player_weighted_count = float(sum(player_counts))

    durations = []
    for ev in events:
        dur = resolve_event_duration(ev)
        if dur is not None and dur > 0:
            durations.append(dur)
    duration_weighted_count: Optional[float] = None
    if durations and len(durations) == event_count:
        duration_weighted_count = float(
            sum(pc * d for pc, d in zip(player_counts, durations))
        )
    elif event_count and all(resolve_event_duration(ev) is not None for ev in events):
        resolved = [
            float(d)
            for ev in events
            for d in [resolve_event_duration(ev)]
            if d is not None
        ]
        duration_weighted_count = float(
            sum(pc * d for pc, d in zip(player_counts, resolved))
        )

    band_occupancy = register_band_occupancy(midis, context.register_bands)
    register_entropy_val = register_entropy(band_occupancy)
    max_band_entropy = np.log2(len(context.register_bands)) if len(context.register_bands) > 1 else 1.0
    register_entropy_norm = (
        register_entropy_val / max_band_entropy if max_band_entropy > 0 else 0.0
    )

    pitch_span = float(context.pitch_span_semitones)
    registral_dispersion = (
        pitch_span / max(1, distinct_pitch_count - 1) if distinct_pitch_count > 1 else 0.0
    )
    registral_compression = 1.0 / (1.0 + pitch_span) if distinct_pitch_count >= 2 else 0.0

    chroma = np.asarray(context.chroma_vector, dtype=float)
    chroma_concentration = float(np.max(chroma)) if chroma.size else 0.0

    timbre_div = float(context.timbre.get("timbre_diversity", 0))
    timbre_blend = float(context.timbre.get("timbre_balance", 0))
    family_ids = {ev.family for ev in events}
    family_diversity = len(family_ids) / max(1, event_count)

    has_temporal = any(
        ev.onset is not None or ev.offset is not None or resolve_event_duration(ev) is not None
        for ev in events
    )

    harmonic_adjustment = 1.0 - context.harmonic_ratio * COMPOSITE_HARMONIC_DAMPING
    composite_product = context.refined_density * context.dynamic_boost

    subindices: dict[str, Any] = {
        "event_count": _subindex_entry(
            raw={
                "event_count": event_count,
                "distinct_pitch_count": distinct_pitch_count,
                "doubling_count": doubling_count,
                "player_weighted_count": player_weighted_count,
                "duration_weighted_count": duration_weighted_count,
            },
            normalized=player_weighted_count / max(1, event_count),
            interpretation=(
                "Simultaneous sounding events; player-weighted count includes doublings. "
                "Distinct pitch count uses aggregated pitch bins."
            ),
            assumptions=[
                "Duration weighting requires onset/offset or duration on every event.",
            ],
        ),
        "interval_compactness": _subindex_entry(
            raw=float(context.interval_compactness_raw),
            normalized=float(context.interval_compactness_reported),
            source_type="score_derived",
            validation_status="verified_only",
            confidence="medium",
            interpretation=(
                "Interval compactness over distinct aggregated pitch bins; "
                "exact unison doublings excluded."
            ),
            warnings=(
                ["unison_doublings_excluded_from_interval_structure"]
                if doubling_count > 0
                else []
            ),
        ),
        "registral": _subindex_entry(
            raw={
                "pitch_span_semitones": pitch_span,
                "distinct_pitch_count": distinct_pitch_count,
                "register_band_occupancy": band_occupancy,
                "register_entropy": register_entropy_val,
                "registral_dispersion": registral_dispersion,
                "registral_compression": registral_compression,
            },
            normalized=register_entropy_norm,
            interpretation=(
                "Register spread and band occupancy from distinct aggregated pitch bins."
            ),
            assumptions=[
                f"Register bands are configurable defaults: {list(context.register_bands)}.",
            ],
        ),
        "orchestral_mass": _subindex_entry(
            raw=float(context.sonic_mass),
            normalized=float(context.dynamic_boost),
            source_type="symbolic_metadata",
            validation_status="verified_only",
            confidence="medium",
            interpretation=(
                "Symbolic orchestration mass from written dynamics and player counts."
            ),
            warnings=[
                "Written dynamics (p, mf, ff) are symbolic score markings, not SPL.",
            ],
            assumptions=[
                "Dynamic-to-weight mapping is symbolic dynamic weighting for score analysis.",
                "Instrument density component uses externally sourced acoustic metadata where GPR modules exist.",
            ],
        ),
        "timbral_heterogeneity": _subindex_entry(
            raw={
                "family_diversity": family_diversity,
                "instrument_diversity": timbre_div,
                "blend_index": timbre_blend,
                "orchestration_evenness": float(
                    context.orchestration.get("orchestration_evenness", 0)
                ),
            },
            normalized=float(context.orchestration.get("register_balance", 0)),
            source_type="symbolic_metadata",
            validation_status="verified_only",
            confidence="medium",
            interpretation=(
                "Timbral/orchestration complexity from symbolic instrument metadata — "
                "not measured timbre."
            ),
            warnings=["Not measured timbre or acoustic spectral overlap."],
        ),
        "harmonicity_proxy": _subindex_entry(
            raw={
                "harmonic_ratio": float(context.harmonic_ratio),
                "chroma_concentration": chroma_concentration,
            },
            normalized=float(context.harmonic_ratio),
            source_type="metadata_proxy",
            validation_status="heuristic",
            confidence="low",
            interpretation=(
                "Harmonic-template and pitch-class concentration proxies from "
                "input symbolic pitches — distinct from interval compactness."
            ),
            warnings=[
                "Harmonicity and interval compactness are separate constructs.",
            ],
        ),
        "temporal": _subindex_entry(
            raw={
                "available": has_temporal,
                "duration_weighted_event_count": duration_weighted_count,
            },
            normalized=None if not has_temporal else duration_weighted_count,
            source_type="score_derived",
            validation_status="verified_only" if has_temporal else "theoretical",
            confidence="high" if has_temporal else "low",
            interpretation=(
                "Temporal vertical density requires onset/offset metadata "
                "(full time-series analysis in Phase 6)."
            ),
            warnings=(
                []
                if has_temporal
                else ["No temporal metadata on events; temporal subindex unavailable."]
            ),
        ),
        "composite": {
            "value": float(context.total_density),
            "pre_log": float(context.total_density_pre_log),
            "source_type": "metadata_proxy",
            "validation_status": "heuristic",
            "confidence": "medium",
            "interpretation": (
                "Decomposable composite heuristic; components listed below."
            ),
            "components": {
                "pitch_structure_density": float(context.refined_density),
                "dynamic_boost": float(context.dynamic_boost),
                "normalization_divisor": MAX_DENS_GLOBAL,
                "log_compression_applied": USE_LOG_COMPRESSION,
            },
            "component_product_pre_norm": float(composite_product),
            "dominant_factors": _rank_dominant_factors(context),
            "warnings": _composite_warnings(context),
        },
    }

    return subindices


def _rank_dominant_factors(context: SubindexContext) -> list[str]:
    """Rank composite multipliers by deviation from unity (simple dominance hint)."""
    factors = {
        "pitch_structure_density": context.refined_density,
        "dynamic_boost": context.dynamic_boost,
    }
    ranked = sorted(factors.items(), key=lambda kv: abs(np.log(max(kv[1], 1e-9))), reverse=True)
    return [name for name, _ in ranked[:3]]


def _composite_warnings(context: SubindexContext) -> list[str]:
    return []


def attach_density_subindices(resultados: dict[str, Any], context: SubindexContext) -> dict[str, Any]:
    """Add density_subindices and construct_records to results dict in place."""
    resultados["density_subindices"] = build_density_subindices(context)
    score_only = True
    meta = resultados.get("metric_metadata")
    if isinstance(meta, dict) and "score_only_mode" in meta:
        score_only = bool(meta["score_only_mode"])
    return attach_construct_records(resultados, score_only_mode=score_only)
