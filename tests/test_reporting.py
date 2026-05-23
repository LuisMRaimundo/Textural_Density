"""
Phase 9: reporting and interpretability tests.
"""

from __future__ import annotations

import pytest

from core.reporting import (
    explain_vertical_slice,
    format_interpretability_report,
    format_sensitivity_report,
    run_sensitivity_analysis,
)
from data_processor import calculate_metrics


@pytest.fixture
def baseline_input_data():
    return {
        "notes": ["C4", "E4", "G4", "C5"],
        "dynamics": ["mf", "f", "ff", "mf"],
        "instruments": ["flauta", "clarinete", "flauta", "clarinete"],
        "num_instruments": [1, 2, 1, 1],
        "weight_factor": 0.5,
        "save_results": False,
        "show_graphs": False,
    }


class TestExplainVerticalSlice:
    def test_returns_non_empty_string(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        text = explain_vertical_slice(resultados)
        assert isinstance(text, str)
        assert len(text) > 200

    def test_mentions_composite_and_limitations(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        text = explain_vertical_slice(resultados).lower()
        assert "composite" in text or "total" in text
        assert "limitation" in text
        assert "score" in text or "audio" in text

    def test_mentions_interval_pairs(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        text = explain_vertical_slice(resultados)
        assert "C4" in text and "E4" in text

    def test_mentions_instruments(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        text = explain_vertical_slice(resultados).lower()
        assert "flauta" in text or "clarinete" in text

    def test_no_combination_tone_language(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        text = explain_vertical_slice(resultados).lower()
        assert "combination tone" not in text
        assert "tartini" not in text


class TestInterpretabilityReport:
    def test_includes_legacy_and_metadata(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        report = format_interpretability_report(resultados)
        assert "DENSITY" in report
        assert "METRIC METADATA" in report
        assert "SUBINDICES" in report
        assert "INTERPRETATION" in report


class TestSensitivityAnalysis:
    def test_sensitivity_runs(self, baseline_input_data):
        sens = run_sensitivity_analysis(baseline_input_data)
        assert "baseline_total_density" in sens
        assert len(sens["variations"]) >= 4
        assert "not empirical validation" in sens["disclaimer"].lower()

    def test_sensitivity_variations_change_or_document(self, baseline_input_data):
        sens = run_sensitivity_analysis(baseline_input_data)
        params = {v["parameter"] for v in sens["variations"]}
        assert "weight_factor" in params
        assert "calculate_combination_tones" not in params

    def test_format_sensitivity_report(self, baseline_input_data):
        sens = run_sensitivity_analysis(baseline_input_data)
        text = format_sensitivity_report(sens)
        assert "SENSITIVITY" in text
        assert "Baseline" in text

    def test_scalar_baseline_unchanged(self, baseline_input_data):
        r1, _, _ = calculate_metrics(baseline_input_data)
        run_sensitivity_analysis(baseline_input_data)
        r2, _, _ = calculate_metrics(baseline_input_data)
        assert float(r1["density"]["total"]) == pytest.approx(float(r2["density"]["total"]))
