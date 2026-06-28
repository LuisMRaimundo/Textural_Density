"""Tests for violin sordina vs arco diagnostic traceability."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from instrumentos.registry import resolve_profile
from instrumentos.violin_sordina_diagnostics import (
    AUDIT_FLAG_HIGH,
    compare_violin_sordina_to_arco,
    compare_violin_sordina_to_arco_dataframe,
    input_implies_violin_sordina,
)


@pytest.mark.parametrize(
    "alias",
    [
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


def test_compare_detects_sordina_gt_arco_at_a3_pp():
    rows = compare_violin_sordina_to_arco()
    a3_pp = next(row for row in rows if row["note"] == "A3" and row["dynamic"] == "pp")
    assert a3_pp["sordina_gt_arco"] is True
    assert a3_pp["sordina_value"] > a3_pp["arco_value"]
    assert a3_pp["sordina_arco_ratio"] > 1.0
    assert a3_pp["audit_flag"] == AUDIT_FLAG_HIGH
    assert a3_pp["density_relation_to_arco"] == "sordina_gt_arco"


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
    assert densities == pytest.approx([38.949341, 28.582867], rel=0, abs=1e-5)
    assert resultados["density"]["instrument"] == pytest.approx(48.311815, rel=0, abs=1e-4)

    trace = resultados["instrument_lookup_trace"]
    assert len(trace) == 2

    sordina_row = trace[0]
    assert sordina_row["resolved_profile_id"] == "violino_sordina"
    assert sordina_row["module_name"] == "violin_sordina"
    assert sordina_row["one_player_density"] == pytest.approx(38.949341, rel=0, abs=1e-5)
    assert sordina_row["corresponding_arco_density"] == pytest.approx(30.702267, rel=0, abs=1e-5)
    assert sordina_row["sordina_arco_ratio"] > 1.0
    assert sordina_row["density_relation_to_arco"] == "sordina_gt_arco"
    assert sordina_row["audit_flag"] == AUDIT_FLAG_HIGH

    arco_row = trace[1]
    assert arco_row["module_name"] == "violin"
    assert arco_row["corresponding_arco_density"] == pytest.approx(28.582867, rel=0, abs=1e-5)
    assert arco_row["sordina_arco_ratio"] == pytest.approx(1.0)
    assert arco_row["density_relation_to_arco"] == ""


def test_sordina_misresolution_warning():
    request = AnalysisRequest(
        notes=("G4",),
        dynamics=("mf",),
        instruments=("Violin con sordina (typo unresolved)",),
        num_instruments=(1,),
    )
    resultados, _, _ = calculate_metrics(request)
    warnings = resultados["metric_metadata"]["warnings"]
    assert any(
        "Input appears to request violin con sordina" in warning for warning in warnings
    )


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
