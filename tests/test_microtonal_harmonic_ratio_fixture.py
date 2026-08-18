"""B1: committed microtonal fixture — 12-EDO snapshots cannot protect this fix."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from microtonal import note_to_midi
from spectral_analysis import calculate_harmonic_ratio

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "microtonal_harmonic_ratio.json"


def _load() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_file_exists():
    assert FIXTURE.is_file()


def test_note_spellings_match_committed_midis():
    spec = _load()
    midis = [float(note_to_midi(n)) for n in spec["notes_if_parsed"]]
    assert midis == pytest.approx(spec["pitches"], abs=1e-9)


def test_microtonal_harmonic_ratio_matches_fixture():
    spec = _load()
    ratio = calculate_harmonic_ratio(spec["pitches"], spec["amplitudes"])
    assert ratio == pytest.approx(spec["expected_harmonic_ratio"], abs=1e-12)


def test_legacy_one_sided_rule_would_fail_this_fixture():
    spec = _load()
    pitches = np.asarray(spec["pitches"], dtype=float)
    amps = np.asarray(spec["amplitudes"], dtype=float)
    intervals = pitches - pitches.min()
    legacy = float(amps[np.isclose(intervals % 12, 0, atol=0.25)].sum() / amps.sum())
    assert legacy == pytest.approx(spec["legacy_one_sided_harmonic_ratio"], abs=1e-12)
    assert legacy != pytest.approx(spec["expected_harmonic_ratio"], abs=1e-12)
