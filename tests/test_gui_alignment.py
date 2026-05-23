"""
Repository-alignment tests: GUI defaults, core adapter, strict-symbolic mode.
"""

from __future__ import annotations

import pytest

from core import calculate_metrics
from core.defaults import METRIC_SCHEMA_VERSION, RESEARCH_ANALYSIS_DEFAULTS
from error_handler import InputError
from gui.analysis_adapter import calculate_from_gui, normalize_gui_input_data

_REMOVED_COMBO_KEYS = (
    "calculate_combination_tones",
    "combination_tones",
    "resultant_tones",
    "include_resultants",
    "include_combination_tones",
    "virtual_tones",
    "generated_tones",
)


class TestResearchApiDefaults:
    def test_defaults_exclude_combination_tone_keys(self):
        for key in _REMOVED_COMBO_KEYS:
            assert key not in RESEARCH_ANALYSIS_DEFAULTS

    def test_metric_schema_version_strict_symbolic(self):
        assert "strict-symbolic" in METRIC_SCHEMA_VERSION

    def test_calculate_metrics_symbolic_only(self):
        input_data = {
            "notes": ["C4", "E4", "G4"],
            "dynamics": ["mf", "mf", "mf"],
            "instruments": ["flauta", "flauta", "flauta"],
            "num_instruments": [1, 1, 1],
            "weight_factor": 0.5,
        }
        resultados, _, pitches = calculate_metrics(input_data)
        meta = resultados["metric_metadata"]
        assert meta["score_only_mode"] is True
        assert "combination_tones_enabled" not in meta
        assert "combination_tones" not in meta.get("metrics", {})
        assert "combination_tones" not in resultados
        assert len(pitches) == len(input_data["notes"])

    @pytest.mark.parametrize("key", _REMOVED_COMBO_KEYS)
    def test_removed_combination_keys_rejected(self, key):
        input_data = {
            "notes": ["A4", "C5"],
            "dynamics": ["mf", "mf"],
            "instruments": ["flauta", "flauta"],
            "num_instruments": [1, 1],
            "weight_factor": 0.5,
            key: True,
        }
        with pytest.raises(InputError, match="Removed option"):
            calculate_metrics(input_data)


class TestGuiConfigNormalization:
    def test_normalize_gui_input_excludes_removed_keys(self):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
            "calculate_combination_tones": True,
            "include_resultants": True,
        }
        normalized = normalize_gui_input_data(raw)
        pipeline = normalized.to_pipeline_dict()
        for key in _REMOVED_COMBO_KEYS:
            assert key not in pipeline

    def test_gui_default_constant_matches_research_api(self):
        normalized = normalize_gui_input_data(
            {
                "notes": ["C4"],
                "dynamics": ["mf"],
                "instruments": ["flauta"],
                "num_instruments": [1],
            }
        )
        assert normalized.weight_factor == RESEARCH_ANALYSIS_DEFAULTS["weight_factor"]


class TestGuiCoreAdapter:
    def test_calculate_from_gui_includes_metric_metadata(self):
        input_data = {
            "notes": ["C4", "E4", "G4"],
            "dynamics": ["mf", "mf", "mf"],
            "instruments": ["flauta", "flauta", "flauta"],
            "num_instruments": [1, 1, 1],
            "weight_factor": 0.5,
        }
        resultados, densidades, pitches = calculate_from_gui(input_data)
        assert "metric_metadata" in resultados
        assert "density_subindices" in resultados
        assert "combination_tones_enabled" not in resultados["metric_metadata"]
        assert len(densidades) == 3
        assert len(pitches) == 3

    def test_calculate_from_gui_matches_core_when_normalized(self):
        raw = {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "mf"],
            "instruments": ["flauta", "clarinete"],
            "num_instruments": [1, 1],
            "weight_factor": 0.5,
        }
        r_gui, d_gui, p_gui = calculate_from_gui(raw)
        r_core, d_core, p_core = calculate_metrics(normalize_gui_input_data(raw))
        assert r_gui["density"]["total"] == pytest.approx(r_core["density"]["total"])
        assert d_gui == pytest.approx(d_core)
        assert p_gui == pytest.approx(p_core)

    def test_gui_does_not_pass_removed_combo_keys(self):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
            "calculate_combination_tones": True,
        }
        normalized = normalize_gui_input_data(raw)
        assert "calculate_combination_tones" not in normalized.to_pipeline_dict()


class TestStrictSymbolicMetadata:
    def test_no_combination_tone_metadata(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        meta = resultados["metric_metadata"]
        assert "combination_tones_enabled" not in meta
        assert "combination_tones" not in meta.get("metrics", {})


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
