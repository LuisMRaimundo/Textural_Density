"""
Unit tests for spectral_analysis.py module.

Tests cover:
- Spectral moments calculation
- Chroma vector calculation
- Harmonic ratio
- Extended spectral moments
"""

import numpy as np
import pytest

from spectral_analysis import (
    calculate_chroma_vector,
    calculate_extended_spectral_moments,
    calculate_harmonic_ratio,
    calculate_spectral_moments,
    robust_gaussian_kde,
)


class TestCalculateSpectralMoments:
    """Test spectral moments calculation."""

    def test_basic_spectral_moments(self):
        """Test basic spectral moments calculation."""
        pitches = [60.0, 64.0, 67.0]  # C4, E4, G4
        amplitudes = [1.0, 1.5, 1.2]

        result = calculate_spectral_moments(pitches, amplitudes)

        assert "centroid" in result
        assert "spread" in result
        assert "spectral_skewness" in result
        assert result["centroid"]["frequency"] > 0

    def test_empty_input(self):
        """Test with empty input."""
        result = calculate_spectral_moments([], [])

        assert result["centroid"]["frequency"] == 0.0
        assert result["spread"]["deviation"] == 0.0

    def test_single_pitch(self):
        """Test with single pitch."""
        pitches = [60.0]
        amplitudes = [1.0]

        result = calculate_spectral_moments(pitches, amplitudes)

        assert result["centroid"]["frequency"] > 0
        assert result["spread"]["deviation"] == 0.0  # No spread for single point

    def test_numpy_arrays(self):
        """Test with numpy arrays."""
        pitches = np.array([60.0, 64.0, 67.0])
        amplitudes = np.array([1.0, 1.5, 1.2])

        result = calculate_spectral_moments(pitches, amplitudes)

        assert result["centroid"]["frequency"] > 0

    def test_centroid_calculation(self):
        """Test centroid calculation accuracy."""
        pitches = [60.0, 72.0]  # C4, C5 (octave apart)
        amplitudes = [1.0, 1.0]

        result = calculate_spectral_moments(pitches, amplitudes)

        # Centroid frequency (Hz) should be between C4 and C5 (~262–523 Hz)
        centroid_hz = result["centroid"]["frequency"]
        assert 262 < centroid_hz < 523


class TestCalculateExtendedSpectralMoments:
    """Test extended spectral moments."""

    def test_extended_moments(self):
        """Test extended spectral moments calculation."""
        pitches = [60.0, 64.0, 67.0, 72.0]
        amplitudes = [1.0, 1.5, 1.2, 1.8]

        result = calculate_extended_spectral_moments(pitches, amplitudes)

        assert "centroid" in result
        assert "spread" in result
        assert "spectral_skewness" in result
        assert "spectral_kurtosis" in result

    def test_kurtosis_range(self):
        """Test that kurtosis is in reasonable range."""
        pitches = np.random.uniform(60, 84, size=20)
        amplitudes = np.random.uniform(0.5, 2.0, size=20)

        result = calculate_extended_spectral_moments(pitches, amplitudes)

        kurtosis = result["spectral_kurtosis"]
        assert -10 < kurtosis < 10  # Reasonable range


class TestCalculateChromaVector:
    """Test chroma vector calculation."""

    def test_chroma_vector_basic(self):
        """Test basic chroma vector calculation."""
        pitches = [60.0, 64.0, 67.0]  # C4, E4, G4
        amplitudes = [1.0, 1.5, 1.2]

        chroma = calculate_chroma_vector(pitches, amplitudes)

        assert len(chroma) == 12  # 12 pitch classes
        assert np.all(np.array(chroma) >= 0)  # All values non-negative
        assert abs(sum(chroma) - 1.0) < 0.01  # Normalised to sum 1

    def test_chroma_vector_sum(self):
        """Test that chroma vector sums correctly."""
        pitches = [60.0, 72.0]  # C4, C5 (same chroma)
        amplitudes = [1.0, 1.0]

        chroma = calculate_chroma_vector(pitches, amplitudes)

        # Both C notes → all energy in C chroma bin; normalised so sum=1
        assert chroma[0] > 0  # C is index 0
        assert abs(chroma[0] - 1.0) < 0.01  # Single chroma class


class TestCalculateHarmonicRatio:
    """Test harmonic ratio calculation."""

    def test_harmonic_ratio_basic(self):
        """Test basic harmonic ratio calculation."""
        pitches = [60.0, 64.0, 67.0]  # C4, E4, G4 (major triad)
        amplitudes = [1.0, 1.5, 1.2]

        ratio = calculate_harmonic_ratio(pitches, amplitudes)

        assert 0 <= ratio <= 1  # Should be normalized
        assert isinstance(ratio, (float, np.floating))

    def test_harmonic_ratio_empty(self):
        """Test with empty input."""
        ratio = calculate_harmonic_ratio([], [])

        assert ratio == 0.0 or np.isnan(ratio)


class TestRobustGaussianKde:
    """KDE helper should tolerate singular covariance (jitter path)."""

    def test_well_conditioned_data(self):
        data = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
        kde = robust_gaussian_kde(data)
        assert kde is not None

    def test_singular_triggers_jitter_path(self):
        # Identical samples → singular covariance; must not raise
        data = np.array([[1.0, 1.0, 1.0]])
        kde = robust_gaussian_kde(data)
        assert kde is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_nan_handling(self):
        """Test handling of NaN values."""
        pitches = [60.0, np.nan, 67.0]
        amplitudes = [1.0, 1.5, 1.2]

        # Should handle NaN gracefully
        result = calculate_spectral_moments(pitches, amplitudes)
        assert not np.isnan(result["centroid"]["frequency"])

    def test_inf_handling(self):
        """Test handling of infinite values."""
        pitches = [60.0, np.inf, 67.0]
        amplitudes = [1.0, 1.5, 1.2]

        # Should handle inf gracefully (nan_to_num or similar may produce large finite)
        result = calculate_spectral_moments(pitches, amplitudes)
        assert "centroid" in result
        freq = result["centroid"]["frequency"]
        assert freq >= 0 and (np.isfinite(freq) or np.isinf(freq))

    def test_mismatched_lengths(self):
        """Test with mismatched array lengths."""
        pitches = [60.0, 64.0]
        amplitudes = [1.0, 1.5, 1.2]  # Different length

        # Should handle gracefully or raise error
        try:
            result = calculate_spectral_moments(pitches, amplitudes)
            # If no error, check result is valid
            assert "centroid" in result
        except (ValueError, IndexError):
            # Error is acceptable
            assert True
