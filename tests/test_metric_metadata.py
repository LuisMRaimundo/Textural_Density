"""
Phase 3: metric metadata and epistemic labelling tests.
"""

from __future__ import annotations

import pytest

from core.metrics_metadata import (
    MetricAssemblyContext,
    attach_metric_metadata,
    build_metric_metadata,
    collect_slice_warnings,
    metric_result_to_dict,
)
from core.converters import analysis_config_from_input, legacy_input_to_vertical_slice
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


class TestMetricMetadataIntegration:
    def test_calculate_metrics_includes_metric_metadata(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        assert "metric_metadata" in resultados

    def test_metric_metadata_structure(self, baseline_input_data):
        meta = calculate_metrics(baseline_input_data)[0]["metric_metadata"]
        assert "metrics" in meta
        assert "combination_tones_enabled" not in meta
        assert "warnings" in meta
        assert "assumptions" in meta
        assert "normalization" in meta
        assert isinstance(meta["warnings"], list)
        assert isinstance(meta["assumptions"], list)

    def test_scalar_values_unchanged_with_metadata(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        meta = resultados["metric_metadata"]["metrics"]
        d = resultados["density"]
        assert float(meta["density.interval"]["value"]) == pytest.approx(float(d["interval"]))
        assert float(meta["density.instrument"]["value"]) == pytest.approx(float(d["instrument"]))
        assert float(meta["density.weighted"]["value"]) == pytest.approx(float(d["weighted"]))
        assert float(meta["density.refined"]["value"]) == pytest.approx(float(d["refined"]))
        assert float(meta["density.total"]["value"]) == pytest.approx(float(d["total"]))

    def test_interval_score_derived(self, baseline_input_data):
        meta = calculate_metrics(baseline_input_data)[0]["metric_metadata"]["metrics"]
        interval = meta["density.interval"]
        assert interval["source_type"] == "score_derived"
        assert float(interval["raw_value"]) >= float(interval["value"])

    def test_weighted_density_linear_blend_documented(self, baseline_input_data):
        meta = calculate_metrics(baseline_input_data)[0]["metric_metadata"]["metrics"]
        weighted = meta["density.weighted"]
        assert any("linear" in a.lower() for a in weighted["assumptions"])

    def test_total_density_pre_log_captured(self, baseline_input_data):
        meta = calculate_metrics(baseline_input_data)[0]["metric_metadata"]["metrics"]
        total = meta["density.total"]
        assert "raw_value" in total
        assert float(total["raw_value"]) >= float(total["value"])

    def test_no_combination_tone_metadata(self, baseline_input_data):
        meta = calculate_metrics(baseline_input_data)[0]["metric_metadata"]["metrics"]
        assert "combination_tones" not in meta

    def test_score_only_metadata_by_default(self):
        resultados, _, _ = calculate_metrics(
            {
                "notes": ["C4", "E4"],
                "dynamics": ["mf", "mf"],
                "instruments": ["flauta", "flauta"],
                "num_instruments": [1, 1],
            }
        )
        meta = resultados["metric_metadata"]
        assert meta["score_only_mode"] is True
        assert "use_psychoacoustic" not in meta

    def test_instrument_density_uses_external_acoustic_metadata(self, baseline_input_data):
        meta = calculate_metrics(baseline_input_data)[0]["metric_metadata"]["metrics"]
        inst = meta["density.instrument"]
        assert inst["source_type"] == "external_acoustic_metadata"
        assert any("externally sourced" in a.lower() for a in inst["assumptions"])

    def test_normalization_constants_documented(self, baseline_input_data):
        norm = calculate_metrics(baseline_input_data)[0]["metric_metadata"]["normalization"]
        assert "MAX_DENS_GLOBAL" in norm
        assert "USE_LOG_COMPRESSION" in norm
        assert "WEIGHTED_DI_MAX" in norm
        assert "WEIGHTED_DV_MAX" in norm


class TestMetricMetadataHelpers:
    def test_metric_result_to_dict_serializes(self):
        from core.models import MetricResult

        result = MetricResult(
            name="test.metric",
            value=1.23,
            raw_value=2.34,
            source_type="score_derived",
            validation_status="verified_only",
            confidence="high",
            interpretation="Test metric.",
        )
        payload = metric_result_to_dict(result)
        assert payload["name"] == "test.metric"
        assert payload["value"] == 1.23
        assert payload["raw_value"] == 2.34
        assert payload["source_type"] == "score_derived"

    def test_collect_slice_warnings_unknown_dynamic(self):
        vertical_slice = legacy_input_to_vertical_slice(
            {
                "notes": ["C4", "E4"],
                "dynamics": ["xyz_loud", "mf"],
                "instruments": ["flauta", "flauta"],
                "num_instruments": [1, 1],
            }
        )
        config = analysis_config_from_input({})
        warnings, assumptions = collect_slice_warnings(vertical_slice, config)
        assert any("Unknown dynamic" in w for w in warnings)
        assert any("score/information input only" in a for a in assumptions)
