"""
Symbolic orchestration mass — score-derived metadata, not loudness or SPL.

Behaviour-preserving extraction from ``data_processor.calcular_massa_sonora``.
Written dynamics are applied once via instrument module GPR lookups; this module
does not apply a second symbolic dynamic multiplier when one_player densities
already include dynamic dependence.
"""

from __future__ import annotations

from typing import Sequence

from core.quantity_scaling import (
    DYNAMIC_APPLIED_IN_INSTRUMENT_PROFILE,
    DYNAMIC_APPLIED_IN_MASS_FORMULA,
    DYNAMIC_APPLIED_ONCE,
    linear_orchestral_mass,
    validate_quantity,
)

# Legacy symbolic dynamic weights — retained for documentation and non-GPR paths.
# Not applied to sonic mass when instrument modules already encode dynamics.
SYMBOLIC_DYNAMIC_FACTORS: dict[str, float] = {
    "pppp": 0.2,
    "ppp": 0.3,
    "pp": 0.4,
    "p": 0.6,
    "mf": 1.0,
    "f": 1.5,
    "ff": 2.0,
    "fff": 2.5,
    "ffff": 3.0,
}


def compute_orchestration_mass(
    notas: Sequence[str],
    dinamicas: Sequence[str],
    numeros_instrumentos: Sequence[int | float],
    densidades_instrumento: Sequence[float],
) -> float:
    """
    Compute symbolic orchestration mass for a vertical slice.

    Each event contribution = one_player_density × player_count (linear).
    ``one_player_density`` must already include instrument-module dynamic lookup;
    no additional SYMBOLIC_DYNAMIC_FACTORS multiplier is applied.
    """
    del notas, dinamicas  # grouping handled upstream; signature kept for compat
    contributions = [
        (float(densidades_instrumento[i]), numeros_instrumentos[i])
        for i in range(len(densidades_instrumento))
    ]
    return linear_orchestral_mass(contributions)


def compute_orchestration_mass_from_sources(
    one_player_densities: Sequence[float],
    player_counts: Sequence[int | float],
) -> float:
    """Linear mass from aligned per-event one-player densities and Qty."""
    contributions = [
        (float(d), player_counts[i]) for i, d in enumerate(one_player_densities)
    ]
    return linear_orchestral_mass(contributions)


def orchestration_mass_metadata(value: float) -> dict[str, object]:
    """Epistemic metadata for orchestration mass construct output."""
    return {
        "construct_id": "orchestration_mass",
        "value": float(value),
        "raw_value": float(value),
        "source_type": "symbolic_metadata",
        "verification_status": "verified_by_tests",
        "included_in_composite": True,
        "component_weight": None,
        "metric_basis": "player_weighted_power_proxy",
        "interpretation": (
            "Symbolic orchestration mass: sum(qty_i × one_player_density_i). "
            "Linear player-count scaling; not loudness, SPL, or acoustic power."
        ),
        "assumptions": [
            "One-player density includes instrument-module dynamic lookup exactly once.",
            "Incoherent source addition: mass scales linearly with player count.",
        ],
        "warnings": [
            "Written dynamics (p, mf, ff, …) are symbolic score markings, not SPL.",
            "This is a symbolic external-acoustic-metadata proxy, not measured ensemble loudness.",
        ],
        "dynamic_applied_in_instrument_profile": DYNAMIC_APPLIED_IN_INSTRUMENT_PROFILE,
        "dynamic_applied_in_mass_formula": DYNAMIC_APPLIED_IN_MASS_FORMULA,
        "dynamic_applied_once": DYNAMIC_APPLIED_ONCE,
    }
