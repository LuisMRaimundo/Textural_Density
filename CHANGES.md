# CHANGES — Textural Density

Numeric and formula history for Textural Density. Cross-links: [TECHNICAL_MANUAL §3.5 / §3.12 / §7.5.1](docs/TECHNICAL_MANUAL.md) · [MATHEMATICAL_MANUAL §H](docs/MATHEMATICAL_MANUAL.md) · [constants_and_assumptions §7](docs/constants_and_assumptions.md).

## 2026-08-03 — Task 8c: unify composite (blend × mass)

**Formula change (intentional).** Composite no longer uses the pitch-gated
product `pitch_structure × √M / 575`, and the unpitched-only fallback to raw
weighted orchestral is **removed** (it made percussion-only scores
incommensurable with mixed scores).

**Single path for all regimes:**

```text
D_blend = density.weighted = 10 · (w · DI/DI_max + (1−w) · DV/DV_max)
Composite = log10(1 + D_blend · √M / REF)
```

with `REF = MAX_DENS_GLOBAL = 193` (recalibrated from **575** so all-pitched
display values keep the previous order of magnitude). `D_pitch` / `DV = 0` is
just a numeric zero — no `if` on event kinds in the composite path.

### Old → new mapping (all-pitched baselines)

| Artefact | Old `density.total` | New `density.total` | Notes |
|----------|---------------------|---------------------|-------|
| `tests/fixtures/regression_baseline.json` | 0.041179053279871765 | 0.04109677176465272 | REF 575→193; blend×mass |
| `tests/snapshots/numeric_outputs/synthetic_triad.json` | 0.01937804332565535 | 0.03033402437047291 | same formula |
| `replication/outputs_frozen/json/synthetic_triad.json` | 0.01937804332565535 | 0.03033402437047291 | regenerated |
| Benchmark `excerpt_001`…`005` | (pitch-gated era) | re-frozen via `benchmarks/scripts/freeze_outputs.py` | numeric layer only |

Pitch-structure density (`density.pitch_structure`), interval compactness, and
instrument RSS are **unchanged** by this edit; only `density.total` / composite
assembly and `MAX_DENS_GLOBAL` move.

### Display

- Header: `Composite: log10(1 + D_blend·√M / REF) with w=…, REF=193 (…)`.
- Unpitched-only spectral / advanced blocks: `n/a — no pitched content`.

### Construct-separation note

Exact unison can now score higher on `density.total` than a sparse
differentiated chord when Qty/mass dominates (composite includes mass in every
regime). The former check `property.unison_not_highest_composite` is replaced by
`property.unison_not_highest_pitch_structure` — vertical diversity remains on
the pitch-structure axis (`density.pitch_structure = 0` for exact unison).
