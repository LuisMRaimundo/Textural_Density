"""Replication package tests (Task 4)."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from core.defaults import METRIC_SCHEMA_VERSION
from core.hash_utils import config_hash, input_hash_from_dict


ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "replication" / "corpus" / "metadata" / "synthetic_triad.json"
FROZEN = ROOT / "replication" / "outputs_frozen" / "json" / "synthetic_triad.json"
CONFIG = ROOT / "replication" / "configs" / "score_only_default.json"


class TestReplicationHashes:
    def test_config_hash_stable(self):
        with open(CONFIG, encoding="utf-8") as f:
            cfg = json.load(f)
        h1 = config_hash(cfg)
        h2 = config_hash(cfg)
        assert h1 == h2
        assert len(h1) == 64

    def test_input_hash_stable(self):
        with open(META, encoding="utf-8") as f:
            meta = json.load(f)
        inp = meta["input"]
        assert input_hash_from_dict(inp) == input_hash_from_dict(inp)


class TestReplicationScripts:
    @pytest.fixture(scope="class")
    def ensure_frozen(self):
        if not FROZEN.exists():
            subprocess.run(
                [sys.executable, str(ROOT / "replication/scripts/reproduce_metrics.py")],
                check=True,
                cwd=str(ROOT),
            )

    def test_reproduce_metrics_creates_frozen(self, ensure_frozen):
        assert FROZEN.exists()
        with open(FROZEN, encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("synthetic_fixture") is True
        assert data.get("metric_schema_version") == METRIC_SCHEMA_VERSION
        assert "density" in data
        for key, val in data["density"].items():
            if isinstance(val, (int, float)):
                assert math.isfinite(float(val)), key

    def test_compare_to_frozen_passes(self, ensure_frozen):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "replication/scripts/compare_to_frozen_outputs.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "OK numeric synthetic_triad" in proc.stdout

    def test_reproduce_tables(self, ensure_frozen):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "replication/scripts/reproduce_tables.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        csv_path = ROOT / "replication" / "tables" / "thesis_symbolic_density_summary.csv"
        assert csv_path.exists()
