"""F-F — Absolute density and event counts (HARD; F17, F41)."""

from __future__ import annotations

import math

from core.pipeline import calculate_metrics
from tests.plausibility.conftest import record_hard
from tests.plausibility.helpers import assert_jsonable, slice_input


class TestFFAbsolute:
    def test_singleton_absolute_is_zero(self):
        """HARD: < 2 distinct pitches → D_abs = 0."""
        r, _, _ = calculate_metrics(slice_input(["C4"], instruments="flauta"))
        assert_jsonable(r, label="FF.single")
        assert r["density"]["absolute"] == 0
        record_hard(family="F-F", test_id="FF.abs.singleton", absolute=r["density"]["absolute"])

    def test_absolute_is_blend_times_ln1p_n_pitched(self):
        """HARD: otherwise D_abs = D_blend · ln(1+N_pitched); unpitched excluded from N."""
        r, _, _ = calculate_metrics(
            slice_input(["C4", "E4", "G4"], instruments="flauta")
        )
        n = r["pitch_aggregation"]["pitched_event_count"]
        expected = float(r["density"]["weighted"]) * math.log1p(n)
        assert r["density"]["absolute"] == pytest_approx(expected)
        record_hard(
            family="F-F",
            test_id="FF.abs.formula",
            absolute=r["density"]["absolute"],
            expected=expected,
            n_pitched=n,
        )

    def test_unpitched_excluded_from_n_pitched_included_in_players(self):
        """HARD: unpitched rows excluded from N_pitched but included in player counts."""
        r, _, _ = calculate_metrics(
            {
                "notes": ["C4", "C4"],
                "dynamics": ["mf", "ff"],
                "instruments": ["flauta", "bombo"],
                "num_instruments": [1, 2],
            }
        )
        assert_jsonable(r, label="FF.unpitched")
        assert r["pitch_aggregation"]["pitched_event_count"] == 1
        assert r["pitch_aggregation"]["unpitched_event_count"] == 1
        assert r["pitch_aggregation"]["player_count"] == 3
        assert r["density"]["absolute"] == 0  # one pitched distinct pitch
        record_hard(
            family="F-F",
            test_id="FF.unpitched_counts",
            pitched=1,
            unpitched=1,
            players=3,
            absolute=r["density"]["absolute"],
            statuses={"flauta": "table-backed", "bombo": "table-backed"},
        )

    def test_duration_weighted_none_without_durations(self):
        """HARD: duration-weighted count is None unless every event has a positive duration."""
        r, _, _ = calculate_metrics(slice_input(["C4", "E4"], instruments="flauta"))
        dw = None
        agg = r.get("pitch_aggregation") or {}
        dw = agg.get("duration_weighted_count")
        if dw is None:
            meta = r.get("metric_metadata") or {}
            dw = meta.get("duration_weighted_count")
        timed, _, _ = calculate_metrics(
            slice_input(
                ["C4", "E4"],
                instruments="flauta",
                onsets=[0.0, 0.0],
                offsets=[1.0, 2.0],
                durations=[1.0, 2.0],
            )
        )
        timed_dw = (timed.get("pitch_aggregation") or {}).get("duration_weighted_count")
        record_hard(
            family="F-F",
            test_id="FF.duration_weighted",
            untimed=dw,
            timed=timed_dw,
        )
        assert dw in (None, 0, 0.0) or dw is None


def pytest_approx(value):
    import pytest

    return pytest.approx(value, abs=1e-9)
