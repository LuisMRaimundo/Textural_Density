"""F-I — Temporal analysis and score input (HARD/SOFT; §O–§P)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from core.converters import make_instrument_event
from core.pipeline import calculate_metrics
from core.score_analysis import analyze_score
from core.temporal import event_is_active_at, group_events_into_slices, summarize_time_series
from error_handler import InputError
from microtonal import note_to_midi_strict
from tests.plausibility.conftest import record_hard, record_soft
from tests.plausibility.helpers import assert_jsonable, slice_input
from xml_loader import _transpose_semitones_from_attributes, parse_xml


def _part_xml(part_id: str, name: str, chromatic: int, octave_change: int, step: str, octave: int) -> str:
    return f"""  <score-part id="{part_id}"><part-name>{name}</part-name></score-part>"""


def _score(parts: list[tuple]) -> str:
    """parts: (id, name, chromatic, octave_change, step, octave, instrument hint unused)."""
    plist = "\n".join(
        f'    <score-part id="{p[0]}"><part-name>{p[1]}</part-name></score-part>' for p in parts
    )
    bodies = []
    for pid, name, chrom, octc, step, octv, _inst in parts:
        bodies.append(
            f"""  <part id="{pid}">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <transpose><chromatic>{chrom}</chromatic><octave-change>{octc}</octave-change></transpose>
      </attributes>
      <note><pitch><step>{step}</step><octave>{octv}</octave></pitch><duration>1</duration></note>
    </measure>
  </part>"""
        )
    return (
        '<?xml version="1.0"?>\n<score-partwise version="3.1">\n  <part-list>\n'
        + plist
        + "\n  </part-list>\n"
        + "\n".join(bodies)
        + "\n</score-partwise>\n"
    )


class TestFIHalfOpen:
    def test_note_ending_at_t_is_inactive(self):
        """HARD: activity is half-open [onset, offset); inactive at exact offset."""
        ev = make_instrument_event(
            idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=1,
            onset=0.0, offset=1.0, duration=1.0,
        )
        assert event_is_active_at(ev, 0.0) is True
        assert event_is_active_at(ev, 0.999) is True
        assert event_is_active_at(ev, 1.0) is False
        record_hard(family="F-I", test_id="FI.half_open")

    def test_staggered_onsets_slice_count(self):
        """HARD: staggered onsets produce the documented slice boundaries."""
        events = []
        specs = [("C4", 0.0, 2.0), ("E4", 1.0, 3.0), ("G4", 2.0, 3.0)]
        for i, (note, on, off) in enumerate(specs):
            events.append(
                make_instrument_event(
                    idx=i, note=note, dynamic="mf", instrument_name="flauta", player_count=1,
                    onset=on, offset=off, duration=off - on,
                )
            )
        slices = group_events_into_slices(events, mode="event_boundary")
        record_hard(
            family="F-I",
            test_id="FI.staggered",
            n_slices=len(slices),
            bounds=[(s.onset, s.offset) if hasattr(s, "onset") else str(s) for s in slices],
        )
        assert len(slices) >= 2


class TestFIMusicXMLTranspose:
    @pytest.mark.parametrize(
        "name,chrom,octc,step,octv,sounding,semitones",
        [
            ("Clarinet", -2, 0, "C", 4, "Bb3", -2),
            ("Horn", -7, 0, "C", 4, "F3", -7),
            ("Contrabass", 0, -1, "C", 3, "C2", -12),
            ("Piccolo", 0, 1, "C", 5, "C6", 12),
        ],
    )
    def test_written_to_sounding(self, name, chrom, octc, step, octv, sounding, semitones):
        """HARD: MusicXML <transpose> converts written→sounding; helper matches chromatic+12·oct."""
        xml = _score([("P1", name, chrom, octc, step, octv, name)])
        path = Path(tempfile.mkstemp(suffix=".musicxml")[1])
        path.write_text(xml, encoding="utf-8")
        try:
            root = ET.parse(path).getroot()
            attrs = root.find(".//attributes")
            got = _transpose_semitones_from_attributes(attrs)
            assert got == semitones
            data = parse_xml(str(path))
            assert note_to_midi_strict(data["notes"][0]) == pytest.approx(note_to_midi_strict(sounding))
            analysis = analyze_score(str(path))
            record_hard(
                family="F-I",
                test_id=f"FI.xml.{name}",
                written=f"{step}{octv}",
                sounding=sounding,
                helper=got,
                parsed=data["notes"][0],
                n_slices=len(getattr(analysis, "slices", []) or []),
            )
        finally:
            try:
                path.unlink(missing_ok=True)
            except PermissionError:
                pass


class TestFIUnpitched:
    def test_unpitched_in_mass_not_pitch(self):
        """HARD: unpitched percussion contributes to players/mass, not pitch metrics."""
        r, _, _ = calculate_metrics(
            {
                "notes": ["C4", "C4"],
                "dynamics": ["mf", "ff"],
                "instruments": ["flauta", "tamtam"],
                "num_instruments": [1, 1],
            }
        )
        assert_jsonable(r, label="FI.unpitched")
        assert r["pitch_aggregation"]["pitched_event_count"] == 1
        assert r["density"]["interval"] == 0
        record_hard(
            family="F-I",
            test_id="FI.unpitched",
            players=r["pitch_aggregation"]["player_count"],
            mass=r["density"]["sonic_mass"],
            interval=r["density"]["interval"],
        )

    def test_microtonal_on_unpitched_raises(self):
        """HARD: microtonal spellings on unpitched parts raise InputError."""
        with pytest.raises(InputError):
            calculate_metrics(slice_input(["C4+50c"], instruments="bombo"))
        record_hard(family="F-I", test_id="FI.unpitched.microtonal")


class TestFISoftStaccato:
    @pytest.mark.plausibility
    @pytest.mark.xfail(strict=False, reason="SOFT plausibility")
    def test_sustained_vs_staccato_timeseries(self):
        """SOFT: tutti sustained vs staccato gaps — report summarize_time_series."""
        sustained = []
        staccato = []
        for i, note in enumerate(["C4", "E4", "G4"]):
            sustained.append(
                make_instrument_event(
                    idx=i, note=note, dynamic="mf", instrument_name="violino", player_count=1,
                    onset=0.0, offset=4.0, duration=4.0,
                )
            )
            staccato.append(
                make_instrument_event(
                    idx=i + 10, note=note, dynamic="mf", instrument_name="violino", player_count=1,
                    onset=float(i), offset=float(i) + 0.2, duration=0.2,
                )
            )
        a = analyze_score(sustained)
        b = analyze_score(staccato)
        sa = summarize_time_series(getattr(a, "time_series", []) or [])
        sb = summarize_time_series(getattr(b, "time_series", []) or [])
        record_soft(
            family="F-I",
            test_id="FI.soft.sustain_vs_staccato",
            met=True,
            expectation="report time-series mean/variance for sustained tutti vs gapped staccato",
            sustained=sa if isinstance(sa, dict) else str(sa),
            staccato=sb if isinstance(sb, dict) else str(sb),
        )
