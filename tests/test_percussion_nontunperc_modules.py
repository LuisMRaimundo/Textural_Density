"""Tests for NonTunPerc Analysis-backed percussion density modules."""

from __future__ import annotations

import importlib

import pytest

from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from gui.state import INSTRUMENTS
from instrumentos import get_instrument_module
from instrumentos.registry import resolve_profile

_SPECS = (
    {
        "display": "Bass drum",
        "instrument_id": "bombo",
        "module": "bass_drum",
        "aliases": ("Bass drum", "bass_drum", "bombo"),
        "note": "C2",
        "pp": 2.18772,
        "mf": 3.703499,
        "ff": 6.576554,
    },
    {
        "display": "Cymbals",
        "instrument_id": "pratos",
        "module": "cymbals",
        "aliases": ("Cymbals", "cymbals", "pratos"),
        "note": "C5",
        "pp": 15.777819,
        "mf": 22.031373,
        "ff": 32.559219,
    },
    {
        "display": "Tam-tam",
        "instrument_id": "tamtam",
        "module": "tamtam",
        "aliases": ("Tam-tam", "tam_tam", "tamtam"),
        "note": "C2",
        "pp": 4.004706,
        "mf": 5.525262,
        "ff": 52.090379,
    },
    {
        "display": "Gong",
        "instrument_id": "gongo",
        "module": "gong",
        "aliases": ("Gong", "gong", "gongo"),
        "note": "C3",
        "pp": 1.746191,
        "mf": 2.437317,
        "ff": 26.999281,
    },
)


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_aliases_resolve_to_table_backed_profile(spec):
    for alias in spec["aliases"]:
        profile = resolve_profile(alias)
        assert profile is not None
        assert profile.instrument_id == spec["instrument_id"]
        assert profile.module_name == spec["module"]
        assert profile.profile_status == "literature_derived"


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_appears_in_gui_instrument_list(spec):
    assert spec["display"] in INSTRUMENTS


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_module_contract_and_analysis_anchors(spec):
    mod = importlib.import_module(f"instrumentos.{spec['module']}")
    assert hasattr(mod, "spectral_data")
    assert hasattr(mod, "calcular_densidade")
    assert hasattr(mod, "predict_intermediate_dynamics")
    assert mod.INSTRUMENT_SOURCE.dynamic_levels == ("pp", "mf", "ff")
    assert "density_profiles.csv" in (mod.INSTRUMENT_SOURCE.source_url_or_identifier or "")
    row = mod.spectral_data[spec["note"]]
    assert row["pp"] == pytest.approx(spec["pp"])
    assert row["mf"] == pytest.approx(spec["mf"])
    assert row["ff"] == pytest.approx(spec["ff"])
    resolved = get_instrument_module(spec["display"])
    assert resolved.calcular_densidade(spec["note"], "mf") == pytest.approx(spec["mf"])
    assert resolved.calcular_densidade(spec["note"], "ff") == pytest.approx(spec["ff"])


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_calculate_metrics_accepts_display_name(spec):
    resultados, densities, pitches = calculate_metrics(
        AnalysisRequest(
            notes=(spec["note"],),
            dynamics=("mf",),
            instruments=(spec["display"],),
            num_instruments=(1,),
        )
    )
    assert len(pitches) == 1
    assert densities[0] == pytest.approx(spec["mf"], rel=0, abs=1e-5)
    trace = resultados["instrument_lookup_trace"][0]
    assert trace["resolved_profile_id"] == spec["instrument_id"]
    assert trace["module_name"] == spec["module"]
