"""MusicXML concert/sounding pitch: <transpose> applied once before lookup."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from microtonal import note_to_midi

from data_processor import calculate_metrics as dp_calculate_metrics
from error_handler import InputError
from xml_loader import parse_xml, parse_xml_to_events


def _write_xml(content: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".musicxml", delete=False) as f:
        f.write(content)
        return f.name


def _cleanup(path: str) -> None:
    Path(path).unlink(missing_ok=True)


class TestDoubleBassSoundingPitch:
    _XML = """<?xml version="1.0"?>
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>Contrabass</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <transpose><chromatic>0</chromatic><octave-change>-1</octave-change></transpose>
      </attributes>
      <note><pitch><step>C</step><octave>3</octave></pitch><duration>1</duration></note>
    </measure>
  </part>
</score-partwise>"""

    def test_parse_xml_converts_written_c3_to_sounding_c2(self):
        path = _write_xml(self._XML)
        try:
            data = parse_xml(path)
            assert note_to_midi(data["notes"][0]) == pytest.approx(note_to_midi("C2"))
        finally:
            _cleanup(path)

    def test_events_split_written_and_sounding(self):
        path = _write_xml(self._XML)
        try:
            events, _, warnings = parse_xml_to_events(path)
            ev = events[0]
            assert ev.sounding_pitch.note_name == "C2"
            assert ev.written_pitch is not None
            assert ev.written_pitch.note_name == "C3"
            assert any("concert pitch" in w.lower() for w in warnings)
        finally:
            _cleanup(path)

    def test_pipeline_accepts_sounding_pitch_for_contrabaixo(self):
        path = _write_xml(self._XML)
        try:
            data = parse_xml(path)
            data["dynamics"] = ["mf"]
            data["instruments"] = ["contrabaixo"]
            data["num_instruments"] = [1]
            data["weight_factor"] = 0.5
            resultados, _, _ = dp_calculate_metrics(data)
            assert float(resultados["density"]["instrument"]) > 0.0
        finally:
            _cleanup(path)


class TestBbClarinetSoundingPitch:
    _XML = """<?xml version="1.0"?>
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>Clarinet</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <transpose><chromatic>-2</chromatic></transpose>
      </attributes>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note>
    </measure>
  </part>
</score-partwise>"""

    def test_written_c4_transposed_to_sounding_bb3(self):
        path = _write_xml(self._XML)
        try:
            data = parse_xml(path)
            assert note_to_midi(data["notes"][0]) == pytest.approx(note_to_midi("Bb3"))
        finally:
            _cleanup(path)

    def test_events_have_written_sounding_split(self):
        path = _write_xml(self._XML)
        try:
            events, _, warnings = parse_xml_to_events(path)
            ev = events[0]
            assert ev.written_pitch is not None
            assert note_to_midi(ev.sounding_pitch.note_name) == pytest.approx(note_to_midi("Bb3"))
            assert any("concert pitch" in w.lower() for w in warnings)
        finally:
            _cleanup(path)


class TestContrabassoonMusicXmlSoundingPitch:
    _XML = """<?xml version="1.0"?>
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>Contrabassoon</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>1</divisions></attributes>
      <note><pitch><step>G</step><octave>4</octave></pitch><duration>1</duration></note>
    </measure>
  </part>
</score-partwise>"""

    def test_g4_sounding_accepted(self):
        path = _write_xml(self._XML)
        try:
            data = parse_xml(path)
            data["dynamics"] = ["mf"]
            data["instruments"] = ["Contrabassoon"]
            data["num_instruments"] = [1]
            data["weight_factor"] = 0.5
            _, _, pitches = dp_calculate_metrics(data)
            assert pitches[0] == pytest.approx(67.0)
        finally:
            _cleanup(path)

    def test_contrabassoon_g6_sounding_rejected(self):
        xml = self._XML.replace("<octave>4</octave>", "<octave>6</octave>")
        path = _write_xml(xml)
        try:
            data = parse_xml(path)
            data["dynamics"] = ["mf"]
            data["instruments"] = ["contrabassoon"]
            data["num_instruments"] = [1]
            with pytest.raises(InputError, match="outside the range"):
                dp_calculate_metrics(data)
        finally:
            _cleanup(path)
