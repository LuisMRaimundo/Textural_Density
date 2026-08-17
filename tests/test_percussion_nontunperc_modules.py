"""Tests for NonTunPerc MC-backed unpitched percussion density modules."""

from __future__ import annotations

import importlib

import pytest

from config import DYNAMIC_LEVELS
from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from core.unpitched_routing import canonical_unpitched_note
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
        "pp": 7.613906,
        "mf": 12.889258,
        "ff": 22.888331,
        "f": 17.17596,
    },
    {
        "display": "Cymbals",
        "instrument_id": "pratos",
        "module": "cymbals",
        "phase": "shimmer",
        "aliases": ("Cymbals", "cymbals", "pratos"),
        "pp": 1.973133,
        "mf": 2.665803,
        "ff": 20.729071,
        "f": 7.433681,
    },
    {
        "display": "Tam-tam",
        "instrument_id": "tamtam",
        "module": "tamtam",
        "phase": "shimmer",
        "aliases": ("Tam-tam", "tam_tam", "tamtam"),
        "pp": 3.049788,
        "mf": 4.096546,
        "ff": 12.324004,
        "f": 7.105339,
    },
    {
        "display": "Gong",
        "instrument_id": "gongo",
        "module": "gong",
        "phase": "shimmer",
        "aliases": ("Gong", "gong", "gongo"),
        "pp": 1.537666,
        "mf": 2.10794,
        "ff": 17.148679,
        "f": 6.012353,
    },
)


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
    assert src.dynamic_levels == tuple(DYNAMIC_LEVELS)
    assert "NO CALIBRATION ACHIEVED" in src.extraction_method
    assert "4a110db" in src.citation or "4a110db" in mod.SPECTRAL_PHASE_CI["nontunperc_commit"]
    assert mod.SPECTRAL_PHASE_CI["phase"] == spec["phase"]
    assert "p05" in mod.spectral_data_ci and "p95" in mod.spectral_data_ci
    assert mod.LOOKUP_NOTE == canonical_unpitched_note(spec["display"])
    assert list(mod.spectral_data) == [mod.LOOKUP_NOTE]
    ladder = mod.DYNAMIC_CDM
    assert ladder["pp"] == pytest.approx(spec["pp"])
    assert ladder["mf"] == pytest.approx(spec["mf"])
    assert ladder["ff"] == pytest.approx(spec["ff"])
    assert ladder["ff"] > ladder["mf"] > ladder["pp"]
    # Interior levels committed (former internal_default log-linear path).
    assert ladder["f"] == pytest.approx(spec["f"])
    assert ladder["pp"] < ladder["p"] < ladder["mp"] < ladder["mf"] < ladder["f"] < ladder["ff"]


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_no_runtime_gpr_helper_and_note_ignored(spec):
    mod = get_instrument_module(spec["display"])
    assert not hasattr(mod, "predict_intermediate_dynamics")
    # Dynamics-only: arbitrary note strings yield the same committed cell.
    assert mod.calcular_densidade("C4", "f") == pytest.approx(spec["f"])
    assert mod.calcular_densidade("G9", "f") == pytest.approx(spec["f"])
    assert mod.calcular_densidade(mod.LOOKUP_NOTE, "mf") == pytest.approx(spec["mf"])


@pytest.mark.parametrize("spec", _SPECS, ids=lambda s: s["module"])
def test_calculate_metrics_accepts_display_name(spec):
    note = canonical_unpitched_note(spec["display"])
    resultados, densities, pitches = calculate_metrics(
        AnalysisRequest(
            notes=(note,),
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
