"""
Composite symbolic density assembly — weighted blend metadata and helpers.

Strictly symbolic: linear normalized blend only (no Stevens/power-law compression).

Single source of truth for the blend expression used in computation AND display:
``D_blend = BLEND_SCALE * (w * DI/DI_max + (1-w) * DV/DV_max)``.
Header / metadata strings are f-strings over these same names — never hand-copied.
"""

from __future__ import annotations

import math
from typing import Any, Optional

from core.pitch_structure import compute_composite_vertical_density
from core.sensitivity import DEFAULT_WEIGHT_SETS

DOCUMENTED_COMPOSITE_WEIGHTS: dict[str, float] = dict(
    DEFAULT_WEIGHT_SETS["baseline"]
)

# Blend scale and min-max caps — referenced by compute_* and format_* alike.
BLEND_SCALE = 10.0
WEIGHTED_DI_MAX = 100.0
WEIGHTED_DV_MAX = 10.0


def compute_blend_density(
    DI: float,
    DV: float,
    w: float = 0.5,
    *,
    DI_max: float = WEIGHTED_DI_MAX,
    DV_max: float = WEIGHTED_DV_MAX,
    scale: float = BLEND_SCALE,
) -> float:
    """
    Slider-controlled blend (``density.weighted``).

    Equivalent forms (same floats when caps/scale are the defaults):
      scale * (w * DI/DI_max + (1-w) * DV/DV_max)
      w * (scale/DI_max) * DI + (1-w) * (scale/DV_max) * DV
    With defaults: ``w*(DI/10) + (1-w)*DV`` — equals weighted_orch + weighted_pitch.
    """
    return float(scale * (w * (DI / DI_max) + (1.0 - w) * (DV / DV_max)))


def blend_definition_expression(
    *,
    DI_max: float = WEIGHTED_DI_MAX,
    DV_max: float = WEIGHTED_DV_MAX,
    scale: float = BLEND_SCALE,
) -> str:
    """
    Symbolic D_blend definition using the same constants as ``compute_blend_density``.

    Prefer the expanded two-term form (no leading scale factor that can be
    double-counted when auditing against printed weighted components):
    ``w*(DI/(DI_max/scale)) + (1-w)*(DV/(DV_max/scale))``.
    """
    di_div = DI_max / scale
    dv_div = DV_max / scale
    if abs(dv_div - 1.0) < 1e-12:
        return f"w*(DI/{di_div:g}) + (1-w)*DV"
    return f"w*(DI/{di_div:g}) + (1-w)*(DV/{dv_div:g})"


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
    DI_max: float = WEIGHTED_DI_MAX,
    DV_max: float = WEIGHTED_DV_MAX,
    scale: float = BLEND_SCALE,
) -> str:
    """
    Numerical Results header line — formula text is derived from the same
    constants/expression as ``compute_blend_density`` / ``compute_composite_from_blend``.
    """
    outer = composite_outer_expression(use_log_compression=use_log_compression)
    blend_def = blend_definition_expression(DI_max=DI_max, DV_max=DV_max, scale=scale)
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
    DI_max: float = WEIGHTED_DI_MAX,
    DV_max: float = WEIGHTED_DV_MAX,
    scale: float = BLEND_SCALE,
) -> str:
    """Static formula string for ``composite_meta['formula']`` (no slice values)."""
    outer = composite_outer_expression(use_log_compression=use_log_compression)
    blend_def = blend_definition_expression(DI_max=DI_max, DV_max=DV_max, scale=scale)
    return f"{outer} with D_blend = {blend_def}"


def compute_weighted_density_normalized(
    DI: float,
    DV: float,
    metodo: str = "min-max",
    w: float = 0.5,
    DI_max: float = WEIGHTED_DI_MAX,
    DV_max: float = WEIGHTED_DV_MAX,
) -> Optional[float]:
    """
    Normalised weighted blend of instrument and interval density.

    Min-max path delegates to ``compute_blend_density`` (single expression).
    """
    try:
        if metodo == "min-max":
            return compute_blend_density(
                DI, DV, w, DI_max=DI_max, DV_max=DV_max, scale=BLEND_SCALE
            )
        if metodo == "z-score":
            DI_mean, DI_std = 50, 25
            DV_mean, DV_std = 5, 2.5
            DI_norm = (DI - DI_mean) / DI_std if DI_std > 0 else 0
            DV_norm = (DV - DV_mean) / DV_std if DV_std > 0 else 0
            return float(BLEND_SCALE * (w * DI_norm + (1 - w) * DV_norm))
        raise ValueError(f"Invalid method: '{metodo}'. Choose 'min-max' or 'z-score'.")
    except ValueError:
        raise
    except Exception as e:
        import logging

        logging.error(f"Error computing weighted density: {e}")
        return None


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
            "DI_max": WEIGHTED_DI_MAX,
            "DV_max": WEIGHTED_DV_MAX,
            "blend_scale": BLEND_SCALE,
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
            "Weighted density uses linear min-max normalization and blend only.",
            "Sensitivity weights are diagnostic only.",
        ],
        "warnings": [],
    }
