# QA checklist — release and formula migrations

Use alongside [`score_only_90_readiness_checklist.md`](score_only_90_readiness_checklist.md).

## Test suite and CI (verified 2026-06-25, `main` @ `607bf4a`)

| Gate | Status |
|------|--------|
| Full suite | **862 passed** (861 non-slow + 1 slow) |
| Non-slow suite | **861 passed** |
| Full-project coverage | **84.95%** (gate ≥ 63%) |
| `core/` + `validation/` coverage | ≥ 80% (CI quality job) |
| MyPy (`core`, `validation`) | Clean |
| Slow performance gate | Pass |
| `import Main` smoke | OK |
| `pytest --collect-only` | 862 collected |
| GitHub Actions | `test` 3.10, 3.11 + `quality` — green |
| CircleCI | `tests-3.10`, `tests-3.11` — green |
| Local Python | 3.10.11 (CI also covers 3.11) |

- [x] Full suite green locally and on CI
- [x] GitHub Actions: `test` (3.10, 3.11) + `quality` green
- [x] CircleCI: `tests-3.10`, `tests-3.11` green

**Epistemic scope:** the suite verifies implementation contracts, source consistency, provenance propagation, symbolic/musical invariants, and reproducibility — not perceptual adequacy of CDM or correspondence to perceived density/loudness.

## String musicological battery (PR #13)

97 tests across:

- `tests/string_constants.py`
- `tests/test_string_module_contracts.py`
- `tests/test_string_source_reproducibility.py`
- `tests/test_string_musicological_invariants.py`
- `tests/test_string_score_scenarios.py`
- `tests/test_instrument_provenance.py`

Coverage includes: module/table contracts; exact anchor lookup; source workbook reconstruction (local); pitch spelling; Unicode accidentals; enharmonic normalization; cents/microtonal handling; interpolation provenance; GPR diagnostics; organological fixtures; ensemble/MusicXML scenarios; double-bass sounding-pitch via MusicXML transposition; quantity row-splitting; unison/octave/cluster/register/dynamics/event-order invariants.

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

1. **Double-bass table span adjudication:** committed module spans E1–C5 (45 rows). Older documentation listed E1–A3. Confirm whether rows above A3 share the same methodological status as the core arco-sustain corpus or require separate QC.
2. **Technique metadata vs tables:** registry `supported_techniques` may include pizzicato, tremolo, harmonics, mute; CDM tables are arco sustain only.
3. **GPR determinism:** production `GaussianProcessRegressor` instances set explicit `random_state=GPR_RANDOM_STATE` (`0`) via `create_dynamic_gpr()`; output is independent of global `np.random` state and benchmark order. Determinism is numerical repeatability only — not general perceptual or empirical validation.

Resolved by PR #14: viola machine-local `D:\CORDAS\...` provenance path (now portable doc anchor).

## Validation contract layers (symbolic)

- [x] Interval-density formal contracts (`tests/test_densidade_intervalar_contract_additional.py`)
- [x] Instrument-density registry scaffold (`tests/test_instrument_density_registry_scaffold_contract_additional.py`)
- [x] Scientific/musicological output plausibility (`tests/test_scientific_musicological_output_plausibility_additional.py`)
- [x] Excel importer Phase 1a (`tests/test_instrument_profile_excel_importer_additional.py`)
- [x] String musicological battery (PR #13)
- [x] Media note-label normalization (`tests/test_notes.py`, PR #14)

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
