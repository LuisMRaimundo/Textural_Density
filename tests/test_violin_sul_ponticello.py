"""Tests for violin sul ponticello workbook-imported density module."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile


@pytest.mark.parametrize(
    "alias",
    [
        "Violin sul ponticello",
        "violin_sul_ponticello",
        "violino sul ponticello",
        "sul ponticello violin",
    ],
)
def test_sul_ponticello_aliases_resolve(alias: str):
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == "violino_sul_ponticello"
    assert profile.module_name == "violin_sul_ponticello"


def test_sul_ponticello_appears_in_gui_instrument_list():
    assert "vl_sul_pont" in INSTRUMENTS


def test_full_ten_level_ladder_committed():
    mod = importlib.import_module("instrumentos.violin_sul_ponticello")
    levels = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")
    assert len(mod.spectral_data) == 53
    assert next(iter(mod.spectral_data)) == "G3"
    assert next(reversed(mod.spectral_data)) == "B7"
    for note, row in mod.spectral_data.items():
        assert tuple(row.keys()) == levels, note
        assert all(v > 0 for v in row.values()), note


def test_mf_lookup_returns_workbook_anchor():
    mod = importlib.import_module("instrumentos.violin_sul_ponticello")
    assert mod.calcular_densidade("G4", "mf") == pytest.approx(33.832693, rel=0, abs=1e-5)
    assert mod.calcular_densidade("A3", "mf") == pytest.approx(31.104002, rel=0, abs=1e-5)


def test_ff_lookup_returns_workbook_anchor():
    mod = importlib.import_module("instrumentos.violin_sul_ponticello")
    assert mod.calcular_densidade("G4", "ff") == pytest.approx(34.86448, rel=0, abs=1e-5)


def test_pp_is_measured_workbook_anchor():
    mod = importlib.import_module("instrumentos.violin_sul_ponticello")
    assert mod.calcular_densidade("G4", "pp") == pytest.approx(33.833192, rel=0, abs=1e-5)


def test_pp_and_ff_are_not_equal_to_mf_for_typical_note():
    mod = importlib.import_module("instrumentos.violin_sul_ponticello")
    row = mod.spectral_data["G4"]
    assert row["pp"] != pytest.approx(row["mf"], rel=0, abs=1e-6)
    assert row["ff"] != pytest.approx(row["mf"], rel=0, abs=1e-6)


def test_pipeline_accepts_violin_sul_ponticello():
    request = AnalysisRequest(
        notes=("G4",),
        dynamics=("mf",),
        instruments=("Violin sul ponticello",),
        num_instruments=(1,),
    )
    resultados, densities, _ = calculate_metrics(request)
    assert densities[0] == pytest.approx(33.832693, rel=0, abs=1e-5)
    trace = resultados["instrument_lookup_trace"][0]
    assert trace["resolved_profile_id"] == "violino_sul_ponticello"
    assert trace["module_name"] == "violin_sul_ponticello"


def test_intermediate_dynamic_uses_anchors():
    mod = importlib.import_module("instrumentos.violin_sul_ponticello")
    pp = mod.calcular_densidade("G4", "pp")
    mf = mod.calcular_densidade("G4", "mf")
    mp = mod.calcular_densidade("G4", "mp")
    assert pp != mf
    assert mp is not None
