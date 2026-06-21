#!/usr/bin/env python3
"""Refresh golden regression fixtures after intentional acoustic-table updates."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from data_processor import calculate_metrics, calcular_densidade_ponderada_normalizada  # noqa: E402
from densidade_intervalar import calculate_interval_density  # noqa: E402
from core.defaults import apply_research_defaults  # noqa: E402
from core.pipeline import calculate_metrics as pipeline_calculate_metrics  # noqa: E402
from snapshot_utils import extract_metadata_snapshot, extract_numeric_snapshot  # noqa: E402


def main() -> int:
    baseline_input = {
        "notes": ["C4", "E4", "G4", "C5"],
        "dynamics": ["mf", "f", "ff", "mf"],
        "instruments": ["flauta", "clarinete", "flauta", "clarinete"],
        "num_instruments": [1, 2, 1, 1],
        "weight_factor": 0.5,
        "save_results": False,
        "show_graphs": False,
    }
    resultados, densidades, pitches = calculate_metrics(baseline_input)
    baseline = {
        "density": {k: float(v) for k, v in resultados["density"].items()},
        "harmonic_ratio": float(resultados["additional_metrics"]["harmonic_ratio"]),
        "complexity": float(resultados["additional_metrics"]["complexity"]),
        "pitches_primary_count": len(pitches),
        "instrument_densities": [float(x) for x in densidades],
        "note_to_midi_C4": 60.0,
        "midi_to_hz_A4": 440.0,
        "interval_density_C4_G4": float(
            calculate_interval_density(["C4", "G4"], lamb=0.05, use_optimization=False)
        ),
        "weighted_density_DI50_DV5": float(
            calcular_densidade_ponderada_normalizada(50.0, 5.0, w=0.5)
        ),
        "chroma_sum": 1.0,
    }
    baseline_path = ROOT / "tests" / "fixtures" / "regression_baseline.json"
    baseline_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"Wrote {baseline_path}")

    meta_path = ROOT / "replication" / "corpus" / "metadata" / "synthetic_triad.json"
    config_path = ROOT / "replication" / "configs" / "score_only_default.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    triad_input = apply_research_defaults({**cfg, **meta.get("input", {})})
    triad_resultados, _, _ = pipeline_calculate_metrics(triad_input)
    numeric = extract_numeric_snapshot(triad_resultados)
    metadata = extract_metadata_snapshot(triad_resultados)
    (ROOT / "tests" / "snapshots" / "numeric_outputs" / "synthetic_triad.json").write_text(
        json.dumps(numeric, indent=2), encoding="utf-8"
    )
    (ROOT / "tests" / "snapshots" / "metadata_outputs" / "synthetic_triad.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    (ROOT / "replication" / "outputs_frozen" / "json" / "synthetic_triad.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print("Wrote synthetic_triad snapshots")

    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "replication" / "scripts" / "reproduce_metrics.py")],
        check=True,
        cwd=str(ROOT),
    )
    print("Regenerated replication frozen outputs via reproduce_metrics.py")

    manifest_path = ROOT / "benchmarks" / "corpus" / "manifest.json"
    if manifest_path.is_file():
        subprocess.run(
            [sys.executable, str(ROOT / "benchmarks" / "scripts" / "freeze_outputs.py")],
            check=True,
            cwd=str(ROOT),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
