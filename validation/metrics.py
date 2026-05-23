"""
Statistical comparison utilities for empirical validation (Phase 8).

Used when expert annotations or listening-test data are supplied.
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np
from scipy import stats


def spearman_correlation(
    predicted: Sequence[float],
    observed: Sequence[float],
) -> tuple[float, float]:
    """Return (rho, p_value). Requires at least 3 paired samples."""
    x = np.asarray(predicted, dtype=float)
    y = np.asarray(observed, dtype=float)
    if x.size != y.size:
        raise ValueError("predicted and observed must have the same length")
    if x.size < 3:
        raise ValueError("Spearman correlation requires at least 3 samples")
    rho, p_value = stats.spearmanr(x, y)
    return float(rho), float(p_value)


def kendall_tau(
    predicted: Sequence[float],
    observed: Sequence[float],
) -> tuple[float, float]:
    """Return (tau, p_value). Requires at least 3 paired samples."""
    x = np.asarray(predicted, dtype=float)
    y = np.asarray(observed, dtype=float)
    if x.size != y.size:
        raise ValueError("predicted and observed must have the same length")
    if x.size < 3:
        raise ValueError("Kendall tau requires at least 3 samples")
    tau, p_value = stats.kendalltau(x, y)
    return float(tau), float(p_value)


def root_mean_square_error(
    predicted: Sequence[float],
    observed: Sequence[float],
) -> float:
    x = np.asarray(predicted, dtype=float)
    y = np.asarray(observed, dtype=float)
    if x.size != y.size:
        raise ValueError("predicted and observed must have the same length")
    if x.size == 0:
        raise ValueError("empty input")
    return float(np.sqrt(np.mean((x - y) ** 2)))


def mean_absolute_error(
    predicted: Sequence[float],
    observed: Sequence[float],
) -> float:
    x = np.asarray(predicted, dtype=float)
    y = np.asarray(observed, dtype=float)
    if x.size != y.size:
        raise ValueError("predicted and observed must have the same length")
    if x.size == 0:
        raise ValueError("empty input")
    return float(np.mean(np.abs(x - y)))


def bootstrap_ci(
    values: Sequence[float],
    *,
    n_bootstrap: int = 2000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """
    Bootstrap confidence interval for the mean.

    Returns (mean, lower, upper).
    """
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError("empty input")
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n_bootstrap):
        sample = rng.choice(arr, size=arr.size, replace=True)
        means.append(float(np.mean(sample)))
    alpha = 1.0 - confidence
    lower = float(np.quantile(means, alpha / 2))
    upper = float(np.quantile(means, 1 - alpha / 2))
    return float(np.mean(arr)), lower, upper


def krippendorff_alpha_placeholder(
    ratings_matrix: np.ndarray,
) -> Optional[float]:
    """
    Placeholder for inter-rater reliability.

    Returns None with insufficient data; full implementation deferred until
    multi-rater annotation corpora exist in the repository.
    """
    matrix = np.asarray(ratings_matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return None
    # Minimal fallback: mean pairwise Pearson as rough agreement hint only.
    rows = [matrix[i, :] for i in range(matrix.shape[0])]
    correlations = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if np.std(rows[i]) > 0 and np.std(rows[j]) > 0:
                r = float(np.corrcoef(rows[i], rows[j])[0, 1])
                correlations.append(r)
    if not correlations:
        return None
    return float(np.mean(correlations))
