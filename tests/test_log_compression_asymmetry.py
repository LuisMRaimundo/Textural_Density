"""Log compression applies to the composite only, not to DV."""

from __future__ import annotations

import math

import pytest

from config import USE_LOG_COMPRESSION
from core.composite import INSTRUMENT_BLEND_DIVISOR, compute_blend_density
from core.pitch_structure import (
    calculate_interval_density_from_distinct_midis,
    compute_composite_vertical_density,
    effective_interval_cardinality,
)


def test_log_compression_flag_remains_on():
    assert USE_LOG_COMPRESSION is True


def test_interval_cardinality_is_not_log_compressed():
    midis = [60.0, 64.0, 67.0]
    raw = calculate_interval_density_from_distinct_midis(midis)
    dv = effective_interval_cardinality(raw, len(midis))
    closed = (math.sqrt(1.0 + 8.0 * raw) - 1.0) / 2.0
    assert dv == pytest.approx(closed, abs=1e-12)
    assert dv != pytest.approx(math.log10(1.0 + closed), rel=1e-3)


def test_composite_applies_log_compression():
    total, pre_log = compute_composite_vertical_density(
        10.0, 4.0, 193.0, apply_log_compression=True
    )
    assert pre_log == pytest.approx(10.0 * 2.0 / 193.0, abs=1e-12)
    assert total == pytest.approx(math.log10(1.0 + pre_log), abs=1e-12)
    assert total != pytest.approx(pre_log, rel=1e-3)


def test_blend_is_fixed_divisor_not_logged_di():
    di = 34.50033721929513
    dv = 1.85
    blend = compute_blend_density(di, dv, w=0.5)
    expected = 0.5 * di / INSTRUMENT_BLEND_DIVISOR + 0.5 * dv
    assert blend == pytest.approx(expected, abs=1e-12)
    logged_di_blend = 0.5 * math.log10(1.0 + di) / INSTRUMENT_BLEND_DIVISOR + 0.5 * dv
    assert blend != pytest.approx(logged_di_blend, rel=1e-3)
