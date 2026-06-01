# API Documentation

**Simultaneity Density Analyser (SDA)** — also known as **Densidade Vertical**

## Documentation suite

| Document | Contents |
|----------|----------|
| [MATHEMATICAL_MANUAL.md](MATHEMATICAL_MANUAL.md) | Formulas, algorithms, tutorial, glossary |
| [TECHNICAL_MANUAL.md](TECHNICAL_MANUAL.md) | Architecture, data flow, worked examples |
| [MIGRATION.md](MIGRATION.md) | Backward compatibility and upgrade notes |
| This file | Function-level API overview |

**Recommended import path for new code:**

```python
from core import calculate_metrics, analyze_score
```

Legacy `from data_processor import calcular_metricas` remains supported and is identical to `calculate_metrics`.

---

## `core` — primary API

### `calculate_metrics(input_data: dict) -> tuple[dict, list[float], list[float]]`

Alias: `calcular_metricas`. Single vertical-slice analysis.

**Required input keys** (equal-length lists):

| Key | Type | Description |
|-----|------|-------------|
| `notes` | `list[str]` | Note names (supports cents, e.g. `C4+50c`) |
| `dynamics` | `list[str]` | Dynamic markings (`pp` … `ffff`) |
| `instruments` | `list[str]` | Instrument name per note |
| `num_instruments` | `list[int]` | Player count per note (≥ 1) |

**Common optional keys:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `weight_factor` | `float` | `0.5` | Blend instrument vs interval density |
| `save_results` | `bool` | `False` | GUI/export flag |
| `show_graphs` | `bool` | `False` | GUI flag |

**Removed keys (3.0.0-strict-symbolic):** `use_stevens`, `alpha`, `beta`, `use_psychoacoustic`, `use_perceptual_weighting` — raise `InputError` if present in analytical input.

**Removed keys (4.0.0-strict-symbolic):** `calculate_combination_tones`, `combination_tones`, `resultant_tones`, `include_resultants`, `include_combination_tones`, `virtual_tones`, `generated_tones` — raise `InputError` if present in analytical input.

**Optional timing keys** (equal length to `notes`, Phase 6):

| Key | Type | Description |
|-----|------|-------------|
| `onsets` | `list[float]` | Start time (seconds) |
| `offsets` | `list[float]` | End time (seconds) |
| `durations` | `list[float]` | Duration (seconds) |
| `part_ids` | `list[str]` | Part identifiers |

**Returns:**

1. **`resultados`** — results dict (see [Output structure](#output-structure))
2. **`densidades_instr`** — per-note instrument densities (aligned with input order)
3. **`pitches`** — MIDI pitches for input notes

**Example:**

```python
from core import calculate_metrics

input_data = {
    "notes": ["C4", "E4", "G4"],
    "dynamics": ["mf", "f", "mf"],
    "instruments": ["flauta", "clarinete", "flauta"],
    "num_instruments": [1, 2, 1],
    "weight_factor": 0.5,
}

resultados, densidades, pitches = calculate_metrics(input_data)
print(resultados["density"]["total"])
print(resultados["metric_metadata"]["metrics"]["density.total"]["source_type"])
```

---

### `analyze_score(source, config=None) -> ScoreAnalysisResult`

Timed score analysis over multiple vertical slices.

**`source`:** one of

- File path (`.xml`, `.mid`, `.midi`)
- Legacy input `dict` (single slice)
- `list[InstrumentEvent]`

**`config`:** optional `AnalysisConfig` or options `dict` (merged with file settings). Temporal mode via `temporal_mode`: `"event_boundary"` (default) or `"instantaneous"`.

**Returns:** `ScoreAnalysisResult` with:

| Field | Type | Description |
|-------|------|-------------|
| `slices` | `list[VerticalSliceAnalysis]` | Per-slice metrics and subindices |
| `time_series` | `list[dict]` | Density summaries over time |
| `global_summary` | `dict[str, MetricResult]` | Aggregates (`slice_count`, min/max/mean total density, …) |
| `warnings`, `assumptions` | `list[str]` | Epistemic notes |
| `config` | `AnalysisConfig` | Resolved options |
| `source_path` | `str \| None` | Path when loaded from file |

**Example:**

```python
from core import analyze_score

result = analyze_score("score.xml")
for entry in result.time_series:
    print(entry["time"], entry.get("density_total"))
```

---

### `load_timed_events_from_path(path) -> tuple[list[InstrumentEvent], dict, list[str]]`

Load timed events from XML or MIDI without running full analysis. Returns `(events, file_options, warnings)`.

---

### Converters (`core.converters`)

| Function | Description |
|----------|-------------|
| `legacy_input_to_vertical_slice(input_data)` | Legacy dict → `VerticalSlice` |
| `vertical_slice_to_legacy_lists(slice)` | `VerticalSlice` → `(notes, dynamics, instruments, counts)` |
| `make_instrument_event(..., written_note=None)` | Build one `InstrumentEvent`; optional written pitch when transposition applies |
| `note_string_to_pitch(note)` | Note string → `Pitch` |
| `analysis_config_from_input(input_data)` | Dict → `AnalysisConfig` |

---

### Temporal (`core.temporal`)

| Function | Description |
|----------|-------------|
| `group_events_into_slices(events, mode="event_boundary")` | Segment timed events into `VerticalSlice` list |
| `normalize_event_timing(events)` | Fill missing offset/duration |
| `resolve_event_offset(event)` / `resolve_event_duration(event)` | Timing helpers |
| `events_have_timing(events)` | Whether any event has onset metadata |

---

### Reporting (`core.reporting`)

| Function | Description |
|----------|-------------|
| `explain_vertical_slice(resultados) -> str` | Short interpretability text |
| `format_interpretability_report(resultados) -> str` | Full text report |
| `run_sensitivity_analysis(input_data, include_lambda=False) -> dict` | Parameter robustness sweep |
| `format_sensitivity_report(sensitivity) -> str` | Format sensitivity results |

Sensitivity analysis is **not** empirical validation.

---

### Metadata and subindices

| Function | Module | Description |
|----------|--------|-------------|
| `attach_metric_metadata(resultados, context)` | `core.metrics_metadata` | Attach `metric_metadata` block |
| `build_metric_metadata(context)` | `core.metrics_metadata` | Build metadata dict |
| `metric_result_to_dict(result)` | `core.metrics_metadata` | Serialize `MetricResult` |
| `attach_density_subindices(resultados, context)` | `core.subindices` | Attach `density_subindices` |
| `build_density_subindices(context)` | `core.subindices` | Build subindices dict |

Normally called internally by `calculate_metrics`; exposed for custom pipelines.

---

### Data models (`core.models`)

| Class | Purpose |
|-------|---------|
| `Pitch` | Symbolic pitch (MIDI, note name, cents) |
| `InstrumentEvent` | One sounding event; optional `written_pitch` when MusicXML transpose applies |
| `VerticalSlice` | Simultaneous events at one moment |
| `AnalysisConfig` | Analysis options |
| `MetricResult` | Scalar metric + epistemic fields |
| `VerticalSliceAnalysis` | Slice + metrics + subindices |
| `ScoreAnalysisResult` | Full timed score analysis |

**Type literals:** `SourceType`, `ValidationStatus`, `ConfidenceLevel` (see [MATHEMATICAL_MANUAL.md](MATHEMATICAL_MANUAL.md) §M).

---

### Output structure

Legacy scalars (unchanged):

```python
resultados["density"]           # interval, instrument, weighted, refined, total, sonic_mass, absolute
resultados["spectral_moments"]
resultados["additional_metrics"]  # complexity, harmonic_ratio, chroma_vector
resultados["texture"]
resultados["timbre"]
resultados["orchestration"]
resultados["input_data"]
resultados["pitch_aggregation"]   # event/player counts, pitch_polyphony, pitch bins
resultados["quantity_scaling"]    # incoherent source-addition model metadata
```

Additive blocks (Phases 3–5):

```python
resultados["metric_metadata"]     # epistemic labelling per metric
resultados["density_subindices"]  # interpretable decomposition
```

**GUI entry (approved):** `AnalysisController.analyze(gui_input_dict)` builds
`AnalysisRequest` via `adapters.gui_adapter.build_analysis_request`, then calls
`core.pipeline.calculate_metrics`. GUI code must not import `data_processor` for analysis.

---

## `validation` — verification framework

```python
from validation import run_verification_suite, generate_validation_report
from validation.metrics import spearman_correlation, kendall_tau, root_mean_square_error
```

| Function | Description |
|----------|-------------|
| `run_verification_suite() -> VerificationResult` | Synthetic cases + property checks |
| `generate_validation_report(verification=None, output_path=None) -> str` | Markdown report |
| `all_synthetic_cases()` | List of `SyntheticCase` fixtures |
| `load_expert_annotations(path) -> list[ExpertAnnotation]` | Load expert JSON |
| `spearman_correlation(x, y)` | Correlation statistic |
| `kendall_tau(x, y)` | Kendall τ |
| `root_mean_square_error(pred, obs)` | RMSE |
| `mean_absolute_error(pred, obs)` | MAE |
| `bootstrap_ci(values, ...)` | Bootstrap confidence interval |

**Not** the same as `generate_validation_text` (GUI historical-stats formatter in `data_processor`).

---

## `instrumentos` — registry and modules

```python
from instrumentos import get_instrument_module, get_instrument_profile, resolve_profile
from instrumentos.registry import list_instrument_ids, list_profiles
```

| Function | Description |
|----------|-------------|
| `get_instrument_module(name)` | Resolve module for instrument (dedicated → coarse → fallback) |
| `get_instrument_profile(name) -> InstrumentProfile` | Profile metadata including `profile_status` |
| `resolve_profile(name) -> InstrumentProfile \| None` | Lookup by name/alias |
| `list_instrument_ids()` | All registered instrument IDs (~28) |
| `list_profiles()` | All `InstrumentProfile` objects |

Each instrument module must implement:

- `calcular_densidade(nota: str, dinamica: str) -> float`
- `predict_intermediate_dynamics(pitches, pp, mf, ff) -> dict`

See [instrumentos/README.md](../instrumentos/README.md).

---

## `data_processor` — backward-compatibility shim

Re-exports `core.pipeline.calculate_metrics` and legacy GUI helpers (`save_results`, `generate_validation_text`, …). **New code should import from `core`.**

| Function | Description |
|----------|-------------|
| `calculate_metrics` / `calcular_metricas` | Delegates to `core.pipeline` |
| `calcular_densidade_ponderada_normalizada(...)` | Delegates to `core.composite` |
| `calcular_massa_sonora(...)` | Delegates to `core.orchestration_mass` |
| `load_instrument_module(name)` | Delegates to `instrumentos.get_instrument_module` |
| `format_output_string(resultados) -> str` | Delegates to `core.formatting` |
| `generate_validation_text(resultados_validacao, num_historico) -> str` | GUI validation summary text |

---

## `xml_loader` — score file intake

```python
from xml_loader import parse_xml, parse_xml_to_events, note_string_to_gui_parts
```

| Function | Description |
|----------|-------------|
| `parse_xml(filepath) -> dict` | Custom `<densidade_analysis>` or MusicXML → legacy input dict. MusicXML notes are **concert pitch** after `<transpose>`. |
| `parse_xml_to_events(filepath) -> (events, options, warnings)` | Typed `InstrumentEvent` list; sets `written_pitch` when transposition applies. |
| `note_string_to_gui_parts(note_str)` | GUI field helper `(base, octave, cents)` |

**MusicXML transposition:** Per-part `<attributes><transpose>` with `<chromatic>` and optional `<octave-change>`. See [TECHNICAL_MANUAL.md §7.4](TECHNICAL_MANUAL.md#74-musicxml-loading-and-transposition).

**Warnings:** Untimed MusicXML → single vertical slice; transpose applied → concert-pitch warning.

---

| Function | Module | Description |
|----------|--------|-------------|
| `write_results_json(resultados, path)` | `score_io.exporters` | Export results to JSON |

---

## Utility modules

### `microtonal` / `utils.notes`

- `note_to_midi(note) -> float`
- `midi_to_hz(midi) -> float` / `midi_to_frequency`
- `hz_to_midi(freq) -> float`
- `converter_para_sustenido(note) -> str`

### `densidade_intervalar`

- `calculate_interval_density(pitches, lamb=...)`
- `calculate_interval_density_normalized(pitches, lamb=...)`
- `modified_exponential_decay(delta, lamb)`
- `calibrate_lambda(experimental_data)` / `load_calibrated_parameters()`

### `spectral_analysis`

- `calculate_spectral_moments` / `calculate_extended_spectral_moments`
- `calculate_chroma_vector`
- `calculate_harmonic_ratio`

---

## Configuration (`config.py`)

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_DENS_GLOBAL` | `20.0` | Total-density normalisation divisor |
| `USE_LOG_COMPRESSION` | `True` | Apply `log10(1+x)` to total density |
| `COMPOSITE_HARMONIC_DAMPING` | `0.15` | Harmonic-ratio damping in composite |
| `DEFAULT_REGISTER_BANDS` | dict | Register bands for subindices |
| `DYNAMIC_LEVELS` | tuple | Supported dynamics |
| `DEFAULT_LAMBDA` | `0.05` | Interval decay default |

Calibrated λ: `config/density_params.json`.

---

## GUI entry points

| Command | Description |
|---------|-------------|
| `python Main.py` | Tkinter GUI |
| `python run.py` | Launcher (sets cwd) |
| `densidade-vertical` | Console script after `pip install -e .` |

---

**Package version:** 1.1.1 · **Last updated:** 2026-06-01
