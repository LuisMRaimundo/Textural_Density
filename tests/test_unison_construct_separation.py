"""
Regression tests: exact unison doublings vs pitch-differentiated simultaneities.

Textural Density separates orchestral mass from vertical pitch structure.
"""

from __future__ import annotations

import pytest

from core.pitch_aggregation import aggregate_events_by_pitch
from core.pipeline import calculate_metrics


def _slice_input(notes: list[str], **kwargs):
    n = len(notes)
    return {
        "notes": notes,
        "dynamics": kwargs.get("dynamics", ["mf"] * n),
        "instruments": kwargs.get("instruments", ["Flauta"] * n),
        "num_instruments": kwargs.get("num_instruments", [1] * n),
        "weight_factor": kwargs.get("weight_factor", 0.5),
    }


class TestCaseAExactUnison:
    """C4, C4, C4, C4"""

    @pytest.fixture
    def result(self):
        resultados, _, _ = calculate_metrics(_slice_input(["C4", "C4", "C4", "C4"]))
        return resultados

    def test_event_and_pitch_counts(self, result):
        agg = result["pitch_aggregation"]
        assert agg["event_count"] == 4
        assert agg["distinct_pitch_count"] == 1
        assert agg["doubling_count"] == 3
        assert agg["interval_pairs_count_distinct"] == 0
        assert agg["pitch_aggregation_applied"] is True
        assert agg["unison_doublings_excluded_from_interval_structure"] is True

    def test_pitch_structural_zeros(self, result):
        assert result["density"]["interval"] == pytest.approx(0.0)
        assert result["density"]["pitch_structure"] == pytest.approx(0.0)
        assert result["density"]["absolute"] == pytest.approx(0.0)
        assert result["spectral_moments"]["spread"]["deviation"] == pytest.approx(0.0)
        assert result["spectral_moments"]["spectral_entropy"] == pytest.approx(0.0)
        sub = result["density_subindices"]["registral"]["raw"]
        assert sub["pitch_span_semitones"] == pytest.approx(0.0)

    def test_sonic_mass_high(self, result):
        assert result["density"]["sonic_mass"] > 0


class TestCaseBChromaticCluster:
    """C4, C#4, D4, E4"""

    @pytest.fixture
    def result(self):
        resultados, _, _ = calculate_metrics(
            _slice_input(["C4", "C#4", "D4", "E4"])
        )
        return resultados

    def test_distinct_pitches(self, result):
        agg = result["pitch_aggregation"]
        assert agg["event_count"] == 4
        assert agg["distinct_pitch_count"] == 4
        assert agg["doubling_count"] == 0
        assert agg["interval_pairs_count_distinct"] == 6

    def test_pitch_structure_positive(self, result):
        assert result["density"]["interval"] > 0
        assert result["density"]["pitch_structure"] > 0
        assert result["spectral_moments"]["spectral_entropy"] > 0


class TestCaseCTertianStructure:
    """C4, E4, G4, C5"""

    @pytest.fixture
    def result(self):
        resultados, _, _ = calculate_metrics(
            _slice_input(["C4", "E4", "G4", "C5"])
        )
        return resultados

    def test_span_and_entropy(self, result):
        agg = result["pitch_aggregation"]
        assert agg["distinct_pitch_count"] == 4
        span = result["density_subindices"]["registral"]["raw"]["pitch_span_semitones"]
        assert span == pytest.approx(12.0)
        assert result["spectral_moments"]["spectral_entropy"] > 0


class TestUnisonVsDifferentiatedComparison:
    def test_unison_not_highest_composite(self):
        unison, _, _ = calculate_metrics(_slice_input(["C4", "C4", "C4", "C4"]))
        chromatic, _, _ = calculate_metrics(_slice_input(["C4", "C#4", "D4", "E4"]))
        tertian, _, _ = calculate_metrics(_slice_input(["C4", "E4", "G4", "C5"]))

        u_total = unison["density"]["total"]
        assert chromatic["density"]["total"] > u_total
        assert tertian["density"]["total"] > u_total
        assert chromatic["density"]["pitch_structure"] > unison["density"]["pitch_structure"]
        assert unison["density"]["pitch_structure"] == pytest.approx(0.0)

    def test_unison_entropy_lower_than_chromatic(self):
        unison, _, _ = calculate_metrics(_slice_input(["C4", "C4", "C4", "C4"]))
        chromatic, _, _ = calculate_metrics(_slice_input(["C4", "C#4", "D4", "E4"]))
        assert chromatic["spectral_moments"]["spectral_entropy"] > unison["spectral_moments"]["spectral_entropy"]


class TestCaseDOneVsDuplicatedPitch:
    def test_mass_increases_doubling_pitch_structure_unchanged(self):
        one, _, _ = calculate_metrics(_slice_input(["C4"]))
        four, _, _ = calculate_metrics(_slice_input(["C4", "C4", "C4", "C4"]))
        ten_players, _, _ = calculate_metrics(_slice_input(["C4"], num_instruments=[10]))

        assert four["density"]["sonic_mass"] >= one["density"]["sonic_mass"]
        assert ten_players["density"]["sonic_mass"] >= one["density"]["sonic_mass"]
        assert ten_players["pitch_aggregation"]["total_player_count"] == 10
        assert ten_players["pitch_aggregation"]["event_count"] == 1
        assert four["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert one["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert four["density"]["pitch_structure"] == pytest.approx(0.0)
        assert one["density"]["pitch_structure"] == pytest.approx(0.0)
        assert ten_players["density"]["pitch_structure"] == pytest.approx(0.0)
        assert four["density"]["interval"] == pytest.approx(0.0)
        assert four["spectral_moments"]["spectral_entropy"] == pytest.approx(0.0)


class TestCaseEMicrotonalDistinction:
    def test_microtonal_pitches_not_collapsed(self):
        notes = ["C4", "C4+25c", "C#4-12c", "E4"]
        agg = aggregate_events_by_pitch(notes)
        assert agg.distinct_pitch_count == 4
        assert agg.interval_pairs_count_distinct == 6

        resultados, _, _ = calculate_metrics(_slice_input(notes))
        assert resultados["pitch_aggregation"]["distinct_pitch_count"] == 4


class TestPitchStructuralInvariance:
    def test_splitting_identical_events_does_not_change_pitch_structure(self):
        base, _, _ = calculate_metrics(_slice_input(["C4", "E4", "G4"]))
        dup, _, _ = calculate_metrics(_slice_input(["C4", "C4", "E4", "G4"]))

        assert dup["density"]["pitch_structure"] == pytest.approx(
            base["density"]["pitch_structure"], rel=1e-6
        )
        assert dup["density"]["interval"] == pytest.approx(base["density"]["interval"], rel=1e-6)
        assert dup["density"]["sonic_mass"] >= base["density"]["sonic_mass"]

    def test_unison_duplication_does_not_increase_interval_compactness(self):
        single, _, _ = calculate_metrics(_slice_input(["C4", "E4"]))
        doubled, _, _ = calculate_metrics(_slice_input(["C4", "C4", "E4"]))

        assert doubled["density"]["interval"] == pytest.approx(single["density"]["interval"])
        assert doubled["pitch_aggregation"]["doubling_count"] == 1
