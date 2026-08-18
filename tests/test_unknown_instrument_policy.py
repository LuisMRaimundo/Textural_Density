"""Unknown / withdrawn instrument ids are rejected on the analysis path."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from error_handler import InputError
from instrumentos import get_instrument_module, get_instrument_profile
from instrumentos.registry import profile_for_event, resolve_profile


WITHDRAWN = (
    "violoncelo_sordina",
    "violoncelo_sul_tasto",
    "violoncelo_sul_ponticello",
    "contrabaixo_sordina",
    "contrabaixo_sul_tasto",
    "contrabaixo_sul_ponticello",
)


def test_resolve_profile_is_none_for_unknown():
    assert resolve_profile("__not_an_instrument__") is None
    assert resolve_profile("violoncelo_sordina") is None


def test_profile_for_event_raises_by_default():
    with pytest.raises(InputError, match="Unknown instrument"):
        profile_for_event("__not_an_instrument__")


def test_profile_for_event_audit_flag_returns_unknown_proxy():
    profile = profile_for_event("__not_an_instrument__", allow_unknown=True)
    assert profile.instrument_id == "unknown"
    assert profile.profile_status == "coarse_default"


@pytest.mark.parametrize("wid", WITHDRAWN)
def test_withdrawn_id_raises_and_does_not_resolve_to_parent(wid: str):
    parent = "violoncelo" if wid.startswith("violoncelo") else "contrabaixo"
    assert resolve_profile(wid) is None
    with pytest.raises(InputError, match="Unknown instrument"):
        calculate_metrics(
            {
                "notes": ["C3"],
                "dynamics": ["mf"],
                "instruments": [wid],
                "num_instruments": [1],
            }
        )
    assert resolve_profile(parent) is not None
    with pytest.raises(InputError, match="Unknown instrument"):
        get_instrument_module(wid)
    with pytest.raises(InputError, match="Unknown instrument"):
        get_instrument_profile(wid)


def test_registered_coarse_id_still_resolves():
    mod = get_instrument_module("trombone_baixo")
    assert getattr(mod, "IS_COARSE_DEFAULT", False) is True
    profile = get_instrument_profile("piano")
    assert profile.instrument_id == "piano"
    assert profile.module_name is None
