"""Task 8b/8c: unpitched aggregation contract (counts, texture, unified composite)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from config import MAX_DENS_GLOBAL
from core.formatting import format_output_string
from core.pipeline import calculate_metrics
from core.request import AnalysisRequest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
BASELINE_PATH = FIXTURES / "regression_baseline.json"


def _mixed_four_events() -> AnalysisRequest:
    """Two pitched + two unpitched (expected Event/Player Count 4/4)."""
    return AnalysisRequest(
        notes=("C4", "E4", "C5", "D2"),
        dynamics=("mf", "mf", "fff", "fff"),
        instruments=("Violin", "Violin", "Cymbals", "Bass drum"),
        num_instruments=(1, 1, 1, 1),
    )


def test_mixed_slice_event_and_player_count_include_unpitched():
    r = calculate_metrics(_mixed_four_events())[0]
    agg = r["pitch_aggregation"]
    assert agg["event_count"] == 4
    assert agg["player_count"] == 4
    assert agg["pitched_event_count"] == 2
    assert agg["unpitched_event_count"] == 2
    assert agg["distinct_pitch_count"] == 2
    assert agg["pitch_polyphony"] == 2


def test_mixed_slice_texture_contract():
    r = calculate_metrics(_mixed_four_events())[0]
    tex = r["texture"]
    assert tex["player_count"] == pytest.approx(4.0)
    assert tex["player_weighted_texture_mass"] == pytest.approx(4.0)
    assert tex["texture_polyphony"] == pytest.approx(2.0)
    assert tex["pitch_polyphony"] == pytest.approx(2.0)
    assert tex["average_texture_density"] > 0.0
    assert tex["average_texture_density"] != pytest.approx(4.0)
    expected_avg = float(r["density"]["sonic_mass"]) / 4.0
    assert tex["average_texture_density"] == pytest.approx(expected_avg, rel=1e-9)


def test_mixed_slice_display_mentions_unpitched_exclusion():
    r = calculate_metrics(_mixed_four_events())[0]
    text = format_output_string(r)
    assert "2 unpitched events excluded from pitch metrics by type" in text
    assert "Composite: log10(1 + D_blend*sqrt(M)/REF)" in text
    assert "D_blend=" in text
    assert f"REF={MAX_DENS_GLOBAL:g}" in text


def test_unpitched_only_composite_on_unified_path():
    r = calculate_metrics(
        AnalysisRequest(
            notes=("C2", "D2"),
            dynamics=("fff", "fff"),
            instruments=("Tam-tam", "Bass drum"),
            num_instruments=(1, 1),
        )
    )[0]
    assert r["density"]["pitch_structure"] == pytest.approx(0.0)
    assert r["density"]["total"] > 0.0
    assert r["composite_meta"]["mode"] == "weighted_blend_mass_log"
    text = format_output_string(r)
    assert "fallback" not in text.lower()
    assert "2 unpitched events excluded from pitch metrics by type" in text
    assert "n/a — no pitched content" in text


def test_image1_pitched_only_density_matches_frozen_baseline():
    """Pitched-only regression baseline (re-frozen under unified composite)."""
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    input_data = {
        "notes": ["C4", "E4", "G4", "C5"],
        "dynamics": ["mf", "f", "ff", "mf"],
        "instruments": ["flauta", "clarinete", "flauta", "clarinete"],
        "num_instruments": [1, 2, 1, 1],
        "weight_factor": 0.5,
        "save_results": False,
        "show_graphs": False,
    }
    r = calculate_metrics(input_data)[0]
    for key, expected in baseline["density"].items():
        assert float(r["density"][key]) == pytest.approx(
            float(expected), rel=1e-12, abs=0.0
        ), key
    assert r["pitch_aggregation"]["event_count"] == 4
    assert r["pitch_aggregation"]["player_count"] == 5
    assert r["pitch_aggregation"]["unpitched_event_count"] == 0
    text = format_output_string(r)
    assert "unpitched events excluded" not in text
    assert f"REF={MAX_DENS_GLOBAL:g}" in text
