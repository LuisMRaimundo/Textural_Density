"""Tests for double-bass technique modules (dest-Zenodo Dynamics_predicter workbooks)."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile

DEST_TECHNIQUES = (
    {
        "display": "cb_sord",
        "module": "double_bass_sordina",
        "registry_id": "contrabaixo_sordina",
        "aliases": (
            "cb_sord",
            "cb_con_sord",
            "Double bass sordina",
            "contrabaixo_sordina",
            "double bass con sordina",
            "muted double bass",
        ),
        "probe_note": "F1",
        "probe_mf": 45.06363,
        "n_notes": 45,
        "first": "E1",
        "last": "C5",
    },
    {
        "display": "cb_sp",
        "module": "double_bass_sul_ponticello",
        "registry_id": "contrabaixo_sul_ponticello",
        "aliases": (
            "cb_sp",
            "cb_sul_pont",
            "Double bass sul ponticello",
            "contrabaixo_sul_ponticello",
            "double bass sul ponticello",
            "sul ponticello double bass",
        ),
        "probe_note": "E1",
        "probe_mf": 51.658048,
        "n_notes": 45,
        "first": "E1",
        "last": "C5",
    },
    {
        "display": "cb_harm",
        "module": "double_bass_harmonics",
        "registry_id": "contrabaixo_harm",
        "aliases": (
            "cb_harm",
            "double_bass_harmonics",
            "double bass harmonics",
            "contrabaixo_harm",
            "harmonics double bass",
        ),
        "probe_note": "E3",
        "probe_mf": 25.779643,
        "n_notes": 21,
        "first": "E3",
        "last": "C5",
    },
)


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
@pytest.mark.parametrize("alias_idx", range(4))
def test_dbass_technique_aliases_resolve(tech: dict, alias_idx: int):
    alias = tech["aliases"][alias_idx]
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == tech["registry_id"]
    assert profile.module_name == tech["module"]


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
def test_dbass_technique_appears_in_gui(tech: dict):
    assert tech["display"] in INSTRUMENTS
    assert "Double bass sul tasto" not in INSTRUMENTS


def test_retired_sul_tasto_absent():
    """double_bass_sul_tasto (STE assumption-based) remains withdrawn."""
    assert "Double bass sul tasto" not in INSTRUMENTS
    assert resolve_profile("contrabaixo_sul_tasto") is None
    assert resolve_profile("double_bass_sul_tasto") is None


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
def test_dest_workbook_full_ten_level_ladder_committed(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    levels = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")
    assert not hasattr(mod, "PP_MEASURED")
    assert len(mod.spectral_data) == tech["n_notes"]
    assert next(iter(mod.spectral_data)) == tech["first"]
    assert next(reversed(mod.spectral_data)) == tech["last"]
    for note, row in mod.spectral_data.items():
        assert tuple(row.keys()) == levels, note
        assert all(v > 0 for v in row.values()), note


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
def test_mf_lookup_returns_workbook_anchor(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.calcular_densidade(tech["probe_note"], "mf") == pytest.approx(
        tech["probe_mf"], rel=0, abs=1e-5
    )


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
def test_pipeline_accepts_dbass_technique(tech: dict):
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


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
def test_dest_workbook_measured_anchor_provenance(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.INSTRUMENT_SOURCE.uncertainty == "high"
    assert "measured pp/mf/ff anchors" in mod.INSTRUMENT_SOURCE.citation
    if tech["module"] == "double_bass_sordina":
        assert "E1" in mod.spectral_data
    if tech["module"] == "double_bass_harmonics":
        assert "E1" not in mod.spectral_data
        assert "C#5" not in mod.spectral_data
        assert "G6" not in mod.spectral_data
