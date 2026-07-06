"""Contracts for technique metadata vs numerical table coverage."""

from __future__ import annotations

import importlib
import inspect

import pytest

from instrumentos.registry import REGISTRY
from tests.string_constants import STRING_INSTRUMENTS

GPR_WIND_MODULES = ("flute", "oboe", "clarinet", "bassoon")
GPR_STRING_MODULES = ("violin", "viola", "cello", "double_bass")


@pytest.mark.parametrize("module_name", GPR_STRING_MODULES)
def test_string_table_technique_is_arco_sustain(module_name: str):
    mod = importlib.import_module(f"instrumentos.{module_name}")
    src = mod.INSTRUMENT_SOURCE
    assert src.source_technique == "arco_sustain"
    assert src.table_supported_techniques == ("arco_sustain",)


@pytest.mark.parametrize("module_name", GPR_WIND_MODULES)
def test_wind_table_technique_is_ordinary_sustain(module_name: str):
    mod = importlib.import_module(f"instrumentos.{module_name}")
    src = mod.INSTRUMENT_SOURCE
    assert src.source_technique == "ordinary_sustain"
    assert src.table_supported_techniques == ("ordinary_sustain",)


@pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
def test_registry_lists_broader_techniques_than_table(spec):
    profile = REGISTRY[spec.registry_ids[0]]
    mod = importlib.import_module(f"instrumentos.{spec.module_name}")
    table_techniques = set(mod.INSTRUMENT_SOURCE.table_supported_techniques)
    registry_techniques = set(profile.supported_techniques)
    assert "arco" in registry_techniques
    assert "pizzicato" in registry_techniques
    assert "pizzicato" not in table_techniques


@pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
def test_calcular_densidade_has_no_technique_parameter(spec):
    mod = importlib.import_module(f"instrumentos.{spec.module_name}")
    sig = inspect.signature(mod.calcular_densidade)
    assert "technique" not in sig.parameters


@pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
def test_string_profile_warns_technique_overclaim(spec):
    profile = REGISTRY[spec.registry_ids[0]]
    joined = " ".join(profile.missing_data_warnings).lower()
    assert "arco_sustain" in joined or "arco sustain" in joined
    assert "technique" in joined


def test_flute_registry_technique_warning():
    profile = REGISTRY["flauta"]
    joined = " ".join(profile.missing_data_warnings).lower()
    assert "ordinary_sustain" in joined
    assert "technique" in joined


@pytest.mark.parametrize("module_name", GPR_STRING_MODULES + GPR_WIND_MODULES)
def test_dynamic_anchors_unchanged_pp_mf_ff(module_name: str):
    mod = importlib.import_module(f"instrumentos.{module_name}")
    assert mod.INSTRUMENT_SOURCE.dynamic_levels == ("pp", "mf", "ff")
