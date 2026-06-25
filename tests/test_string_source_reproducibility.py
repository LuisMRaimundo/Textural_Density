"""Workbook-to-module source reconstruction audit for string GPR tables."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest

from microtonal import note_to_midi_strict
from tests.string_constants import SOURCE_DYNAMICS, STRING_INSTRUMENTS, StringInstrumentSpec
from tools.generate_instrument_modules import CONFIGS, load_spectral_data

VALUE_TOL = 1e-5
RUN_ROOT = os.environ.get("TEXTURAL_DENSITY_RUN_ROOT")


def _workbook_config(module_name: str) -> dict | None:
    for cfg in CONFIGS:
        if cfg["module"] == module_name:
            return cfg
    return None


def _compare_tables(workbook_table: dict, committed_table: dict) -> dict:
    wb_notes = set(workbook_table)
    cm_notes = set(committed_table)
    missing_in_committed = sorted(wb_notes - cm_notes, key=note_to_midi_strict)
    extra_in_committed = sorted(cm_notes - wb_notes, key=note_to_midi_strict)
    value_mismatches = []
    for pitch in sorted(wb_notes & cm_notes, key=note_to_midi_strict):
        for dyn in SOURCE_DYNAMICS:
            wb_val = workbook_table[pitch][dyn]
            cm_val = committed_table[pitch][dyn]
            if abs(wb_val - cm_val) > VALUE_TOL:
                value_mismatches.append(
                    {"pitch": pitch, "dynamic": dyn, "workbook": wb_val, "committed": cm_val}
                )
    return {
        "workbook_row_count": len(workbook_table),
        "committed_row_count": len(committed_table),
        "missing_in_committed": missing_in_committed,
        "extra_in_committed": extra_in_committed,
        "value_mismatches": value_mismatches,
        "match": not (missing_in_committed or extra_in_committed or value_mismatches),
    }


@pytest.mark.musicological
class TestStringSourceReconstruction:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_workbook_matches_committed_module(self, spec: StringInstrumentSpec, tmp_path: Path):
        cfg = _workbook_config(spec.module_name)
        assert cfg is not None
        workbook = Path(cfg["workbook"])
        if not workbook.is_file():
            pytest.skip(f"UNVERIFIED — SOURCE WORKBOOK NOT ACCESSIBLE: {workbook}")

        workbook_table = load_spectral_data(workbook)
        committed = importlib.import_module(f"instrumentos.{spec.module_name}").spectral_data
        report = {
            "module": spec.module_name,
            "workbook": str(workbook),
            "comparison": _compare_tables(workbook_table, committed),
        }

        out_dir = Path(RUN_ROOT) if RUN_ROOT else tmp_path
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / f"string-source-audit-{spec.module_name}.json"
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        cmp = report["comparison"]
        assert cmp["workbook_row_count"] == spec.documented_row_count
        assert cmp["committed_row_count"] == spec.documented_row_count
        assert cmp["match"], (
            f"Workbook vs committed mismatch for {spec.module_name}: "
            f"missing={cmp['missing_in_committed'][:3]}, "
            f"extra={cmp['extra_in_committed'][:3]}, "
            f"value_diffs={len(cmp['value_mismatches'])}"
        )
