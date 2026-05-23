"""Tests for replication benchmark manifest."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "replication" / "benchmark_manifest.json"

REQUIRED_FIELDS = frozenset(
    {
        "benchmark_id",
        "file_path",
        "format",
        "corpus_status",
        "composer",
        "work_title",
        "excerpt_label",
        "instrumentation",
        "measure_range",
        "source",
        "license_status",
        "license_note",
        "limitations",
        "include_in_official_benchmark",
        "reason_included_or_excluded",
    }
)

OFFICIAL_LICENSES = frozenset(
    {
        "owned_by_project_author",
        "public_domain_verified",
        "openly_licensed",
    }
)


@pytest.fixture
def manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


class TestBenchmarkManifest:
    def test_manifest_loads(self, manifest):
        assert manifest["manifest_version"]
        assert isinstance(manifest["entries"], list)

    def test_required_fields(self, manifest):
        for entry in manifest["entries"]:
            missing = REQUIRED_FIELDS - set(entry)
            assert not missing, entry.get("benchmark_id")

    def test_synthetic_labelled(self, manifest):
        synthetic = [e for e in manifest["entries"] if e["corpus_status"] == "synthetic_fixture"]
        assert synthetic
        for e in synthetic:
            assert e["include_in_official_benchmark"] is False

    def test_unknown_license_not_official(self, manifest):
        for entry in manifest["entries"]:
            if "unknown" in entry["license_status"]:
                assert entry["include_in_official_benchmark"] is False

    def test_no_representative_corpus_claim(self, manifest):
        assert manifest.get("corpus_maturity") != "representative_licensed_corpus"
        official = [e for e in manifest["entries"] if e["include_in_official_benchmark"]]
        assert official == []

    def test_official_requires_valid_license(self, manifest):
        for entry in manifest["entries"]:
            if entry["include_in_official_benchmark"]:
                assert entry["license_status"] in OFFICIAL_LICENSES

    def test_scan_intake_script_runs(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "replication/scripts/scan_benchmark_intake.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
