"""Tests for double bass technique modules from Contrabass-pp/mf/ff workbooks."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile

TECHNIQUES = (
    {
        "display": "Double bass sordina",
        "module": "double_bass_sordina",
        "registry_id": "contrabaixo_sordina",
        "aliases": (
            "Double bass sordina",
            "double_bass_sordina",
            "contrabaixo_sordina",
            "muted contrabass",
        ),
        "probe_note": "A2",
        "probe_mf": 31.564113,
    },
    {
        "display": "Double bass sul tasto",
        "module": "double_bass_sul_tasto",
        "registry_id": "contrabaixo_sul_tasto",
        "aliases": (
            "Double bass sul tasto",
            "double_bass_sul_tasto",
            "contrabaixo_sul_tasto",
            "sul tasto double bass",
        ),
        "probe_note": "A2",
        "probe_mf": 35.946108,
    },
    {
        "display": "Double bass sul ponticello",
        "module": "double_bass_sul_ponticello",
        "registry_id": "contrabaixo_sul_ponticello",
        "aliases": (
            "Double bass sul ponticello",
            "double_bass_sul_ponticello",
            "contrabaixo_sul_ponticello",
            "sul ponticello double bass",
        ),
        "probe_note": "A2",
        "probe_mf": 49.502383,
    },
)


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
@pytest.mark.parametrize("alias_idx", range(4))
def test_double_bass_technique_aliases_resolve(tech: dict, alias_idx: int):
    alias = tech["aliases"][alias_idx]
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == tech["registry_id"]
    assert profile.module_name == tech["module"]


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_double_bass_technique_appears_in_gui(tech: dict):
    assert tech["display"] in INSTRUMENTS


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_workbook_anchors_preserved(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    for note, pp in mod.PP_MEASURED.items():
        assert mod.spectral_data[note]["pp"] == pytest.approx(round(pp, 6), rel=0, abs=1e-6)
    for note, mf in mod.MF_MEASURED.items():
        assert mod.spectral_data[note]["mf"] == pytest.approx(round(mf, 6), rel=0, abs=1e-6)
    for note, ff in mod.FF_MEASURED.items():
        assert mod.spectral_data[note]["ff"] == pytest.approx(round(ff, 6), rel=0, abs=1e-6)
    assert len(mod.spectral_data) == 45
    assert next(iter(mod.spectral_data)) == "E1"
    assert next(reversed(mod.spectral_data)) == "C5"


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_mf_lookup_returns_workbook_anchor(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.calcular_densidade(tech["probe_note"], "mf") == pytest.approx(
        tech["probe_mf"], rel=0, abs=1e-5
    )


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_pipeline_accepts_double_bass_technique(tech: dict):
    request = AnalysisRequest(
        notes=(tech["probe_note"],),
        dynamics=("mf",),
        instruments=(tech["display"],),
        num_instruments=(1,),
    )
    resultados, densities, _ = calculate_metrics(request)
    assert densities[0] == pytest.approx(tech["probe_mf"], rel=0, abs=1e-5)
    trace = resultados["instrument_lookup_trace"][0]
    assert trace["resolved_profile_id"] == tech["registry_id"]
    assert trace["module_name"] == tech["module"]


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_high_uncertainty_assumption_based_provenance(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.INSTRUMENT_SOURCE.uncertainty == "high"
    assert "assumption-based" in mod.INSTRUMENT_SOURCE.citation.lower()
