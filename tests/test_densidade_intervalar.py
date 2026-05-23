"""
Unit tests for densidade_intervalar.py — interval decay, labels, density, config I/O.
"""

import math

import numpy as np
import pytest

import densidade_intervalar as di


class TestModifiedExponentialDecay:
    def test_unison_is_one(self):
        assert di.modified_exponential_decay(0, lamb=0.05) == 1.0

    def test_decay_positive_delta(self):
        lamb = 0.05
        delta = 24.0
        expected = math.exp(-lamb * delta)
        assert di.modified_exponential_decay(delta, lamb=lamb) == pytest.approx(expected)


class TestTranslateTraditionalInterval:
    def test_unison(self):
        assert di.translate_to_traditional_interval(0) == "unison"

    def test_octave_overflow_in_name(self):
        out = di.translate_to_traditional_interval(48)  # 2 full 24-step octaves
        assert "octave" in out


class TestIntervalStringToNumber:
    def test_english_interval_token(self):
        assert di.interval_string_to_number("m3 (interval 6)") == 6

    def test_portuguese_intervalo_token(self):
        assert di.interval_string_to_number("m3 (intervalo 6)") == 6

    def test_no_match_returns_none(self):
        assert di.interval_string_to_number("not an interval") is None


class TestGetIntervals:
    def test_pair_returns_one_string(self):
        out = di.get_intervals(["C4", "E4"])
        assert len(out) == 1
        assert "interval" in out[0]


class TestCalculateIntervalDensity:
    def test_single_note_zero(self):
        assert di.calculate_interval_density(["C4"], lamb=0.05) == 0.0

    def test_triad_positive(self):
        d = di.calculate_interval_density(["C4", "E4", "G4"], lamb=0.05, use_optimization=False)
        assert d > 0.0


class TestCalibratedConfigIO:
    def test_save_load_roundtrip(self, tmp_path, monkeypatch):
        cfg = tmp_path / "density_params.json"
        monkeypatch.setattr(di, "CONFIG_PATH", str(cfg))
        assert di.save_calibrated_parameters({"lambda": 0.42}) is True
        assert di.load_calibrated_parameters() == pytest.approx(0.42)

    def test_get_current_lambda_matches_load(self, tmp_path, monkeypatch):
        cfg = tmp_path / "density_params.json"
        monkeypatch.setattr(di, "CONFIG_PATH", str(cfg))
        di.save_calibrated_parameters({"lambda": 0.33})
        assert di.get_current_lambda() == pytest.approx(0.33)


class TestCalibrateLambdaMapping:
    """Phase 4: calibrate_lambda must map semitone keys to correct dyads."""

    def test_calibrate_lambda_runs_with_reference_data(self, tmp_path, monkeypatch):
        cfg = tmp_path / "density_params.json"
        monkeypatch.setattr(di, "CONFIG_PATH", str(cfg))
        lamb = di.calibrate_lambda({0: 1.0, 2: -0.5, 5: 1.0})
        assert 0.01 <= lamb <= 1.0
        assert di.load_calibrated_parameters() == pytest.approx(lamb)

    def test_consonance_rating_dyads_are_semitone_correct(self):
        from utils.notes import dyad_notes_from_semitone_interval, note_to_midi

        for semitones in di.CONSONANCE_RATINGS:
            base, upper = dyad_notes_from_semitone_interval("C4", int(semitones))
            delta = int(round(note_to_midi(upper) - note_to_midi(base)))
            assert delta == semitones, f"interval {semitones}: got {base}-{upper} ({delta} st)"
