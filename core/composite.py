"""
Composite symbolic density assembly — weighted blend metadata and helpers.

Strictly symbolic: fixed-divisor instrument term plus effective interval
cardinality. No data-dependent min/max, no unit-range mode.
"""

from __future__ import annotations

import math
from typing import Any, Optional

from core.pitch_structure import compute_composite_vertical_density
from core.sensitivity import DEFAULT_WEIGHT_SETS

DOCUMENTED_COMPOSITE_WEIGHTS: dict[str, float] = dict(
    DEFAULT_WEIGHT_SETS["baseline"]
)

# Instrument term divisor: w * DI / INSTRUMENT_BLEND_DIVISOR.
# DV enters the blend without a divisor.
INSTRUMENT_BLEND_DIVISOR = 10.0
# Retained only as the equivalent identity DI_max = 10 * divisor for metadata.
WEIGHTED_DI_MAX = 100.0


def compute_blend_density(
    DI: float,
    DV: float,
    w: float = 0.5,
) -> float:
    """
    Slider-controlled blend (``density.weighted``).

    ``w * (DI / 10) + (1 - w) * DV``
    No clamping is applied to DI or DV.
    """
    return float(
        w * (float(DI) / INSTRUMENT_BLEND_DIVISOR) + (1.0 - w) * float(DV)
    )


def blend_term_contributions(
    *,
    DI: float,
    DV: float,
    w: float = 0.5,
) -> dict[str, Any]:
    """Realised blend-term contributions (diagnostic; does not change density)."""
    instrument_term = float(w * (float(DI) / INSTRUMENT_BLEND_DIVISOR))
    interval_term = float((1.0 - w) * float(DV))
    # Zero whenever distinct_pitch_count < 2 (DV=0) or w=1. Never emit inf/nan.
    if interval_term == 0.0 or not math.isfinite(interval_term):
        ratio: float | None = None
    else:
        raw_ratio = instrument_term / interval_term
        ratio = raw_ratio if math.isfinite(raw_ratio) else None
    return {
        "w": float(w),
        "instrument_divisor": float(INSTRUMENT_BLEND_DIVISOR),
        "instrument_term": instrument_term,
        "interval_term": interval_term,
        "instrument_to_interval_ratio": ratio,
    }


def blend_definition_expression() -> str:
    """Symbolic D_blend definition matching ``compute_blend_density``."""
    return f"w*(DI/{INSTRUMENT_BLEND_DIVISOR:g}) + (1-w)*DV"


def compute_composite_from_blend(
    d_blend: float,
    sonic_mass: float,
    ref: float,
    *,
    use_log_compression: bool,
) -> float:
    """Composite from blend, mass, and REF — delegates to the production formula."""
    total, _ = compute_composite_vertical_density(
        d_blend,
        sonic_mass,
        ref,
        apply_log_compression=use_log_compression,
    )
    return total


def composite_outer_expression(*, use_log_compression: bool) -> str:
    """Outer composite skeleton (evaluable once D_blend, M, REF are bound)."""
    if use_log_compression:
        return "log10(1 + D_blend*sqrt(M)/REF)"
    return "D_blend*sqrt(M)/REF"


def format_composite_header_line(
    *,
    d_blend: float,
    sonic_mass: float,
    w: float,
    ref: float,
    use_log_compression: bool,
) -> str:
    """
    Numerical Results header line — formula text is derived from the same
    constants/expression as ``compute_blend_density`` / ``compute_composite_from_blend``.
    """
    outer = composite_outer_expression(use_log_compression=use_log_compression)
    blend_def = blend_definition_expression()
    return (
        f"Composite: {outer} with w={w:g}, REF={ref:g}, "
        f"D_blend={float(d_blend):.4f}, M={float(sonic_mass):.4f} "
        f"(D_blend = {blend_def})"
    )


def composite_formula_metadata(
    *,
    w: float,
    ref: float,
    use_log_compression: bool,
) -> str:
    """Static formula string for ``composite_meta['formula']`` (no slice values)."""
    outer = composite_outer_expression(use_log_compression=use_log_compression)
    blend_def = blend_definition_expression()
    return f"{outer} with D_blend = {blend_def}"


def build_composite_component_metadata(
    *,
    weighted_density: float,
    refined_density: float,
    total_density: float,
    total_density_pre_log: Optional[float],
    blend_weight_w: float = 0.5,
) -> dict[str, Any]:
    """Component-weight and assembly metadata for composite symbolic density."""
    return {
        "construct_id": "composite_symbolic_density",
        "value": float(total_density),
        "raw_value": total_density_pre_log,
        "normalized_value": float(total_density),
        "source_type": "metadata_proxy",
        "verification_status": "verified_by_tests",
        "included_in_composite": True,
        "component_weight": None,
        "blend_parameters": {
            "instrument_interval_blend_w": float(blend_weight_w),
            "instrument_divisor": float(INSTRUMENT_BLEND_DIVISOR),
            "definition": blend_definition_expression(),
        },
        "documented_sensitivity_weights": dict(DOCUMENTED_COMPOSITE_WEIGHTS),
        "components": {
            "weighted_density": float(weighted_density),
            "refined_density": float(refined_density),
        },
        "interpretation": (
            "Composite heuristic from score-derived and metadata-proxy subindices; "
            "subindices remain separately accessible."
        ),
        "assumptions": [
            "Weighted density is w*(DI/10) + (1-w)*DV; DV is effective interval cardinality.",
            "Sensitivity weights are diagnostic only.",
        ],
        "warnings": [],
    }
