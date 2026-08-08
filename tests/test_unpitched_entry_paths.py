"""Task 6: unpitched entry paths (GUI adapter, MusicXML, MIDI)."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.gui_adapter import build_analysis_request
from core.converters import legacy_input_to_vertical_slice, make_instrument_event
from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from core.unpitched_routing import (
    UNPITCHED_INSTRUMENT_GROUP_LABEL,
    canonical_unpitched_note,
)
from error_handler import InputError
from gui.state import INSTRUMENT_DROPDOWN_VALUES, INSTRUMENTS
from midi_loader import parse_midi_to_events
from xml_loader import parse_xml_to_events


def test_dropdown_groups_unpitched_percussion():
    assert UNPITCHED_INSTRUMENT_GROUP_LABEL in INSTRUMENT_DROPDOWN_VALUES
    idx = INSTRUMENT_DROPDOWN_VALUES.index(UNPITCHED_INSTRUMENT_GROUP_LABEL)
    after = INSTRUMENT_DROPDOWN_VALUES[idx + 1 :]
    for name in ("Bass drum", "Cymbals", "Tam-tam", "Gong"):
        assert name in INSTRUMENTS
        assert name in after


def test_gui_adapter_injects_canonical_placeholder_despite_stale_note():
    stale = "C4"
    req = build_analysis_request(
        {
            "notes": [stale],
            "dynamics": ["mf"],
            "instruments": ["Cymbals"],
            "num_instruments": [1],
        }
    )
    expected = canonical_unpitched_note("Cymbals")
    assert expected == "C5"
    assert req.notes[0] == expected
    assert req.notes[0] != stale
    slice_ = legacy_input_to_vertical_slice(req.to_pipeline_dict())
    assert slice_.events[0].unpitched is True
    assert slice_.events[0].sounding_pitch.note_name == expected


def test_cents_entry_for_tamtam_is_rejected():
    with pytest.raises(InputError, match="does not accept"):
        build_analysis_request(
            {
                "notes": ["C2+10c"],
                "dynamics": ["mf"],
                "instruments": ["Tam-tam"],
                "num_instruments": [1],
            }
        )
    with pytest.raises(InputError, match="does not accept"):
        make_instrument_event(
            idx=0,
            note="C2+25c",
            dynamic="mf",
            instrument_name="Tam-tam",
            player_count=1,
        )


def test_musicxml_violin_plus_unpitched_cymbal_pitch_metrics(tmp_path: Path):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC
  "-//Recordare//DTD MusicXML 3.1 Partwise//EN"
  "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>Violin</part-name></score-part>
    <score-part id="P2"><part-name>Cymbals</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>1</duration><voice>1</voice><type>quarter</type>
      </note>
    </measure>
  </part>
  <part id="P2">
    <measure number="1">
      <note>
        <unpitched>
          <display-step>E</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>1</duration><voice>1</voice><type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""
    path = tmp_path / "violin_cymbal.xml"
    path.write_text(xml, encoding="utf-8")
    events, _opts, warnings = parse_xml_to_events(str(path))
    assert len(events) == 2
    cym = next(e for e in events if e.instrument_id == "pratos")
    assert cym.unpitched is True
    assert cym.sounding_pitch.note_name == canonical_unpitched_note("Cymbals")
    # display-step E5 must NOT become the lookup key
    assert cym.sounding_pitch.note_name != "E5"

    violin_only = calculate_metrics(
        AnalysisRequest(
            notes=("C4",),
            dynamics=("mf",),
            instruments=("Violin",),
            num_instruments=(1,),
        )
    )[0]
    both = calculate_metrics(
        AnalysisRequest(
            notes=tuple(e.sounding_pitch.note_name for e in events),
            dynamics=tuple(e.dynamic or "mf" for e in events),
            instruments=tuple(e.instrument_name for e in events),
            num_instruments=(1, 1),
        )
    )[0]
    assert both["density"]["interval"] == pytest.approx(violin_only["density"]["interval"])
    assert both["density"]["pitch_structure"] == pytest.approx(
        violin_only["density"]["pitch_structure"]
    )
    assert both["pitch_aggregation"]["distinct_pitch_count"] == 1


def test_midi_channel10_bass_drum_maps_unpitched(tmp_path: Path):
    mido = pytest.importorskip("mido")
    path = tmp_path / "kick.mid"
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    # Channel 10 = index 9; GM key 36 = Bass Drum 1
    track.append(mido.Message("note_on", note=36, velocity=80, channel=9, time=0))
    track.append(mido.Message("note_off", note=36, velocity=0, channel=9, time=480))
    mid.save(path)

    events, _opts, warnings = parse_midi_to_events(str(path))
    assert len(events) == 1
    evt = events[0]
    assert evt.instrument_id == "bombo"
    assert evt.unpitched is True
    assert evt.sounding_pitch.note_name == canonical_unpitched_note("Bass drum")
    assert evt.sounding_pitch.note_name == "D2"


def test_midi_unmapped_channel10_key_skipped(tmp_path: Path):
    mido = pytest.importorskip("mido")
    path = tmp_path / "skip.mid"
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.Message("note_on", note=54, velocity=80, channel=9, time=0))
    track.append(mido.Message("note_off", note=54, velocity=0, channel=9, time=480))
    # Also a mappable kick so the file is not empty after skip
    track.append(mido.Message("note_on", note=36, velocity=80, channel=9, time=0))
    track.append(mido.Message("note_off", note=36, velocity=0, channel=9, time=480))
    mid.save(path)

    events, _opts, warnings = parse_midi_to_events(str(path))
    assert len(events) == 1
    assert any("unmappable MIDI channel-10 key 54" in w for w in warnings)
