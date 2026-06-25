#!/usr/bin/env python3
"""Run licensed benchmark excerpts through the canonical pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from core.defaults import apply_research_defaults
from core.pipeline import calculate_metrics
from snapshot_utils import extract_metadata_snapshot, extract_numeric_snapshot
from xml_loader import parse_xml

BENCHMARKS = Path(__file__).resolve().parents[1]
MANIFEST = BENCHMARKS / "corpus" / "manifest.json"
CONFIG = ROOT / "replication" / "configs" / "score_only_default.json"


def _load_manifest() -> list[dict]:
    with open(MANIFEST, encoding="utf-8") as f:
        return list(json.load(f).get("entries") or [])


def run_entry(entry: dict) -> dict:
    import numpy as np

    # GPR optimizer restarts consume NumPy global RNG; reset per excerpt so
    # benchmark order and prior MusicXML transpose work cannot shift later entries.
    np.random.seed(0)
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    parsed = parse_xml(str(BENCHMARKS / entry["musicxml"]))
    input_data = apply_research_defaults({**cfg, **parsed})
    resultados, _, _ = calculate_metrics(input_data)
    return {
        "benchmark_id": entry["id"],
        "numeric": extract_numeric_snapshot(resultados),
        "metadata": extract_metadata_snapshot(resultados),
        "composite_trace": resultados.get("composite_trace"),
    }


def main() -> int:
    for entry in _load_manifest():
        payload = run_entry(entry)
        print(f"OK {entry['id']} total={payload['numeric']['density']['total']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
