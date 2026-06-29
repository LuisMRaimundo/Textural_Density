"""Tests for violin art harm mf-only anchor extrapolation."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from instrumentos.registry import resolve_profile


@pytest.mark.parametrize(
    "alias",
    [
        "Violin art harm",
        "violin_art_harm",
        "violin artificial harmonics",
        "violino art harm",
        "art harm violin",
    ],
)
def test_art_harm_aliases_resolve(alias: str):
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == "violino_art_harm"
    assert profile.module_name == "violin_art_harm"


def test_mf_measured_values_preserved():
    mod = importlib.import_module("instrumentos.violin_art_harm")
    assert len(mod.MF_MEASURED) == 25
    assert mod.MF_MEASURED["G5"] == pytest.approx(12.974202, rel=0, abs=1e-5)
    assert mod.spectral_data["G5"]["mf"] == pytest.approx(12.974202, rel=0, abs=1e-5)
    assert mod.spectral_data["G#5"]["mf"] == pytest.approx(11.284534, rel=0, abs=1e-5)
    assert mod.spectral_data["G7"]["mf"] == pytest.approx(5.525015, rel=0, abs=1e-5)


def test_pp_ff_extrapolated_not_equal_to_mf():
    mod = importlib.import_module("instrumentos.violin_art_harm")
    row = mod.spectral_data["A5"]
    assert row["pp"] != pytest.approx(row["mf"], rel=0, abs=1e-4)
    assert row["ff"] != pytest.approx(row["mf"], rel=0, abs=1e-4)


def test_pipeline_accepts_violin_art_harm():
    request = AnalysisRequest(
        notes=("A5",),
        dynamics=("mf",),
        instruments=("Violin art harm",),
        num_instruments=(1,),
    )
    resultados, densities, _ = calculate_metrics(request)
    assert densities[0] == pytest.approx(10.221026, rel=0, abs=1e-5)
    trace = resultados["instrument_lookup_trace"][0]
    assert trace["resolved_profile_id"] == "violino_art_harm"
    assert trace["module_name"] == "violin_art_harm"


def test_gpr_covers_intermediate_dynamics_in_pipeline():
    request = AnalysisRequest(
        notes=("G5",),
        dynamics=("mp",),
        instruments=("Violin art harm",),
        num_instruments=(1,),
    )
    _, densities, _ = calculate_metrics(request)
    mod = importlib.import_module("instrumentos.violin_art_harm")
    pp = mod.calcular_densidade("G5", "pp")
    mf = mod.calcular_densidade("G5", "mf")
    assert min(pp, mf) <= densities[0] <= max(pp, mf)
