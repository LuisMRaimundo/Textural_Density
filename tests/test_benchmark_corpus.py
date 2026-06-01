"""Licensed benchmark corpus regression tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
EXPECTED = BENCHMARKS / "expected_outputs"


def _assert_numeric_close(current: Any, expected: Any, *, path: str = "") -> None:
    if isinstance(expected, dict):
        assert isinstance(current, dict), path
        assert current.keys() == expected.keys(), path
        for key in expected:
            _assert_numeric_close(current[key], expected[key], path=f"{path}.{key}")
        return
    if isinstance(expected, (int, float)):
        assert isinstance(current, (int, float)), path
        assert float(current) == pytest.approx(float(expected), rel=1e-6, abs=1e-6), path
        return
    assert current == expected, path


@pytest.fixture(scope="module")
def manifest_entries():
    manifest_path = BENCHMARKS / "corpus" / "manifest.json"
    if not manifest_path.exists():
        pytest.skip("benchmark manifest missing")
    with open(manifest_path, encoding="utf-8") as f:
        return list(json.load(f).get("entries") or [])


class TestBenchmarkCorpus:
    def test_benchmark_numeric_matches_frozen(self, manifest_entries):
        from benchmarks.scripts.run_benchmarks import run_entry

        for entry in manifest_entries:
            expected_path = EXPECTED / f"{entry['id']}.json"
            if not expected_path.exists():
                pytest.skip("Run benchmarks/scripts/freeze_outputs.py first")
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            current = run_entry(entry)
            _assert_numeric_close(current["numeric"], expected["numeric"], path=entry["id"])

    def test_manifest_has_license(self, manifest_entries):
        for entry in manifest_entries:
            assert entry.get("license") == "owned_by_project_author"
