"""Tests for instrument metadata audit."""

from __future__ import annotations

import json
from pathlib import Path

from instrumentos.metadata_audit import audit_instrument_profile, build_instrument_metadata_audit
from instrumentos.registry import list_profiles, profile_for_event, resolve_profile


def test_build_audit():
    audit = build_instrument_metadata_audit()
    assert audit["instrument_count"] == len(list_profiles())
    assert audit["profiles"]


def test_every_profile_has_status_and_uncertainty():
    for p in build_instrument_metadata_audit()["profiles"]:
        assert p["profile_status"] in (
            "symbolic_default",
            "literature_informed",
            "empirical_profile",
            "unknown_needs_review",
        )
        assert p["uncertainty"] in ("low", "medium", "high", "unknown")


def test_unknown_instrument_fallback():
    fb = profile_for_event("not_a_real_instrument_xyz")
    audited = audit_instrument_profile(fb)
    assert audited["profile_status"] == "symbolic_default"
    assert audited["warnings"]


def test_no_empirical_without_source():
    for p in build_instrument_metadata_audit()["profiles"]:
        if p["profile_status"] == "empirical_profile":
            assert p["source_notes"]
        assert not p["claims_empirical_without_notes"]


def test_orchestration_mass_symbolic_in_reports():
    from data_processor import calculate_metrics

    r, _, _ = calculate_metrics(
        {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "mf"],
            "instruments": ["flauta", "flauta"],
            "num_instruments": [1, 1],
        }
    )
    om = r["density_subindices"]["orchestral_mass"]
    assert om["source_type"] in ("symbolic_metadata", "score_derived")


def test_audit_json_export_script_output(tmp_path):
    audit = build_instrument_metadata_audit()
    out = tmp_path / "audit.json"
    out.write_text(json.dumps(audit), encoding="utf-8")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["instrument_count"] > 0
