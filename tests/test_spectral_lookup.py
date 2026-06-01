"""Tests for MIDI-space spectral table lookup (octave-safe)."""

from __future__ import annotations

import logging

import pytest

from instrumentos.flauta import calcular_densidade, spectral_data
from instrumentos.spectral_lookup import lookup_spectral_density
from microtonal import note_to_midi


class TestFlautaOctaveSafeLookup:
    def test_d_sharp6_does_not_equal_d_sharp4(self):
        d6 = calcular_densidade("D#6", "mf")
        d4 = calcular_densidade("D#4", "mf")
        assert d6 != pytest.approx(d4)
        assert d6 < d4

    def test_c_sharp5_extrapolates_from_table_top_not_d_sharp4(self):
        cs5 = calcular_densidade("C#5", "mf")
        c5 = calcular_densidade("C5", "mf")
        d4 = calcular_densidade("D#4", "mf")
        assert cs5 != pytest.approx(d4)
        assert cs5 < c5

    def test_microtonal_cents_interpolation_in_register(self):
        d4_36c = calcular_densidade("D4+36c", "mf")
        d4 = calcular_densidade("D4", "mf")
        d_sharp4 = calcular_densidade("D#4", "mf")
        assert min(d4, d_sharp4) <= d4_36c <= max(d4, d_sharp4)

    def test_high_pitch_extrapolation_uses_top_of_table(self, caplog):
        caplog.set_level(logging.WARNING, logger="flauta")
        calcular_densidade("D#6", "mf")
        joined = caplog.text
        assert "D#4" not in joined or "desvio" in joined.lower()
        assert any(level >= logging.WARNING for _, level, _ in caplog.record_tuples)


class TestSpectralLookupCore:
    def test_extrapolation_above_table(self):
        logger = logging.getLogger("test.spectral_lookup")
        table = {
            "C4": {"mf": 10.0},
            "C5": {"mf": 8.0},
        }
        value = lookup_spectral_density(table, "C6", "mf", logger=logger)
        assert value < 8.0
        assert value != pytest.approx(10.0)

    def test_target_midi_preserved_for_out_of_range(self):
        logger = logging.getLogger("test.spectral_lookup")
        target = float(note_to_midi("D#6"))
        entries = sorted((float(note_to_midi(k)), k) for k in spectral_data)
        assert target > entries[-1][0]
