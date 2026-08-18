"""A1: interval-density return is a mean of decay terms, then log10-capped."""

from __future__ import annotations

import math
import random

import pytest

from config import USE_LOG_COMPRESSION
from core.pitch_structure import (
    calculate_interval_density_from_distinct_midis,
    normalize_interval_density,
)
from densidade_intervalar import modified_exponential_decay


LOG10_2 = math.log10(2.0)


def test_use_log_compression_is_on():
    assert USE_LOG_COMPRESSION is True


def test_decay_terms_are_at_most_one():
    for delta in (0.0, 0.5, 1.0, 12.0, 24.0, 48.0):
        assert modified_exponential_decay(delta) <= 1.0


def test_normalize_interval_density_is_mean_then_log10():
    midis = [60.0, 64.0, 67.0]
    n = len(midis)
    raw = calculate_interval_density_from_distinct_midis(midis)
    mean = 2.0 * raw / (n * (n - 1))
    assert mean <= 1.0
    expected = math.log10(1.0 + mean)
    assert normalize_interval_density(raw, n) == pytest.approx(expected, abs=1e-12)
    assert expected <= LOG10_2


def test_normalize_interval_density_bounded_by_log10_2_random_midi_sets():
    """Property: random MIDI sets of size 2..40 stay <= log10(2)."""
    rng = random.Random(20260818)
    for _ in range(250):
        n = rng.randint(2, 40)
        midis = [rng.uniform(0.0, 127.0) for _ in range(n)]
        raw = calculate_interval_density_from_distinct_midis(midis)
        mean = 2.0 * raw / (n * (n - 1))
        assert mean <= 1.0 + 1e-12
        value = normalize_interval_density(raw, n)
        assert value <= LOG10_2 + 1e-12
        assert value == pytest.approx(math.log10(1.0 + mean), abs=1e-12)
