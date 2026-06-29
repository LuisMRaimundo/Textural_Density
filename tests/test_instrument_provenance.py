"""CI guards for instrument acoustic provenance."""

from __future__ import annotations

import importlib

import pytest

from instrumentos.provenance import InstrumentSource

ACOUSTIC_MODULES = (
    "flute",
    "clarinet",
    "oboe",
    "violin",
    "violin_sordina",
    "violin_sul_ponticello",
    "violin_art_harm",
    "viola",
    "cello",
    "double_bass",
)


@pytest.mark.parametrize("module_name", ACOUSTIC_MODULES)
def test_acoustic_instrument_modules_have_provenance(module_name: str):
    mod = importlib.import_module(f"instrumentos.{module_name}")
    assert hasattr(mod, "INSTRUMENT_SOURCE")
    src: InstrumentSource = mod.INSTRUMENT_SOURCE
    assert src.citation
    assert src.extraction_method
    assert src.pitch_range[0] < src.pitch_range[1]
    assert src.uncertainty in {"low", "medium", "high"}
    assert src.version
