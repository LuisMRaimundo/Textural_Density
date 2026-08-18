"""B4: compute_composite_from_blend is a thin wrapper on the production formula."""

from __future__ import annotations

from core.composite import compute_composite_from_blend
from core.pitch_structure import compute_composite_vertical_density


def test_compute_composite_from_blend_delegates_identically():
    for blend, mass, ref, logged in (
        (1.8318962800717329, 58.0918049, 193.0, True),
        (0.0, 10.0, 193.0, True),
        (10.0, 4.0, 193.0, False),
    ):
        total, _ = compute_composite_vertical_density(
            blend, mass, ref, apply_log_compression=logged
        )
        wrapped = compute_composite_from_blend(
            blend, mass, ref, use_log_compression=logged
        )
        assert wrapped == total
