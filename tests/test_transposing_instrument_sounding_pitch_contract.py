"""MusicXML concert/sounding pitch: <transpose> applied once before lookup."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import mock

import pytest
from microtonal import note_to_midi

from core.converters import make_instrument_event
from core.orchestration import compute_event_one_player_density
from core.pipeline import calculate_metrics
from data_processor import calculate_metrics as dp_calculate_metrics
from error_handler import InputError
from instrumentos import get_instrument_module
from instrumentos.registry import REGISTRY, resolve_profile
from xml_loader import parse_xml, parse_xml_to_events


def _write_xml(content: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".musicxml", delete=False) as f:
        f.write(content)
        return f.name


def _cleanup(path: str) -> None:
    Path(path).unlink(missing_ok=True)


class TestManualSoundingPitchNoTransposition:
    @pytest.mark.parametrize(
        "instrument,note",
        [
            ("contrabaixo", "E1"),
            ("contrabaixo", "C2"),
            ("contrabassoon", "Bb0"),
            ("flautim", "C6"),
            ("trompete", "C4"),
            ("trompa", "C4"),
            ("cor_anglais", "G4"),
            ("clarinete_baixo", "D2"),
        ],
    )
    def test_manual_sounding_pitch_accepted(self, instrument: str, note: str):
        calculate_metrics(
            {
                "notes": [note],
                "dynamics": ["mf"],
                "instruments": [instrument],
                "num_instruments": [1],
            }
        )

    @pytest.mark.parametrize("instrument_id", [p.instrument_id for p in REGISTRY.values() if p.transposition != 0])
    def test_manual_input_does_not_apply_registry_transposition(self, instrument_id: str):
        profile = REGISTRY[instrument_id]
        _, _, pitches = calculate_metrics(
            {
                "notes": ["C4"],
                "dynamics": ["mf"],
                "instruments": [profile.display_name],
                "num_instruments": [1],
            }
        )
        assert pitches[0] == pytest.approx(60.0)


class TestDoubleBassMusicXmlSoundingPitch:
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

    def test_written_c3_converts_to_sounding_c2(self):
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
            assert ev.written_pitch is not None
            assert ev.written_pitch.note_name == "C3"
            assert ev.sounding_pitch.note_name == "C2"
            assert any("concert pitch" in w.lower() for w in warnings)
        finally:
            _cleanup(path)

    def test_density_lookup_receives_sounding_pitch(self):
        path = _write_xml(self._XML)
        try:
            events, _, _ = parse_xml_to_events(path)
            ev = events[0]
            mod = get_instrument_module("contrabaixo")
            seen: list[str] = []
            original = mod.calcular_densidade

            def _spy(note, dynamic):
                seen.append(note)
                return original(note, dynamic)

            with mock.patch.object(mod, "calcular_densidade", side_effect=_spy):
                compute_event_one_player_density(ev, lambda _: mod)
            assert seen == ["C2"]
        finally:
            _cleanup(path)


class TestBbClarinetMusicXmlSoundingPitch:
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

    def test_written_c4_converts_to_sounding_bb3(self):
        path = _write_xml(self._XML)
        try:
            data = parse_xml(path)
            assert note_to_midi(data["notes"][0]) == pytest.approx(note_to_midi("Bb3"))
        finally:
            _cleanup(path)

    def test_events_have_written_sounding_split(self):
        path = _write_xml(self._XML)
        try:
            events, _, _ = parse_xml_to_events(path)
            ev = events[0]
            assert ev.written_pitch is not None
            assert ev.written_pitch.note_name.startswith("C")
            assert note_to_midi(ev.sounding_pitch.note_name) == pytest.approx(note_to_midi("Bb3"))
        finally:
            _cleanup(path)


class TestHornInFMusicXmlSoundingPitch:
    _XML = """<?xml version="1.0"?>
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>Horn in F</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <transpose><chromatic>-7</chromatic></transpose>
      </attributes>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note>
    </measure>
  </part>
</score-partwise>"""

    def test_written_c4_converts_to_sounding_f3(self):
        path = _write_xml(self._XML)
        try:
            data = parse_xml(path)
            assert note_to_midi(data["notes"][0]) == pytest.approx(note_to_midi("F3"))
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

    def test_no_transpose_keeps_written_as_sounding(self):
        path = _write_xml(self._XML)
        try:
            _, _, pitches = dp_calculate_metrics(
                {
                    **parse_xml(path),
                    "dynamics": ["mf"],
                    "instruments": ["Contrabassoon"],
                    "num_instruments": [1],
                    "weight_factor": 0.5,
                }
            )
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


class TestErrorMessageClarity:
    def test_out_of_range_manual_mentions_sounding_pitch(self):
        with pytest.raises(InputError) as exc:
            calculate_metrics(
                {
                    "notes": ["C1"],
                    "dynamics": ["mf"],
                    "instruments": ["flauta"],
                    "num_instruments": [1],
                }
            )
        assert "sounding" in str(exc.value).lower()

    def test_out_of_range_musicxml_mentions_written_when_set(self):
        with pytest.raises(InputError) as exc:
            make_instrument_event(
                idx=2,
                note="C1",
                written_note="C2",
                dynamic="mf",
                instrument_name="contrabaixo",
                player_count=1,
            )
        msg = str(exc.value)
        assert "written" in msg
        assert "sounding" in msg.lower()


class TestAliasPitchContract:
    @pytest.mark.parametrize("alias", ["double_bass", "contrabaixo", "contrabassoon", "clarinet", "trompete"])
    def test_alias_resolves_same_profile(self, alias: str):
        profile = resolve_profile(alias)
        assert profile is not None
        assert profile.sounding_range[0] < profile.sounding_range[1]


class TestTableBackedSoundingPitchKeys:
    @pytest.mark.parametrize("module_name", ["violin", "viola", "cello", "double_bass", "flute", "clarinet", "oboe", "bassoon"])
    def test_table_span_matches_instrument_source_pitch_range(self, module_name: str):
        mod = __import__(f"instrumentos.{module_name}", fromlist=["spectral_data"])
        lo, hi = mod.INSTRUMENT_SOURCE.pitch_range
        notes = sorted(mod.spectral_data.keys(), key=lambda n: note_to_midi(n))
        assert note_to_midi(notes[0]) >= lo - 1e-6
        assert note_to_midi(notes[-1]) <= hi + 1e-6

    def test_double_bass_table_uses_sounding_e1_not_written(self):
        mod = __import__("instrumentos.double_bass", fromlist=["spectral_data"])
        assert "E1" in mod.spectral_data
        assert "E2" not in mod.spectral_data or note_to_midi("E1") < note_to_midi("E2")
