# QA checklist — release and formula migrations

Use alongside [`score_only_90_readiness_checklist.md`](score_only_90_readiness_checklist.md).

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

## Frozen outputs (when formulas change)

- [ ] Update `tests/fixtures/regression_baseline.json`
- [ ] Update `tests/snapshots/numeric_outputs/` and document in `tests/snapshots/MIGRATION.md`
- [ ] Run `python benchmarks/scripts/freeze_outputs.py`
- [ ] Run `python replication/scripts/reproduce_metrics.py` and `compare_to_frozen_outputs.py`

## Replication benchmark checklist

- [ ] Manifest license fields valid
- [ ] Frozen numeric outputs match after intentional changes
- [ ] Qty semantics sign-off (above) completed for any mass/density formula change
