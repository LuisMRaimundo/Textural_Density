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
| `STRESS_TEST_REPORT.md` | Self-contained methods-style report |
| `stress_results.csv` | Wide-format metrics for every slice |
| `stress_figures/` | A2 / B3 / C3 / C5 plots |

Generated artifacts are gitignored; regenerate with the command above.
