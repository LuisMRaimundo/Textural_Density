"""Parametrized register contracts for every instrument in the registry."""

from __future__ import annotations

import importlib

import pytest
from microtonal import midi_to_note_name, note_to_midi_strict

from core.converters import make_instrument_event
from data_processor import calculate_metrics
from error_handler import InputError
from instrumentos import get_instrument_module
from instrumentos.registry import REGISTRY, list_profiles, resolve_profile
from tests.instrument_register_audit import build_instrument_register_audit, gpr_module_ids

ALL_PROFILES = list(list_profiles())
ALL_IDS = [p.instrument_id for p in ALL_PROFILES]
GPR_IDS = gpr_module_ids()


@pytest.fixture(scope="module")
def register_audit():
    return build_instrument_register_audit()


class TestRegisterAuditArtifact:
    def test_audit_covers_every_registry_instrument(self, register_audit):
        audited = {i["instrument_id"] for i in register_audit["instruments"]}
        assert audited == set(REGISTRY.keys())

    def test_audit_json_fields_present(self, register_audit):
        for inst in register_audit["instruments"]:
            assert isinstance(inst["registry_sounding_min_midi"], int)
            assert isinstance(inst["registry_sounding_max_midi"], int)
            assert inst["registry_sounding_min_midi"] <= inst["registry_sounding_max_midi"]


@pytest.mark.parametrize("instrument_id", ALL_IDS)
def test_canonical_profile_resolves(instrument_id):
    profile = REGISTRY[instrument_id]
    assert resolve_profile(instrument_id) is profile
    assert resolve_profile(profile.display_name) is profile


@pytest.mark.parametrize("instrument_id", ALL_IDS)
def test_sounding_range_finite_ordered_integers(instrument_id):
    lo, hi = REGISTRY[instrument_id].sounding_range
    assert lo == int(lo)
    assert hi == int(hi)
    assert lo < hi


@pytest.mark.parametrize("instrument_id", ALL_IDS)
def test_boundary_min_max_accepted(instrument_id):
    profile = REGISTRY[instrument_id]
    lo, hi = (int(profile.sounding_range[0]), int(profile.sounding_range[1]))
    for midi in (lo, hi):
        note = midi_to_note_name(float(midi))
        _, _, pitches = calculate_metrics(
            {
                "notes": [note],
                "dynamics": ["mf"],
                "instruments": [profile.display_name],
                "num_instruments": [1],
            }
        )
        assert pitches[0] == pytest.approx(float(midi))


@pytest.mark.parametrize("instrument_id", ALL_IDS)
def test_one_semitone_below_min_rejected(instrument_id):
    profile = REGISTRY[instrument_id]
    lo = int(profile.sounding_range[0])
    if lo <= 0:
        pytest.skip("MIDI floor")
    note = midi_to_note_name(float(lo - 1))
    with pytest.raises(InputError, match="outside the sounding range"):
        calculate_metrics(
            {
                "notes": [note],
                "dynamics": ["mf"],
                "instruments": [profile.instrument_id],
                "num_instruments": [1],
            }
        )


@pytest.mark.parametrize("instrument_id", ALL_IDS)
def test_one_semitone_above_max_rejected(instrument_id):
    profile = REGISTRY[instrument_id]
    hi = int(profile.sounding_range[1])
    if hi >= 127:
        pytest.skip("MIDI ceiling")
    note = midi_to_note_name(float(hi + 1))
    with pytest.raises(InputError, match="outside the sounding range"):
        calculate_metrics(
            {
                "notes": [note],
                "dynamics": ["mf"],
                "instruments": [profile.instrument_id],
                "num_instruments": [1],
            }
        )


@pytest.mark.parametrize("instrument_id", GPR_IDS)
def test_gpr_table_anchors_pass_range_validation(instrument_id):
    profile = REGISTRY[instrument_id]
    mod = get_instrument_module(instrument_id)
    table = mod.spectral_data
    lo, hi = profile.sounding_range
    for pitch_label in table:
        midi = float(note_to_midi_strict(pitch_label))
        assert lo - 1e-6 <= midi <= hi + 1e-6, (
            f"{instrument_id}: table anchor {pitch_label!r} (MIDI {midi}) "
            f"outside registry sounding range [{lo}, {hi}]"
        )
        calculate_metrics(
            {
                "notes": [pitch_label],
                "dynamics": ["mf"],
                "instruments": [profile.display_name],
                "num_instruments": [1],
            }
        )


@pytest.mark.parametrize("instrument_id", GPR_IDS)
def test_table_midi_span_consistent(instrument_id):
    mod = get_instrument_module(instrument_id)
    notes = sorted(mod.spectral_data.keys(), key=note_to_midi_strict)
    lo = int(note_to_midi_strict(notes[0]))
    hi = int(note_to_midi_strict(notes[-1]))
    src = getattr(mod, "INSTRUMENT_SOURCE", None)
    if src and getattr(src, "pitch_range", None):
        assert list(src.pitch_range) == [lo, hi]


class TestContrabassoonRegression:
    """Reproduce and lock the reported Contrabassoon G4 failure on main."""

    def test_contrabassoon_g4_sounding_accepted(self):
        _, _, pitches = calculate_metrics(
            {
                "notes": ["G4"],
                "dynamics": ["mf"],
                "instruments": ["Contrabassoon"],
                "num_instruments": [1],
            }
        )
        assert pitches[0] == pytest.approx(67.0)

    def test_contrabassoon_g4_is_sounding_not_auto_transposed(self):
        ev = make_instrument_event(
            idx=2,
            note="G4",
            dynamic="mf",
            instrument_name="Contrabassoon",
            player_count=1,
        )
        assert ev.sounding_pitch.midi == pytest.approx(67.0)
        assert ev.written_pitch is None

    def test_contrabassoon_genuinely_high_note_rejected(self):
        with pytest.raises(InputError, match="outside the sounding range"):
            calculate_metrics(
                {
                    "notes": ["C6"],
                    "dynamics": ["mf"],
                    "instruments": ["contrabassoon"],
                    "num_instruments": [1],
                }
            )


class TestViolaRegression:
    def test_viola_a5_table_boundary_accepted(self):
        _, _, pitches = calculate_metrics(
            {
                "notes": ["A5"],
                "dynamics": ["mf"],
                "instruments": ["viola"],
                "num_instruments": [1],
            }
        )
        assert pitches[0] == pytest.approx(81.0)
