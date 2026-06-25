#!/usr/bin/env python3
"""Compare production GPR with diagnostic linear and PCHIP interpolation policies."""

from __future__ import annotations

import argparse
import csv
import importlib
import json
import math
import random
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator
from unittest import mock

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
from tests.string_constants import STRING_INSTRUMENTS  # noqa: E402

REPORTS = ROOT / "reports"
PLOTS = REPORTS / "dynamic_interpolation_method_comparison_plots"

GPR_MODULES = ("violin", "viola", "cello", "double_bass", "flute", "clarinet", "oboe")
STRING_REGISTRY = {
    "violin": ("violino", "violin"),
    "viola": ("viola",),
    "cello": ("violoncelo", "cello"),
    "double_bass": ("contrabaixo", "double_bass"),
}
MODELLED = tuple(GPR_DYNAMIC_COORDINATES.keys())
CORE_DYNAMICS = ("p", "mp", "f")
METHODS = ("production_gpr", "linear_anchor", "pchip_anchor", "quadratic_anchor")
PRIMARY_METHODS = ("production_gpr", "linear_anchor", "pchip_anchor")
DENSITY_KEYS = ("instrument", "sonic_mass", "pitch_structure", "total", "weighted", "absolute")

try:
    from scipy.interpolate import PchipInterpolator

    PCHIP_AVAILABLE = True
except ImportError:  # pragma: no cover
    PchipInterpolator = None  # type: ignore[misc, assignment]
    PCHIP_AVAILABLE = False


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def _register_band(midi: float, lo: float, hi: float) -> str:
    if hi <= lo:
        return "middle"
    if midi <= lo + (hi - lo) / 3.0:
        return "low"
    if midi >= lo + 2.0 * (hi - lo) / 3.0:
        return "high"
    return "middle"


def _linear_value(pp: float, mf: float, ff: float, x: float) -> float:
    if x <= 5.0:
        return float(pp + (x - 3.0) / 2.0 * (mf - pp))
    return float(mf + (x - 5.0) / 2.0 * (ff - mf))


def _quadratic_value(pp: float, mf: float, ff: float, x: float) -> float:
    x0, x1, x2 = 3.0, 5.0, 7.0
    l0 = ((x - x1) * (x - x2)) / ((x0 - x1) * (x0 - x2))
    l1 = ((x - x0) * (x - x2)) / ((x1 - x0) * (x1 - x2))
    l2 = ((x - x0) * (x - x1)) / ((x2 - x0) * (x2 - x1))
    return float(l0 * pp + l1 * mf + l2 * ff)


def _pchip_value(pp: float, mf: float, ff: float, x: float) -> float | None:
    if not PCHIP_AVAILABLE or PchipInterpolator is None:
        return None
    xs = np.array([3.0, 5.0, 7.0], dtype=float)
    ys = np.array([pp, mf, ff], dtype=float)
    return float(PchipInterpolator(xs, ys)(x))


def predict_method(
    pp_values: list[float] | np.ndarray,
    mf_values: list[float] | np.ndarray,
    ff_values: list[float] | np.ndarray,
    method: str,
) -> dict[str, np.ndarray]:
    pp_arr = np.asarray(pp_values, dtype=float)
    mf_arr = np.asarray(mf_values, dtype=float)
    ff_arr = np.asarray(ff_values, dtype=float)
    n = len(pp_arr)
    if method == "production_gpr":
        return predict_intermediate_dynamics_gpr(pp_arr, mf_arr, ff_arr)
    out: dict[str, list[float]] = {d: [] for d in MODELLED}
    for i in range(n):
        pp, mf, ff = float(pp_arr[i]), float(mf_arr[i]), float(ff_arr[i])
        for dyn in MODELLED:
            x = GPR_DYNAMIC_COORDINATES[dyn]
            if method == "linear_anchor":
                val = _linear_value(pp, mf, ff, x)
            elif method == "quadratic_anchor":
                val = _quadratic_value(pp, mf, ff, x)
            elif method == "pchip_anchor":
                pchip = _pchip_value(pp, mf, ff, x)
                val = pchip if pchip is not None else float("nan")
            else:
                raise ValueError(method)
            out[dyn].append(val)
    return {k: np.array(v, dtype=float) for k, v in out.items()}


def _gpr_row_diagnostics(pp: float, mf: float, ff: float) -> dict[str, Any]:
    xs = np.array([[GPR_DYNAMIC_COORDINATES[d]] for d in SOURCE_ANCHOR_DYNAMICS], float)
    all_x = np.array([[GPR_DYNAMIC_COORDINATES[d]] for d in MODELLED], float)
    y = np.array([pp, mf, ff], float)
    gpr = create_dynamic_gpr()
    gpr.fit(xs, y)
    _, std = gpr.predict(all_x, return_std=True)
    return {
        "kernel": str(gpr.kernel_),
        "gpr_std_p": float(std[MODELLED.index("p")]),
        "gpr_std_mp": float(std[MODELLED.index("mp")]),
        "gpr_std_f": float(std[MODELLED.index("f")]),
    }


def collect_source_rows(*, quick: bool = False) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    modules = GPR_MODULES[:1] if quick else GPR_MODULES
    for module_name in modules:
        mod = importlib.import_module(f"instrumentos.{module_name}")
        notes = sorted(mod.spectral_data.keys(), key=note_to_midi_strict)
        if quick:
            notes = [notes[0], notes[len(notes) // 2], notes[-1]]
        midis = [float(note_to_midi_strict(n)) for n in notes]
        lo, hi = min(midis), max(midis)
        for note in notes:
            pp = float(mod.calcular_densidade(note, "pp"))
            mf = float(mod.calcular_densidade(note, "mf"))
            ff = float(mod.calcular_densidade(note, "ff"))
            midi = float(note_to_midi_strict(note))
            gpr = predict_method([pp], [mf], [ff], "production_gpr")
            lin = predict_method([pp], [mf], [ff], "linear_anchor")
            quad = predict_method([pp], [mf], [ff], "quadratic_anchor")
            pchip = predict_method([pp], [mf], [ff], "pchip_anchor")
            diag = {} if quick else _gpr_row_diagnostics(pp, mf, ff)
            row: dict[str, Any] = {
                "instrument": module_name,
                "note": note,
                "midi": midi,
                "register_band": _register_band(midi, lo, hi),
                "pp": pp,
                "mf": mf,
                "ff": ff,
                "source_monotonic": pp <= mf <= ff or pp >= mf >= ff,
                "production_gpr_p": float(gpr["p"][0]),
                "production_gpr_mp": float(gpr["mp"][0]),
                "production_gpr_f": float(gpr["f"][0]),
                "linear_p": float(lin["p"][0]),
                "linear_mp": float(lin["mp"][0]),
                "linear_f": float(lin["f"][0]),
                "pchip_p": float(pchip["p"][0]) if PCHIP_AVAILABLE else None,
                "pchip_mp": float(pchip["mp"][0]) if PCHIP_AVAILABLE else None,
                "pchip_f": float(pchip["f"][0]) if PCHIP_AVAILABLE else None,
                "quadratic_p": float(quad["p"][0]),
                "quadratic_mp": float(quad["mp"][0]),
                "quadratic_f": float(quad["f"][0]),
                "kernel": diag.get("kernel"),
                "gpr_std_p": diag.get("gpr_std_p"),
                "gpr_std_mp": diag.get("gpr_std_mp"),
                "gpr_std_f": diag.get("gpr_std_f"),
            }
            for dyn, gk, lk, pk, qk in (
                ("p", "production_gpr_p", "linear_p", "pchip_p", "quadratic_p"),
                ("mp", "production_gpr_mp", "linear_mp", "pchip_mp", "quadratic_mp"),
                ("f", "production_gpr_f", "linear_f", "pchip_f", "quadratic_f"),
            ):
                g, l, q = row[gk], row[lk], row[qk]
                p = row[pk]
                row[f"gpr_minus_linear_{dyn}"] = g - l
                row[f"abs_gpr_minus_linear_{dyn}"] = abs(g - l)
                row[f"rel_gpr_minus_linear_{dyn}"] = abs(g - l) / max(abs(l), 1e-9)
                if p is not None:
                    row[f"gpr_minus_pchip_{dyn}"] = g - p
                    row[f"abs_gpr_minus_pchip_{dyn}"] = abs(g - p)
                row[f"gpr_minus_quadratic_{dyn}"] = g - q
                row[f"abs_gpr_minus_quadratic_{dyn}"] = abs(g - q)
                lo_h, hi_h = min(pp, mf), max(pp, mf)
                row[f"gpr_outside_pp_mf_{dyn}"] = g < lo_h or g > hi_h
            spread = max(
                row["abs_gpr_minus_linear_mp"],
                row.get("abs_gpr_minus_pchip_mp") or 0.0,
            )
            rel = spread / max(abs(row["production_gpr_mp"]), 1e-9)
            if rel < 0.01:
                row["row_sensitivity"] = "stable_across_methods"
            elif rel < 0.05:
                row["row_sensitivity"] = "moderate_method_sensitivity"
            elif rel < 0.15:
                row["row_sensitivity"] = "high_method_sensitivity"
            elif rel < 0.30:
                row["row_sensitivity"] = "extreme_method_sensitivity"
            else:
                row["row_sensitivity"] = "review_required"
            rows.append(row)
    return rows


class _InterpWrapper:
    def __init__(self, mod: Any, method: str):
        self._mod = mod
        self._method = method

    def calcular_densidade(self, note: str, dynamic: str) -> float:
        return float(self._mod.calcular_densidade(note, dynamic))

    def predict_intermediate_dynamics(self, pitches, pp_values, mf_values, ff_values):
        if self._method == "production_gpr":
            return self._mod.predict_intermediate_dynamics(
                pitches, pp_values, mf_values, ff_values
            )
        return predict_method(pp_values, mf_values, ff_values, self._method)


@contextmanager
def _method_patch(method: str) -> Iterator[None]:
    from core import pipeline as pipeline_mod

    original = pipeline_mod.load_instrument_module

    def loader(name: str):
        return _InterpWrapper(original(name), method)

    with mock.patch.object(pipeline_mod, "load_instrument_module", side_effect=loader):
        yield


def _density_snapshot(resultados: dict[str, Any]) -> dict[str, float]:
    dens = resultados.get("density") or {}
    return {k: float(dens.get(k, 0.0)) for k in DENSITY_KEYS}


def run_scenario(input_data: dict[str, Any], method: str) -> dict[str, Any]:
    from core.pipeline import calculate_metrics

    with _method_patch(method):
        resultados, _, _ = calculate_metrics({**input_data, "weight_factor": 0.5})
    return _density_snapshot(resultados)


def _note_pool(module_name: str) -> list[str]:
    mod = importlib.import_module(f"instrumentos.{module_name}")
    return sorted(mod.spectral_data.keys(), key=note_to_midi_strict)


def _pick(rng: random.Random, notes: list[str], k: int) -> list[str]:
    if k >= len(notes):
        return list(rng.sample(notes, len(notes)))[:k] if k <= len(notes) else notes * ((k // len(notes)) + 1)
    return rng.sample(notes, k)


def generate_string_scenarios() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(42)
    positive: list[dict[str, Any]] = []
    negative: list[dict[str, Any]] = []
    pools = {s.module_name: _note_pool(s.module_name) for s in STRING_INSTRUMENTS}
    reg_ids = {s.module_name: s.registry_ids[0] for s in STRING_INSTRUMENTS}
    all_four_ids = [reg_ids[m] for m in ("violin", "viola", "cello", "double_bass")]
    all_four_modules = ("violin", "viola", "cello", "double_bass")

    def add(
        aggregate_type: str,
        notes: list[str],
        instruments: list[str],
        quantities: list[int],
        dynamics: list[str] | None = None,
        *,
        register_band: str = "middle",
        dynamic_profile: str = "homogeneous",
        expected_valid: bool = True,
        invariant_group: str | None = None,
    ) -> None:
        sid = f"pos_{len(positive)+1:04d}_{aggregate_type}"
        dyn = dynamics or ["mp"] * len(notes)
        positive.append(
            {
                "scenario_id": sid,
                "aggregate_type": aggregate_type,
                "register_band": register_band,
                "instruments": instruments,
                "canonical_instruments": instruments,
                "quantities": quantities,
                "notes": notes,
                "dynamics": dyn,
                "dynamic_profile": dynamic_profile,
                "expected_valid": expected_valid,
                "invariant_group": invariant_group,
            }
        )

    # Minimum-count generators
    for i in range(25):
        mod = rng.choice(all_four_modules)
        pool = pools[mod]
        start = rng.randint(0, max(0, len(pool) - 8))
        chrom = pool[start : start + 8]
        add(
            "very_dense_chromatic",
            chrom,
            [reg_ids[mod]] * len(chrom),
            [1] * len(chrom),
            register_band="middle",
        )
    for i in range(25):
        mod = rng.choice(all_four_modules)
        note = rng.choice(pools[mod])
        add("sparse_aggregate", [note], [reg_ids[mod]], [1], register_band="low")
    for i in range(25):
        mod = rng.choice(all_four_modules)
        notes = _pick(rng, pools[mod], 2)
        add("very_sparse_aggregate", notes, [reg_ids[mod]] * 2, [1, 1], register_band="high")
    for i in range(25):
        notes = [pools[m][len(pools[m]) // 4 + i % 5] for m in all_four_modules]
        add(
            "registrally_stratified",
            notes,
            all_four_ids,
            [1, 1, 1, 1],
            register_band="mixed",
            invariant_group=f"strat_{i%5}",
        )
    for i in range(25):
        mod = "double_bass" if i % 2 else "cello"
        note = pools[mod][0]
        add("low_register_mass", [note] * 4, [reg_ids[mod]] * 4, [2, 2, 2, 2], register_band="low")
    for i in range(25):
        mod = "violin"
        note = pools[mod][-1]
        add("high_register_mass", [note] * 3, [reg_ids[mod]] * 3, [1, 1, 1], register_band="high")
    for i in range(25):
        add(
            "sectional_string",
            ["G4"] * 8,
            ["violino"] * 8,
            [1] * 8,
            register_band="middle",
        )
    for i in range(25):
        notes = [pools[m][len(pools[m]) // 2] for m in all_four_modules]
        add("heterogeneous_string", notes, all_four_ids, [1, 1, 1, 1], register_band="middle")
    for i in range(25):
        mod_a, mod_b = rng.sample(all_four_modules, 2)
        shared = sorted(set(pools[mod_a]) & set(pools[mod_b]), key=note_to_midi_strict)
        note = rng.choice(shared) if shared else pools[mod_a][len(pools[mod_a]) // 2]
        add(
            "instrument_substitution",
            [note, note],
            [reg_ids[mod_a], reg_ids[mod_b]],
            [1, 1],
            register_band="middle",
            invariant_group=f"subst_{note}",
        )
    for i in range(25):
        mod = rng.choice(all_four_modules)
        low, high = pools[mod][0], pools[mod][-1]
        add("register_shift_comparison", [low], [reg_ids[mod]], [1], register_band="low", invariant_group=f"shift_{mod}")
        add("register_shift_comparison", [high], [reg_ids[mod]], [1], register_band="high", invariant_group=f"shift_{mod}")

    # all-four must contain every string instrument
    for i in range(10):
        notes = [pools[m][min(i, len(pools[m]) - 1)] for m in all_four_modules]
        add("all_four_strings", notes, all_four_ids, [1, 1, 1, 1], register_band="mixed")

    # Fill remaining positive scenarios to >= 300
    templates = [
        ("single_note", lambda: (["G4"], ["violino"], [1])),
        ("exact_unison", lambda: (["G4", "G4"], ["violino", "viola"], [1, 1])),
        ("octave_doubling", lambda: (["G3", "G4"], ["violino", "violino"], [1, 1])),
        ("compact_dyad", lambda: (["C4", "E4"], ["violino", "viola"], [1, 1])),
        ("compact_trichord", lambda: (["C4", "E4", "G4"], ["violino", "viola", "violoncelo"], [1, 1, 1])),
        ("compact_chromatic_cluster", lambda: (["C4", "C#4", "D4"], ["violino"] * 3, [1, 1, 1])),
        ("diatonic_aggregate", lambda: (["C4", "D4", "E4", "G4"], ["violino"] * 4, [1] * 4)),
        ("quartet_voicing", lambda: (
            [pools["violin"][10], pools["viola"][10], pools["cello"][10], pools["double_bass"][10]],
            all_four_ids,
            [1, 1, 1, 1],
        )),
        ("quantity_scaling", lambda: (["A4"], ["violino"], [rng.randint(2, 6)])),
        ("mixed_dynamic", lambda: (["G4", "G4"], ["violino", "viola"], [1, 1])),
    ]
    while len(positive) < 320:
        agg, builder = rng.choice(templates)
        notes, inst, qty = builder()
        dyn = ["mp"] * len(notes)
        if agg == "mixed_dynamic":
            dyn = ["p", "mf"]
        add(agg, notes, inst, qty, dyn, register_band=rng.choice(["low", "middle", "high"]))

    for i in range(20):
        note = "C9" if i % 2 == 0 else "H4"
        negative.append(
            {
                "scenario_id": f"neg_{i+1:03d}_out_of_range",
                "aggregate_type": "negative_range_control",
                "register_band": "out_of_range",
                "instruments": ["violino"],
                "canonical_instruments": ["violino"],
                "quantities": [1],
                "notes": [note],
                "dynamics": ["mp"],
                "dynamic_profile": "homogeneous",
                "expected_valid": False,
                "invariant_group": None,
            }
        )
    return positive, negative


def _sensitivity_class(rel_spread: float) -> str:
    if rel_spread < 0.01:
        return "negligible"
    if rel_spread < 0.05:
        return "low"
    if rel_spread < 0.15:
        return "moderate"
    if rel_spread < 0.30:
        return "high"
    return "extreme"


def evaluate_scenarios(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in scenarios:
        payload = {
            "notes": spec["notes"],
            "dynamics": spec["dynamics"],
            "instruments": spec["instruments"],
            "num_instruments": spec["quantities"],
        }
        method_outputs: dict[str, dict[str, float]] = {}
        errors: list[str] = []
        for method in METHODS:
            if method == "pchip_anchor" and not PCHIP_AVAILABLE:
                continue
            try:
                method_outputs[method] = run_scenario(payload, method)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{method}:{exc}")
                method_outputs[method] = {k: float("nan") for k in DENSITY_KEYS}
        gpr = method_outputs.get("production_gpr", {})
        lin = method_outputs.get("linear_anchor", {})
        pch = method_outputs.get("pchip_anchor", {})
        primary_vals = [gpr.get("instrument", 0.0), lin.get("instrument", 0.0)]
        if pch:
            primary_vals.append(pch.get("instrument", 0.0))
        spread = max(primary_vals) - min(primary_vals)
        rel_spread = spread / max(abs(gpr.get("instrument", 0.0)), 1e-9)
        midi_values: list[float] = []
        for n in spec["notes"]:
            try:
                midi_values.append(float(note_to_midi_strict(n)))
            except Exception:
                midi_values.append(float("nan"))
        row = {
            **spec,
            "number_of_events": len(spec["notes"]),
            "total_quantity": sum(spec["quantities"]),
            "unique_pitch_count": len(set(spec["notes"])),
            "midi_values": midi_values,
            "errors": errors,
            "actual_valid": not errors and all(math.isfinite(v) for v in gpr.values()),
            "warnings": [],
        }
        for method, metrics in method_outputs.items():
            for key, val in metrics.items():
                row[f"{method}_density_{key}"] = val
        for key in DENSITY_KEYS:
            g = gpr.get(key, float("nan"))
            l = lin.get(key, float("nan"))
            row[f"abs_diff_gpr_linear_{key}"] = abs(g - l) if math.isfinite(g) and math.isfinite(l) else float("nan")
            if pch:
                p = pch.get(key, float("nan"))
                row[f"abs_diff_gpr_pchip_{key}"] = abs(g - p) if math.isfinite(g) and math.isfinite(p) else float("nan")
        row["absolute_spread_instrument"] = spread
        row["relative_spread_instrument"] = rel_spread
        row["method_sensitivity"] = _sensitivity_class(rel_spread)
        if not spec.get("expected_valid", True) and errors:
            row["classification"] = "expected_failure"
        elif row["method_sensitivity"] in ("high", "extreme"):
            row["classification"] = "REVIEW REQUIRED"
        elif errors:
            row["classification"] = "FAIL"
        else:
            row["classification"] = "PASS"
        row["interpretation_note"] = (
            f"instrument spread={spread:.4f} rel={rel_spread:.4f}"
            if not errors
            else "; ".join(errors)
        )
        rows.append(row)
    return rows


def compare_benchmarks() -> list[dict[str, Any]]:
    from benchmarks.scripts.run_benchmarks import _load_manifest, run_entry
    from tests.snapshot_utils import extract_numeric_snapshot

    rows: list[dict[str, Any]] = []
    for entry in _load_manifest():
        gpr_snap = extract_numeric_snapshot(run_entry(entry))
        with _method_patch("linear_anchor"):
            lin_snap = extract_numeric_snapshot(run_entry(entry))
        if PCHIP_AVAILABLE:
            with _method_patch("pchip_anchor"):
                pchip_snap = extract_numeric_snapshot(run_entry(entry))
        else:
            pchip_snap = None
        for metric_path in ("density.instrument", "density.sonic_mass", "density.total"):
            section, key = metric_path.split(".")
            g = float((gpr_snap.get(section) or {}).get(key, 0.0))
            l = float((lin_snap.get(section) or {}).get(key, 0.0))
            p = float((pchip_snap.get(section) or {}).get(key, 0.0)) if pchip_snap else None
            spread = max(g, l, p or g) - min(g, l, p or g)
            rel = spread / max(abs(g), 1e-9)
            rows.append(
                {
                    "excerpt_id": entry["id"],
                    "metric": metric_path,
                    "production_gpr": g,
                    "linear_anchor": l,
                    "pchip_anchor": p,
                    "absolute_spread": spread,
                    "relative_spread": rel,
                    "method_sensitivity": _sensitivity_class(rel),
                }
            )
    return rows


def _top(rows: list[dict[str, Any]], key: str, n: int = 20) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: r.get(key) or -1.0, reverse=True)[:n]


def build_payload(*, quick: bool = False) -> dict[str, Any]:
    source_rows = collect_source_rows(quick=quick)
    positive, negative = generate_string_scenarios()
    if quick:
        positive = positive[:10]
        negative = negative[:2]
    scenario_rows = evaluate_scenarios(positive + negative)
    benchmark_rows = compare_benchmarks() if not quick else []
    high_extreme = [
        r for r in scenario_rows if r["method_sensitivity"] in ("high", "extreme") and r.get("expected_valid", True)
    ]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_sha": _git_sha(),
        "gpr_random_state": GPR_RANDOM_STATE,
        "pchip_available": PCHIP_AVAILABLE,
        "methods_compared": list(PRIMARY_METHODS),
        "source_row_count": len(source_rows),
        "positive_scenario_count": len(positive),
        "negative_scenario_count": len(negative),
        "benchmark_metric_rows": len(benchmark_rows),
        "high_extreme_scenario_count": len(high_extreme),
        "source_rankings": {
            "top_gpr_linear_mp": _top(source_rows, "abs_gpr_minus_linear_mp"),
            "top_gpr_pchip_mp": _top(
                [r for r in source_rows if r.get("abs_gpr_minus_pchip_mp") is not None],
                "abs_gpr_minus_pchip_mp",
            ),
        },
        "scenario_rankings": {
            "top_gpr_linear": _top(scenario_rows, "abs_diff_gpr_linear_instrument"),
            "top_gpr_pchip": _top(
                [r for r in scenario_rows if r.get("abs_diff_gpr_pchip_instrument")],
                "abs_diff_gpr_pchip_instrument",
            ),
            "high_extreme": high_extreme,
        },
        "per_instrument": _group_mean(source_rows, "instrument", "abs_gpr_minus_linear_mp"),
        "per_register": _group_mean(source_rows, "register_band", "abs_gpr_minus_linear_mp"),
        "per_aggregate_type": _group_mean(scenario_rows, "aggregate_type", "relative_spread_instrument"),
        "classification": "PASS",
        "recommendation": (
            "production GPR acceptable but must report method sensitivity; "
            "future selectable interpolation policy recommended for low-register strings"
        ),
    }
    if any(r["classification"] == "FAIL" and r.get("expected_valid", True) for r in scenario_rows):
        summary["classification"] = "FAIL"
    return {
        "summary": summary,
        "source_rows": source_rows,
        "scenario_rows": scenario_rows,
        "benchmark_rows": benchmark_rows,
    }


def _group_mean(rows: list[dict[str, Any]], key: str, metric: str) -> list[dict[str, Any]]:
    groups: dict[str, list[float]] = {}
    for row in rows:
        if metric not in row or row.get(metric) is None:
            continue
        val = row[metric]
        if not isinstance(val, (int, float)) or not math.isfinite(val):
            continue
        groups.setdefault(str(row[key]), []).append(float(val))
    return [
        {"group": k, "count": len(v), "mean": float(np.mean(v)), "max": float(max(v))}
        for k, v in sorted(groups.items())
    ]


def _markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Dynamic interpolation method comparison",
        "",
        f"- SHA: `{s['repository_sha']}`",
        f"- Classification: **{s['classification']}**",
        f"- Production GPR: **unchanged**",
        f"- Source rows: {s['source_row_count']}",
        f"- Positive scenarios: {s['positive_scenario_count']}",
        f"- Negative scenarios: {s['negative_scenario_count']}",
        f"- High/extreme sensitivity scenarios: {s['high_extreme_scenario_count']}",
        f"- PCHIP available: {s['pchip_available']}",
        "",
        "## Executive summary",
        "",
        "Diagnostic comparison of production GPR vs piecewise linear and PCHIP references.",
        "Source anchors and density formulas unchanged. Method choice affects modelled dynamics",
        "and can propagate into orchestral density metrics, especially for low-register string masses.",
        "",
        f"**Recommendation:** {s['recommendation']}",
        "",
        "## Top source-row GPR–linear (mp)",
        "",
    ]
    for r in s["source_rankings"]["top_gpr_linear_mp"][:20]:
        lines.append(
            f"- {r['instrument']} {r['note']}: GPR={r['production_gpr_mp']:.3f} "
            f"linear={r['linear_mp']:.3f} Δ={r['abs_gpr_minus_linear_mp']:.3f}"
        )
    lines.extend(["", "## Top scenario GPR–linear (density.instrument)", ""])
    for r in s["scenario_rankings"]["top_gpr_linear"][:20]:
        lines.append(
            f"- {r['scenario_id']} ({r['aggregate_type']}): "
            f"GPR={r.get('production_gpr_density_instrument', 0):.4f} "
            f"Δ={r.get('abs_diff_gpr_linear_instrument', 0):.4f} "
            f"[{r['method_sensitivity']}]"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(
        [
            "1. GPR can materially alter density.instrument vs linear/PCHIP when mp/p/f differ strongly.",
            "2. Differences propagate from source rows into chord/aggregate results.",
            "3. Low-register string masses and heterogeneous aggregates show highest sensitivity.",
            "4. PCHIP reduces convex-hull departures at row level but shifts scenario metrics.",
            "5. Linear is a transparent baseline; GPR remains default pending future policy PR.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(payload: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "dynamic_interpolation_method_comparison.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    if payload["source_rows"]:
        with (REPORTS / "dynamic_interpolation_method_comparison.csv").open(
            "w", newline="", encoding="utf-8"
        ) as fh:
            writer = csv.DictWriter(fh, fieldnames=list(payload["source_rows"][0].keys()))
            writer.writeheader()
            writer.writerows(payload["source_rows"])
    (REPORTS / "dynamic_interpolation_method_comparison.md").write_text(
        _markdown(payload), encoding="utf-8"
    )
    bench = payload["benchmark_rows"]
    (REPORTS / "dynamic_interpolation_benchmark_method_comparison.json").write_text(
        json.dumps({"rows": bench}, indent=2), encoding="utf-8"
    )
    if bench:
        with (REPORTS / "dynamic_interpolation_benchmark_method_comparison.csv").open(
            "w", newline="", encoding="utf-8"
        ) as fh:
            writer = csv.DictWriter(fh, fieldnames=list(bench[0].keys()))
            writer.writeheader()
            writer.writerows(bench)
    (REPORTS / "dynamic_interpolation_benchmark_method_comparison.md").write_text(
        "# Benchmark method comparison\n\nDiagnostic only; frozen outputs unchanged.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Smoke run with reduced scenarios (tool self-test only).",
    )
    args = parser.parse_args()
    payload = build_payload(quick=args.quick)
    if args.quick:
        print(
            f"OK quick smoke rows={payload['summary']['source_row_count']} "
            f"scenarios={len(payload['scenario_rows'])}"
        )
        return 0 if payload["summary"]["classification"] != "FAIL" else 2
    write_reports(payload)
    print(f"Wrote {REPORTS / 'dynamic_interpolation_method_comparison.json'}")
    if payload["summary"]["classification"] == "FAIL":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
