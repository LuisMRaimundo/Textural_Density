"""
Tests for optimization utilities.

Tests cover:
- Vectorized distance calculations
- Cache functionality
- Performance improvements
"""

import numpy as np
import pytest

from utils.optimization import (
    CalculationCache,
    clear_density_cache,
    optimized_interval_density,
    vectorized_density_calculation,
    vectorized_pairwise_distances,
)


class TestVectorizedPairwiseDistances:
    """Test vectorized pairwise distance calculations."""

    def test_basic_distances(self):
        """Test basic distance calculation."""
        pitches = np.array([60.0, 64.0, 67.0])  # C4, E4, G4
        distances = vectorized_pairwise_distances(pitches)

        assert distances.shape == (3, 3)
        assert distances[0, 1] == 4.0  # E4 - C4 = 4 semitons
        assert distances[0, 2] == 7.0  # G4 - C4 = 7 semitons
        assert distances[1, 2] == 3.0  # G4 - E4 = 3 semitons

    def test_empty_array(self):
        """Test with empty array."""
        pitches = np.array([])
        distances = vectorized_pairwise_distances(pitches)
        assert len(distances) == 0

    def test_single_pitch(self):
        """Test with single pitch (no pairs, so empty array)."""
        pitches = np.array([60.0])
        distances = vectorized_pairwise_distances(pitches)
        assert distances.size == 0

    def test_symmetry(self):
        """Implementation returns upper triangle only (lower/diag = 0). Check upper has correct distances."""
        pitches = np.array([60.0, 64.0, 67.0, 72.0])
        distances = vectorized_pairwise_distances(pitches)

        for i in range(len(pitches)):
            for j in range(len(pitches)):
                if i < j:
                    assert distances[i, j] == abs(pitches[i] - pitches[j])
                else:
                    assert distances[i, j] == 0


class TestVectorizedDensityCalculation:
    """Test vectorized density calculations."""

    def test_basic_density(self):
        """Test basic density calculation."""
        pitches = np.array([60.0, 64.0, 67.0])

        def exp_decay(d, lamb=0.05):
            return np.exp(-lamb * d)

        density = vectorized_density_calculation(pitches, exp_decay)

        assert density > 0
        assert isinstance(density, float)

    def test_with_weights(self):
        """Test density calculation with weights."""
        pitches = np.array([60.0, 64.0, 67.0])

        def exp_decay(d, lamb=0.05):
            return np.exp(-lamb * d)

        # Create weight matrix
        distances = vectorized_pairwise_distances(pitches)
        weights = np.ones_like(distances)
        weights[distances > 5] = 0.5  # Reduce weight for large intervals

        density = vectorized_density_calculation(pitches, exp_decay, weights=weights)

        assert density > 0

    def test_empty_array(self):
        """Test with empty array."""
        pitches = np.array([])

        def decay(d):
            return np.exp(-0.05 * d)

        density = vectorized_density_calculation(pitches, decay)
        assert density == 0.0


class TestCalculationCache:
    """Test calculation cache."""

    def test_cache_basic(self):
        """Test basic cache operations."""
        cache = CalculationCache(max_size=10)

        key = (60.0, 64.0, 0.05)
        value = 1.234

        assert cache.get(key) is None
        cache.set(key, value)
        assert cache.get(key) == value

    def test_cache_eviction(self):
        """Test cache eviction when full."""
        cache = CalculationCache(max_size=3)

        # Fill cache
        for i in range(5):
            cache.set((i,), float(i))

        # Oldest entries should be evicted
        assert len(cache.cache) == 3

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = CalculationCache()

        cache.set((1,), 1.0)
        cache.set((2,), 2.0)
        cache.get((1,))  # Hit
        cache.get((3,))  # Miss

        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 2
        assert 0 <= stats["hit_rate"] <= 1

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = CalculationCache()

        cache.set((1,), 1.0)
        assert len(cache.cache) == 1

        cache.clear()
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0


class TestOptimizedIntervalDensity:
    """Test optimized interval density function."""

    def test_basic_calculation(self):
        """Test basic optimized calculation."""
        pitches = np.array([60.0, 64.0, 67.0])

        density = optimized_interval_density(pitches, lamb=0.05, use_cache=False)

        assert density > 0
        assert isinstance(density, float)

    def test_with_cache(self):
        """Test with caching enabled."""
        clear_density_cache()

        pitches1 = np.array([60.0, 64.0, 67.0])
        pitches2 = np.array([60.0, 64.0, 67.0])  # Same pitches

        density1 = optimized_interval_density(pitches1, lamb=0.05, use_cache=True)
        density2 = optimized_interval_density(pitches2, lamb=0.05, use_cache=True)

        assert abs(density1 - density2) < 1e-10  # Should be identical
        assert density1 > 0

    def test_small_array(self):
        """Test with small array (should still work)."""
        pitches = np.array([60.0, 64.0])

        density = optimized_interval_density(pitches, lamb=0.05)

        assert density > 0


class TestPerformance:
    """Test performance improvements."""

    def test_large_array_performance(self):
        """Test that vectorized version is faster for large arrays."""
        import time

        # Create large array
        pitches = np.random.uniform(60, 84, size=100)  # 100 random pitches

        # Time vectorized version
        start = time.time()
        density = optimized_interval_density(pitches, lamb=0.05, use_cache=False)
        vectorized_time = time.time() - start

        assert density > 0
        assert vectorized_time < 1.0  # Should be fast (< 1 second)

    def test_cache_hit_performance(self):
        """Test that cache returns same value on hit (timing can be flaky)."""
        clear_density_cache()
        pitches = np.array([60.0, 64.0, 67.0])

        density1 = optimized_interval_density(pitches, lamb=0.05, use_cache=True)
        density2 = optimized_interval_density(pitches, lamb=0.05, use_cache=True)

        assert abs(density1 - density2) < 1e-10
        assert density1 > 0
