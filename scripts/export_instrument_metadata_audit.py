#!/usr/bin/env python3
"""Write instrument metadata audit JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from instrumentos.metadata_audit import build_instrument_metadata_audit


def main() -> int:
    audit = build_instrument_metadata_audit()
    out = ROOT / "instrumentos" / "instrument_metadata_audit.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)
    print(f"Wrote {out.relative_to(ROOT)} ({audit['instrument_count']} profiles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
