"""
Event density construct — score-derived simultaneous event counts.

Low-risk core-native extraction (Phase: score-only upgrade).
"""

from __future__ import annotations

from typing import Any, Optional

from core.models import VerticalSlice
from core.temporal import resolve_event_duration


def compute_event_density(vertical_slice: VerticalSlice) -> dict[str, Any]:
    """
    Compute event-density metrics from a symbolic vertical slice.

    Returns raw counts suitable for construct-level validation against
    expert score annotations (event_density dimension).
    """
    events = vertical_slice.events
    player_counts = [max(1, int(ev.player_count)) for ev in events]
    event_count = len(events)
    player_weighted_count = float(sum(player_counts))

    durations: list[float] = []
    for ev in events:
        dur = resolve_event_duration(ev)
        if dur is not None and dur > 0:
            durations.append(float(dur))

    duration_weighted_count: Optional[float] = None
    if durations and len(durations) == event_count:
        duration_weighted_count = float(
            sum(pc * d for pc, d in zip(player_counts, durations))
        )

    return {
        "event_count": event_count,
        "player_weighted_count": player_weighted_count,
        "duration_weighted_count": duration_weighted_count,
        "source_type": "score_derived",
        "validation_status": "verified_only",
        "interpretation": (
            "Number of simultaneously active symbolic events; "
            "player-weighted count includes doublings."
        ),
    }
