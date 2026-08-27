"""Unknown / withdrawn instrument ids are rejected on the analysis path."""

from __future__ import annotations

import pytest

from adapters.gui_adapter import build_analysis_request, calculate_from_gui_request
from core.pipeline import calculate_metrics
from core.score_analysis import analyze_score
from core.unpitched_routing import UNPITCHED_INSTRUMENT_GROUP_LABEL
from error_handler import InputError
from instrumentos import get_instrument_module, get_instrument_profile
from instrumentos.registry import (
    accepted_instrument_ids_text,
    list_instrument_ids,
    profile_for_event,
    resolve_profile,
)
from xml_loader import parse_xml_to_events


WITHDRAWN = (
    "violoncelo_sul_tasto",
    "contrabaixo_sordina",
    "contrabaixo_sul_tasto",
    "contrabaixo_sul_ponticello",
)


def test_resolve_profile_is_none_for_unknown():
    assert resolve_profile("__not_an_instrument__") is None
    assert resolve_profile("violoncelo_sul_tasto") is None


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


def test_musicxml_qualified_part_names_are_aliases_not_proxy():
    assert resolve_profile("Clarinet in Bb").instrument_id == "clarinete"
    assert resolve_profile("Horn in F").instrument_id == "trompa"


def test_registered_coarse_id_still_resolves():
    mod = get_instrument_module("trombone_baixo")
    assert getattr(mod, "IS_COARSE_DEFAULT", False) is True
    profile = get_instrument_profile("piano")
    assert profile.instrument_id == "piano"
    assert profile.module_name is None


def test_unknown_error_lists_accepted_ids():
    with pytest.raises(InputError, match="Accepted registry ids") as exc:
        calculate_metrics(
            {
                "notes": ["C4"],
                "dynamics": ["mf"],
                "instruments": ["__not_an_instrument__"],
                "num_instruments": [1],
            }
        )
    msg = str(exc.value)
    ids = accepted_instrument_ids_text()
    assert ids in msg
    assert "flauta" in msg
    assert "violino" in msg


def _unmapped_part_xml() -> str:
    return """<?xml version="1.0"?>
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>Violin I</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>1</divisions></attributes>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note>
    </measure>
  </part>
</score-partwise>
"""


def test_musicxml_unmapped_part_names_part_and_accepted_ids(tmp_path):
    path = tmp_path / "unmapped_part.musicxml"
    path.write_text(_unmapped_part_xml(), encoding="utf-8")
    with pytest.raises(InputError, match="Violin I") as exc:
        parse_xml_to_events(str(path))
    msg = str(exc.value)
    assert "part_id='P1'" in msg
    assert "Accepted registry ids" in msg
    assert "violino" in msg
    for iid in list_instrument_ids():
        assert iid in msg


def test_analyze_score_unmapped_part_aborts_whole_score(tmp_path):
    path = tmp_path / "unmapped_part.musicxml"
    path.write_text(_unmapped_part_xml(), encoding="utf-8")
    with pytest.raises(InputError, match="Violin I") as exc:
        analyze_score(str(path))
    msg = str(exc.value)
    assert "part_id='P1'" in msg
    assert "Accepted registry ids" in msg


def test_gui_adapter_rejects_unrecognised_dropdown_state():
    raw = {
        "notes": ["C4"],
        "dynamics": ["mf"],
        "instruments": [UNPITCHED_INSTRUMENT_GROUP_LABEL],
        "num_instruments": [1],
    }
    with pytest.raises(InputError, match="Accepted registry ids"):
        build_analysis_request(raw)
    with pytest.raises(InputError, match="Unknown instrument"):
        calculate_from_gui_request(
            {
                "notes": ["C4"],
                "dynamics": ["mf"],
                "instruments": ["violoncelo_sul_tasto"],
                "num_instruments": [1],
            }
        )
