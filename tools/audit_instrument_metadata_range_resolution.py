#!/usr/bin/env python3
"""Generate instrument metadata / range resolution audit reports."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from instrumentos.metadata_range_audit import build_metadata_range_resolution_audit

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def _markdown(payload: dict) -> str:
    excl_ids = payload.get("table_excludes_sounding_range_ids") or []
    excl_n = payload.get("table_excludes_sounding_range_count", 0)
    lines = [
        "# Instrument metadata / range resolution audit",
        "",
        f"**Instruments audited:** {payload['instrument_count']}",
        "",
        "## Executive summary",
        "",
        "- **Double bass:** source_table_span E1–C5 (MIDI 28–72) aligns with committed table and registry; E1–A3 was obsolete documentation.",
        "- **Violin sounding [55,103]:** table G3–G7 aligns (not a double-bass case).",
        f"- **Table excludes sounding range (partial):** {excl_n} instrument(s): "
        f"{', '.join(excl_ids) if excl_ids else 'none'}.",
        "- **Technique:** modules declare `source_technique` / `table_supported_techniques`; registry lists broader organological capabilities.",
        "- **Trombone:** committed table (`trombone.py`, C#1–C5) — **PASS** when registry matches the table span.",
        "- **Tuba:** committed table (`tuba.py`, C1–A#4) — **PASS** when registry matches the table span.",
        "- **Transposition:** registry field is metadata-only; manual input is sounding pitch; MusicXML applies `<transpose>` once.",
        "",
        "## Range semantics",
        "",
    ]
    for key, desc in payload["range_semantics"].items():
        lines.append(f"- **{key}:** {desc}")
    lines.extend(
        [
            "",
            "## Double-bass resolution",
            "",
            f"- Classification: **{payload['double_bass_resolution']['classification']}**",
            f"- Source table span: {payload['double_bass_resolution']['source_table_span']}",
            f"- Obsolete docs span: {payload['double_bass_resolution']['obsolete_documentation_span']} ({payload['double_bass_resolution']['obsolete_status']})",
            f"- Upper-register QC: **{payload['double_bass_resolution']['upper_register_methodological_qc']}**",
            f"- {payload['double_bass_resolution']['rationale']}",
            "",
            "## Trombone review",
            "",
            f"- Classification: **{payload['trombone_review']['classification']}**",
            f"- {payload['trombone_review']['rationale']}",
            "",
            "## Tuba review",
            "",
            f"- Classification: **{payload['tuba_review']['classification']}**",
            f"- {payload['tuba_review']['rationale']}",
            "",
            "## Transposition review",
            "",
            f"- Classification: **{payload['transposition_review']['classification']}**",
            f"- {payload['transposition_review']['contract']}",
            "",
            "## Per-instrument summary",
            "",
            "| ID | Table span | Sounding MIDI | Comfortable | Excludes range? | Range | Technique |",
            "|----|------------|---------------|-------------|-----------------|-------|-----------|",
        ]
    )
    for inst in payload["instruments"]:
        span = inst["source_table_span"]
        span_s = f"{span['first_note']}–{span['last_note']}" if span else "—"
        snd = inst["registry_sounding_range_midi"]
        cft = inst["registry_comfortable_range_midi"]
        excl = inst.get("exclusion_kind") or "—"
        if inst.get("table_excludes_sounding_range") and excl == "partial_table":
            excl_s = (
                f"YES (lo={inst.get('missing_low_semitones')}, "
                f"hi={inst.get('missing_high_semitones')})"
            )
        else:
            excl_s = excl
        lines.append(
            f"| {inst['instrument_id']} | {span_s} | {snd[0]}–{snd[1]} | {cft[0]}–{cft[1]} | "
            f"{excl_s} | {inst['range_classification']} | {inst['technique']['classification']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _write_csv(payload: dict, path: Path) -> None:
    fieldnames = [
        "instrument_id",
        "display_name",
        "module_name",
        "table_backed",
        "source_table_first",
        "source_table_last",
        "source_table_row_count",
        "instrument_source_pitch_range",
        "registry_sounding_min",
        "registry_sounding_max",
        "registry_comfortable_min",
        "registry_comfortable_max",
        "registry_transposition",
        "source_technique",
        "table_supported_techniques",
        "registry_supported_techniques",
        "range_classification",
        "technique_classification",
        "table_excludes_sounding_range",
        "exclusion_kind",
        "missing_low_semitones",
        "missing_high_semitones",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for inst in payload["instruments"]:
            span = inst["source_table_span"] or {}
            tech = inst["technique"]
            writer.writerow(
                {
                    "instrument_id": inst["instrument_id"],
                    "display_name": inst["display_name"],
                    "module_name": inst["module_name"] or "",
                    "table_backed": inst["table_backed"],
                    "source_table_first": span.get("first_note", ""),
                    "source_table_last": span.get("last_note", ""),
                    "source_table_row_count": span.get("row_count", ""),
                    "instrument_source_pitch_range": inst["instrument_source_pitch_range"],
                    "registry_sounding_min": inst["registry_sounding_range_midi"][0],
                    "registry_sounding_max": inst["registry_sounding_range_midi"][1],
                    "registry_comfortable_min": inst["registry_comfortable_range_midi"][0],
                    "registry_comfortable_max": inst["registry_comfortable_range_midi"][1],
                    "registry_transposition": inst["registry_transposition"],
                    "source_technique": tech.get("source_technique") or "",
                    "table_supported_techniques": "|".join(
                        tech.get("table_supported_techniques") or []
                    ),
                    "registry_supported_techniques": "|".join(
                        tech.get("registry_supported_techniques") or []
                    ),
                    "range_classification": inst["range_classification"],
                    "technique_classification": tech.get("classification"),
                    "table_excludes_sounding_range": inst.get(
                        "table_excludes_sounding_range", ""
                    ),
                    "exclusion_kind": inst.get("exclusion_kind", ""),
                    "missing_low_semitones": inst.get("missing_low_semitones", ""),
                    "missing_high_semitones": inst.get("missing_high_semitones", ""),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports-dir", type=Path, default=REPORTS)
    args = parser.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    payload = build_metadata_range_resolution_audit()
    json_path = args.reports_dir / "instrument_metadata_range_resolution_audit.json"
    md_path = args.reports_dir / "instrument_metadata_range_resolution_audit.md"
    csv_path = args.reports_dir / "instrument_metadata_range_resolution_audit.csv"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    _write_csv(payload, csv_path)
    print(f"Wrote {json_path.name}, {md_path.name}, {csv_path.name}")


if __name__ == "__main__":
    main()
