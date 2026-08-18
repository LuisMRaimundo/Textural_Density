# Plausibility formula-to-code inventory

**Pinned audit commit:** `0bd9d7d` (package 1.1.5; two HARD defects recorded as-is).  
**Pinned fix commit:** `b5e095a` (wrap-around enharmonics + fail-closed unknown-id + SOFT XPASS cleanup).  
**Package after publish checks:** `1.1.6` · methodology `5.1.0-strict-symbolic`.  
**Branch:** `verify/plausibility-battery`.

Formula numbers follow the battery brief (F1–F44). Call sites are production unless marked **non-production**.

---

## Front matter (2026-08-18)

| ID | Construct | Production call sites | Notes |
|---|---|---|---|
| F9 | Instrument density / registry lookup | `instrumentos/registry.py` (`resolve_profile`, `profile_for_event`, `require_registered_instrument`, `get_instrument_module`); `core/converters.py`; `core/score_analysis.py`; `xml_loader.py`; `midi_loader.py`; `adapters/gui_adapter.py` | **Fail-closed:** unknown / withdrawn ids raise `InputError` (`field: instruments`). The error names the MusicXML/MIDI part (`part_id`, `part`) and lists accepted registry ids. The GUI adapter no longer relies on the coarse proxy for unrecognised dropdown states. |
| F14 | Distinct-bin MIDI aggregation (feeds F12–F16 blend) | `core/pitch_aggregation.py` (`note_to_midi_strict`); `core/source_aggregation.py` (`note_to_midi_strict`) | Strict parser only. `Cb5` = B4 = 71; `B#3` = C4 = 60. |

**Non-production (same convention as `compute_registral_compactness`):**

| Symbol | Location | Convention |
|---|---|---|
| `compute_registral_compactness` | `core/pitch_structure.py` | Not on any production path. `calculate_metrics` reports `registral_compression` = `1/(1+span)` instead. |
| `profile_for_event(..., allow_unknown=True)` | `instrumentos/registry.py` | Audit-only. Not reachable from `calculate_metrics`. Serves `_UNKNOWN_PROFILE` for metadata-audit tools. |
| `core.reporting._top_interval_pairs` | `core/reporting.py` | Report-string-only interval labels. Uses `note_to_midi_strict` so wrap-around spellings cannot diverge from F14. Not on the analysis MIDI axis. |

---

## Catalog

| IDs | Family | Primary modules |
|---|---|---|
| F1–F4 | Pitch grammar / tuning | `microtonal.py` (`parse_pitch_strict`, `note_to_midi_strict`) |
| F5–F8, F37 | Interval density | `densidade_intervalar.py`, `core/interval_compactness.py` |
| F9 | Instrument ladders / lookup | `instrumentos/*`, `instrumentos/registry.py` — fail-closed unknown-id rule above |
| F10–F11 | Quantity / sonic mass | `core/source_aggregation.py`, `core/quantity_scaling.py` |
| F12–F16, F42 | Blend / composite | `core/composite.py`; MIDI bins from F14 (`core/pitch_aggregation.py`, `core/source_aggregation.py`) |
| F17, F41 | Absolute density / counts | `core/pipeline.py`, `core/event_density.py` |
| F18–F24 | Spectral | `spectral_analysis.py` |
| F25–F36, F38–F40 | Registral / texture | `core/subindices.py`, `timbre_texture_analysis.py` |
| F43–F44 | Temporal / score I/O | `core/score_analysis.py`, `xml_loader.py`, `midi_loader.py` |

Verification battery: `tests/plausibility/` (one module per family F-A…F-K). Audit: `reports/plausibility_audit_2026-08-18.md`.
