"""Wrap-around enharmonics (Cb↔B, B#↔C) use the strict parser on the analysis path."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from core.reporting import _top_interval_pairs
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


GOLDEN_NOTES = ["C4", "E4", "G4", "C5"]
# Wrap-around spellings only (octave-crossing Cb/B#). E4 and G4 have none.
GOLDEN_WRAP_SUBSTITUTIONS = {"C4": "B#3", "C5": "B#4"}


def _golden_input(notes: list[str]) -> dict:
    return {
        "notes": notes,
        "dynamics": ["mf", "f", "ff", "mf"],
        "instruments": ["flauta", "clarinete", "flauta", "clarinete"],
        "num_instruments": [1, 2, 1, 1],
        "weight_factor": 0.5,
    }


def test_golden_baseline_wrap_spellings_match_plain_totals():
    """Every wrap-around spelling in the golden slice equals its plain equivalent.

    Stronger than the 12-EDO golden fixture, which contains no Cb/B# spellings.
    """
    baseline, _, _ = calculate_metrics(_golden_input(GOLDEN_NOTES))
    expected = baseline["density"]

    for idx, plain in enumerate(GOLDEN_NOTES):
        wrap = GOLDEN_WRAP_SUBSTITUTIONS.get(plain)
        if wrap is None:
            continue
        notes = list(GOLDEN_NOTES)
        notes[idx] = wrap
        got, _, _ = calculate_metrics(_golden_input(notes))
        for key, val in expected.items():
            assert got["density"][key] == pytest.approx(float(val), rel=1e-5, abs=1e-6), (
                f"{plain}->{wrap} {key}"
            )

    combined = [GOLDEN_WRAP_SUBSTITUTIONS.get(n, n) for n in GOLDEN_NOTES]
    got, _, _ = calculate_metrics(_golden_input(combined))
    for key, val in expected.items():
        assert got["density"][key] == pytest.approx(float(val), rel=1e-5, abs=1e-6), key


def test_report_interval_labels_use_strict_wrap():
    """Report-string interval labels use the same wrap as aggregation (not analysis)."""
    pairs = _top_interval_pairs(["Cb5", "B4"], top_n=1)
    assert pairs
    n1, n2, weight = pairs[0]
    assert {n1, n2} == {"Cb5", "B4"}
    assert weight == pytest.approx(1.0, abs=1e-6)
