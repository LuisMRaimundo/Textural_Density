"""Unit tests for pitch aggregation utility."""

from __future__ import annotations

import pytest

from core.pitch_aggregation import aggregate_events_by_pitch


def test_four_unisons_one_bin():
    agg = aggregate_events_by_pitch(["C4", "C4", "C4", "C4"])
    assert agg.event_count == 4
    assert agg.distinct_pitch_count == 1
    assert agg.doubling_count == 3
    assert len(agg.pitch_bins) == 1
    assert agg.pitch_bins[0].event_count == 4
    assert agg.interval_pairs_count_distinct == 0


def test_enharmonic_same_bin():
    agg = aggregate_events_by_pitch(["C#4", "Db4"])
    assert agg.distinct_pitch_count == 1


def test_microtonal_distinct_bins():
    agg = aggregate_events_by_pitch(["C4", "C4+25c", "C#4-12c", "E4"])
    assert agg.distinct_pitch_count == 4
    assert agg.interval_pairs_count_distinct == 6


def test_weights_summed_per_bin():
    agg = aggregate_events_by_pitch(
        ["C4", "C4", "E4"],
        weights=[1.0, 2.0, 3.0],
        player_counts=[1, 2, 1],
    )
    c_bin = next(b for b in agg.pitch_bins if b.representative_note.startswith("C"))
    assert c_bin.total_weight == pytest.approx(3.0)
    assert c_bin.total_player_count == 3
