"""Tests for violin sul tasto workbook-imported density module."""

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
        "Violin sul tasto",
        "violin_sul_tasto",
        "violino sul tasto",
        "sul tasto violin",
    ],
)
def test_sul_tasto_aliases_resolve(alias: str):
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == "violino_sul_tasto"
    assert profile.module_name == "violin_sul_tasto"


def test_sul_tasto_appears_in_gui_instrument_list():
    assert "vl_sul_tast" in INSTRUMENTS


def test_full_ten_level_ladder_committed():
    mod = importlib.import_module("instrumentos.violin_sul_tasto")
    levels = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")
    assert len(mod.spectral_data) == 53
    assert next(iter(mod.spectral_data)) == "G3"
    assert next(reversed(mod.spectral_data)) == "B7"
    for note, row in mod.spectral_data.items():
        assert tuple(row.keys()) == levels, note
        assert all(v > 0 for v in row.values()), note


def test_mf_lookup_returns_workbook_anchor():
    mod = importlib.import_module("instrumentos.violin_sul_tasto")
    assert mod.calcular_densidade("G4", "mf") == pytest.approx(41.350741, rel=0, abs=1e-5)
    assert mod.calcular_densidade("G3", "mf") == pytest.approx(38.487619, rel=0, abs=1e-5)


def test_pipeline_accepts_violin_sul_tasto():
    request = AnalysisRequest(
        notes=("G4",),
        dynamics=("mf",),
        instruments=("vl_sul_tast",),
        num_instruments=(1,),
    )
    resultados, densities, _ = calculate_metrics(request)
    assert densities[0] == pytest.approx(41.350741, rel=0, abs=1e-5)
    trace = resultados["instrument_lookup_trace"][0]
    assert trace["resolved_profile_id"] == "violino_sul_tasto"
    assert trace["module_name"] == "violin_sul_tasto"
