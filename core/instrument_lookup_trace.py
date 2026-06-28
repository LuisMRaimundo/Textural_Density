"""Per-event instrument density lookup trace (diagnostic, read-only)."""

from __future__ import annotations

from typing import Any, Sequence

from config import DYNAMIC_LEVELS
from core.models import VerticalSlice
from instrumentos.violin_sordina_diagnostics import build_event_lookup_trace_row


def build_instrument_lookup_trace(
    vertical_slice: VerticalSlice,
    one_player_densities: Sequence[float],
    known_dynamics: tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    """
    Build per-event lookup diagnostics aligned with ``vertical_slice.events``.

    Uses densities already computed by the pipeline; does not alter them.
    """
    known = known_dynamics or tuple(DYNAMIC_LEVELS) if DYNAMIC_LEVELS else ("pp", "mf", "ff")
    trace: list[dict[str, Any]] = []
    for index, event in enumerate(vertical_slice.events):
        density = float(one_player_densities[index]) if index < len(one_player_densities) else 0.0
        trace.append(
            build_event_lookup_trace_row(
                event=event,
                one_player_density=density,
                known_dynamics=known,
            )
        )
    return trace
