"""Unpitched instruments must not enter pitch-structure metrics."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from instrumentos.registry import resolve_profile

_UNPITCHED = (
    ("Bass drum", "bombo", "bass_drum"),
    ("Cymbals", "pratos", "cymbals"),
    ("Tam-tam", "tamtam", "tamtam"),
    ("Gong", "gongo", "gong"),
)


@pytest.mark.parametrize("display,iid,module", _UNPITCHED)
def test_registry_and_module_flag_unpitched(display, iid, module):
    profile = resolve_profile(display)
    assert profile is not None
    assert profile.instrument_id == iid
    assert profile.unpitched is True
    assert profile.module_name == module
    mod = __import__(f"instrumentos.{module}", fromlist=["INSTRUMENT_SOURCE"])
    assert mod.INSTRUMENT_SOURCE.unpitched is True


def test_violin_plus_cymbal_same_note_pitch_metrics_match_violin_alone():
    violin_only = calculate_metrics(
        AnalysisRequest(
            notes=("C4",),
            dynamics=("mf",),
            instruments=("Violin",),
            num_instruments=(1,),
        )
    )[0]
    both = calculate_metrics(
        AnalysisRequest(
            notes=("C4", "C4"),
            dynamics=("mf", "mf"),
            instruments=("Violin", "Cymbals"),
            num_instruments=(1, 1),
        )
    )[0]

    v_agg = violin_only["pitch_aggregation"]
    b_agg = both["pitch_aggregation"]
    assert b_agg["distinct_pitch_count"] == v_agg["distinct_pitch_count"] == 1
    assert b_agg["interval_pairs_count_distinct"] == 0
    assert both["density"]["interval"] == pytest.approx(violin_only["density"]["interval"])
    assert both["density"]["pitch_structure"] == pytest.approx(
        violin_only["density"]["pitch_structure"]
    )
    assert both["density"]["sonic_mass"] > violin_only["density"]["sonic_mass"]
    assert both["density"]["instrument"] > violin_only["density"]["instrument"]

    warnings = both["metric_metadata"]["warnings"]
    joined = " ".join(str(w) for w in warnings)
    assert "Unpitched instrument" in joined
    assert "Cymbals" in joined


def test_tamtam_does_not_change_registral_span():
    violin = calculate_metrics(
        AnalysisRequest(
            notes=("C4", "G4"),
            dynamics=("mf", "mf"),
            instruments=("Violin", "Violin"),
            num_instruments=(1, 1),
        )
    )[0]
    with_tt = calculate_metrics(
        AnalysisRequest(
            notes=("C4", "G4", "C1"),
            dynamics=("mf", "mf", "mf"),
            instruments=("Violin", "Violin", "Tam-tam"),
            num_instruments=(1, 1, 1),
        )
    )[0]
    assert with_tt["composite_trace"]["inputs"]["registral_span"] == pytest.approx(
        violin["composite_trace"]["inputs"]["registral_span"]
    )
    assert with_tt["composite_trace"]["inputs"]["registral_span"] == pytest.approx(7.0)
