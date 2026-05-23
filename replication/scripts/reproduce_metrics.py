#!/usr/bin/env python3
"""Recompute score-only metrics for replication corpus (synthetic + official benchmarks)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.defaults import METRIC_SCHEMA_VERSION, apply_research_defaults
from core.hash_utils import config_hash, input_hash_from_dict
from data_processor import calculate_metrics

OFFICIAL_LICENSES = frozenset(
    {
        "owned_by_project_author",
        "public_domain_verified",
        "openly_licensed",
    }
)


def _load_manifest() -> dict:
    path = ROOT / "replication" / "benchmark_manifest.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _freeze_payload(
    *,
    piece_id: str,
    source: str,
    synthetic_fixture: bool,
    input_data: dict,
    merged_defaults: dict,
    resultados: dict,
) -> dict:
    meta = resultados.get("metric_metadata", {})
    return {
        "piece_id": piece_id,
        "source": source,
        "synthetic_fixture": synthetic_fixture,
        "score_only_mode": bool(meta.get("score_only_mode", True)),
        "software_version": meta.get("software_version", "unknown"),
        "metric_schema_version": METRIC_SCHEMA_VERSION,
        "config_hash": config_hash(merged_defaults),
        "input_hash": input_hash_from_dict(input_data),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "density": resultados.get("density", {}),
        "density_subindices": resultados.get("density_subindices", {}),
        "construct_records": resultados.get("construct_records", {}),
        "metric_metadata": meta,
    }


def _process_synthetic_metadata(
    meta_dir: Path,
    out_dir: Path,
    merged_defaults: dict,
) -> int:
    count = 0
    for meta_file in sorted(meta_dir.glob("*.json")):
        with open(meta_file, encoding="utf-8") as f:
            meta = json.load(f)
        input_data = apply_research_defaults({**merged_defaults, **meta.get("input", {})})
        resultados, _, _ = calculate_metrics(input_data)
        payload = _freeze_payload(
            piece_id=meta.get("piece_id", meta_file.stem),
            source=meta.get("source", "unknown"),
            synthetic_fixture=meta.get("source") == "synthetic_fixture",
            input_data=input_data,
            merged_defaults=merged_defaults,
            resultados=resultados,
        )
        out_path = out_dir / f"{meta_file.stem}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"Wrote {out_path.relative_to(ROOT)} [synthetic_fixture]")
        count += 1
    return count


def _process_official_score_files(manifest: dict, out_dir: Path, merged_defaults: dict) -> int:
    """Process official representative benchmarks from manifest (when files exist)."""
    count = 0
    for entry in manifest.get("entries", []):
        if not entry.get("include_in_official_benchmark"):
            continue
        if entry.get("license_status") not in OFFICIAL_LICENSES:
            print(
                f"SKIP {entry.get('benchmark_id')}: license_status "
                f"{entry.get('license_status')} not eligible for official benchmark"
            )
            continue
        file_path = ROOT / entry["file_path"]
        if not file_path.is_file():
            print(f"SKIP {entry.get('benchmark_id')}: file not found at {entry['file_path']}")
            continue
        fmt = entry.get("format", "")
        if fmt == "json_input":
            with open(file_path, encoding="utf-8") as f:
                meta = json.load(f)
            input_data = apply_research_defaults({**merged_defaults, **meta.get("input", {})})
        else:
            print(
                f"SKIP {entry.get('benchmark_id')}: score file format {fmt} "
                "requires manual metadata wiring (not yet automated in reproduce_metrics)"
            )
            continue
        resultados, _, _ = calculate_metrics(input_data)
        bid = entry["benchmark_id"]
        payload = _freeze_payload(
            piece_id=bid,
            source=entry.get("source", "official_benchmark"),
            synthetic_fixture=False,
            input_data=input_data,
            merged_defaults=merged_defaults,
            resultados=resultados,
        )
        out_path = out_dir / f"{bid}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        csv_dir = ROOT / "replication" / "outputs_frozen" / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        csv_path = csv_dir / f"{bid}.csv"
        d = payload["density"]
        csv_path.write_text(
            "benchmark_id,density.total,density.interval,density.sonic_mass\n"
            f"{bid},{d.get('total')},{d.get('interval')},{d.get('sonic_mass')}\n",
            encoding="utf-8",
        )
        print(f"Wrote {out_path.relative_to(ROOT)} [official_representative]")
        count += 1
    return count


def main() -> int:
    manifest = _load_manifest()
    meta_dir = ROOT / "replication" / "corpus" / "metadata"
    out_dir = ROOT / "replication" / "outputs_frozen" / "json"
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = ROOT / "replication" / "configs" / "score_only_default.json"
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    merged_defaults = apply_research_defaults(config)

    n_synthetic = _process_synthetic_metadata(meta_dir, out_dir, merged_defaults)
    n_official = _process_official_score_files(manifest, out_dir, merged_defaults)

    if n_synthetic == 0 and n_official == 0:
        print("No outputs generated.")
        return 1
    print(
        f"Done: {n_synthetic} synthetic fixture(s), {n_official} official representative benchmark(s)."
    )
    if manifest.get("corpus_maturity") == "synthetic_scaffold_only":
        print("WARNING: corpus is not yet representative — synthetic outputs are scaffold only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
