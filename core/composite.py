"""
Composite symbolic density assembly — weighted blend metadata and helpers.

Strictly symbolic: linear normalized blend only (no Stevens/power-law compression).
"""

from __future__ import annotations

from typing import Any, Optional

from core.sensitivity import DEFAULT_WEIGHT_SETS

DOCUMENTED_COMPOSITE_WEIGHTS: dict[str, float] = dict(
    DEFAULT_WEIGHT_SETS["baseline"]
)

WEIGHTED_DI_MAX = 100.0
WEIGHTED_DV_MAX = 10.0


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

    D_pond = 10 * (w * DI_norm + (1 - w) * DV_norm)
    """
    try:
        if metodo == "min-max":
            DI_norm = DI / DI_max
            DV_norm = DV / DV_max
        elif metodo == "z-score":
            DI_mean, DI_std = 50, 25
            DV_mean, DV_std = 5, 2.5
            DI_norm = (DI - DI_mean) / DI_std if DI_std > 0 else 0
            DV_norm = (DV - DV_mean) / DV_std if DV_std > 0 else 0
        else:
            raise ValueError(f"Invalid method: '{metodo}'. Choose 'min-max' or 'z-score'.")

        return float(10 * (w * DI_norm + (1 - w) * DV_norm))
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
