"""
Per-event orchestration density from instrument modules.

Instrument modules interpolate **externally sourced acoustic amplitude tables**
(sparse note×dynamic GPR profiles). The analysis pipeline does not ingest audio;
it applies pre-loaded acoustic metadata to notated pitch and dynamic markings.

Quantity scaling (player count) is applied at the source-aggregation layer via
``core.quantity_scaling`` and ``core.source_aggregation`` — not inside per-event
density lookup.
"""

from __future__ import annotations

import logging
from typing import Callable, Protocol, Sequence

from config import DYNAMIC_LEVELS
from core.models import InstrumentEvent, VerticalSlice
from core.quantity_scaling import validate_quantity
from core.source_aggregation import (
    AggregatedSource,
    aggregate_event_sources,
    compute_orchestral_metrics_from_sources,
)

logger = logging.getLogger("core.orchestration")


class InstrumentModule(Protocol):
    def calcular_densidade(self, note: str, dynamic: str) -> float: ...

    def predict_intermediate_dynamics(
        self,
        notes: list[str],
        pp: list[float],
        mf: list[float],
        ff: list[float],
    ) -> dict[str, list[float]]: ...


def _normalize_dynamic(dynamic: str | None, known_dynamics: tuple[str, ...]) -> str:
    dyn = (dynamic or "mf").strip().lower()
    return dyn if dyn in known_dynamics else "mf"


def compute_event_one_player_density(
    event: InstrumentEvent,
    load_instrument_module: Callable[[str], InstrumentModule],
    known_dynamics: tuple[str, ...] | None = None,
) -> float:
    """
    Single-player instrument density for one notated event.

    Includes exactly one dynamic treatment via the instrument module lookup.
    Does **not** scale by player count (Qty).
    """
    known = known_dynamics or tuple(DYNAMIC_LEVELS) if DYNAMIC_LEVELS else ("pp", "mf", "ff")
    module = load_instrument_module(event.instrument_id)
    note = event.sounding_pitch.note_name
    if not note:
        raise ValueError(f"Event {event.event_id} has no note_name on sounding_pitch")

    dyn_norm = _normalize_dynamic(event.dynamic, known)
    if dyn_norm in ("pp", "mf", "ff"):
        density = module.calcular_densidade(note, dyn_norm)
    else:
        pp = module.calcular_densidade(note, "pp")
        mf = module.calcular_densidade(note, "mf")
        ff = module.calcular_densidade(note, "ff")
        density = module.predict_intermediate_dynamics([note], [pp], [mf], [ff])[
            dyn_norm
        ][0]

    return float(density)


def compute_event_instrument_density(
    event: InstrumentEvent,
    load_instrument_module: Callable[[str], InstrumentModule],
    known_dynamics: tuple[str, ...] | None = None,
) -> float:
    """
    Alias for ``compute_event_one_player_density`` (no Qty scaling).

    Legacy callers expected sqrt(player_count) here; that compounding was removed.
    """
    return compute_event_one_player_density(event, load_instrument_module, known_dynamics)


def compute_one_player_densities_for_slice(
    vertical_slice: VerticalSlice,
    load_instrument_module: Callable[[str], InstrumentModule],
    known_dynamics: tuple[str, ...] | None = None,
) -> list[float]:
    """Per-event one-player densities aligned with slice.events order."""
    return [
        compute_event_one_player_density(event, load_instrument_module, known_dynamics)
        for event in vertical_slice.events
    ]


def compute_instrument_densities_for_slice(
    vertical_slice: VerticalSlice,
    load_instrument_module: Callable[[str], InstrumentModule],
    known_dynamics: tuple[str, ...] | None = None,
) -> list[float]:
    """Backward-compatible alias — returns one-player densities (no Qty factor)."""
    return compute_one_player_densities_for_slice(
        vertical_slice, load_instrument_module, known_dynamics
    )


def compute_total_instrument_density(densities: Sequence[float]) -> float:
    """
    Deprecated sum helper.

    Prefer ``compute_slice_orchestral_metrics`` for RSS pressure-equivalent density.
    """
    return float(sum(densities))


def compute_slice_orchestral_metrics(
    notas: Sequence[str],
    dinamicas: Sequence[str],
    instrumentos: Sequence[str],
    player_counts: Sequence[int | float],
    one_player_densities: Sequence[float],
    known_dynamics: tuple[str, ...] | None = None,
) -> tuple[float, float, tuple[AggregatedSource, ...]]:
    """
    Pressure-equivalent instrument density and sonic mass for a vertical slice.

    Returns (instrument_density_pressure_equiv, sonic_mass, aggregated_sources).
    """
    known = known_dynamics or tuple(DYNAMIC_LEVELS) if DYNAMIC_LEVELS else ("pp", "mf", "ff")

    def norm_dyn(d: str) -> str:
        return _normalize_dynamic(d, known)

    sources = aggregate_event_sources(
        notas,
        dinamicas,
        instrumentos,
        player_counts,
        one_player_densities,
        normalize_dynamic=norm_dyn,
    )
    pressure, mass = compute_orchestral_metrics_from_sources(sources)
    return pressure, mass, sources


def total_player_count(player_counts: Sequence[int | float]) -> int:
    """Sum of validated Qty values across events."""
    return int(sum(validate_quantity(q) for q in player_counts))
