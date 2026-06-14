#!/usr/bin/env python3
"""Compare current replication outputs to frozen baselines (numeric-first)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_root = str(ROOT)
if _root in sys.path:
    sys.path.remove(_root)
sys.path.insert(0, _root)

from core.defaults import apply_research_defaults
from core.pipeline import calculate_metrics
from tests.snapshot_utils import extract_metadata_snapshot, extract_numeric_snapshot

NUMERIC_TOLERANCE = 1e-5
META = ROOT / "replication" / "corpus" / "metadata"
CONFIG = ROOT / "replication" / "configs" / "score_only_default.json"
FROZEN_DIR = ROOT / "replication" / "outputs_frozen" / "json"
SNAPSHOT_NUM = ROOT / "tests" / "snapshots" / "numeric_outputs"
SNAPSHOT_META = ROOT / "tests" / "snapshots" / "metadata_outputs"


def _compare_numeric(path: str, current: object, frozen: object, changes: list[str]) -> None:
    if isinstance(current, dict) and isinstance(frozen, dict):
        for k in sorted(set(current) | set(frozen)):
            _compare_numeric(f"{path}.{k}", current.get(k), frozen.get(k), changes)
        return
    if isinstance(current, (int, float)) and isinstance(frozen, (int, float)):
        if abs(float(current) - float(frozen)) > NUMERIC_TOLERANCE:
            changes.append(f"{path}: {frozen} -> {current}")
        return
    if current != frozen:
        changes.append(f"{path}: {frozen!r} -> {current!r}")


def _load_input(stem: str) -> dict:
    with open(META / f"{stem}.json", encoding="utf-8") as f:
        meta = json.load(f)
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    return apply_research_defaults({**cfg, **meta.get("input", {})})


def main() -> int:
    exit_code = 0
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)

    for frozen_path in sorted(FROZEN_DIR.glob("*.json")):
        stem = frozen_path.stem
        resultados, _, _ = calculate_metrics(_load_input(stem))
        numeric = extract_numeric_snapshot(resultados)
        metadata = extract_metadata_snapshot(resultados)

        num_snap = SNAPSHOT_NUM / f"{stem}.json"
        meta_snap = SNAPSHOT_META / f"{stem}.json"
        if num_snap.exists():
            expected_num = json.loads(num_snap.read_text(encoding="utf-8"))
            num_changes: list[str] = []
            _compare_numeric("root", numeric, expected_num, num_changes)
            if num_changes:
                print(f"NUMERIC BREAKING {stem}:")
                for c in num_changes:
                    print(f"  {c}")
                exit_code = 1
            else:
                print(f"OK numeric {stem}")

        if meta_snap.exists():
            expected_meta = json.loads(meta_snap.read_text(encoding="utf-8"))
            if metadata != expected_meta:
                print(f"METADATA DRIFT {stem} (update tests/snapshots/metadata_outputs if intentional):")
                for key in sorted(set(metadata) | set(expected_meta)):
                    if metadata.get(key) != expected_meta.get(key):
                        print(f"  {key}: {expected_meta.get(key)!r} -> {metadata.get(key)!r}")
                exit_code = 1
            else:
                print(f"OK metadata {stem}")

        with open(frozen_path, encoding="utf-8") as f:
            frozen = json.load(f)
        frozen_num = extract_numeric_snapshot(frozen)
        num_changes = []
        _compare_numeric("root", numeric, frozen_num, num_changes)
        if num_changes:
            print(f"FROZEN NUMERIC BREAKING {frozen_path.name}:")
            for c in num_changes:
                print(f"  {c}")
            exit_code = 1
        else:
            print(f"OK frozen numeric {frozen_path.name}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
