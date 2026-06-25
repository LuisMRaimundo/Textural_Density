"""Contracts for instrument metadata range semantics and table alignment."""

from __future__ import annotations

import importlib

import pytest
from microtonal import note_to_midi_strict

from instrumentos.metadata_range_audit import build_metadata_range_resolution_audit
from instrumentos.registry import REGISTRY, list_profiles, resolve_profile

GPR_MODULE_NAMES = frozenset(
    {"flute", "oboe", "clarinet", "violin", "viola", "cello", "double_bass"}
)
GPR_REGISTRY_IDS = frozenset(
    {"flauta", "oboe", "clarinete", "violino", "viola", "violoncelo", "contrabaixo"}
)


@pytest.fixture(scope="module")
def audit_payload():
    return build_metadata_range_resolution_audit()


class TestMetadataRangeAuditArtifact:
    def test_covers_all_registry_instruments(self, audit_payload):
        audited = {i["instrument_id"] for i in audit_payload["instruments"]}
        assert audited == set(REGISTRY.keys())

    def test_committed_reports_exist(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1] / "reports"
        for name in (
            "instrument_metadata_range_resolution_audit.json",
            "instrument_metadata_range_resolution_audit.md",
            "instrument_metadata_range_resolution_audit.csv",
        ):
            assert (root / name).is_file(), name


@pytest.mark.parametrize("module_name", sorted(GPR_MODULE_NAMES))
def test_gpr_source_pitch_range_matches_table(module_name: str):
    mod = importlib.import_module(f"instrumentos.{module_name}")
    notes = sorted(mod.spectral_data.keys(), key=note_to_midi_strict)
    lo = int(note_to_midi_strict(notes[0]))
    hi = int(note_to_midi_strict(notes[-1]))
    assert mod.INSTRUMENT_SOURCE.pitch_range == (lo, hi)


@pytest.mark.parametrize("instrument_id", sorted(GPR_REGISTRY_IDS))
def test_gpr_registry_sounding_range_covers_table(instrument_id: str):
    profile = REGISTRY[instrument_id]
    mod = importlib.import_module(f"instrumentos.{profile.module_name}")
    lo, hi = profile.sounding_range
    t_lo, t_hi = mod.INSTRUMENT_SOURCE.pitch_range
    assert lo <= t_lo and hi >= t_hi


class TestDoubleBassSpanResolution:
    def test_source_table_span_e1_c5(self):
        mod = importlib.import_module("instrumentos.double_bass")
        notes = sorted(mod.spectral_data.keys(), key=note_to_midi_strict)
        assert notes[0] == "E1"
        assert notes[-1] == "C5"
        assert mod.INSTRUMENT_SOURCE.pitch_range == (28, 72)

    def test_registry_aligned_with_table(self):
        profile = REGISTRY["contrabaixo"]
        assert profile.sounding_range == (28, 72)
        assert profile.comfortable_range == (31, 55)

    def test_audit_passes_span_documentation(self, audit_payload):
        db = audit_payload["double_bass_resolution"]
        assert db["classification"] == "PASS"
        assert db["obsolete_documentation_span"] == "E1–A3"
        assert db["upper_register_methodological_qc"] == "REVIEW REQUIRED"


class TestTubaClassification:
    def test_coarse_default_no_module(self):
        profile = REGISTRY["tuba"]
        assert profile.module_name is None
        assert profile.profile_status == "coarse_default"

    def test_audit_review_required(self, audit_payload):
        assert audit_payload["tuba_review"]["classification"] == "REVIEW REQUIRED"


class TestTranspositionMetadata:
    def test_manual_input_contract_documented(self, audit_payload):
        assert audit_payload["transposition_review"]["classification"] == "PASS"

    @pytest.mark.parametrize(
        "alias",
        ["contrabaixo", "contrafagote", "flautim", "piccolo"],
    )
    def test_octave_displaced_instruments_zero_registry_transposition(self, alias: str):
        profile = resolve_profile(alias)
        assert profile is not None
        assert profile.transposition == 0


@pytest.mark.parametrize("instrument_id", sorted(REGISTRY.keys()))
def test_aliases_resolve_to_canonical(instrument_id: str):
    profile = REGISTRY[instrument_id]
    for alias in (profile.display_name, *profile.aliases):
        resolved = resolve_profile(alias)
        assert resolved is not None
        assert resolved.instrument_id == instrument_id
