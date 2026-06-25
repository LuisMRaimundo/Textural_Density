# Constants and assumptions — score-only analysis

Inventory of constants and modelling assumptions for the **systematic score-only symbolic method**. See also programmatic export: `python scripts/export_constants_assumptions.py` → `replication/checksums/constants_and_assumptions.json`.

---

## 1. Pitch assumptions

| Name | Value | Module | Configurable | Role / limitations |
|------|-------|--------|--------------|-------------------|
| `MIDI_BASE_FREQUENCY` | 440.0 Hz | `config.py` | Yes (input) | A4 reference for MIDI→Hz; symbolic, not measured audio |
| `MIDI_BASE_NOTE` | 69 | `config.py` | No | MIDI number for A4 |
| `TAMANHO_OITAVA_MICROTONAL` | 24 | `config.py` | No | Microtonal octave division for notation parser |
| Microtonal cents | ±N cents on note string | `microtonal.py` | Via notation | Continuous pitch offset |
| MusicXML transpose | Applied once before validation/lookup | `xml_loader.py` | Per-part `<attributes>` | Written `<pitch>` + `<transpose>` → sounding |
| `written_pitch` vs `sounding_pitch` | Optional on `InstrumentEvent` | `core/models.py` | Set when MusicXML transpose applies | Metrics use sounding; written retained for errors |

---

## 2. Interval compactness assumptions

| Name | Value | Module | Configurable | Role / limitations |
|------|-------|--------|--------------|-------------------|
| `DEFAULT_LAMBDA` | 0.05 | `config.py` | Yes (input/XML) | Exponential decay over pitch distance |
| Distance unit | Semitones (×2 in decay arg) | `densidade_intervalar.py` | No | Score-derived compactness, not sensory dissonance |

---

## 3. Event density assumptions

| Name | Definition | Module | Notes |
|------|------------|--------|-------|
| Event | One symbolic row in a vertical slice | `core/models.py` | Notes + dynamics + instrument + player count |
| Player weighting | Σ player_count | `core/event_density.py` | Doublings increase weighted count |
| Qty scaling model | Incoherent source addition | `core/quantity_scaling.py` | Mass ∝ qty; pressure-equiv ∝ RSS; not pitch structure |
| Source grouping | (MIDI, instrument, dynamic) | `core/source_aggregation.py` | Row-splitting invariance for mass/RSS |
| Duration weighting | When all events have duration metadata | `core/temporal.py` | Optional temporal weight |

---

## 4. Register assumptions

| Name | Value | Module | Configurable |
|------|-------|--------|--------------|
| `DEFAULT_REGISTER_BANDS` | very_low … very_high MIDI ranges | `config.py` | Yes |
| Pitch span | max−min MIDI semitones in slice | `core/pitch_structure.py` | Derived from **sounding/concert** pitches |
| Registral compression | 1/(1+span) | `core/registral_density.py` | Fixed formula |

---

## 5. Written dynamic assumptions

| Name | Role | Module | Limitation |
|------|------|--------|------------|
| `DYNAMIC_LEVELS` | Allowed symbolic markings | `config.py` | Not SPL |
| Source CDM anchors | Measured sparse table columns | `instrumentos/*.py` | **pp, mf, ff only** |
| Modelled dynamics | GPR-interpolated values | `instrumentos/gpr_dynamic_interpolation.py` | **p, mp, f, pppp…ffff** — not measured |
| `mp` coordinate | Ordinal GPR control between `p` (4.0) and `mf` (5.0) | `gpr_dynamic_interpolation.py` | **4.5** — not dB or perceptual intensity |
| Ordinal weights p…ffff | Symbolic orchestration mass (coarse fallback) | `instrumentos/registry.py` | Not loudness |
| Unknown dynamic | Falls back to `mf` with warning | `core/metrics_metadata.py` | Documented |
| Dynamic monotonicity | **Not assumed** | GPR + source tables | CDM may decrease across dynamics |

Dedicated GPR modules fit a Matérn kernel on pp/mf/ff anchors and predict intermediate dynamics at fixed ordinal coordinates. Interpolation does not create new measured source data.

---

## 6. Instrument / orchestration assumptions

| Name | Role | Module |
|------|------|--------|
| `REGISTRY` profiles | Register, family, dynamic-response metadata | `instrumentos/registry.py` |
| GPR modules (`flute`, `oboe`, `clarinet`, `violin`, `viola`, `cello`, `double_bass`, …) | Sparse note×dynamic CDM tables (externally sourced) | `instrumentos/*.py` |
| `profile_status` | `literature_derived` / `empirical_profile` / `coarse_default` | Audit: `instrumentos/metadata_audit.py` |
| `uncertainty` | low / medium / high | All profiles |
| Unknown instrument | Generic fallback without external acoustic table | `profile_for_event()` |

**Epistemic rule:** instrument density uses **externally obtained acoustic metadata** interpolated by GPR where modules exist. The pipeline does **not** analyse audio at runtime. Written dynamics remain symbolic score markings (not SPL).

---

## 7. Composite assumptions

| Name | Value | Module | Role |
|------|-------|--------|------|
| `MAX_DENS_GLOBAL` | 20.0 | `config.py` | Total density normalization |
| `USE_LOG_COMPRESSION` | True | `config.py` | log10(1+x) on total |
| `COMPOSITE_HARMONIC_DAMPING` | 0.15 | `config.py` | Harmonic ratio adjustment |
| `DEFAULT_WEIGHT_FACTOR` | 0.5 | `config.py` | Instrument vs interval blend |

Weighted density uses a linear min-max blend only (Stevens' Law removed in 3.0.0).

---

## 8. Removed branches

### 3.0.0-strict-symbolic (perceptual)

| Branch | Status |
|--------|--------|
| `use_stevens`, `alpha`, `beta` | **Removed** — raises `InputError` |
| `use_psychoacoustic` | **Removed** — raises `InputError` |
| `use_perceptual_weighting` | **Removed** — raises `InputError` |

### 4.0.0-strict-symbolic (combination-tone / virtual pitches)

| Branch | Status |
|--------|--------|
| `calculate_combination_tones` | **Removed** — raises `InputError` |
| `combination_tones`, `resultant_tones`, `include_resultants`, `include_combination_tones`, `virtual_tones`, `generated_tones` | **Removed** — raises `InputError` |

Spectral summaries use notated/input symbolic pitches only.

---

## Export

```bash
python scripts/export_constants_assumptions.py
```

Validates research defaults exclude all removed keys.
