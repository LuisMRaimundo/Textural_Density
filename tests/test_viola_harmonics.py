"""Tests for the pooled viola harmonics module (OK_VIOLA harmonics workbook)."""

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
        "vla harm",
        "viola_harmonics",
        "viola harmonics",
        "viola harm",
        "harmonics viola",
    ],
)
def test_harmonics_aliases_resolve(alias: str):
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == "viola_harm"
    assert profile.module_name == "viola_harmonics"


def test_harmonics_appears_in_gui_instrument_list():
    assert "vla harm" in INSTRUMENTS


def test_full_ten_level_ladder_committed():
    mod = importlib.import_module("instrumentos.viola_harmonics")
    levels = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")
    assert len(mod.spectral_data) == 37
    assert next(iter(mod.spectral_data)) == "C4"
    assert next(reversed(mod.spectral_data)) == "C7"
    for note, row in mod.spectral_data.items():
        assert tuple(row.keys()) == levels, note
        assert all(v > 0 for v in row.values()), note


def test_mf_lookup_returns_workbook_anchor():
    mod = importlib.import_module("instrumentos.viola_harmonics")
    assert mod.calcular_densidade("C4", "mf") == pytest.approx(17.4591, rel=0, abs=1e-5)
    assert mod.calcular_densidade("C5", "mf") == pytest.approx(12.7194, rel=0, abs=1e-5)


def test_pipeline_accepts_viola_harmonics():
    request = AnalysisRequest(
        notes=("C4",),
        dynamics=("mf",),
        instruments=("vla harm",),
        num_instruments=(1,),
    )
    resultados, densities, _ = calculate_metrics(request)
    assert densities[0] == pytest.approx(17.4591, rel=0, abs=1e-5)
    trace = resultados["instrument_lookup_trace"][0]
    assert trace["resolved_profile_id"] == "viola_harm"
    assert trace["module_name"] == "viola_harmonics"
