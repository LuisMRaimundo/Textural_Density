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
| Committed ladder cells | Exact `spectral_data` lookup | `instrumentos/*.py` | Must include requested dynamic |
| Full ordinary-sustain ladders | 10 dynamics from Dynamics_predicter `Results` | `violin`/`viola`/`cello`/`double_bass`/`flute`/`clarinet`/`bassoon`/`oboe` | Non-anchor cells workbook-modelled, not lab-measured |
| Sparse modules (migration) | Still pp/mf/ff only until ladders committed | trumpet, techniques, … | Missing cell → `MissingCommittedDynamicError` |
| Ordinal weights p…ffff | Symbolic orchestration mass (coarse fallback) | `instrumentos/registry.py` | Not loudness |
| Unknown dynamic | Falls back to `mf` with warning | `core/metrics_metadata.py` | Documented |
| Dynamic monotonicity | **Not assumed** | source tables | CDM may decrease across dynamics |

**Production rule (2026-08-03):** no runtime GPR / adaptive-tail fill-in. `calcular_densidade` reads committed cells only. Legacy code: `tools/legacy_gpr_dynamic_interpolation.py`.

**Technique modules:** violin harmonics (`violin_art_harm`, `violin_nat_harm`) and most technique tables still commit sparse pp/mf/ff until full ladders are supplied.

---

## 6. Instrument / orchestration assumptions

| Name | Role | Module |
|------|------|--------|
| `REGISTRY` profiles | Register, family, dynamic-response metadata | `instrumentos/registry.py` |
| Table-backed modules (`flute`, `oboe`, `clarinet`, `bassoon`, `trumpet`, strings, percussion, …) | Note×dynamic CDM tables (externally sourced; ordinary-sustain winds/strings listed above = full ladder) | `instrumentos/*.py` |
| `profile_status` | `literature_derived` / `empirical_profile` / `coarse_default` | Audit: `instrumentos/metadata_audit.py` |
| `uncertainty` | low / medium / high | All profiles |
| Unknown instrument | Generic fallback without external acoustic table | `profile_for_event()` |

**Epistemic rule:** instrument density uses **externally obtained acoustic metadata** looked up from committed tables where modules exist. The pipeline does **not** analyse audio at runtime and does **not** invent missing dynamics. Written dynamics remain symbolic score markings (not SPL).

---

## 7. Composite assumptions

| Name | Value | Module | Role |
|------|-------|--------|------|
| `MAX_DENS_GLOBAL` (REF) | **193.0** | `config.py` | Fixed composite reference in $\log_{10}(1+D_{\mathrm{blend}}\sqrt{M}/\mathrm{REF})$. Task 8c re-freeze: chosen so frozen all-pitched baselines keep pre-unification order of magnitude (match ≈192.6→193). Traceability: `CHANGES.md` “Task 8c”. **Not** Qty or table size. |
| `USE_LOG_COMPRESSION` | True | `config.py` | log10(1+x) on composite |
| `COMPOSITE_HARMONIC_DAMPING` | 0.15 | `config.py` | Harmonic ratio adjustment in $D_{\mathrm{pitch}}$ (reported axis; not the composite product) |
| `DEFAULT_WEIGHT_FACTOR` ($w$) | 0.5 | `config.py` / `core.defaults` | Instrument vs interval blend inside $D_{\mathrm{blend}}$ |

**Unified composite (Task 8c):** one formula for pitched, unpitched, and mixed slices — $D_{\mathrm{blend}}=\texttt{density.weighted}=w\cdot(D_{\mathrm{inst}}/10)+(1-w)\cdot D_{\mathrm{int}}$ (defaults), then mass boost / REF. Display strings from `core.composite` only. No unpitched-only fallback. Traceability: `CHANGES.md`.
| `DYN_TAIL_SHRINK` ($\gamma$) | **0.5** | `config.py` | Geometric shrink for register-adaptive saturating dynamic tails (5.1.0); whole tail ≤ one measured step |
| `DENSITY_FLOOR` | $10^{-9}$ | `config.py` | Unreachable safety assert on saturated tail amplitudes (not a silent clamp) |

Weighted density uses a linear min-max blend only (Stevens' Law removed in 3.0.0). Pitch-structure density is the **extensive** raw pairwise sum $S$ (5.0.0); registral-span damping is **not** applied in the aggregate.

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
