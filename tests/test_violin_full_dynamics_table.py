"""Violin arco commits a full 10-dynamic ladder; no runtime GPR helper."""

from __future__ import annotations

import importlib

import pytest

from config import DYNAMIC_LEVELS
from core.converters import make_instrument_event
from core.orchestration import compute_event_one_player_density


@pytest.fixture(scope="module")
def violin():
    return importlib.import_module("instrumentos.violin")


def test_violin_source_declares_full_ladder(violin):
    assert violin.INSTRUMENT_SOURCE.dynamic_levels == tuple(DYNAMIC_LEVELS)


def test_violin_has_no_runtime_gpr_helper(violin):
    assert not hasattr(violin, "predict_intermediate_dynamics")


def test_violin_spectral_rows_have_all_dynamics(violin):
    for note, row in violin.spectral_data.items():
        for dyn in DYNAMIC_LEVELS:
            assert dyn in row, f"{note} missing {dyn}"


@pytest.mark.parametrize("dyn", list(DYNAMIC_LEVELS))
def test_pipeline_uses_committed_table(violin, dyn):
    pitch = "A3"
    event = make_instrument_event(
        idx=0,
        note=pitch,
        dynamic=dyn,
        instrument_name="violino",
        player_count=1,
    )
    density = compute_event_one_player_density(event, lambda _: violin)
    assert density == pytest.approx(violin.spectral_data[pitch][dyn])
