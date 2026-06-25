# Mathematical Manual & Tutorial — Textural Density

This document is the **canonical reference** for **equations, algorithms, and models** implemented in **Textural Density**, plus a **pedagogical tutorial** for reading results and tuning parameters.

**Epistemic premise:** Textural Density is a strictly symbolic score-analysis framework. It computes analytical density indices from symbolic score data and symbolic metadata. It does **not** implement an auditory model. Unless explicitly labelled `empirical`, spectral and orchestration outputs are **metadata proxies** — not measured acoustics.

**Removed in 3.0.0-strict-symbolic:** Stevens' Law, psychoacoustic corrections (masking, roughness, loudness, Bark), and perceptual interval weighting. Sections C–E and Stevens portions of G below are retained only as migration reference; they are not active options.

### LaTeX format (StackEdit, MathJax, KaTeX, GitHub)

All mathematics is written in **LaTeX** using:

| Delimiter | Use |
|-----------|-----|
| `$ ... $` | Inline math, e.g. `$f(m) = 440 \cdot 2^{(m-69)/12}$` |
| `$$` on its own line | Display (block) math: open with `$$`, equation, close with `$$` on a new line |

This matches **StackEdit**, **Stack Exchange** (MathJax), **VS Code** (Markdown Math), **GitHub**, and **KaTeX**. Do not use bare Unicode superscripts or the `·` character for multiplication inside formulas; use `\cdot`, `\times`, or `\log_{10}(1+x)` as below.

---

## Table of contents

1. [Notation and conventions](#1-notation-and-conventions)
2. [Models by item (formula catalog)](#2-models-by-item-formula-catalog)
   - [A. Pitch and frequency](#a-pitch-and-frequency)
   - [B. Interval density (pairwise decay)](#b-interval-density-pairwise-decay)
   - [C. Optional perceptual weighting (pairwise)](#c-optional-perceptual-weighting-pairwise)
   - [D. Interval density — psychoacoustic path](#d-interval-density--psychoacoustic-path)
   - [E. Psychoacoustic primitives (Bark, masking, roughness, loudness)](#e-psychoacoustic-primitives-bark-masking-roughness-loudness)
   - [F. Instrument density and sonic mass](#f-instrument-density-and-sonic-mass)
   - [G. Weighted density (normalisation + Stevens)](#g-weighted-density-normalisation--stevens)
   - [H. Pitch-structure density and composite vertical density](#h-pitch-structure-density-and-composite-vertical-density)
   - [I. Spectral moments, chroma, harmonic ratio](#i-spectral-moments-chroma-harmonic-ratio)
   - [J. Texture, timbre blend, orchestration](#j-texture-timbre-blend-orchestration)
   - [L. $\lambda$ calibration](#l-λ-calibration)
   - [M. Epistemic taxonomy and `metric_metadata`](#m-epistemic-taxonomy-and-metric_metadata)
   - [N. Density subindices (`density_subindices`)](#n-density-subindices-density_subindices)
   - [O. Temporal score analysis](#o-temporal-score-analysis)
   - [P. MusicXML transposition (concert pitch)](#p-musicxml-transposition-concert-pitch)
   - [Q. Verification properties (synthetic)](#q-verification-properties-synthetic)
3. [End-to-end pipeline (diagram)](#3-end-to-end-pipeline-diagram)
4. [Pedagogical tutorial](#4-pedagogical-tutorial)
5. [Glossary](#5-glossary)
6. [Code index](#6-code-index)

---

## 1. Notation and conventions

| Symbol | Meaning |
|--------|---------|
| $m_i$ | MIDI pitch (real-valued; microtones allowed) |
| $f$ | Frequency in Hz |
| $n$ | Number of notes in the vertical (same as `len(notes)`) |
| $a_i$ | Non-negative weight for pitch $i$ (instrument densities from symbolic metadata) |
| $S = \sum_i a_i$ | Total weight (for spectral moments) |
| $\lambda$ | Decay parameter for interval density (`DEFAULT_LAMBDA` or calibrated) |
| $\delta$ | Distance in **microtonal steps** (24 per octave in this system); linked to semitone distance $\Delta_{\mathrm{st}}$ by $\delta = 2\Delta_{\mathrm{st}}$ in the default path |

The application is **symbolic**: it does not analyse audio waveforms; it computes metrics from **note names**, **dynamics**, and **instrument tags**.

---

## 2. Models by item (formula catalog)

### A. Pitch and frequency

**Module:** `microtonal.py` (`midi_to_hz`, `hz_to_midi`, `note_to_midi`, …).

**Equal temperament (continuous MIDI):**

$$
f(m) = f_{\mathrm{A4}} \cdot 2^{(m - m_{\mathrm{A4}})/12}, \quad f_{\mathrm{A4}} = 440\,\mathrm{Hz},\; m_{\mathrm{A4}} = 69.
$$

**Inverse:**

$$
m = m_{\mathrm{A4}} + 12 \log_2\!\left(\frac{f}{f_{\mathrm{A4}}}\right), \quad f > 0.
$$

**Semitone span of a chord:**

$$
A_{\mathrm{st}} = \max_i m_i - \min_i m_i \quad (\text{pitch span from notated/input symbolic events}).
$$

---

### B. Interval density (pairwise decay)

**Module:** `densidade_intervalar.py` — `modified_exponential_decay`, `calculate_interval_density`.

**Microtonal distance** for a pair $(i,j)$:

$$
\Delta_{\mathrm{st}}(i,j) = |m_i - m_j|, \qquad \delta(i,j) = 2 \cdot \Delta_{\mathrm{st}}(i,j).
$$

(If two *different* note strings yield $\Delta_{\mathrm{st}} < 0.01$ semitones due to float noise, the code may force a minimum step of $0.25$ semitones before computing $\delta$.)

**Decay (unison = strongest contribution):**

$$
\phi(\delta;\lambda) = \begin{cases}
1 & \delta = 0 \\
e^{-\lambda \delta} & \delta > 0
\end{cases}
$$

with $\lambda$ from `load_calibrated_parameters()` or an explicit argument.

**Raw interval density** (sum over unordered pairs):

$$
D_{\mathrm{int}}^{\mathrm{raw}} = \sum_{i<j} \phi\bigl(\delta(i,j);\lambda\bigr).
$$

**Normalised interval density** (average per unordered pair):

$$
\bar{D}_{\mathrm{int}} = \frac{2\,D_{\mathrm{int}}^{\mathrm{raw}}}{n(n-1)} \quad (n \ge 2).
$$

If `USE_LOG_COMPRESSION` is true (`config.py`):

$$
\bar{D}_{\mathrm{int}} \leftarrow \log_{10}(1 + \bar{D}_{\mathrm{int}}).
$$

---

### C. [REMOVED] Perceptual interval weighting

Removed in **3.0.0-strict-symbolic**. Analytical input containing `use_perceptual_weighting` raises `InputError`.

---

### D. [REMOVED] Psychoacoustic interval path

Removed in **3.0.0-strict-symbolic**. Analytical input containing `use_psychoacoustic` raises `InputError`.

---

### E. [REMOVED] Psychoacoustic primitives

Removed in **3.0.0-strict-symbolic** (`psychoacoustic_corrections.py` deleted).

---

### F. Instrument density and sonic mass

**Modules:** `instrumentos/*`, `core/quantity_scaling.py`, `core/source_aggregation.py`, `core/orchestration.py`, `core/orchestration_mass.py`.

Each note uses **its own instrument module**. Unknown instruments fall back to `coarse_default`.

**One-player density** (dynamic applied once in module lookup):

$$
d_j^{(1)} = \texttt{calcular\_densidade}(\text{note}, \text{dynamic}).
$$

Source groups merge identical (MIDI pitch, instrument, dynamic) rows so one row with Qty = N equals N rows with Qty = 1.

**Pressure-equivalent instrument density** (incoherent RSS):

$$
D_{\mathrm{inst}} = \sqrt{\sum_j n_j \cdot \bigl(d_j^{(1)}\bigr)^2}.
$$

**Sonic mass** (linear player scaling; no second dynamic multiplier):

$$
M_{\mathrm{sonic}} = \sum_j n_j \cdot d_j^{(1)}, \qquad \text{boost} = \sqrt{M_{\mathrm{sonic}}}.
$$

Qty does **not** affect pitch-structure metrics (interval pairs, spectral entropy, pitch polyphony, etc.).

---

### G. Weighted density (linear min-max blend)

**Module:** `core/composite.py` — `compute_weighted_density_normalized`.

**Min–max** (default):

$$
\widehat{D}_{\mathrm{inst}} = \frac{D_{\mathrm{inst}}}{D_{\mathrm{inst,max}}}, \quad
\widehat{D}_{\mathrm{int}} = \frac{D_{\mathrm{int}}}{D_{\mathrm{int,max}}}.
$$

**Blend:**

$$
D_{\mathrm{pond}} = 10 \cdot \bigl( w \, \widehat{D}_{\mathrm{inst}} + (1-w)\, \widehat{D}_{\mathrm{int}} \bigr), \quad w \in [0,1].
$$

> **Removed:** Stevens power-law (`use_stevens`, `alpha`, `beta`) — see [MIGRATION.md](MIGRATION.md).

---

### H. Pitch-structure density and composite vertical density

**Modules:** `core/pitch_aggregation.py`, `core/pitch_structure.py`, `core/pipeline.py`.

Textural Density separates **orchestral mass** from **vertical pitch structure**. Exact unison doublings increase event/mass descriptors but do not create additional interval structure, spectral entropy, or registral diversity.

**Pitch aggregation:** events merge by exact MIDI (tolerance $10^{-6}$). Interval compactness, spectral moments, chroma, and harmonic ratio use **distinct pitch bins** with mean weight per bin (invariant under within-bin doublings).

**Pitch-structure density** ($n_{\mathrm{distinct}} \geq 2$ required):

$$
D_{\mathrm{pitch}} = D_{\mathrm{int}}^{\mathrm{norm}} \cdot \frac{1}{1 + A_{\mathrm{st}}/12} \cdot (1 + \ln(1 + H)) \cdot (1 - 0.15 \cdot \mathrm{harmonicRatio}).
$$

If $n_{\mathrm{distinct}} < 2$, $D_{\mathrm{pitch}} = 0$.

**Composite vertical density:**

$$
D_{\mathrm{total}}^{\mathrm{raw}} = \frac{D_{\mathrm{pitch}} \cdot \sqrt{M_{\mathrm{sonic}}}}{D_{\max}}.
$$

Optionally apply $\log_{10}(1 + x)$ if `USE_LOG_COMPRESSION`.

> **Removed:** `D_{\mathrm{ref}} = D_{\mathrm{pond}}/A_{\mathrm{st}}` with zero-span exemption; cohesion factor $10/(1+A_{\mathrm{st}})$ in the composite product.

**Absolute density** (reference, unchanged):

$$
D_{\mathrm{abs}} = D_{\mathrm{pond}} \cdot \ln(1 + N_{\mathrm{events}}).
$$

---

### I. Spectral moments, chroma, harmonic ratio

**Module:** `spectral_analysis.py`.

**Moments** on pitches $m_i$ with weights $a_i$:

$$
\mu = \frac{1}{S}\sum_i a_i m_i, \quad
\sigma^2 = \frac{1}{S}\sum_i a_i (m_i-\mu)^2, \quad
\gamma_1 = \frac{\frac{1}{S}\sum_i a_i (m_i-\mu)^3}{\sigma^3}\ (\sigma>0).
$$

**Excess kurtosis:**

$$
\gamma_2 = \frac{\frac{1}{S}\sum_i a_i (m_i-\mu)^4}{\sigma^4} - 3.
$$

**Flatness:** ratio of geometric to arithmetic mean of amplitudes (on $a_i > 10^{-10}$).

**Roll-off (85%):** cumulative sum of $a_i$ in array order; MIDI at 85% cumulative energy mapped to Hz.

**Entropy:** $H = -\sum_i p_i \log_2 p_i$, $p_i = a_i/S$, with small $p_i$ filtered.

**Chroma:** $c_i = \mathrm{round}(m_i) \bmod 12$, energies summed per class and normalised.

**Harmonic ratio:** fundamental $m_{\min}$; energy in bins with $(m_i - m_{\min}) \bmod 12 \approx 0$ (atol `0.25`).

---

### J. Texture, timbre blend, orchestration

**Module:** `timbre_texture_analysis.py`.

**Texture** (`calculate_texture_density`) on **distinct pitch bins**:

- `player_count` / `player_weighted_texture_mass` $= \sum_i n_{\mathrm{instr},i}$ (total players)
- `pitch_polyphony` $= n_{\mathrm{distinct}}$ (distinct pitch bins — **not** mean Qty)
- `texture_polyphony` — alias of `pitch_polyphony` (legacy key)
- `texture_variability` $= \mathrm{std}(m_i)$
- `texture_contrast` $= \max m_i - \min m_i$

**Timbre blend** (`calculate_timbre_blend`):

- `timbre_diversity` $= |\{\text{unique instruments}\}| / n$
- For each instrument $k$, average density $\bar{d}_k$; `density_variance` $= \mathrm{Var}_k(\bar{d}_k)$
- `blend_index` $= 1 / (1 + \sigma_d^2)$ where $\sigma_d^2 = \mathrm{Var}_k(\bar{d}_k)$ (`density_variance` in code)

**Orchestration** (`calculate_orchestration_balance`): split registers **baixo** $[0,48)$, **médio** $[48,72)$, **agudo** $[72,108)$. Sum densities per register; normalise to $p_r$, $r \in \{1,2,3\}$.

- **Register balance** (normalised entropy):

$$
R_{\mathrm{reg}} = \frac{-\sum_{r: p_r>0} p_r \log_2 p_r}{\log_2 3}.
$$

- **Density balance:** `1 - (max(p) - min(p))` over the three registers.

- **Gini** on sorted normalised register masses; **evenness** $= 1 - |\mathrm{Gini}|$.

---

### L. $\lambda$ calibration

**Module:** `densidade_intervalar.py` — `calibrate_lambda`.

Reference ratings `CONSONANCE_RATINGS` map interval classes to empirical scores. Dyad intervals are built with `utils/notes.dyad_notes_from_semitone_interval()` (Phase 4 fix). For candidate $\lambda$, minimise squared error between predicted normalised density and ratings (see [Technical Manual](TECHNICAL_MANUAL.md), Section 3.15). Optimal $\lambda$ is saved to `config/density_params.json`.

---

### M. Epistemic taxonomy and `metric_metadata`

**Modules:** `core/models.py`, `core/metrics_metadata.py`.

Every scalar in `resultados["density"]` is mirrored in `resultados["metric_metadata"]` with explicit epistemic fields:

| Field | Values | Meaning |
|-------|--------|---------|
| `source_type` | `score_derived`, `external_acoustic_metadata`, `metadata_proxy`, `calibrated_proxy`, `empirical` | How the value was obtained |
| `validation_status` | `theoretical`, `verified_only`, `partially_calibrated`, `externally_validated`, `heuristic` | Evidence level |
| `confidence` | `high`, `medium`, `low` | Reporting confidence |

Each metric entry includes `value`, optional `raw_value` / `normalized_value`, `interpretation`, `warnings`, and `assumptions`. Global blocks document normalization constants (`MAX_DENS_GLOBAL`, `USE_LOG_COMPRESSION`, weighted-density maxima).

**Rule:** Instrument GPR tables are **`external_acoustic_metadata`** (sparse externally sourced amplitude data, GPR-interpolated at analysis time). They must not be cited as full measured spectra or as live audio analysis. Registry-only coarse profiles are **`metadata_proxy`**. Removed branches (Stevens' Law, psychoacoustic corrections, perceptual interval weighting, combination tones) are no longer available.

---

### N. Density subindices (`density_subindices`)

**Module:** `core/subindices.py` — `build_density_subindices`.

Decomposes the composite score into interpretable components. Legacy scalars in `density.*` are unchanged; subindices add structured context.

| Subindex | Key quantities | Default `source_type` |
|----------|----------------|------------------------|
| `event_count` | event count, player-weighted count, duration-weighted count | `score_derived` |
| `interval_compactness` | raw vs reported interval density | `score_derived` / `metadata_proxy` |
| `registral` | pitch span, band occupancy, register entropy | `score_derived` |
| `orchestral_mass` | sonic mass scalar | `metadata_proxy` |
| `timbral_heterogeneity` | family/instrument diversity, blend | `metadata_proxy` |
| `harmonicity_proxy` | harmonic ratio, chroma concentration | `metadata_proxy` |
| `temporal` | timing availability, duration-weighted count | `score_derived` when timed |
| `composite` | component product and dominant factors | `metadata_proxy` |

**Register band occupancy** (default bands in `config.DEFAULT_REGISTER_BANDS`): for MIDI pitches $m_i$, count events per band $b$ with bounds $[L_b, U_b)$:

$$
O_b = \frac{|\{i : L_b \le m_i < U_b\}|}{n}.
$$

**Register entropy** (normalised):

$$
H_{\mathrm{reg}} = \frac{-\sum_b O_b \log_2 O_b}{\log_2 B}, \quad B = \text{number of bands}.
$$

**Registral compression:**

$$
C_{\mathrm{reg}} = \frac{1}{1 + A_{\mathrm{st}}}.
$$

**Duration-weighted event count** (when all events have resolvable duration $d_i$):

$$
N_{\mathrm{dur}} = \sum_i n_{\mathrm{instr},i} \cdot d_i.
$$

**Composite vertical density** (current assembly):

$$
D_{\mathrm{total}}^{\mathrm{raw}} = \frac{D_{\mathrm{pitch}} \cdot \sqrt{M_{\mathrm{sonic}}}}{D_{\max}}.
$$

With `COMPOSITE_HARMONIC_DAMPING = 0.15` applied inside $D_{\mathrm{pitch}}$. Final total applies optional $\log_{10}(1+x)$.

> **Removed:** $\Pi = D_{\mathrm{ref}} \cdot C_{\mathrm{coes}} \cdot C_{\mathrm{comp}} \cdot (1 - \mathrm{harmonicRatio} \cdot \texttt{COMPOSITE\_HARMONIC\_DAMPING}) \cdot \sqrt{M}$.

---

### O. Temporal score analysis

**Modules:** `core/temporal.py`, `core/score_analysis.py`.

Timed `InstrumentEvent` objects carry optional `onset`, `offset`, `duration` (seconds). Activity at instant $t$ uses half-open interval $[\mathrm{onset}, \mathrm{offset})$.

**Modes** (`group_events_into_slices`):

- **`event_boundary`:** one vertical slice at each distinct onset; active set = all events sounding at that boundary.
- **`instantaneous`:** single slice containing all events (ignores timing for segmentation).

`analyze_score(source, config)` accepts a file path (`.xml`, `.mid`), legacy input dict, or `list[InstrumentEvent]`. It runs `calculate_metrics` per slice and returns `ScoreAnalysisResult` with `slices[]`, `time_series[]`, and `global_summary{}`.

When input lacks timing metadata, analysis collapses to a single slice with an explicit assumption warning.

---

### P. MusicXML script pitch (transpose not applied)

**Module:** `xml_loader.py` — `_transpose_semitones_from_attributes` (metadata only).

MusicXML may declare **written** pitch in `<pitch>` and an offset in `<attributes><transpose>`. Textural Density analyses the notated pitch as shown on the part:

$$
m_{\mathrm{analysed}} = m_{\mathrm{written}}.
$$

The declared transpose offset is stored in event metadata (`transpose_semitones`) but is **not** subtracted or added at runtime. All pitch-structure metrics use this script pitch.

**Not applied at runtime:** chromatic/octave transpose conversion; registry `transposition` field; diatonic spelling-only transposition without chromatic offset.

---

### Q. Verification properties (synthetic)

**Module:** `validation/verification.py` — `run_verification_suite()`.

These are **implementation correctness checks**, not empirical validation:

| Property | Expected behaviour |
|----------|-------------------|
| Finite outputs | All `density.*` scalars finite for synthetic cases |
| Chromatic vs wide | Interval density higher for chromatic cluster than wide-spaced chord |
| Player mass | Orchestral mass increases linearly with Qty; pressure-equivalent instrument density scales as RSS; interval/pitch-structure unchanged |
| Qty vs pitch structure | Qty does not increase pitch polyphony, interval pairs, or spectral entropy for unison doublings |
| Dynamic monotonicity | Sonic mass increases from `pp` to `ff` at fixed pitch (via module lookup, applied once) |
| Row-splitting | One row Qty=N ≡ N identical rows Qty=1 for mass and pressure-equivalent density |
| Duplicate events | Duplicated pitch rows increase player/event counts; pitch structure uses aggregated bins |

External expert/listening/corpus validation requires annotated JSON in `validation/expert_annotations/`, `validation/listening_tests/`, and `validation/corpus_examples/`. Until then, status is **`verified_only`**.

**String GPR modules (2026-06):** an additional musicological contract battery (`pytest -m musicological`, PR #13) and viola media note-label normalization (PR #14) verify source-table alignment and symbolic invariants — not perceptual CDM validation. See [TECHNICAL_MANUAL.md](TECHNICAL_MANUAL.md) §8 and [instrument_acoustic_sources.md](instrument_acoustic_sources.md).

---

## 3. End-to-end pipeline (diagram)

```mermaid
flowchart TD
  subgraph Input
    N[Notes + dynamics + instruments + counts]
    T[Optional onset/offset/duration]
  end

  subgraph Temporal
    SL[Group events into vertical slices]
  end

  subgraph Interval
    DI[Interval density: pairwise pitch-distance decay]
  end

  subgraph Instrument
    REG[Registry resolves per-event module]
    INST[One-player densities d_j^(1)]
    AGG[Source groups: pitch + instrument + dynamic]
    DINST[RSS pressure-equiv: sqrt(sum n_j d_j^2)]
    MASS[Linear mass: sum n_j d_j]
  end

  subgraph PitchStructure
    PBIN[Aggregate distinct pitch bins]
    DPITCH[Pitch-structure density]
  end

  subgraph Fusion
    W[Weighted linear blend + min-max]
  end

  subgraph Spectral
    SP[Spectral moments + chroma + harmonic ratio]
    TX[Texture + timbre + orchestration]
  end

  subgraph Epistemic
    META[metric_metadata labelling]
    SUB[density_subindices decomposition]
  end

  subgraph Out
    TOT[Total density + absolute + outputs]
  end

  N --> SL
  T --> SL
  SL --> PBIN --> DI
  SL --> REG --> INST --> AGG --> DINST
  AGG --> MASS
  DI --> DPITCH
  DINST --> W
  DI --> W
  DPITCH --> TOT
  MASS --> TOT
  PBIN --> SP
  SP --> TOT
  N --> TX
  TX --> TOT
  TOT --> META
  TOT --> SUB
```

---

## 4. Pedagogical tutorial

### 4.1 What problem does this solve?

**Vertical density** tries to quantify how “full” or “complex” a **simultaneity** (chord or cluster) is **at one moment in time**, using:

- **Interval content** (how intervals are spaced — exponential decay favours small $\delta$ in $\phi$),
- **Orchestration** (which instruments and how many),
- **Spectral shape** (moments, entropy, harmonic ratio) from notated/input symbolic pitches.

It is **not** voice-leading analysis, **not** rhythmic density, and **not** a full hearing model — it is a **consistent, tunable metric** for composition and analysis. Textural Density does not generate non-notated virtual pitches.

### 4.2 How to read one number

1. Look at **`density.interval`** vs **`density.instrument`**: is the chord “heavy” because of **intervals** or **timbre**?
2. Check **`density.weighted`** and **`density.refined`**: refined divides by pitch span — **wide spreads** reduce refined density unless compensated elsewhere.
3. Open **`density_subindices`**: inspect `interval_compactness`, `registral`, `orchestral_mass`, and `composite.components` for a decomposed reading.
4. Read **`metric_metadata`**: check `source_type`, `validation_status`, and `warnings` before citing a value in research writing.
5. **Spectral entropy** drives **`complexity`** in the total-density formula — **more spread-out** spectral distributions (higher entropy) increase the factor $C_{\mathrm{comp}}$.
6. **Harmonic ratio** (0–1) **reduces** total density slightly via $(1 - 0.15 \cdot \mathrm{harmonicRatio})$ — energy in harmonic rows relative to the lowest pitch is treated as “simpler”.

### 4.3 Lesson 1 — Minimal chord

Input three notes in the same octave with `weight_factor = 0.5`. Compare:

- **Major triad** vs **cluster** (minor seconds): interval density should be **higher** for the cluster (more close pairs, larger $\phi$).
- Increase **instrument** weight by setting `weight_factor` toward **1** — instrument modules dominate.

### 4.4 Lesson 2 — Parameters that matter most

| Parameter | Effect |
|-----------|--------|
| `weight_factor` (w) | Balance instrument vs interval density |
| `USE_LOG_COMPRESSION` | Flattens extreme values (config) |

### 4.5 Lesson 3 — Calibration

If you use **λ calibration**, run the calibration workflow from the menu (Tools → Calibration) or call `calibrate_lambda` with your own experimental data. The fitted $\lambda$ changes how fast $\phi$ decays with $\delta$ — **larger λ** penalises wide intervals more strongly.

### 4.6 Mini exercise (paper)

For two notes $m_1=60$, $m_2=64$, $\lambda=0.05$: compute $\delta = 8$, $\phi(\delta)=e^{-0.05\cdot 8}$. For three notes, sum **three** pairwise terms. Compare with $\lambda=0.2$.

---

## 5. Glossary

| Term | Meaning |
|------|---------|
| **Textural Density** | Research software for vertical symbolic density analysis |
| **Vertical** | One time-slice of simultaneous notes (not a score) |
| **Metadata proxy** | Symbolic estimate standing in for a perceptual quantity — not measured |
| **verified_only** | Passes synthetic/property checks; no external validation corpus yet |
| **MIDI** | Pitch in semitones; fractional MIDI = microtones |
| **Microtonal steps** | Internal 24-step octave grid; $\delta = 2 \cdot \Delta_{\mathrm{st}}$ in default pairing |
| **Subindex** | Interpretable component in `density_subindices` |

---

## 6. Code index

| Topic | Primary file(s) |
|-------|-----------------|
| Public API | `core/__init__.py` — `calculate_metrics`, `analyze_score` |
| Main pipeline | `core/pipeline.py` `calculate_metrics` |
| MusicXML intake / transpose | `xml_loader.py` |
| Per-event instruments | `core/orchestration.py`, `instrumentos/registry.py` |
| Epistemic metadata | `core/metrics_metadata.py` |
| Subindices | `core/subindices.py` |
| Temporal analysis | `core/temporal.py`, `core/score_analysis.py` |
| Interpretability | `core/reporting.py` |
| Verification | `validation/verification.py`, `validation/synthetic_cases.py` |
| Interval decay | `densidade_intervalar.py` |
| Spectral metrics | `spectral_analysis.py` |
| Texture / orchestration | `timbre_texture_analysis.py` |
| Pitch conversion | `microtonal.py` |
| Instruments | `instrumentos/*.py` |

For architecture and output JSON keys, see [TECHNICAL_MANUAL.md](TECHNICAL_MANUAL.md). For upgrading existing scripts, see [MIGRATION.md](MIGRATION.md). For package vs methodology versions, see [VERSIONING.md](VERSIONING.md). For function signatures, see [API.md](API.md).

*Last updated: 2026-06-01 (package 1.1.1; MusicXML transpose §P).*
