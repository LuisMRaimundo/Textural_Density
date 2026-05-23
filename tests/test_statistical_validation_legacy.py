"""Legacy statistical_validation module behaviour tests."""

from __future__ import annotations

import warnings

import pandas as pd
import pytest

from statistical_validation import (
    create_metrics_profile,
    plot_metrics_comparison,
    validate_metrics_reliability,
)


class TestStatisticalValidationLegacy:
    def test_validate_metrics_reliability_emits_deprecation(self):
        df = pd.DataFrame({"density.total": [0.1, 0.2, 0.15]})
        with pytest.warns(DeprecationWarning, match="legacy GUI-era"):
            result = validate_metrics_reliability({"density.total": df["density.total"].tolist()})
        assert "descriptive_stats" in result

    def test_create_metrics_profile_emits_deprecation(self):
        with pytest.warns(DeprecationWarning, match="legacy GUI-era"):
            profile = create_metrics_profile({}, {}, {})
        assert isinstance(profile, pd.DataFrame)

    def test_plot_metrics_comparison_emits_deprecation(self):
        df = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]})
        with pytest.warns(DeprecationWarning, match="legacy GUI-era"):
            out = plot_metrics_comparison(df)
        assert out is None or hasattr(out[0], "savefig")
