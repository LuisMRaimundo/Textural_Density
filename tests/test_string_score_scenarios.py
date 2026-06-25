"""Integrated score scenarios for string ensemble textural-density contracts."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from microtonal import note_to_midi

from core.pipeline import calculate_metrics
from data_processor import calculate_metrics as dp_calculate_metrics
from xml_loader import parse_xml, parse_xml_to_events


def _slice(
    notes: list[str],
    *,
    dynamics: list[str] | None = None,
    instruments: list[str] | None = None,
    nums: list[int] | None = None,
):
    n = len(notes)
    return {
        "notes": notes,
        "dynamics": dynamics or ["mf"] * n,
        "instruments": instruments or ["violino"] * n,
        "num_instruments": nums or [1] * n,
        "weight_factor": 0.5,
    }


def _metrics(**kwargs) -> dict:
    resultados, _, _ = calculate_metrics(_slice(**kwargs))
    return resultados


@pytest.mark.musicological
class TestStringVerticalSliceScenarios:
    def test_single_string_note(self):
        r = _metrics(notes=["G4"], instruments=["violin"])
        assert r["pitch_aggregation"]["event_count"] == 1
        assert r["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert float(r["density"]["instrument"]) > 0.0

    def test_two_strings_same_pitch(self):
        r = _metrics(notes=["G4", "G4"], instruments=["violin", "viola"])
        assert r["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert r["pitch_aggregation"]["event_count"] == 2

    def test_string_quartet_unison(self):
        r = _metrics(
            notes=["G3", "G3", "G3", "G3"],
            instruments=["violino", "viola", "violoncelo", "contrabaixo"],
        )
        assert r["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert r["pitch_aggregation"]["event_count"] == 4

    def test_octave_doubling_creates_distinct_bins(self):
        r = _metrics(notes=["G3", "G4"], instruments=["violino", "violino"])
        assert r["pitch_aggregation"]["distinct_pitch_count"] == 2

    def test_string_quartet_chord(self):
        r = _metrics(
            notes=["C4", "G3", "E4", "C3"],
            instruments=["violino", "viola", "violoncelo", "contrabaixo"],
        )
        assert r["pitch_aggregation"]["distinct_pitch_count"] == 4

    def test_event_order_permutation_invariant_pitch_structure(self):
        a = _metrics(
            notes=["C4", "E4", "G4"],
            instruments=["violino", "viola", "violoncelo"],
        )
        b = _metrics(
            notes=["G4", "C4", "E4"],
            instruments=["violoncelo", "violino", "viola"],
        )
        assert a["density"]["pitch_structure"] == pytest.approx(b["density"]["pitch_structure"])
        assert a["pitch_aggregation"]["distinct_pitch_count"] == b["pitch_aggregation"]["distinct_pitch_count"]

    def test_qty_row_splitting_equivalence(self):
        one_row = _metrics(notes=["G4"], instruments=["violin"], nums=[4])
        split = _metrics(
            notes=["G4", "G4", "G4", "G4"],
            instruments=["violin"] * 4,
            nums=[1, 1, 1, 1],
        )
        assert one_row["density"]["sonic_mass"] == pytest.approx(split["density"]["sonic_mass"])
        assert one_row["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert split["pitch_aggregation"]["distinct_pitch_count"] == 1

    def test_qty_does_not_create_pitch_polyphony(self):
        r = _metrics(notes=["A4"], instruments=["violin"], nums=[8])
        assert r["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert r["pitch_aggregation"]["player_count"] == 8

    def test_changing_instrument_assignment_may_change_instrument_density(self):
        violins = _metrics(notes=["G4", "G4"], instruments=["violin", "violin"])
        mixed = _metrics(notes=["G4", "G4"], instruments=["violin", "cello"])
        assert mixed["density"]["instrument"] != pytest.approx(violins["density"]["instrument"])

    def test_microtonal_string_simultaneity_finite(self):
        r = _metrics(
            notes=["G4+25c", "G4+75c"],
            instruments=["violin", "viola"],
        )
        assert r["pitch_aggregation"]["distinct_pitch_count"] == 2
        assert float(r["density"]["instrument"]) > 0.0


@pytest.mark.musicological
class TestDoubleBassSoundingPitchMusicXml:
    """MusicXML: double-bass written pitch transposed to sounding pitch before lookup."""

    _DB_XML = """<?xml version="1.0"?>
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".musicxml", delete=False) as f:
            f.write(self._DB_XML)
            path = f.name
        try:
            data = parse_xml(path)
            assert note_to_midi(data["notes"][0]) == pytest.approx(note_to_midi("C2"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_events_use_sounding_pitch_with_written_split(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".musicxml", delete=False) as f:
            f.write(self._DB_XML)
            path = f.name
        try:
            events, _, warnings = parse_xml_to_events(path)
            assert len(events) == 1
            ev = events[0]
            assert ev.written_pitch is not None
            assert ev.sounding_pitch.note_name == "C2"
            assert any("concert pitch" in w.lower() for w in warnings)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_pipeline_lookup_uses_sounding_pitch_for_contrabaixo(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".musicxml", delete=False) as f:
            f.write(self._DB_XML)
            path = f.name
        try:
            data = parse_xml(path)
            resultados, densities, _ = dp_calculate_metrics(
                {
                    **data,
                    "dynamics": ["mf"],
                    "instruments": ["contrabaixo"],
                    "num_instruments": [1],
                    "weight_factor": 0.5,
                }
            )
            assert float(resultados["density"]["instrument"]) > 0.0
            assert len(densities) == 1
            assert densities[0] > 0.0
        finally:
            Path(path).unlink(missing_ok=True)
