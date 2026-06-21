"""
Phase 2 tests: score-event models, legacy conversion, per-event instruments.
"""

from __future__ import annotations

import pytest

from core.converters import (
    legacy_input_to_vertical_slice,
    note_string_to_pitch,
    vertical_slice_to_legacy_lists,
)
from core.orchestration import compute_instrument_densities_for_slice
from core.pipeline import calculate_metrics
from data_processor import calculate_metrics as dp_calculate_metrics, load_instrument_module
from error_handler import InputError
from microtonal import InvalidPitchNotation


class TestPitch:
    def test_c4_midi_and_frequency(self):
        pitch = note_string_to_pitch("C4")
        assert pitch.midi == pytest.approx(60.0)
        assert pitch.cents_offset == 0.0
        assert pitch.frequency_hz == pytest.approx(261.63, rel=1e-3)
        assert pitch.pitch_class == 0

    def test_cents_offset(self):
        pitch = note_string_to_pitch("A4+50c")
        assert pitch.midi == pytest.approx(69.5, abs=1e-6)
        assert pitch.cents_offset == 50

    def test_note_string_to_pitch_preserves_cross_octave_enharmonics(self):
        assert note_string_to_pitch("Cb4").midi == pytest.approx(59.0)
        assert note_string_to_pitch("B#4").midi == pytest.approx(72.0)
        assert note_string_to_pitch("Cb4+50c").midi == pytest.approx(59.5)
        assert note_string_to_pitch("B#4-50c").midi == pytest.approx(71.5)

    def test_note_string_to_pitch_rejects_invalid_pitch(self):
        with pytest.raises(InvalidPitchNotation):
            note_string_to_pitch("garbage")


class TestLegacyConverter:
    def test_builds_one_event_per_index(self):
        data = {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "f"],
            "instruments": ["flauta", "clarinete"],
            "num_instruments": [1, 2],
        }
        sl = legacy_input_to_vertical_slice(data)
        assert len(sl.events) == 2
        assert sl.events[0].instrument_id == "flauta"
        assert sl.events[1].instrument_id == "clarinete"
        assert sl.events[1].player_count == 2

    def test_mismatched_lengths_raise(self):
        with pytest.raises(InputError, match="same length"):
            legacy_input_to_vertical_slice(
                {
                    "notes": ["C4", "E4"],
                    "dynamics": ["mf"],
                    "instruments": ["flauta"],
                    "num_instruments": [1],
                }
            )

    def test_round_trip_lists(self):
        data = {
            "notes": ["C4", "G4"],
            "dynamics": ["mf", "ff"],
            "instruments": ["flauta", "oboe"],
            "num_instruments": [1, 3],
        }
        sl = legacy_input_to_vertical_slice(data)
        notes, dyns, insts, nums = vertical_slice_to_legacy_lists(sl)
        assert len(notes) == 2
        assert insts == ["flauta", "oboe"]
        assert nums == [1, 3]
        assert dyns == ["mf", "ff"]


class TestPerEventInstrumentDensity:
    def test_mixed_instruments_differ_from_first_only(self):
        mixed = {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "f"],
            "instruments": ["flauta", "clarinete"],
            "num_instruments": [1, 1],
        }
        flauta_only = {
            **mixed,
            "instruments": ["flauta", "flauta"],
        }
        r_mixed, d_mixed, _ = calculate_metrics(mixed)
        r_flauta, d_flauta, _ = calculate_metrics(flauta_only)

        assert d_mixed[1] != pytest.approx(d_flauta[1], rel=1e-6)
        assert r_mixed["density"]["instrument"] != pytest.approx(
            r_flauta["density"]["instrument"], rel=1e-6
        )

    def test_orchestration_helper_per_event(self):
        data = {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "f"],
            "instruments": ["flauta", "clarinete"],
            "num_instruments": [1, 2],
        }
        sl = legacy_input_to_vertical_slice(data)
        densities = compute_instrument_densities_for_slice(sl, load_instrument_module)
        assert len(densities) == 2
        assert densities[0] > 0
        assert densities[1] > densities[0]


class TestPipelineStrictPitchList:
    def test_calculate_metrics_pitch_list_uses_event_midi(self):
        data = {
            "notes": ["Cb4", "B#4"],
            "dynamics": ["mf", "mf"],
            "instruments": ["flauta", "flauta"],
            "num_instruments": [1, 1],
        }
        _, _, pitches = calculate_metrics(data)
        assert pitches[0] == pytest.approx(59.0)
        assert pitches[1] == pytest.approx(72.0)

    def test_calculate_metrics_rejects_invalid_pitch(self):
        data = {
            "notes": ["garbage"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
        }
        with pytest.raises(InvalidPitchNotation):
            calculate_metrics(data)

    def test_data_processor_gateway_rejects_invalid_pitch(self):
        data = {
            "notes": ["garbage"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
        }
        with pytest.raises(InvalidPitchNotation):
            dp_calculate_metrics(data)
