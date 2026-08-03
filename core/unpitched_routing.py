"""
Exclude unpitched instruments from pitch-structure aggregation.

Unpitched events still contribute to orchestration mass and per-instrument
CDM lookup; their nominal note keys must not enter distinct pitch bins,
interval compactness, registral span, or pitch-structure density.
"""

from __future__ import annotations

from typing import Sequence

from instrumentos.registry import resolve_profile


def instrument_is_unpitched(instrument_name: str) -> bool:
    """True when the resolved registry profile is flagged unpitched."""
    profile = resolve_profile(instrument_name)
    return bool(profile is not None and getattr(profile, "unpitched", False))


def partition_pitched_events(
    notas: Sequence[str],
    *,
    weights: Sequence[float],
    player_counts: Sequence[int],
    dynamics: Sequence[str],
    instruments: Sequence[str],
) -> tuple[
    list[str],
    list[float],
    list[int],
    list[str],
    list[str],
    list[str],
]:
    """
    Split simultaneous events into pitched-only lists for pitch aggregation.

    Returns
    -------
    pitched_notas, pitched_weights, pitched_players, pitched_dynamics,
    pitched_instruments, warnings
        ``warnings`` lists one message per unpitched event that would otherwise
        have entered a pitch bin via its nominal note key.
    """
    pitched_notas: list[str] = []
    pitched_weights: list[float] = []
    pitched_players: list[int] = []
    pitched_dynamics: list[str] = []
    pitched_instruments: list[str] = []
    warnings: list[str] = []

    n = len(notas)
    for i in range(n):
        note = notas[i] if i < len(notas) else ""
        inst = str(instruments[i]) if i < len(instruments) else ""
        dyn = str(dynamics[i]) if i < len(dynamics) else "mf"
        w = float(weights[i]) if i < len(weights) else 1.0
        pc = int(player_counts[i]) if i < len(player_counts) else 1
        if not note:
            continue
        if instrument_is_unpitched(inst):
            warnings.append(
                f"Unpitched instrument '{inst}' note key '{note}' excluded from "
                "pitch-structure bins (interval compactness, registral span, "
                "distinct pitch count); retained for orchestration mass and "
                "instrument CDM lookup only."
            )
            continue
        pitched_notas.append(note)
        pitched_weights.append(w)
        pitched_players.append(pc)
        pitched_dynamics.append(dyn)
        pitched_instruments.append(inst)

    return (
        pitched_notas,
        pitched_weights,
        pitched_players,
        pitched_dynamics,
        pitched_instruments,
        warnings,
    )
