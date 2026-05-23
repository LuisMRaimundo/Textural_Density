"""
Phase 8: validation and verification framework tests.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from validation.metrics import (
    bootstrap_ci,
    kendall_tau,
    krippendorff_alpha_placeholder,
    mean_absolute_error,
    root_mean_square_error,
    spearman_correlation,
)
from validation.report import generate_validation_report
from validation.schemas import ExpertAnnotation, load_expert_annotations
from validation.synthetic_cases import all_synthetic_cases
from validation.verification import run_verification_suite

VALIDATION_ROOT = Path(__file__).parent.parent / "validation"


class TestValidationMetrics:
    def test_spearman_perfect_correlation(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        rho, p = spearman_correlation(x, x)
        assert rho == pytest.approx(1.0)
        assert p >= 0.0

    def test_kendall_tau(self):
        x = [1.0, 2.0, 3.0, 4.0]
        y = [1.1, 2.2, 2.9, 4.1]
        tau, _ = kendall_tau(x, y)
        assert tau > 0.9

    def test_rmse_mae(self):
        pred = [1.0, 2.0, 3.0]
        obs = [1.0, 2.5, 2.5]
        assert root_mean_square_error(pred, obs) == pytest.approx(0.408248, rel=1e-3)
        assert mean_absolute_error(pred, obs) == pytest.approx(1.0 / 3, rel=1e-3)

    def test_bootstrap_ci_contains_mean(self):
        values = [0.1, 0.2, 0.3, 0.4, 0.5]
        mean, lower, upper = bootstrap_ci(values, n_bootstrap=500, seed=0)
        assert lower <= mean <= upper

    def test_krippendorff_placeholder_returns_value(self):
        matrix = np.array([[1.0, 2.0, 3.0], [1.1, 2.1, 2.9]])
        alpha = krippendorff_alpha_placeholder(matrix)
        assert alpha is not None
        assert -1.0 <= alpha <= 1.0


class TestExpertAnnotationSchema:
    def test_load_template(self):
        path = VALIDATION_ROOT / "expert_annotations" / "example_template.json"
        records = load_expert_annotations(path)
        assert len(records) == 1
        assert isinstance(records[0], ExpertAnnotation)
        assert records[0].rating_dimension == "vertical_density"


class TestVerificationSuite:
    def test_all_synthetic_cases_present(self):
        cases = all_synthetic_cases()
        assert len(cases) >= 15
        ids = {c.case_id for c in cases}
        assert "chromatic_cluster" in ids
        assert "wide_spaced" in ids

    def test_verification_suite_passes(self):
        result = run_verification_suite()
        assert result.synthetic_cases_run >= 15
        assert result.passed, result.failed_checks

    def test_generate_validation_report(self, tmp_path):
        report_text = generate_validation_report(output_path=tmp_path / "validation_report.md")
        assert "verified_only" in report_text.lower() or "verification" in report_text.lower()
        assert (tmp_path / "validation_report.md").is_file()
