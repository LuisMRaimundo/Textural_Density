"""Input-order 85% weight-quantile: numbers preserved, labels clarified."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from microtonal import midi_to_hz
from spectral_analysis import calculate_extended_spectral_moments


def _quantile_hz(pitches, amps):
    result = calculate_extended_spectral_moments(pitches, amps)
    return result


class TestNumericPreservation:
    def test_alias_matches_canonical(self):
        result = _quantile_hz([60.0, 64.0, 67.0, 72.0], [1.0, 1.5, 1.2, 1.8])
        assert result["input_order_weight_quantile_hz"] == result["spectral_rolloff"]

    def test_reviewed_order_sensitive_sequences(self):
        farbass = [60.0, 62.0, 64.0, 65.0, 70.0, 28.0]
        contrasting = [84.0, 36.0]
        equal6 = [1.0] * 6
        equal2 = [1.0, 1.0]
        assert _quantile_hz(farbass, equal6)["spectral_rolloff"] == pytest.approx(
            midi_to_hz(28.0)
        )
        assert _quantile_hz(contrasting, equal2)["spectral_rolloff"] == pytest.approx(
            midi_to_hz(36.0)
        )

    def test_reordering_changes_statistic(self):
        ascending = _quantile_hz([48.0, 60.0, 72.0], [1.0, 1.0, 1.0])
        descending = _quantile_hz([72.0, 60.0, 48.0], [1.0, 1.0, 1.0])
        assert ascending["spectral_rolloff"] != pytest.approx(descending["spectral_rolloff"])
        assert descending["input_order_weight_quantile_hz"] == pytest.approx(
            midi_to_hz(48.0)
        )


class TestDensityTotalUnaffected:
    def test_composite_unchanged_when_notes_reordered_for_quantile_only(self):
        # Same distinct pitches and instruments: density.total must match.
        low_first = calculate_metrics(
            {
                "notes": ["C4", "E4", "G4"],
                "dynamics": ["mf", "mf", "mf"],
                "instruments": ["flauta", "flauta", "flauta"],
                "num_instruments": [1, 1, 1],
            }
        )[0]
        high_first = calculate_metrics(
            {
                "notes": ["G4", "E4", "C4"],
                "dynamics": ["mf", "mf", "mf"],
                "instruments": ["flauta", "flauta", "flauta"],
                "num_instruments": [1, 1, 1],
            }
        )[0]
        assert low_first["density"]["total"] == pytest.approx(high_first["density"]["total"])
        assert low_first["spectral_moments"]["spectral_rolloff"] != pytest.approx(
            high_first["spectral_moments"]["spectral_rolloff"]
        )
        assert (
            low_first["spectral_moments"]["input_order_weight_quantile_hz"]
            == low_first["spectral_moments"]["spectral_rolloff"]
        )
