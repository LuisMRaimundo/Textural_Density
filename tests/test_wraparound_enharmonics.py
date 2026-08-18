"""Wrap-around enharmonics (Cb↔B, B#↔C) use the strict parser on the analysis path."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from microtonal import note_to_midi_strict, parse_pitch_strict


def _slice(notes: list[str], instrument: str = "flauta") -> dict:
    n = len(notes)
    return {
        "notes": notes,
        "dynamics": ["mf"] * n,
        "instruments": [instrument] * n,
        "num_instruments": [1] * n,
    }


WRAP_PAIRS = [
    ("Cb4", "B3"),
    ("Cb5", "B4"),
    ("B#3", "C4"),
    ("B#4", "C5"),
]


@pytest.mark.parametrize("written,canonical", WRAP_PAIRS)
def test_strict_parser_wraps_octave(written: str, canonical: str):
    assert parse_pitch_strict(written).midi == pytest.approx(parse_pitch_strict(canonical).midi)
    assert note_to_midi_strict(written) == pytest.approx(note_to_midi_strict(canonical))


@pytest.mark.parametrize("written,canonical", WRAP_PAIRS)
def test_pipeline_density_matches_canonical_spelling(written: str, canonical: str):
    """Cb/B# totals follow the wrapped MIDI cell; default 12-EDO spellings are unchanged."""
    a, _, pa = calculate_metrics(_slice([written, "G4"]))
    b, _, pb = calculate_metrics(_slice([canonical, "G4"]))
    assert pa == pytest.approx(pb)
    for key in a["density"]:
        assert a["density"][key] == pytest.approx(b["density"][key]), key


def test_cb5_and_b4_collapse_to_one_bin():
    r, _, pitches = calculate_metrics(_slice(["B4", "Cb5"]))
    assert r["pitch_aggregation"]["distinct_pitch_count"] == 1
    assert pitches[0] == pytest.approx(71.0)
    assert pitches[1] == pytest.approx(71.0)
