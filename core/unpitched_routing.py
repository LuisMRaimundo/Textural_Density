"""
Unpitched instrument routing — entry helpers and pitch-structure exclusion.

Entry paths (GUI / MusicXML / MIDI) must emit the same representation:
``unpitched=True`` on the event plus a canonical placeholder lookup key.
Pitch-structure exclusion remains here in ``partition_pitched_events`` — do
not duplicate that filter in the GUI or loaders.
"""

from __future__ import annotations

from typing import Sequence

from error_handler import InputError
from instrumentos.registry import resolve_profile
from microtonal import extract_cents_float, midi_to_note_name

# GUI dropdown separator (non-selectable).
UNPITCHED_INSTRUMENT_GROUP_LABEL = "── Unpitched percussion ──"

# MIDI channel 10 is 0-based index 9 in mido / the MIDI spec.
GM_PERCUSSION_CHANNEL = 9

# GM drum-kit key → (registry display name or id, approximation note for logs).
# Unlisted keys on channel 10 are skipped with a warning (never pitched fallback).
GM_PERCUSSION_KEY_MAP: dict[int, tuple[str, str | None]] = {
    35: ("Bass drum", None),
    36: ("Bass drum", None),
    49: ("Cymbals", None),  # Crash Cymbal 1
    57: ("Cymbals", None),  # Crash Cymbal 2
    51: ("Cymbals", "ride cymbal approximated as Cymbals module"),
    59: ("Cymbals", "ride cymbal approximated as Cymbals module"),
    52: ("Cymbals", "Chinese cymbal approximated as Cymbals module"),
}

_QUARTER_TONE_MARKERS = ("\u2193", "\u2191", "↓", "↑")


def instrument_is_unpitched(instrument_name: str) -> bool:
    """True when the resolved registry profile is flagged unpitched."""
    profile = resolve_profile(instrument_name)
    return bool(profile is not None and getattr(profile, "unpitched", False))


def canonical_unpitched_note(instrument_name: str) -> str:
    """
    Chromatic placeholder at the integer midpoint of registry ``sounding_range``.

    Lookup convention only — no acoustic meaning. Raises ``InputError`` if the
    name does not resolve to an unpitched profile.
    """
    profile = resolve_profile(instrument_name)
    if profile is None or not getattr(profile, "unpitched", False):
        raise InputError(
            f"Instrument '{instrument_name}' is not a registered unpitched profile; "
            "cannot build a canonical placeholder key.",
            field="instruments",
        )
    lo, hi = profile.sounding_range
    mid = int((int(lo) + int(hi)) // 2)
    return midi_to_note_name(float(mid))


def note_has_microtonal_deviation(note: str) -> bool:
    """True when ``note`` carries cents suffix or quarter-tone spelling markers."""
    if not note:
        return False
    _base, cents = extract_cents_float(str(note))
    if abs(float(cents)) > 0.0:
        return True
    return any(marker in str(note) for marker in _QUARTER_TONE_MARKERS)


def reject_unpitched_microtones(instrument_name: str, note: str) -> None:
    """Raise ``InputError`` if an unpitched instrument carries cents/microtones."""
    if not instrument_is_unpitched(instrument_name):
        return
    if note_has_microtonal_deviation(note):
        raise InputError(
            f"Unpitched instrument '{instrument_name}' does not accept "
            f"cents or microtonal spellings (got {note!r}). "
            "Use dynamic and quantity only; the lookup key is assigned internally.",
            field="notes",
        )


def normalize_unpitched_entry_note(instrument_name: str, note: str) -> str:
    """
    For unpitched instruments: reject microtones, then return the canonical key.

    Pitched instruments: return ``note`` unchanged.
    """
    if not instrument_is_unpitched(instrument_name):
        return note
    reject_unpitched_microtones(instrument_name, note)
    return canonical_unpitched_note(instrument_name)


def map_gm_percussion_key(midi_key: int) -> tuple[str, str | None] | None:
    """
    Map a GM channel-10 key number to (instrument_name, approximation_note).

    Returns ``None`` when the key has no supported mapping (caller must skip).
    """
    return GM_PERCUSSION_KEY_MAP.get(int(midi_key))


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
