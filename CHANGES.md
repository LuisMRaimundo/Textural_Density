# CHANGES — Textural Density

Numeric and formula history for Textural Density. Cross-links: [TECHNICAL_MANUAL §3.5 / §3.12 / §7.5.1](docs/TECHNICAL_MANUAL.md) · [MATHEMATICAL_MANUAL §H](docs/MATHEMATICAL_MANUAL.md) · [constants_and_assumptions §7](docs/constants_and_assumptions.md).

## 2026-08-27 — Cello technique ladders from dest-Zenodo dynamics

Added `cello_sordina`, `cello_sul_ponticello`, and `cello_harmonics` from `D:\CORDAS_2\Cello_*_dynamics.xlsx` (`Results`, Dynamics_predicter v1.5.2.1 `--pchip` r=0.8). Same commit path as the violin/viola techniques (`--cello-only`). GUI display names are `vlc_sord`, `vlc_sp`, `vlc_harm`. Sordina is C2–A5 (46 notes); ponticello is C2–C6 (49 notes); harmonics is C4–E7 (41 notes; C2–B3 withdrawn from the dest book). Cello sul tasto stays withdrawn. Formulae unchanged.

## 2026-08-26 — Refresh string technique range-audit docs

Regenerated `reports/instrument_register_audit.*` and `reports/instrument_metadata_range_resolution_audit.*` so committed spans match dest-Zenodo tables (viola sordina/ponticello C3–A#6; viola/violin harmonics C5–B7; violin ponticello G3–B7). GUI names for viola techniques remain `vla sord`, `vla sp`, `vla harm`. Formulae unchanged.

## 2026-08-26 — Viola technique ladders from dest-Zenodo dynamics

Rebuilt `viola`, `viola_sordina`, `viola_sul_ponticello`, and `viola_harmonics` from `D:\CORDAS_2\Viola_*_dynamics.xlsx` (`Results`, Dynamics_predicter v1.5.2.1 `--pchip` r=0.8). Same commit path as the violin techniques (`--viola-only`). GUI display names remain `vla sord`, `vla sp`, `vla harm`. Sordina and ponticello tables are C3–A#6 (47 notes); harmonics is C5–B7 (36 notes). Formulae unchanged.

## 2026-08-26 — Violin technique ladders from dest-Zenodo dynamics

Rebuilt `violin_sordina`, `violin_sul_tasto`, `violin_sul_ponticello`, and `violin_harmonics` from `D:\CORDAS_2\Violin_*_dynamics.xlsx` (`Results`, Dynamics_predicter v1.5.2.1). Same commit path as the existing harmonics generator (`--violin-only`). GUI display names are now `vl_con_sord`, `vl_sul_pont`, `vl_sul_tast`, `vl_harm` (old short names remain aliases). Harmonics table is C5–B7 (36 notes); ponticello is G3–B7 (53 notes). Formulae unchanged.

## 2026-08-25 — Dest-Zenodo ordinary-sustain ladders: freeze refresh

Ordinary-sustain CDM tables (12 instruments) were rebuilt from dest `_2` Zenodo books via Dynamics_predicter. This commit refreshes the goldens and contracts that those tables drive. Formulae unchanged.

- Trombone sounding span is now MIDI **29–72 (F1–C5)**. C#1–E1 were dropped because dest books have no complete pp/mf/ff triad.
- Official refresher: `python tools/refresh_regression_fixtures.py` (regression baseline, synthetic triad snapshots, replication freeze, benchmark excerpts).
- Composite GUI-chain goldens in `tests/test_composite_unification_acceptance.py` re-frozen (5 strings ff total 0.11097 at w=0.5).
- Violin G4 mf pin is 32.4618617. Sordina mute-attenuation pin moved from A3 pp (now sordina > arco vs dest arco) to A#4 pp, where sordina < arco still holds.
- Blend orch/pitch ratio is no longer pinned at 16.1; it follows the committed triad snapshot.

## 2026-08-18 — Strict wrap-around enharmonics; reject unknown instrument ids (package 1.1.6)

**Numeric change for `Cb` / `B#` spellings only.** Default 12-EDO totals (C, C#, D, … and same-octave flats such as Db/Eb) are unchanged. Locked by `tests/test_wraparound_enharmonics.py::test_golden_baseline_wrap_spellings_match_plain_totals`: the golden regression slice (`C4 E4 G4 C5`) with every wrap-around spelling substituted for its plain equivalent (`C4`→`B#3`, `C5`→`B#4`) yields identical `density.*` totals. The committed 12-EDO golden fixture itself contains no such spellings.

- `core.pitch_aggregation` and `core.source_aggregation` convert note strings with `note_to_midi_strict` (octave wrap: `Cb5` = B4 = 71, `B#3` = C4 = 60). The legacy `note_to_midi` path mapped `Cb5` → 83.
- `converter_para_sustenido` now wraps `Cb`/`B#` when building `Pitch.note_name` (`Cb5` → `B4`, not `B5`), so the orchestration lookup string and the aggregation key stay on the same MIDI. Instrument-table lookup also reads the MIDI axis from the written spelling before `to_sharp` preprocess.
- `core.reporting` interval labels (`explain_score_slice` / `_top_interval_pairs`) are report-string-only and now use `note_to_midi_strict` so wrap-around labels cannot diverge from aggregation.
- **Unknown-id policy:** unregistered names, including the withdrawn cello/bass technique ids, raise `InputError` (`field: instruments`). They are not remapped to a parent module and not served by the generic coarse proxy. The error names the MusicXML/MIDI part (`part_id`, `part`) and lists accepted registry ids. `analyze_score`, the MusicXML/MIDI importers, and the GUI adapter all fail closed (the adapter no longer relies on the coarse proxy for unrecognised dropdown states). The proxy is audit-only (`profile_for_event(..., allow_unknown=True)`), not reachable from `calculate_metrics`. Registered coarse ids are unchanged. Common MusicXML labels `Clarinet in Bb` and `Horn in F` are aliases of `clarinete` / `trompa` (not a proxy). Benchmark `excerpt_003` is re-frozen now that that part uses the clarinet table instead of the former 8.0 unknown proxy. Documented in Mathematical Manual §F and `docs/API.md`.

## 2026-08-18 — Withdraw cello and double-bass technique modules

Removed from `instrumentos/` and the GUI (profiles with `module_name` only):

- `cello_sordina`, `cello_sul_tasto`, `cello_sul_ponticello`
- `double_bass_sordina`, `double_bass_sul_tasto`, `double_bass_sul_ponticello`

Ordinary cello and double-bass arco modules remain. Violin and viola technique /
harmonic modules are unchanged. Dedicated generators and technique-module tests
were retired with the tables.

## 2026-08-18 — Add trombone: committed 10-level dynamic ladder

New `instrumentos/trombone.py`: 48 pitches (C#1–C5, MIDI 25–72) × 10 dynamics from
`D:\METAIS\Trombone_Dynamics.xlsx` (`Results`) via Dynamics_predicter v1.5
(measured pp/mf/ff anchors verbatim).

- Registry: trombone wired to the module, GUI display name **Trb**, sounding
  range updated from the (40–72) placeholder to the table span (25–72).
- Metadata range audit: trombone review classifies against the committed table
  (**PASS** when registry matches span); trombone added to the table-backed
  brass module set. Bass trombone remains coarse.
- Tests: trombone classification contract added; coarse-only provenance tests
  now use bass trombone (and piano where a second coarse profile is required).

## 2026-08-18 — Symmetric octave-class harmonic ratio; opt-in blend normalisation (package 1.1.5)

Schema label unchanged (`5.1.0-strict-symbolic`). Two production commits, then this docs/version alignment.

**[`cea577a`](https://github.com/LuisMRaimundo/Textural_Density/commit/cea577a) — defect repairs** (default 12-EDO totals unchanged):

- Harmonic membership is the symmetric octave-class distance $\min(r,12-r)\le 0.25$ with $r=(m_i-m_{\min})\bmod 12$. Microtonal `harmonic_ratio` / `pitch_structure` can change; committed 12-EDO snapshots do not. Lock: `tests/fixtures/microtonal_harmonic_ratio.json`.
- `MIN_PCHIP_ANCHORS = 4` unifies explicit `"pchip"` with `"auto"` (auto behaviour unchanged).
- `compute_registral_compactness` marked non-production; README no longer lists it as a reported subindex.
- `compute_composite_from_blend` delegates to `compute_composite_vertical_density`.
- Verification tests for the DV $\le\log_{10}(2)$ bound and the triad orch/pitch ratio $\approx 16.1$ at $w=0.5$.

**[`72eb0a5`](https://github.com/LuisMRaimundo/Textural_Density/commit/72eb0a5) — opt-in / diagnostics** (legacy default bit-identical):

- `INTERVAL_BLEND_NORMALISATION = "legacy" | "unit_range"`. `"unit_range"` is approximate parity (DV bounded; DI still divided by the unclamped empirical `DI_max=100`). The two modes are not comparable.
- `composite_meta.blend_term_contributions` reports realised blend terms; `instrument_to_interval_ratio` is JSON `null` when the interval term is 0.
- Mathematical Manual §H: divisors are not clamps; double-log asymmetry on DV vs uncompressed DI is pinned, not “fixed”.

## 2026-08-09 — Add tuba: committed 10-level dynamic ladder

New `instrumentos/tuba.py`: 47 pitches (C1–A#4, MIDI 24–70) × 10 dynamics from
`D:\METAIS\Tuba_Zenodo_collections_media.xlsx` (`Tuba_Media`) via
Dynamics_predicter v1.5 (measured pp/mf/ff anchors verbatim).

- Registry: tuba wired to the module, display name **Tba**, sounding range
  updated from the (28–58) placeholder to the table span (24–70).
- Metadata range audit: tuba review classifies against the committed table
  (**PASS** when registry matches span); trumpet/horn/tuba added to the
  table-backed module set.
- Tests: tuba classification contract updated; coarse-only provenance test now
  uses trombone + bass trombone. Trombone later gained a committed table
  (2026-08-18); bass trombone remains coarse.

## 2026-08-08 — Data-faithful 10-level ladders for all pitched instruments

**Numeric change on all pitched table-backed modules.** Ladders regenerated with
**Dynamics_predicter v1.5** (PCHIP interiors, tapered outers, `--pchip`) from the
curated Zenodo `*_Media` workbook anchors; measured pp/mf/ff committed
**verbatim** (the 2026-08-03 isotonic clamp is no longer applied — measured
non-monotonicity is preserved by design):

- Arco/ordinario rebuilds: violin, viola, cello, double bass, flute, oboe,
  clarinet, bassoon, trumpet; **new module: horn** (`horn.py`, G1–F5).
- The 12 string technique modules (sordina / sul tasto / sul ponticello ×
  violin, viola, cello, double bass) rebuilt from their pre-clamp measured
  anchors (`*_MEASURED` dicts again match `spectral_data` exactly).
- Violin harmonic modules keep the D6 monotone ladders pending rebuild.
- GUI: English orchestral short display names (Vl, Vla, Vc, Db, Fl, Ob, Cl,
  Bsn, Tpt, Hn); former long names remain as aliases.
- Contract rewrite: `tests/test_pitched_dynamic_monotone_ladders.py` now checks
  full-ladder completeness + hygiene (interiors within measured segments,
  tapered outers, no zigzag) instead of strict monotonicity.
- Frozen fixtures refrozen (regression baseline, benchmark corpus, composite
  acceptance goldens, replication snapshots, GPR audit reports).
- String source reconstruction configs fixed: all four strings verify against
  their curated Media sheets (violin/viola paths corrected; cello now reads
  `Cello_Media`).
- Audit tools tolerate non-git checkouts when recording the repository SHA.

## 2026-08-03 — Stress-battery D6 hotfix (data layer)

**Numeric change** on pitched table-backed modules: pp/mf/ff anchors are
isotonic-clamped soft→loud, then full `DYNAMIC_LEVELS` rebuilt offline with the
former unpitched `internal_default` log-linear CDM + adaptive tails
(`tools/enforce_pitched_monotone_dynamic_ladders.py`). Fixes stress assertion
`D6_ffff_gt_pp` (ffff composite was below pp).

- Contract: `tests/test_pitched_dynamic_monotone_ladders.py`
- Range audit: explicit `table_excludes_sounding_range` column; labelled
  `LABELLED_TABLE_FALLBACK` warnings + lookup-trace fields when a note is inside
  sounding range but outside the table (never silent). Violin [55,103] is
  aligned; double bass remains E1–C5 / [28,72].
- C2 probe: Tam-tam **ff** (not ffff); quintet adds Double bass **A1** (in-range).
- Reports: `reports/STRESS_TEST_REPORT_v1.md` (pre-fix) + `v2` (post-fix);
  `git_hash()` hardened (reads `git -C` / `.git` refs; no silent `unknown` when readable).
- Lookup-trace fix: coarse profiles no longer fall through to the violin table.
- Engine/composite untouched; A–E assertions remain green.

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
