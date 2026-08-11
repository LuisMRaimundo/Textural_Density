"""Tests for viola technique modules (STE workbooks + OK_VIOLA dynamics workbooks)."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile

# STE-workbook modules (assumption-based anchors, PP/MF/FF_MEASURED dicts).
TECHNIQUES = (
    {
        "display": "Viola sul tasto",
        "module": "viola_sul_tasto",
        "registry_id": "viola_sul_tasto",
        "aliases": (
            "Viola sul tasto",
            "viola_sul_tasto",
            "viola sul tasto",
            "sul tasto viola",
        ),
        "probe_note": "C4",
        "probe_mf": 23.001624,
    },
)

# OK-workbook modules (measured anchors, clarinet-format spectral_data only).
OK_TECHNIQUES = (
    {
        "display": "vla sp",
        "module": "viola_sul_ponticello",
        "registry_id": "viola_sul_ponticello",
        "aliases": (
            "vla sp",
            "Viola sul ponticello",
            "viola_sul_ponticello",
            "viola sul ponticello",
            "sul ponticello viola",
        ),
        "probe_note": "C4",
        "probe_mf": 23.1077,
    },
    {
        "display": "vla sord",
        "module": "viola_sordina",
        "registry_id": "viola_sordina",
        "aliases": (
            "vla sord",
            "Viola sordina",
            "viola_sordina",
            "viola con sordina",
            "muted viola",
        ),
        "probe_note": "C4",
        "probe_mf": 17.4591,
    },
)


ALL_TECHNIQUES = TECHNIQUES + OK_TECHNIQUES


@pytest.mark.parametrize("tech", ALL_TECHNIQUES, ids=lambda t: t["module"])
@pytest.mark.parametrize("alias_idx", range(4))
def test_viola_technique_aliases_resolve(tech: dict, alias_idx: int):
    alias = tech["aliases"][alias_idx]
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == tech["registry_id"]
    assert profile.module_name == tech["module"]


@pytest.mark.parametrize("tech", ALL_TECHNIQUES, ids=lambda t: t["module"])
def test_viola_technique_appears_in_gui(tech: dict):
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
    assert next(iter(mod.spectral_data)) == "C3"
    assert next(reversed(mod.spectral_data)) == "C7"


@pytest.mark.parametrize("tech", OK_TECHNIQUES, ids=lambda t: t["module"])
def test_ok_workbook_full_ten_level_ladder_committed(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    levels = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")
    assert not hasattr(mod, "PP_MEASURED")
    assert len(mod.spectral_data) == 49
    assert next(iter(mod.spectral_data)) == "C3"
    assert next(reversed(mod.spectral_data)) == "C7"
    for note, row in mod.spectral_data.items():
        assert tuple(row.keys()) == levels, note
        assert all(v > 0 for v in row.values()), note


@pytest.mark.parametrize("tech", ALL_TECHNIQUES, ids=lambda t: t["module"])
def test_mf_lookup_returns_workbook_anchor(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.calcular_densidade(tech["probe_note"], "mf") == pytest.approx(
        tech["probe_mf"], rel=0, abs=1e-5
    )


@pytest.mark.parametrize("tech", ALL_TECHNIQUES, ids=lambda t: t["module"])
def test_pipeline_accepts_viola_technique(tech: dict):
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


@pytest.mark.parametrize("tech", OK_TECHNIQUES, ids=lambda t: t["module"])
def test_ok_workbook_measured_anchor_provenance(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.INSTRUMENT_SOURCE.uncertainty == "high"
    assert "measured pp/mf/ff anchors" in mod.INSTRUMENT_SOURCE.citation
