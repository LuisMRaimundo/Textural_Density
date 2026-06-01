"""
Aggregate symbolic events by source identity for quantity/mass invariance.

One row with Qty = N and N identical rows with Qty = 1 must yield the same
player count, pressure-equivalent instrument density, and sonic mass.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from core.quantity_scaling import (
    linear_orchestral_mass,
    rss_pressure_equivalent,
    validate_quantity,
)
from microtonal import note_to_midi


@dataclass(frozen=True)
class AggregatedSource:
    """One incoherent source group after row-splitting merge."""

    midi: float
    instrument: str
    dynamic: str
    one_player_density: float
    player_count: float

    def to_dict(self) -> dict[str, object]:
        return {
            "midi": float(self.midi),
            "instrument": self.instrument,
            "dynamic": self.dynamic,
            "one_player_density": float(self.one_player_density),
            "player_count": float(self.player_count),
        }


def _source_key(
    note: str,
    instrument: str,
    dynamic: str,
    *,
    normalize_dynamic: Callable[[str], str],
) -> tuple[float, str, str]:
    midi = float(note_to_midi(note))
    inst = str(instrument).strip().lower()
    dyn = normalize_dynamic(dynamic)
    return midi, inst, dyn


def aggregate_event_sources(
    notas: Sequence[str],
    dinamicas: Sequence[str],
    instrumentos: Sequence[str],
    player_counts: Sequence[int | float],
    one_player_densities: Sequence[float],
    *,
    normalize_dynamic: Callable[[str], str],
) -> tuple[AggregatedSource, ...]:
    """
    Merge events sharing (MIDI pitch, instrument, dynamic) into source groups.

    Player counts sum within each group; one_player_density must be identical
    for events in the same group (same pitch/instrument/dynamic lookup).
    """
    groups: dict[tuple[float, str, str], dict[str, float]] = {}

    for i, note in enumerate(notas):
        if not note:
            continue
        key = _source_key(
            note,
            instrumentos[i] if i < len(instrumentos) else "flauta",
            dinamicas[i] if i < len(dinamicas) else "mf",
            normalize_dynamic=normalize_dynamic,
        )
        density = float(one_player_densities[i]) if i < len(one_player_densities) else 0.0
        qty = validate_quantity(
            player_counts[i] if i < len(player_counts) else 1
        )

        if key not in groups:
            groups[key] = {
                "one_player_density": density,
                "player_count": qty,
            }
        else:
            entry = groups[key]
            entry["player_count"] = float(entry["player_count"]) + qty
            existing = float(entry["one_player_density"])
            if abs(existing - density) > 1e-9:
                raise ValueError(
                    f"Inconsistent one_player_density for source {key}: "
                    f"{existing} vs {density}"
                )

    return tuple(
        AggregatedSource(
            midi=key[0],
            instrument=key[1],
            dynamic=key[2],
            one_player_density=float(entry["one_player_density"]),
            player_count=float(entry["player_count"]),
        )
        for key, entry in sorted(groups.items())
    )


def compute_orchestral_metrics_from_sources(
    sources: Sequence[AggregatedSource],
) -> tuple[float, float]:
    """
    Return (pressure_equivalent_instrument_density, sonic_mass).

    Pressure-equivalent: sqrt(sum(qty_i * base_i^2))
    Mass: sum(qty_i * base_i)
    """
    if not sources:
        return 0.0, 0.0
    contributions = [(s.one_player_density, s.player_count) for s in sources]
    pressure = rss_pressure_equivalent(contributions)
    mass = linear_orchestral_mass(contributions)
    return float(pressure), float(mass)
