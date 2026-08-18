"""F-A — Pitch grammar and tuning (HARD; Mathematical Manual §A–§B)."""

from __future__ import annotations

import pytest
from microtonal import InvalidPitchNotation, hz_to_midi, midi_to_hz, parse_pitch_strict

from core.pipeline import calculate_metrics
from tests.plausibility.conftest import record_hard
from tests.plausibility.helpers import (
    A4_HZ,
    assert_jsonable,
    independent_hz,
    independent_midi_from_hz,
    slice_input,
)


class TestFATuning:
    def test_a4_is_440_hz(self):
        """HARD: midi_to_hz(69) == 440 (§A)."""
        got = midi_to_hz(69)
        assert got == pytest.approx(A4_HZ)
        assert independent_hz(69) == pytest.approx(A4_HZ)
        record_hard(family="F-A", test_id="FA.hz.a4", value=got)

    @pytest.mark.parametrize("midi", [0, 21, 60, 60.5, 69, 108, 127])
    def test_hz_midi_roundtrip(self, midi: float):
        """HARD: hz_to_midi(midi_to_hz(m)) == m for documented MIDI set."""
        back = hz_to_midi(midi_to_hz(midi))
        assert back == pytest.approx(midi)
        assert independent_midi_from_hz(independent_hz(midi)) == pytest.approx(midi)
        record_hard(family="F-A", test_id=f"FA.roundtrip.{midi}", midi=midi, back=back)

    def test_hz_to_midi_nonpositive_is_zero(self):
        """HARD: hz_to_midi(0) returns 0 (documented edge case)."""
        assert hz_to_midi(0) == 0
        assert hz_to_midi(-1.0) == 0
        record_hard(family="F-A", test_id="FA.hz.zero")


class TestFAEnharmonics:
    @pytest.mark.parametrize(
        "a,b",
        [("C#4", "Db4"), ("F#4", "Gb4"), ("B4", "Cb5")],
    )
    def test_enharmonic_pairs_match_pitches_and_density(self, a: str, b: str):
        """HARD: enharmonic spellings give identical pitches and density.*."""
        from microtonal import note_to_midi

        ra, da, pa = calculate_metrics(slice_input([a, "G4"], instruments="flauta"))
        rb, db, pb = calculate_metrics(slice_input([b, "G4"], instruments="flauta"))
        assert_jsonable(ra, label=f"FA.enh.{a}")
        diffs = {
            key: (ra["density"][key], rb["density"][key])
            for key in ra["density"]
            if ra["density"][key] != pytest.approx(rb["density"][key])
        }
        record_hard(
            family="F-A",
            test_id=f"FA.enh.{a}.{b}",
            status="pass" if not diffs and pa == pytest.approx(pb) else "fail",
            pitches_a=pa,
            pitches_b=pb,
            density_a=ra["density"],
            density_b=rb["density"],
            density_diffs=diffs,
            note_to_midi_a=note_to_midi(a),
            note_to_midi_b=note_to_midi(b),
            parse_strict_a=parse_pitch_strict(a).midi,
            parse_strict_b=parse_pitch_strict(b).midi,
        )
        assert pa == pytest.approx(pb)
        for key in ra["density"]:
            assert ra["density"][key] == pytest.approx(rb["density"][key]), key


class TestFAMicrotonalGrammar:
    def test_c4_plus_50c_is_60_5(self):
        """HARD: C4+50c → MIDI 60.5 via parse_pitch_strict."""
        parsed = parse_pitch_strict("C4+50c")
        assert parsed.midi == pytest.approx(60.5)
        record_hard(family="F-A", test_id="FA.micro.C4+50c", midi=parsed.midi)

    @pytest.mark.parametrize(
        "note,expected",
        [
            ("C4+25c", 60.25),
            ("C4+50c", 60.5),
            ("C4-50c", 59.5),
            ("A4", 69.0),
        ],
    )
    def test_quarter_tone_and_cent_spellings(self, note: str, expected: float):
        """HARD: accepted quarter-tone / cent spellings map to intended MIDI."""
        parsed = parse_pitch_strict(note)
        assert parsed.midi == pytest.approx(expected)
        record_hard(family="F-A", test_id=f"FA.micro.{note}", midi=parsed.midi)

    @pytest.mark.parametrize("bad", ["H4", "C##4", "foo"])
    def test_malformed_strings_raise_and_never_fallback_to_c4(self, bad: str):
        """HARD: malformed strings raise InvalidPitchNotation and never become C4."""
        with pytest.raises(InvalidPitchNotation):
            parse_pitch_strict(bad)
        with pytest.raises(InvalidPitchNotation):
            calculate_metrics(slice_input([bad], instruments="flauta"))
        record_hard(family="F-A", test_id=f"FA.invalid.{bad}")


class TestFAPitchBinMerge:
    def test_sub_tolerance_collapse(self):
        """HARD: MIDI 60 and 60+5e-7 collapse into one distinct pitch."""
        near = "C4+0.00005c"  # 5e-7 semitones (= 5e-5 cents)
        resultados, _, pitches = calculate_metrics(
            slice_input(["C4", near], instruments="flauta")
        )
        assert_jsonable(resultados, label="FA.merge.collapse")
        n = resultados["pitch_aggregation"]["distinct_pitch_count"]
        assert n == 1
        assert pitches[0] == pytest.approx(60.0)
        record_hard(family="F-A", test_id="FA.merge.collapse", distinct=n, pitches=pitches)

    def test_cent_offset_does_not_collapse(self):
        """HARD: MIDI 60 and 60.01 remain two distinct pitches."""
        resultados, _, pitches = calculate_metrics(
            slice_input(["C4", "C4+1c"], instruments="flauta")
        )
        assert_jsonable(resultados, label="FA.merge.keep")
        n = resultados["pitch_aggregation"]["distinct_pitch_count"]
        assert n == 2
        assert pitches[1] == pytest.approx(60.01)
        record_hard(family="F-A", test_id="FA.merge.keep", distinct=n, pitches=pitches)
