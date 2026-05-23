"""
Optimization utilities for density calculations.

This module provides optimized implementations of common operations,
including vectorized distance calculations and caching mechanisms.
"""

import numpy as np
from functools import lru_cache
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def vectorized_pairwise_distances(pitches: np.ndarray) -> np.ndarray:
    """
    Calculate pairwise distances using vectorized numpy operations.
    
    This is much faster than nested loops for large arrays.
    
    Args:
        pitches: Array of MIDI pitch values (1D array)
    
    Returns:
        Upper triangular matrix of pairwise distances (excluding diagonal)
        Shape: (n, n) where n = len(pitches)
    
    Example:
        >>> pitches = np.array([60.0, 64.0, 67.0])
        >>> distances = vectorized_pairwise_distances(pitches)
        >>> # distances[i, j] = |pitches[i] - pitches[j]| for i < j
    """
    if len(pitches) < 2:
        return np.array([])
    
    # Vectorized calculation: broadcast subtraction
    # Creates matrix where distances[i, j] = pitches[i] - pitches[j]
    distances = np.abs(pitches[:, np.newaxis] - pitches[np.newaxis, :])
    
    # Return only upper triangle (i < j) to avoid duplicates
    return np.triu(distances, k=1)


def vectorized_density_calculation(
    pitches: np.ndarray,
    decay_func: callable,
    weights: Optional[np.ndarray] = None
) -> float:
    """
    Calculate interval density using vectorized operations.
    
    This replaces O(N²) nested loops with vectorized numpy operations,
    providing significant speedup for large note sets.
    
    Args:
        pitches: Array of MIDI pitch values
        decay_func: Function that takes distance and returns density contribution
        weights: Optional array of weights for each pitch pair
    
    Returns:
        Total interval density
    
    Example:
        >>> pitches = np.array([60.0, 64.0, 67.0])
        >>> def exp_decay(d, lamb=0.05):
        ...     return np.exp(-lamb * d)
        >>> density = vectorized_density_calculation(pitches, exp_decay)
    """
    if len(pitches) < 2:
        return 0.0
    
    # Calculate all pairwise distances at once
    distances = vectorized_pairwise_distances(pitches)
    
    # Apply decay function to all distances
    # Only process upper triangle (non-zero values)
    mask = distances > 0
    density_contributions = np.zeros_like(distances)
    density_contributions[mask] = decay_func(distances[mask])
    
    # Apply weights if provided
    if weights is not None:
        if weights.shape == distances.shape:
            density_contributions *= weights
        else:
            logger.warning("Weights shape mismatch, ignoring weights")
    
    # Sum all contributions
    return float(np.sum(density_contributions))


@lru_cache(maxsize=128)
def cached_decay_function(distance: float, lamb: float = 0.05) -> float:
    """
    Cached exponential decay function.
    
    Args:
        distance: Interval distance
        lamb: Decay parameter
    
    Returns:
        Decay value
    """
    return float(np.exp(-lamb * distance))


class CalculationCache:
    """
    Cache for expensive calculations.
    
    Useful for repeated calculations with same inputs.
    """
    
    def __init__(self, max_size: int = 256):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: Tuple) -> Optional[float]:
        """Get cached value."""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: Tuple, value: float) -> None:
        """Set cached value."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self) -> dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'size': len(self.cache)
        }


# Global cache instance
_density_cache = CalculationCache(max_size=512)


def get_density_cache() -> CalculationCache:
    """Get global density calculation cache."""
    return _density_cache


def clear_density_cache() -> None:
    """Clear global density calculation cache."""
    _density_cache.clear()


def optimized_interval_density(
    pitches: np.ndarray,
    lamb: float = 0.05,
    use_cache: bool = True
) -> float:
    """
    Optimized interval density calculation.
    
    Uses vectorized operations and optional caching for maximum performance.
    
    Args:
        pitches: Array of MIDI pitch values
        lamb: Decay parameter
        use_cache: Whether to use caching
    
    Returns:
        Interval density value
    """
    if len(pitches) < 2:
        return 0.0
    
    # Create cache key
    cache_key = (tuple(pitches), lamb) if use_cache else None
    
    # Check cache
    if use_cache and cache_key:
        cached_value = _density_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
    
    # Vectorized calculation
    def decay_func(d: np.ndarray) -> np.ndarray:
        return np.exp(-lamb * d)
    
    density = vectorized_density_calculation(pitches, decay_func)
    
    # Cache result
    if use_cache and cache_key:
        _density_cache.set(cache_key, density)
    
    return density

