"""
Interval compactness — score-derived pairwise pitch-distance metric.

Pipeline uses distinct aggregated pitch bins; this module exposes helpers for
tests and subindex assembly.
"""

from __future__ import annotations

from typing import Any

from core.pitch_aggregation import PitchAggregationResult, aggregate_events_by_pitch
from core.pitch_structure import compute_interval_compactness_distinct


def compute_interval_compactness(notes: list[str]) -> dict[str, Any]:
    """Compute interval compactness over distinct aggregated pitch bins."""
    agg = aggregate_events_by_pitch(notes)
    raw, reported = compute_interval_compactness_distinct(agg)
    return {
        "value": float(reported),
        "raw": float(raw),
        "source_type": "score_derived",
        "validation_status": "verified_by_tests",
        "interpretation": (
            "Pairwise pitch-distance compactness from distinct aggregated pitch bins; "
            "exact unison doublings excluded."
        ),
        "distinct_pitch_count": agg.distinct_pitch_count,
        "interval_pairs_count_distinct": agg.interval_pairs_count_distinct,
    }


def compute_interval_compactness_from_aggregation(
    aggregation: PitchAggregationResult,
) -> dict[str, Any]:
    raw, reported = compute_interval_compactness_distinct(aggregation)
    return {
        "value": float(reported),
        "raw": float(raw),
        "distinct_pitch_count": aggregation.distinct_pitch_count,
        "interval_pairs_count_distinct": aggregation.interval_pairs_count_distinct,
    }
