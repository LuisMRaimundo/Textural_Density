"""
Phase 5: vertical-density subindices tests.
"""

from __future__ import annotations

import numpy as np
import pytest

from core.converters import legacy_input_to_vertical_slice, analysis_config_from_input
from core.subindices import SubindexContext, build_density_subindices
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


class TestSubindicesIntegration:
    def test_calculate_metrics_includes_density_subindices(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        assert "density_subindices" in resultados

    def test_required_subindex_keys(self, baseline_input_data):
        sub = calculate_metrics(baseline_input_data)[0]["density_subindices"]
        for key in (
            "event_count",
            "interval_compactness",
            "registral",
            "orchestral_mass",
            "timbral_heterogeneity",
            "harmonicity_proxy",
            "temporal",
            "composite",
        ):
            assert key in sub

    def test_composite_matches_legacy_total(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        sub = resultados["density_subindices"]
        assert float(sub["composite"]["value"]) == pytest.approx(
            float(resultados["density"]["total"]), rel=1e-9
        )

    def test_composite_components_documented(self, baseline_input_data):
        components = calculate_metrics(baseline_input_data)[0]["density_subindices"]["composite"]["components"]
        for key in (
            "pitch_structure_density",
            "dynamic_boost",
            "normalization_divisor",
        ):
            assert key in components

    def test_interval_compactness_not_dissonance_label(self, baseline_input_data):
        ic = calculate_metrics(baseline_input_data)[0]["density_subindices"]["interval_compactness"]
        assert "distinct" in ic["interpretation"].lower()

    def test_orchestral_mass_dynamic_warning(self, baseline_input_data):
        om = calculate_metrics(baseline_input_data)[0]["density_subindices"]["orchestral_mass"]
        assert any("spl" in w.lower() or "ordinal" in w.lower() for w in om["warnings"])

    def test_timbral_heterogeneity_is_symbolic_metadata(self, baseline_input_data):
        th = calculate_metrics(baseline_input_data)[0]["density_subindices"]["timbral_heterogeneity"]
        assert th["source_type"] == "symbolic_metadata"

    def test_no_combination_tone_subindex(self, baseline_input_data):
        sub = calculate_metrics(baseline_input_data)[0]["density_subindices"]
        assert "combination_tone_candidates" not in sub

    def test_scalar_density_unchanged_with_subindices(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        d = resultados["density"]
        assert float(d["interval"]) > 0
        assert float(d["total"]) > 0


class TestSubindexProperties:
    def test_event_count_increases_with_more_notes(self, baseline_input_data):
        r1, _, _ = calculate_metrics(baseline_input_data)
        data2 = dict(baseline_input_data)
        data2["notes"] = baseline_input_data["notes"] + ["D4"]
        data2["dynamics"] = baseline_input_data["dynamics"] + ["mf"]
        data2["instruments"] = baseline_input_data["instruments"] + ["flauta"]
        data2["num_instruments"] = baseline_input_data["num_instruments"] + [1]
        r2, _, _ = calculate_metrics(data2)
        c1 = r1["density_subindices"]["event_count"]["raw"]["event_count"]
        c2 = r2["density_subindices"]["event_count"]["raw"]["event_count"]
        assert c2 == c1 + 1

    def test_player_weighted_mass_increases_with_doubling(self, baseline_input_data):
        data = dict(baseline_input_data)
        data["num_instruments"] = [2, 2, 2, 2]
        sub = calculate_metrics(data)[0]["density_subindices"]
        base = calculate_metrics(baseline_input_data)[0]["density_subindices"]
        assert (
            sub["event_count"]["raw"]["player_weighted_count"]
            > base["event_count"]["raw"]["player_weighted_count"]
        )

    def test_temporal_unavailable_without_metadata(self, baseline_input_data):
        temporal = calculate_metrics(baseline_input_data)[0]["density_subindices"]["temporal"]
        assert temporal["raw"]["available"] is False
        assert temporal["warnings"]


class TestBuildDensitySubindicesUnit:
    def test_registral_pitch_span(self, baseline_input_data):
        vertical_slice = legacy_input_to_vertical_slice(baseline_input_data)
        config = analysis_config_from_input(baseline_input_data)
        ctx = SubindexContext(
            vertical_slice=vertical_slice,
            config=config,
            interval_compactness_raw=0.2,
            interval_compactness_reported=0.15,
            pitch_span_semitones=12.0,
            sonic_mass=5.0,
            harmonic_ratio=0.3,
            chroma_vector=np.ones(12) / 12,
            texture={},
            timbre={"timbre_diversity": 2, "timbre_balance": 0.5},
            orchestration={"register_balance": 0.6, "orchestration_evenness": 0.7},
            refined_density=0.05,
            total_density=0.1,
            total_density_pre_log=0.12,
            cohesion_factor=0.8,
            complexity_factor=1.1,
            dynamic_boost=2.0,
        )
        sub = build_density_subindices(ctx)
        assert sub["registral"]["raw"]["pitch_span_semitones"] == pytest.approx(12.0)
        assert sum(sub["registral"]["raw"]["register_band_occupancy"].values()) == pytest.approx(1.0)
