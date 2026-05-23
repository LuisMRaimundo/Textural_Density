"""
Phase 6: temporal score analysis tests.
"""

from __future__ import annotations

import pytest

from core.converters import make_instrument_event
from core.models import InstrumentEvent
from core.score_analysis import analyze_score
from core.temporal import group_events_into_slices
from data_processor import calculate_metrics


@pytest.fixture
def baseline_input_data():
    return {
        "notes": ["C4", "E4", "G4", "C5"],
        "dynamics": ["mf", "f", "ff", "mf"],
        "instruments": ["flauta", "clarinete", "flauta", "clarinete"],
        "num_instruments": [1, 2, 1, 1],
        "weight_factor": 0.5,
        "save_results": False,
        "show_graphs": False,
    }


@pytest.fixture
def timed_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<densidade_analysis>
  <settings>
    <weight_factor>0.5</weight_factor>
    <calculate_combination_tones>false</calculate_combination_tones>
  </settings>
  <voices>
    <voice>
      <note>C4</note><dynamics>mf</dynamics><instrument>flauta</instrument>
      <num_instruments>1</num_instruments><onset>0.0</onset><duration>2.0</duration>
    </voice>
    <voice>
      <note>E4</note><dynamics>f</dynamics><instrument>clarinete</instrument>
      <num_instruments>1</num_instruments><onset>1.0</onset><duration>1.0</duration>
    </voice>
  </voices>
</densidade_analysis>
"""
    path = tmp_path / "timed_score.xml"
    path.write_text(content, encoding="utf-8")
    return path


class TestGroupEventsIntoSlices:
    def test_untimed_events_single_slice(self):
        events = [
            make_instrument_event(
                idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=1
            ),
            make_instrument_event(
                idx=1, note="E4", dynamic="f", instrument_name="clarinete", player_count=1
            ),
        ]
        slices = group_events_into_slices(events)
        assert len(slices) == 1
        assert len(slices[0].events) == 2

    def test_timed_events_create_multiple_slices(self):
        events = [
            make_instrument_event(
                idx=0,
                note="C4",
                dynamic="mf",
                instrument_name="flauta",
                player_count=1,
                onset=0.0,
                duration=2.0,
            ),
            make_instrument_event(
                idx=1,
                note="E4",
                dynamic="f",
                instrument_name="clarinete",
                player_count=1,
                onset=1.0,
                duration=1.0,
            ),
        ]
        slices = group_events_into_slices(events)
        assert len(slices) == 2
        assert slices[0].time == pytest.approx(0.0)
        assert len(slices[0].events) == 1
        assert slices[1].time == pytest.approx(1.0)
        assert len(slices[1].events) == 2


class TestAnalyzeScore:
    def test_legacy_dict_single_slice(self, baseline_input_data):
        result = analyze_score(baseline_input_data)
        assert len(result.slices) == 1
        assert result.time_series is not None
        assert len(result.time_series) == 1
        assert "slice_count" in result.global_summary

    def test_timed_xml_multiple_slices(self, timed_xml):
        result = analyze_score(str(timed_xml))
        assert len(result.slices) == 2
        assert len(result.time_series) == 2
        assert result.time_series[0]["event_count"] == 1
        assert result.time_series[1]["event_count"] == 2
        assert result.global_summary["density_total_max"].value >= result.global_summary[
            "density_total_min"
        ].value

    def test_global_summary_slice_count(self, timed_xml):
        result = analyze_score(str(timed_xml))
        assert float(result.global_summary["slice_count"].value) == 2.0

    def test_midi_warnings_present(self, tmp_path):
        mido = pytest.importorskip("mido")
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
        track.append(mido.Message("note_on", note=60, velocity=80, time=0))
        track.append(mido.Message("note_off", note=60, velocity=0, time=480))
        track.append(mido.Message("note_on", note=64, velocity=90, time=0))
        track.append(mido.Message("note_off", note=64, velocity=0, time=480))
        midi_path = tmp_path / "test.mid"
        mid.save(str(midi_path))

        result = analyze_score(str(midi_path))
        assert len(result.slices) >= 1
        assert any("MIDI" in w for w in result.warnings)

    def test_slice_metrics_finite(self, timed_xml):
        result = analyze_score(str(timed_xml))
        for slice_analysis in result.slices:
            total = slice_analysis.composite_density.value
            assert float(total) >= 0.0


class TestTemporalSubindexWithTiming:
    def test_timed_slice_activates_temporal_subindex(self, timed_xml):
        result = analyze_score(str(timed_xml))
        # Second slice has two events with resolved durations from XML
        sub = result.slices[1].subindices
        assert sub["temporal"]["raw"]["available"] is True

    def test_legacy_calculate_metrics_still_single_slice(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        assert resultados["density_subindices"]["temporal"]["raw"]["available"] is False
