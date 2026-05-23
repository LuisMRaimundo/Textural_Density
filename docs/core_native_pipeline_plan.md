# Core-native pipeline extraction plan



**Status:** Core-native — `calculate_metrics` lives in `core/pipeline.py`. `data_processor.py` is a backward-compatible shim (legacy helpers + re-exports).



## Target audit path



```

score input → vertical slices → score-derived subindices → composite symbolic density → report

```



All steps are auditable inside `core/` without GUI-era internals.



## Inventory (current)



| Function / area | Location | Category | Tests | Risk | Order |

|-----------------|----------|----------|-------|------|-------|

| `legacy_input_to_vertical_slice` | `core/converters.py` | score-derived | `test_converters`, regression | low | ✅ done |

| `compute_event_density` | `core/event_density.py` | score-derived | `test_event_density`, axioms | low | ✅ done |

| `compute_interval_compactness` | `core/interval_compactness.py` | score-derived | `test_core_extraction`, axioms | low | ✅ done |

| `register_band_occupancy`, `compute_registral_density` | `core/registral_density.py` | score-derived | `test_core_extraction`, axioms | low | ✅ done |

| `analyze_composite_weight_sensitivity` | `core/sensitivity.py` | diagnostic | `test_export_and_sensitivity` | low | ✅ done |

| `export_constants_and_assumptions` | `core/export_constants.py` | metadata | `test_export_and_sensitivity` | low | ✅ done |

| `compute_orchestration_mass` | `core/orchestration_mass.py` | score-derived | `test_core_extraction`, axioms | low | ✅ done |

| `compute_weighted_density_normalized` | `core/composite.py` | score-derived | `test_core_extraction` | medium | ✅ done |

| `build_construct_records` | `core/construct_metadata.py` | epistemic | `test_construct_metadata` | low | ✅ done |

| `build_density_subindices` | `core/subindices.py` | score-derived | `test_subindices` | medium | ✅ done |

| `build_metric_metadata` | `core/metrics_metadata.py` | epistemic | `test_metric_metadata` | medium | ✅ done |

| `calculate_metrics` | `core/pipeline.py` | score-derived | regression, integration | **high** | ✅ done |

| `format_output_string` | `core/formatting.py` | reporting | `test_data_processor` | low | ✅ done |

| `calcular_densidade_ponderada_normalizada` | shim → `core/composite.py` | score-derived | regression | medium | ✅ done |

| Instrument density GPR | per-instrument modules | symbolic metadata | `test_instrument_registry` | medium | 4 |

| Combination tones | *(removed 4.0.0)* | — | rejection tests | n/a | deleted |

| Psychoacoustic corrections | *(removed 3.0.0)* | — | rejection tests | n/a | deleted |

| GUI formatting / plots | `Main.py`, `gui_components.py` | GUI-era | `test_gui_alignment` | n/a | never in core |

| GUI typed adapter | `gui/types.py`, `gui/analysis_adapter.py` | GUI boundary | `test_core_gui_separation` | low | ✅ done |

| Temporal grouping | `core/temporal.py` | score-derived | `test_score_analysis` | low | ✅ done |

| Score file loading | `core/score_analysis.py` | score-derived | `test_score_analysis` | low | ✅ done |



## Proposed target modules



```

core/

  models.py              ✅ exists

  pitch.py               (extract from microtonal/utils — future)

  score_events.py        (alias/wrapper over converters — future)

  slicing.py             (temporal.py rename/split — future)

  event_density.py       ✅ done

  interval_compactness.py ✅ done (wrapper, no formula change)

  registral_density.py   ✅ done (shared with subindices)

  orchestration_mass.py  ✅ done

  timbral_orchestration.py (future)

  temporal_density.py    (future — temporal.py partial)

  composite.py           ✅ weighted blend + metadata

  construct_metadata.py  ✅ construct_records hooks

  sensitivity.py         ✅ diagnostic weight sensitivity

  export_constants.py    ✅ constants inventory export

  pipeline.py            ✅ calculate_metrics (canonical)

  formatting.py          ✅ format_output_string

  results.py             (future)

  config.py              defaults.py + models.AnalysisConfig ✅



data_processor.py        shim: re-exports + legacy helpers (save_results, validation text)

gui/

  types.py               ✅ TypedDict boundaries

  analysis_adapter.py    ✅ calculate_from_gui → core only

```



## Removed legacy branches (hard removal)



- Stevens' Law, psychoacoustic corrections, perceptual interval weighting (3.0.0)

- Combination-tone / virtual-tone generation (4.0.0)



No reintroduction via `legacy/` adapters without an explicit project decision and full test/doc update.



## Extraction rules



1. No formula changes without regression tests.

2. One low-risk module per patch when tests exist.

3. Backward-compatible wrappers for public functions.

4. ~~Do not claim extraction complete while `data_processor.calculate_metrics` remains the implementation.~~ **Satisfied** — implementation is in `core/pipeline.py`.



## Completed in systematic score-only upgrade (latest)



- `core/pipeline.py` — canonical `calculate_metrics` / `calcular_metricas`

- `core/formatting.py` — `format_output_string`

- `gui/types.py` — typed GUI input/result boundaries

- `data_processor.py` slimmed to shim + legacy-only helpers



## Next safe extractions



1. `core/temporal_density.py` — temporal subindex assembly from `core/temporal.py`

2. Move `generate_validation_text` to a GUI or reporting module (optional)

3. `core/orchestration_mass.py` slice wrapper using `core/orchestration.py`


