"""Tests for cello technique modules (dest-Zenodo Dynamics_predicter workbooks)."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile

DEST_TECHNIQUES = (
    {
        "display": "vlc_sord",
        "module": "cello_sordina",
        "registry_id": "violoncelo_sordina",
        "aliases": (
            "vlc_sord",
            "vlc_con_sord",
            "Cello sordina",
            "violoncelo_sordina",
            "cello con sordina",
            "muted cello",
        ),
        "probe_note": "C2",
        "probe_mf": 62.349097,
        "n_notes": 46,
        "first": "C2",
        "last": "A5",
    },
    {
        "display": "vlc_sp",
        "module": "cello_sul_ponticello",
        "registry_id": "violoncelo_sul_ponticello",
        "aliases": (
            "vlc_sp",
            "vlc_sul_pont",
            "Cello sul ponticello",
            "violoncelo_sul_ponticello",
            "cello sul ponticello",
            "sul ponticello cello",
        ),
        "probe_note": "C2",
        "probe_mf": 64.153127,
        "n_notes": 46,
        "first": "C2",
        "last": "A5",
    },
    {
        "display": "vlc_harm",
        "module": "cello_harmonics",
        "registry_id": "violoncelo_harm",
        "aliases": (
            "vlc_harm",
            "cello_harmonics",
            "cello harmonics",
            "violoncelo_harm",
            "harmonics cello",
        ),
        "probe_note": "C4",
        "probe_mf": 20.2499,
        "n_notes": 25,
        "first": "C4",
        "last": "C6",
    },
)


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
@pytest.mark.parametrize("alias_idx", range(4))
def test_cello_technique_aliases_resolve(tech: dict, alias_idx: int):
    alias = tech["aliases"][alias_idx]
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == tech["registry_id"]
    assert profile.module_name == tech["module"]


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
def test_cello_technique_appears_in_gui(tech: dict):
    assert tech["display"] in INSTRUMENTS
    assert "Cello sul tasto" not in INSTRUMENTS


def test_retired_sul_tasto_absent():
    """cello_sul_tasto (STE assumption-based) remains withdrawn."""
    assert "Cello sul tasto" not in INSTRUMENTS
    assert resolve_profile("violoncelo_sul_tasto") is None
    assert resolve_profile("cello_sul_tasto") is None


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


@pytest.mark.parametrize("tech", DEST_TECHNIQUES, ids=lambda t: t["module"])
def test_dest_workbook_measured_anchor_provenance(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert mod.INSTRUMENT_SOURCE.uncertainty == "high"
    assert "measured pp/mf/ff anchors" in mod.INSTRUMENT_SOURCE.citation
    assert tech["first"] not in ("C2",) or tech["module"] != "cello_harmonics"
    if tech["module"] == "cello_harmonics":
        assert "C2" not in mod.spectral_data
        assert "B3" not in mod.spectral_data
