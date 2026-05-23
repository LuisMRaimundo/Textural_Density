"""
Registral density / compactness — score-derived register metrics.

Low-risk core-native extraction from subindices registral block.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from config import DEFAULT_REGISTER_BANDS
from core.models import VerticalSlice


def register_band_occupancy(
    midis: list[float],
    bands: dict[str, tuple[int, int]],
) -> dict[str, float]:
    """Fraction of events per register band (documented bands from config by default)."""
    counts = {name: 0 for name in bands}
    for midi in midis:
        for name, (low, high) in bands.items():
            if low <= midi < high:
                counts[name] += 1
                break
    total = sum(counts.values()) or 1
    return {name: counts[name] / total for name in bands}


def register_entropy(proportions: dict[str, float]) -> float:
    values = [p for p in proportions.values() if p > 0]
    if len(values) <= 1:
        return 0.0
    return float(-sum(p * np.log2(p) for p in values))


def compute_registral_density(
    vertical_slice: VerticalSlice,
    pitch_span_semitones: float,
    register_bands: dict[str, tuple[int, int]] | None = None,
) -> dict[str, Any]:
    """
    Score-derived registral metrics for a vertical slice.

    Registral compactness decreases as pitch span widens (all else equal).
    """
    bands = register_bands or dict(DEFAULT_REGISTER_BANDS)
    midis = [float(ev.sounding_pitch.midi) for ev in vertical_slice.events]
    event_count = len(midis)
    band_occupancy = register_band_occupancy(midis, bands)
    entropy = register_entropy(band_occupancy)
    max_entropy = np.log2(len(bands)) if len(bands) > 1 else 1.0
    entropy_norm = entropy / max_entropy if max_entropy > 0 else 0.0
    dispersion = pitch_span_semitones / max(1, event_count - 1) if event_count > 1 else 0.0
    compression = 1.0 / (1.0 + pitch_span_semitones)

    return {
        "pitch_span_semitones": float(pitch_span_semitones),
        "register_band_occupancy": band_occupancy,
        "register_bands_config": {k: list(v) for k, v in bands.items()},
        "register_entropy": entropy,
        "register_entropy_normalized": float(entropy_norm),
        "registral_dispersion": float(dispersion),
        "registral_compression": float(compression),
        "source_type": "score_derived",
        "validation_status": "verified_by_tests",
        "interpretation": (
            "Register spread and band occupancy from symbolic MIDI pitches; "
            "distinct from interval compactness."
        ),
    }
