"""B1: harmonic membership uses a symmetric octave-class distance."""

from __future__ import annotations

import pytest

from spectral_analysis import calculate_harmonic_ratio


def _pair_ratio(interval: float, *, fundamental: float = 60.0) -> float:
    return calculate_harmonic_ratio(
        [fundamental, fundamental + interval],
        [1.0, 1.0],
    )


@pytest.mark.parametrize(
    "interval, harmonic",
    [
        (11.80, True),   # oct_dist = 0.20
        (11.85, True),   # oct_dist = 0.15 (old modulo+isclose rejected this)
        (11.90, True),   # oct_dist = 0.10
        (12.00, True),
        (12.10, True),
        (23.85, True),   # 23.85 % 12 = 11.85, oct_dist = 0.15
        (11.74, False),  # oct_dist = 0.26, just outside
        (4.00, False),
    ],
)
def test_octave_class_distance_symmetric(interval: float, harmonic: bool):
    ratio = _pair_ratio(interval)
    assert ratio == pytest.approx(1.0 if harmonic else 0.5)


def test_negative_intervals_when_fundamental_is_above():
    # Interval −11.85 wraps to 0.15 — accepted by both old and new rules.
    assert _pair_ratio(-11.85, fundamental=72.0) == pytest.approx(1.0)
    # Interval −12.15 wraps to 11.85 — old one-sided rule rejected this.
    assert _pair_ratio(-12.15, fundamental=72.0) == pytest.approx(1.0)
    assert _pair_ratio(-12.00, fundamental=72.0) == pytest.approx(1.0)
    assert _pair_ratio(-7.00, fundamental=72.0) == pytest.approx(0.5)
