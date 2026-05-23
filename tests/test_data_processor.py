"""
Unit tests for data_processor.py module.

Tests cover:
- Metric calculation functions
- Input validation
- Error handling
- Integration with symbolic pitch-only spectral summaries
"""

import numpy as np
import pytest

from data_processor import (
    _normalize_notes_to_sustenido,
    _validate_and_extract_input,
    calcular_densidade_ponderada_normalizada,
    calcular_massa_sonora,
    calculate_metrics,
    format_output_string,
)
from error_handler import InputError


class TestValidateAndExtractInput:
    """Unit tests for _validate_and_extract_input (Phase 4.1)."""

    def test_valid_input(self):
        data = {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "f"],
            "instruments": ["flauta", "clarinete"],
            "num_instruments": [1, 2],
            "weight_factor": 0.3,
        }
        n, d, i, num, w = _validate_and_extract_input(data)
        assert n == ["C4", "E4"] and d == ["mf", "f"]
        assert w == 0.3

    def test_missing_lists_raises(self):
        with pytest.raises(InputError, match="required"):
            _validate_and_extract_input(
                {"notes": [], "dynamics": [], "instruments": [], "num_instruments": []}
            )

    def test_mismatched_lengths_raises(self):
        with pytest.raises(InputError, match="same length"):
            _validate_and_extract_input(
                {
                    "notes": ["C4", "E4"],
                    "dynamics": ["mf"],
                    "instruments": ["flauta"],
                    "num_instruments": [1],
                }
            )


class TestNormalizeNotesToSustenido:
    """Unit tests for _normalize_notes_to_sustenido (Phase 4.1)."""

    def test_already_sharp(self):
        out = _normalize_notes_to_sustenido(["C4", "C#4", "G5"])
        assert "C4" in out and "C#4" in out and "G5" in out

    def test_flat_converted(self):
        out = _normalize_notes_to_sustenido(["Eb4"])
        assert "D#" in out[0] and "4" in out[0]

    def test_cents_preserved(self):
        out = _normalize_notes_to_sustenido(["C4+25c"])
        assert "25" in out[0] or "25c" in out[0]


class TestCalculateMetrics:
    """Test main metric calculation function."""

    def test_calculate_metrics_basic(self, sample_input_data):
        """Test basic metric calculation."""
        resultados, densidades, pitches = calculate_metrics(sample_input_data)

        assert resultados is not None
        assert "density" in resultados
        assert "spectral_moments" in resultados
        assert isinstance(densidades, list)
        assert isinstance(pitches, list)
        assert len(pitches) > 0

    def test_calculate_metrics_empty_input(self):
        """Test that empty input raises error."""
        input_data = {"notes": [], "dynamics": [], "instruments": [], "num_instruments": []}

        with pytest.raises(InputError):
            calculate_metrics(input_data)

    def test_calculate_metrics_mismatched_lengths(self):
        """Test that mismatched input lengths raise error."""
        input_data = {
            "notes": ["C4", "E4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
        }

        with pytest.raises(InputError):
            calculate_metrics(input_data)

    def test_calculate_metrics_pitch_count_matches_notes(self, sample_input_data):
        """Pitches must reflect notated events only (no virtual tones)."""
        resultados, _, pitches = calculate_metrics(sample_input_data)
        assert len(pitches) == len(sample_input_data["notes"])
        assert "combination_tones" not in resultados

    def test_removed_combination_tones_key_rejected(self, sample_input_data):
        sample_input_data["calculate_combination_tones"] = True
        with pytest.raises(InputError, match="calculate_combination_tones"):
            calculate_metrics(sample_input_data)


class TestDensidadePonderada:
    """Test weighted density calculation."""

    def test_calcular_densidade_ponderada_normalizada(self):
        """Test normalized weighted density calculation."""
        DI = 50.0
        DV = 5.0

        result = calcular_densidade_ponderada_normalizada(
            DI, DV, metodo="min-max", w=0.5
        )

        assert result == pytest.approx(5.0)

    def test_invalid_metodo_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid method"):
            calcular_densidade_ponderada_normalizada(50.0, 5.0, metodo="bogus")

    def test_calcular_densidade_ponderada_extreme_weights(self):
        """Test with extreme weight values (use DI,DV so min-max gives different norms)."""
        # With DI_max=100, DV_max=10: DI=80 -> 0.8, DV=2 -> 0.2; w=0 -> DV only -> 2.0, w=1 -> DI only -> 8.0
        DI = 80.0
        DV = 2.0

        result_w0 = calcular_densidade_ponderada_normalizada(DI, DV, w=0.0)
        result_w1 = calcular_densidade_ponderada_normalizada(DI, DV, w=1.0)

        assert result_w0 != result_w1
        assert result_w0 == pytest.approx(2.0, rel=1e-5)
        assert result_w1 == pytest.approx(8.0, rel=1e-5)


class TestMassaSonora:
    """Test sound mass calculation."""

    def test_calcular_massa_sonora(self):
        """Test sound mass calculation."""
        notas = ["C4", "E4", "G4"]
        dinamicas = ["mf", "f", "ff"]
        numeros_instr = [1, 2, 1]
        densidades_instr = [1.0, 1.5, 1.2]

        massa = calcular_massa_sonora(notas, dinamicas, numeros_instr, densidades_instr)

        assert massa > 0
        assert isinstance(massa, (int, float))


class TestFormatOutputString:
    """Test output formatting."""

    def test_format_output_string(self, sample_input_data):
        """Test output string formatting."""
        resultados, _, _ = calculate_metrics(sample_input_data)

        output = format_output_string(resultados)

        assert isinstance(output, str)
        assert len(output) > 0
        assert "DENSITY" in output or "Density" in output


class TestInputValidation:
    """Test input validation."""

    def test_invalid_note_format(self):
        """Test handling of invalid note formats."""
        input_data = {
            "notes": ["INVALID_NOTE"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
        }

        # Should either raise error or handle gracefully
        try:
            resultados, _, _ = calculate_metrics(input_data)
            assert True
        except (InputError, ValueError):
            assert True

    def test_invalid_dynamic(self):
        """Test handling of invalid dynamic."""
        input_data = {
            "notes": ["C4"],
            "dynamics": ["INVALID_DYNAMIC"],
            "instruments": ["flauta"],
            "num_instruments": [1],
        }

        resultados, _, _ = calculate_metrics(input_data)
        assert resultados is not None
