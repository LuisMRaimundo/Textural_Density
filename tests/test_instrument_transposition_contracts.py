"""Written vs sounding pitch contracts for transposing instruments."""

from __future__ import annotations

import pytest

from core.converters import make_instrument_event
from data_processor import calculate_metrics
from error_handler import InputError
from instrumentos.registry import REGISTRY, resolve_profile

# Registry documents score-only transposition metadata (not applied to manual input).
TRANSPOSING_PROFILES = [
    p
    for p in REGISTRY.values()
    if p.transposition != 0
]


@pytest.mark.parametrize(
    "instrument_id,expected_semitones",
    [
        ("cor_anglais", 7),
        ("clarinete_baixo", 14),
        ("trompa", 7),
        ("trompete", 2),
    ],
)
def test_registry_transposition_metadata(instrument_id, expected_semitones):
    profile = REGISTRY[instrument_id]
    assert profile.transposition == expected_semitones


@pytest.mark.parametrize("instrument_id", [p.instrument_id for p in TRANSPOSING_PROFILES])
def test_manual_input_does_not_apply_registry_transposition(instrument_id):
    """Legacy/GUI ``notes[]`` are sounding pitch; registry ``transposition`` is metadata only."""
    profile = REGISTRY[instrument_id]
    # C4 at concert pitch must validate as sounding C4 (MIDI 60), not transposed.
    _, _, pitches = calculate_metrics(
        {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": [profile.display_name],
            "num_instruments": [1],
        }
    )
    assert pitches[0] == pytest.approx(60.0)


@pytest.mark.parametrize("instrument_id", [p.instrument_id for p in TRANSPOSING_PROFILES])
def test_make_instrument_event_note_is_sounding(instrument_id):
    profile = REGISTRY[instrument_id]
    ev = make_instrument_event(
        idx=0,
        note="G4",
        dynamic="mf",
        instrument_name=profile.display_name,
        player_count=1,
    )
    assert ev.sounding_pitch.midi == pytest.approx(67.0)
    assert ev.written_pitch is None


class TestNonTransposingOctaveInstruments:
    """Instruments often written an octave apart; registry transposition stays 0 unless documented."""

    @pytest.mark.parametrize(
        "alias",
        ["contrabassoon", "contrafagote", "piccolo", "flautim", "contrabaixo", "double_bass"],
    )
    def test_no_registry_transposition_metadata(self, alias):
        profile = resolve_profile(alias)
        assert profile is not None
        assert profile.transposition == 0

    def test_contrabassoon_manual_g4_validates_as_sounding_g4(self):
        profile = resolve_profile("contrabassoon")
        lo, hi = profile.sounding_range
        assert lo <= 67 <= hi
        calculate_metrics(
            {
                "notes": ["G4"],
                "dynamics": ["mf"],
                "instruments": ["contrabassoon"],
                "num_instruments": [1],
            }
        )

    def test_double_bass_manual_c2_in_range(self):
        calculate_metrics(
            {
                "notes": ["C2"],
                "dynamics": ["mf"],
                "instruments": ["contrabaixo"],
                "num_instruments": [1],
            }
        )


class TestErrorMessageWrittenSounding:
    def test_out_of_range_includes_written_when_set(self):
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
        assert "MIDI" in msg
        assert "written" in msg
        assert "event index 2" in msg

    def test_out_of_range_manual_input_mentions_script_pitch(self):
        with pytest.raises(InputError) as exc:
            calculate_metrics(
                {
                    "notes": ["C1"],
                    "dynamics": ["mf"],
                    "instruments": ["flauta"],
                    "num_instruments": [1],
                }
            )
        assert "written on the instrument part" in str(exc.value).lower()
