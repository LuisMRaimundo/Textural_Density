"""Tests for violin sordina vs arco diagnostic traceability."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile
from instrumentos.violin_sordina_diagnostics import (
    compare_violin_sordina_to_arco,
    compare_violin_sordina_to_arco_dataframe,
    input_implies_violin_sordina,
)


def test_sordina_appears_in_gui_instrument_list():
    assert "vl_con_sord" in INSTRUMENTS


@pytest.mark.parametrize(
    "alias",
    [
        "vl_con_sord",
        "Violin sordina",
        "violin_sordina",
        "Violin con sordina",
        "violin con sordina",
        "violino con sordina",
        "muted violin",
    ],
)
def test_sordina_aliases_resolve_to_violino_sordina(alias: str):
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == "violino_sordina"
    assert profile.module_name == "violin_sordina"


@pytest.mark.parametrize(
    "label,expected",
    [
        ("Violin con sordina", True),
        ("violin muted", True),
        ("Violin", False),
        ("Viola", False),
    ],
)
def test_input_implies_violin_sordina(label: str, expected: bool):
    assert input_implies_violin_sordina(label) is expected


def test_compare_detects_sordina_lt_arco_at_asharp4_pp():
    """Mute attenuation still holds at A#4 pp after dest-Zenodo arco refresh."""
    rows = compare_violin_sordina_to_arco()
    a_sharp4_pp = next(
        row for row in rows if row["note"] == "A#4" and row["dynamic"] == "pp"
    )
    assert a_sharp4_pp["sordina_gt_arco"] is False
    assert a_sharp4_pp["sordina_value"] < a_sharp4_pp["arco_value"]
    assert a_sharp4_pp["sordina_arco_ratio"] < 1.0
    assert a_sharp4_pp["audit_flag"] is None
    assert a_sharp4_pp["density_relation_to_arco"] == "sordina_lt_arco"


def test_compare_dataframe_has_expected_columns():
    frame = compare_violin_sordina_to_arco_dataframe()
    assert not frame.empty
    for column in (
        "note",
        "dynamic",
        "arco_value",
        "sordina_value",
        "sordina_arco_ratio",
        "sordina_gt_arco",
        "audit_flag",
    ):
        assert column in frame.columns


def test_lookup_trace_does_not_change_calculation_results():
    request = AnalysisRequest(
        notes=("A3", "G4"),
        dynamics=("pp", "mf"),
        instruments=("Violin sordina", "Violin"),
        num_instruments=(1, 1),
    )

    resultados, densities, _ = calculate_metrics(request)
    assert densities == pytest.approx([30.232629, 32.461862], rel=0, abs=1e-5)
    assert resultados["density"]["instrument"] == pytest.approx(
        (30.232629 ** 2 + 32.461862 ** 2) ** 0.5, rel=0, abs=1e-4
    )

    trace = resultados["instrument_lookup_trace"]
    assert len(trace) == 2

    sordina_row = trace[0]
    assert sordina_row["resolved_profile_id"] == "violino_sordina"
    assert sordina_row["module_name"] == "violin_sordina"
    assert sordina_row["one_player_density"] == pytest.approx(30.232629, rel=0, abs=1e-5)
    assert sordina_row["corresponding_arco_density"] == pytest.approx(21.976319, rel=0, abs=1e-5)
    assert sordina_row["sordina_arco_ratio"] > 1.0
    assert sordina_row["density_relation_to_arco"] == "sordina_gt_arco"
    assert sordina_row["audit_flag"] == "sordina_gt_arco_high"

    arco_row = trace[1]
    assert arco_row["module_name"] == "violin"
    assert arco_row["corresponding_arco_density"] == pytest.approx(32.461862, rel=0, abs=1e-5)
    assert arco_row["sordina_arco_ratio"] == pytest.approx(1.0)
    assert arco_row["density_relation_to_arco"] == ""


def test_sordina_misresolution_is_rejected():
    from error_handler import InputError

    request = AnalysisRequest(
        notes=("G4",),
        dynamics=("mf",),
        instruments=("Violin con sordina (typo unresolved)",),
        num_instruments=(1,),
    )
    with pytest.raises(InputError, match="Accepted registry ids"):
        calculate_metrics(request)


def test_composite_trace_includes_lookup_trace():
    request = AnalysisRequest(
        notes=("A3",),
        dynamics=("pp",),
        instruments=("Violin sordina",),
        num_instruments=(1,),
    )
    resultados, _, _ = calculate_metrics(request)
    trace = resultados["composite_trace"]["inputs"]["instrument_lookup_trace"]
    assert len(trace) == 1
    assert trace[0]["note"] == "A3"
    assert trace[0]["dynamic"] == "pp"
