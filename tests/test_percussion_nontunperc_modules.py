"""Tests for NonTunPerc MC-backed unpitched percussion density modules."""

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
        "phase": "strike",
        "aliases": ("Bass drum", "bass_drum", "bombo"),
        "note": "C2",
        "pp": 7.613906,
        "mf": 12.889258,
        "ff": 22.888331,
    },
    {
        "display": "Cymbals",
        "instrument_id": "pratos",
        "module": "cymbals",
        "phase": "shimmer",
        "aliases": ("Cymbals", "cymbals", "pratos"),
        "note": "C5",
        "pp": 1.973133,
        "mf": 2.665803,
        "ff": 20.729071,
    },
    {
        "display": "Tam-tam",
        "instrument_id": "tamtam",
        "module": "tamtam",
        "phase": "shimmer",
        "aliases": ("Tam-tam", "tam_tam", "tamtam"),
        "note": "C2",
        "pp": 3.049788,
        "mf": 4.096546,
        "ff": 12.324004,
    },
    {
        "display": "Gong",
        "instrument_id": "gongo",
        "module": "gong",
        "phase": "shimmer",
        "aliases": ("Gong", "gong", "gongo"),
        "note": "C3",
        "pp": 1.537666,
        "mf": 2.10794,
        "ff": 17.148679,
    },
)

_INTERIOR = ("pp", "p", "mp", "mf", "f", "ff")


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_aliases_resolve_to_table_backed_profile(spec):
    for alias in spec["aliases"]:
        profile = resolve_profile(alias)
        assert profile is not None
        assert profile.instrument_id == spec["instrument_id"]
        assert profile.module_name == spec["module"]
        assert profile.unpitched is True


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_appears_in_gui_instrument_list(spec):
    assert spec["display"] in INSTRUMENTS


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_module_contract_mc_anchors_and_provenance(spec):
    mod = importlib.import_module(f"instrumentos.{spec['module']}")
    src = mod.INSTRUMENT_SOURCE
    assert src.source_type == "model_derived"
    assert src.unpitched is True
    assert "NO CALIBRATION ACHIEVED" in src.extraction_method
    assert "4a110db" in src.citation or "4a110db" in mod.SPECTRAL_PHASE_CI["nontunperc_commit"]
    assert mod.SPECTRAL_PHASE_CI["phase"] == spec["phase"]
    assert "p05" in mod.spectral_data_ci and "p95" in mod.spectral_data_ci
    row = mod.spectral_data[spec["note"]]
    assert row["pp"] == pytest.approx(spec["pp"])
    assert row["mf"] == pytest.approx(spec["mf"])
    assert row["ff"] == pytest.approx(spec["ff"])
    # Documented physical mf→ff cascade discontinuity retained.
    assert row["ff"] > row["mf"]


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_no_runtime_gpr_helper(spec):
    mod = get_instrument_module(spec["display"])
    assert not hasattr(mod, "predict_intermediate_dynamics")
    # Non-anchor dynamics require a committed full ladder (pending migration).
    from instrumentos.pitch_interpolation import MissingCommittedDynamicError

    with pytest.raises(MissingCommittedDynamicError):
        mod.calcular_densidade(spec["note"], "f")


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
    # Solo unpitched → no pitched bins.
    assert resultados["pitch_aggregation"]["distinct_pitch_count"] == 0
