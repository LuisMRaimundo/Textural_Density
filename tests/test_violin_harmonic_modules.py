"""Tests for violin harmonic modules from Violin_*_harmo workbooks."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos.registry import resolve_profile

TECHNIQUES = (
    {
        "display": "Violin art harm",
        "module": "violin_art_harm",
        "registry_id": "violino_art_harm",
        "aliases": (
            "Violin art harm",
            "violin_art_harm",
            "violin artificial harmonics",
            "violino art harm",
            "art harm violin",
        ),
        "probe_note": "G5",
        "n_notes": 30,
        "first": "G5",
        "last": "C8",
    },
    {
        "display": "Violin nat harm",
        "module": "violin_nat_harm",
        "registry_id": "violino_nat_harm",
        "aliases": (
            "Violin nat harm",
            "violin_nat_harm",
            "violin natural harmonics",
            "violino nat harm",
            "nat harm violin",
        ),
        "probe_note": "G5",
        "n_notes": 20,
        "first": "G4",
        "last": "B7",
    },
)


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
@pytest.mark.parametrize("alias_idx", range(5))
def test_harmonic_aliases_resolve(tech: dict, alias_idx: int):
    alias = tech["aliases"][alias_idx]
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == tech["registry_id"]
    assert profile.module_name == tech["module"]


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_harmonic_appears_in_gui(tech: dict):
    assert tech["display"] in INSTRUMENTS


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_workbook_anchors_preserved(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    assert hasattr(mod, "PP_MEASURED")
    assert hasattr(mod, "MF_MEASURED")
    assert hasattr(mod, "FF_MEASURED")
    for note, pp in mod.PP_MEASURED.items():
        assert mod.spectral_data[note]["pp"] == pytest.approx(round(pp, 6), rel=0, abs=1e-6)
    for note, mf in mod.MF_MEASURED.items():
        assert mod.spectral_data[note]["mf"] == pytest.approx(round(mf, 6), rel=0, abs=1e-6)
    for note, ff in mod.FF_MEASURED.items():
        assert mod.spectral_data[note]["ff"] == pytest.approx(round(ff, 6), rel=0, abs=1e-6)
    assert len(mod.spectral_data) == tech["n_notes"]
    assert next(iter(mod.spectral_data)) == tech["first"]
    assert next(reversed(mod.spectral_data)) == tech["last"]


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_mf_lookup_returns_workbook_anchor(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    note = tech["probe_note"]
    assert mod.calcular_densidade(note, "mf") == pytest.approx(
        mod.MF_MEASURED[note], rel=0, abs=1e-5
    )


@pytest.mark.parametrize("tech", TECHNIQUES, ids=lambda t: t["module"])
def test_pipeline_accepts_harmonic_technique(tech: dict):
    mod = importlib.import_module(f"instrumentos.{tech['module']}")
    note = tech["probe_note"]
    request = AnalysisRequest(
        notes=(note,),
        dynamics=("mf",),
        instruments=(tech["display"],),
        num_instruments=(1,),
    )
    resultados, densities, _ = calculate_metrics(request)
    assert densities[0] == pytest.approx(mod.MF_MEASURED[note], rel=0, abs=1e-5)
    trace = resultados["instrument_lookup_trace"][0]
    assert trace["resolved_profile_id"] == tech["registry_id"]
    assert trace["module_name"] == tech["module"]
