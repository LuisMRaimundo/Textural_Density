#!/usr/bin/env python3
"""Freeze benchmark expected outputs (numeric + metadata layers)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scripts.run_benchmarks import _load_manifest, run_entry

BENCHMARKS = Path(__file__).resolve().parents[1]
OUT = BENCHMARKS / "expected_outputs"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for entry in _load_manifest():
        payload = run_entry(entry)
        path = OUT / f"{entry['id']}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
