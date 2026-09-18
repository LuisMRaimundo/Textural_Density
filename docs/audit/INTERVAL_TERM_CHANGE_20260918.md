# Interval term change — effective interval cardinality

**Date:** 2026-09-18  
**Branch:** `feat/interval-effective-cardinality` (not pushed, not merged, not tagged)  
**Baseline HEAD:** `0c5cab945a9c3f83b55ac9b723bf62939fad0b1b`  
**Package:** 1.1.7 → 1.2.0 (`pyproject.toml`, `core/version.py`)  
**Methodology:** 5.1.0-strict-symbolic → 5.2.0-strict-symbolic (`core/defaults.py:11`)  
**Probe:** `scripts/diagnostic_probe.py` (H3/H4 reconstruction diffs were 0.0)

This report does not claim scientific validity of Textural Density. Every numerical claim cites `file:line` or executed output.

---

## Preconditions

### P1 — Kernel bounds (PASS)

Loaded λ = **0.05** (`parameters/density_params.json`; `load_calibrated_parameters()`; probe `P1_kernel.lambda`).

Implementation (`densidade_intervalar.py:241–243`):

```
if delta == 0:
    return 1.0
return math.exp(-lamb * delta)
```

Executed `scripts/diagnostic_probe.py` → `P1_kernel.ok = True`:

| δ (microtonal steps) | K(δ) | 0 < K ≤ 1 |
|---|---|---|
| 0 | 1.0 | K(0)=1 |
| 0.001 | 0.9999500012499791 | yes |
| 0.5 | 0.9753099120283326 | yes |
| 1.0 | 0.951229424500714 | yes |
| 2.0 | 0.9048374180359595 | yes |
| 12.0 | 0.5488116360940264 | yes |
| 24.0 | 0.301194211912202 | yes |
| 48.0 | 0.09071795328941247 | yes |
| 96.0 | 0.008229747049020023 | yes |

The n_eff reading is therefore well-defined: every pair term is in (0, 1], and unison distance is 1.

Kernel and λ were not changed.

### P2 — Table coefficients reachable in tests (PASS)

Executed probe `table_coeff_scan` over every registry module that exposes `spectral_data`:

- 33 table-backed modules
- 12110 cells
- `nonpositive = []`
- `ok = True`

Instrument tables were not edited in this change (`git diff --name-only -- instrumentos parameters` is empty except that `parameters/density_params.json` is unchanged; SHA-256 prefix `151a6eae5a49f309`).

### P3 — Pre-existing working-tree changes (PASS; none left untouched)

Inspection started from clean `0c5cab9` on `feat/interval-effective-cardinality`. There were **no** leftover uncommitted string-table or instrument-module edits. This patch does not touch `instrumentos/*.py` table cells.

REF remains **193** (`config.py:28`). Final composite `log10(1+x)` remains (`config.py:29`, `core/pitch_structure.py:129–130`).

---

## Definition now in production

`core/pitch_structure.py:43–53` — `effective_interval_cardinality`:

\[
D_V = \frac{\sqrt{1+8S}-1}{2}=n_{\mathrm{eff}}-1
\quad(n\ge 2);\qquad D_V=0\quad(n<2).
\]

`normalize_interval_density`, mean-pairwise normalisation, and the `USE_LOG_COMPRESSION` branch **inside** that helper are gone. No alias.

`core/composite.py:27–40` — blend (numerically the previous default):

\[
D_{\mathrm{blend}} = w\cdot D_I/10 + (1-w)\cdot D_V
\]

`INTERVAL_BLEND_NORMALISATION` / `unit_range` removed. Probe H3 abs_diff **0.0**; H4 abs_diff **0.0**.

Export key `density.interval` is unchanged; human label is “effective interval cardinality (n_eff − 1)” (`core/formatting.py:86`, `gui/widgets/results_panel.py:143`, `core/metrics_metadata.py:256–259`). Raw pair sum S remains `interval_compactness.raw`.

---

## Tests T1–T8

Executed: `tests/test_effective_interval_cardinality.py` (T1–T7) all **PASSED**.

Full suite after refreshing the editable metadata (`pip install -e . --no-deps`, no dependency upgrade): **1961 passed**, 12 skipped, 33 xfailed on the first full run except `test_get_package_version_matches_fallback` (installed dist still said 1.1.7). That test **PASSED** after the metadata refresh. Coverage on the full run: **86.23%**.

### T1–T5, T6

T1–T5 passed at the stated tolerances. T6 (production `density.total` / `density.weighted` never decrease when a distinct pitch is added; seeded grid) **PASSED** — no failing case to report.

### T7 — order only; actual totals (4 violins mf, Qty 1)

From executed `scripts/diagnostic_probe.py` `before_after` (same production path as T7):

| voicing | density.total |
|---|---|
| cluster C4–C#4–D4–D#4 | 0.086574 |
| major thirds C4–E4–G#4–C5 | 0.071617 |
| fifths C4–G4–D5–A5 | 0.066878 |
| octaves G3–G6 | 0.073474 |

Order: cluster > thirds > fifths. These match the HEAD-`0c5cab9` table expectation cited in the task (~0.0866, 0.0716, 0.0669, octaves ~0.0735).

### T8 — updated goldens

Only values that move because \(D_V\) changed (instrument RSS, mass, \(S\), \(D_{\mathrm{pitch}}\) unchanged unless listed). Tolerances were not loosened.

| Golden | Field | Old (0c5cab9) | New | Reason |
|---|---|---|---|---|
| `tests/snapshots/numeric_outputs/synthetic_triad.json` | `density.interval` | 0.2137588382139519 | 1.5162954002371611 | mean-log \(D_V\) → \(n_{\mathrm{eff}}-1\) |
| same | `density.weighted` | 2.44601147563867 | 3.0972797566502743 | same blend with new DV |
| same | `density.total` | 0.04688897865038914 | 0.058564805375031864 | log10(1+blend√M/193) |
| same | `density.absolute` | 3.390891915912431 | 4.293741461455062 | uses new weighted |
| same | `density.weighted_pitch` | 0.10687941910697595 | 0.7581477001185806 | 0.5·new DV |
| same | `interval_compactness.normalized` | 0.2137588382139519 | 1.5162954002371611 | reports DV |
| `tests/snapshots/metadata_outputs/synthetic_triad.json` | `metric_schema_version` | 5.1.0-strict-symbolic | 5.2.0-strict-symbolic | methodology bump |
| `replication/outputs_frozen/json/synthetic_triad.json` | same density keys | as snapshot old | as snapshot new | frozen copy of production |
| `replication/tables/thesis_symbolic_density_summary.md/.csv` | interval / total / compactness / schema | 0.21376 / 0.04689 / 5.1.0 | 1.51630 / 0.05856 / 5.2.0 | table from frozen JSON |
| `tests/fixtures/regression_baseline.json` | `density.interval` | 0.1886837391214329 | 2.103757825240598 | new DV |
| same | `density.weighted` | 2.803586228929951 | 3.7611232719895344 | new DV in blend |
| same | `density.total` | 0.06363638437261204 | 0.08339696358969217 | new blend |
| same | `density.absolute` | 4.512197967618012 | 6.053294387278149 | new weighted |
| same | `density.weighted_pitch` | 0.09434186956071647 | 1.051878912620299 | 0.5·new DV |
| same | instrument / pitch_structure / sonic_mass / weighted_orchestral | unchanged | unchanged | not functions of reported DV |
| `tests/test_composite_unification_acceptance.py` | 5 strings ff | 0.11097263710915733 | 0.13760876084378282 | new DV in blend×mass |
| same | +bass drum | 0.12076759726730982 | 0.14837365260546084 | same |
| same | +cymbals | 0.12909176148013493 | 0.15748910017708936 | same |
| same | +flute/oboe ffff | 0.1405447032447646 | 0.17769046379474154 | same |
| same | +tam-tam ffff | 0.1473125021895525 | 0.18514978714582095 | same |
| same | Qty expansion 4/5/5/3/10 | 0.4069651180509932 | 0.4468783742513252 | same |
| `benchmarks/expected_outputs/excerpt_001.json` | interval / weighted / total | 0.2137588382139519 / 2.44601147563867 / 0.04688897865038914 | 1.5162954002371611 / 3.0972797566502743 / 0.058564805375031864 | freeze of production |
| excerpt_002 | interval / weighted / total | 0.1886837391214329 / 2.44095021212104 / 0.049418411167705636 | 2.103757825240598 / 3.3984872551806227 / 0.0673659880937583 | same |
| excerpt_003 | interval / weighted / total | 0.22383396101669067 / 2.5999606010814253 / 0.05448862894059124 | 2.3881882960595386 / 3.682137768602849 / 0.07529672717883186 | same |
| excerpt_004 | interval / weighted / total | 0.23609954188252116 / 2.651603914996785 / 0.05918442415611134 | 3.333440435923234 / 4.200274362017142 / 0.09035349419098379 | same |
| excerpt_005 | interval / weighted / total | 0.19291068220480828 / 4.269560282111826 / 0.121022012758108 | 4.372138689177468 / 6.359174285598156 / 0.1698637228767285 | same |
| `reports/plausibility_raw.json` | recorded DV / weighted / total fields | pre-5.2.0 dump | rewritten by F-B / F-E battery | dump follows live DV; not a loosened assertion |

`weighted_density_DI50_DV5 = 5.0` in the regression fixture was **not** changed (`0.5·50/10 + 0.5·5 = 5`).

---

## BEFORE / AFTER table

Old \(D_V=\log_{10}(1+2S/n(n-1))\). New \(D_V=(\sqrt{1+8S}-1)/2\). Blend and REF unchanged, so old weighted/total are the same formula with old DV. Executed by `scripts/diagnostic_probe.py` (`before_after`).

Share = interval term / weighted = \((1-w)D_V / D_{\mathrm{blend}}\) at \(w=0.5\).

| Case | old DV | new DV | old weighted | new weighted | old total | new total | old share | new share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| chromatic n=1 | 0.0 | 0.0 | 1.445382 | 1.445382 | 0.017144 | 0.017144 | 0.0 | 0.0 |
| chromatic n=2 | 0.279858 | 0.935157 | 2.206666 | 2.534315 | 0.036395 | 0.041548 | 0.0634 | 0.1845 |
| chromatic n=3 | 0.273264 | 1.846660 | 2.605086 | 3.391784 | 0.051064 | 0.065375 | 0.0524 | 0.2722 |
| chromatic n=4 | 0.266890 | 2.730415 | 2.946597 | 4.178360 | 0.065164 | 0.089750 | 0.0453 | 0.3267 |
| chromatic n=6 | 0.254769 | 4.418076 | 3.512864 | 5.594517 | 0.091420 | 0.137714 | 0.0363 | 0.3949 |
| chromatic n=12 | 0.222943 | 8.923652 | 4.600062 | 8.950417 | 0.152105 | 0.259125 | 0.0242 | 0.4985 |
| cluster C4–D♯4 (4 vl) | 0.266890 | 2.730415 | 2.858646 | 4.090409 | 0.062270 | 0.086574 | 0.0467 | 0.3338 |
| major thirds (4 vl) | 0.186147 | 2.082949 | 2.559470 | 3.507871 | 0.053389 | 0.071617 | 0.0364 | 0.2969 |
| fifths (4 vl) | 0.130624 | 1.612064 | 2.531953 | 3.272673 | 0.052617 | 0.066878 | 0.0258 | 0.2463 |
| octaves G3–G6 (4 vl) | 0.073861 | 1.073113 | 2.964181 | 3.463807 | 0.063613 | 0.073474 | 0.0125 | 0.1549 |
| minor-second dyad | 0.279858 | 0.935157 | 2.206666 | 2.534315 | 0.036395 | 0.041548 | 0.0634 | 0.1845 |
| dyad + C8 (piano) | 0.116404 | 0.947178 | 0.693002 | 1.108389 | 0.007115 | 0.011324 | 0.0840 | 0.4273 |
| tutti 12 mixed sources | 0.140160 | 6.608294 | 5.266832 | 8.500899 | 0.176733 | 0.257823 | 0.0133 | 0.3887 |

Tutti notes/instruments/dynamics (probe `tutti_12_mixed`):  
C5/flauta/mf, G4/oboe/p, E4/clarinete/mp, C3/fagote/f, G3/trompa/ff, A4/violino/mf, D4/viola/p, G2/violoncelo/mp, C4/trompete/f, Bb3/trombone/mf, E3/piano/pp, E2/contrabaixo/ff.

The old mean-log term **falls** from n=2 to n=12 (0.280 → 0.223) and was 2–6 % of weighted. New DV **rises** (0.935 → 8.924) and is 18–50 % of weighted on these slices.

---

## NOT VERIFIED

- **Historical research workbooks / characterisation CSVs / `reports/stress_results_v1.csv`** were not regenerated (task: do not rerun the corpus). Their stored `density.interval` values remain the pre-5.2.0 mean-log numbers.
- **CI on GitHub Actions / CircleCI** was not run.
- **GUI click-through** was not exercised in a browser; labels were updated in source (`results_panel.py:143`, `formatting.py:86`).
- **Installed-dist metadata** on a machine that still has wheel `1.1.7` will make `get_package_version()` return 1.1.7 until `pip install -e .` (or an equivalent install) is refreshed. Source `PACKAGE_VERSION` is 1.2.0.

---

## Unchanged by design

- Kernel `modified_exponential_decay` and λ = 0.05
- REF = 193
- RSS instrument density and linear mass
- `compute_pitch_structure_density` (raw S × entropy × damping)
- Final `log10(1+x)` on the composite
- Export key `density.interval`
