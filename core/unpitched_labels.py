"""Shared display labels for unpitched aggregation notes."""

from __future__ import annotations


def format_unpitched_exclusion_note(unpitched_event_count: int) -> str:
    """
    Singular/plural exclusion line for Numerical Results / reports / logs.

    Examples:
      1 unpitched event excluded from pitch metrics by type (...)
      2 unpitched events excluded from pitch metrics by type (...)
    """
    n = int(unpitched_event_count)
    noun = "event" if n == 1 else "events"
    return (
        f"{n} unpitched {noun} excluded from pitch metrics by type "
        "(see ORCHESTRAL MASS / TEXTURE)"
    )
