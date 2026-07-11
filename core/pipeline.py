"""
Core-native vertical-slice analysis pipeline.

Single source of truth for ``calculate_metrics`` / ``calcular_metricas``.
Does not import Tkinter or GUI modules.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from config import MAX_DENS_GLOBAL, USE_LOG_COMPRESSION
from core.composite import compute_weighted_density_normalized
from core.converters import (
    analysis_config_from_input,
    legacy_input_to_vertical_slice,
    vertical_slice_to_legacy_lists,
)
from core.composite_trace import build_composite_trace
from core.defaults import apply_research_defaults
from core.input_validation import validate_no_removed_options
from core.instrument_lookup_trace import build_instrument_lookup_trace
from core.request import AnalysisRequest
from core.metrics_metadata import MetricAssemblyContext, attach_metric_metadata
from core.orchestration import compute_one_player_densities_for_slice, compute_slice_orchestral_metrics
from core.quantity_scaling import quantity_scaling_metadata
from core.pitch_aggregation import PitchAggregationResult, aggregate_events_by_pitch
from core.pitch_structure import (
    compute_composite_vertical_density,
    compute_interval_compactness_distinct,
    compute_pitch_structure_density,
    compute_registral_span_distinct,
)
from core.subindices import SubindexContext, attach_density_subindices
from error_handler import handle_exceptions
from instrumentos import get_instrument_module
from spectral_analysis import (
    calculate_chroma_vector,
    calculate_extended_spectral_moments,
    calculate_harmonic_ratio,
)
from timbre_texture_analysis import (
    calculate_orchestration_balance,
    calculate_texture_density,
    calculate_timbre_blend,
)

logger = logging.getLogger(__name__)


def load_instrument_module(instrument_name: str):
    """Resolve instrument module by name (delegates to ``instrumentos`` registry)."""
    return get_instrument_module(instrument_name)


def _bin_spectral_weights(pitch_agg: PitchAggregationResult) -> list[float]:
    """Mean weight per pitch bin — invariant under exact unison doublings within a bin."""
    return [b.total_weight / max(1, b.event_count) for b in pitch_agg.pitch_bins]


def _assemble_results(
    notas: list[str],
    dinamicas: list[str],
    instrumentos: list[str],
    numeros_instr: list[int],
    densidade_intervalar_val: float,
    densidade_instrumento_val: float,
    densidade_ponderada_val: float,
    pitch_structure_density: float,
    densidade_total_val: float,
    massa_sonora_val: float,
    densidade_absoluta_val: float,
    ext_mom: dict[str, Any],
    comp_dict: dict[str, Any],
    harm_rat: float,
    chroma: Any,
    texture: dict[str, Any],
    timbre: dict[str, Any],
    orch: dict[str, Any],
    pitch_aggregation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "density": {
            "interval": densidade_intervalar_val,
            "instrument": densidade_instrumento_val,
            "weighted": densidade_ponderada_val,
            "pitch_structure": pitch_structure_density,
            "refined": pitch_structure_density,
            "total": densidade_total_val,
            "sonic_mass": massa_sonora_val,
            "absolute": densidade_absoluta_val,
        },
        "spectral_moments": ext_mom,
        "additional_metrics": {
            "complexity": comp_dict.get("spectral_entropy", 0),
            "harmonic_ratio": harm_rat,
            "chroma_vector": chroma.tolist() if isinstance(chroma, np.ndarray) else chroma,
        },
        "texture": texture,
        "timbre": timbre,
        "orchestration": orch,
        "pitch_aggregation": pitch_aggregation,
        "input_data": {
            "notes": notas,
            "dynamics": dinamicas,
            "instruments": instrumentos,
            "num_instruments": numeros_instr,
        },
    }


@handle_exceptions(show_dialog=False, rethrow=True)
def calculate_metrics(
    input_data: AnalysisRequest | dict[str, Any],
) -> tuple[dict[str, Any], list[float], list[float]]:
    """
    Calculate symbolic vertical-slice density metrics from notated input events.

    Accepts ``AnalysisRequest`` (preferred) or legacy dict (compatibility).
    Returns ``(resultados, instrument_densities, pitches)``.
    """
    if isinstance(input_data, AnalysisRequest):
        input_data = apply_research_defaults(input_data.to_pipeline_dict())
    else:
        validate_no_removed_options(input_data)
        input_data = apply_research_defaults(dict(input_data))
    vertical_slice = legacy_input_to_vertical_slice(input_data)
    analysis_config = analysis_config_from_input(input_data)
    notas, dinamicas, instrumentos, numeros_instr = vertical_slice_to_legacy_lists(
        vertical_slice
    )
    weight_factor = float(input_data.get("weight_factor", 0.5))

    one_player_densities = compute_one_player_densities_for_slice(
        vertical_slice,
        load_instrument_module,
    )
    instrument_lookup_trace = build_instrument_lookup_trace(
        vertical_slice,
        one_player_densities,
    )
    densidade_instrumento_val, massa_sonora_val, aggregated_sources = (
        compute_slice_orchestral_metrics(
            notas,
            dinamicas,
            instrumentos,
            numeros_instr,
            one_player_densities,
        )
    )

    pitch_agg = aggregate_events_by_pitch(
        notas,
        weights=one_player_densities,
        player_counts=numeros_instr,
        dynamics=dinamicas,
        instruments=instrumentos,
    )

    densidade_intervalar_raw, densidade_intervalar_val = compute_interval_compactness_distinct(
        pitch_agg
    )

    bin_midis = pitch_agg.bin_midis
    bin_weights_spectral = _bin_spectral_weights(pitch_agg)
    bin_players = pitch_agg.bin_player_counts

    amplitude_st = compute_registral_span_distinct(pitch_agg)

    ext_mom = calculate_extended_spectral_moments(bin_midis, bin_weights_spectral)
    comp_dict = ext_mom
    chroma = calculate_chroma_vector(bin_midis, bin_weights_spectral)
    harm_rat = calculate_harmonic_ratio(bin_midis, bin_weights_spectral)
    spectral_entropy = float(comp_dict.get("spectral_entropy", 0))

    texture = calculate_texture_density(bin_midis, bin_players)
    timbre = calculate_timbre_blend(instrumentos, one_player_densities)
    orch = calculate_orchestration_balance(bin_midis, bin_weights_spectral, instrumentos)

    densidade_ponderada_val = compute_weighted_density_normalized(
        densidade_instrumento_val,
        densidade_intervalar_val,
        metodo="min-max",
        w=weight_factor,
    ) or 0.0
    weighted_orchestral = compute_weighted_density_normalized(
        densidade_instrumento_val, 0.0, metodo="min-max", w=weight_factor
    ) or 0.0
    weighted_pitch = compute_weighted_density_normalized(
        0.0, densidade_intervalar_val, metodo="min-max", w=weight_factor
    ) or 0.0

    pitch_structure_density = compute_pitch_structure_density(
        interval_sum_raw=densidade_intervalar_raw,
        aggregation=pitch_agg,
        spectral_entropy=spectral_entropy,
        harmonic_ratio=float(harm_rat),
    )

    densidade_total_val, densidade_total_pre_log = compute_composite_vertical_density(
        pitch_structure_density,
        massa_sonora_val,
        MAX_DENS_GLOBAL,
        apply_log_compression=USE_LOG_COMPRESSION,
    )

    mass_boost = float(np.sqrt(max(0.0, massa_sonora_val)))
    complexity_factor = 1.0 + float(np.log1p(spectral_entropy))

    total_tones_count = len(notas)
    if pitch_agg.distinct_pitch_count < 2:
        densidade_absoluta_val = 0.0
    else:
        densidade_absoluta_val = densidade_ponderada_val * np.log1p(total_tones_count)

    pitch_aggregation_dict = pitch_agg.to_dict()
    pitch_aggregation_dict["source_groups"] = [s.to_dict() for s in aggregated_sources]
    pitch_aggregation_dict["instrument_lookup_trace"] = instrument_lookup_trace
    resultados = _assemble_results(
        notas,
        dinamicas,
        instrumentos,
        numeros_instr,
        densidade_intervalar_val,
        densidade_instrumento_val,
        densidade_ponderada_val,
        pitch_structure_density,
        densidade_total_val,
        massa_sonora_val,
        densidade_absoluta_val,
        ext_mom,
        comp_dict,
        harm_rat,
        chroma,
        texture,
        timbre,
        orch,
        pitch_aggregation_dict,
    )
    resultados["density"]["weighted_pitch"] = float(weighted_pitch)
    resultados["density"]["weighted_orchestral"] = float(weighted_orchestral)
    resultados["quantity_scaling"] = quantity_scaling_metadata(
        player_count=int(pitch_agg.total_player_count)
    )

    try:
        from core.version import get_package_version

        software_version = get_package_version()
    except Exception:
        software_version = "unknown"

    pitches = [float(event.sounding_pitch.midi) for event in vertical_slice.events]

    attach_metric_metadata(
        resultados,
        MetricAssemblyContext(
            vertical_slice=vertical_slice,
            config=analysis_config,
            interval_density_raw=float(densidade_intervalar_raw),
            interval_density_reported=float(densidade_intervalar_val),
            instrument_density=float(densidade_instrumento_val),
            weighted_density=float(densidade_ponderada_val),
            refined_density=float(pitch_structure_density),
            total_density=float(densidade_total_val),
            total_density_pre_log=float(densidade_total_pre_log),
            sonic_mass=float(massa_sonora_val),
            absolute_density=float(densidade_absoluta_val),
            harmonic_ratio=float(harm_rat),
            complexity=spectral_entropy,
            spectral_moments=ext_mom,
            chroma_vector=chroma,
            texture=texture,
            timbre=timbre,
            orchestration=orch,
            amplitude_semitones=float(amplitude_st),
            cohesion_factor=1.0,
            complexity_factor=float(complexity_factor),
            dynamic_boost=float(mass_boost),
            pitch_aggregation=pitch_aggregation_dict,
        ),
        input_data=input_data,
        software_version=software_version,
    )
    attach_density_subindices(
        resultados,
        SubindexContext(
            vertical_slice=vertical_slice,
            config=analysis_config,
            interval_compactness_raw=float(densidade_intervalar_raw),
            interval_compactness_reported=float(densidade_intervalar_val),
            pitch_span_semitones=float(amplitude_st),
            sonic_mass=float(massa_sonora_val),
            harmonic_ratio=float(harm_rat),
            chroma_vector=chroma,
            texture=texture,
            timbre=timbre,
            orchestration=orch,
            refined_density=float(pitch_structure_density),
            total_density=float(densidade_total_val),
            total_density_pre_log=float(densidade_total_pre_log),
            cohesion_factor=1.0,
            complexity_factor=float(complexity_factor),
            dynamic_boost=float(mass_boost),
            pitch_aggregation=pitch_aggregation_dict,
        ),
    )
    resultados["composite_trace"] = build_composite_trace(
        instrument_density=float(densidade_instrumento_val),
        interval_density=float(densidade_intervalar_val),
        weighted_density=float(densidade_ponderada_val),
        pitch_structure_density=float(pitch_structure_density),
        registral_span=float(amplitude_st),
        distinct_pitch_count=int(pitch_agg.distinct_pitch_count),
        event_count=int(pitch_agg.event_count),
        complexity_factor=float(complexity_factor),
        harmonic_ratio=float(harm_rat),
        sonic_mass=float(massa_sonora_val),
        total_density=float(densidade_total_val),
        pitch_aggregation=pitch_aggregation_dict,
        instrument_lookup_trace=instrument_lookup_trace,
    )
    resultados["instrument_lookup_trace"] = instrument_lookup_trace
    return resultados, one_player_densities, pitches


calcular_metricas = calculate_metrics

__all__ = [
    "calculate_metrics",
    "calcular_metricas",
    "load_instrument_module",
]
