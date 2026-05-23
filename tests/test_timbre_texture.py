"""
Unit tests for timbre_texture_analysis.py module.

Tests cover:
- Texture density calculation
- Timbre blend calculation
- Orchestration balance
"""

import numpy as np
import pytest

from timbre_texture_analysis import (
    calculate_orchestration_balance,
    calculate_texture_density,
    calculate_timbre_blend,
)


class TestCalculateTextureDensity:
    """Test texture density calculation."""

    def test_basic_texture_density(self):
        """Test basic texture density calculation."""
        pitches = [60.0, 64.0, 67.0]
        instruments_counts = [1, 2, 1]

        result = calculate_texture_density(pitches, instruments_counts)

        assert "average_texture_density" in result
        assert "texture_polyphony" in result
        assert "texture_variability" in result
        assert "texture_contrast" in result
        assert result["average_texture_density"] == 4  # 1+2+1
        assert result["pitch_polyphony"] == 3  # distinct pitch bins
        assert result["texture_polyphony"] == 3  # alias: distinct pitches, not mean Qty
        assert result["player_count"] == 4

    def test_empty_input(self):
        """Test with empty input."""
        result = calculate_texture_density([], [])

        assert result["average_texture_density"] == 0
        assert result["texture_polyphony"] == 0
        assert result["pitch_polyphony"] == 0
        assert result["player_count"] == 0
        assert result["texture_variability"] == 0
        assert result["texture_contrast"] == 0

    def test_single_pitch(self):
        """Test with single pitch."""
        pitches = [60.0]
        instruments_counts = [2]

        result = calculate_texture_density(pitches, instruments_counts)

        assert result["average_texture_density"] == 2
        assert result["player_count"] == 2
        assert result["pitch_polyphony"] == 1
        assert result["texture_polyphony"] == 1
        assert result["texture_variability"] == 0  # No spread for single point
        assert result["texture_contrast"] == 0

    def test_texture_contrast(self):
        """Test texture contrast calculation."""
        pitches = [60.0, 84.0]  # C4 to C6 (2 octaves)
        instruments_counts = [1, 1]

        result = calculate_texture_density(pitches, instruments_counts)

        assert result["texture_contrast"] == 24.0  # 84 - 60 = 24 semitons

    def test_numpy_arrays(self):
        """Test with numpy arrays."""
        pitches = np.array([60.0, 64.0, 67.0])
        instruments_counts = np.array([1, 2, 1])

        result = calculate_texture_density(pitches, instruments_counts)

        assert result["average_texture_density"] == 4


class TestCalculateTimbreBlend:
    """Test timbre blend calculation."""

    def test_basic_timbre_blend(self):
        """Test basic timbre blend calculation."""
        instruments = ["flauta", "clarinete", "flauta"]
        densities = [1.0, 1.5, 1.2]

        result = calculate_timbre_blend(instruments, densities)

        assert "timbre_diversity" in result
        assert "timbre_balance" in result
        assert "timbre_dominance" in result
        # timbre_diversity = unique_instruments / total (ratio 0–1)
        assert result["timbre_diversity"] == pytest.approx(2 / 3)  # 2 unique of 3

    def test_single_instrument(self):
        """Test with single instrument type."""
        instruments = ["flauta", "flauta", "flauta"]
        densities = [1.0, 1.5, 1.2]

        result = calculate_timbre_blend(instruments, densities)

        # timbre_diversity = unique/total = 1/3; single type => high blend => balance 1.0
        assert result["timbre_diversity"] == pytest.approx(1 / 3)
        assert result["timbre_balance"] == 1.0  # Perfect balance (single type)

    def test_empty_input(self):
        """Test with empty input."""
        result = calculate_timbre_blend([], [])

        assert result["timbre_diversity"] == 0
        assert result["timbre_balance"] == 0.0

    def test_timbre_dominance(self):
        """Test timbre dominance calculation."""
        instruments = ["flauta", "clarinete", "flauta", "flauta"]
        densities = [1.0, 1.5, 1.2, 1.3]

        result = calculate_timbre_blend(instruments, densities)

        # Flauta should dominate (3 occurrences vs 1)
        assert result["timbre_dominance"] > 0.5


class TestCalculateOrchestrationBalance:
    """Test orchestration balance calculation."""

    def test_basic_orchestration_balance(self):
        """Test basic orchestration balance."""
        pitches = [60.0, 64.0, 67.0]
        densities = [1.0, 1.5, 1.2]
        instruments = ["flauta", "clarinete", "flauta"]

        result = calculate_orchestration_balance(pitches, densities, instruments)

        assert "orchestration_balance" in result
        assert "pitch_balance" in result
        assert "instrument_balance" in result

    def test_empty_input(self):
        """Test with empty input."""
        result = calculate_orchestration_balance([], [], [])

        assert "orchestration_balance" in result
        assert result["orchestration_balance"] == 0.0 or result["orchestration_balance"] == 1.0


class TestEdgeCases:
    """Test edge cases."""

    def test_mismatched_lengths(self):
        """Test with mismatched array lengths."""
        pitches = [60.0, 64.0]
        instruments_counts = [1, 2, 1]  # Different length

        # Should handle gracefully or raise error
        try:
            result = calculate_texture_density(pitches, instruments_counts)
            # If no error, result should be valid
            assert "average_texture_density" in result
        except (ValueError, IndexError):
            # Error is acceptable
            assert True

    def test_negative_values(self):
        """Test handling of negative values."""
        pitches = [60.0, 64.0]
        instruments_counts = [-1, 2]  # Negative count

        # Should handle gracefully (treat as 0 or raise error)
        try:
            result = calculate_texture_density(pitches, instruments_counts)
            assert result["average_texture_density"] >= 0
        except ValueError:
            # Error is acceptable
            assert True
