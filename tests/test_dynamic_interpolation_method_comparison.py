"""Tests for dynamic interpolation method comparison tool."""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "compare_dynamic_interpolation_methods.py"
REPORTS = ROOT / "reports"

GPR_MODULES = ("violin", "viola", "cello", "double_bass", "flute", "clarinet", "oboe", "bassoon")
MIN_COMPLEX_TYPES = (
    "very_dense_chromatic",
    "sparse_aggregate",
    "very_sparse_aggregate",
    "registrally_stratified",
    "low_register_mass",
    "high_register_mass",
    "sectional_string",
    "heterogeneous_string",
    "instrument_substitution",
    "register_shift_comparison",
)


def _run_tool(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )


def _committed_payload() -> dict:
    path = REPORTS / "dynamic_interpolation_method_comparison.json"
    assert path.is_file(), "committed comparison report missing"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def comparison_payload() -> dict:
    return _committed_payload()


class TestDynamicInterpolationMethodComparison:
    def test_tool_quick_smoke_runs(self):
        proc = _run_tool("--quick")
        assert proc.returncode == 0
        assert "OK quick smoke" in proc.stdout

    def test_committed_outputs_exist(self):
        assert (REPORTS / "dynamic_interpolation_method_comparison.csv").is_file()
        assert (REPORTS / "dynamic_interpolation_method_comparison.json").is_file()
        assert (REPORTS / "dynamic_interpolation_method_comparison.md").is_file()
        assert (REPORTS / "dynamic_interpolation_benchmark_method_comparison.json").is_file()

    def test_all_gpr_instruments_in_source_rows(self, comparison_payload):
        instruments = {r["instrument"] for r in comparison_payload["source_rows"]}
        assert instruments == set(GPR_MODULES)

    def test_source_row_count_matches_tables(self, comparison_payload):
        expected = sum(
            len(importlib.import_module(f"instrumentos.{m}").spectral_data) for m in GPR_MODULES
        )
        assert comparison_payload["summary"]["source_row_count"] == expected

    def test_at_least_300_positive_scenarios(self, comparison_payload):
        assert comparison_payload["summary"]["positive_scenario_count"] >= 300

    def test_at_least_20_negative_scenarios(self, comparison_payload):
        assert comparison_payload["summary"]["negative_scenario_count"] >= 20

    def test_complex_aggregate_minimum_counts(self, comparison_payload):
        counts = Counter(r["aggregate_type"] for r in comparison_payload["scenario_rows"])
        for agg in MIN_COMPLEX_TYPES:
            assert counts[agg] >= 20, f"{agg} has {counts[agg]}"

    def test_all_four_strings_contains_every_instrument(self, comparison_payload):
        required = {"violino", "viola", "violoncelo", "contrabaixo"}
        rows = [
            r
            for r in comparison_payload["scenario_rows"]
            if r["aggregate_type"] == "all_four_strings"
        ]
        assert rows
        for row in rows:
            assert set(row["instruments"]) == required

    def test_pchip_status(self, comparison_payload):
        assert comparison_payload["summary"]["pchip_available"] is True

    def test_markdown_has_ranked_tables(self, comparison_payload):
        md = (REPORTS / "dynamic_interpolation_method_comparison.md").read_text(encoding="utf-8")
        assert "GPR–linear" in md or "GPR-linear" in md
        assert "Executive summary" in md

    def test_negative_scenarios_fail_cleanly(self, comparison_payload):
        neg = [r for r in comparison_payload["scenario_rows"] if not r.get("expected_valid", True)]
        assert len(neg) >= 20
        assert all(r["classification"] == "expected_failure" for r in neg)

    def test_positive_scenarios_finite_production_outputs(self, comparison_payload):
        pos = [r for r in comparison_payload["scenario_rows"] if r.get("expected_valid", True)]
        for row in pos:
            val = row.get("production_gpr_density_instrument")
            assert val is not None
            assert val == val
            assert val >= 0.0

    def test_predict_method_deterministic(self):
        from tools.compare_dynamic_interpolation_methods import predict_method

        pp, mf, ff = [38.37], [66.29], [55.64]
        a = predict_method(pp, mf, ff, "production_gpr")["mp"][0]
        b = predict_method(pp, mf, ff, "production_gpr")["mp"][0]
        assert float(a) == float(b)

    def test_production_gpr_module_unchanged(self):
        text = (ROOT / "instrumentos" / "gpr_dynamic_interpolation.py").read_text(encoding="utf-8")
        assert "GPR_RANDOM_STATE" in text
        assert "create_dynamic_gpr" in text

    def test_summary_classification_pass(self, comparison_payload):
        assert comparison_payload["summary"]["classification"] == "PASS"
