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


def _note_label(pitch) -> str:
    return pitch.spelling or pitch.note_name or f"MIDI {pitch.midi:.2f}"


def validate_event_sounding_range(event: InstrumentEvent, *, index: int | None = None) -> None:
    """
    Raise ``InputError`` when the event's concert/sounding pitch is outside range.

    Uses ``instrumentos.registry`` ``sounding_range`` (concert-pitch MIDI semitones).
    Manual legacy input and the GUI supply **sounding/concert** pitch directly.
    MusicXML written ``<pitch>`` is converted via ``<transpose>`` before validation
    (see ``xml_loader``). ``registry.transposition`` is notation metadata only and is
    not applied to manual input.
    """
    profile = profile_for_event(event.instrument_name)
    low, high = profile.sounding_range
    midi = float(event.sounding_pitch.midi)
    if _midi_in_sounding_range(midi, low, high):
        return

    sounding_label = _note_label(event.sounding_pitch)
    written_clause = ""
    if event.written_pitch is not None:
        w_midi = float(event.written_pitch.midi)
        if abs(w_midi - midi) > _RANGE_EPS:
            written_label = _note_label(event.written_pitch)
            written_clause = (
                f"; written {written_label!r} (MIDI {w_midi:.2g})"
            )

    idx_part = f" at event index {index}" if index is not None else ""
    field = "notes" if index is None else f"notes[{index}]"
    if event.written_pitch is not None:
        guidance = "MusicXML written pitch was transposed to sounding pitch for validation."
    else:
        guidance = "Enter sounding/concert pitch (manual and GUI input are not transposed)."
    raise InputError(
        f"Note {sounding_label!r} (sounding MIDI {midi:.2g}) is outside the range "
        f"[{low:.0f}, {high:.0f}] for instrument {event.instrument_name!r} "
        f"({profile.display_name}){written_clause}{idx_part}. "
        f"{guidance}",
        field=field,
    )


def validate_vertical_slice_pitch_ranges(vertical_slice: VerticalSlice) -> None:
    """Validate every event in a vertical slice against its instrument sounding range."""
    for idx, event in enumerate(vertical_slice.events):
        validate_event_sounding_range(event, index=idx)
