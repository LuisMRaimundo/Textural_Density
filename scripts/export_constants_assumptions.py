#!/usr/bin/env python3
"""Export constants and assumptions JSON summary."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.export_constants import write_constants_json


def main() -> int:
    out = ROOT / "replication" / "checksums" / "constants_and_assumptions.json"
    path = write_constants_json(out)
    print(f"Wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
