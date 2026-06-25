"""
Unit tests for utils.notes (Phase 4.1).

Tests pure functions: to_sharp, normalize_note_string, normalize_media_note_label, extract_cents, note_to_midi.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.notes import (
    dyad_notes_from_semitone_interval,
    extract_cents,
    frequency_to_midi,
    is_valid_note,
    midi_to_frequency,
    midi_to_hz,
    midi_to_note_name,
    normalize_note_string,
    normalize_media_note_label,
    note_to_midi,
    to_sharp,
)


class TestToSharp:
    """Test flat/arrow to sharp conversion."""

    def test_c_sharp_unchanged(self):
        assert to_sharp("C#4") == "C#4"

    def test_flat_conversion(self):
        assert to_sharp("Eb4") == "D#4"
        assert to_sharp("Bb3") == "A#3"
        assert to_sharp("Ab5") == "G#5"

    def test_quarter_arrow_unchanged(self):
        # to_sharp converts arrow to +/- form
        assert "C" in to_sharp("C↑4") and "4" in to_sharp("C↑4")


class TestNormalizeNoteString:
    """Test note string normalization."""

    def test_standard_note(self):
        assert normalize_note_string("c4") == "C4"
        assert normalize_note_string("  G#5  ") == "G#5"

    def test_flat_to_sharp(self):
        assert normalize_note_string("Eb4") == "D#4"

    def test_cents_preserved(self):
        assert "25" in normalize_note_string("C4+25c") or "25c" in normalize_note_string("C4+25c")

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="Nota não é uma string"):
            normalize_note_string(42)


class TestNormalizeMediaNoteLabel:
    def test_strips_duplicate_suffix(self):
        assert normalize_media_note_label("F4 (2)") == "F4"
        assert normalize_media_note_label("f4(2)") == "F4"


class TestExtractCents:
    """Test cents extraction from note strings."""

    def test_no_cents(self):
        assert extract_cents("C4") == ("C4", 0)
        assert extract_cents("G#5") == ("G#5", 0)

    def test_positive_cents(self):
        assert extract_cents("C4+25c") == ("C4", 25)
        assert extract_cents("E4+50c") == ("E4", 50)

    def test_negative_cents(self):
        assert extract_cents("C4-25c") == ("C4", -25)


class TestNoteToMidi:
    """Test note to MIDI conversion."""

    def test_c4(self):
        assert abs(note_to_midi("C4") - 60) < 0.01

    def test_a4(self):
        assert abs(note_to_midi("A4") - 69) < 0.01

    def test_with_cents(self):
        midi = note_to_midi("C4+50c")
        assert 60 < midi < 61

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Formato de nota inválido"):
            note_to_midi("X9")


class TestIsValidNote:
    """Test note validation."""

    def test_valid(self):
        assert is_valid_note("C4") is True
        assert is_valid_note("C#4") is True
        assert is_valid_note("C4+25c") is True

    def test_invalid(self):
        assert is_valid_note("") is False
        assert is_valid_note("X9") is False


class TestMidiHzConversion:
    """Test MIDI <-> Hz and frequency helpers."""

    def test_midi_to_hz_a4(self):
        assert abs(midi_to_hz(69) - 440.0) < 0.01

    def test_midi_to_frequency(self):
        assert abs(midi_to_frequency(69) - 440.0) < 0.01

    def test_frequency_to_midi(self):
        assert abs(frequency_to_midi(440.0) - 69) < 0.01

    def test_midi_to_note_name_with_cents(self):
        name = midi_to_note_name(60.5)
        assert "c" in name or "+" in name
        assert "50" in name


class TestDyadNotesFromSemitoneInterval:
    """Phase 4: calibration dyads must use semitone distance, not diatonic index."""

    @pytest.mark.parametrize(
        "semitones,expected_upper_midi",
        [
            (0, 60),
            (2, 62),
            (3, 63),
            (4, 64),
            (5, 65),
            (6, 66),
        ],
    )
    def test_dyad_semitone_distance(self, semitones, expected_upper_midi):
        base, upper = dyad_notes_from_semitone_interval("C4", semitones)
        assert base == "C4"
        assert int(round(note_to_midi(base))) == 60
        assert int(round(note_to_midi(upper))) == expected_upper_midi
        assert int(round(note_to_midi(upper) - note_to_midi(base))) == semitones

    def test_rejects_negative_semitones(self):
        with pytest.raises(ValueError):
            dyad_notes_from_semitone_interval("C4", -1)
