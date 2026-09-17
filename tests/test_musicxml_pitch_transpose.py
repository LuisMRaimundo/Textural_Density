"""MusicXML written MIDI and concert-pitch transpose (strict, no C4 fallback)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from error_handler import InputError
from microtonal import note_to_midi_strict
from xml_loader import (
    apply_written_midi_transpose,
    musicxml_written_midi,
    parse_musicxml_written_pitch,
    parse_xml,
    parse_xml_to_events,
)

# Independent of xml_loader internals: MusicXML step/octave/alter → MIDI.
_STEP_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _independent_midi(step: str, octave: int, alter: float = 0.0) -> float:
    return float((octave + 1) * 12 + _STEP_PC[step] + alter)


def _write(xml: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".musicxml", delete=False) as handle:
        handle.write(xml)
        return handle.name


def _pitch_el(step: str, octave: str, alter: str | None = None):
    alter_xml = f"<alter>{alter}</alter>" if alter is not None else ""
    return ET.fromstring(
        f"<pitch><step>{step}</step>{alter_xml}<octave>{octave}</octave></pitch>"
    )


def _score(part_name: str, attributes: str, notes: str) -> str:
    return f"""<?xml version="1.0"?>
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>{part_name}</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes>{attributes}</attributes>
      {notes}
    </measure>
  </part>
</score-partwise>"""


class TestWrittenMidiIndependent:
    def test_cb5_is_71_before_transposition(self):
        expected = _independent_midi("C", 5, -1.0)
        assert expected == 71.0
        assert musicxml_written_midi("C", 5, -1.0) == pytest.approx(expected)
        parsed = parse_musicxml_written_pitch(_pitch_el("C", "5", "-1"))
        assert parsed.written_midi == pytest.approx(71.0)
        assert note_to_midi_strict("Cb5") == pytest.approx(71.0)

    def test_b_sharp_crosses_octave_boundary(self):
        expected = _independent_midi("B", 3, 1.0)
        assert expected == 60.0
        assert musicxml_written_midi("B", 3, 1.0) == pytest.approx(expected)
        assert parse_musicxml_written_pitch(_pitch_el("B", "3", "1")).written_midi == pytest.approx(60.0)

    def test_double_sharp_and_double_flat(self):
        css = _independent_midi("C", 4, 2.0)
        cbb = _independent_midi("C", 4, -2.0)
        assert css == 62.0
        assert cbb == 58.0
        assert musicxml_written_midi("C", 4, 2.0) == pytest.approx(css)
        assert musicxml_written_midi("C", 4, -2.0) == pytest.approx(cbb)


class TestTransposeHelpers:
    def test_zero_transpose_preserves_parseable_cb5(self):
        sounding = apply_written_midi_transpose(71.0, 0.0, "Cb5")
        assert note_to_midi_strict(sounding) == pytest.approx(71.0)

    def test_positive_and_negative_chromatic(self):
        up = apply_written_midi_transpose(60.0, 2.0, "C4")
        down = apply_written_midi_transpose(60.0, -2.0, "C4")
        assert note_to_midi_strict(up) == pytest.approx(_independent_midi("C", 4) + 2)
        assert note_to_midi_strict(down) == pytest.approx(_independent_midi("C", 4) - 2)

    def test_invalid_written_string_does_not_become_c4(self):
        from xml_loader import _apply_semitone_transpose

        with pytest.raises(InputError):
            _apply_semitone_transpose("H4", 2)
        with pytest.raises(InputError):
            parse_musicxml_written_pitch(_pitch_el("H", "4"))
        with pytest.raises(InputError):
            parse_musicxml_written_pitch(_pitch_el("C", "x"))
        with pytest.raises(InputError):
            parse_musicxml_written_pitch(_pitch_el("C", "4", "not-a-number"))


class TestEndToEndMusicXml:
    def test_cb5_transposed_down_a_tone(self):
        xml = _score(
            "Flute",
            "<transpose><chromatic>-2</chromatic></transpose>",
            "<note><pitch><step>C</step><alter>-1</alter><octave>5</octave></pitch><duration>1</duration></note>",
        )
        path = _write(xml)
        try:
            data = parse_xml(path)
            expected = _independent_midi("C", 5, -1.0) - 2.0
            assert note_to_midi_strict(data["notes"][0]) == pytest.approx(expected)
            assert expected == 69.0
        finally:
            Path(path).unlink(missing_ok=True)

    def test_octave_change_only(self):
        xml = _score(
            "Contrabass",
            "<transpose><chromatic>0</chromatic><octave-change>-1</octave-change></transpose>",
            "<note><pitch><step>C</step><octave>3</octave></pitch><duration>1</duration></note>",
        )
        path = _write(xml)
        try:
            data = parse_xml(path)
            expected = _independent_midi("C", 3) - 12.0
            assert note_to_midi_strict(data["notes"][0]) == pytest.approx(expected)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_no_transpose_ordinary_c4(self):
        xml = _score(
            "Flute",
            "<divisions>1</divisions>",
            "<note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note>",
        )
        path = _write(xml)
        try:
            data = parse_xml(path)
            assert data["notes"][0] == "C4"
            assert note_to_midi_strict(data["notes"][0]) == pytest.approx(60.0)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_double_sharp_end_to_end(self):
        xml = _score(
            "Flute",
            "<transpose><chromatic>0</chromatic></transpose>",
            "<note><pitch><step>C</step><alter>2</alter><octave>4</octave></pitch><duration>1</duration></note>",
        )
        path = _write(xml)
        try:
            data = parse_xml(path)
            assert note_to_midi_strict(data["notes"][0]) == pytest.approx(62.0)
            events, _, _ = parse_xml_to_events(path)
            assert events[0].sounding_pitch.midi == pytest.approx(62.0)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_fractional_octave_change_raises(self):
        xml = _score(
            "Flute",
            "<transpose><chromatic>0</chromatic><octave-change>0.5</octave-change></transpose>",
            "<note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note>",
        )
        path = _write(xml)
        try:
            with pytest.raises(InputError):
                parse_xml(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_bb_clarinet_c4_still_bb3(self):
        xml = _score(
            "Clarinet",
            "<transpose><chromatic>-2</chromatic></transpose>",
            "<note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note>",
        )
        path = _write(xml)
        try:
            data = parse_xml(path)
            assert note_to_midi_strict(data["notes"][0]) == pytest.approx(
                _independent_midi("B", 3, -1.0)
            )
        finally:
            Path(path).unlink(missing_ok=True)
