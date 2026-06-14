"""Tests for Excel-based instrument profile importer (Phase 1a)."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("openpyxl")
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from import_instrument_profiles_from_excel import (  # noqa: E402
    DEFAULT_TRANSFORM_POLICY,
    REQUIRED_ACOUSTIC_PITCH_BASIS,
    module_imports_are_safe,
    run_import,
    validate_and_build,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "instrument_import"


def _write_workbook(path: Path, sheets: dict[str, list[dict]]) -> None:
    wb = Workbook()
    default = wb.active
    wb.remove(default)
    for sheet_name, rows in sheets.items():
        ws = wb.create_sheet(sheet_name)
        if not rows:
            continue
        headers = list(rows[0].keys())
        ws.append(headers)
        for row in rows:
            ws.append([row.get(h) for h in headers])
    wb.save(path)


def _minimal_sheets(*, include_meta: bool = True, **overrides) -> dict[str, list[dict]]:
    meta = (
        [{"key": "acoustic_pitch_basis", "value": REQUIRED_ACOUSTIC_PITCH_BASIS}]
        if include_meta
        else []
    )
    registry = overrides.get(
        "Registry",
        [
            {
                "instrument_id": "test_inst",
                "display_name": "Test Instrument",
                "family": "woodwinds",
                "subfamily": "",
                "transposition": 0,
                "sounding_range_low_midi": 48,
                "sounding_range_high_midi": 84,
                "comfortable_range_low_midi": 55,
                "comfortable_range_high_midi": 80,
                "profile_status": "literature_derived",
                "source_type": "external_acoustic_metadata",
                "uncertainty": "medium",
                "source_notes": "Synthetic test profile only.",
                "supported_techniques": "",
                "aliases": "",
            }
        ],
    )
    acoustic = overrides.get(
        "AcousticTable",
        [
            {
                "instrument_id": "test_inst",
                "note_sounding": "C4",
                "midi_sounding": 60,
                "dynamic": "mf",
                "value": 10.0,
                "value_kind": "amplitude_proxy",
                "unit": "td_amplitude_proxy_v1",
                "cell_status": "manual_entry",
                "source_system": "",
                "source_file": "",
                "source_column": "",
                "source_hash": "",
                "transform_policy": "",
                "uncertainty": "",
                "validation_status": "",
                "notes": "",
                "note_written_optional": "",
                "midi_written_optional": "",
                "transposition_semitones_optional": "",
            }
        ],
    )
    provenance = overrides.get(
        "Provenance",
        [
            {
                "instrument_id": "test_inst",
                "source_type": "external_acoustic_metadata",
                "citation": "Synthetic fixture",
                "source_url_or_identifier": "",
                "upstream_system": "manual_excel",
                "upstream_version": "",
                "analysis_profile_hash": "",
                "import_run_id": "",
                "import_date": "",
                "operator": "",
                "transform_policy": DEFAULT_TRANSFORM_POLICY,
                "transform_parameters": "",
                "rows_accepted": "",
                "rows_rejected": "",
                "notes": "",
            }
        ],
    )
    sheets = {"WorkbookMeta": meta, "Registry": registry, "AcousticTable": acoustic, "Provenance": provenance}
    sheets.update({k: v for k, v in overrides.items() if k not in sheets})
    return sheets


def _bb_clarinet_sheets() -> dict[str, list[dict]]:
    return _minimal_sheets(
        Registry=[
            {
                "instrument_id": "clarinete",
                "display_name": "Clarinet in Bb",
                "family": "woodwinds",
                "subfamily": "single_reed",
                "transposition": -2,
                "sounding_range_low_midi": 50,
                "sounding_range_high_midi": 88,
                "comfortable_range_low_midi": 55,
                "comfortable_range_high_midi": 80,
                "profile_status": "literature_derived",
                "source_type": "external_acoustic_metadata",
                "uncertainty": "medium",
                "source_notes": "Synthetic Bb clarinet fixture.",
                "supported_techniques": "",
                "aliases": "",
            }
        ],
        AcousticTable=[
            {
                "instrument_id": "clarinete",
                "note_sounding": "C4",
                "midi_sounding": 60,
                "dynamic": "mf",
                "value": 23.778,
                "value_kind": "amplitude_proxy",
                "unit": "td_amplitude_proxy_v1",
                "cell_status": "manual_entry",
                "source_system": "",
                "source_file": "",
                "source_column": "",
                "source_hash": "",
                "transform_policy": "",
                "uncertainty": "",
                "validation_status": "",
                "notes": "",
                "note_written_optional": "D4",
                "midi_written_optional": 62,
                "transposition_semitones_optional": -2,
            }
        ],
        Provenance=[
            {
                "instrument_id": "clarinete",
                "source_type": "external_acoustic_metadata",
                "citation": "Synthetic fixture",
                "source_url_or_identifier": "",
                "upstream_system": "manual_excel",
                "upstream_version": "",
                "analysis_profile_hash": "",
                "import_run_id": "",
                "import_date": "",
                "operator": "",
                "transform_policy": DEFAULT_TRANSFORM_POLICY,
                "transform_parameters": "",
                "rows_accepted": "",
                "rows_rejected": "",
                "notes": "",
            }
        ],
    )


class TestMinimalValidWorkbook:
    def test_minimal_valid_workbook(self, tmp_path):
        wb_path = tmp_path / "minimal.xlsx"
        _write_workbook(wb_path, _minimal_sheets())
        result = validate_and_build(wb_path)
        assert result.ok
        assert "test_inst" in result.packages
        pkg = result.packages["test_inst"]
        assert pkg["schema_version"]
        assert pkg["acoustic_pitch_basis"] == REQUIRED_ACOUSTIC_PITCH_BASIS
        assert pkg["registry"]["instrument_id"] == "test_inst"
        assert pkg["acoustic_table"]["entries"][0]["note_sounding"] == "C4"
        assert pkg["provenance"]["citation"] == "Synthetic fixture"
        assert pkg["import_audit"]["source_workbook_sha256"]


class TestAcousticPitchBasis:
    def test_missing_acoustic_pitch_basis_rejected(self, tmp_path):
        wb_path = tmp_path / "no_basis.xlsx"
        _write_workbook(wb_path, _minimal_sheets(include_meta=False, WorkbookMeta=[]))
        result = validate_and_build(wb_path)
        assert not result.ok
        assert any(i.code == "missing_acoustic_pitch_basis" for i in result.errors)


class TestNoDoubleTransposition:
    def test_bb_clarinet_sounding_pitch_unchanged(self, tmp_path):
        wb_path = tmp_path / "bb_clarinet.xlsx"
        _write_workbook(wb_path, _bb_clarinet_sheets())
        result = validate_and_build(wb_path)
        assert result.ok
        entry = result.packages["clarinete"]["acoustic_table"]["entries"][0]
        assert entry["note_sounding"] == "C4"
        assert entry["midi_sounding"] == pytest.approx(60.0)
        assert entry["midi_sounding"] != pytest.approx(58.0)
        assert entry["midi_sounding"] != pytest.approx(62.0)
        assert result.packages["clarinete"]["registry"]["transposition"] == -2

    def test_written_fields_traceability_only(self, tmp_path):
        wb_path = tmp_path / "bb_clarinet.xlsx"
        _write_workbook(wb_path, _bb_clarinet_sheets())
        result = validate_and_build(wb_path)
        cell = result.packages["clarinete"]["acoustic_table"]["cells"][0]
        trace = cell["written_traceability"]
        assert trace["note_written_optional"] == "D4"
        assert trace["midi_written_optional"] == pytest.approx(62.0)
        assert trace["transposition_semitones_optional"] == -2
        assert cell["note_sounding"] == "C4"
        assert "note_written_optional" not in entry_keys(result.packages["clarinete"]["acoustic_table"]["entries"][0])


def entry_keys(entry: dict) -> set[str]:
    return set(entry.keys())


class TestValidationFailures:
    def test_duplicate_rows_rejected(self, tmp_path):
        rows = _minimal_sheets()["AcousticTable"] * 2
        wb_path = tmp_path / "dup.xlsx"
        _write_workbook(wb_path, _minimal_sheets(AcousticTable=rows))
        result = validate_and_build(wb_path)
        assert not result.ok
        assert any(i.code == "duplicate_cell" for i in result.errors)

    def test_invalid_note_rejected(self, tmp_path):
        acoustic = _minimal_sheets()["AcousticTable"]
        acoustic[0]["note_sounding"] = "NOT_A_REAL_NOTE_XYZ!!!"
        acoustic[0]["midi_sounding"] = 99
        wb_path = tmp_path / "bad_note.xlsx"
        _write_workbook(wb_path, _minimal_sheets(AcousticTable=acoustic))
        result = validate_and_build(wb_path)
        assert not result.ok
        assert any(i.code == "pitch_mismatch" for i in result.errors)

    def test_non_finite_value_rejected(self, tmp_path):
        acoustic = _minimal_sheets()["AcousticTable"]
        acoustic[0]["value"] = float("nan")
        wb_path = tmp_path / "nan.xlsx"
        _write_workbook(wb_path, _minimal_sheets(AcousticTable=acoustic))
        result = validate_and_build(wb_path)
        assert not result.ok
        assert any(i.code == "non_finite_value" for i in result.errors)

    def test_measured_proxy_requires_provenance(self, tmp_path):
        acoustic = _minimal_sheets()["AcousticTable"]
        acoustic[0]["cell_status"] = "measured_proxy"
        wb_path = tmp_path / "proxy.xlsx"
        _write_workbook(wb_path, _minimal_sheets(AcousticTable=acoustic))
        result = validate_and_build(wb_path)
        assert not result.ok
        assert any(i.code == "measured_proxy_missing_provenance" for i in result.errors)


class TestMissingCellsAllowed:
    def test_sparse_table_allowed(self, tmp_path):
        acoustic = _minimal_sheets()["AcousticTable"]
        acoustic.append(
            {
                **acoustic[0],
                "dynamic": "pp",
                "value": "",
                "cell_status": "missing",
            }
        )
        wb_path = tmp_path / "sparse.xlsx"
        _write_workbook(wb_path, _minimal_sheets(AcousticTable=acoustic))
        result = validate_and_build(wb_path)
        assert result.ok
        entry = result.packages["test_inst"]["acoustic_table"]["entries"][0]
        assert "pp" not in entry["dynamics"]
        assert entry["cell_status_by_dynamic"]["pp"] == "missing"


class TestDryRunAndWrite:
    def test_dry_run_does_not_write_json(self, tmp_path):
        wb_path = tmp_path / "minimal.xlsx"
        out_dir = tmp_path / "out"
        report = tmp_path / "report.json"
        _write_workbook(wb_path, _minimal_sheets())
        result = run_import(wb_path, out_dir, dry_run=True, report_path=report)
        assert result.ok
        assert not out_dir.exists() or list(out_dir.glob("*.profile.json")) == []
        assert report.is_file()

    def test_non_dry_run_writes_json(self, tmp_path):
        wb_path = tmp_path / "minimal.xlsx"
        out_dir = tmp_path / "out"
        _write_workbook(wb_path, _minimal_sheets())
        result = run_import(wb_path, out_dir, dry_run=False)
        assert result.ok
        profile = out_dir / "test_inst.profile.json"
        assert profile.is_file()
        data = json.loads(profile.read_text(encoding="utf-8"))
        assert data["acoustic_pitch_basis"] == REQUIRED_ACOUSTIC_PITCH_BASIS
        assert (out_dir / "index.json").is_file()


class TestProductionSafety:
    def test_no_production_module_mutation(self, tmp_path):
        flauta = ROOT / "instrumentos" / "flauta.py"
        before = hashlib.sha256(flauta.read_bytes()).hexdigest()
        wb_path = tmp_path / "minimal.xlsx"
        out_dir = tmp_path / "out"
        _write_workbook(wb_path, _minimal_sheets())
        run_import(wb_path, out_dir, dry_run=False)
        after = hashlib.sha256(flauta.read_bytes()).hexdigest()
        assert before == after

    def test_importer_does_not_import_forbidden_modules(self):
        assert module_imports_are_safe()
        tree = ast.parse((ROOT / "tools" / "import_instrument_profiles_from_excel.py").read_text(encoding="utf-8"))
        forbidden = {"proc_audio", "spectral_analysis", "SoundSpectrAnalyse", "fft", "stft"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not any(f in alias.name for f in forbidden)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                assert not any(f in mod for f in forbidden)


class TestGenericPitchColumnsRejected:
    def test_generic_note_midi_columns_rejected(self, tmp_path):
        acoustic = [
            {
                "instrument_id": "test_inst",
                "note": "C4",
                "midi": 60,
                "dynamic": "mf",
                "value": 10.0,
                "cell_status": "manual_entry",
            }
        ]
        wb_path = tmp_path / "generic.xlsx"
        _write_workbook(wb_path, _minimal_sheets(AcousticTable=acoustic))
        result = validate_and_build(wb_path)
        assert not result.ok
        assert any(
            i.code in ("missing_sounding_columns", "generic_pitch_columns")
            for i in result.errors
        )
