"""Committed pitched CDM ladders must be soft→loud monotone (stress D6 hotfix)."""

from __future__ import annotations

import importlib

import pytest

from config import DYNAMIC_LEVELS
from instrumentos.registry import list_profiles
from microtonal import midi_to_note_name, note_to_midi_strict


def _pitched_modules() -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for p in list_profiles():
        if p.module_name and not p.unpitched and p.module_name not in seen:
            seen.add(p.module_name)
            names.append(p.module_name)
    return names


def _sample_pitches(spectral: dict[str, dict[str, float]], n: int = 3) -> list[str]:
    notes = sorted(spectral.keys(), key=lambda k: note_to_midi_strict(k))
    if len(notes) <= n:
        return notes
    idxs = [0, len(notes) // 2, len(notes) - 1]
    return [notes[i] for i in idxs]


@pytest.mark.parametrize("module_name", _pitched_modules())
def test_pitched_module_cdm_monotone_at_sample_pitches(module_name: str):
    mod = importlib.import_module(f"instrumentos.{module_name}")
    spectral = mod.spectral_data
    assert spectral, f"{module_name}: empty spectral_data"
    levels = tuple(DYNAMIC_LEVELS)
    assert mod.INSTRUMENT_SOURCE.dynamic_levels == levels
    for note in _sample_pitches(spectral, 3):
        row = spectral[note]
        vals = [float(row[d]) for d in levels]
        for soft, loud, d0, d1 in zip(vals, vals[1:], levels, levels[1:]):
            assert soft <= loud + 1e-12, (
                f"{module_name} {note}: {d0}={soft} > {d1}={loud}"
            )


def test_registry_pitched_modules_cover_three_sample_notes():
    """Sanity: sample pitch helper returns MIDI-ordered keys."""
    mod = importlib.import_module("instrumentos.violin")
    samples = _sample_pitches(mod.spectral_data, 3)
    assert len(samples) == 3
    midis = [note_to_midi_strict(n) for n in samples]
    assert midis == sorted(midis)
    # Midpoint sample is a real table key
    assert samples[1] in mod.spectral_data
    assert midi_to_note_name(float(midis[0]))  # import path stays warm
