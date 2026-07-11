"""
Vertical pitch-structure density (distinct pitch bins only).

Separates orchestral mass from pitch-structure diversity. Exact unison doublings
contribute to mass descriptors but not to interval compactness, spectral entropy,
registral diversity, or composite vertical pitch-structure density.
"""

from __future__ import annotations

import numpy as np

from config import COMPOSITE_HARMONIC_DAMPING, USE_LOG_COMPRESSION
from core.pitch_aggregation import PitchAggregationResult
from densidade_intervalar import load_calibrated_parameters, modified_exponential_decay


def calculate_interval_density_from_distinct_midis(
    midis: list[float],
    lamb: float | None = None,
) -> float:
    """
    Pairwise interval sum over distinct MIDI pitch bins (no duplicate unison pairs).

    Low-level ``modified_exponential_decay`` is unchanged; only distinct-bin pairs are counted.
    """
    if len(midis) < 2:
        return 0.0
    if lamb is None:
        lamb = load_calibrated_parameters()
    total = 0.0
    n = len(midis)
    for i in range(n):
        for j in range(i + 1, n):
            delta_semitones = abs(float(midis[i]) - float(midis[j]))
            delta = delta_semitones * 2.0
            total += modified_exponential_decay(delta, lamb)
    return float(total)


def normalize_interval_density(raw: float, distinct_pitch_count: int) -> float:
    """Mean pairwise normalization over distinct pitch bins."""
    if distinct_pitch_count < 2:
        return 0.0
    n = distinct_pitch_count
    normalized = float(2.0 * raw / (n * (n - 1)))
    if USE_LOG_COMPRESSION:
        normalized = float(np.log10(1.0 + normalized))
    return normalized


def compute_interval_compactness_distinct(
    aggregation: PitchAggregationResult,
    lamb: float | None = None,
) -> tuple[float, float]:
    """Return (raw, normalized) interval compactness over distinct pitch bins."""
    midis = aggregation.bin_midis
    if aggregation.distinct_pitch_count < 2:
        return 0.0, 0.0
    raw = calculate_interval_density_from_distinct_midis(midis, lamb=lamb)
    reported = normalize_interval_density(raw, aggregation.distinct_pitch_count)
    return raw, reported


def compute_registral_span_distinct(aggregation: PitchAggregationResult) -> float:
    """Pitch span in semitones over distinct pitch bins."""
    if aggregation.distinct_pitch_count < 2:
        return 0.0
    midis = aggregation.bin_midis
    return float(max(midis) - min(midis))


def compute_registral_compactness(registral_span_semitones: float) -> float:
    """Bounded registral factor — no singular exemption at span = 0."""
    return 1.0 / (1.0 + registral_span_semitones / 12.0)


def compute_pitch_structure_density(
    *,
    interval_sum_raw: float,
    aggregation: PitchAggregationResult,
    spectral_entropy: float,
    harmonic_ratio: float,
) -> float:
    """Extensive pitch-structure density (distinct pitches required).

    Built from the accumulating raw pairwise interval sum, so adding a distinct
    note never decreases the value. Registral span is NOT applied here (the
    pairwise exponential decay already attenuates distant pairs); it remains a
    separately reported subindex.
    """
    if aggregation.distinct_pitch_count < 2:
        return 0.0
    entropy_factor = 1.0 + float(np.log1p(max(0.0, spectral_entropy)))
    harmonic_adjustment = 1.0 - float(harmonic_ratio) * COMPOSITE_HARMONIC_DAMPING
    return float(interval_sum_raw * entropy_factor * harmonic_adjustment)


def compute_composite_vertical_density(
    pitch_structure_density: float,
    sonic_mass: float,
    max_dens_global: float,
    apply_log_compression: bool = USE_LOG_COMPRESSION,
) -> tuple[float, float]:
    """
    Composite vertical density = pitch_structure × mass boost.

    Mass boost cannot alone produce high vertical pitch-structure density when
    ``pitch_structure_density`` is zero (exact unison case).
    """
    mass_boost = float(np.sqrt(max(0.0, sonic_mass)))
    pre_log = pitch_structure_density * mass_boost / float(max_dens_global)
    total = pre_log
    if apply_log_compression:
        total = float(np.log10(1.0 + pre_log))
    return float(total), float(pre_log)
