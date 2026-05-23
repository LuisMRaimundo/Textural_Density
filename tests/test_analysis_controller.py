"""Tests for AnalysisController (GUI orchestration without Tkinter)."""

from __future__ import annotations

import pytest

from gui.controllers.analysis_controller import AnalysisController


class TestAnalysisController:
    def test_analyze_matches_build_request_path(self):
        raw = {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "mf"],
            "instruments": ["flauta", "clarinete"],
            "num_instruments": [1, 1],
            "weight_factor": 0.5,
        }
        request = AnalysisController.build_request(raw)
        resultados, densidades, pitches = AnalysisController.analyze(raw)
        assert request.notes == ("C4", "E4")
        assert "density" in resultados
        assert len(densidades) == 2
        assert len(pitches) == 2

    def test_format_results_non_empty(self):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
        }
        resultados, _, _ = AnalysisController.analyze(raw)
        text = AnalysisController.format_results(resultados)
        assert isinstance(text, str)
        assert len(text.strip()) > 0

    def test_strips_gui_only_keys_from_request(self):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
            "save_results": True,
            "show_graphs": False,
        }
        request = AnalysisController.build_request(raw)
        pipeline = request.to_pipeline_dict()
        assert "save_results" not in pipeline
        assert "show_graphs" not in pipeline
