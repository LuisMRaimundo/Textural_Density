# QA checklist — release and formula migrations

Use alongside [`score_only_90_readiness_checklist.md`](score_only_90_readiness_checklist.md).

## Test suite and CI (verified 2026-07-12, methodology `5.1.0-strict-symbolic`, package `1.1.4`)

| Gate | Status |
|------|--------|
| Full suite | Re-verify after dynamics migration (adaptive-tail xfails retired) |
| Skipped | 2 — violin / viola source-workbook reproducibility when Zenodo files absent |
| Xfailed | Adaptive-tail positivity grid removed with runtime GPR (2026-08-03) |
| Full-project coverage | gate ≥ 63% (CI quality job) |
| `core/` + `validation/` coverage | ≥ 80% (CI quality job) |
| MyPy (`core`, `validation`) | Clean |
| Slow performance gate | Pass |
| `import Main` smoke | OK |
| GitHub Actions | `test` 3.10, 3.11 + `quality` — green |
| CircleCI | `tests-3.10`, `tests-3.11` — green |
| Local Python | 3.10 (CI also covers 3.11) |

- [x] Full suite green locally and on CI
- [x] GitHub Actions: `test` (3.10, 3.11) + `quality` green
- [x] CircleCI: `tests-3.10`, `tests-3.11` green

**Epistemic scope:** the suite verifies implementation contracts, source consistency, provenance propagation, symbolic/musical invariants, and reproducibility — not auditory adequacy of CDM or correspondence to listener judgments of textural density / symbolic-dynamic mass.

## String musicological battery (PR #13)

97 tests across:

- `tests/string_constants.py`
- `tests/test_string_module_contracts.py`
- `tests/test_string_source_reproducibility.py`
- `tests/test_string_musicological_invariants.py`
- `tests/test_string_score_scenarios.py`
- `tests/test_instrument_provenance.py`

Coverage includes: module/table contracts; exact anchor lookup; source workbook reconstruction (local); pitch spelling; Unicode accidentals; enharmonic normalization; cents/microtonal handling; interpolation provenance; committed-dynamics contracts; organological fixtures; ensemble/MusicXML scenarios; double-bass sounding-pitch via MusicXML transposition; quantity row-splitting; unison/octave/cluster/register/dynamics/event-order invariants.

Run: `pytest -m musicological -q`

- [x] String battery passes (violin, viola, cello, double bass + aliases)

## Viola source-label correction (PR #14)

- [x] `normalize_media_note_label()` strips trailing `(2)` before canonical parsing (`F4 (2)` → `F4`)
- [x] Viola `spectral_data` aligned to `VIOLA_Media` (C3–C7, 49 rows)
- [x] `calcular_densidade("C3", "mf")` → 62.806258 (corrected anchor)
- [x] Portable viola provenance: `docs/instrument_acoustic_sources.md#viola`
- [x] Violin, cello, double-bass tables unchanged by PR #14

## Source workbook reconstruction (local)

| Workbook | Status |
|----------|--------|
| `VIOLIN_Zenodo_collections_media.xlsx` | PASS — 49 rows, 0 value differences |
| `ViOLA_Zenodo_collections_media.xlsx` / `VIOLA_Media` | PASS — 49 rows, 0 value differences |
| `CELLO_Zenodo_collections_media.xlsx` | PASS |
| `DOUBLEBASS_Zenodo_collections_media.xlsx` | PASS |

CI skips reconstruction when `D:\CORDAS\` workbooks are unavailable on the runner.

## Remaining scientific-review candidates

1. **Double-bass table span adjudication:** resolved — `source_table_span` E1–C5 aligns with committed module, `INSTRUMENT_SOURCE.pitch_range`, and registry; E1–A3 was obsolete documentation. Upper-register methodological QC (A♯3–C5) remains **REVIEW REQUIRED**.
2. **Technique metadata vs tables:** resolved — `INSTRUMENT_SOURCE.source_technique` / `table_supported_techniques` distinguish numerical table coverage from registry organological capabilities.
3. **Tuba range:** MIDI 28–58 is coarse-default validation placeholder — **REVIEW REQUIRED** for authoritative organological range.
4. **Committed dynamics (2026-08-03):** runtime GPR removed; all table-backed pitched modules + unpitched percussion commit soft→loud monotone 10-level ladders; coarse-default registry names remain without acoustic tables.

Resolved by PR #14: viola machine-local `D:\CORDAS\...` provenance path (now portable doc anchor).

## Validation contract layers (symbolic)

- [x] Interval-density formal contracts (`tests/test_densidade_intervalar_contract_additional.py`)
- [x] Instrument-density registry scaffold (`tests/test_instrument_density_registry_scaffold_contract_additional.py`)
- [x] Scientific/musicological output plausibility (`tests/test_scientific_musicological_output_plausibility_additional.py`)
- [x] Excel importer Phase 1a (`tests/test_instrument_profile_excel_importer_additional.py`)
- [x] String musicological battery (PR #13)
- [x] Media note-label normalization (`tests/test_notes.py`, PR #14)

## Unpitched percussion entry paths (PR #29)

- [x] GUI: note/octave/cents hidden for Bass drum / Cymbals / Tam-tam / Gong; group label `── Unpitched percussion ──`
- [x] Adapter injects canonical placeholder (`D2` / `C5` / `C2` / `C3`) regardless of stale note state
- [x] Cents/microtones for unpitched instruments raise `InputError`
- [x] MusicXML `<unpitched>` maps by part name; display-step/octave never become sounding pitch
- [x] MIDI channel 10 GM map (35/36 bass drum; 49/57 crash; 51/59 ride→Cymbals approx; 52 Chinese→Cymbals); unmapped keys skipped with warning
- [x] Pitch-structure exclusion only in `partition_pitched_events` (no duplicate filters in GUI/loaders)
- [x] Docs: README, `docs/TECHNICAL_MANUAL.md` §7.5, `docs/instrument_acoustic_sources.md`, `instrumentos/README.md`

Run: `pytest tests/test_unpitched_entry_paths.py tests/test_unpitched_pitch_exclusion.py -q`

## Unpitched aggregation (PR #31 / Task 8b) + unified composite (PR #33 / Task 8c) + labels (PR #35)

- [x] Event Count / Player Count = pitched + unpitched (mixed slice 4/4)
- [x] Texture `player_count` / `player_weighted_texture_mass` include unpitched Qty
- [x] Texture `average_texture_density` = Qty-weighted mean CDM (includes unpitched)
- [x] Texture `texture_polyphony` / variability / contrast remain pitched-only
- [x] Unified composite: `log10(1 + D_blend*sqrt(M)/REF)` with `REF=193`; no unpitched-only fallback
- [x] Property tests: monotonicity, mixed > subsets, continuity (`tests/test_unified_composite_contract.py`)
- [x] Display: singular/plural exclusion; header from `core.composite` with `D_blend=` + `M=`; unpitched-only spectral = `n/a`
- [x] Acceptance freeze: `tests/test_composite_unification_acceptance.py`
- [x] All-pitched baselines re-frozen; old→new totals in `CHANGES.md`
- [x] Docs cross-links: TECHNICAL_MANUAL §3.5 / §3.12 / §7.5.1, API, constants, acoustic sources, VERSIONING

Run: `pytest tests/test_unpitched_aggregation_contract.py tests/test_unified_composite_contract.py -q`

## Density stress battery (PR #37)

- [x] Entry point `run_stress_battery.py` uses only public API (`AnalysisRequest` / `calculate_metrics`)
- [x] Families A–E covered (doubling, dynamics, mix/register, extremes, Monte Carlo + determinism)
- [x] Artifacts: working `STRESS_TEST_REPORT.md` / CSV / figures (gitignored); tracked `reports/STRESS_TEST_REPORT_v1.md` + `v2.md`
- [x] D6 hotfix: monotone pitched ladders; C2 Tam-tam ff; git hash populated in report
- [x] Registry contract: `tests/test_stress_battery_registry.py`
- [x] Docs: [`tests/stress/README.md`](../tests/stress/README.md), README Testing, CHANGES, TECHNICAL_MANUAL §10
- [ ] Re-run after formula edits and attach regenerated report to the PR if behaviour shifts

Run: `python run_stress_battery.py` (full battery ≈ 40–60 s locally)

## GUI architecture

- [x] `pytest tests/test_gui_architecture.py` passes
- [x] No `gui/**/*.py` file imports `data_processor`
- [x] `Main.py` calls `AnalysisController.analyze` / `format_results` only
- [x] GUI input flows through `build_analysis_request` → `AnalysisRequest.from_mapping`
- [x] Removed legacy keys stripped before core (`core/input_validation.py`)

## Qty semantics sign-off

**Qty semantics verified:**

- Qty represents player/instrument count, not additional pitch events.
- Qty affects player_count and orchestral/sonic mass.
- Qty does not affect distinct_pitch_count, interval-pair count, spectral entropy, registral span, chroma classes, or pitch polyphony.
- One row with Qty = N and N identical rows with Qty = 1 are equivalent for player-count, mass, and pressure-equivalent instrument-density purposes.
- No metric scales as Qty^(3/2).
- Dynamics are applied exactly once.
- GUI labels distinguish event count, player count, pitch polyphony, and orchestral mass.

Tests: `tests/test_quantity_scaling.py`, `tests/test_gui_architecture.py`.

- [x] GitHub Actions quality job green (mypy on `core/` + `validation/`; coverage gates)

## MusicXML / score intake

- [x] MusicXML `<transpose>` applied once — written `<pitch>` converted to sounding/concert pitch
- [x] `written_pitch` vs `sounding_pitch` on `InstrumentEvent` when MusicXML transposition applies
- [x] `tests/test_xml_loader.py::TestMusicXmlTranspose` passes
- [x] `benchmarks/corpus/excerpt_003.musicxml` + frozen `expected_outputs/excerpt_003.json`
- [x] `benchmarks/corpus/excerpt_004.musicxml` (transpose persists measure 2) + frozen output
- [x] `benchmarks/corpus/excerpt_005.musicxml` (multi-instrument dynamics) + frozen output
- [x] Dynamic docs aligned with committed-ladder lookup; see `docs/TECHNICAL_MANUAL.md` §2.4.1
- [x] Table-backed pitched + unpitched-percussion full monotone dynamics tables; `MissingCommittedDynamicError` only for truly missing cells
- [ ] Global onset reconstruction from MusicXML `<duration>` accumulation (not implemented)

## Frozen outputs (when formulas change)

- [ ] Update `tests/fixtures/regression_baseline.json`
- [ ] Update `tests/snapshots/numeric_outputs/` and document in `tests/snapshots/MIGRATION.md`
- [ ] Run `python benchmarks/scripts/freeze_outputs.py`
- [ ] Run `python replication/scripts/reproduce_metrics.py` and `compare_to_frozen_outputs.py`

## Replication benchmark checklist

- [ ] Manifest license fields valid
- [ ] Frozen numeric outputs match after intentional changes
- [ ] Qty semantics sign-off (above) completed for any mass/density formula change
