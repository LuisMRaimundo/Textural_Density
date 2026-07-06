"""Tests for GPR model-quality diagnostic audit tool."""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
TOOL = ROOT / "tools" / "audit_gpr_model_quality.py"

GPR_MODULES = (
    "violin",
    "viola",
    "cello",
    "double_bass",
    "flute",
    "clarinet",
    "oboe",
    "bassoon",
)
REQUIRED_COLUMNS = {
    "instrument",
    "note",
    "midi",
    "register_band",
    "pp",
    "gpr_p",
    "gpr_mp",
    "mf",
    "gpr_f",
    "ff",
    "linear_anchor_pp_mf_mp",
    "quadratic_mp",
    "abs_gpr_minus_linear",
    "abs_gpr_minus_quadratic",
    "convex_hull_departure_pp_mf",
    "classification",
    "interpretation_note",
}


def _run_audit() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )


def _content_hash() -> str:
    data = json.loads((REPORTS / "gpr_model_quality_audit.json").read_text(encoding="utf-8"))
    data["summary"].pop("generated_at", None)
    data["summary"].pop("repository_sha", None)
    for row in data.get("rows", []):
        row.pop("diagnostic_warnings", None)
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


@pytest.fixture(scope="module")
def audit_payload():
    _run_audit()
    return json.loads((REPORTS / "gpr_model_quality_audit.json").read_text(encoding="utf-8"))


class TestGprModelQualityAuditTool:
    def test_audit_runs_successfully(self):
        proc = _run_audit()
        assert proc.returncode == 0

    def test_outputs_created(self):
        assert (REPORTS / "gpr_model_quality_audit.csv").is_file()
        assert (REPORTS / "gpr_model_quality_audit.json").is_file()
        assert (REPORTS / "gpr_model_quality_audit.md").is_file()

    def test_all_gpr_instruments_included(self, audit_payload):
        instruments = {r["instrument"] for r in audit_payload["rows"]}
        assert instruments == set(GPR_MODULES)

    def test_all_source_rows_included(self, audit_payload):
        expected = 0
        for name in GPR_MODULES:
            mod = importlib.import_module(f"instrumentos.{name}")
            expected += len(mod.spectral_data)
        assert audit_payload["summary"]["row_count"] == expected
        assert len(audit_payload["rows"]) == expected

    def test_required_columns_present(self, audit_payload):
        for row in audit_payload["rows"]:
            missing = REQUIRED_COLUMNS - set(row)
            assert not missing, f"missing {missing}"

    def test_markdown_contains_rankings(self, audit_payload):
        md = (REPORTS / "gpr_model_quality_audit.md").read_text(encoding="utf-8")
        assert "Convex-hull departures" in md
        assert "GPR−linear" in md or "GPR-linear" in md or "|GPR−linear|" in md
        assert "GPR−quadratic" in md or "|GPR−quadratic|" in md
        assert "Model interpretation" in md

    def test_pchip_status_documented(self, audit_payload):
        summary = audit_payload["summary"]
        assert "pchip_available" in summary
        if summary["pchip_available"]:
            assert any(r["pchip_mp"] is not None for r in audit_payload["rows"])
        else:
            pytest.skip("PCHIP not available")

    def test_no_negative_or_non_finite_production_predictions(self, audit_payload):
        assert audit_payload["summary"]["negative_count"] == 0
        assert audit_payload["summary"]["non_finite_count"] == 0
        assert audit_payload["summary"]["fail_count"] == 0

    def test_convex_hull_departures_reported(self, audit_payload):
        count = audit_payload["summary"]["convex_hull_departures_pp_mf"]
        assert count >= 1
        assert len(audit_payload["summary"]["rankings"]["convex_hull_pp_mf"]) == count

    def test_deterministic_across_two_runs(self):
        _run_audit()
        h1 = _content_hash()
        _run_audit()
        h2 = _content_hash()
        assert h1 == h2

    def test_production_gpr_module_unchanged(self):
        text = (ROOT / "instrumentos" / "gpr_dynamic_interpolation.py").read_text(encoding="utf-8")
        assert "GPR_RANDOM_STATE" in text
        assert "create_dynamic_gpr" in text

    def test_classification_pass(self, audit_payload):
        assert audit_payload["summary"]["classification"] == "PASS"
