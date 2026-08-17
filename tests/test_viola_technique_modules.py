"""Tests for viola technique modules (OK_VIOLA dynamics workbooks)."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile

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


@pytest.mark.parametrize("tech", OK_TECHNIQUES, ids=lambda t: t["module"])
@pytest.mark.parametrize("alias_idx", range(4))
def test_viola_technique_aliases_resolve(tech: dict, alias_idx: int):
    alias = tech["aliases"][alias_idx]
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == tech["registry_id"]
    assert profile.module_name == tech["module"]


@pytest.mark.parametrize("tech", OK_TECHNIQUES, ids=lambda t: t["module"])
def test_viola_technique_appears_in_gui(tech: dict):
    assert tech["display"] in INSTRUMENTS


def test_retired_sul_tasto_absent():
    """viola_sul_tasto (STE assumption-based) was retired on 2026-08-11."""
    assert "Viola sul tasto" not in INSTRUMENTS
    assert resolve_profile("viola_sul_tasto") is None


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


@pytest.mark.parametrize("tech", OK_TECHNIQUES, ids=lambda t: t["module"])
def test_mf_lookup_returns_workbook_anchor(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.calcular_densidade(tech["probe_note"], "mf") == pytest.approx(
        tech["probe_mf"], rel=0, abs=1e-5
    )


@pytest.mark.parametrize("tech", OK_TECHNIQUES, ids=lambda t: t["module"])
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


@pytest.mark.parametrize("tech", OK_TECHNIQUES, ids=lambda t: t["module"])
def test_ok_workbook_measured_anchor_provenance(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.INSTRUMENT_SOURCE.uncertainty == "high"
    assert "measured pp/mf/ff anchors" in mod.INSTRUMENT_SOURCE.citation
