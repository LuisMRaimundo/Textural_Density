"""Tests for unified pitch interpolation in instrument metadata lookup."""

from __future__ import annotations

import logging
import math

import pytest

from instrumentos import get_instrument_module
from instrumentos.flauta import calcular_densidade as flauta_density, spectral_data as flauta_table
from instrumentos.pitch_interpolation import (
    MetadataTableConflictError,
    resolve_density_from_table,
    validate_metadata_table,
)
from instrumentos.spectral_lookup import lookup_spectral_density, lookup_spectral_density_detailed
from microtonal import InvalidPitchNotation, note_to_midi_strict


CHROMATIC_TABLE = {
    "C4": {"pp": 4.0, "mf": 10.0, "ff": 16.0},
    "C#4": {"pp": 5.0, "mf": 20.0, "ff": 25.0},
    "D4": {"pp": 6.0, "mf": 30.0, "ff": 36.0},
    "G4": {"pp": 7.0, "mf": 9.0, "ff": 11.0},
}

EXTENDED_CHROMATIC = {
    **CHROMATIC_TABLE,
    "B3": {"mf": 8.0},
    "A5": {"mf": 12.0},
    "D3": {"mf": 14.0},
}


def _resolve(table, note, dynamic="mf", **kwargs):
    logger = logging.getLogger("test.pitch_interpolation")
    return resolve_density_from_table(table, note, dynamic, logger=logger, **kwargs)


class TestExactChromaticLookup:
    def test_chromatic_anchor_unchanged(self):
        result = _resolve(CHROMATIC_TABLE, "C4", "mf")
        assert result.value == pytest.approx(10.0)
        assert result.provenance == "exact"

    def test_lookup_spectral_density_backward_compat(self):
        logger = logging.getLogger("test.pitch_interpolation.compat")
        value = lookup_spectral_density(CHROMATIC_TABLE, "D4", "mf", logger=logger)
        assert value == pytest.approx(30.0)


class TestMicrotonalFromChromaticOnly:
    def test_quarter_tone_finite_from_chromatic_table(self):
        result = _resolve(CHROMATIC_TABLE, "C4+50c", "mf")
        assert math.isfinite(result.value)
        assert result.provenance in ("interpolated", "normalized_exact")

    def test_c4_plus_50c_between_c4_and_c_sharp4(self):
        result = _resolve(CHROMATIC_TABLE, "C4+50c", "mf")
        assert 10.0 <= result.value <= 20.0
        assert result.value == pytest.approx(15.0)

    def test_c_down4_equivalent_to_c4_plus_50c(self):
        r_cents = _resolve(CHROMATIC_TABLE, "C4+50c", "mf")
        r_arrow = _resolve(CHROMATIC_TABLE, "C↓4", "mf")
        assert r_cents.target_midi == pytest.approx(r_arrow.target_midi, abs=1e-4)
        assert r_cents.value == pytest.approx(r_arrow.value)

    def test_unicode_sharp_matches_ascii(self):
        table = {"C♯4": {"mf": 20.0}, "C4": {"mf": 10.0}}
        r_uni = _resolve(table, "C♯4", "mf")
        r_ascii = _resolve(table, "C#4", "mf")
        assert r_uni.value == pytest.approx(20.0)
        assert r_ascii.value == pytest.approx(20.0)
        assert r_uni.provenance == "exact"


class TestExistingInstrumentBehaviour:
    def test_flauta_chromatic_unchanged(self):
        assert flauta_density("G4", "mf") == pytest.approx(
            lookup_spectral_density(flauta_table, "G4", "mf", logger=logging.getLogger("flauta"))
        )

    def test_flauta_microtonal_cents_still_works(self):
        d4_36c = flauta_density("D4+36c", "mf")
        d4 = flauta_density("D4", "mf")
        d_sharp4 = flauta_density("D#4", "mf")
        assert min(d4, d_sharp4) <= d4_36c <= max(d4, d_sharp4)

    def test_flauta_pasted_microtonal_entry_has_priority(self):
        if "C#+4" in flauta_table:
            pasted = flauta_density("C#+4", "mf")
            interpolated = _resolve(flauta_table, "C#+4", "mf").value
            assert pasted == pytest.approx(interpolated)
            assert _resolve(flauta_table, "C#+4", "mf").provenance == "exact"

    def test_clarinet_chromatic_lookup_finite(self):
        mod = get_instrument_module("clarinete")
        assert math.isfinite(mod.calcular_densidade("G4", "mf"))

    def test_string_chromatic_table_accepts_microtonal(self):
        mod = get_instrument_module("violino")
        assert math.isfinite(mod.calcular_densidade("G4+50c", "mf"))
        assert math.isfinite(mod.calcular_densidade("A↓4", "mf"))


class TestCoarseDefaultMicrotonal:
    def test_coarse_instrument_microtonal_finite(self):
        mod = get_instrument_module("trombone")
        assert math.isfinite(mod.calcular_densidade("F4+50c", "mf"))


class TestOctaveSafety:
    def test_d_sharp6_not_equal_d_sharp4(self):
        d6 = flauta_density("D#6", "mf")
        d4 = flauta_density("D#4", "mf")
        assert d6 != pytest.approx(d4)

    def test_high_pitch_not_collapsed_to_low_register(self):
        target = float(note_to_midi_strict("D#6"))
        logger = logging.getLogger("test.pitch_interpolation.octave")
        result = lookup_spectral_density_detailed(flauta_table, "D#6", "mf", logger=logger)
        assert result.target_midi == pytest.approx(target)
        assert result.value != pytest.approx(flauta_density("D#4", "mf"))


class TestStrictCentsInterpolation:
    def test_d3_plus_7c_interpolated(self):
        result = _resolve(EXTENDED_CHROMATIC, "D3+7c", "mf", interpolation_method="linear")
        assert result.provenance == "interpolated"
        assert result.target_midi == pytest.approx(50.07, abs=1e-9)
        assert math.isfinite(result.value)

    def test_a5_minus_30c_interpolated(self):
        result = _resolve(EXTENDED_CHROMATIC, "A5-30c", "mf", interpolation_method="linear")
        assert result.provenance == "interpolated"
        assert result.target_midi == pytest.approx(80.70, abs=1e-9)
        assert math.isfinite(result.value)

    def test_c4_plus_125c_between_c_sharp4_and_d4(self):
        result = _resolve(CHROMATIC_TABLE, "C4+125c", "mf", interpolation_method="linear")
        assert result.target_midi == pytest.approx(61.25, abs=1e-9)
        assert result.lower_anchor_key == "C#4"
        assert result.upper_anchor_key == "D4"
        assert result.value == pytest.approx(22.5)

    def test_c4_minus_30c_between_b3_and_c4(self):
        table = {**CHROMATIC_TABLE, "B3": {"mf": 8.0}}
        result = _resolve(table, "C4-30c", "mf", interpolation_method="linear")
        assert result.target_midi == pytest.approx(59.70, abs=1e-9)
        assert result.lower_anchor_key == "B3"
        assert result.upper_anchor_key == "C4"
        assert result.value == pytest.approx(9.4)

    def test_invalid_target_note_fallback_without_c4_midi(self):
        result = _resolve(CHROMATIC_TABLE, "foo", "mf")
        assert result.provenance == "fallback"
        assert result.target_midi is None


class TestMetadataTableValidation:
    def test_identical_duplicate_midi_deduplicated(self):
        table = {
            "C#4": {"mf": 20.0, "pp": 5.0},
            "Db4": {"mf": 20.0, "pp": 5.0},
        }
        normalized, warnings = validate_metadata_table(table)
        assert len(normalized) == 1
        assert normalized["C#4"]["mf"] == pytest.approx(20.0)
        assert any("duplicate" in w.lower() for w in warnings)

    def test_conflicting_duplicate_midi_raises(self):
        table = {
            "C#4": {"mf": 20.0},
            "Db4": {"mf": 25.0},
        }
        with pytest.raises(MetadataTableConflictError, match="Conflicting metadata"):
            validate_metadata_table(table)

    def test_resolve_raises_on_conflicting_table(self):
        table = {"C#4": {"mf": 20.0}, "Db4": {"mf": 25.0}}
        with pytest.raises(MetadataTableConflictError):
            _resolve(table, "C4", "mf")


class TestRangeHandling:
    def test_slightly_outside_extrapolates_with_warning(self, caplog):
        logger = logging.getLogger("test.pitch_interpolation.range")
        caplog.set_level(logging.WARNING, logger="test.pitch_interpolation.range")
        table = {"C4": {"mf": 10.0}, "C5": {"mf": 8.0}}
        result = _resolve(table, "C6", "mf")
        assert math.isfinite(result.value)
        assert result.provenance == "extrapolated"
        assert result.value < 8.0

    def test_far_outside_uses_fallback_not_silent_misleading(self, caplog):
        logger = logging.getLogger("test.pitch_interpolation.far")
        caplog.set_level(logging.ERROR, logger="test.pitch_interpolation.far")
        table = {"C4": {"mf": 10.0}, "C5": {"mf": 8.0}}
        result = resolve_density_from_table(
            table,
            "C8",
            "mf",
            logger=logger,
            fallback_value=5.0,
        )
        assert result.provenance == "fallback"
        assert result.value == pytest.approx(5.0)
        assert any(rec.levelno >= logging.ERROR for rec in caplog.records)


class TestProvenanceMetadata:
    def test_interpolated_carries_modelled_estimate_warning(self):
        result = _resolve(CHROMATIC_TABLE, "C4+50c", "mf")
        assert any("modelled estimate" in w.lower() for w in result.warnings)

    def test_exact_has_no_modelled_warning(self):
        result = _resolve(CHROMATIC_TABLE, "C4", "mf")
        assert not any("modelled estimate" in w.lower() for w in result.warnings)


class TestDynamicSeparation:
    def test_pitch_interpolation_per_dynamic_independent(self):
        r_pp = _resolve(CHROMATIC_TABLE, "C4+50c", "pp", interpolation_method="linear")
        r_mf = _resolve(CHROMATIC_TABLE, "C4+50c", "mf", interpolation_method="linear")
        r_ff = _resolve(CHROMATIC_TABLE, "C4+50c", "ff", interpolation_method="linear")
        assert r_pp.value < r_mf.value < r_ff.value
        assert r_pp.value == pytest.approx(4.5)
        assert r_mf.value == pytest.approx(15.0)
        assert r_ff.value == pytest.approx(20.5)
