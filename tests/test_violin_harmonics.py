"""Tests for the pooled violin harmonics module (OK_VIOLIN harmonics workbook)."""

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
        "vl_harm",
        "vl harm",
        "violin_harmonics",
        "violin harmonics",
        "violino harmonics",
        "harmonics violin",
    ],
)
def test_harmonics_aliases_resolve(alias: str):
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == "violino_harm"
    assert profile.module_name == "violin_harmonics"


def test_harmonics_appears_in_gui_instrument_list():
    assert "vl_harm" in INSTRUMENTS


def test_full_ten_level_ladder_committed():
    mod = importlib.import_module("instrumentos.violin_harmonics")
    levels = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")
    assert len(mod.spectral_data) == 29
    assert next(iter(mod.spectral_data)) == "G5"
    assert next(reversed(mod.spectral_data)) == "B7"
    for note, row in mod.spectral_data.items():
        assert tuple(row.keys()) == levels, note
        assert all(v > 0 for v in row.values()), note


def test_mf_lookup_returns_workbook_anchor():
    mod = importlib.import_module("instrumentos.violin_harmonics")
    assert mod.calcular_densidade("G5", "mf") == pytest.approx(15.728918, rel=0, abs=1e-5)
    assert mod.calcular_densidade("B7", "mf") == pytest.approx(4.818004, rel=0, abs=1e-5)


def test_pipeline_accepts_violin_harmonics():
    request = AnalysisRequest(
        notes=("G5",),
        dynamics=("mf",),
        instruments=("vl_harm",),
        num_instruments=(1,),
    )
    resultados, densities, _ = calculate_metrics(request)
    assert densities[0] == pytest.approx(15.728918, rel=0, abs=1e-5)
    trace = resultados["instrument_lookup_trace"][0]
    assert trace["resolved_profile_id"] == "violino_harm"
    assert trace["module_name"] == "violin_harmonics"
