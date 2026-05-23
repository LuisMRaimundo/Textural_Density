"""
Tests for score-only global defaults and report metadata.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.defaults import (
    METRIC_SCHEMA_VERSION,
    RESEARCH_ANALYSIS_DEFAULTS,
    apply_research_defaults,
)
from core.models import AnalysisConfig
from core.reporting import explain_score_slice
from data_processor import calculate_metrics
from error_handler import InputError
from gui.analysis_adapter import normalize_gui_input_data
from midi_loader import _default_midi_options
from xml_loader import _settings_to_options

MINIMAL_INPUT = {
    "notes": ["C4", "E4", "G4"],
    "dynamics": ["mf", "mf", "mf"],
    "instruments": ["flauta", "flauta", "flauta"],
    "num_instruments": [1, 1, 1],
}

_REMOVED_COMBO_KEYS = (
    "calculate_combination_tones",
    "combination_tones",
    "resultant_tones",
    "include_resultants",
    "include_combination_tones",
    "virtual_tones",
    "generated_tones",
)


class TestScoreOnlyDefaults:
    def test_research_defaults_constants(self):
        assert "strict-symbolic" in METRIC_SCHEMA_VERSION
        assert "use_psychoacoustic" not in RESEARCH_ANALYSIS_DEFAULTS
        assert "use_stevens" not in RESEARCH_ANALYSIS_DEFAULTS
        for key in _REMOVED_COMBO_KEYS:
            assert key not in RESEARCH_ANALYSIS_DEFAULTS

    def test_analysis_config_defaults(self):
        cfg = AnalysisConfig()
        assert cfg.weight_factor == 0.5
        assert not hasattr(cfg, "calculate_combination_tones")
        assert not hasattr(cfg, "use_psychoacoustic")

    def test_apply_research_defaults_fills_missing(self):
        merged = apply_research_defaults({"notes": ["C4"]})
        assert merged["weight_factor"] == 0.5
        assert "use_psychoacoustic" not in merged
        for key in _REMOVED_COMBO_KEYS:
            assert key not in merged

    def test_api_default_config_score_only(self):
        resultados, _, _ = calculate_metrics(dict(MINIMAL_INPUT))
        meta = resultados["metric_metadata"]
        assert meta["score_only_mode"] is True
        assert "combination_tones_enabled" not in meta
        assert "use_psychoacoustic" not in meta
        assert meta["validation_status"] == "verified_only"
        assert "config_hash" in meta
        assert "input_hash" in meta
        assert "metric_schema_version" in meta

    def test_gui_normalize_strips_removed_keys(self):
        gui = normalize_gui_input_data(
            {
                "notes": ["C4"],
                "dynamics": ["mf"],
                "instruments": ["flauta"],
                "num_instruments": [1],
                "use_stevens": True,
                "use_psychoacoustic": True,
                "calculate_combination_tones": True,
            }
        )
        pipeline = gui.to_pipeline_dict()
        assert "use_stevens" not in pipeline
        assert "use_psychoacoustic" not in pipeline
        assert "calculate_combination_tones" not in pipeline

    def test_midi_loader_defaults(self):
        opts = _default_midi_options()
        assert "use_psychoacoustic" not in opts
        for key in _REMOVED_COMBO_KEYS:
            assert key not in opts

    def test_xml_settings_defaults(self):
        opts = _settings_to_options(None)
        assert "use_psychoacoustic" not in opts
        for key in _REMOVED_COMBO_KEYS:
            assert key not in opts

    def test_removed_analytical_keys_rejected(self):
        with pytest.raises(InputError, match="use_psychoacoustic"):
            calculate_metrics({**MINIMAL_INPUT, "use_psychoacoustic": True})
        with pytest.raises(InputError, match="calculate_combination_tones"):
            calculate_metrics({**MINIMAL_INPUT, "calculate_combination_tones": True})

    def test_explain_score_slice_no_perception_language(self):
        resultados, _, _ = calculate_metrics(dict(MINIMAL_INPUT))
        text = explain_score_slice(resultados)
        assert "score_only_mode" in text or "score-only" in text.lower()
        assert "No audio waveform" in text
        lowered = text.lower()
        assert "use_psychoacoustic" not in lowered
        assert "combination tone" not in lowered
        assert "tartini" not in lowered


class TestReplicationConfig:
    def test_score_only_config_file(self):
        path = Path(__file__).resolve().parents[1] / "replication" / "configs" / "score_only_default.json"
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
        assert "use_psychoacoustic" not in cfg
        for key in _REMOVED_COMBO_KEYS:
            assert key not in cfg
