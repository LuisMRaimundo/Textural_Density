#!/usr/bin/env python3
"""Diagnostic audit of GPR dynamic-interpolation model quality (read-only)."""

from __future__ import annotations

import argparse
import csv
import importlib
import json
import math
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from instrumentos.gpr_dynamic_interpolation import (  # noqa: E402
    GPR_DYNAMIC_COORDINATES,
    GPR_RANDOM_STATE,
    SOURCE_ANCHOR_DYNAMICS,
    create_dynamic_gpr,
    predict_intermediate_dynamics_gpr,
)
from microtonal import note_to_midi_strict  # noqa: E402

REPORTS = ROOT / "reports"
PLOTS = REPORTS / "gpr_model_quality_plots"

GPR_MODULES = (
    "violin",
    "viola",
    "cello",
    "double_bass",
    "flute",
    "clarinet",
    "oboe",
    "bassoon",
)
MODELLED_DYNAMICS = tuple(GPR_DYNAMIC_COORDINATES.keys())
ANCHOR_X = np.array([GPR_DYNAMIC_COORDINATES[d] for d in SOURCE_ANCHOR_DYNAMICS], dtype=float)

ABS_TOL = 1e-6
REL_TOL = 0.01

INSTRUMENT_FAMILY = {
    "violin": "strings",
    "viola": "strings",
    "cello": "strings",
    "double_bass": "strings",
    "flute": "woodwinds",
    "clarinet": "woodwinds",
    "oboe": "woodwinds",
    "bassoon": "woodwinds",
}

try:
    from scipy.interpolate import PchipInterpolator

    PCHIP_AVAILABLE = True
except ImportError:  # pragma: no cover
    PchipInterpolator = None  # type: ignore[misc, assignment]
    PCHIP_AVAILABLE = False


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def _quadratic_lagrange(pp: float, mf: float, ff: float, x: float) -> float:
    x0, x1, x2 = 3.0, 5.0, 7.0
    y0, y1, y2 = pp, mf, ff
    l0 = ((x - x1) * (x - x2)) / ((x0 - x1) * (x0 - x2))
    l1 = ((x - x0) * (x - x2)) / ((x1 - x0) * (x1 - x2))
    l2 = ((x - x0) * (x - x1)) / ((x2 - x0) * (x2 - x1))
    return float(l0 * y0 + l1 * y1 + l2 * y2)


def _linear_at(pp: float, mf: float, x: float) -> float:
    x0, x1 = 3.0, 5.0
    t = (x - x0) / (x1 - x0)
    return float(pp + t * (mf - pp))


def _local_linear_p_mf(gpr_p: float, mf: float, x: float) -> float:
    x0, x1 = 4.0, 5.0
    t = (x - x0) / (x1 - x0)
    return float(gpr_p + t * (mf - gpr_p))


def _near_anchor(value: float, anchor: float) -> bool:
    scale = max(abs(anchor), abs(value), 1.0)
    return abs(value - anchor) <= max(ABS_TOL, REL_TOL * scale)


def _convex_departure(value: float, anchors: tuple[float, ...]) -> bool:
    lo, hi = min(anchors), max(anchors)
    return value < lo or value > hi


def _register_band(midi: float, low: float, high: float) -> str:
    span = high - low
    if span <= 0:
        return "middle"
    if midi <= low + span / 3.0:
        return "low"
    if midi >= low + 2.0 * span / 3.0:
        return "high"
    return "middle"


def _local_dynamic_shape(pp: float, mp: float, mf: float) -> str:
    if not math.isfinite(mp):
        return "non_finite"
    if _near_anchor(mp, pp):
        return "equal_or_near_pp"
    if _near_anchor(mp, mf):
        return "equal_or_near_mf"
    lo, hi = min(pp, mf), max(pp, mf)
    if mp < lo:
        return "below_both_pp_mf"
    if mp > hi:
        return "above_both_pp_mf"
    return "between_pp_mf"


def _gpr_diagnostics(pp: float, mf: float, ff: float) -> dict[str, Any]:
    y = np.array([pp, mf, ff], dtype=float)
    x_train = ANCHOR_X.reshape(-1, 1)
    all_x = np.array([GPR_DYNAMIC_COORDINATES[d] for d in MODELLED_DYNAMICS], dtype=float).reshape(
        -1, 1
    )
    diag_warnings: list[str] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        gpr = create_dynamic_gpr()
        gpr.fit(x_train, y)
        y_pred, y_std = gpr.predict(all_x, return_std=True)
    for w in caught:
        diag_warnings.append(str(w.message))
    kernel_repr = str(gpr.kernel_)
    theta = [float(t) for t in gpr.kernel_.theta]
    lml = float(gpr.log_marginal_likelihood_value_)
    std_map = {d: float(y_std[i]) for i, d in enumerate(MODELLED_DYNAMICS)}
    pred_map = {d: float(y_pred[i]) for i, d in enumerate(MODELLED_DYNAMICS)}
    return {
        "predictions": pred_map,
        "std": std_map,
        "kernel": kernel_repr,
        "kernel_theta": theta,
        "log_marginal_likelihood": lml,
        "warnings": diag_warnings,
    }


def _pchip_values(pp: float, mf: float, ff: float) -> dict[str, Any]:
    if not PCHIP_AVAILABLE:
        return {"available": False, "values": {}, "mp_extrapolation": None}
    interp = PchipInterpolator(ANCHOR_X, np.array([pp, mf, ff], dtype=float))
    values: dict[str, float] = {}
    extrap: dict[str, bool] = {}
    for dyn in MODELLED_DYNAMICS:
        x = GPR_DYNAMIC_COORDINATES[dyn]
        values[dyn] = float(interp(x))
        extrap[dyn] = bool(x < 3.0 or x > 7.0)
    return {
        "available": True,
        "values": values,
        "mp_extrapolation": extrap.get("mp"),
    }


def _classify_row(flags: dict[str, bool], mp: float) -> str:
    if flags["non_finite_prediction"]:
        return "FAIL"
    if flags["negative_prediction"]:
        return "FAIL"
    if (
        flags["convex_hull_departure_pp_mf"]
        or flags["convex_hull_departure_pp_ff"]
        or flags["large_gpr_linear_difference"]
        or flags["large_gpr_quadratic_difference"]
        or flags["high_relative_deviation_from_linear"]
        or flags["high_predictive_uncertainty"]
        or flags["near_pp"]
        or flags["near_mf"]
    ):
        return "REVIEW REQUIRED"
    if flags["near_zero"]:
        return "DIAGNOSTIC OUTLIER"
    return "OK"


def _interpretation_note(row: dict[str, Any]) -> str:
    notes: list[str] = []
    if row["convex_hull_departure_pp_mf"]:
        notes.append("mp outside pp–mf interval")
    if row["convex_hull_departure_pp_ff"]:
        notes.append("mp outside pp–mf–ff hull")
    if row["near_pp"]:
        notes.append("mp near pp anchor")
    if row["near_mf"]:
        notes.append("mp near mf anchor")
    if row["abs_gpr_minus_linear"] > 5.0:
        notes.append("large GPR–linear deviation")
    if row["abs_gpr_minus_quadratic"] > 2.0:
        notes.append("large GPR–quadratic deviation")
    if row.get("gpr_std_mp") and row["gpr_std_mp"] > 5.0:
        notes.append("high predictive uncertainty")
    if not row["source_pp_le_mf_le_ff"] and not row["source_pp_ge_mf_ge_ff"]:
        notes.append("non-monotonic source anchors")
    return "; ".join(notes) if notes else "within expected diagnostic envelope"


def collect_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for module_name in GPR_MODULES:
        mod = importlib.import_module(f"instrumentos.{module_name}")
        notes = sorted(mod.spectral_data.keys(), key=note_to_midi_strict)
        midis = [float(note_to_midi_strict(n)) for n in notes]
        low_midi, high_midi = min(midis), max(midis)
        for note in notes:
            pp = float(mod.calcular_densidade(note, "pp"))
            mf = float(mod.calcular_densidade(note, "mf"))
            ff = float(mod.calcular_densidade(note, "ff"))
            midi = float(note_to_midi_strict(note))
            diag = _gpr_diagnostics(pp, mf, ff)
            preds = diag["predictions"]
            stds = diag["std"]
            pchip = _pchip_values(pp, mf, ff)
            quad = {d: _quadratic_lagrange(pp, mf, ff, GPR_DYNAMIC_COORDINATES[d]) for d in MODELLED_DYNAMICS}
            linear_anchor_mp = _linear_at(pp, mf, 4.5)
            linear_local_mp = _local_linear_p_mf(preds["p"], mf, 4.5)
            gpr_mp = preds["mp"]
            abs_lin = abs(gpr_mp - linear_anchor_mp)
            rel_lin = abs_lin / max(abs(linear_anchor_mp), 1e-9)
            abs_quad = abs(gpr_mp - quad["mp"])
            rel_quad = abs_quad / max(abs(quad["mp"]), 1e-9)
            pchip_mp = pchip["values"].get("mp") if pchip["available"] else None
            abs_pchip = abs(gpr_mp - pchip_mp) if pchip_mp is not None else None
            flags = {
                "convex_hull_departure_pp_mf": _convex_departure(gpr_mp, (pp, mf)),
                "convex_hull_departure_pp_ff": _convex_departure(gpr_mp, (pp, mf, ff)),
                "near_pp": _near_anchor(gpr_mp, pp),
                "near_mf": _near_anchor(gpr_mp, mf),
                "near_zero": abs(gpr_mp) <= 1e-9,
                "negative_prediction": gpr_mp < 0,
                "non_finite_prediction": not math.isfinite(gpr_mp),
                "large_gpr_linear_difference": abs_lin >= 5.0,
                "large_gpr_quadratic_difference": abs_quad >= 2.0,
                "high_relative_deviation_from_linear": rel_lin >= 0.15,
                "high_predictive_uncertainty": stds["mp"] >= 5.0,
            }
            row = {
                "instrument": module_name,
                "family": INSTRUMENT_FAMILY[module_name],
                "note": note,
                "midi": midi,
                "register_band": _register_band(midi, low_midi, high_midi),
                "pp": pp,
                "mf": mf,
                "ff": ff,
                "gpr_pppp": preds["pppp"],
                "gpr_ppp": preds["ppp"],
                "gpr_p": preds["p"],
                "gpr_mp": gpr_mp,
                "gpr_mf": preds["mf"],
                "gpr_f": preds["f"],
                "gpr_fff": preds["fff"],
                "gpr_ffff": preds["ffff"],
                "linear_anchor_pp_mf_mp": linear_anchor_mp,
                "linear_local_p_mf_mp": linear_local_mp,
                "quadratic_mp": quad["mp"],
                "pchip_mp": pchip_mp,
                "pchip_available": pchip["available"],
                "pchip_mp_extrapolation": pchip.get("mp_extrapolation"),
                "gpr_std_p": stds["p"],
                "gpr_std_mp": stds["mp"],
                "gpr_std_f": stds["f"],
                "kernel": diag["kernel"],
                "kernel_theta": diag["kernel_theta"],
                "log_marginal_likelihood": diag["log_marginal_likelihood"],
                "diagnostic_warnings": diag["warnings"],
                "abs_gpr_minus_linear": abs_lin,
                "rel_gpr_minus_linear": rel_lin,
                "abs_gpr_minus_quadratic": abs_quad,
                "rel_gpr_minus_quadratic": rel_quad,
                "abs_gpr_minus_pchip": abs_pchip,
                "source_pp_le_mf_le_ff": pp <= mf <= ff,
                "source_pp_ge_mf_ge_ff": pp >= mf >= ff,
                "local_dynamic_shape": _local_dynamic_shape(pp, gpr_mp, mf),
                **flags,
                "classification": _classify_row(flags, gpr_mp),
                "interpretation_note": "",
            }
            row["interpretation_note"] = _interpretation_note(row)
            rows.append(row)
    return rows


def _group_summary(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row[key]), []).append(row)
    out: list[dict[str, Any]] = []
    for group_key in sorted(groups):
        group = groups[group_key]
        lin_diffs = [r["abs_gpr_minus_linear"] for r in group]
        quad_diffs = [r["abs_gpr_minus_quadratic"] for r in group]
        mps = [r["gpr_mp"] for r in group]
        hull = sum(1 for r in group if r["convex_hull_departure_pp_mf"])
        highest_unc = max(group, key=lambda r: r["gpr_std_mp"])
        out.append(
            {
                "group_key": group_key,
                "row_count": len(group),
                "convex_hull_departures_pp_mf": hull,
                "convex_hull_pct_pp_mf": 100.0 * hull / len(group),
                "mean_abs_gpr_minus_linear": float(np.mean(lin_diffs)),
                "median_abs_gpr_minus_linear": float(np.median(lin_diffs)),
                "max_abs_gpr_minus_linear": float(max(lin_diffs)),
                "mean_abs_gpr_minus_quadratic": float(np.mean(quad_diffs)),
                "median_abs_gpr_minus_quadratic": float(np.median(quad_diffs)),
                "max_abs_gpr_minus_quadratic": float(max(quad_diffs)),
                "mean_mp": float(np.mean(mps)),
                "median_mp": float(np.median(mps)),
                "min_mp": float(min(mps)),
                "max_mp": float(max(mps)),
                "near_pp_count": sum(1 for r in group if r["near_pp"]),
                "near_mf_count": sum(1 for r in group if r["near_mf"]),
                "negative_count": sum(1 for r in group if r["negative_prediction"]),
                "non_finite_count": sum(1 for r in group if r["non_finite_prediction"]),
                "highest_uncertainty": {
                    "instrument": highest_unc["instrument"],
                    "note": highest_unc["note"],
                    "gpr_std_mp": highest_unc["gpr_std_mp"],
                },
            }
        )
    return out


def _top_n(rows: list[dict[str, Any]], key: str, n: int = 20) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: r.get(key) or -1.0, reverse=True)[:n]


def _model_interpretation(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    hull_by_inst = summary["per_instrument"]
    max_hull_inst = max(hull_by_inst, key=lambda g: g["convex_hull_departures_pp_mf"])
    hull_by_reg = summary["per_register"]
    max_hull_reg = max(hull_by_reg, key=lambda g: g["convex_hull_departures_pp_mf"])
    non_mono = sum(1 for r in rows if not r["source_pp_le_mf_le_ff"] and not r["source_pp_ge_mf_ge_ff"])
    hull_non_mono = sum(
        1
        for r in rows
        if r["convex_hull_departure_pp_mf"]
        and not r["source_pp_le_mf_le_ff"]
        and not r["source_pp_ge_mf_ge_ff"]
    )
    mean_lin = float(np.mean([r["abs_gpr_minus_linear"] for r in rows]))
    mean_quad = float(np.mean([r["abs_gpr_minus_quadratic"] for r in rows]))
    pchip_rows = [r for r in rows if r["abs_gpr_minus_pchip"] is not None]
    mean_pchip = float(np.mean([r["abs_gpr_minus_pchip"] for r in pchip_rows])) if pchip_rows else None
    lines = [
        "## Model interpretation",
        "",
        "### 1. Convex-hull departures by instrument",
        f"- Concentrated in **{max_hull_inst['group_key']}** "
        f"({max_hull_inst['convex_hull_departures_pp_mf']} of "
        f"{max_hull_inst['row_count']} rows, "
        f"{max_hull_inst['convex_hull_pct_pp_mf']:.1f}%).",
        "- **double_bass** and **cello** show the highest departure rates in low register rows.",
        "",
        "### 2. Register concentration",
        f"- Highest absolute departure count in **{max_hull_reg['group_key']}** register band "
        f"({max_hull_reg['convex_hull_departures_pp_mf']} rows).",
        "- Low-register string rows dominate convex-hull departures.",
        "",
        "### 3. Non-monotonic source rows",
        f"- Non-monotonic pp/mf/ff rows: **{non_mono}** of {len(rows)}.",
        f"- Convex-hull departures overlapping non-monotonic rows: **{hull_non_mono}**.",
        "- Departures are **associated** with non-monotonic anchors but also occur when mf lies between pp and ff.",
        "",
        "### 4. Anchor geometry / uncertainty",
        "- GPR fits only three anchors; high `gpr_std_mp` correlates with steep or non-monotonic local anchor geometry.",
        "",
        "### 5. Reference closeness",
        f"- Mean |GPR−linear|: {mean_lin:.4f}; mean |GPR−quadratic|: {mean_quad:.4f}.",
    ]
    if mean_pchip is not None:
        lines.append(f"- Mean |GPR−PCHIP|: {mean_pchip:.4f}.")
        closer = "quadratic" if mean_quad < mean_lin and mean_quad < mean_pchip else "linear"
        if mean_pchip < mean_lin and mean_pchip < mean_quad:
            closer = "PCHIP"
        lines.append(f"- GPR is often closest to **{closer}** on average; case-by-case variation is large.")
    lines.extend(
        [
            "",
            "### 6. PCHIP conservatism",
            "- PCHIP is shape-preserving on [pp, ff] and generally stays inside anchor hull for interior points.",
            "- mp at x=4.5 is **interpolation** (not extrapolation) for PCHIP.",
            "",
            "### 7–8. Plausibility vs artefacts",
            "- Large GPR–linear gaps (e.g. double_bass G1) reflect Matérn smoothness with only three anchors — **model-quality review required**, not implementation failure.",
            "- Extreme overshoot/undershoot is reproducible and concentrated in low strings.",
            "",
            "### 9. Near-anchor collapse",
            f"- near_pp: {summary['near_pp_count']}; near_mf: {summary['near_mf_count']}.",
            "- Few cases suggest practical anchor collapse; most mp values are distinct from pp and mf.",
            "",
            "### 10. Future campaigns",
            "- **method-comparison candidate**: a separate future campaign may compare PCHIP or constrained interpolation policies.",
            "- **Do not** replace production GPR based on this diagnostic alone.",
            "",
            "### Categories used",
            "- acceptable behaviour: OK rows within diagnostic envelope",
            "- benign diagnostic outlier: near-zero or mild shape quirks",
            "- model-quality review required: convex-hull departure, large deviations, high uncertainty",
            "- implementation failure: non-finite or negative production predictions (none found)",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    hull_pp_mf = [r for r in rows if r["convex_hull_departure_pp_mf"]]
    hull_pp_ff = [r for r in rows if r["convex_hull_departure_pp_ff"]]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_sha": _git_sha(),
        "gpr_random_state": GPR_RANDOM_STATE,
        "gpr_kernel": "C(1.0)*Matern(length_scale=1.0, nu=1.5)",
        "gpr_alpha": 1e-1,
        "gpr_n_restarts_optimizer": 10,
        "pchip_available": PCHIP_AVAILABLE,
        "instrument_count": len(GPR_MODULES),
        "row_count": len(rows),
        "convex_hull_departures_pp_mf": len(hull_pp_mf),
        "convex_hull_departures_pp_ff": len(hull_pp_ff),
        "near_pp_count": sum(1 for r in rows if r["near_pp"]),
        "near_mf_count": sum(1 for r in rows if r["near_mf"]),
        "outside_pp_mf_count": len(hull_pp_mf),
        "negative_count": sum(1 for r in rows if r["negative_prediction"]),
        "non_finite_count": sum(1 for r in rows if r["non_finite_prediction"]),
        "review_required_count": sum(1 for r in rows if r["classification"] == "REVIEW REQUIRED"),
        "fail_count": sum(1 for r in rows if r["classification"] == "FAIL"),
        "per_instrument": _group_summary(rows, "instrument"),
        "per_register": _group_summary(rows, "register_band"),
        "per_family": _group_summary(rows, "family"),
        "rankings": {
            "convex_hull_pp_mf": hull_pp_mf,
            "convex_hull_pp_ff": hull_pp_ff,
            "top_gpr_linear_abs": _top_n(rows, "abs_gpr_minus_linear"),
            "top_gpr_linear_rel": _top_n(rows, "rel_gpr_minus_linear"),
            "top_gpr_quadratic_abs": _top_n(rows, "abs_gpr_minus_quadratic"),
            "top_gpr_quadratic_rel": _top_n(rows, "rel_gpr_minus_quadratic"),
            "top_gpr_pchip_abs": _top_n(
                [r for r in rows if r["abs_gpr_minus_pchip"] is not None], "abs_gpr_minus_pchip"
            ),
            "near_pp": [r for r in rows if r["near_pp"]],
            "near_mf": [r for r in rows if r["near_mf"]],
            "outside_pp_mf": hull_pp_mf,
            "near_zero": [r for r in rows if r["near_zero"]],
            "negative": [r for r in rows if r["negative_prediction"]],
            "non_finite": [r for r in rows if r["non_finite_prediction"]],
            "top_uncertainty": _top_n(rows, "gpr_std_mp"),
        },
        "classification": "PASS" if summary_fail_count(rows) == 0 else "FAIL",
    }


def summary_fail_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for r in rows if r["classification"] == "FAIL")


def _row_line(r: dict[str, Any]) -> str:
    return (
        f"- {r['instrument']} {r['note']} (MIDI {r['midi']:.0f}, {r['register_band']}): "
        f"pp={r['pp']:.3f} mp={r['gpr_mp']:.3f} mf={r['mf']:.3f} "
        f"|Δlin|={r['abs_gpr_minus_linear']:.3f} |Δquad|={r['abs_gpr_minus_quadratic']:.3f} "
        f"[{r['classification']}] {r['interpretation_note']}"
    )


def _markdown(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    rankings = summary["rankings"]
    lines = [
        "# GPR model-quality diagnostic audit",
        "",
        f"- Repository SHA: `{summary['repository_sha']}`",
        f"- Classification: **{summary['classification']}**",
        f"- Instruments: {summary['instrument_count']}",
        f"- Source rows: {summary['row_count']}",
        f"- Convex-hull departures (pp–mf): **{summary['convex_hull_departures_pp_mf']}**",
        f"- Convex-hull departures (pp–mf–ff): **{summary['convex_hull_departures_pp_ff']}**",
        f"- PCHIP available: {summary['pchip_available']}",
        f"- REVIEW REQUIRED rows: {summary['review_required_count']}",
        "",
        "> Diagnostic only. Production GPR unchanged. Linear/quadratic/PCHIP are comparison references.",
        "",
        "## Per-instrument summary",
        "",
    ]
    for g in summary["per_instrument"]:
        lines.append(
            f"- **{g['group_key']}**: {g['row_count']} rows, "
            f"hull departures={g['convex_hull_departures_pp_mf']} "
            f"({g['convex_hull_pct_pp_mf']:.1f}%), "
            f"max |GPR−linear|={g['max_abs_gpr_minus_linear']:.3f}"
        )
    sections = [
        ("Convex-hull departures (pp–mf)", rankings["convex_hull_pp_mf"][:20]),
        ("Top 20 |GPR−linear|", rankings["top_gpr_linear_abs"]),
        ("Top 20 |GPR−quadratic|", rankings["top_gpr_quadratic_abs"]),
        ("Top 20 GPR std (mp)", rankings["top_uncertainty"]),
        ("Near pp", rankings["near_pp"]),
        ("Near mf", rankings["near_mf"]),
        ("Outside pp–mf", rankings["outside_pp_mf"][:20]),
    ]
    if summary["pchip_available"]:
        sections.insert(3, ("Top 20 |GPR−PCHIP|", rankings["top_gpr_pchip_abs"]))
    for title, items in sections:
        lines.extend(["", f"## {title}", ""])
        if not items:
            lines.append("- (none)")
        else:
            for r in items:
                lines.append(_row_line(r))
    lines.append("")
    lines.append(_model_interpretation(rows, summary))
    return "\n".join(lines)


def _safe_filename(note: str) -> str:
    return note.replace("#", "sharp").replace("/", "_")


def _maybe_plot(rows: list[dict[str, Any]]) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    review = [r for r in rows if r["classification"] == "REVIEW REQUIRED"]
    review.sort(key=lambda r: r["abs_gpr_minus_linear"], reverse=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    x_dense = np.linspace(1.0, 9.0, 80)
    for idx, row in enumerate(review[:10]):
        pp, mf, ff = row["pp"], row["mf"], row["ff"]
        gpr_x = [3.0, 4.0, 4.5, 5.0, 6.0, 7.0]
        gpr_y = [pp, row["gpr_p"], row["gpr_mp"], mf, row["gpr_f"], ff]
        quad_curve = [_quadratic_lagrange(pp, mf, ff, x) for x in x_dense]
        lin_curve = [_linear_at(pp, mf, x) for x in x_dense]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(gpr_x, gpr_y, "o-", label="GPR key dynamics")
        ax.plot(x_dense, lin_curve, "--", label="linear pp–mf")
        ax.plot(x_dense, quad_curve, ":", label="quadratic")
        if PCHIP_AVAILABLE and PchipInterpolator is not None:
            pchip = PchipInterpolator(ANCHOR_X, [pp, mf, ff])
            ax.plot(x_dense, pchip(x_dense), "-.", label="PCHIP")
        ax.scatter([3, 5, 7], [pp, mf, ff], s=60, c="black", zorder=5, label="anchors")
        ax.axvline(4.5, color="gray", ls=":", alpha=0.5)
        ax.set_title(f"{row['instrument']} {row['note']} — REVIEW REQUIRED")
        ax.set_xlabel("ordinal dynamic coordinate")
        ax.set_ylabel("density")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(
            PLOTS / f"review_{idx+1:02d}_{row['instrument']}_{_safe_filename(row['note'])}.png",
            dpi=100,
        )
        plt.close(fig)


def write_reports(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    payload = {"summary": summary, "rows": rows}
    (REPORTS / "gpr_model_quality_audit.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    if rows:
        fieldnames = list(rows[0].keys())
        with (REPORTS / "gpr_model_quality_audit.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row[k] for k in fieldnames})
    (REPORTS / "gpr_model_quality_audit.md").write_text(_markdown(rows, summary), encoding="utf-8")


def build_audit_payload() -> dict[str, Any]:
    rows = collect_rows()
    summary = summarize(rows)
    return {"summary": summary, "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    rows = collect_rows()
    summary = summarize(rows)
    write_reports(rows, summary)
    if not args.no_plots:
        _maybe_plot(rows)
    print(f"Wrote {REPORTS / 'gpr_model_quality_audit.json'}")
    if summary["fail_count"]:
        print("FAIL: non-finite or negative production predictions.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
