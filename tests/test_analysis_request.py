"""Tests for strict AnalysisRequest boundary."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from error_handler import InputError


def _minimal_request(**overrides):
    base = {
        "notes": ("C4", "E4", "G4"),
        "dynamics": ("mf", "mf", "mf"),
        "instruments": ("flauta", "flauta", "flauta"),
        "num_instruments": (1, 1, 1),
        "weight_factor": 0.5,
    }
    base.update(overrides)
    return AnalysisRequest(**base)


class TestAnalysisRequest:
    def test_rejects_unknown_keys(self):
        with pytest.raises(InputError, match="Unknown analytical keys"):
            AnalysisRequest.from_mapping(
                {
                    "notes": ["C4"],
                    "dynamics": ["mf"],
                    "instruments": ["flauta"],
                    "num_instruments": [1],
                    "save_results": True,
                }
            )

    @pytest.mark.parametrize(
        "removed_key",
        [
            "use_stevens",
            "alpha",
            "beta",
            "use_psychoacoustic",
            "use_perceptual_weighting",
            "calculate_combination_tones",
        ],
    )
    def test_rejects_removed_keys(self, removed_key):
        with pytest.raises(InputError):
            AnalysisRequest.from_mapping(
                {
                    "notes": ["C4"],
                    "dynamics": ["mf"],
                    "instruments": ["flauta"],
                    "num_instruments": [1],
                    removed_key: True,
                }
            )

    def test_pipeline_accepts_request(self):
        req = _minimal_request()
        resultados, densidades, pitches = calculate_metrics(req)
        assert len(pitches) == 3
        assert len(densidades) == 3
        assert "density" in resultados

    def test_composite_trace_present(self):
        resultados, _, _ = calculate_metrics(_minimal_request())
        assert "composite_trace" in resultados
        assert "pitch_aggregation" in resultados
        trace = resultados["composite_trace"]
        assert trace["steps"]["pitch_structure_density"]["value"] >= 0
