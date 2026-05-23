# Legacy pipeline extraction plan

**Status (2026-05):** The main analytical path is **core-native**. `core/pipeline.py` implements `calculate_metrics`; `data_processor.py` is a backward-compatibility shim re-exporting core symbols. This document records **residual** legacy dependencies and optional future extractions.

---

## Current path (score-only vertical slice)

```
GUI (Main.py)
    → AnalysisController.analyze
        → adapters.gui_adapter.build_analysis_request
            → AnalysisRequest.from_mapping
                → core.pipeline.calculate_metrics
                    → core/pitch_aggregation, core/pitch_structure
                    → core/quantity_scaling, core/source_aggregation
                    → core/orchestration, core/orchestration_mass
                    → densidade_intervalar, spectral_analysis, timbre_texture_analysis
                    → core.metrics_metadata, core.subindices

Scripts / tests
    → core.calculate_metrics  (or AnalysisRequest → pipeline)
    → data_processor.calculate_metrics  (shim → core.pipeline)
```

Temporal analysis: `core.analyze_score` → `core.pipeline.calculate_metrics` per slice.

GUI validation text: `validation.gui_validation.generate_validation_text` (not analytical).

---

## Extraction inventory

### Target: `core/pitch.py` (or extend `core/converters.py`)

| Legacy location | Function / concern |
|-----------------|-------------------|
| `data_processor` | `_normalize_notes_to_sustenido` |
| `microtonal` | Already separate; keep as dependency |

### Target: `core/intervals.py`

| Legacy location | Function |
|-----------------|----------|
| `densidade_intervalar` | `calculate_interval_density`, exponential decay |
| `data_processor` | `calcular_densidade_intervalar_com_cents` |

### Target: `core/density.py`

| Legacy location | Function |
|-----------------|----------|
| `data_processor` | `calcular_densidade_ponderada_normalizada`, refined/total assembly steps |
| `data_processor` | `calcular_densidade_fundida` (legacy alternate blend) |

### Target: `core/spectral_metadata.py`

| Legacy location | Function |
|-----------------|----------|
| `spectral_analysis` | moments, chroma, harmonic ratio |
| `data_processor` | spectral assembly block inside `calculate_metrics` |

### Target: `core/orchestration.py` — **done**

| Status | Function |
|--------|----------|
| **Extracted** | `compute_event_one_player_density`, `compute_slice_orchestral_metrics` |
| **Extracted** | `core/orchestration_mass.py`, `core/quantity_scaling.py`, `core/source_aggregation.py` |

### Target: `core/results.py` — **partial**

| Status | Function |
|--------|----------|
| **Extracted** | `core/formatting.format_output_string` |
| **Extracted** | `validation/gui_validation.generate_validation_text` |
| **Legacy shim** | `data_processor_legacy.save_results` (prefer `score_io.exporters`) |

### Remain as compatibility wrappers

| Module | Role |
|--------|------|
| `data_processor.calculate_metrics` | Shim → `core.pipeline.calculate_metrics` |
| `densidade_intervalar` | Interval compactness (score-derived; candidate for `core/` merge) |
| `statistical_validation.py` | Legacy GUI historical stats — deprecated for research |

---

## Extraction rules (future phases)

1. Move **pure** functions with regression tests first.
2. No formula changes without baseline update.
3. Keep `calculate_metrics` signature and return shape stable.
4. One module per PR; run full test suite + regression baseline each time.
5. Do not import Tkinter into any `core/` module.

---

## Coverage note

Legacy modules with lower coverage (`data_processor.py`, `densidade_intervalar.py`, `xml_loader.py`) should gain tests **during** extraction, not before wholesale moves.

---

*Added: repository-alignment patch (2026-05-20).*
