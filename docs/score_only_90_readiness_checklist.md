# Score-Only 90+ Readiness Checklist

Practical checklist for **systematic score-only symbolic analysis**. See [`score_only_upgrade_rubric.md`](score_only_upgrade_rubric.md) (v2.0.0).

---

## A. Already aligned

- [x] Strict-symbolic defaults (Stevens/psycho/perceptual weighting removed; combination-tone analysis removed in 4.0.0)
- [x] Report metadata: `score_only_mode`, config/input hashes, validation status
- [x] Formal axioms documented (`docs/formal_construct_axioms.md`)
- [x] Property tests for key axioms (`tests/test_formal_construct_axioms.py`)
- [x] Benchmark manifest with honest corpus gap (`replication/benchmark_manifest.json`)
- [x] Constants/assumptions documentation + export script
- [x] Composite weight sensitivity (diagnostic, `core/sensitivity.py`)
- [x] Instrument metadata audit module + docs
- [x] Partial core extraction: interval compactness, registral density, orchestration mass, composite blend
- [x] Construct-level metadata hooks (`construct_records` in results)
- [x] Benchmark intake scaffolding (`replication/corpus/intake/`, `scan_benchmark_intake.py`)
- [x] Formal verification scaffolding (regression tests, synthetic verification cases)
- [x] Replication scaffolding (`replication/`, compare scripts, synthetic frozen output)
- [x] Upgrade rubric and scoring helper (v2.0.0 — systematic line)
- [x] Automated test suite passing

**Systematic validation status:** `verified_by_tests` for many constructs; **not** `corpus_replicated` until representative benchmark exists.

---

## B. Still required for 90+

- [x] Layered snapshot regression (`tests/snapshots/numeric_outputs`, `metadata_outputs`)
- [x] Licensed benchmark excerpts (`benchmarks/corpus/`, frozen `expected_outputs/`)
- [x] Strict `AnalysisRequest` typed boundary (`core/request.py`, `adapters/`)
- [x] Instrument acoustic provenance (`instrumentos/provenance.py`, `INSTRUMENT_SOURCE`)
- [x] `data_processor.py` reduced to compatibility shim (`data_processor_legacy.py` for helpers)
- [x] Composite dependency trace (`composite_trace` in pipeline output)
- [ ] Frozen outputs from licensed/representative benchmark corpus
- [ ] Reproduction scripts for thesis/research tables on representative corpus
- [x] Core-native pipeline extraction (`calculate_metrics` in `core/pipeline.py`; `data_processor` is a backward-compat shim)
- [x] Typed GUI adapter boundary (`gui/types.py`, `gui/analysis_adapter.py` → `adapters/gui_adapter.py` → `core` only)
- [x] GUI analysis path audited: `Main.py` → `AnalysisController` → adapter → `AnalysisRequest` → `core.pipeline` (see `tests/test_gui_architecture.py`)
- [ ] Optional: report integration for composite weight sensitivity section

---

## F. Qty semantics sign-off

Verify before release or formula migration:

- [x] **Qty represents player/instrument count, not additional pitch events.**
- [x] **Qty affects `player_count` and orchestral/sonic mass** (linear mass; RSS pressure-equivalent instrument density).
- [x] **Qty does not affect** `distinct_pitch_count`, interval-pair count, spectral entropy, registral span, chroma classes, or pitch polyphony.
- [x] **Row-splitting invariance:** one row with Qty = N ≡ N identical rows with Qty = 1 for player-count, mass, and pressure-equivalent instrument density.
- [x] **No metric scales as Qty^(3/2).**
- [x] **Dynamics applied exactly once** (instrument-module lookup; no second multiplier in mass).
- [x] **GUI labels** distinguish event count, player count, pitch polyphony, and orchestral mass.

Regression: `tests/test_quantity_scaling.py`, `tests/test_gui_architecture.py`.

Module reference: `core/quantity_scaling.py`, `core/source_aggregation.py`.

---

## C. Optional empirical extensions

**Not required** for the systematic score-only line. Useful only if the research question shifts toward **perception or expert-judgment prediction**:

- [ ] Expert score annotations
- [ ] Inter-rater reliability
- [ ] Correlation with human ratings
- [ ] Listening tests
- [ ] Psychoacoustic calibration studies

---

## D. Red lines

The project must **not** claim:

- audio analysis or waveform processing  
- measured spectral density  
- hearing-model validity (main line)  
- **90+** from scaffolding or synthetic corpus alone  
- **90+** requires expert ratings or listening tests  
- written dynamics as loudness or SPL  
- instrument profiles as **full** measured spectra or live audio analysis without empirical data  
- methodological invalidity **solely** because external ratings are absent  

---

## E. Next concrete upgrade targets

1. Add first **representative licensed MusicXML** benchmark excerpt to `replication/corpus/intake/`.
2. Complete manifest metadata and set `include_in_official_benchmark: true` with valid license.
3. Freeze JSON/CSV outputs; verify `compare_to_frozen_outputs.py`.
4. ~~Extract remaining `calculate_metrics` assembly into `core/pipeline.py` (regression-guarded).~~ **Done** — `data_processor` re-exports from core.

```bash
python validation/scripts/score_upgrade_rubric.py docs/examples/score_only_rubric_scores_example.json
```
