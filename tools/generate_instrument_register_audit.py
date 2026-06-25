#!/usr/bin/env python3
"""Generate instrument register audit reports (JSON + Markdown)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.instrument_register_audit import build_instrument_register_audit  # noqa: E402


def _markdown_report(audit: dict) -> str:
    lines = [
        "# Instrument register audit",
        "",
        f"**Instruments audited:** {audit['instrument_count']}",
        "",
        "## Pitch contract",
        "",
    ]
    for key, value in audit["pitch_contract"].items():
        lines.append(f"- **{key}:** {value}")
    lines.extend(["", "## Per-instrument summary", ""])
    lines.append(
        "| ID | Family | Sounding MIDI | Transposition | Table span | Discrepancy |"
    )
    lines.append("|----|--------|---------------|---------------|------------|-------------|")
    for inst in audit["instruments"]:
        span = inst.get("table_span")
        span_txt = (
            f"{span['first_note']}–{span['last_note']} ({span['min_midi']}–{span['max_midi']})"
            if span
            else "—"
        )
        lo = inst["registry_sounding_min_midi"]
        hi = inst["registry_sounding_max_midi"]
        lines.append(
            f"| {inst['instrument_id']} | {inst['family']} | {lo}–{hi} | "
            f"{inst['transposition_semitones']} ({inst['transposition_class']}) | "
            f"{span_txt} | {inst['range_discrepancy']} |"
        )
    review = [
        i
        for i in audit["instruments"]
        if i["range_discrepancy"] in ("BUG_table_anchor_outside_registry", "REVIEW_REQUIRED")
    ]
    if review:
        lines.extend(["", "## REVIEW REQUIRED / discrepancies", ""])
        for inst in review:
            lines.append(
                f"- **{inst['instrument_id']}:** {inst['range_discrepancy']}"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    audit = build_instrument_register_audit()
    out_dir = ROOT / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "instrument_register_audit.json"
    md_path = out_dir / "instrument_register_audit.md"
    json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    md_path.write_text(_markdown_report(audit), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
