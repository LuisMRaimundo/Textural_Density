"""Tests for strict microtonal pitch parsing."""

from __future__ import annotations

import math

import pytest

from microtonal import (
    InvalidPitchNotation,
    note_to_midi,
    note_to_midi_strict,
    parse_pitch_strict,
)


class TestNoteToMidiStrictCents:
    def test_d3_plus_7c(self):
        assert note_to_midi_strict("D3+7c") == pytest.approx(50.07, abs=1e-9)

    def test_a5_minus_30c(self):
        assert note_to_midi_strict("A5-30c") == pytest.approx(80.70, abs=1e-9)

    def test_c4_plus_125c(self):
        assert note_to_midi_strict("C4+125c") == pytest.approx(61.25, abs=1e-9)

    def test_c4_plus_7_5c(self):
        assert note_to_midi_strict("C4+7.5c") == pytest.approx(60.075, abs=1e-9)

    def test_c4_plus_7_cent_sign(self):
        assert note_to_midi_strict("C4+7¢") == pytest.approx(60.07, abs=1e-9)

    def test_c4_minus_130c(self):
        assert note_to_midi_strict("C4-130c") == pytest.approx(58.70, abs=1e-9)


class TestNoteToMidiStrictInvalid:
    @pytest.mark.parametrize(
        "bad",
        ["H4", "C##4", "C4+abc", "foo", "", "   "],
    )
    def test_invalid_raises(self, bad):
        with pytest.raises(InvalidPitchNotation):
            note_to_midi_strict(bad)

    @pytest.mark.parametrize(
        "bad",
        ["H4", "C##4", "C4+abc", "foo"],
    )
    def test_invalid_never_returns_c4(self, bad):
        with pytest.raises(InvalidPitchNotation):
            note_to_midi_strict(bad)
        assert note_to_midi_strict("D4") != pytest.approx(60.0)


class TestLegacyNoteToMidiPermissive:
    def test_legacy_still_falls_back_to_c4_for_garbage(self):
        assert note_to_midi("totally_invalid_pitch") == pytest.approx(60.0)

    def test_strict_flag_routes_to_strict_parser(self):
        assert note_to_midi("C4+7c", strict=True) == pytest.approx(60.07, abs=1e-9)
        with pytest.raises(InvalidPitchNotation):
            note_to_midi("foo", strict=True)


class TestParsePitchStrict:
    def test_chromatic_parsed(self):
        parsed = parse_pitch_strict("C4")
        assert parsed.letter == "C"
        assert parsed.octave == 4
        assert parsed.cents == pytest.approx(0.0)
        assert parsed.midi == pytest.approx(60.0)

    def test_quarter_tone_arrow_equivalent_to_cents(self):
        arrow = parse_pitch_strict("C↓4")
        cents = parse_pitch_strict("C4+50c")
        assert arrow.midi == pytest.approx(cents.midi, abs=1e-9)

    def test_unicode_sharp(self):
        assert note_to_midi_strict("C♯4") == pytest.approx(61.0, abs=1e-9)


class TestDecimalCentsLegacyPath:
    def test_legacy_note_to_midi_supports_decimal_cents(self):
        assert note_to_midi("C4+7.5c") == pytest.approx(60.075, abs=1e-9)

    def test_large_cents_offset(self):
        value = note_to_midi("C4+125c")
        assert value == pytest.approx(61.25, abs=1e-9)
        assert math.isfinite(value)
