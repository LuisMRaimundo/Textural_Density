"""Tests for cello technique modules imported from Cello_pp/mf/ff workbooks."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile

TECHNIQUES = (
    {
        "display": "Cello sordina",
        "module": "cello_sordina",
        "registry_id": "violoncelo_sordina",
        "aliases": (
            "Cello sordina",
            "cello_sordina",
            "violoncelo_sordina",
            "muted cello",
        ),
        "probe_note": "C4",
        "probe_mf": 22.066789,
    },
    {
        "display": "Cello sul tasto",
        "module": "cello_sul_tasto",
        "registry_id": "violoncelo_sul_tasto",
        "aliases": (
            "Cello sul tasto",
            "cello_sul_tasto",
            "violoncelo_sul_tasto",
            "sul tasto cello",
        ),
        "probe_note": "C4",
        "probe_mf": 25.130286,
    },
    {
        "display": "Cello sul ponticello",
        "module": "cello_sul_ponticello",
        "registry_id": "violoncelo_sul_ponticello",
        "aliases": (
            "Cello sul ponticello",
            "cello_sul_ponticello",
            "violoncelo_sul_ponticello",
            "sul ponticello cello",
        ),
        "probe_note": "C4",
        "probe_mf": 34.607615,
    },
)


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
@pytest.mark.parametrize("alias_idx", range(4))
def test_cello_technique_aliases_resolve(tech: dict, alias_idx: int):
    alias = tech["aliases"][alias_idx]
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == tech["registry_id"]
    assert profile.module_name == tech["module"]


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_cello_technique_appears_in_gui(tech: dict):
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
    assert len(mod.spectral_data) == 49
    assert next(iter(mod.spectral_data)) == "C2"
    assert next(reversed(mod.spectral_data)) == "C6"


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_mf_lookup_returns_workbook_anchor(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.calcular_densidade(tech["probe_note"], "mf") == pytest.approx(
        tech["probe_mf"], rel=0, abs=1e-5
    )


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_pipeline_accepts_cello_technique(tech: dict):
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
