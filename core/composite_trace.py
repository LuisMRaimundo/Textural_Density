"""Composite density dependency trace — makes construct overlap inspectable."""



from __future__ import annotations



from typing import Any





def build_composite_trace(

    *,

    instrument_density: float,

    interval_density: float,

    weighted_density: float,

    pitch_structure_density: float,

    registral_span: float,

    distinct_pitch_count: int,

    event_count: int,

    complexity_factor: float,

    harmonic_ratio: float,

    sonic_mass: float,

    total_density: float,

    pitch_aggregation: dict[str, Any] | None = None,

    instrument_lookup_trace: list[dict[str, Any]] | None = None,

) -> dict[str, Any]:

    trace = {

        "weighted_density": {

            "value": float(weighted_density),

            "depends_on": ["instrument_density", "interval_compactness_distinct"],

        },

        "interval_compactness_distinct": {

            "value": float(interval_density),

            "depends_on": ["distinct_pitch_count", "pitch_bins"],

        },

        "pitch_structure_density": {

            "value": float(pitch_structure_density),

            "depends_on": [

                "interval_compactness_distinct",

                "distinct_pitch_count",

                "registral_span",

                "symbolic_entropy",

                "harmonicity_proxy",

                "pitch_differentiation_ratio",

            ],

        },

        "complexity_factor": {

            "value": float(complexity_factor),

            "depends_on": ["symbolic_entropy", "pitch_bins"],

        },

        "sonic_mass": {

            "value": float(sonic_mass),

            "depends_on": ["raw_event_count", "player_count", "instrument_density"],

        },

        "total_density": {

            "value": float(total_density),

            "depends_on": ["pitch_structure_density", "sonic_mass"],

        },

    }

    warnings: list[str] = []

    if distinct_pitch_count < 2 and event_count >= 2:

        warnings.append(

            "exact unison doublings: pitch_structure_density is zero; "

            "sonic_mass remains event-based"

        )

    if pitch_aggregation and pitch_aggregation.get("doubling_count", 0) > 0:

        warnings.append(

            "pitch aggregation applied: interval structure uses distinct pitch bins only"

        )

    return {

        "steps": trace,

        "overlap_warnings": warnings,

        "inputs": {

            "instrument_density": float(instrument_density),

            "interval_compactness_distinct": float(interval_density),

            "registral_span": float(registral_span),

            "distinct_pitch_count": int(distinct_pitch_count),

            "event_count": int(event_count),

            "harmonic_ratio": float(harmonic_ratio),

            "sonic_mass": float(sonic_mass),

            "pitch_aggregation": pitch_aggregation or {},

            "instrument_lookup_trace": instrument_lookup_trace or [],

        },

    }

