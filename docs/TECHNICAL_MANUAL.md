# Technical Manual: Textural Density

This document is a comprehensive, pedagogical technical manual for **Textural Density**. It bridges high-level design and low-level mathematical implementation.

**Math formatting:** All formulas use **LaTeX** — inline math in `$...$`, display math on **separate lines** as `$$` … `$$` (StackEdit, Stack Exchange MathJax, KaTeX, GitHub, VS Code Markdown Math). Use `\cdot`, `\times`, or `\log_{10}(1+x)`; avoid bare Unicode operators inside expressions.

**Epistemic premise (strictly symbolic):** Score/information input only — no audio waveforms, no measured spectra, no auditory perception model, no FFT/STFT at runtime, no EWSD, no SoundSpectrAnalyse H/I/S integration. Textural Density computes analytical density indices from notated/input symbolic events and symbolic metadata only. It does not generate non-notated virtual pitches and does not implement acoustic, psychoacoustic, or perceptual modelling. See [revised_path_to_90_score_only.md](revised_path_to_90_score_only.md).

**Auxiliary tooling:** Excel/importer scripts under `tools/` are offline metadata-curation helpers — not part of this analytical core. See [instrument_profile_importer.md](instrument_profile_importer.md).

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
- **Layered metrics:** Raw densities → normalised weighted density → **pitch-structure density** (distinct bins) → composite vertical density with sonic-mass boost.
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
├── coarse_default.py          # Fallback for unknown instruments
└── *.py                       # Per-instrument GPR modules

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
| **`xml_loader.parse_xml` / `parse_xml_to_events`** | Load custom `<densidade_analysis>` or MusicXML; apply `<transpose>` for concert pitch. |
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
  - `calcular_densidade(nota, dinamica)` → float
  - `predict_intermediate_dynamics(pitches, pp_values, mf_values, ff_values)` → dict of arrays
- Modules embed **sparse acoustic amplitude tables** (`spectral_data`) obtained from **external sources** (literature / measurement summaries), interpolated by Gaussian-process regression (GPR). This is **not** runtime audio analysis.
- **`instrumentos/registry.py`** maps names/aliases to profiles with `profile_status` (`literature_derived`, `empirical_source`, `coarse_default`) and `uncertainty`.
- Instruments **without** GPR tables use coarse register/dynamic models only (`coarse_default`).
- **Per-event resolution:** each note uses its own instrument module via `core/orchestration.py`.
- Unknown instruments fall back to generic coarse profile with warnings in `metric_metadata`.

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

- **Spectral spread (pitch range in semitones):**
  $$A_{\mathrm{st}} = \max_k m_k - \min_k m_k \quad \text{(over distinct aggregated pitch bins)}.$$
  Used in bounded registral compactness $1/(1 + A_{\mathrm{st}}/12)$ — not as a singular divisor for density.

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
  Defaults: $D_{\mathrm{inst,max}} = 100$, $D_{\mathrm{int,max}} = 10$ (parameters `DI_max`, `DV_max`).

- **Alternative: z-score normalisation** (method `"z-score"`): $\widehat{D}_{\mathrm{inst}} = (D_{\mathrm{inst}} - \mu_{\mathrm{inst}})/\sigma_{\mathrm{inst}}$, $\widehat{D}_{\mathrm{int}} = (D_{\mathrm{int}} - \mu_{\mathrm{int}})/\sigma_{\mathrm{int}}$ with configurable $\mu$, $\sigma$ (example values in code: $\mu_{\mathrm{inst}}=50$, $\sigma_{\mathrm{inst}}=25$; $\mu_{\mathrm{int}}=5$, $\sigma_{\mathrm{int}}=2.5$).

- **Weighted combination** (weight $w \in [0,1]$, `weight_factor` in input):
  $$D_{\mathrm{pond}} = 10 \cdot \bigl( w \, \widehat{D}_{\mathrm{inst}} + (1-w) \, \widehat{D}_{\mathrm{int}} \bigr).$$
  $$D_{\mathrm{pond}} = 10 \cdot \bigl( w \, \widetilde{D}_{\mathrm{inst}} + (1-w) \, \widetilde{D}_{\mathrm{int}} \bigr).$$
  So $w=0$ uses only interval density, $w=1$ only instrument density.

### 3.5 Pitch-structure and composite vertical density

- **Pitch-structure density** (`density.pitch_structure`, alias `density.refined`):
  Zero when `distinct_pitch_count < 2`. Otherwise:
  $$D_{\mathrm{pitch}} = D_{\mathrm{int}}^{\mathrm{norm}} \cdot \frac{1}{1 + A_{\mathrm{st}}/12} \cdot (1 + \ln(1+H)) \cdot (1 - 0.15 \cdot r_{\mathrm{harm}}),$$
  where $H$ is spectral entropy and $r_{\mathrm{harm}}$ is harmonic ratio — both computed over **distinct pitch bins** with mean weight per bin.

- **Composite vertical density:**
  $$D_{\mathrm{total}} = \log_{10}\!\left(1 + \frac{D_{\mathrm{pitch}} \cdot \sqrt{M_{\mathrm{sonic}}}}{D_{\max}}\right)$$
  (when log compression enabled). Sonic mass $M_{\mathrm{sonic}}$ remains event-based; it cannot alone make exact unison the highest vertical-density case.

### 3.6 Sonic mass and dynamic boost

Implemented in `core/orchestration_mass.py`; result used as `dynamic_boost = sqrt(M)`.

**Dynamic treatment:** Written dynamics are applied **once** via instrument-module GPR lookup (`calcular_densidade(note, dynamic)`). The mass formula does **not** apply a second symbolic dynamic multiplier.

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

- **Definition:** Ratio of energy in “harmonic” bins (pitches within ±0.25 semitons of a multiple of 12 semitons above the fundamental) to total energy. Fundamental is $m_{\min}$ if not provided.
  $$\mathrm{harmonicRatio} = \frac{ \sum_{i \in \mathcal{H}} a_i }{ \sum_i a_i }, \quad \mathcal{H} = \bigl\{ i : \bigl| (m_i - m_{\min}) \bmod 12 \bigr| \leq 0.25 \text{ (in code: } \mathrm{isclose}((m_i - m_{\min}) \bmod 12, 0, \mathrm{atol}=0.25) \bigr\}.$$
  If total energy is 0, the ratio is 0.

### 3.11 Complexity factor (pitch-structure path)

Spectral entropy $H$ enters **pitch-structure density** only (not a separate cohesion multiplier):

$$C_{\mathrm{comp}} = 1 + \ln(1 + H).$$

> **Removed:** cohesion factor $C_{\mathrm{coes}} = 10/(1 + A_{\mathrm{st}})$ in the composite product.

### 3.12 Total density (final formula)

- **Unnormalised total** (current composite):
  $$D_{\mathrm{total}}^{\mathrm{raw}} = \frac{D_{\mathrm{pitch}} \cdot \sqrt{M_{\mathrm{sonic}}}}{D_{\max}}.$$

- **Optional log compression** (when `USE_LOG_COMPRESSION` is True):
  $$D_{\mathrm{total}} = \log_{10}(1 + D_{\mathrm{total}}^{\mathrm{raw}}).$$
  Otherwise $D_{\mathrm{total}} = D_{\mathrm{total}}^{\mathrm{raw}}$.

### 3.13 Absolute density (reference)

- **Tone count:** $N_{\mathrm{tones}} = n$ (number of notated/input symbolic events).

- **Absolute density** (code: `np.log1p(total_tones_count)`):
  $$D_{\mathrm{abs}} = D_{\mathrm{pond}} \cdot \ln(1 + N_{\mathrm{tones}}).$$

### 3.14 Texture metrics (summary)

Implemented in `calculate_texture_density(pitches, instruments_counts)`.

- **Average texture density:** $\sum_i n_{\mathrm{instr},i}$.
- **Texture polyphony:** $\frac{1}{n}\sum_i n_{\mathrm{instr},i}$ (mean instruments per note).
- **Texture variability:** standard deviation of $m_i$ (semitons).
- **Texture contrast:** $\max_i m_i - \min_i m_i$ (semitons).

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
    "instruments": ["flauta", "flauta", "clarinete"],
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

7. **Pitch-structure density:** $D_{\mathrm{pitch}} = D_{\mathrm{int}}^{\mathrm{norm}} \cdot \frac{1}{1 + A_{\mathrm{st}}/12} \cdot (1 + \ln(1+H)) \cdot (1 - 0.15 \cdot r_{\mathrm{harm}})$ over distinct bins.

8. **Spectral moments:** On distinct-bin MIDI pitches with mean weight per bin; compute centroid, spread, entropy, etc.

9. **Chroma and harmonic ratio:** From distinct pitch bins only.

10. **Sonic mass:** $M_{\mathrm{sonic}} = \sum_i d_i^{(1)} \cdot n_i$ (linear Qty; here $n_i=1$); $\mathrm{boost} = \sqrt{M_{\mathrm{sonic}}}$.

11. **Composite vertical density:** $D_{\mathrm{total}}^{\mathrm{raw}} = D_{\mathrm{pitch}} \cdot \sqrt{M_{\mathrm{sonic}}} / D_{\max}$; optional $\log_{10}(1+x)$.

12. **Absolute density:** $D_{\mathrm{abs}} = D_{\mathrm{pond}} \cdot \ln(1 + N_{\mathrm{events}})$ when $n_{\mathrm{distinct}} \geq 2$; else 0.

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
| Event count | Number of notated input rows |
| Player count | Sum of Qty |
| Pitch polyphony | Distinct simultaneous pitch bins |
| Player doubling count | Player count − distinct pitch count |
| Instrument density | Pressure-equivalent RSS proxy |
| Sonic / orchestral mass | Linear sum(qty × one-player density) |

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
events = [make_instrument_event(0, "C4", "mf", "flauta", 1, onset=0.0, duration=2.0), ...]
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

**Concert pitch (transposing instruments):** When a part declares `<attributes><transpose>`, written pitch is converted to **sounding/concert pitch** before metrics run:

$$
m_{\mathrm{sounding}} = m_{\mathrm{written}} + \Delta_{\mathrm{chromatic}} + 12 \cdot \Delta_{\mathrm{octave\_change}}
$$

Example: B♭ clarinet with `<chromatic>-2</chromatic>` — written C4 → sounding B♭3.

| Function | Returns | Notes |
|----------|---------|-------|
| `parse_xml(path)` | Legacy dict (`notes`, `dynamics`, …) | `notes` are **concert** pitches for MusicXML |
| `parse_xml_to_events(path)` | `(events, options, warnings)` | Sets `written_pitch` when it differs from `sounding_pitch` |

**Limitations (documented):**

- Untimed MusicXML is treated as **one vertical slice** (warning emitted).
- Global onset times are **not** reconstructed from cumulative `<duration>` unless explicit `<onset>` is present in custom XML.
- Parser is hand-rolled (`xml.etree`); it does not use music21. Transposition follows MusicXML `<transpose>` elements only.

Tests: `tests/test_xml_loader.py::TestMusicXmlTranspose`. Benchmarks: `benchmarks/corpus/excerpt_003.musicxml`–`excerpt_004.musicxml` (transpose); see [`benchmarks/README.md`](../benchmarks/README.md).

---

## 8. Validation and verification

### 8.1 Verification vs validation

| Term | Meaning in Textural Density |
|------|----------------|
| **Verification** | Synthetic cases + property checks confirming implementation correctness |
| **Validation** | Comparison against expert ratings, listening tests, or corpus benchmarks |

Current status: **`verified_only`** — no external validation corpora loaded by default.

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

| Gate | Threshold |
|------|-----------|
| Core + validation coverage | ≥ 80% |
| Full project coverage | ≥ 63% |
| Mypy (core, validation) | Zero errors with `--follow-imports=skip` |
| Finite outputs | All synthetic cases produce finite `density.*` scalars |
| Performance | 50-note slice completes in < 5 s |
| Import hygiene | `core/` and `validation/` modules must not import Tkinter |

Run locally:

```bash
pytest tests/ -q --no-cov
pytest tests/ -q -o addopts= --cov=core --cov=validation --cov-fail-under=80
mypy core validation --ignore-missing-imports --follow-imports=skip
```

---

*Last updated: 2026-06-01 (package 1.1.1; MusicXML transpose §7.4; see VERSIONING.md).*
