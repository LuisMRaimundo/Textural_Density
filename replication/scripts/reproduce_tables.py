#!/usr/bin/env python3
"""Generate thesis/research tables from frozen replication outputs."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_manifest() -> dict:
    path = ROOT / "replication" / "benchmark_manifest.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    config_path = ROOT / "replication" / "configs" / "thesis_tables_config.json"
    with open(config_path, encoding="utf-8") as f:
        table_cfg = json.load(f)
    manifest = _load_manifest()
    frozen_dir = ROOT / "replication" / "outputs_frozen" / "json"
    out_dir = ROOT / "replication" / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for frozen_path in sorted(frozen_dir.glob("*.json")):
        with open(frozen_path, encoding="utf-8") as f:
            data = json.load(f)
        density = data.get("density", {})
        sub = data.get("density_subindices", {})
        constructs = data.get("construct_records", {})
        meta = data.get("metric_metadata", {})
        ec = sub.get("event_count", {}).get("raw", {})
        piece_id = data.get("piece_id", frozen_path.stem)
        synthetic = bool(data.get("synthetic_fixture", False))
        ic = constructs.get("interval_compactness", {})
        rd = constructs.get("registral_density", {})
        om = constructs.get("orchestration_mass", {})
        rows.append(
            {
                "benchmark_id": piece_id,
                "synthetic_fixture": synthetic,
                "density.total": density.get("total"),
                "density.interval": density.get("interval"),
                "density.sonic_mass": density.get("sonic_mass"),
                "event_count": ec.get("event_count") if isinstance(ec, dict) else None,
                "interval_compactness_norm": ic.get("normalized_value")
                or sub.get("interval_compactness", {}).get("normalized"),
                "registral_norm": rd.get("normalized_value")
                or sub.get("registral", {}).get("normalized"),
                "orchestration_mass": om.get("value") or density.get("sonic_mass"),
                "composite_subindex": sub.get("composite", {}).get("value"),
                "config_hash": meta.get("config_hash"),
                "input_hash": meta.get("input_hash"),
                "metric_schema_version": meta.get("metric_schema_version"),
                "score_only_mode": data.get("score_only_mode", meta.get("score_only_mode")),
            }
        )

    if not rows:
        print("No frozen outputs found; run reproduce_metrics.py first.")
        return 1

    table_id = table_cfg["table_id"]
    out_csv = out_dir / f"{table_id}.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    out_md = out_dir / f"{table_id}.md"
    lines = [
        f"# {table_id}",
        "",
        f"Corpus maturity: **{manifest.get('corpus_maturity', 'unknown')}**",
        "",
        manifest.get("warning", ""),
        "",
        "| " + " | ".join(rows[0].keys()) + " |",
        "| " + " | ".join("---" for _ in rows[0]) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[k]) for k in rows[0]) + " |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_csv.relative_to(ROOT)} ({len(rows)} row(s))")
    print(f"Wrote {out_md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
