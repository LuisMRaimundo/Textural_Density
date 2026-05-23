"""Tests for expert score annotation validation framework (Task 3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from validation.metrics import kendall_tau, mean_absolute_error, spearman_correlation
from validation.score_schemas import (
    ScoreAnnotation,
    load_score_annotations,
    validate_annotation_file,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation"
    / "score_annotations"
    / "examples"
    / "toy_fixture.json"
)


class TestScoreAnnotationSchema:
    def test_load_toy_fixture(self):
        anns = load_score_annotations(FIXTURE_PATH)
        assert len(anns) >= 2
        assert all(a.is_fixture for a in anns)

    def test_reject_missing_fields(self):
        with pytest.raises(ValueError, match="Missing required"):
            ScoreAnnotation.from_dict({"corpus_id": "x"})

    def test_reject_unknown_dimension(self):
        with pytest.raises(ValueError, match="Unknown rating_dimension"):
            ScoreAnnotation.from_dict(
                {
                    "corpus_id": "c",
                    "piece_id": "p",
                    "slice_id": "s",
                    "score_source": "test",
                    "input_file": "f.json",
                    "rater_id": "r",
                    "rating_dimension": "not_a_real_dimension",
                    "rating_value": 1.0,
                    "rating_scale_min": 1.0,
                    "rating_scale_max": 5.0,
                    "annotation_protocol_version": "1.0.0",
                }
            )

    def test_reject_malformed_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        _, errors = validate_annotation_file(bad)
        assert errors

    def test_empty_missing_file_returns_empty(self, tmp_path):
        missing = tmp_path / "missing.json"
        assert load_score_annotations(missing) == []


class TestCorrelationFunctions:
    def test_spearman_perfect_monotone(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        rho, p = spearman_correlation(x, y)
        assert rho == pytest.approx(1.0)
        assert p >= 0.0

    def test_kendall_tau_known(self):
        x = [1.0, 2.0, 3.0, 4.0]
        y = [1.0, 2.0, 3.0, 4.0]
        tau, _ = kendall_tau(x, y)
        assert tau == pytest.approx(1.0)

    def test_mae_known(self):
        assert mean_absolute_error([1.0, 2.0, 3.0], [1.5, 2.5, 2.5]) == pytest.approx(0.5)


class TestScoreValidationReport:
    def test_report_when_no_annotations(self, tmp_path):
        from validation.scripts import correlate_metrics_with_ratings as mod

        empty = tmp_path / "empty.json"
        empty.write_text("[]", encoding="utf-8")
        report = tmp_path / "report.md"
        # invoke main logic via subprocess-style import
        import sys

        argv = sys.argv
        try:
            sys.argv = ["correlate", str(empty), "--report", str(report)]
            assert mod.main() == 0
        finally:
            sys.argv = argv
        text = report.read_text(encoding="utf-8")
        assert "verification only" in text.lower()

    def test_toy_fixture_report_labels_fixture(self, tmp_path):
        report_path = Path(__file__).resolve().parents[1] / "validation" / "reports" / "score_validation_report.md"
        # Default committed report states verification only
        text = report_path.read_text(encoding="utf-8")
        assert "verification only" in text.lower()
