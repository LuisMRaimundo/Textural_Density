#!/usr/bin/env python3
"""Diagnostic audit for GPR ``mp`` dynamic interpolation on string tables."""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from instrumentos.gpr_dynamic_interpolation import (  # noqa: E402
    GPR_DYNAMIC_COORDINATES,
    create_dynamic_gpr,
    predict_intermediate_dynamics_gpr,
)
from microtonal import note_to_midi_strict  # noqa: E402
from tests.string_constants import STRING_INSTRUMENTS  # noqa: E402

REPORTS = ROOT / "reports"

def _piecewise_linear_mp(pp: float, mf: float) -> float:
    return 0.5 * pp + 0.5 * mf


def _quadratic_mp(pp: float, mf: float, ff: float) -> float:
    # Lagrange through (3,pp), (5,mf), (7,ff) evaluated at x=4.5 — diagnostic only.
    x0, x1, x2 = 3.0, 5.0, 7.0
    x = 4.5
    l0 = ((x - x1) * (x - x2)) / ((x0 - x1) * (x0 - x2))
    l1 = ((x - x0) * (x - x2)) / ((x1 - x0) * (x1 - x2))
    l2 = ((x - x0) * (x - x1)) / ((x2 - x0) * (x2 - x1))
    return l0 * pp + l1 * mf + l2 * ff


def _gpr_std_at_mp(pp: float, mf: float, ff: float) -> float | None:
    existing = np.array([[3.0], [5.0], [7.0]], dtype=float)
    target = np.array([[4.5]], dtype=float)
    y = np.array([pp, mf, ff], dtype=float)
    gpr = create_dynamic_gpr()
    gpr.fit(existing, y)
    _, std = gpr.predict(target, return_std=True)
    return float(std[0])


def _convex_hull_departure(pp: float, mp: float, mf: float) -> bool:
    lo, hi = min(pp, mf), max(pp, mf)
    return mp < lo or mp > hi


def collect_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in STRING_INSTRUMENTS:
        mod = __import__(f"instrumentos.{spec.module_name}", fromlist=["spectral_data"])
        for note in sorted(mod.spectral_data.keys()):
            pp = float(mod.calcular_densidade(note, "pp"))
            mf = float(mod.calcular_densidade(note, "mf"))
            ff = float(mod.calcular_densidade(note, "ff"))
            preds = predict_intermediate_dynamics_gpr([pp], [mf], [ff])
            gpr_p = float(preds["p"][0])
            gpr_mp = float(preds["mp"][0])
            gpr_f = float(preds["f"][0])
            linear_mp = _piecewise_linear_mp(pp, mf)
            quad_mp = _quadratic_mp(pp, mf, ff)
            std_mp = _gpr_std_at_mp(pp, mf, ff)
            rows.append(
                {
                    "instrument": spec.module_name,
                    "note": note,
                    "midi": float(note_to_midi_strict(note)),
                    "pp_source": pp,
                    "mf_source": mf,
                    "ff_source": ff,
                    "gpr_p": gpr_p,
                    "gpr_mp": gpr_mp,
                    "gpr_f": gpr_f,
                    "linear_mp_estimate": linear_mp,
                    "quadratic_mp_estimate": quad_mp,
                    "gpr_mp_std": std_mp,
                    "mp_minus_p": gpr_mp - gpr_p,
                    "mf_minus_mp": mf - gpr_mp,
                    "outside_pp_mf_interval": _convex_hull_departure(pp, gpr_mp, mf),
                    "finite": math.isfinite(gpr_mp),
                    "negative": gpr_mp < 0,
                    "warnings": [],
                    "model": "GPR_Matern_nu1.5_alpha1e-1_n_restarts10",
                    "mp_coordinate": GPR_DYNAMIC_COORDINATES["mp"],
                }
            )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gpr_mps = [r["gpr_mp"] for r in rows]
    lin_diffs = [abs(r["gpr_mp"] - r["linear_mp_estimate"]) for r in rows]
    quad_diffs = [abs(r["gpr_mp"] - r["quadratic_mp_estimate"]) for r in rows]
    mp_mf_diffs = [abs(r["gpr_mp"] - r["mf_source"]) for r in rows]

    def _top_n(items: list[dict[str, Any]], key: str, n: int = 10) -> list[dict[str, Any]]:
        return sorted(items, key=lambda r: r[key], reverse=True)[:n]

    enriched = []
    for r in rows:
        enriched.append(
            {
                **r,
                "abs_gpr_minus_linear": abs(r["gpr_mp"] - r["linear_mp_estimate"]),
                "abs_gpr_minus_quadratic": abs(r["gpr_mp"] - r["quadratic_mp_estimate"]),
                "abs_mp_minus_mf_source": abs(r["gpr_mp"] - r["mf_source"]),
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "row_count": len(rows),
        "gpr_mp_min": min(gpr_mps),
        "gpr_mp_max": max(gpr_mps),
        "gpr_mp_mean": float(np.mean(gpr_mps)),
        "gpr_mp_median": float(np.median(gpr_mps)),
        "max_abs_gpr_minus_linear": max(lin_diffs),
        "max_abs_gpr_minus_quadratic": max(quad_diffs),
        "non_finite_count": sum(1 for r in rows if not r["finite"]),
        "negative_count": sum(1 for r in rows if r["negative"]),
        "convex_hull_departure_count": sum(1 for r in rows if r["outside_pp_mf_interval"]),
        "top_gpr_vs_linear": _top_n(enriched, "abs_gpr_minus_linear"),
        "top_mp_vs_mf": _top_n(enriched, "abs_mp_minus_mf_source"),
        "review_required": any(
            not r["finite"] or r["negative"] for r in rows
        ),
    }


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS / "mp_dynamic_interpolation_audit.json"
    csv_path = REPORTS / "mp_dynamic_interpolation_audit.csv"
    md_path = REPORTS / "mp_dynamic_interpolation_audit.md"

    payload = {"summary": summary, "rows": rows}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    md_lines = [
        "# mp dynamic interpolation audit",
        "",
        f"- Rows: {summary['row_count']}",
        f"- GPR mp min/max: {summary['gpr_mp_min']:.6f} / {summary['gpr_mp_max']:.6f}",
        f"- GPR mp mean/median: {summary['gpr_mp_mean']:.6f} / {summary['gpr_mp_median']:.6f}",
        f"- Max |GPR mp − linear|: {summary['max_abs_gpr_minus_linear']:.6f}",
        f"- Max |GPR mp − quadratic|: {summary['max_abs_gpr_minus_quadratic']:.6f}",
        f"- Non-finite: {summary['non_finite_count']}",
        f"- Negative: {summary['negative_count']}",
        f"- Convex-hull departures (pp..mf): {summary['convex_hull_departure_count']}",
        f"- Review required: {summary['review_required']}",
        "",
        "## Top GPR vs linear differences",
        "",
    ]
    for item in summary["top_gpr_vs_linear"]:
        md_lines.append(
            f"- {item['instrument']} {item['note']}: GPR={item['gpr_mp']:.4f}, "
            f"linear={item['linear_mp_estimate']:.4f}, "
            f"diff={item['abs_gpr_minus_linear']:.4f}"
        )
    md_lines.extend(["", "## Top |mp − mf_source|", ""])
    for item in summary["top_mp_vs_mf"]:
        md_lines.append(
            f"- {item['instrument']} {item['note']}: mp={item['gpr_mp']:.4f}, "
            f"mf={item['mf_source']:.4f}, diff={item['abs_mp_minus_mf_source']:.4f}"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote {json_path}, {csv_path}, {md_path}")


def main() -> int:
    rows = collect_rows()
    summary = summarize(rows)
    write_outputs(rows, summary)
    if summary["review_required"]:
        print("REVIEW REQUIRED: non-finite or negative mp outputs detected.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
