"""Table MIDI coverage vs registry sounding range (pitched modules)."""

from __future__ import annotations

import importlib
from functools import lru_cache
from typing import Any

from instrumentos.registry import resolve_profile
from microtonal import note_to_midi_strict


@lru_cache(maxsize=64)
def module_table_midi_span(module_name: str) -> tuple[int, int] | None:
    """Return (min_midi, max_midi) of spectral_data keys, or None."""
    try:
        mod = importlib.import_module(f"instrumentos.{module_name}")
    except ImportError:
        return None
    table = getattr(mod, "spectral_data", None)
    if not table:
        return None
    midis = [int(note_to_midi_strict(k)) for k in table]
    return min(midis), max(midis)


def table_excludes_sounding_range(
    sounding_lo: int,
    sounding_hi: int,
    table_span: tuple[int, int] | None,
    *,
    unpitched: bool = False,
) -> dict[str, Any]:
    """
    Compare registry sounding range to committed table span.

    Unpitched modules are pitch-independent — exclusion is not applicable.
    """
    if unpitched:
        return {
            "table_excludes_sounding_range": False,
            "exclusion_kind": "not_applicable_unpitched",
            "missing_low_semitones": 0,
            "missing_high_semitones": 0,
            "table_span_midi": None,
        }
    if table_span is None:
        return {
            "table_excludes_sounding_range": True,
            "exclusion_kind": "no_table",
            "missing_low_semitones": None,
            "missing_high_semitones": None,
            "table_span_midi": None,
        }
    t_lo, t_hi = table_span
    miss_lo = max(0, t_lo - int(sounding_lo))
    miss_hi = max(0, int(sounding_hi) - t_hi)
    excludes = miss_lo > 0 or miss_hi > 0
    return {
        "table_excludes_sounding_range": excludes,
        "exclusion_kind": "partial_table" if excludes else "full_coverage",
        "missing_low_semitones": miss_lo,
        "missing_high_semitones": miss_hi,
        "table_span_midi": [t_lo, t_hi],
    }


def pitch_outside_table_but_in_sounding_range(
    instrument_name: str,
    note: str,
) -> str | None:
    """
    Return a labelled warning when denslookup will extrapolate/fallback
    because the note is inside registry sounding_range but outside the table.
    """
    profile = resolve_profile(instrument_name)
    if profile is None or not profile.module_name or profile.unpitched:
        return None
    span = module_table_midi_span(profile.module_name)
    if span is None:
        return (
            f"LABELLED_TABLE_FALLBACK: instrument {instrument_name!r} has no "
            f"committed spectral_data table for note {note!r}; density uses "
            f"coarse/fallback path (never silent)."
        )
    try:
        midi = float(note_to_midi_strict(note))
    except Exception:
        return None
    lo, hi = profile.sounding_range
    t_lo, t_hi = span
    if not (lo - 1e-6 <= midi <= hi + 1e-6):
        return None  # registry validation owns OOR sounding notes
    if t_lo - 1e-6 <= midi <= t_hi + 1e-6:
        return None
    return (
        f"LABELLED_TABLE_FALLBACK: note {note!r} (MIDI {midi:.2g}) is inside "
        f"sounding range [{lo:.0f},{hi:.0f}] for {instrument_name!r} but outside "
        f"committed table span [{t_lo},{t_hi}]; density uses labelled "
        f"pitch-extrapolation / fallback (never silent)."
    )
