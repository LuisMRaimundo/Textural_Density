"""Tests for core export_constants and composite sensitivity."""

from __future__ import annotations

import pytest

from core.export_constants import export_constants_and_assumptions
from core.sensitivity import (
    DEFAULT_WEIGHT_SETS,
    analyze_composite_weight_sensitivity,
    analyze_composite_weight_sensitivity_from_subindices,
)
from data_processor import calculate_metrics


class TestExportConstants:
    def test_export_runs(self):
        data = export_constants_and_assumptions()
        assert "MAX_DENS_GLOBAL" in data["normalization"]
        assert "calculate_combination_tones" not in data["research_defaults"]

    def test_docs_file_exists(self):
        from pathlib import Path

        p = Path(__file__).resolve().parents[1] / "docs" / "constants_and_assumptions.md"
        assert p.is_file()


class TestCompositeSensitivity:
    @pytest.fixture
    def subindices(self):
        data = {
            "notes": ["C4", "E4", "G4"],
            "dynamics": ["mf", "mf", "mf"],
            "instruments": ["flauta", "flauta", "flauta"],
            "num_instruments": [1, 1, 1],
        }
        return calculate_metrics(data)[0]["density_subindices"]

    def test_deterministic(self, subindices):
        a = analyze_composite_weight_sensitivity_from_subindices(subindices)
        b = analyze_composite_weight_sensitivity_from_subindices(subindices)
        assert a.baseline_composite == pytest.approx(b.baseline_composite)
        assert len(a.alternatives) == len(b.alternatives)

    def test_all_weight_sets_recorded(self, subindices):
        result = analyze_composite_weight_sensitivity_from_subindices(subindices)
        assert set(result.weight_sets_used.keys()) == set(DEFAULT_WEIGHT_SETS.keys())

    def test_deltas_computed(self, subindices):
        result = analyze_composite_weight_sensitivity_from_subindices(subindices)
        assert result.alternatives
        for alt in result.alternatives:
            assert "delta_from_baseline" in alt
            assert "diagnostic_composite" in alt

    def test_missing_subindices_warns(self):
        result = analyze_composite_weight_sensitivity({"density_subindices": {}})
        assert result.warnings

    def test_default_composite_unchanged_by_sensitivity_helper(self):
        data = {
            "notes": ["C4", "E4", "G4"],
            "dynamics": ["mf", "mf", "mf"],
            "instruments": ["flauta", "flauta", "flauta"],
            "num_instruments": [1, 1, 1],
        }
        before, _, _ = calculate_metrics(data)
        analyze_composite_weight_sensitivity(before)
        after, _, _ = calculate_metrics(data)
        assert float(before["density"]["total"]) == pytest.approx(float(after["density"]["total"]))
