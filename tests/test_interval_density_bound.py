"""Effective interval cardinality: formula and kernel bounds."""

from __future__ import annotations

import math
import random

import pytest

from core.pitch_structure import (
    calculate_interval_density_from_distinct_midis,
    effective_interval_cardinality,
)
from densidade_intervalar import modified_exponential_decay


def test_kernel_at_most_one_and_unison_is_one():
    assert modified_exponential_decay(0.0) == 1.0
    for delta in (0.5, 1.0, 12.0, 24.0, 48.0):
        k = modified_exponential_decay(delta)
        assert 0.0 < k <= 1.0


def test_effective_interval_cardinality_matches_closed_form():
    midis = [60.0, 64.0, 67.0]
    raw = calculate_interval_density_from_distinct_midis(midis)
    expected = (math.sqrt(1.0 + 8.0 * raw) - 1.0) / 2.0
    assert effective_interval_cardinality(raw, 3) == pytest.approx(expected, abs=1e-12)
    assert effective_interval_cardinality(raw, 1) == 0.0


def test_effective_cardinality_grows_with_random_additions():
    rng = random.Random(20260918)
    for _ in range(80):
        n = rng.randint(2, 12)
        midis = [rng.uniform(40.0, 90.0) for _ in range(n)]
        raw = calculate_interval_density_from_distinct_midis(midis)
        dv = effective_interval_cardinality(raw, n)
        extra = max(midis) + 1.5
        raw2 = calculate_interval_density_from_distinct_midis(midis + [extra])
        dv2 = effective_interval_cardinality(raw2, n + 1)
        assert dv2 > dv
