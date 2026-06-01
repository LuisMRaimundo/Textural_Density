"""
Explicit quantity (Qty / player-count) scaling semantics.

Textural Density treats Qty as the number of players assigned to a symbolic event.
Mass-like quantities scale linearly; pressure-equivalent quantities use
root-sum-square incoherent source addition. Qty does not create pitch structure.
"""

from __future__ import annotations

import math
from typing import Sequence

# Metadata constants (also surfaced in metric_metadata.quantity_scaling)
QUANTITY_SCALING_MODEL = "incoherent_source_addition"
POWER_OR_MASS_GAIN = "qty"
PRESSURE_EQUIVALENT_GAIN = "sqrt(sum(qty_i * base_i^2))"
COHERENT_PHASE_LOCKED_ADDITION_ASSUMED = False

QUANTITY_POWER_GAIN_FORMULA = "qty"
QUANTITY_PRESSURE_GAIN_FORMULA = "sqrt(sum(qty_i * base_i^2))"

DYNAMIC_APPLIED_IN_INSTRUMENT_PROFILE = True
DYNAMIC_APPLIED_IN_MASS_FORMULA = False
DYNAMIC_APPLIED_ONCE = True

QTY_AFFECTS_PITCH_STRUCTURE = False
QTY_AFFECTS_ORCHESTRAL_MASS = True
QTY_AFFECTS_PRESSURE_EQUIVALENT_INSTRUMENT_DENSITY = True


def validate_quantity(qty: int | float) -> float:
    """Require qty >= 1; reject zero, negative, NaN, or non-finite values."""
    if not isinstance(qty, (int, float)):
        raise TypeError(f"quantity must be numeric, got {type(qty)!r}")
    value = float(qty)
    if not math.isfinite(value):
        raise ValueError(f"quantity must be finite, got {qty!r}")
    if value < 1.0:
        raise ValueError(f"quantity must be >= 1, got {qty!r}")
    return value


def quantity_power_gain(qty: int | float) -> float:
    """Linear player-count gain for mass-like quantities."""
    return validate_quantity(qty)


def quantity_pressure_gain(qty: int | float) -> float:
    """Per-source pressure-equivalent gain for identical incoherent sources."""
    return math.sqrt(validate_quantity(qty))


def rss_pressure_equivalent(
    contributions: Sequence[tuple[float, int | float]],
) -> float:
    """
    Root-sum-square pressure equivalent across sources.

    Each contribution is (one_player_density, qty).
    Returns sqrt(sum(qty_i * base_i^2)).
    """
    total = 0.0
    for base_density, qty in contributions:
        q = validate_quantity(qty)
        b = float(base_density)
        total += q * b * b
    return math.sqrt(total)


def linear_orchestral_mass(
    contributions: Sequence[tuple[float, int | float]],
) -> float:
    """Sum of qty_i * one_player_density_i (mass-like, linear in player count)."""
    return sum(float(base) * validate_quantity(qty) for base, qty in contributions)


def quantity_scaling_metadata(*, player_count: int) -> dict[str, object]:
    """Shared quantity-scaling metadata block for results."""
    return {
        "quantity_scaling_model": QUANTITY_SCALING_MODEL,
        "quantity_power_gain_formula": QUANTITY_POWER_GAIN_FORMULA,
        "quantity_pressure_gain_formula": QUANTITY_PRESSURE_GAIN_FORMULA,
        "coherent_phase_locked_addition_assumed": COHERENT_PHASE_LOCKED_ADDITION_ASSUMED,
        "player_count": int(player_count),
        "qty_affects_pitch_structure": QTY_AFFECTS_PITCH_STRUCTURE,
        "qty_affects_orchestral_mass": QTY_AFFECTS_ORCHESTRAL_MASS,
        "qty_affects_pressure_equivalent_instrument_density": (
            QTY_AFFECTS_PRESSURE_EQUIVALENT_INSTRUMENT_DENSITY
        ),
        "dynamic_applied_in_instrument_profile": DYNAMIC_APPLIED_IN_INSTRUMENT_PROFILE,
        "dynamic_applied_in_mass_formula": DYNAMIC_APPLIED_IN_MASS_FORMULA,
        "dynamic_applied_once": DYNAMIC_APPLIED_ONCE,
    }
