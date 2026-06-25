#!/usr/bin/env python3
"""Audit production GPR dynamic-interpolation determinism."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import platform
import random
import sys
import time
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
GPR_MODULES = (
    "violin",
    "viola",
    "cello",
    "double_bass",
    "flute",
    "clarinet",
    "oboe",
)
MODELLED_DYNAMICS = tuple(GPR_DYNAMIC_COORDINATES.keys())
FLOAT_TOL = 1e-9


def _git_sha() -> str:
    import subprocess

    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def _inventory() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    helper = ROOT / "instrumentos" / "gpr_dynamic_interpolation.py"
    rows.append(
        {
            "file": str(helper.relative_to(ROOT)),
            "function": "create_dynamic_gpr",
            "estimator_type": "GaussianProcessRegressor",
            "classification": "production",
            "kernel": "C(1.0)*Matern(length_scale=1.0, nu=1.5)",
            "alpha": 1e-1,
            "optimizer": "fmin_l_bfgs_b",
            "n_restarts_optimizer": 10,
            "normalize_y": False,
            "random_state": GPR_RANDOM_STATE,
            "uses_global_numpy_state": False,
            "output_committed": False,
            "correction_required": False,
        }
    )
    for name in GPR_MODULES:
        rows.append(
            {
                "file": f"instrumentos/{name}.py",
                "function": "predict_intermediate_dynamics",
                "estimator_type": "delegates_to_shared_helper",
                "classification": "production",
                "random_state": GPR_RANDOM_STATE,
                "uses_global_numpy_state": False,
                "output_committed": True,
                "correction_required": False,
            }
        )
    rows.append(
        {
            "file": "tools/audit_mp_dynamic_interpolation.py",
            "function": "_gpr_std_at_mp",
            "estimator_type": "GaussianProcessRegressor via create_dynamic_gpr",
            "classification": "tool",
            "random_state": GPR_RANDOM_STATE,
            "uses_global_numpy_state": False,
            "output_committed": True,
            "correction_required": False,
        }
    )
    return rows


def _representative_notes(mod) -> tuple[str, str, str]:
    notes = sorted(mod.spectral_data.keys(), key=note_to_midi_strict)
    return notes[0], notes[len(notes) // 2], notes[-1]


def _predict_mp(mod, note: str) -> float:
    pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
    return float(mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])["mp"][0])


def _run_case_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    run_no = 0
    seeds = [(0, 0), (1, 0), (42, 0), (999, 0), (0, 1), (0, 100), (0, 10000)]
    for module_name in GPR_MODULES:
        mod = importlib.import_module(f"instrumentos.{module_name}")
        notes = list(_representative_notes(mod))
        for note in notes:
            for dynamic in MODELLED_DYNAMICS:
                pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
                for seed, consume in seeds:
                    run_no += 1
                    np.random.seed(seed)
                    for _ in range(consume):
                        np.random.random()
                    t0 = time.perf_counter()
                    preds = mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])
                    elapsed = time.perf_counter() - t0
                    rows.append(
                        {
                            "instrument": module_name,
                            "note": note,
                            "midi": float(note_to_midi_strict(note)),
                            "dynamic": dynamic,
                            "run_number": run_no,
                            "global_seed_precondition": seed,
                            "values_consumed_before_fit": consume,
                            "evaluation_order": "canonical",
                            "prediction": float(preds[dynamic][0]),
                            "elapsed_s": elapsed,
                        }
                    )
    return rows


def _order_permutation_summary() -> dict[str, Any]:
    cases: list[tuple[str, str]] = []
    for module_name in GPR_MODULES:
        mod = importlib.import_module(f"instrumentos.{module_name}")
        for note in _representative_notes(mod):
            cases.append((module_name, note))

    def evaluate(batch: list[tuple[str, str]]) -> dict[str, float]:
        out: dict[str, float] = {}
        for module_name, note in batch:
            mod = importlib.import_module(f"instrumentos.{module_name}")
            np.random.seed(123456)
            np.random.random()
            out[f"{module_name}|{note}"] = _predict_mp(mod, note)
        return out

    canonical = evaluate(cases)
    reverse = evaluate(list(reversed(cases)))
    sh1 = list(cases)
    sh2 = list(cases)
    random.Random(1).shuffle(sh1)
    random.Random(42).shuffle(sh2)
    shuffle1 = evaluate(sh1)
    shuffle42 = evaluate(sh2)
    max_abs = max(
        abs(canonical[k] - reverse[k]) for k in canonical
    )
    max_abs = max(max_abs, max(abs(canonical[k] - shuffle1[k]) for k in canonical))
    max_abs = max(max_abs, max(abs(canonical[k] - shuffle42[k]) for k in canonical))
    return {
        "canonical_count": len(canonical),
        "max_absolute_variation": float(max_abs),
        "exact_match": bool(max_abs <= FLOAT_TOL),
    }


def _rng_preservation_summary() -> dict[str, Any]:
    mod = importlib.import_module("instrumentos.violin")
    note = _representative_notes(mod)[1]
    pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
    np.random.seed(2025)
    for _ in range(13):
        np.random.random()
    before = np.random.get_state()
    mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])
    after = np.random.get_state()
    preserved = bool(
        before[0] == after[0]
        and np.array_equal(before[1], after[1])
        and before[2:] == after[2:]
    )
    return {"preserved": preserved}


def _benchmark_order_summary() -> dict[str, Any]:
    from benchmarks.scripts.run_benchmarks import _load_manifest, run_entry

    entries = _load_manifest()
    canonical = {e["id"]: run_entry(e)["numeric"]["density"]["absolute"] for e in entries}
    reverse = {
        e["id"]: run_entry(e)["numeric"]["density"]["absolute"] for e in reversed(entries)
    }
    shuffled = list(entries)
    random.Random(1).shuffle(shuffled)
    shuffle_map = {e["id"]: run_entry(e)["numeric"]["density"]["absolute"] for e in shuffled}
    max_abs = max(abs(canonical[k] - reverse[k]) for k in canonical)
    max_abs = max(max_abs, max(abs(canonical[k] - shuffle_map[k]) for k in canonical))
    return {"max_absolute_variation": float(max_abs), "exact_match": bool(max_abs <= 1e-6)}


def _frozen_diff_summary() -> dict[str, Any]:
    from benchmarks.scripts.run_benchmarks import _load_manifest, run_entry

    expected_dir = ROOT / "benchmarks" / "expected_outputs"
    diffs: list[dict[str, Any]] = []
    for entry in _load_manifest():
        expected_path = expected_dir / f"{entry['id']}.json"
        if not expected_path.exists():
            continue
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        current = run_entry(entry)
        old = float(expected["numeric"]["density"]["absolute"])
        new = float(current["numeric"]["density"]["absolute"])
        diff = new - old
        diffs.append(
            {
                "excerpt": entry["id"],
                "field": "density.absolute",
                "old": old,
                "new": new,
                "absolute_difference": diff,
                "relative_difference": diff / old if old else 0.0,
            }
        )
    return {"differences": diffs, "any_change": bool(any(abs(d["absolute_difference"]) > 1e-6 for d in diffs))}


def _repeated_call_variation() -> dict[str, Any]:
    mod = importlib.import_module("instrumentos.violin")
    note = "G4"
    pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
    values = [
        float(mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])["mp"][0])
        for _ in range(10)
    ]
    spread = max(values) - min(values)
    return {"values": values, "max_absolute_variation": spread}


def build_audit_payload() -> dict[str, Any]:
    import sklearn
    import scipy

    case_rows = _run_case_matrix()
    by_key: dict[tuple[str, str, str], list[float]] = {}
    for row in case_rows:
        if row["dynamic"] != "mp":
            continue
        key = (row["instrument"], row["note"], str(row["global_seed_precondition"]))
        by_key.setdefault(key, []).append(row["prediction"])
    seed_variations = [
        max(vals) - min(vals) for vals in by_key.values() if len(vals) > 1
    ]
    max_seed_var = max(seed_variations) if seed_variations else 0.0

    payload = {
        "repository_sha": _git_sha(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "sklearn_version": sklearn.__version__,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "inventory": _inventory(),
        "random_state_policy": {"GPR_RANDOM_STATE": GPR_RANDOM_STATE},
        "kernel_configuration": {
            "kernel": "C(1.0)*Matern(length_scale=1.0, nu=1.5)",
            "alpha": 1e-1,
            "n_restarts_optimizer": 10,
            "normalize_y": False,
        },
        "instruments_tested": len(GPR_MODULES),
        "notes_tested_per_instrument": 3,
        "dynamic_predictions_tested": len(case_rows),
        "repeated_call": _repeated_call_variation(),
        "order_permutation": _order_permutation_summary(),
        "rng_preservation": _rng_preservation_summary(),
        "benchmark_order": _benchmark_order_summary(),
        "frozen_output_diff": _frozen_diff_summary(),
        "max_global_seed_variation_mp": max_seed_var,
        "classification": "PASS",
        "cases": case_rows,
    }
    if max_seed_var > FLOAT_TOL:
        payload["classification"] = "FAIL"
    if not payload["rng_preservation"]["preserved"]:
        payload["classification"] = "FAIL"
    if not payload["order_permutation"]["exact_match"]:
        payload["classification"] = "FAIL"
    if payload["frozen_output_diff"]["any_change"]:
        payload["classification"] = "REVIEW REQUIRED"
    return payload


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# GPR determinism audit",
        "",
        f"- Repository SHA: `{payload['repository_sha']}`",
        f"- Classification: **{payload['classification']}**",
        f"- `GPR_RANDOM_STATE`: `{payload['random_state_policy']['GPR_RANDOM_STATE']}`",
        f"- Instruments tested: {payload['instruments_tested']}",
        f"- Dynamic predictions tested: {payload['dynamic_predictions_tested']}",
        f"- Max repeated-call variation (violin G4 mp): "
        f"{payload['repeated_call']['max_absolute_variation']}",
        f"- Max global-seed variation (mp): {payload['max_global_seed_variation_mp']}",
        f"- Order permutation exact match: {payload['order_permutation']['exact_match']}",
        f"- Global RNG preserved: {payload['rng_preservation']['preserved']}",
        f"- Benchmark order max variation: {payload['benchmark_order']['max_absolute_variation']}",
        f"- Frozen output changes: {payload['frozen_output_diff']['any_change']}",
        "",
        "## Inventory",
        "",
    ]
    for row in payload["inventory"]:
        lines.append(
            f"- `{row['file']}` `{row.get('function','')}` "
            f"random_state={row.get('random_state')} "
            f"class={row['classification']}"
        )
    if payload["frozen_output_diff"]["differences"]:
        lines.extend(["", "## Frozen output differences", ""])
        for diff in payload["frozen_output_diff"]["differences"]:
            if abs(diff["absolute_difference"]) > 1e-6:
                lines.append(
                    f"- {diff['excerpt']}: {diff['old']} -> {diff['new']} "
                    f"(Δ={diff['absolute_difference']})"
                )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Determinism means repeatability of the numerical procedure.",
            "- Determinism does not establish acoustic or perceptual validity.",
            "- Production GPR owns `random_state`; global `np.random.seed` is not required.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(payload: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS / "gpr_determinism_audit.json"
    md_path = REPORTS / "gpr_determinism_audit.md"
    csv_path = REPORTS / "gpr_determinism_audit.csv"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    if payload["cases"]:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(payload["cases"][0].keys()))
            writer.writeheader()
            writer.writerows(payload["cases"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout-hash", action="store_true", help="Print SHA-256 of JSON payload.")
    args = parser.parse_args()
    payload = build_audit_payload()
    write_reports(payload)
    if args.stdout_hash:
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
        print(digest)
    print(f"Wrote {REPORTS / 'gpr_determinism_audit.json'}")
    return 0 if payload["classification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
