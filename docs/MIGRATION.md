# Migration Guide — Textural Density

This document helps users and integrators move from pre-upgrade scripts (flat `data_processor` imports, GUI-era assumptions) to the current **Textural Density** architecture (Phases 0–12).

**Related docs:** [Technical Manual](TECHNICAL_MANUAL.md) · [Mathematical Manual](MATHEMATICAL_MANUAL.md) · [API](API.md) · [Versioning & license](VERSIONING.md)

---

## 1. Summary

| Area | Status |
|------|--------|
| Legacy input dict (`notes`, `dynamics`, …) | **Supported** — unchanged required keys |
| Return tuple `(resultados, densidades_instr, pitches)` | **Supported** |
| `resultados["density"]` scalar keys | **Supported** — same names (`interval`, `instrument`, `weighted`, `refined`, `total`, `sonic_mass`, `absolute`) |
| `calcular_metricas` alias | **Supported** — identical to `calculate_metrics` |
| `from data_processor import calculate_metrics` | **Supported** — still works |
| New output blocks | **Additive only** — `metric_metadata`, `density_subindices` |
| GUI (`Main.py`, `python run.py`) | **Supported** — entry point unchanged |
| Per-event instrument density | **Behavior change** — see §4.1 |
| `calculate_combination_tones` and related keys | **Removed (4.0.0-strict-symbolic)** — analytical input raises `InputError` |
| Stevens' Law / `use_stevens`, `alpha`, `beta` | **Removed (3.0.0-strict-symbolic)** — analytical input raises `InputError` |
| `use_psychoacoustic` | **Removed (3.0.0-strict-symbolic)** — analytical input raises `InputError` |
| `use_perceptual_weighting` | **Removed (3.0.0-strict-symbolic)** — analytical input raises `InputError` |
| Saved GUI/XML preferences with removed keys | **Migrated** — keys stripped with warning; not passed to pipeline |
| Expert score validation | **New scaffolding** — `validation/score_annotations/` (status: `verified_only`) |
| Replication package | **New** — `replication/` with synthetic fixture + frozen outputs |
| MusicXML `<transpose>` → concert pitch | **New (1.1.1)** — `xml_loader.py`; `written_pitch` on events when applicable |

**Epistemic note:** All metrics remain score/symbolic outputs. New metadata labels clarify which values are **metadata proxies**, not measured acoustics.

**Consolidation (4.0.0):** Earlier versions included optional perceptual/acoustic proxy branches (Stevens' Law, psychoacoustic corrections, perceptual interval weighting, combination tones). These have been removed to keep the project strictly symbolic and methodologically coherent.

---

## 2. Recommended import paths

### Before (still valid)

```python
from data_processor import calcular_metricas

resultados, densidades, pitches = calcular_metricas(input_data)
total = resultados["density"]["total"]
```

### After (recommended for new code)

```python
from core import calculate_metrics, analyze_score

resultados, densidades, pitches = calculate_metrics(input_data)
total = resultados["density"]["total"]

# GUI path (Main.py) uses gui.analysis_adapter.calculate_from_gui — same pipeline + metadata
```

Both paths call the same implementation. `core` re-exports via `core/pipeline.py` and adds typed models, temporal analysis, validation, and reporting without requiring Tkinter.

---

## 3. Backward-compatible additions (opt-in to read)

These keys are **appended** to `resultados` and do not alter legacy scalar values when options match the regression baseline.

### 3.1 `metric_metadata` (Phase 3)

Epistemic labelling for every density metric:

```python
meta = resultados["metric_metadata"]["metrics"]["density.total"]
print(meta["source_type"])        # e.g. "metadata_proxy"
print(meta["validation_status"])  # e.g. "heuristic"
print(meta["warnings"])           # list of strings
```

Legacy code that ignores unknown keys continues to work.

### 3.2 `density_subindices` (Phase 5)

Interpretable decomposition (event count, registral spread, composite components, etc.):

```python
sub = resultados["density_subindices"]
print(sub["composite"]["components"]["cohesion_factor"])
```

### 3.3 Optional timing fields on input (Phase 6)

Existing parallel-list input accepts **optional** equal-length lists:

| Key | Type | Purpose |
|-----|------|---------|
| `onsets` | `list[float]` | Event start time (seconds) |
| `offsets` | `list[float]` | Event end time (seconds) |
| `durations` | `list[float]` | Event duration (seconds) |
| `part_ids` | `list[str]` | Part identifiers |

Omitting these preserves single-slice behaviour. For full temporal analysis, prefer `analyze_score(path)` or pass a `list[InstrumentEvent]`.

---

## 4. Intentional behavior changes

### 4.1 Per-event instrument modules (Phase 2)

**Before:** Documentation stated the first instrument in the list was used for all notes.

**Now:** Each note uses **its own** instrument module via `core/orchestration.py` and `instrumentos/registry.py`.

**Impact:** `density.instrument`, per-note `densidades_instr`, and derived totals may **differ** from pre-Phase-2 runs when notes used different instruments. Interval density is unchanged.

**Action:** Re-baseline any saved golden values that assumed a single instrument module. Reference fixture: `tests/fixtures/regression_baseline.json`.

### 4.2 Combination-tone analysis removed (4.0.0-strict-symbolic)

**Before:** Optional combination-tone / resultant-tone analysis could be enabled with `calculate_combination_tones=True`. Virtual pitches were merged into spectral and density calculations.

**Now:** Textural Density is strictly symbolic. Combination-tone analysis is **hard-removed**. Keys such as `calculate_combination_tones`, `combination_tones`, `resultant_tones`, `include_resultants`, `include_combination_tones`, `virtual_tones`, and `generated_tones` raise `InputError` if present in analytical input.

**Impact:** Total density, spectral moments, chroma, harmonic ratio, registral span, and related metrics are computed from **notated/input symbolic pitches only**.

**Action:** Remove combination-tone keys from scripts and notebooks. Saved GUI/XML preferences containing these keys are stripped with a migration warning and are not passed to the calculation pipeline.

### 4.3 Unknown instruments → coarse proxy (Phase 7)

Unregistered instrument names resolve to `instrumentos/coarse_default.py` with warnings in `metric_metadata`. Densities remain finite but carry `confidence: low` and `profile_status: coarse_default`.

**Action:** Register instruments in `instrumentos/registry.py` or accept proxy warnings in research output.

### 4.4 Lambda calibration dyad fix (Phase 4)

`calibrate_lambda()` now builds dyads with `utils/notes.dyad_notes_from_semitone_interval()`. Stored `config/density_params.json` value (`lambda: 0.05`) is unchanged; **re-run calibration** only if you depend on newly fitted λ from the corrected routine.

---

## 5. Naming disambiguation

| Name | Module | Purpose |
|------|--------|---------|
| `calculate_metrics` / `calcular_metricas` | `data_processor`, `core` | Main vertical-slice pipeline |
| `generate_validation_text` | `data_processor`, `core` | **GUI** historical-stats text formatter |
| `run_verification_suite` | `validation` | Synthetic/property verification (Phase 8) |
| `generate_validation_report` | `validation` | Markdown verification report |
| `statistical_validation` | top-level module | Legacy GUI plotting — **deprecated**; emits `DeprecationWarning`. Use `validation/` for research. |

Do not replace `generate_validation_text` calls with `generate_validation_report`; they serve different roles.

---

## 6. Output key reference

### Unchanged (read these as before)

```python
resultados["density"]["interval"]
resultados["density"]["instrument"]
resultados["density"]["weighted"]
resultados["density"]["refined"]
resultados["density"]["total"]
resultados["density"]["sonic_mass"]
resultados["density"]["absolute"]
resultados["spectral_moments"]
resultados["additional_metrics"]
resultados["texture"]
resultados["timbre"]
resultados["orchestration"]
resultados["input_data"]          # echo of options used
```

**Removed output keys (4.0.0):** `combination_tones`, `combination_tone_candidates`, and related virtual-tone metadata are no longer produced.

### Common mistake

The README quick-start once showed `resultados['densidade']['total']` — the correct key is **`density`** (English), not `densidade`.

---

## 7. Migration checklist

Use this when updating external scripts, notebooks, or thesis code:

- [ ] Switch imports to `from core import calculate_metrics` (optional but recommended)
- [ ] Confirm access uses `resultados["density"]`, not `densidade`
- [ ] Remove any `calculate_combination_tones` or related keys from analytical input (they now raise errors)
- [ ] Re-baseline instrument/total density if chords mixed multiple instruments
- [ ] After quantity-scaling updates: refresh frozen outputs if `density.instrument` or `density.sonic_mass` drift (see `tests/snapshots/MIGRATION.md`)
- [ ] Optionally consume `metric_metadata` / `density_subindices` for publication-ready labelling
- [ ] For timed scores, evaluate `analyze_score()` instead of manual looping
- [ ] For verification, use `validation.run_verification_suite()` — not GUI `statistical_validation`
- [ ] Run `pytest tests/test_regression_baseline.py` after any local formula edits

---

## 8. Regression baseline

Golden values for the canonical four-note slice are locked in:

- **Fixture input:** `tests/test_regression_baseline.py` → `baseline_input_data`
- **Expected values:** `tests/fixtures/regression_baseline.json`

Re-capture the JSON **only** after intentional formula changes:

```bash
pytest tests/test_regression_baseline.py -v
# If intentional change: update regression_baseline.json and document in _meta
```

Current baseline `_meta.phase2_note` documents the per-event instrument update.

---

## 11. Quantity (Qty) scaling — incoherent source addition

**Breaking change (intentional):** numeric values for `density.instrument` and `density.sonic_mass` changed when Qty > 1.

| Quantity | Old (removed) | New |
|----------|---------------|-----|
| Per-event density | $d \sqrt{n}$ then summed | One-player $d^{(1)}$ only |
| Sonic mass | $\sum d\sqrt{n} \cdot g(\mathrm{dyn}) \cdot n$ (≈ $d \cdot n^{3/2}$) | $\sum n \cdot d^{(1)}$ (linear) |
| Instrument density (slice) | Sum of per-event $\sqrt{n}$ terms | RSS $\sqrt{\sum n (d^{(1)})^2}$ |

**Unchanged semantics:** Qty still does not create pitch-structure events. Row-splitting invariance: one row Qty=N ≡ N rows Qty=1.

**Refresh:** `tests/fixtures/regression_baseline.json`, `tests/snapshots/`, benchmark `expected_outputs/`, `replication/outputs_frozen/json/`.

See also: `tests/snapshots/MIGRATION.md`, `core/quantity_scaling.py`.

**Qty semantics sign-off:** [`docs/qa_checklist.md`](qa_checklist.md), [`score_only_90_readiness_checklist.md`](score_only_90_readiness_checklist.md) §F.

---

## 9. GUI and packaging

| Entry | Status |
|-------|--------|
| `python Main.py` | Unchanged |
| `python run.py` | Unchanged |
| `densidade-vertical` (after `pip install -e .`) | Unchanged |
| `build_exe.py` / PyInstaller | Unchanged |

Analytical code in `core/` and `validation/` does **not** import Tkinter at module load time; the GUI remains in `Main.py`, `gui_components.py`, and `gui/`.

---

## 10. Version map (upgrade phases)

| Phase | User-visible change |
|-------|---------------------|
| 0 | Regression baseline tests |
| 1 | `core` package shim; GUI/core separation |
| 2 | Per-event instruments; typed `VerticalSlice` |
| 3 | `metric_metadata` on all results |
| 4 | λ calibration dyad fix |
| 5 | `density_subindices` |
| 6 | `analyze_score`, MIDI/XML timing, temporal modes |
| 7 | Instrument registry + coarse fallback |
| 8 | `validation/` verification framework |
| 9 | `core/reporting` interpretability + sensitivity |
| 10 | CI quality gates, coverage, mypy on core |
| 11 | Manuals updated (`MATHEMATICAL_MANUAL`, `TECHNICAL_MANUAL`) |
| 12 | This migration guide |
| 13 | MusicXML transpose → concert pitch; benchmark excerpts `003`–`005`; docs/CI alignment (1.1.1) |

---

## 12. MusicXML transposition (1.1.1)

**Before:** MusicXML `<pitch>` was read as sounding pitch. Transposing parts (clarinet in B♭, horn in F, …) could produce incorrect interval/register metrics unless the file was pre-transposed.

**Now:** `xml_loader` reads `<attributes><transpose>` per part and converts to concert pitch:

- `parse_xml` → `notes` list uses **sounding** MIDI/note strings.
- `parse_xml_to_events` → `InstrumentEvent.sounding_pitch` (analysis) and optional `written_pitch` (provenance).

No migration required for custom `<densidade_analysis>` XML or manual GUI entry. Re-run benchmarks if you relied on untransposed MusicXML for orchestral scores.

See [TECHNICAL_MANUAL.md §7.4](TECHNICAL_MANUAL.md#74-musicxml-loading-and-transposition).

---

## 11. Getting help

- **Formulas:** [MATHEMATICAL_MANUAL.md](MATHEMATICAL_MANUAL.md)
- **Architecture:** [TECHNICAL_MANUAL.md](TECHNICAL_MANUAL.md)
- **Function signatures:** [API.md](API.md) *(may lag `core` — prefer `core.__all__` and docstrings)*
- **Tests as specification:** `tests/test_regression_baseline.py`, `tests/test_quality_gates.py`

---

*Last updated: 2026-06-01 (1.1.1 — MusicXML transpose, documentation alignment).*
