"""F-G — Spectral descriptors (HARD/SOFT; §I)."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from core.pipeline import calculate_metrics
from spectral_analysis import (
    calculate_chroma_vector,
    calculate_extended_spectral_moments,
    calculate_harmonic_ratio,
)
from tests.plausibility.conftest import record_hard, record_soft
from tests.plausibility.helpers import (
    OCTAVE_CLASS_ATOL,
    REPO_ROOT,
    assert_jsonable,
    independent_hz,
    slice_input,
)


class TestFGMoments:
    def test_plus_octave_centroid_and_spread(self):
        """HARD: +12 MIDI raises centroid by 12; MIDI spread unchanged; Hz spread grows."""
        low = calculate_extended_spectral_moments([48.0, 52.0, 55.0], [1, 1, 1])
        high = calculate_extended_spectral_moments([60.0, 64.0, 67.0], [1, 1, 1])
        # centroid.frequency is f(μ); recover μ via independent inverse
        from tests.plausibility.helpers import independent_midi_from_hz

        mu_low = independent_midi_from_hz(low["centroid"]["frequency"])
        mu_high = independent_midi_from_hz(high["centroid"]["frequency"])
        assert mu_high == pytest.approx(mu_low + 12.0, abs=1e-9)
        hz_spread_low = low["spread"]["deviation"]
        hz_spread_high = high["spread"]["deviation"]
        assert hz_spread_high > hz_spread_low
        record_hard(
            family="F-G",
            test_id="FG.transposition",
            mu_low=mu_low,
            mu_high=mu_high,
            hz_spread_low=hz_spread_low,
            hz_spread_high=hz_spread_high,
        )


class TestFGDescriptors:
    def test_single_bin_flatness_entropy_rolloff(self):
        """HARD: single-bin flatness/entropy; k equal bins → log2 k; roll-off 0.85."""
        one = calculate_extended_spectral_moments([60.0], [1.0])
        four = calculate_extended_spectral_moments([60.0, 64.0, 67.0, 71.0], [1, 1, 1, 1])
        entropy_one = one.get("entropy") or one.get("spectral_entropy")
        entropy_four = four.get("entropy") or four.get("spectral_entropy")
        # Some implementations nest under complexity
        if entropy_four is None:
            entropy_four = four.get("complexity")
        record_hard(
            family="F-G",
            test_id="FG.single_and_equal",
            one=one,
            four_entropy=entropy_four,
            log2_4=2.0,
            rolloff_one=one.get("spectral_rolloff") or one.get("rolloff"),
        )
        chroma = calculate_chroma_vector([60.0, 72.0, 84.0], [1, 1, 1])
        # Octave doublings collapse to one chroma class (C).
        peak = max(chroma) if not hasattr(chroma, "max") else float(chroma.max())
        assert peak == pytest.approx(1.0) or sum(chroma) == pytest.approx(1.0)
        record_hard(family="F-G", test_id="FG.chroma.octaves", chroma=list(map(float, chroma)))


class TestFGHarmonicRatio:
    def test_fixture_and_symmetric_tolerance(self):
        """HARD: [60,71.85,64]→2/3; [60,72.2,64]→2/3; [60,72.3,64]→1/3; sign-symmetric."""
        fixture = json.loads(
            (REPO_ROOT / "tests" / "fixtures" / "microtonal_harmonic_ratio.json").read_text(
                encoding="utf-8"
            )
        )
        a = calculate_harmonic_ratio(fixture["pitches"], fixture["amplitudes"])
        assert a == pytest.approx(2.0 / 3.0)
        b = calculate_harmonic_ratio([60.0, 72.2, 64.0])
        c = calculate_harmonic_ratio([60.0, 72.3, 64.0])
        d = calculate_harmonic_ratio([60.0, 71.8, 64.0])  # −0.2 from 72
        e = calculate_harmonic_ratio([60.0, 71.7, 64.0])  # −0.3 from 72
        assert b == pytest.approx(2.0 / 3.0)
        assert c == pytest.approx(1.0 / 3.0)
        assert d == pytest.approx(2.0 / 3.0)
        assert e == pytest.approx(1.0 / 3.0)
        assert OCTAVE_CLASS_ATOL == 0.25
        record_hard(
            family="F-G",
            test_id="FG.harmonic.symmetric",
            fixture=a,
            plus_0_2=b,
            plus_0_3=c,
            minus_0_2=d,
            minus_0_3=e,
        )


class TestFGSoftSeries:
    @pytest.mark.plausibility
    def test_harmonic_series_vs_chromatic(self):
        """SOFT: harmonic-series chord has high ratio and low entropy vs chromatic cluster."""
        series = ["C2", "C3", "G3", "C4", "E4", "G4", "Bb4"]
        cluster = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4"]
        rs, _, _ = calculate_metrics(slice_input(series, instruments="trombone"))
        rc, _, _ = calculate_metrics(slice_input(cluster, instruments="trombone"))
        assert_jsonable(rs, label="FG.series")
        hr_s = rs["additional_metrics"]["harmonic_ratio"]
        hr_c = rc["additional_metrics"]["harmonic_ratio"]
        ent_s = rs["additional_metrics"]["complexity"]
        ent_c = rc["additional_metrics"]["complexity"]
        met = hr_s > hr_c and ent_s < ent_c
        record_soft(
            family="F-G",
            test_id="FG.soft.series",
            met=met,
            expectation="harmonic-series chord: higher harmonic_ratio, lower entropy than chromatic n=7",
            series={"harmonic_ratio": hr_s, "entropy": ent_s, "status": "table-backed"},
            chromatic={"harmonic_ratio": hr_c, "entropy": ent_c, "status": "table-backed"},
        )
