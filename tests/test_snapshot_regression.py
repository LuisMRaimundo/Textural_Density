"""
Layered snapshot regression tests.

Numeric snapshots guard formula stability; metadata snapshots guard epistemic labelling.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.defaults import apply_research_defaults
from core.pipeline import calculate_metrics
from tests.snapshot_utils import extract_metadata_snapshot, extract_numeric_snapshot

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = Path(__file__).resolve().parent / "snapshots"
META = ROOT / "replication" / "corpus" / "metadata" / "synthetic_triad.json"
CONFIG = ROOT / "replication" / "configs" / "score_only_default.json"
MIGRATION_NOTE = SNAPSHOTS / "MIGRATION.md"


@pytest.fixture
def synthetic_triad_resultados():
    with open(META, encoding="utf-8") as f:
        meta = json.load(f)
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    input_data = apply_research_defaults({**cfg, **meta.get("input", {})})
    resultados, _, _ = calculate_metrics(input_data)
    return resultados


NUMERIC_TOLERANCE = 1e-5


def assert_numeric_snapshot_equal(current: dict, expected: dict, path: str = "root") -> None:
    if isinstance(current, dict) and isinstance(expected, dict):
        keys = set(current) | set(expected)
        for key in keys:
            assert_numeric_snapshot_equal(
                current.get(key), expected.get(key), f"{path}.{key}"
            )
        return
    if isinstance(current, (int, float)) and isinstance(expected, (int, float)):
        assert float(current) == pytest.approx(float(expected), rel=1e-9, abs=1e-9)
        return
    assert current == expected


class TestNumericSnapshots:
    def test_synthetic_triad_numeric_unchanged(self, synthetic_triad_resultados):
        path = SNAPSHOTS / "numeric_outputs" / "synthetic_triad.json"
        expected = json.loads(path.read_text(encoding="utf-8"))
        current = extract_numeric_snapshot(synthetic_triad_resultados)
        assert_numeric_snapshot_equal(current, expected)


class TestMetadataSnapshots:
    def test_synthetic_triad_metadata_labels(self, synthetic_triad_resultados):
        path = SNAPSHOTS / "metadata_outputs" / "synthetic_triad.json"
        expected = json.loads(path.read_text(encoding="utf-8"))
        current = extract_metadata_snapshot(synthetic_triad_resultados)
        assert current == expected

    def test_instrument_density_marked_external_acoustic(self, synthetic_triad_resultados):
        meta = extract_metadata_snapshot(synthetic_triad_resultados)
        assert meta["density.instrument.source_type"] == "external_acoustic_metadata"


class TestSnapshotMigrationNote:
    def test_migration_note_documents_epistemic_relabel(self):
        text = MIGRATION_NOTE.read_text(encoding="utf-8")
        assert "external_acoustic_metadata" in text
        assert "numeric" in text.lower()
