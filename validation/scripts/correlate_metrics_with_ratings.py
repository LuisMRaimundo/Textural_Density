#!/usr/bin/env python3
"""Correlate score-derived metrics with expert score annotations (when available)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_processor import calculate_metrics
from validation.metrics import kendall_tau, spearman_correlation
from validation.score_schemas import load_score_annotations


DIMENSION_TO_METRIC = {
    "overall_symbolic_vertical_density": lambda r: float(r["density"]["total"]),
    "event_density": lambda r: float(r.get("density_subindices", {}).get("event_count", {}).get("normalized", 0)),
    "interval_compactness": lambda r: float(r["density"]["interval"]),
    "registral_density": lambda r: float(
        r.get("density_subindices", {}).get("registral", {}).get("normalized", 0)
    ),
    "orchestration_mass": lambda r: float(r["density"]["sonic_mass"]),
    "timbral_orchestration_complexity": lambda r: float(
        r.get("density_subindices", {}).get("timbral_heterogeneity", {}).get("normalized", 0)
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("annotation_file")
    parser.add_argument("--report", default="validation/reports/score_validation_report.md")
    args = parser.parse_args()

    annotations = load_score_annotations(args.annotation_file)
    real = [a for a in annotations if not a.is_fixture]

    lines = ["# Score validation report", ""]
    if not real:
        lines.append(
            "No external score annotations available. Validation status: **verification only**."
        )
        Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(lines[-1])
        return 0

    by_dim: dict[str, tuple[list[float], list[float]]] = {}
    for ann in real:
        input_path = ROOT / ann.input_file
        if not input_path.exists():
            continue
        with open(input_path, encoding="utf-8") as f:
            input_data = json.load(f)
        resultados, _, _ = calculate_metrics(input_data)
        metric_fn = DIMENSION_TO_METRIC.get(ann.rating_dimension)
        if metric_fn is None:
            continue
        predicted = metric_fn(resultados)
        bucket = by_dim.setdefault(ann.rating_dimension, ([], []))
        bucket[0].append(predicted)
        bucket[1].append(ann.rating_value)

    lines.append(f"Non-fixture annotations analysed: {len(real)}")
    lines.append("")
    for dim, (pred, obs) in sorted(by_dim.items()):
        lines.append(f"## {dim}")
        if len(pred) < 3:
            lines.append(f"Insufficient paired samples ({len(pred)}); need ≥3 for correlation.")
            lines.append("")
            continue
        rho, p_rho = spearman_correlation(pred, obs)
        tau, p_tau = kendall_tau(pred, obs)
        lines.append(f"- Spearman rho = {rho:.4f} (p={p_rho:.4g})")
        lines.append(f"- Kendall tau = {tau:.4f} (p={p_tau:.4g})")
        lines.append(f"- n = {len(pred)}")
        lines.append("")

    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
