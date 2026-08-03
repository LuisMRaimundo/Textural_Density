#!/usr/bin/env python3
"""
Density-pipeline stress battery — public API only.

Usage:
  python run_stress_battery.py
  python run_stress_battery.py --e1-trials 50 --seed 42 --skip-determinism

Writes (cwd = repo root recommended):
  STRESS_TEST_REPORT.md
  stress_results.csv
  stress_figures/*.png
"""

from __future__ import annotations

import argparse
import csv
import sys
import tempfile
import time
from pathlib import Path

# Ensure repo root is on sys.path when launched as a script
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import MAX_DENS_GLOBAL  # noqa: E402
from tests.stress.engine import (  # noqa: E402
    csv_sha256,
    evaluate_assertions,
    prepare_and_validate_registry,
    run_slice,
)
from tests.stress.figures import write_figures  # noqa: E402
from tests.stress.report import summarize_e4, write_report  # noqa: E402
from tests.stress.scenarios import WEIGHT  # noqa: E402


def _write_csv(path: Path, results) -> None:
    rows = []
    for r in results:
        row = dict(r.flat)
        row.setdefault("slice_id", r.spec["id"])
        row.setdefault("family", r.spec["family"])
        row.setdefault("summary", r.spec["summary"])
        row["run_ok"] = r.ok
        row["run_error"] = r.error or ""
        rows.append(row)
    # Union of all keys for wide format
    fieldnames: list[str] = []
    seen = set()
    priority = [
        "slice_id",
        "family",
        "summary",
        "run_ok",
        "run_error",
        "weight_factor",
        "density.interval",
        "density.instrument",
        "density.weighted",
        "density.sonic_mass",
        "density.total",
        "density.pitch_structure",
        "pitch_aggregation.event_count",
        "pitch_aggregation.player_count",
        "pitch_aggregation.distinct_pitch_count",
        "pitch_aggregation.unpitched_event_count",
    ]
    for k in priority:
        if any(k in row for row in rows) and k not in seen:
            fieldnames.append(k)
            seen.add(k)
    for row in rows:
        for k in sorted(row.keys()):
            if k not in seen:
                fieldnames.append(k)
                seen.add(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Textural Density stress battery")
    p.add_argument("--seed", type=int, default=20260803, help="RNG seed for family E")
    p.add_argument(
        "--e1-trials",
        type=int,
        default=200,
        help="E1 monotonicity trials (default 200)",
    )
    p.add_argument(
        "--e1-slices",
        type=int,
        default=20,
        help="E2/E3 random-slice counts (default 20)",
    )
    p.add_argument(
        "--skip-determinism",
        action="store_true",
        help="Skip E5 second full pass (faster)",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT,
        help="Directory for report/CSV/figures (default: repo root)",
    )
    args = p.parse_args(argv)

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "STRESS_TEST_REPORT.md"
    csv_path = out_dir / "stress_results.csv"
    fig_dir = out_dir / "stress_figures"

    print(
        f"Stress battery | w={WEIGHT} REF={MAX_DENS_GLOBAL:g} "
        f"seed={args.seed} e1_trials={args.e1_trials}"
    )
    t0 = time.perf_counter()

    scenarios = prepare_and_validate_registry()
    print(f"Running {len(scenarios)} scenario slices…")
    results = [run_slice(s) for s in scenarios]
    n_ok = sum(1 for r in results if r.ok)
    print(f"Scenario slices: {n_ok}/{len(results)} ok")

    print("Evaluating assertions (incl. family E property trials)…")
    asserts = evaluate_assertions(
        results,
        e1_trials=args.e1_trials,
        e1_slices=args.e1_slices,
        seed=args.seed,
    )
    asserts_for_report = summarize_e4(asserts)

    print("Writing CSV…")
    _write_csv(csv_path, results)

    determinism_ok = None
    if not args.skip_determinism:
        print("E5 determinism: second pass…")
        results2 = [run_slice(s) for s in scenarios]
        with tempfile.TemporaryDirectory() as tmp:
            csv2 = Path(tmp) / "stress_results.csv"
            _write_csv(csv2, results2)
            h1, h2 = csv_sha256(csv_path), csv_sha256(csv2)
            determinism_ok = h1 == h2
            # Attach E5 assertion
            from tests.stress.engine import AssertionResult

            asserts.append(
                AssertionResult(
                    "E",
                    "E5_determinism_csv_hash",
                    bool(determinism_ok),
                    f"hash1={h1[:12]} hash2={h2[:12]}",
                )
            )
            asserts_for_report = summarize_e4(asserts)

    print("Figures…")
    figure_paths = write_figures(results, fig_dir)
    # Prefer paths relative to report location for markdown
    rel_figs = {k: Path("stress_figures") / v.name for k, v in figure_paths.items()}

    elapsed = time.perf_counter() - t0
    write_report(
        results=results,
        asserts=asserts_for_report,
        figure_paths=rel_figs,
        seed=args.seed,
        e1_trials=args.e1_trials,
        csv_path=csv_path,
        report_path=report_path,
        determinism_ok=determinism_ok,
        elapsed_s=elapsed,
    )

    # Also archive a versioned copy under reports/ when writing to repo root.
    if out_dir.resolve() == ROOT.resolve():
        archive = ROOT / "reports" / "STRESS_TEST_REPORT_v2.md"
        archive.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Archived: {archive}")

    n_pass = sum(1 for a in asserts if a.passed)
    n_fail = sum(1 for a in asserts if not a.passed)
    n_blocker = sum(1 for a in asserts if (not a.passed and a.severity == "blocker"))
    n_caveat_fail = sum(1 for a in asserts if (not a.passed and a.severity == "caveat"))
    print(
        f"Done in {elapsed:.1f}s — assertions {n_pass} pass / {n_fail} fail "
        f"(blockers={n_blocker}, caveat-findings={n_caveat_fail})"
    )
    print(f"Report: {report_path}")
    print(f"CSV:    {csv_path}")
    # Caveat-severity failures are documented findings, not process blockers.
    return 0 if n_blocker == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
