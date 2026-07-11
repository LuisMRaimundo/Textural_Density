"""
Phase 7: instrument registry tests.
"""

from __future__ import annotations

import pytest

from data_processor import calculate_metrics
from instrumentos import get_instrument_module, get_instrument_profile, list_instrument_ids
from instrumentos.registry import REGISTRY, resolve_profile


REQUIRED_FAMILIES = {
    "violino",
    "viola",
    "violoncelo",
    "contrabaixo",
    "flauta",
    "flautim",
    "oboe",
    "cor_anglais",
    "clarinete",
    "clarinete_baixo",
    "fagote",
    "contrafagote",
    "trompa",
    "trompete",
    "trombone",
    "trombone_baixo",
    "tuba",
    "piano",
    "celesta",
    "harpa",
    "timpanos",
    "bombo",
    "caixa",
    "pratos",
    "tamtam",
    "vibrafone",
    "marimba",
    "metalofone",
}


class TestInstrumentRegistry:
    def test_minimum_orchestral_instruments_registered(self):
        ids = set(list_instrument_ids())
        assert REQUIRED_FAMILIES.issubset(ids)

    def test_alias_resolution(self):
        assert resolve_profile("violin").instrument_id == "violino"
        assert resolve_profile("Flute").instrument_id == "flauta"
        assert resolve_profile("bass_clarinet").instrument_id == "clarinete_baixo"
        assert resolve_profile("glockenspiel").instrument_id == "metalofone"

    def test_dedicated_modules_for_literature_profiles(self):
        for iid in ("flauta", "clarinete", "oboe", "fagote", "violino", "viola", "violoncelo", "contrabaixo"):
            profile = REGISTRY[iid]
            assert profile.module_name is not None
            mod = get_instrument_module(iid)
            assert hasattr(mod, "calcular_densidade")
            assert profile.module_name in (
                "flute",
                "clarinet",
                "oboe",
                "bassoon",
                "violin",
                "viola",
                "cello",
                "double_bass",
            )

    def test_gpr_module_for_violin(self):
        mod = get_instrument_module("violin")
        assert getattr(mod, "IS_COARSE_DEFAULT", False) is False
        density = mod.calcular_densidade("G4", "mf")
        assert density > 0.0
        assert density == pytest.approx(28.582867, rel=1e-4)

    def test_profile_fields_present(self):
        profile = get_instrument_profile("trompete")
        assert profile.family == "brass"
        # Trumpet now ships a dedicated GPR CDM module (instrumentos/trumpet.py).
        assert profile.profile_status == "literature_derived"
        assert profile.uncertainty == "medium"
        assert profile.module_name == "trumpet"
        assert profile.sounding_range[0] < profile.sounding_range[1]
        assert profile.missing_data_warnings

    def test_calculate_metrics_with_coarse_instrument(self):
        data = {
            "notes": ["G4", "D4"],
            "dynamics": ["mf", "f"],
            "instruments": ["trombone", "fagote"],
            "num_instruments": [1, 1],
        }
        resultados, densidades, _ = calculate_metrics(data)
        assert float(resultados["density"]["instrument"]) > 0.0
        assert len(densidades) == 2
        warnings = resultados["metric_metadata"]["warnings"]
        assert any("symbolic_default" in w or "coarse_default" in w for w in warnings)

    def test_regression_baseline_instruments_unchanged(self):
        data = {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "f"],
            "instruments": ["flauta", "clarinete"],
            "num_instruments": [1, 1],
        }
        r1, d1, _ = calculate_metrics(data)
        assert float(r1["density"]["instrument"]) > 0.0
        assert len(d1) == 2
