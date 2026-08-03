# CHANGES — Textural Density

Numeric and formula history for Textural Density. Cross-links: [TECHNICAL_MANUAL §3.5 / §3.12 / §7.5.1](docs/TECHNICAL_MANUAL.md) · [MATHEMATICAL_MANUAL §H](docs/MATHEMATICAL_MANUAL.md) · [constants_and_assumptions §7](docs/constants_and_assumptions.md).

## 2026-08-03 — Unpitched percussion: pitch-independent committed ladders

**Numeric change for non-anchor dynamics** on `bass_drum` / `cymbals` / `tamtam`
/ `gong` (pp/mf/ff anchors unchanged). Restores the former
`internal_default` piecewise log-linear CDM + adaptive-tail values as
**committed** `DYNAMIC_CDM` cells (no runtime GPR / log-linear fill-in).

Also drops the fake chromatic `spectral_data` grid: values were identical on
every note, and the GUI has no pitch for these instruments. Density is
dynamics-only; one canonical placeholder key remains for lookup compat.

Regenerator: `tools/generate_percussion_modules_from_nontunperc.py`.
Acceptance / regression goldens refrozen where non-anchor dynamics appear
(`tests/test_composite_unification_acceptance.py`,
`tests/fixtures/regression_baseline.json`, replication snapshots).

## 2026-08-03 — Full dynamics ladders: viola, cello, double bass, flute, clarinet, bassoon, oboe

**Numeric change for non-anchor dynamics** on these modules (pp/mf/ff anchors
unchanged). Each commits the Dynamics_predicter sheet **`Results`** ladder:

- `viola.py` ← `Viola_Arco normal_iowa_orchidea_dynamics.xlsx`
- `cello.py` ← `Cello_Arco normal_iowa_orchidea_dynamics.xlsx`
- `double_bass.py` ← `DBass_Arco normal__iowa_orchidea_dynamics.xlsx`
- `flute.py` ← `Flute_iowa_orchidea_dynamics.xlsx`
- `clarinet.py` ← `Clarinet_iowa_orchidea_dynamics.xlsx`
- `bassoon.py` ← `Basson_iowa_orchidea_dynamics.xlsx`
- `oboe.py` ← `Oboe_iowa_orchidea_dynamics.xlsx`

Regenerator: `tools/generate_full_dynamics_modules_from_xlsx.py`.
Still sparse (error on missing cells): trumpet, technique modules, etc.

## 2026-08-03 — Remove runtime GPR/tail extrapolation (table-only dynamics)

**Architecture change.** Instrument density no longer invents missing dynamics
at runtime. `core.orchestration` always calls `calcular_densidade`; sparse
tables raise `MissingCommittedDynamicError` for uncommitted markings.

- Retired production path: `predict_intermediate_dynamics` + adaptive tails
- Legacy code moved to `tools/legacy_gpr_dynamic_interpolation.py` (not imported by core)
- **Violin arco** commits the full 10-dynamic `Results` ladder (numeric change
  for non-anchor dynamics; pp/mf/ff anchors unchanged)
- Regenerator: `tools/generate_violin_arco_full_dynamics_from_xlsx.py`
- Other instruments still sparse until their full ladders are committed

## 2026-08-03 — Density stress battery (PR #37)

**No computed value changed.** Adds an analysis-only public-API stress suite:

- Entry: `python run_stress_battery.py` (details: [`tests/stress/README.md`](tests/stress/README.md))
- Families A–E: doubling, dynamics, mix/register, extremes, Monte Carlo + determinism
- Artifacts (gitignored): `STRESS_TEST_REPORT.md`, `stress_results.csv`, `stress_figures/`
- Contract tests: `tests/test_stress_battery_registry.py` (names / Qty / dyn / MIDI only)
- First full local run (~42 s): 61/61 slices; E5 determinism PASS; 0 blockers;
  1 documented caveat (D6: all-ffff composite &lt; all-pp on string quartet —
  see generated report SCOPE NOTES)

## 2026-08-03 — Label / docs accuracy (composite header, plural, REF provenance)

**No computed value changed in this release** (PR #35 code + this docs follow-up).
Totals, blends, mass, and baselines are bit-identical to the Task 8c unification
commit; only display strings, singular/plural wording, documentation, and
acceptance fixtures move.

- Header formula text is generated from `core.composite` (same expression as
  `compute_blend_density`); prints `D_blend=` and `M=`; blend shown as
  `w*(DI/10) + (1-w)*DV` (defaults) so it matches the sum of printed weighted
  components.
- Unpitched exclusion line uses `format_unpitched_exclusion_note` (singular/plural).
- REF=193 provenance documented in `config.py`, MATHEMATICAL_MANUAL, constants.
- Average-texture-density mean behaviour documented (may fall/rise; totals monotone).
- Acceptance freeze: `tests/test_composite_unification_acceptance.py`
  (GUI chain goldens; final composite **0.4595** at `w=0.5` — see test module
  docstring for session transcription notes).
- Cross-links updated in README, VERSIONING, MIGRATION, acoustic sources, QA.

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

- Header: built by `format_composite_header_line` (see label/docs accuracy entry).
- Unpitched-only spectral / advanced blocks: `n/a — no pitched content`.

### Construct-separation note

Exact unison can now score higher on `density.total` than a sparse
differentiated chord when Qty/mass dominates (composite includes mass in every
regime). The former check `property.unison_not_highest_composite` is replaced by
`property.unison_not_highest_pitch_structure` — vertical diversity remains on
the pitch-structure axis (`density.pitch_structure = 0` for exact unison).
