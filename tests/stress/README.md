# Density stress battery

Exercises `core.calculate_metrics` / `AnalysisRequest` across pitched-only,
percussion-only, mixed, degenerate, and property families. **No production code
is modified.**

## Run

From the repository root:

```bash
python run_stress_battery.py
```

Optional flags:

```bash
python run_stress_battery.py --e1-trials 200 --e1-slices 20 --seed 20260803
python run_stress_battery.py --skip-determinism   # skip E5 second pass
```

## Outputs

| Artifact | Role |
|----------|------|
| `STRESS_TEST_REPORT.md` | Working report at repo root (gitignored) |
| `reports/STRESS_TEST_REPORT_v1.md` | Tracked pre-fix archive (D6 caveat era) |
| `reports/STRESS_TEST_REPORT_v2.md` | Tracked post-hotfix archive (copied on each root run) |
| `stress_results.csv` | Wide-format metrics for every slice (gitignored) |
| `stress_figures/` | A2 / B3 / C3 / C5 plots (gitignored) |

Root working copies are gitignored; versioned `reports/STRESS_TEST_REPORT_v*.md` are tracked.
