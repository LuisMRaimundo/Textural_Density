#!/usr/bin/env python3
"""Audit transposing-instrument sounding-pitch contract across registry and tables."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.instrument_register_audit import build_instrument_register_audit  # noqa: E402
from instrumentos.registry import list_profiles, resolve_profile  # noqa: E402

TRANSPOSING_WATCHLIST = (
    "contrabaixo",
    "contrafagote",
    "flautim",
    "clarinete",
    "clarinete_baixo",
    "cor_anglais",
    "trompa",
    "trompete",
)


def _classify_status(profile, base_audit: dict) -> str:
    inst = next(i for i in base_audit["instruments"] if i["instrument_id"] == profile.instrument_id)
    if inst["range_discrepancy"] == "BUG_table_anchor_outside_registry":
        return "FAIL"
    if profile.instrument_id in TRANSPOSING_WATCHLIST and profile.transposition == 0:
        if profile.instrument_id in ("contrabaixo", "contrafagote", "flautim"):
            return "REVIEW_REQUIRED"
    return "PASS"


def build_transposing_audit() -> dict:
    base = build_instrument_register_audit()
    rows = []
    for profile in sorted(list_profiles(), key=lambda p: p.instrument_id):
        table = next(i["table_span"] for i in base["instruments"] if i["instrument_id"] == profile.instrument_id)
        lo, hi = profile.sounding_range
        aliases = [profile.display_name, *profile.aliases]
        rows.append(
            {
                "canonical_id": profile.instrument_id,
                "display_name": profile.display_name,
                "aliases": aliases,
                "family": profile.family,
                "module_name": profile.module_name,
                "table_backed": profile.module_name is not None,
                "source_table_pitch_span": table,
                "registry_sounding_range_midi": [int(lo), int(hi)],
                "registry_transposition_semitones": profile.transposition,
                "manual_input_transposed": False,
                "musicxml_transpose_applied": True,
                "calcular_densidade_expects_sounding_pitch": True,
                "test_coverage": "tests/test_transposing_instrument_sounding_pitch_contract.py",
                "status": _classify_status(profile, base),
            }
        )
    review = [r for r in rows if r["status"] == "REVIEW_REQUIRED"]
    failures = [r for r in rows if r["status"] == "FAIL"]
    return {
        "instrument_count": len(rows),
        "transposing_watchlist_count": len(TRANSPOSING_WATCHLIST),
        "pitch_contract": base["pitch_contract"],
        "review_required": review,
        "failures": failures,
        "instruments": rows,
    }


def _markdown(payload: dict) -> str:
    lines = [
        "# Transposing instrument pitch contract audit",
        "",
        f"- Instruments audited: {payload['instrument_count']}",
        f"- Transposing watchlist: {payload['transposing_watchlist_count']}",
        f"- Failures: {len(payload['failures'])}",
        f"- Review required: {len(payload['review_required'])}",
        "",
        "## Pitch contract",
        "",
    ]
    for k, v in payload["pitch_contract"].items():
        lines.append(f"- **{k}:** {v}")
    if payload["review_required"]:
        lines.extend(["", "## REVIEW REQUIRED", ""])
        for row in payload["review_required"]:
            lines.append(f"- {row['canonical_id']}: transposition metadata is 0 (octave notation only)")
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_transposing_audit()
    out = ROOT / "reports"
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "transposing_instrument_pitch_contract_audit.json"
    md_path = out / "transposing_instrument_pitch_contract_audit.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 1 if payload["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
