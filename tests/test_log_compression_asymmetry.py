"""C3: pin the known double log-compression of DV vs uncompressed DI."""

from __future__ import annotations

import math

import pytest

from config import USE_LOG_COMPRESSION
from core.composite import WEIGHTED_DI_MAX, WEIGHTED_DV_MAX, compute_blend_density
from core.pitch_structure import (
    calculate_interval_density_from_distinct_midis,
    compute_composite_vertical_density,
    normalize_interval_density,
)


def test_log_compression_flag_remains_on():
    assert USE_LOG_COMPRESSION is True


def test_interval_density_is_log_compressed_before_blend():
    midis = [60.0, 64.0, 67.0]
    raw = calculate_interval_density_from_distinct_midis(midis)
    mean = 2.0 * raw / (len(midis) * (len(midis) - 1))
    dv = normalize_interval_density(raw, len(midis))
    assert dv == pytest.approx(math.log10(1.0 + mean), abs=1e-12)
    assert dv != pytest.approx(mean, rel=1e-3)


def test_composite_applies_log_compression_a_second_time():
    total, pre_log = compute_composite_vertical_density(
        10.0, 4.0, 193.0, apply_log_compression=True
    )
    assert pre_log == pytest.approx(10.0 * 2.0 / 193.0, abs=1e-12)
    assert total == pytest.approx(math.log10(1.0 + pre_log), abs=1e-12)
    assert total != pytest.approx(pre_log, rel=1e-3)


def test_instrument_density_is_not_log_compressed_in_the_blend():
    """DI enters the blend raw; DV has already been log-compressed."""
    di = 34.50033721929513
    dv = 0.2137588382139519
    blend = compute_blend_density(di, dv, w=0.5)
    expected = 10.0 * (0.5 * di / WEIGHTED_DI_MAX + 0.5 * dv / WEIGHTED_DV_MAX)
    assert blend == pytest.approx(expected, abs=1e-12)
    # A log on DI would move the blend; this pin forbids that accidental change.
    logged_di_blend = 10.0 * (
        0.5 * math.log10(1.0 + di) / WEIGHTED_DI_MAX + 0.5 * dv / WEIGHTED_DV_MAX
    )
    assert blend != pytest.approx(logged_di_blend, rel=1e-3)
