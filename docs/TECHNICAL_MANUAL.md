# Technical Manual: Textural Density

This document is a comprehensive, pedagogical technical manual for **Textural Density**. It bridges high-level design and low-level mathematical implementation.

> **PDF:** `docs/TECHNICAL_MANUAL.pdf` is an archival snapshot from the 2026-05-23 initial import (`a439f2c`) and predates later alignment commits. This `.md` file is the source of truth.

**Math formatting:** All formulas use **LaTeX** — inline math in `$...$`, display math on **separate lines** as `$$` … `$$` (StackEdit, Stack Exchange MathJax, KaTeX, GitHub, VS Code Markdown Math). Use `\cdot`, `\times`, or `\log_{10}(1+x)`; avoid bare Unicode operators inside expressions.

**Epistemic premise (strictly symbolic):** Score/information input only — no audio waveforms, no measured spectra, no auditory perception model, no FFT/STFT signal processing, no Spectral_Analyser-style live analysis, no EWSD/H/I/S constructs. Textural Density computes analytical density indices from notated/input symbolic events and symbolic metadata only. It does not generate non-notated virtual pitches (including combination or resultant tones) and does not implement acoustic, psychoacoustic, or perceptual modelling. Dynamics are symbolic score markings, not SPL. See [revised_path_to_90_score_only.md](revised_path_to_90_score_only.md).

**Instrument metadata (incomplete):** The external acoustic/proxy corpus is under gradual curation. Many registry entries use coarse fallbacks; final cross-instrument calibration is not complete. Missing data are expected when provenance labels remain honest.

**Auxiliary Excel importer:** `tools/import_instrument_profiles_from_excel.py` validates human-curated workbooks offline and emits JSON packages. It is not part of the analytical core; runtime does not read raw `.xlsx`. Imported acoustic rows are always in **sounding/concert pitch** (`note_sounding`, `midi_sounding`); the importer never transposes metadata rows. See [instrument_profile_importer.md](instrument_profile_importer.md).

**Removed in 3.0.0-strict-symbolic:** Stevens' Law (`use_stevens`, `alpha`, `beta`), psychoacoustic corrections (`use_psychoacoustic`), and perceptual interval weighting (`use_perceptual_weighting`).

**Removed in 4.0.0-strict-symbolic:** Combination-tone / resultant-tone analysis and all related configuration keys.

---

## 1. Overview

### 1.1 High-level purpose

**Textural Density** computes a set of **vertical density** metrics for a given vertical slice of music (a chord or simultaneity). The system:

- Takes as input: **notes** (pitches), **dynamics**, **instruments**, and **number of instruments** per note.
- **Produces:** **interval compactness** (distinct pitch bins), **symbolic orchestration mass**, weighted / pitch-structure / composite density, symbolic spectral summaries, and texture/timbre descriptors — all from notated/input symbolic events only.
- **Construct separation:** exact unison doublings increase event/orchestral mass but do **not** create additional vertical interval structure, spectral entropy, or registral diversity (`core/pitch_aggregation.py`).

The pipeline is **deterministic** given the same input and configuration; it does not perform audio signal processing—it works on symbolic note lists (e.g. from manual entry, XML, or MIDI).

### 1.2 Design principles

- **Recommended entry point:** `from core import calculate_metrics` (alias `calcular_metricas`). Implementation lives in **`core/pipeline.py`**. `data_processor.py` is a backward-compatibility shim.
- **Score-level analysis:** `from core import analyze_score` for timed XML/MIDI or event lists → multiple vertical slices.
- **Layered metrics:** Raw densities → normalised weighted blend $D_{\mathrm{blend}}$ → composite $D_{\mathrm{blend}}\cdot\sqrt{M}/\mathrm{REF}$ (Task 8c). Pitch-structure density is a **reported axis only**.
- **Epistemic transparency:** Every metric carries `metric_metadata`; interpretable decomposition in `density_subindices`.
- **GUI independence:** Analytical modules (`core/`, `validation/`) do not import Tkinter at module load time.
- **Extensibility:** Instrument models are plug-in modules resolved per event via `instrumentos/registry.py`.

---

## 2. Code architecture

### 2.1 Package layout

```
core/                          # Analytical API (GUI-independent)
├── __init__.py                # Public exports
├── pipeline.py                # calculate_metrics (canonical implementation)
├── models.py                  # Pitch, InstrumentEvent, VerticalSlice, MetricResult, …
├── converters.py              # Legacy dict ↔ VerticalSlice
├── orchestration.py           # Per-event instrument density
├── metrics_metadata.py        # Epistemic labelling (Phase 3)
├── subindices.py              # density_subindices (Phase 5)
├── temporal.py                # Vertical-slice segmentation (Phase 6)
├── score_analysis.py          # analyze_score, load_timed_events_from_path
└── reporting.py               # Interpretability + sensitivity (Phase 9)

validation/                    # Verification framework (Phase 8)
├── verification.py            # run_verification_suite()
├── synthetic_cases.py         # Synthetic test chords
├── metrics.py                 # Spearman, Kendall, RMSE, bootstrap CI
├── schemas.py                 # ExpertAnnotation loader
└── report.py                  # generate_validation_report()

instrumentos/
├── registry.py                # InstrumentProfile registry (Phase 7)
├── pitch_interpolation.py     # Continuous-pitch metadata lookup (chromatic anchors → microtones)
├── spectral_lookup.py         # Wrapper used by instrument modules (backward-compatible float API)
├── coarse_default.py          # Fallback for unknown instruments
└── *.py                       # Per-instrument density modules (committed tables)

data_processor.py              # Backward-compatibility shim (re-exports core)
densidade_intervalar.py        # Interval density library
spectral_analysis.py           # Spectral moments
xml_loader.py                  # Custom XML + MusicXML loader (transpose-aware)
score_io/, gui/                # Export and GUI layers (separate from core)
```

### 2.2 Main entry and data flow

| Component | Role |
|-----------|------|
| **`core.calculate_metrics(input_data)`** | Single vertical slice. Returns `(resultados, densidades_instrumento, pitches)`. Attaches `metric_metadata` and `density_subindices`. |
| **`core.analyze_score(source, config)`** | Timed score analysis. Accepts path, legacy dict, or `list[InstrumentEvent]`. Returns `ScoreAnalysisResult`. |
| **`core.legacy_input_to_vertical_slice(data)`** | Converts legacy input dict to typed `VerticalSlice`. |
| **`core.orchestration.compute_event_instrument_density`** | Per-event instrument module lookup and density. |
| **`xml_loader.parse_xml` / `parse_xml_to_events`** | Load custom `<densidade_analysis>` or MusicXML; MusicXML written `<pitch>` is converted to **sounding/concert pitch** via `<transpose>` before validation and lookup (see §7.4). |
| **`data_processor_legacy._validate_and_extract_input`** | Legacy GUI validation helpers (shim path). |

### 2.3 Core calculation modules

| Module | Main functions | Purpose |
|--------|----------------|--------|
| **`densidade_intervalar`** | `calculate_interval_density`, `calculate_interval_density_normalized`, `calibrate_lambda` | Symbolic interval density; λ calibration. |
| **`core.pipeline`** | `calculate_metrics`, `calcular_metricas` | Full vertical-slice pipeline assembly. |
| **`data_processor`** | Re-exports `core.pipeline` symbols | Compatibility shim only. |
| **`spectral_analysis`** | `calculate_spectral_moments`, `calculate_extended_spectral_moments`, `calculate_chroma_vector`, `calculate_harmonic_ratio` | Spectral shape metrics. |
| **`timbre_texture_analysis`** | `calculate_texture_density`, `calculate_timbre_blend`, `calculate_orchestration_balance` | Texture and orchestration descriptors. |
| **`core/metrics_metadata`** | `attach_metric_metadata`, `build_metric_metadata` | Epistemic fields on every metric. |
| **`core/subindices`** | `attach_density_subindices`, `build_density_subindices` | Interpretable decomposition. |
| **`core/temporal`** | `group_events_into_slices`, `normalize_event_timing` | Temporal segmentation. |
| **`core/reporting`** | `explain_vertical_slice`, `run_sensitivity_analysis` | Human-readable reports; robustness sweeps. |

### 2.4 Instrument layer (external acoustic metadata)

- Each **instrument module** under `instrumentos/` exposes:
  - `calcular_densidade(nota, dinamica)` → float (committed `spectral_data` cell)
- Modules embed acoustic amplitude tables (`spectral_data`) from **external sources**. Production looks up the requested dynamic **exactly**; missing cells raise `MissingCommittedDynamicError` (no runtime GPR). **Chromatic-only pitch tables are the canonical model** — quarter-tones and cent deviations resolve via `microtonal.note_to_midi_strict()` and `instrumentos/pitch_interpolation.py`. Optional pasted microtonal rows are curated exact overrides only.
- **Strict pitch grammar:** `parse_pitch_strict()` is the **single authoritative pitch grammar** in `microtonal.py`; `note_to_midi_strict()`, `is_valid_note()`, and instrument metadata lookup all delegate to it. It raises `InvalidPitchNotation` on malformed strings (`H4`, `C##4`, `foo`) and never falls back to C4. `is_valid_note()` is a **non-raising strict predicate** (exactly "`parse_pitch_strict` succeeds"); `extract_cents()` is a **compatibility suffix splitter** (alias of `extract_cents_float`, returning `tuple[str, float]`) that does not validate the pitch base. Legacy `note_to_midi()` remains permissive for backward compatibility in non-canonical helpers only.
- **Canonical core conversion path:** `core/converters.note_string_to_pitch()` and `core/pipeline.calculate_metrics()` (returned pitch list) use the strict parser — MIDI is taken from `ParsedPitch.midi` / `Pitch.midi` before any enharmonic spelling normalization. Invalid input propagates `InvalidPitchNotation`; it never becomes MIDI 60.
- **Octave-boundary enharmonics:** strict MIDI conversion resolves cross-octave spellings — `Cb4` = B3 (MIDI 59), `B#4` = C5 (MIDI 72) — and applies the octave adjustment before adding cents/quarter-tone offsets (`Cb4+50c` = 59.5, `B#4-50c` = 71.5).
- **`format_cents_suffix()`:** precision-safe cents suffix formatter (no scientific notation; integer floats omit `.0`; round-trips through `extract_cents_float()`).
- **Pitch lookup order:** (1) exact table key, (2) normalized MIDI-equivalent match, (3) continuous interpolation/extrapolation. Never collapses to the same pitch class in a distant octave (e.g. D♯6 ≠ D♯4). Cents suffixes support signed decimal values (`+7.5c`, `+125c`, `+7¢`) applied as `cents / 100.0` semitones.
- **Metadata table validation:** harmless duplicate MIDI rows (identical dynamic values) are deduplicated; conflicting duplicates raise `MetadataTableConflictError`.
- **Dynamics:** committed ladder cells only (see §2.4.1). Retired GPR/tail code lives under `tools/legacy_gpr_dynamic_interpolation.py` for historical audits.
- **`instrumentos/registry.py`** maps names/aliases to profiles with `profile_status` (`literature_derived`, `empirical_source`, `coarse_default`) and `uncertainty`.
- Instruments **without** dedicated tables use coarse register/dynamic models only (`coarse_default`), also via `microtonal.note_to_midi_strict` for microtonal input.
- **Per-event resolution:** each note uses its own instrument module via `core/orchestration.py`.
- Unknown instruments raise `InputError` (`field: instruments`). They are not remapped to a parent module or to the generic coarse proxy. The proxy is audit-only (`profile_for_event(..., allow_unknown=True)`).

#### 2.4.1 Dynamic tables (current state)

Instrument density uses **committed** `spectral_data` cells for the requested
dynamic. This is score-grounded symbolic/acoustic-metadata lookup — **not**
perceptual, empirical, or psychoacoustic validation, and **not** runtime
extrapolation.

| Dynamic | Status |
|---------|--------|
| All ten `DYNAMIC_LEVELS` | **Committed table cells** when present in `spectral_data` |
| Missing cell | **Error** (`MissingCommittedDynamicError`) — no runtime fill-in |

**Migration (2026-08-03):** Runtime GPR + adaptive tails removed from production.
**Data-faithful rebuild (2026-08-08/09):** all pitched table-backed modules —
winds (flute, oboe, clarinet, bassoon), brass (trumpet, horn, trombone, tuba), arco strings,
and the remaining violin/viola technique modules — commit 10-level ladders generated offline by
**Dynamics_predicter v1.5** on the measured pp/mf/ff anchors: anchors verbatim,
PCHIP interiors bounded by their measured segment, geometrically tapered outer
levels. Ladders are **not** forced monotone; real measured anchors are
occasionally non-monotone and are preserved. The earlier D6 isotonic clamp
(2026-08-03) remains only in the violin harmonic modules, pending rebuild.
Unpitched percussion uses pitch-independent `DYNAMIC_CDM`. Legacy implementation:
`tools/legacy_gpr_dynamic_interpolation.py`. Ladder hygiene contract:
`tests/test_pitched_dynamic_monotone_ladders.py`.

**Transferred-anchor modules:** Some technique tables (historically `violin_sul_ponticello`) may commit soft/loud anchors derived by ratio transfer. Since 2026-08-11 the violin technique modules (`violin_sordina`, `violin_sul_tasto`, `violin_sul_ponticello`, `violin_harmonics`) commit measured workbook `pp`/`mf`/`ff` anchors from the `OK_VIOLIN_*` dynamics-extrapolation exports.

Historical audits (PR #23 / #24) compared the retired GPR path with linear/PCHIP:

- **357** source-table rows; **320** positive + **20** negative string scenarios; **5** benchmark excerpts (**15** metric rows).
- Source-row GPR differs from conservative references in some cases — highest local sensitivity in **low-register strings** (cello, double bass).
- Scenario-level `density.instrument`: **0** high/extreme; **46** moderate; **182** low; **92** negligible.
- Largest absolute scenario spreads: low-register mass, very sparse/dense chromatic aggregates, all-four-string scenarios — relative sensitivity remained controlled in tested aggregates.
- Benchmark diagnostic comparison: all **negligible**; frozen benchmark outputs unchanged.

**Methodological position (post-2026-08-03):** production no longer interpolates dynamics at runtime. Historical GPR audits remain under `reports/` and `tools/legacy_gpr_*` for method history only.

### 2.5 Configuration and constants

- **`config.py`**: `MAX_DENS_GLOBAL`, `USE_LOG_COMPRESSION`, `DEFAULT_REGISTER_BANDS`, `COMPOSITE_HARMONIC_DAMPING` (0.15), `DYNAMIC_LEVELS`, etc.
- **`densidade_intervalar`**: Calibrated $\lambda$ in `config/density_params.json`, loaded by `load_calibrated_parameters()`.
- **`AnalysisConfig`** (`core/models.py`): typed options for strictly symbolic analysis (`weight_factor`, normalization/temporal configs).

---

## 3. Mathematical foundations

All formulas below are **code-verified**: they match the implementation in `microtonal`, `densidade_intervalar`, `data_processor`, and `spectral_analysis`. Constants (e.g. A4, λ bounds) and function names correspond to the codebase.

### 3.1 Pitch and frequency

**Reference (ISO 16):** Concert pitch A4 = 440 Hz; MIDI note number for A4 is 69. In code: `A4_FREQ = 440.0`, `A4_MIDI = 69` (`microtonal.py`).

- **MIDI to frequency:**
  $$f = f_{\mathrm{A4}} \cdot 2^{(m - 69)/12} = 440 \cdot 2^{(m - 69)/12}, \qquad m \in \mathbb{R}.$$

- **Frequency to MIDI:**
  $$m = 69 + 12 \, \log_2(f / 440), \qquad f > 0.$$

- **Interval between two notes (semitones):**
  $$\Delta_{\mathrm{st}}(i,j) = |m_i - m_j|.$$

- **Pitch span (semitones over distinct aggregated bins):**
  $$A_{\mathrm{st}} = \max_k m_k - \min_k m_k.$$
  Production subindex **registral compression** is $1/(1+A_{\mathrm{st}})$ when $n_{\mathrm{distinct}}\ge 2$, else $0$. The helper **registral compactness** $1/(1+A_{\mathrm{st}}/12)$ exists but is **not** called from `calculate_metrics`. Neither enters $D_{\mathrm{total}}$.

### 3.2 Interval compactness (distinct pitch bins)

Events are aggregated by exact MIDI pitch (`core/pitch_aggregation.py`) before interval structure is computed. Exact unison doublings merge into one bin; microtonally distinct pitches remain separate.

- **Decay function** (unchanged at low level; used only for **distinct-bin** pairs):
  $$\phi(\delta; \lambda) = \begin{cases} 1 & \text{if } \delta = 0, \\ e^{-\lambda \delta} & \text{if } \delta > 0. \end{cases}$$
  Implemented in `modified_exponential_decay(delta, lamb)`. Parameter $\lambda$ is loaded from calibration or defaults to `DEFAULT_LAMBDA` (0.05).

- **Microtonal scale:** In code, interval in semitons $\Delta_{\mathrm{st}}$ is converted to microtonal steps as $\delta = 2 \cdot \Delta_{\mathrm{st}}$ (24 steps per octave). So $\delta(i,j) = 2\,|m_i - m_j|$.

- **Raw interval compactness** (sum over unordered **distinct-bin** pairs only):
  $$D_{\mathrm{int}}^{\mathrm{raw}} = \sum_{k < \ell} \phi\bigl(\delta(k,\ell); \lambda\bigr), \quad n_{\mathrm{distinct}} \geq 2.$$
  If $n_{\mathrm{distinct}} < 2$, reported interval compactness is zero.

- **Normalisation** (average per distinct-bin pair):
  $$D_{\mathrm{int}}^{\mathrm{norm}} = \frac{2 \, D_{\mathrm{int}}^{\mathrm{raw}}}{n_{\mathrm{distinct}}(n_{\mathrm{distinct}}-1)}.$$

- **Optional log compression** (when `USE_LOG_COMPRESSION` is True):
  $$\widetilde{D}_{\mathrm{int}} = \log_{10}(1 + D_{\mathrm{int}}^{\mathrm{norm}}).$$

Interval compactness is **pitch-only**: no register multiplier, no perceptual weighting, no psychoacoustic wrapper.

### 3.3 Instrument density (pressure-equivalent, incoherent RSS)

**Module:** `core/quantity_scaling.py`, `core/source_aggregation.py`, `core/orchestration.py`.

Textural Density treats `Qty` as the number of players assigned to a symbolic event. Quantity affects player count and orchestral mass; it does **not** create additional pitch-structural events.

**One-player density** (single dynamic lookup via instrument module):

$$
d_i^{(1)} = \texttt{calcular\_densidade}(\text{note}_i, \text{dynamic}_i).
$$

Events with the same (MIDI pitch, instrument, dynamic) merge into one **source group** (row-splitting invariance).

**Pressure-equivalent instrument density** (incoherent root-sum-square):

$$
D_{\mathrm{inst}} = \sqrt{\sum_j n_j \cdot \bigl(d_j^{(1)}\bigr)^2}.
$$

For identical sources: $D_{\mathrm{inst}} = d^{(1)} \sqrt{n}$.

> **Removed:** per-event $d_i' = d_i \sqrt{n_{\mathrm{instr},i}}$ summed across rows, which compounded with sonic mass to yield effective $n^{3/2}$ scaling.

### 3.4 Weighted density (linear min-max blend)

Implemented in `calcular_densidade_ponderada_normalizada(DI, DV, ...)` with DI = instrument density, DV = interval density.

- **Min-max normalisation** (method `"min-max"`, configurable maxima):
  $$\widehat{D}_{\mathrm{inst}} = \frac{D_{\mathrm{inst}}}{D_{\mathrm{inst,max}}}, \qquad \widehat{D}_{\mathrm{int}} = \frac{D_{\mathrm{int}}}{D_{\mathrm{int,max}}}.$$
  Defaults: $D_{\mathrm{inst,max}} = 100$, $D_{\mathrm{int,max}} = 10$ (parameters `DI_max`, `DV_max`). These are **normalisation divisors, not clamps**. Default `INTERVAL_BLEND_NORMALISATION = "legacy"` keeps `DV_max = 10`; `"unit_range"` is an opt-in approximate-parity mode. See [MATHEMATICAL_MANUAL §H](MATHEMATICAL_MANUAL.md).

- **Alternative: z-score normalisation** (method `"z-score"`): $\widehat{D}_{\mathrm{inst}} = (D_{\mathrm{inst}} - \mu_{\mathrm{inst}})/\sigma_{\mathrm{inst}}$, $\widehat{D}_{\mathrm{int}} = (D_{\mathrm{int}} - \mu_{\mathrm{int}})/\sigma_{\mathrm{int}}$ with configurable $\mu$, $\sigma$ (example values in code: $\mu_{\mathrm{inst}}=50$, $\sigma_{\mathrm{inst}}=25$; $\mu_{\mathrm{int}}=5$, $\sigma_{\mathrm{int}}=2.5$).

- **Weighted combination** (weight $w \in [0,1]$, `weight_factor` in input):
  $$D_{\mathrm{pond}} = 10 \cdot \bigl( w \, \widehat{D}_{\mathrm{inst}} + (1-w) \, \widehat{D}_{\mathrm{int}} \bigr).$$
  $$D_{\mathrm{pond}} = 10 \cdot \bigl( w \, \widetilde{D}_{\mathrm{inst}} + (1-w) \, \widetilde{D}_{\mathrm{int}} \bigr).$$
  So $w=0$ uses only interval density, $w=1$ only instrument density.

### 3.5 Pitch-structure and composite vertical density

- **Pitch-structure density** (`density.pitch_structure`, alias `density.refined`):
  Zero when `distinct_pitch_count < 2`. Otherwise (extensive form; see `MATHEMATICAL_MANUAL` §H):
  $$D_{\mathrm{pitch}} = S \cdot (1 + \ln(1+H)) \cdot (1 - 0.15 \cdot r_{\mathrm{harm}}),$$
  where $S$ is the raw pairwise interval sum, $H$ is spectral entropy and $r_{\mathrm{harm}}$ is harmonic ratio — both over **distinct pitched bins**.

- **Composite vertical density (unified, all regimes — Task 8c):**
  $$D_{\mathrm{blend}} = 10\cdot\bigl(w\,\widehat{D}_{\mathrm{inst}} + (1-w)\,\widehat{D}_{\mathrm{int}}\bigr)
  \quad(= \texttt{density.weighted}),$$
  $$D_{\mathrm{total}}^{\mathrm{raw}} = \frac{D_{\mathrm{blend}} \cdot \sqrt{M_{\mathrm{sonic}}}}{\mathrm{REF}}, \qquad
  D_{\mathrm{total}} = \log_{10}(1 + D_{\mathrm{total}}^{\mathrm{raw}})$$
  when `USE_LOG_COMPRESSION` is true. $\mathrm{REF}$ = `MAX_DENS_GLOBAL` (**193**).
  Zero interval/pitch contribution is just a numeric zero — **no** event-kind
  fallback. Header from `core.composite.format_composite_header_line` (same
  constants as the computation; prints `D_blend=` and `M=`).
  See `CHANGES.md` for the 575→193 recalibration mapping.

### 3.6 Sonic mass and dynamic boost

Implemented in `core/orchestration_mass.py`; result used as `dynamic_boost = sqrt(M)`.

**Dynamic treatment:** Written dynamics are applied **once** via instrument-module table lookup (`calcular_densidade(note, dynamic)`). The mass formula does **not** apply a second symbolic dynamic multiplier.

**Sonic / orchestration mass** (linear player-count scaling):

$$
M_{\mathrm{sonic}} = \sum_j n_j \cdot d_j^{(1)}.
$$

- **Dynamic boost** (composite path only):
  $$\mathrm{boost} = \sqrt{M_{\mathrm{sonic}}}.$$

This is a symbolic external-acoustic-metadata proxy — not measured SPL or live ensemble loudness. Coherent phase-locked $N^2$ radiation is **not** assumed.

### 3.7 Spectral moments (centroid, spread, skewness, kurtosis)

Implemented in `calculate_spectral_moments` and `calculate_extended_spectral_moments`. Weights $a_i$ = amplitudes (e.g. densities); $S = \sum_i a_i$. Non-finite values are masked out in code.

- **Centroid (MIDI):**
  $$\mu_{\mathrm{MIDI}} = \frac{1}{S} \sum_i a_i \, m_i.$$

- **Spread (standard deviation in MIDI):**
  $$\sigma_{\mathrm{MIDI}} = \sqrt{ \frac{1}{S} \sum_i a_i \, (m_i - \mu_{\mathrm{MIDI}})^2 }, \quad \text{with } \sigma_{\mathrm{MIDI}} \geq 0 \text{ (max with 0 in code)}.$$

- **Skewness:**
  $$\gamma_1 = \frac{ \frac{1}{S} \sum_i a_i \, (m_i - \mu_{\mathrm{MIDI}})^3 }{ \sigma_{\mathrm{MIDI}}^3 }, \quad \text{with } \gamma_1 = 0 \text{ if } \sigma_{\mathrm{MIDI}} = 0.$$

- **Kurtosis (excess):**
  $$\gamma_2 = \frac{ \frac{1}{S} \sum_i a_i \, (m_i - \mu_{\mathrm{MIDI}})^4 }{ \sigma_{\mathrm{MIDI}}^4 } - 3, \quad \text{with } \gamma_2 = 0 \text{ if } \sigma_{\mathrm{MIDI}} = 0.$$

- **Centroid and spread in Hz:** With $f(m) = 440 \cdot 2^{(m-69)/12}$:
  $$f_{\mathrm{centroid}} = f(\mu_{\mathrm{MIDI}}) = 440 \cdot 2^{(\mu_{\mathrm{MIDI}} - 69)/12},$$
  $$\sigma_f = f(\mu_{\mathrm{MIDI}} + \sigma_{\mathrm{MIDI}}) - f(\mu_{\mathrm{MIDI}}) = f_{\mathrm{centroid}} \cdot \bigl( 2^{\sigma_{\mathrm{MIDI}}/12} - 1 \bigr).$$
  The second equality is exact (code: `midi_to_frequency(centroid_midi + spread_midi) - centroid_freq`).

### 3.8 Spectral flatness, roll-off, entropy

- **Flatness** (ratio of geometric to arithmetic mean; only $a_i > 10^{-10}$ used to avoid log(0)):
  $$\mathrm{flatness} = \frac{ \exp\bigl( \frac{1}{n'} \sum_i \ln a_i \bigr) }{ \frac{1}{n'}\sum_i a_i }, \quad \text{over } i \text{ with } a_i > 0.$$
  In code: `np.exp(np.log(nz_amps).mean()) / nz_amps.mean()`.

- **Roll-off (85%):** Amplitudes are cumsummed in pitch order; the roll-off index is the smallest $k$ such that $\sum_{i \leq k} a_i \geq 0.85\, S$. The roll-off frequency is $f(m_k)$ where $m_k$ is the MIDI pitch at that index.

- **Entropy** (with $p_i = a_i/S$, only $p_i > 10^{-10}$ to avoid $\log 0$):
  $$H = -\sum_i p_i \log_2 p_i \quad \text{(bits).}$$

### 3.9 Chroma vector

- **Chroma classes:** $c \in \{0,\ldots,11\}$ (C, C♯, …, B). For each pitch $m_i$, class $c_i = \mathrm{round}(m_i) \bmod 12$ (code: `int(round(p)) % 12`).

- **Chroma energy and normalisation:**
  $$E_c = \sum_{i \colon c_i = c} a_i, \qquad \widetilde{E}_c = \frac{E_c}{\sum_{c'=0}^{11} E_{c'}} \quad \text{if } \sum_{c'} E_{c'} > 0.$$

  The chroma vector is $(\widetilde{E}_0, \ldots, \widetilde{E}_{11})$; normalised so it sums to 1 when there is energy.

### 3.10 Harmonic ratio

- **Definition:** Ratio of energy in harmonic bins to total energy. Fundamental is $m_{\min}$ if not provided. Membership is a **symmetric** octave-class distance (not one-sided `isclose` after modulo):
  $$\mathrm{harmonicRatio} = \frac{\sum_{i \in \mathcal{H}} a_i}{\sum_i a_i},\quad
  \mathcal{H}=\bigl\{i:\min(r_i,\,12-r_i)\le 0.25\bigr\},\quad
  r_i=(m_i-m_{\min})\bmod 12.$$
  If total energy is 0, the ratio is 0.

### 3.11 Complexity factor (pitch-structure path)

Spectral entropy $H$ enters **pitch-structure density** only (not a separate cohesion multiplier):

$$C_{\mathrm{comp}} = 1 + \ln(1 + H).$$

> **Removed:** cohesion factor $C_{\mathrm{coes}} = 10/(1 + A_{\mathrm{st}})$ in the composite product.

### 3.12 Total density (final formula)

Unified composite (Task 8c) — same as §3.5; $D_{\mathrm{pitch}}$ is **not** the product term:

- **Blend** (slider-controlled; equals `density.weighted`; single source in `core.composite`):
  $$D_{\mathrm{blend}} = 10\cdot\bigl(w\,\widehat{D}_{\mathrm{inst}} + (1-w)\,\widehat{D}_{\mathrm{int}}\bigr)
  = w\cdot\frac{D_{\mathrm{inst}}}{10} + (1-w)\cdot D_{\mathrm{int}}$$
  with $\mathrm{DI\_max}=100$, $\mathrm{DV\_max}=10$ (equals printed weighted orch + pitch components).

- **Unnormalised total:**
  $$D_{\mathrm{total}}^{\mathrm{raw}} = \frac{D_{\mathrm{blend}} \cdot \sqrt{M_{\mathrm{sonic}}}}{\mathrm{REF}}, \quad \mathrm{REF}=\texttt{MAX\_DENS\_GLOBAL}=193.$$

- **Optional log compression** (when `USE_LOG_COMPRESSION` is True):
  $$D_{\mathrm{total}} = \log_{10}(1 + D_{\mathrm{total}}^{\mathrm{raw}}).$$
  Otherwise $D_{\mathrm{total}} = D_{\mathrm{total}}^{\mathrm{raw}}$.

Old→new baseline totals: [`CHANGES.md`](../CHANGES.md).

### 3.12.1 Average texture density vs monotone totals

`average_texture_density` is a **per-player mean** of one-player CDM (Qty-weighted). It may
**decrease** when low-CDM instruments are added and **increase** under Qty expansion
weighted toward high-CDM instruments. The monotone quantities under event/Qty growth are
the **totals**: Sonic Mass, instrument RSS, and Composite (`density.total`).

Worked illustrations from the Task 8c GUI acceptance chain
(`tests/test_composite_unification_acceptance.py`):

| Step | `average_texture_density` | Reading |
|------|---------------------------|---------|
| 5 strings ff → +bass drum | ≈40.25 → ≈37.35 | Mean falls: bass drum CDM below the string mean |
| Unit-qty full mix → Qty 4/5/5/3/10 on strings | ≈28.39 → ≈36.25 | Mean rises: expansion weighted toward higher-CDM strings |

(Session notes sometimes cite ≈39.17→36.46 and ≈27.73→33.24 for the same qualitative pair of behaviours.)

### 3.13 Absolute density (reference)

- **Tone count:** $N_{\mathrm{pitched}}$ = pitched event-row count (`pitched_event_count`). Unpitched events are excluded.

- **Absolute density** (code: `np.log1p(pitched_event_count)`):
  $$D_{\mathrm{abs}} = D_{\mathrm{blend}} \cdot \ln(1 + N_{\mathrm{pitched}}) \quad \text{if } n_{\mathrm{distinct}} \ge 2,\qquad D_{\mathrm{abs}} = 0 \text{ otherwise.}$$

### 3.14 Texture metrics (summary)

Implemented in `calculate_texture_density(...)`. See the **unpitched aggregation contract** table in §7.5.1 for which inputs include unpitched events.

- **Player count / player-weighted texture mass:** $\sum n_j$ over the **full slice** (pitched + unpitched Qty).
- **Average texture density:** Qty-weighted mean of one-player CDM values over the **full slice** (includes unpitched CDM).
- **Texture / pitch polyphony:** distinct **pitched** bins only.
- **Texture variability / contrast:** std / range of pitched-bin MIDI only.

### 3.15 Lambda calibration

Implemented in `calibrate_lambda(experimental_data)`. Reference data: `CONSONANCE_RATINGS` (e.g. Hutchinson & Knopoff, Malmberg, Kameoka & Kuriyagawa).

- **Experimental data:** Dict mapping interval (semitons) to consonance rating in $[-1, 1]$ (e.g. 0 → 1.0, 5 → 1.24, 2 → −0.582).

- **Prediction:** For each interval $k$, build a two-note chord and compute raw interval density $D_{\mathrm{int}}(k; \lambda)$. Normalise to $[-1, 1]$ using the **maximum experimental rating** $R_{\max} = \max_j \{\mathrm{rating}_j\}$:
  $$\mathrm{pred\_norm}_k(\lambda) = 2 \cdot \frac{D_{\mathrm{int}}(k; \lambda)}{R_{\max}} - 1.$$

- **Optimisation:** $\lambda^* = \mathrm{argmin}_{\lambda} \sum_k \bigl( \mathrm{pred\_norm}_k(\lambda) - \mathrm{rating}_k \bigr)^2$, with bounds $\lambda \in [0.01, 1]$, method L-BFGS-B. Optimised $\lambda$ is stored in `config/density_params.json` and loaded by `load_calibrated_parameters()`.

### 3.16 Removed: combination-tone analysis (4.0.0)

Combination-tone / resultant-tone analysis was removed in 4.0.0-strict-symbolic. Spectral moments, chroma, harmonic ratio, registral span, refined density, absolute density, and total density are computed from **notated/input symbolic pitches and symbolic weights only**.

---

## 4. Practical example

### 4.1 Sample input

Consider a single chord (vertical slice) with three notes:

```python
input_data = {
    "notes": ["C4", "E4", "G4"],
    "dynamics": ["mf", "f", "mf"],
    "instruments": ["flute", "flute", "clarinet"],
    "num_instruments": [1, 1, 1],
    "weight_factor": 0.5,
}
```

- **Notes:** C4 (MIDI 60), E4 (64), G4 (67).  
- **Spectral spread:** $A_{\mathrm{st}} = 67 - 60 = 7$ semitons.  
- **Weight:** $w = 0.5$ (equal balance between interval and instrument density).

### 4.2 Step-by-step (conceptual)

1. **Validation:** Lists have length 3; all required keys present → extract notes, dynamics, instruments, num_instruments, weight_factor.

2. **Note normalisation:** "C4", "E4", "G4" already in canonical form (e.g. sharp); no change.

3. **Pitch aggregation:** Three events → three distinct pitch bins (no unison merge).

4. **Interval compactness:** Pairs over **distinct bins** only → intervals 4, 7, 3 semitons. With $\lambda \approx 0.05$ and microtonal $\delta = 2 \cdot \Delta_{\mathrm{st}}$:
   - $\phi(8) = e^{-0.05 \cdot 8}$, $\phi(14)$, $\phi(6)$; sum → $D_{\mathrm{int}}^{\mathrm{raw}}$; normalise over distinct-bin pairs.

5. **One-player instrument densities:** For each note, the instrument module returns $d_i^{(1)}$ for the given dynamics (dynamic applied once). With Qty = 1 each, three source groups:
   $$D_{\mathrm{inst}} = \sqrt{(d_1^{(1)})^2 + (d_2^{(1)})^2 + (d_3^{(1)})^2}.$$

6. **Weighted density:** Normalise $D_{\mathrm{inst}}$ and $D_{\mathrm{int}}$ (min-max), then:
   $$D_{\mathrm{pond}} = 10 \cdot (0.5 \cdot \widehat{D}_{\mathrm{inst}} + 0.5 \cdot \widehat{D}_{\mathrm{int}}).$$

7. **Pitch-structure density (reported only):** $D_{\mathrm{pitch}} = S \cdot (1 + \ln(1+H)) \cdot (1 - 0.15 \cdot r_{\mathrm{harm}})$ with $S$ the raw pairwise sum. Registral span is **not** a factor. This value does **not** enter the composite.

8. **Spectral moments:** On distinct-bin MIDI pitches with mean weight per bin; compute centroid, spread, entropy, etc.

9. **Chroma and harmonic ratio:** From distinct pitch bins only.

10. **Sonic mass:** $M_{\mathrm{sonic}} = \sum_i d_i^{(1)} \cdot n_i$ (linear Qty; here $n_i=1$); $\mathrm{boost} = \sqrt{M_{\mathrm{sonic}}}$.

11. **Composite vertical density:** $D_{\mathrm{total}}^{\mathrm{raw}} = D_{\mathrm{blend}} \cdot \sqrt{M_{\mathrm{sonic}}} / \mathrm{REF}$ with $\mathrm{REF}=193$; then $\log_{10}(1+x)$ when log compression is on.

12. **Absolute density:** $D_{\mathrm{abs}} = D_{\mathrm{blend}} \cdot \ln(1 + N_{\mathrm{pitched}})$ when $n_{\mathrm{distinct}} \geq 2$; else 0. $N_{\mathrm{pitched}}$ counts pitched rows only.

### 4.3 Expected output structure

Calling `from core import calculate_metrics` (preferred) or `AnalysisController.analyze` from the GUI:

- **`resultados["density"]`:**  
  `interval`, `instrument`, `weighted`, `refined` / `pitch_structure`, `total`, `sonic_mass`, `absolute`, `weighted_pitch`, `weighted_orchestral`.

- **`resultados["pitch_aggregation"]`:**  
  `event_count`, `player_count`, `distinct_pitch_count`, `pitch_polyphony`, `event_doubling_count`, `player_doubling_count`, `pitch_bins`.

- **`resultados["quantity_scaling"]`:**  
  Incoherent source-addition metadata (`quantity_scaling_model`, `dynamic_applied_once`, etc.).

- **`resultados["metric_metadata"]`:**  
  Per-metric epistemic blocks plus global normalization and quantity-scaling fields.

- **`resultados["density_subindices"]`:**  
  `event_count`, `interval_compactness`, `registral`, `orchestral_mass`, `timbral_heterogeneity`, `harmonicity_proxy`, `temporal`, `composite`.

- **`resultados["spectral_moments"]`:**  
  `centroid` (frequency, note), `spread` (deviation), `spectral_skewness`, `spectral_kurtosis`, `spectral_flatness`, `spectral_rolloff`, `spectral_entropy`.

- **`resultados["additional_metrics"]`:**  
  `complexity`, `harmonic_ratio`, `chroma_vector`.

- **`resultados["texture"]`:**  
  `player_count`, `pitch_polyphony`, `player_weighted_texture_mass`, `texture_variability`, `texture_contrast` (`texture_polyphony` = distinct pitch count, not mean Qty).

- **`resultados["timbre"]`:**  
  Timbre blend: `timbre_diversity`, `blend_index`, `density_variance`, `family_contributions`, `timbre_balance`, `timbre_dominance`.

- **`resultados["orchestration"]`:**  
  Orchestration: `register_balance`, `density_balance`, `orchestration_evenness`, `register_distribution`, and aliases `orchestration_balance`, `pitch_balance`, `instrument_balance`.

- **`densidades_instr`:** One entry per input note; each is **one-player** instrument density (no Qty factor). Slice-level pressure-equivalent density and mass apply RSS / linear scaling via source aggregation.

- **`pitches`:** MIDI of input notes only (one per notated event).

**Quantity terminology (GUI):**

| Label | Meaning |
|-------|---------|
| Event count | Number of notated input rows (**pitched + unpitched**) |
| Player count | Sum of Qty (**pitched + unpitched**) |
| Pitch polyphony | Distinct simultaneous **pitched** bins |
| Event / player doubling | Pitched-only extras beyond distinct pitched bins |
| Instrument density | Pressure-equivalent RSS proxy (includes unpitched) |
| Sonic / orchestral mass | Linear sum(qty × one-player density) (includes unpitched) |

### 4.4 Example numerical ranges (orientation only)

- **Interval density:** Typically positive; depends on $\lambda$ and number/size of intervals. After log, often in a range like $[0, 1]$ for moderate chords.
- **Instrument density:** Positive; order of magnitude depends on instrument modules (e.g. tens).
- **Weighted density:** With min-max and $w=0.5$, often in $[0, 10]$.
- **Total:** After normalisation and log, often in $[0, 1]$ or similar; exact values depend on all factors above.

These ranges are indicative; the manual does not fix a single “expected” number so that the implementation can evolve (e.g. new instruments or calibration) without contradicting the document.

---

## 5. References to code

| Concept | Module | Function / constant |
|--------|--------|----------------------|
| Public API | `core` | `calculate_metrics`, `analyze_score`, `group_events_into_slices` |
| Data models | `core.models` | `InstrumentEvent`, `VerticalSlice`, `MetricResult`, `ScoreAnalysisResult` |
| Epistemic metadata | `core.metrics_metadata` | `attach_metric_metadata`, `build_metric_metadata` |
| Subindices | `core.subindices` | `attach_density_subindices`, `build_density_subindices` |
| Temporal analysis | `core.score_analysis` | `analyze_score`, `load_timed_events_from_path` |
| Instrument registry | `instrumentos.registry` | `resolve_profile`, `get_instrument_module` |
| Verification | `validation.verification` | `run_verification_suite` |
| Validation report | `validation.report` | `generate_validation_report` |
| Interpretability | `core.reporting` | `explain_vertical_slice`, `run_sensitivity_analysis` |
| MIDI ↔ Hz | `microtonal` | `midi_to_hz`, `hz_to_midi`; `A4_FREQ`, `A4_MIDI` |
| Interval decay | `densidade_intervalar` | `modified_exponential_decay` |
| Raw interval density | `densidade_intervalar` | `calculate_interval_density` |
| Normalised interval density | `densidade_intervalar` | `calculate_interval_density_normalized` |
| Quantity scaling | `core.quantity_scaling` | `rss_pressure_equivalent`, `linear_orchestral_mass`, metadata constants |
| Source aggregation | `core.source_aggregation` | `aggregate_event_sources`, row-splitting invariance |
| One-player density | `core.orchestration` | `compute_event_one_player_density`, `compute_slice_orchestral_metrics` |
| Pitch aggregation | `core.pitch_aggregation` | `aggregate_events_by_pitch` |
| Pitch structure | `core.pitch_structure` | `compute_pitch_structure_density`, composite assembly |
| Pipeline | `core.pipeline` | `calculate_metrics` |
| Sonic mass | `core.orchestration_mass` | `compute_orchestration_mass` |
| Weighted density | `core.composite` | `compute_weighted_density_normalized` |
| Spectral moments | `spectral_analysis` | `calculate_spectral_moments`, `calculate_extended_spectral_moments` |
| Chroma | `spectral_analysis` | `calculate_chroma_vector` |
| Harmonic ratio | `spectral_analysis` | `calculate_harmonic_ratio` |
| Legacy shim | `data_processor` | `calculate_metrics`, `calcular_massa_sonora` (delegates to core) |
| Lambda calibration | `densidade_intervalar` | `calibrate_lambda`, `load_calibrated_parameters` |
| Publication figures | `utils.plotting_style` | `create_professional_figure`, `enhance_axes`, `finalize_figure` | to be stable with respect to the mathematical model; implementation details and exact defaults can be read from the source when needed.

---

## 6. Visualization and publication figures

The application uses a central plotting style so that all graphs match the technical manual and are suitable for publication.

### 6.1 Plotting style (`utils.plotting_style`)

- **Theme:** Built-in style `seaborn-v0_8-whitegrid` or `ggplot` (no external seaborn required).
- **Palette:** Viridis and magma (matplotlib colormaps); default colour cycle is viridis.
- **Typography:** Mathtext is enabled so axis labels and legends can use LaTeX-style math (e.g. $\lambda$, $\delta$, $f_c$) without an external LaTeX install.
- **Layout:** Top and right spines are removed; grid is a subtle grey; `finalize_figure(fig)` applies `tight_layout` before save. Use **DISPLAY_DPI (96)** for on-screen and embedded figures so they fit the monitor; use **PUBLICATION_DPI (300)** only when saving to file (e.g. `fig.savefig(..., dpi=PUBLICATION_DPI)`).

### 6.2 Main plotting modules

| Module | Role |
|--------|------|
| **`plot_metr_espectrais`** | Spectral metrics bar chart; chroma and spectral distribution. |
| **`plot_spectrogram`** | Spectrogram-like density view (pitch vs density); optional 3D. |
| **`calibration`** | Decay curve, consonance vs $\lambda$, experimental vs model comparison. |
| **`statistical_validation`** | Metrics comparison and boxplots. |
| **`timbre_texture_analysis`** | 2×2 orchestration view (3D scatter, density profile, heatmap). |
| **`scientific_report_generator`** | Density, spectral, and chroma plots for PDF reports. |

All of these use `create_professional_figure`, `enhance_axes`, and (where applicable) `finalize_figure` from `utils.plotting_style` so that labels use the same conventions as this manual (e.g. $\delta$, $w(\delta)$, $\lambda$).

### 6.3 Running and building

Run the application with `python run.py` or the `densidade-vertical` entry point after `pip install -e .`. To build a standalone Windows executable, use `python build_exe.py` (see README and PyInstaller documentation).

---

## 7. Temporal score analysis

### 7.1 Loading timed events

```python
from core import analyze_score, load_timed_events_from_path

# From file (XML with <onset>/<duration> or MIDI)
result = analyze_score("path/to/score.xml")

# Legacy single-slice dict (no timing → one slice)
result = analyze_score({"notes": ["C4", "E4", "G4"], ...})

# Explicit event list
from core.converters import make_instrument_event
events = [make_instrument_event(0, "C4", "mf", "flute", 1, onset=0.0, duration=2.0), ...]
result = analyze_score(events, config={"temporal_mode": "event_boundary"})
```

### 7.2 `ScoreAnalysisResult` structure

| Field | Content |
|-------|---------|
| `slices` | List of `VerticalSliceAnalysis` — one per temporal slice |
| `time_series` | List of dicts with `time`, `event_count`, density summaries per slice |
| `global_summary` | Aggregates: `slice_count`, `density_total_min/max/mean`, etc. |
| `warnings` / `assumptions` | Score-level epistemic notes |
| `config` | Resolved `AnalysisConfig` |

Each `VerticalSliceAnalysis` contains `metrics`, `subindices`, `composite_density`, and slice-level warnings.

### 7.3 Temporal modes

- **`event_boundary`** (default): slice at each distinct onset; active notes = those sounding at that instant (half-open `[onset, offset)`).
- **`instantaneous`**: all events in one slice regardless of timing.

### 7.4 MusicXML loading and transposition

`xml_loader.py` accepts:

1. **Custom `<densidade_analysis>` XML** — parallel note lists or `<voice>` elements with optional `<onset>` / `<duration>`.
2. **Standard MusicXML** (`score-partwise` / `score-timewise`) — notes extracted per part/measure.

**Sounding/concert pitch (all analytical paths):** Instrument tables, range validation, and density lookup use **concert/sounding pitch**. Manual and GUI input supply sounding pitch directly. MusicXML written ``<pitch>`` is converted via ``<transpose>`` before validation and lookup.

| Input path | Pitch interpreted as | Range validation |
|------------|----------------------|------------------|
| Legacy dict / GUI `notes[]` | **Sounding/concert pitch** as entered | `sounding_pitch.midi` vs `registry.sounding_range` |
| MusicXML `<pitch>` | **Written pitch** → converted via `<transpose>` | **Sounding** MIDI vs `registry.sounding_range` |
| `make_instrument_event(note=…)` | **Sounding/concert pitch** | Same as legacy |

`instrumentos.registry.InstrumentProfile.transposition` is **notation/import metadata only** for manual input — it is **not** applied when building events from legacy/GUI lists. MusicXML uses the part's ``<transpose>`` element instead.

**Range kinds in this repository:**

| Concept | Where stored | Used for validation? |
|---------|--------------|----------------------|
| **Registry range** (`sounding_range`) | `registry.sounding_range` | Yes — **sounding** MIDI vs this span |
| **Comfortable range** | `registry.comfortable_range` | No (orchestration metadata) |
| **Source-table span** | `spectral_data` keys / `INSTRUMENT_SOURCE.pitch_range` | Density lookup; should ⊆ registry `sounding_range` for table-backed modules. Not necessarily equal to practical/comfortable range. |
| **Comfortable range** | `registry.comfortable_range` | Orchestration metadata; narrower central band when documented |

**MusicXML `<transpose>` (applied once):** Exporters include ``<attributes><transpose>`` for transposing parts. Textural Density converts written pitch to concert/sounding pitch:

$$
m_{\mathrm{sounding}} = m_{\mathrm{written}} + \mathrm{chromatic} + 12 \times \mathrm{octave\_change}
$$

Example: B♭ clarinet part with written C4 in `<pitch>` and `<chromatic>-2</chromatic>` — analysis uses **B♭3** (sounding), not C4.

| Function | Returns | Notes |
|----------|---------|-------|
| `parse_xml(path)` | Legacy dict (`notes`, `dynamics`, …) | `notes` are **sounding** pitches for MusicXML |
| `parse_xml_to_events(path)` | `(events, options, warnings)` | Sets `written_pitch` when it differs from sounding |

**Limitations (documented):**

- Untimed MusicXML is treated as **one vertical slice** (warning emitted).
- Global onset times are **not** reconstructed from cumulative `<duration>` unless explicit `<onset>` is present in custom XML.
- Parser is hand-rolled (`xml.etree`); it does not use music21. Transposition follows MusicXML `<transpose>` elements only.

Tests: `tests/test_transposing_instrument_sounding_pitch_contract.py`, `tests/test_xml_loader.py::TestMusicXmlTranspose`; register audit battery: `tests/test_instrument_register_contracts.py`, `tests/test_instrument_transposition_contracts.py`, `tests/test_instrument_alias_registers.py`, `tests/test_musicxml_transposing_instruments.py`. Generate audit artefact: `python tools/audit_transposing_instrument_pitch_contract.py` → `reports/transposing_instrument_pitch_contract_audit.{json,md}`. Benchmarks: `benchmarks/corpus/excerpt_003.musicxml`–`excerpt_004.musicxml` (transpose); see [`benchmarks/README.md`](../benchmarks/README.md).

### 7.5 Unpitched percussion entry paths

Bass drum, Cymbals, Tam-tam, and Gong are **unpitched** (`InstrumentProfile.unpitched` / `InstrumentEvent.unpitched`). Density is pitch-independent (`DYNAMIC_CDM`; `nota` ignored). The chromatic note string on the event is a **placeholder only** (registry sounding-range midpoint) — it has **no acoustic meaning** and must not enter pitch-structure metrics.

**Shared event representation (all entry paths):** `unpitched=True` plus the instrument’s canonical placeholder key. GUI, MusicXML, and MIDI must converge on that shape; they must **not** re-implement pitch-structure exclusion. Exclusion stays solely in `core/unpitched_routing.partition_pitched_events`.

Helpers (same module): `canonical_unpitched_note`, `normalize_unpitched_entry_note`, `reject_unpitched_microtones`, `map_gm_percussion_key`, `GM_PERCUSSION_KEY_MAP`.

| Path | Behaviour |
|------|-----------|
| **GUI** | Note / octave / cents disabled; dropdown groups the four under `── Unpitched percussion ──`. `adapters/gui_adapter` injects the canonical placeholder regardless of stale note state. Cents/microtones raise `InputError`. |
| **MusicXML** | `<unpitched>` maps via part/instrument name to a registered unpitched module; `<display-step>` / `<display-octave>` are **never** promoted to sounding pitch. Unmappable `<unpitched>` events are **skipped** with a per-event warning listing **part name and measure**. |
| **MIDI** | Channel 10 (0-based index 9) only — see GM map below. Unmapped keys are skipped with a warning — **never** a pitched fallback. |

#### Canonical placeholder keys

| Display name | Registry ID | Placeholder | MIDI (midpoint of `sounding_range`) |
|--------------|-------------|-------------|-------------------------------------|
| Bass drum | `bombo` | `D2` | 38 |
| Cymbals | `pratos` | `C5` | 72 |
| Tam-tam | `tamtam` | `C2` | 36 |
| Gong | `gongo` | `C3` | 48 |

#### MIDI GM percussion map (channel 10)

| GM key | Role | Module | Log note |
|--------|------|--------|----------|
| 35, 36 | Acoustic / bass drum | Bass drum | — |
| 49, 57 | Crash cymbal 1 / 2 | Cymbals | — |
| 51, 59 | Ride cymbal 1 / 2 | Cymbals | approximation warning |
| 52 | Chinese cymbal | Cymbals | approximation noted |
| other | — | **skip** | per-event warning |

**Skip-with-warning policy:** unmappable unpitched MusicXML or MIDI events are omitted from the event list and logged; the loader never invents a pitched instrument or sounding pitch as a fallback.

#### 7.5.1 Unpitched aggregation contract

Pitch-structure **exclusion** of note keys remains solely in `partition_pitched_events`. Counts, texture, and mass use the decisions below (implement from this table — do not re-filter in the GUI).

| Metric / field | Includes unpitched? | Notes |
|----------------|---------------------|-------|
| Event Count / Player Count | **Yes** | Full-slice rows / Qty sum (mixed test: 4/4, not 2/2) |
| Distinct Pitch Count / Pitch Polyphony | **No** | Pitched bins only |
| Event / Player Doubling Count | **No** | Pitched extras only |
| Interval / pitch-structure / spectral / registral | **No** | Pitched bins only |
| Sonic mass / instrument RSS / weighted orchestral | **Yes** | Full slice |
| Texture `player_count`, `player_weighted_texture_mass` | **Yes** | Full-slice Qty |
| Texture `average_texture_density` | **Yes** | Qty-weighted mean CDM (includes unpitched) |
| Texture `texture_polyphony` / variability / contrast | **No** | Pitch concepts |
| Composite (unified) | Blend uses instr **yes** / interval only if pitched; mass **yes** | $\log_{10}(1+D_{\mathrm{blend}}\sqrt{M}/193)$; no event-kind branch |

Display: when `unpitched_event_count > 0`, the PITCH STRUCTURE block prints  
`1 unpitched event excluded…` / `N unpitched events excluded…` via `core.unpitched_labels.format_unpitched_exclusion_note`.  
Unpitched-only spectral / advanced sections print `n/a — no pitched content`.

Pipeline fields: `pitch_aggregation.pitched_event_count` / `unpitched_event_count`; `resultados["composite_meta"]` (`mode=weighted_blend_mass_log`, `normalization_ref`, `weight_factor`, `formula`) — outside the numeric `density` map.

Tests: `tests/test_unpitched_entry_paths.py`, `tests/test_unpitched_pitch_exclusion.py`, `tests/test_unpitched_aggregation_contract.py`.

---

## 8. Validation and verification

### 8.1 Verification vs validation

| Term | Meaning in Textural Density |
|------|----------------|
| **Verification** | Synthetic cases + property checks confirming implementation correctness; source-table reconstruction; musicological contract tests |
| **Validation** | Comparison against expert ratings, listening tests, or corpus benchmarks |

Current status: **`verified_only`** — no external validation corpora loaded by default. The test suite (**1542 passed / 2 skipped / 18 xfailed**, 2026-07-12, methodology `5.1.0-strict-symbolic`) provides **software and symbolic-contract verification** — not auditory or empirical validation of CDM.

### 8.1.1 String musicological battery (PR #13)

97 tests (`@pytest.mark.musicological`) across violin, viola, cello, double bass:

| File | Focus |
|------|-------|
| `tests/string_constants.py` | Documented spans, open strings, workbook paths |
| `tests/test_string_module_contracts.py` | Module surface, table shape, exact anchors, provenance portability |
| `tests/test_string_source_reproducibility.py` | Workbook → committed module reconstruction (local) |
| `tests/test_string_musicological_invariants.py` | Pitch spelling, cents, committed-dynamics contracts, interpolation provenance |
| `tests/test_string_score_scenarios.py` | Ensemble slices, MusicXML transposition, Qty invariants |
| `tests/test_instrument_provenance.py` | `INSTRUMENT_SOURCE` guards |

Run: `pytest -m musicological -q`

### 8.1.2 Media note-label normalization (PR #14)

`utils.notes.normalize_media_note_label()` strips trailing duplicate markers such as `(2)` before `normalize_note_string()`. Used when ingesting `*_Media` workbooks. Corrects viola table alignment to `VIOLA_Media` (C3–C7). This is **source-label normalization** — not acoustic or perceptual validation.

### 8.2 Running verification

```python
from validation import run_verification_suite, generate_validation_report

result = run_verification_suite()
assert result.passed

report_text = generate_validation_report()  # writes validation/reports/validation_report.md
```

### 8.3 External data placeholders

| Directory | Purpose |
|-----------|---------|
| `validation/expert_annotations/` | JSON expert density ratings |
| `validation/listening_tests/` | Listening-test result files |
| `validation/corpus_examples/` | Benchmark score excerpts |

See README files in each subdirectory for JSON schemas.

### 8.4 Statistical metrics (for future validation)

`validation.metrics` provides `spearman_correlation`, `kendall_tau`, `root_mean_square_error`, `mean_absolute_error`, `bootstrap_ci`, and a Krippendorff α placeholder.

---

## 9. Interpretability and sensitivity

### 9.1 Explain reports

```python
from core import calculate_metrics, explain_vertical_slice, format_interpretability_report

resultados, _, _ = calculate_metrics(input_data)
print(explain_vertical_slice(resultados))
print(format_interpretability_report(resultados))
```

These functions produce human-readable text citing subindices, metadata warnings, and composite decomposition.

### 9.2 Sensitivity analysis

```python
from core import run_sensitivity_analysis, format_sensitivity_report

sensitivity = run_sensitivity_analysis(input_data)
print(format_sensitivity_report(sensitivity))
```

**Important:** Sensitivity sweeps show **robustness to parameter changes** — they are not empirical validation. Optional `include_lambda=True` varies the interval-decay parameter.

---

## 10. Quality gates and CI

Phase 10 added automated quality checks (see `tests/test_quality_gates.py` and `.github/workflows/tests.yml`):

| Gate | Threshold / status (2026-07-12) |
|------|--------------------------------|
| Full test suite | **1542 passed / 2 skipped / 18 xfailed** (methodology `5.1.0-strict-symbolic`, package `1.1.4`; Python 3.10–3.11 on GitHub Actions and CircleCI) |
| Full-project coverage | ≥ 63% (CI quality job) |
| Core + validation coverage | ≥ 80% |
| Mypy (core, validation) | Zero errors with `--follow-imports=skip` |
| Finite outputs | All synthetic cases produce finite `density.*` scalars |
| Performance | 50-note slice completes in < 5 s (`@pytest.mark.slow`) |
| Import hygiene | `core/` and `validation/` modules must not import Tkinter |

**Verification layers:** interval-density contracts; instrument registry scaffold; musicological plausibility; Excel importer contracts; **string musicological battery (PR #13)**; **media note-label normalization (PR #14)**; **adaptive dynamic tails (`tests/test_adaptive_dynamic_tails.py`)**; **density stress battery (PR #37)** — controlled public-API scenarios A–E via `run_stress_battery.py` (report/CSV/figures; analysis-only, no formula change). These verify symbolic/metadata-level behaviour — not final acoustic calibration or auditory validation.

**CI limitation:** string source-reconstruction tests require local Zenodo workbooks; skipped on runners without `D:\CORDAS\` paths (violin/viola are the two suite skips until deposited; cello/double_bass reconstruction passes when workbooks are present). The stress battery is **local/analysis** (not a CI gate); regenerate report after intentional metric changes.

Run locally:

```bash
pytest tests/ -q --no-cov -m "not slow" -o addopts=
pytest -m musicological -q
pytest tests/test_stress_battery_registry.py -q
python run_stress_battery.py
pytest tests/ -q -o addopts= --cov=core --cov=validation --cov-fail-under=80
mypy core validation --ignore-missing-imports --follow-imports=skip
python -c "import importlib; importlib.import_module('Main'); print('OK')"
```

Stress battery details: [`tests/stress/README.md`](../tests/stress/README.md). Working artifacts: `STRESS_TEST_REPORT.md`, `stress_results.csv`, `stress_figures/` (gitignored). Tracked archives: `reports/STRESS_TEST_REPORT_v1.md` (pre D6 hotfix) and `v2.md` (post-hotfix).

---

*Last updated: 2026-08-18 (symmetric octave-class harmonic ratio; §3.4 cross-ref to Mathematical Manual §H; `.md` canonical over archival PDF).*
