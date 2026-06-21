"""Tests for strict microtonal pitch parsing."""

from __future__ import annotations

import math

import pytest

from microtonal import (
    InvalidPitchNotation,
    converter_para_sustenido,
    extract_cents,
    extract_cents_float,
    format_cents_suffix,
    is_valid_note,
    note_to_midi,
    note_to_midi_strict,
    parse_pitch_strict,
    preprocess_nota,
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


class TestIsValidNoteParity:
    """is_valid_note(note) must equal 'parse_pitch_strict(note) succeeds'."""

    @pytest.mark.parametrize(
        "note",
        [
            "C4", "C#4", "Db4", "D4", "C4+50c", "C4+7.5c", "C4+125c",
            "C↑4", "C↓4", "C+4", "D-5", "F#-3", "Cb4", "B#4",
            "C4+7¢", "Bb3", "C♯4", "Cb4+50c", "B#4-50c",
            "H4", "C##4", "C4+abc", "foo", "", "   ", "x", "C", "44",
        ],
    )
    def test_parity_with_parse_pitch_strict(self, note):
        try:
            parse_pitch_strict(note)
            succeeds = True
        except InvalidPitchNotation:
            succeeds = False
        assert is_valid_note(note) is succeeds

    def test_non_string_is_false(self):
        assert is_valid_note(None) is False  # type: ignore[arg-type]
        assert is_valid_note(42) is False  # type: ignore[arg-type]


class TestExtractCentsCompatibilityAlias:
    """extract_cents is a thin float splitter, not a validator."""

    def test_returns_float_tuple(self):
        base, cents = extract_cents("C4+125c")
        assert base == "C4"
        assert isinstance(cents, float)
        assert cents == pytest.approx(125.0)

    def test_decimal_cents(self):
        assert extract_cents("C4+7.5c") == ("C4", pytest.approx(7.5))

    def test_cent_unicode_symbol(self):
        assert extract_cents("C4+7¢") == ("C4", pytest.approx(7.0))

    def test_no_cents_returns_zero_float(self):
        base, cents = extract_cents("C4")
        assert base == "C4"
        assert cents == pytest.approx(0.0)

    def test_does_not_validate_pitch_base(self):
        # Splitter only separates the suffix; the (invalid) base passes through.
        base, cents = extract_cents("H4+30c")
        assert base == "H4"
        assert cents == pytest.approx(30.0)


class TestFormatCentsSuffix:
    @pytest.mark.parametrize(
        "cents, expected",
        [
            (0.0, ""),
            (50.0, "+50c"),
            (-30.0, "-30c"),
            (125.0, "+125c"),
            (7.5, "+7.5c"),
        ],
    )
    def test_format_cents_suffix_basic(self, cents, expected):
        assert format_cents_suffix(cents) == expected

    @pytest.mark.parametrize(
        "cents",
        [7.5, 7.1234567, -30.125, 0.000001, 125.0],
    )
    def test_format_cents_suffix_round_trips(self, cents):
        suffix = format_cents_suffix(cents)
        _, recovered = extract_cents_float(f"C4{suffix}")
        assert recovered == pytest.approx(cents)
        assert "e" not in suffix.lower()

    def test_zero_is_empty(self):
        assert format_cents_suffix(0) == ""
        assert format_cents_suffix(0.0) == ""

    def test_integer_offset_omits_decimal(self):
        assert format_cents_suffix(50.0) == "+50c"
        assert format_cents_suffix(125) == "+125c"
        assert format_cents_suffix(-30.0) == "-30c"

    def test_decimal_offset_preserved(self):
        assert format_cents_suffix(7.5) == "+7.5c"
        assert format_cents_suffix(-12.25) == "-12.25c"


class TestDecimalCentsRoundTripHelpers:
    def test_preprocess_nota_preserves_decimal_cents(self):
        assert preprocess_nota("C4+7.5c") == "C4+7.5c"

    def test_preprocess_nota_arrow_with_decimal_cents(self):
        # ↓ maps to '+' quarter-tone code; cents preserved without +50.0c artefact
        assert preprocess_nota("C↓4+7.5c") == "C+4+7.5c"

    def test_converter_para_sustenido_preserves_decimal_cents(self):
        assert converter_para_sustenido("Db4+7.5c") == "C#4+7.5c"

    def test_converter_para_sustenido_integer_cents_no_decimal_artefact(self):
        assert converter_para_sustenido("Db4+50c") == "C#4+50c"


class TestOctaveBoundaryEnharmonics:
    def test_cb4_is_b3(self):
        assert note_to_midi_strict("Cb4") == pytest.approx(59.0, abs=1e-9)

    def test_b_sharp4_is_c5(self):
        assert note_to_midi_strict("B#4") == pytest.approx(72.0, abs=1e-9)

    def test_cb4_with_cents(self):
        assert note_to_midi_strict("Cb4+50c") == pytest.approx(59.5, abs=1e-9)

    def test_b_sharp4_with_cents(self):
        assert note_to_midi_strict("B#4-50c") == pytest.approx(71.5, abs=1e-9)

    def test_cb4_equals_b3(self):
        assert note_to_midi_strict("Cb4") == pytest.approx(note_to_midi_strict("B3"))

    def test_b_sharp4_equals_c5(self):
        assert note_to_midi_strict("B#4") == pytest.approx(note_to_midi_strict("C5"))


class TestNoInstrumentInterpolationRegression:
    """Consolidation must not change interpolation behaviour for instruments."""

    def test_chromatic_only_table_interpolates_microtone(self):
        import logging

        from instrumentos.pitch_interpolation import resolve_density_from_table

        table = {
            "C4": {"pp": 4.0, "mf": 10.0, "ff": 16.0},
            "C#4": {"pp": 5.0, "mf": 20.0, "ff": 25.0},
            "D4": {"pp": 6.0, "mf": 30.0, "ff": 36.0},
        }
        result = resolve_density_from_table(
            table, "C4+50c", "mf",
            interpolation_method="linear",
            logger=logging.getLogger("test.microtonal_strict.interp"),
        )
        assert result.provenance == "interpolated"
        assert result.value == pytest.approx(15.0)
        assert result.target_midi == pytest.approx(60.5)

    def test_existing_string_instrument_microtonal_finite(self):
        from instrumentos import get_instrument_module

        mod = get_instrument_module("violin")
        assert math.isfinite(mod.calcular_densidade("G4+50c", "mf"))
        assert math.isfinite(mod.calcular_densidade("A↓4", "mf"))
