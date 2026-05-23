"""
Phase 10: quality gates — finite outputs, structured errors, performance bounds.
"""

from __future__ import annotations

import ast
import importlib
import math
import time
from pathlib import Path

import numpy as np
import pytest

from core import calculate_metrics
from core.converters import make_instrument_event
from core.score_analysis import analyze_score
from core.temporal import (
    group_events_into_slices,
    normalize_event_timing,
    resolve_event_duration,
    resolve_event_offset,
)
from error_handler import InputError
from validation.report import generate_validation_report
from validation.synthetic_cases import all_synthetic_cases, base_input
from validation.verification import CheckResult, VerificationResult, run_verification_suite

CORE_PACKAGES = [
    "core",
    "core.models",
    "core.converters",
    "core.orchestration",
    "core.pipeline",
    "core.metrics_metadata",
    "core.subindices",
    "core.temporal",
    "core.score_analysis",
    "core.reporting",
    "validation",
    "validation.metrics",
    "validation.verification",
    "validation.report",
]


def _module_imports_tkinter(module_name: str) -> bool:
    mod = importlib.import_module(module_name)
    path = Path(mod.__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] == "tkinter" for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] == "tkinter":
                return True
    return False


def _collect_finite_scalars(obj, prefix: str = "") -> list[tuple[str, float]]:
    found: list[tuple[str, float]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            found.extend(_collect_finite_scalars(value, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(obj, (list, tuple)):
        for idx, value in enumerate(obj):
            found.extend(_collect_finite_scalars(value, f"{prefix}[{idx}]"))
    elif isinstance(obj, (int, float, np.floating)) and not isinstance(obj, bool):
        found.append((prefix, float(obj)))
    return found


class TestCorePackageImports:
    @pytest.mark.parametrize("module_name", CORE_PACKAGES)
    def test_core_package_has_no_tkinter_import(self, module_name):
        assert not _module_imports_tkinter(module_name), (
            f"{module_name} must not import tkinter at module level"
        )


class TestFiniteOutputs:
    @pytest.mark.parametrize("case", all_synthetic_cases(), ids=lambda c: c.case_id)
    def test_synthetic_case_density_finite(self, case):
        resultados, _, _ = calculate_metrics(case.input_data)
        for key, val in resultados.get("density", {}).items():
            assert math.isfinite(float(val)), f"density.{key} non-finite for {case.case_id}"

    def test_all_density_subindex_scalars_finite(self):
        data = base_input(["C4", "E4", "G4", "B4", "D5"])
        resultados, _, _ = calculate_metrics(data)
        for path, val in _collect_finite_scalars(resultados.get("density_subindices", {})):
            assert math.isfinite(val), f"density_subindices{path} non-finite"

    def test_metric_metadata_scalars_finite(self):
        data = base_input(["C3", "G3", "D4"])
        resultados, _, _ = calculate_metrics(data)
        for path, val in _collect_finite_scalars(resultados.get("metric_metadata", {})):
            assert math.isfinite(val), f"metric_metadata{path} non-finite"


class TestStructuredErrors:
    def test_empty_notes_raises_input_error(self):
        with pytest.raises(InputError):
            calculate_metrics(
                {
                    "notes": [],
                    "dynamics": [],
                    "instruments": [],
                    "num_instruments": [],
                }
            )

    def test_analyze_score_invalid_source_raises_input_error(self):
        with pytest.raises(InputError, match="source must be"):
            analyze_score(42)  # type: ignore[arg-type]

    def test_verification_suite_reports_failures(self):
        broken = VerificationResult(
            synthetic_cases_run=1,
            checks=[
                CheckResult("synthetic.test.finite", False, "non-finite density"),
                CheckResult("property.test", True, "ok"),
            ],
        )
        text = generate_validation_report(verification=broken)
        assert "Failed checks" in text
        assert "synthetic.test.finite" in text


class TestTemporalEdgeCases:
    def test_instantaneous_mode_single_slice(self):
        events = [
            make_instrument_event(
                idx=0,
                note="C4",
                dynamic="mf",
                instrument_name="flauta",
                player_count=1,
                onset=0.0,
                duration=2.0,
            ),
            make_instrument_event(
                idx=1,
                note="E4",
                dynamic="f",
                instrument_name="clarinete",
                player_count=1,
                onset=1.0,
                duration=1.0,
            ),
        ]
        slices = group_events_into_slices(events, mode="instantaneous")
        assert len(slices) == 1
        assert len(slices[0].events) == 2

    def test_normalize_event_timing_fills_offset(self):
        event = make_instrument_event(
            idx=0,
            note="C4",
            dynamic="mf",
            instrument_name="flauta",
            player_count=1,
            onset=1.0,
            duration=2.0,
        )
        normalized = normalize_event_timing([event])
        assert resolve_event_offset(normalized[0]) == pytest.approx(3.0)
        assert resolve_event_duration(normalized[0]) == pytest.approx(2.0)

    def test_analyze_score_from_event_list(self):
        events = [
            make_instrument_event(
                idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=1
            ),
            make_instrument_event(
                idx=1, note="E4", dynamic="mf", instrument_name="oboe", player_count=1
            ),
        ]
        result = analyze_score(events)
        assert len(result.slices) == 1
        assert result.slices[0].composite_density.value >= 0.0


class TestPerformanceBounds:
    @pytest.mark.slow
    def test_large_orchestral_slice_completes_under_five_seconds(self):
        notes = [f"C{4 + (i % 3)}" for i in range(50)]
        data = base_input(
            notes,
            dynamics=["mf"] * 50,
            instruments=(["flauta", "clarinete", "oboe"] * 17)[:50],
            num_instruments=[1 + (i % 3) for i in range(50)],
        )
        start = time.perf_counter()
        resultados, _, _ = calculate_metrics(data)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"50-note slice took {elapsed:.2f}s"
        assert math.isfinite(float(resultados["density"]["total"]))


class TestVerificationSuiteQuality:
    def test_verification_suite_passes(self):
        result = run_verification_suite()
        assert result.passed, result.failed_checks
