"""
Validate that sounding pitches lie within each instrument's registry sounding range.
"""

from __future__ import annotations

from core.models import InstrumentEvent, VerticalSlice
from error_handler import InputError
from instrumentos.registry import profile_for_event

_RANGE_EPS = 1e-6


def _midi_in_sounding_range(midi: float, low: float, high: float) -> bool:
    return (low - _RANGE_EPS) <= midi <= (high + _RANGE_EPS)


def _note_label(event: InstrumentEvent) -> str:
    pitch = event.sounding_pitch
    return pitch.spelling or pitch.note_name or f"MIDI {pitch.midi:.2f}"


def validate_event_sounding_range(event: InstrumentEvent, *, index: int | None = None) -> None:
    """
    Raise ``InputError`` when the event's sounding pitch is outside the instrument range.

    Uses ``instrumentos.registry`` ``sounding_range`` (concert pitch, MIDI semitones).
    """
    profile = profile_for_event(event.instrument_name)
    low, high = profile.sounding_range
    midi = float(event.sounding_pitch.midi)
    if _midi_in_sounding_range(midi, low, high):
        return

    note_label = _note_label(event)
    idx_part = f" at event index {index}" if index is not None else ""
    field = "notes" if index is None else f"notes[{index}]"
    raise InputError(
        f"Note {note_label!r} (MIDI {midi:.2g}) is outside the sounding range "
        f"[{low:.0f}, {high:.0f}] for instrument {event.instrument_name!r} "
        f"({profile.display_name}){idx_part}.",
        field=field,
    )


def validate_vertical_slice_pitch_ranges(vertical_slice: VerticalSlice) -> None:
    """Validate every event in a vertical slice against its instrument sounding range."""
    for idx, event in enumerate(vertical_slice.events):
        validate_event_sounding_range(event, index=idx)
