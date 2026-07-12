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
   - [F.1 Dynamic interpolation (GPR)](#f1-dynamic-interpolation-gpr)
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

**Modules:** `core/pitch_structure.py` — `calculate_interval_density_from_distinct_midis` (the **core distinct-bin path** reached from `core.calculate_metrics`); `densidade_intervalar.py` — `modified_exponential_decay`, `calculate_interval_density` (**legacy path**, see minimum-step note below).

**Microtonal distance** for a pair $(i,j)$:

$$
\Delta_{\mathrm{st}}(i,j) = |m_i - m_j|, \qquad \delta(i,j) = 2 \cdot \Delta_{\mathrm{st}}(i,j).
$$

**No minimum-interval step on the core path.** The core distinct-bin function applies **no floor**: sub-cent intervals are treated as real distances, so $\delta$ is computed directly from $\Delta_{\mathrm{st}}$ for every distinct-bin pair (e.g. $[C4, C4{+}0.5c]$ gives $\Delta_{\mathrm{st}} = 0.005$ and $\phi = e^{-\lambda \cdot 2 \cdot 0.005}$, unclamped). Genuine float-noise "unisons" cannot form a pair at all: they are absorbed **upstream** by the exact-MIDI pitch aggregation (`core/pitch_aggregation.py`, tolerance $10^{-6}$; §H), which merges pitches within tolerance into a single bin before any pairwise sum, so duplicate pitches never contribute an interval.

> **Legacy-path-only minimum step (0.25 st).** The legacy `densidade_intervalar.calculate_interval_density` still contains a guard that, for two *different* note strings whose $\Delta_{\mathrm{st}} < 0.01$ semitones, forces $\Delta_{\mathrm{st}} \leftarrow \max(\Delta_{\mathrm{st}}, 0.25)$ before computing $\delta$. This floor is **not reachable from `core.calculate_metrics`** — the pipeline uses the distinct-bin path above. The legacy function is invoked only by $\lambda$-calibration internals, offline tooling (`tools/refresh_regression_fixtures.py`), `validation/verification.py`, and unit tests. The paragraph is retained (not deleted) because that function and its floor still exist and are exercised by those non-core call sites; deleting the note would leave their behaviour undocumented.

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

### F.1 Dynamic interpolation (GPR)

**Module:** `instrumentos/gpr_dynamic_interpolation.py` — `create_dynamic_gpr()`, `predict_intermediate_dynamics()`.

Committed CDM tables store **source-anchor dynamics** only: `pp`, `mf`, `ff`. All other allowed markings are **modelled dynamic values** obtained at analysis time:

| Dynamic | Status |
|---------|--------|
| `pp` | source anchor |
| `p` | modelled (GPR) |
| `mp` | modelled (GPR at ordinal coordinate 4.5 between `p`=4.0 and `mf`=5.0) |
| `mf` | source anchor |
| `f` | modelled (GPR) |
| `ff` | source anchor |
| `p`, `mp`, `f` | **interior** modelled (GPR **inside** measured support) |
| `pppp`, `ppp`, `fff`, `ffff` | **tail** modelled (saturating log-domain extension **outside** measured support) |

**Measured support.** For every GPR module the committed table is measured at `pp`, `mf`, `ff` only; this triple is the module's `measured_support` (exposed by `instrumentos.gpr_dynamic_interpolation.MEASURED_SUPPORT`). The softest measured level is `pp`, the loudest `ff`. Every other `DYNAMIC_LEVELS` entry is a model output: **interior** levels (`p`, `mp`, `f`, ordinal coordinates in $[3,7]$) are GPR interpolations; the **tails** (`ppp`, `pppp` below `pp`; `fff`, `ffff` above `ff`) are *not* measured and are *not* continued as GPR trend.

**Production method (interior).** Gaussian-process regression with Matérn kernel fitted on $(x_{\mathrm{pp}}, d_{\mathrm{pp}})$, $(x_{\mathrm{mf}}, d_{\mathrm{mf}})$, $(x_{\mathrm{ff}}, d_{\mathrm{ff}})$ at fixed ordinal coordinates. `GPR_RANDOM_STATE = 0` makes the estimator deterministic by construction; output does not depend on global NumPy RNG state or event order. This is numerical repeatability — **not** measured acoustic data for intermediate dynamics and **not** perceptual validation.

For an interior modelled dynamic $d \in \{p, mp, f\}$ at pitch with anchors $(d_{\mathrm{pp}}, d_{\mathrm{mf}}, d_{\mathrm{ff}})$:

$$
\hat{d}_d = \mathrm{GPR}(x_d \mid \{(x_{\mathrm{pp}}, d_{\mathrm{pp}}), (x_{\mathrm{mf}}, d_{\mathrm{mf}}), (x_{\mathrm{ff}}, d_{\mathrm{ff}})\}),
$$

where $x_d$ is the ordinal coordinate for dynamic $d$. `mp` is **not** aliased to `mf` and is **not** a table column.

**Saturating register-adaptive tail extrapolation (5.1.0-strict-symbolic).** Before this change the GPR trend was extrapolated *unchanged* into the unmeasured tails. Two failure modes resulted: (i) the soft trend overshot **downward**, producing *negative* one-player densities (e.g. `clarinete` C4 at `pppp` $\approx -2.36$, which drove `harmonic_ratio` negative in the `DYNGRAD.wedge` case); and (ii) the loud trend *bent over*, producing a **non-monotone** dip (e.g. the `flauta` C4–E4–G4 triad had sonic mass $62.32$ at `ff` but $59.95$ at `ffff`). A first saturating fix used *fixed* per-step ratios; that removed the incidents but could not track register-dependent compression of the dynamic palette (e.g. `pppp≈ppp≈pp` at the top of the flute).

The production rule is now **register-adaptive by construction**. At the event's sounding pitch $m$, with measured/interpolated anchors $A_{\mathrm{pp}}(m)$, $A_{\mathrm{mf}}(m)$, $A_{\mathrm{ff}}(m)$:

$$
s_{\mathrm{soft}}(m)=\max\!\bigl(0,\tfrac{\ln(A_{\mathrm{mf}}/A_{\mathrm{pp}})}{N_{\mathrm{soft}}}\bigr),\qquad
s_{\mathrm{loud}}(m)=\max\!\bigl(0,\tfrac{\ln(A_{\mathrm{ff}}/A_{\mathrm{mf}})}{N_{\mathrm{loud}}}\bigr),
$$

where $N_{\mathrm{soft}}=3$ (steps `pp→p→mp→mf`) and $N_{\mathrm{loud}}=2$ (`mf→f→ff`) from `DYNAMIC_LEVELS`. Inverted anchors ($A_{\mathrm{pp}}>A_{\mathrm{mf}}$ or $A_{\mathrm{ff}}<A_{\mathrm{mf}}$) clamp the corresponding step to $0$ (flat tail — zero usable differentiation) and emit a metadata warning naming instrument, pitch, and the inverted pair. For $j$ steps below `pp` or above `ff`:

$$
\ln A_{\mathrm{soft}}(j)=\ln A_{\mathrm{pp}}-s_{\mathrm{soft}}\sum_{i=1}^{j}\gamma^{i},\qquad
\ln A_{\mathrm{loud}}(j)=\ln A_{\mathrm{ff}}+s_{\mathrm{loud}}\sum_{i=1}^{j}\gamma^{i},
$$

with geometric shrink $\gamma=$ `DYN_TAIL_SHRINK` $=0.5$ in `config.py`. The cumulative sum is bounded by $\gamma/(1-\gamma)=1$ when $\gamma=0.5$, so **the entire unmeasured tail never exceeds one measured-step's worth of change**. Because $s(m)$ is taken from the local anchors, the tail automatically compresses where measured differentiation collapses at range extremes — no instrument-independent register model is imposed. Technique modules with transferred (not measured) `pp`/`ff` anchors (`violin_sul_ponticello`, `violin_art_harm`) use the same math and additionally warn `"tail computed from transferred anchors"`. `config.DENSITY_FLOOR` remains only as an unreachable safety assert. Interior (in-support) GPR predictions are **unchanged** to within $10^{-9}$. Measured interior non-monotonicity (e.g. `flauta` C4 `mf`>`ff`) is left untouched by design.

**Diagnostic references (not production):** piecewise linear, PCHIP, and quadratic anchor interpolators appear only in audit tools (`tools/audit_gpr_model_quality.py`, `tools/compare_dynamic_interpolation_methods.py`). PR #24 compared methods on 357 source rows (8 GPR modules) and 340 string scenarios; production GPR was unchanged; linear and PCHIP were not adopted. Local method sensitivity is highest in low-register strings at source-row level; scenario-level `density.instrument` showed **0** high/extreme cases in the tested aggregate battery.

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

**Pitch-structure density** ($n_{\mathrm{distinct}} \geq 2$ required) — **extensive** (5.0.0-strict-symbolic):

$$
D_{\mathrm{pitch}} = S \cdot (1 + \ln(1 + H)) \cdot (1 - 0.15 \cdot \mathrm{harmonicRatio}),
\qquad
S = \sum_{i<j} e^{-\lambda \delta_{ij}}.
$$

Here $S$ is the **raw accumulating pairwise interval sum** over distinct pitch bins (the same sum whose mean-per-pair normalisation gives the reported compactness $D_{\mathrm{int}}^{\mathrm{norm}}$). Because $S$ accumulates over pairs, **adding a distinct note never decreases $D_{\mathrm{pitch}}$**. Registral span $A_{\mathrm{st}}$ is **not** applied here — the pairwise exponential decay $e^{-\lambda\delta}$ already attenuates distant pairs, so a second $1/(1+A_{\mathrm{st}}/12)$ damping would penalise ambitus twice. $A_{\mathrm{st}}$ remains a separately reported subindex (`registral`), not a factor in the aggregate.

If $n_{\mathrm{distinct}} < 2$, $D_{\mathrm{pitch}} = 0$.

**Composite vertical density:**

$$
D_{\mathrm{total}}^{\mathrm{raw}} = \frac{D_{\mathrm{pitch}} \cdot \sqrt{M_{\mathrm{sonic}}}}{D_{\max}}.
$$

Optionally apply $\log_{10}(1 + x)$ if `USE_LOG_COMPRESSION`. The mass channel $\sqrt{M_{\mathrm{sonic}}}$ additionally lets a register-isolated note (e.g. a far-below bass) raise the total. Because $S$ is on a larger scale than the previous mean-per-pair term, `MAX_DENS_GLOBAL` ($D_{\max}$) was recalibrated in 5.0.0-strict-symbolic (median-matched against `benchmarks/expected_outputs`; see `config.py`).

> **Removed:** mean-per-pair normalisation $D_{\mathrm{int}}^{\mathrm{norm}}$ as the aggregate's interval term (replaced by the raw sum $S$); redundant registral-span damping $1/(1+A_{\mathrm{st}}/12)$ in the composite product; earlier `D_{\mathrm{ref}} = D_{\mathrm{pond}}/A_{\mathrm{st}}` with zero-span exemption and cohesion factor $10/(1+A_{\mathrm{st}})$. The reported compactness axis $D_{\mathrm{int}}^{\mathrm{norm}}$ (`density.interval`) is unchanged and remains **intensive** (falls with spread).

**Monotonicity semantics (5.0.0-strict-symbolic).** The three quantities have distinct guarantees:

- **Raw interval sum $S$ — hard guarantee.** $S = \sum_{i<j} e^{-\lambda\delta_{ij}}$ is **non-decreasing** under the addition of a distinct pitch bin: a new bin only adds non-negative pairwise terms and never removes existing ones. This is an exact, composition-independent property.
- **Pitch-structure density $D_{\mathrm{pitch}}$ and composite $D_{\mathrm{total}}$ — quasi-monotone.** Both are monotone in $S$ and (for the composite) in sonic mass $M_{\mathrm{sonic}}$, but each is *modulated* by two composition-dependent factors: the entropy factor $\bigl(1 + \ln(1+H)\bigr)$ and the bounded harmonic damping $\bigl(1 - 0.15\cdot\mathrm{harmonicRatio}\bigr)$. Both factors are recomputed over the new bin set, so either can **fall** when the added note increases pitch fusion — most notably an **octave-related** addition, which raises the harmonic ratio (more energy in octave multiples of the lowest pitch) and can also flatten/redistribute the spectral-energy entropy. Consequently $D_{\mathrm{pitch}}$ (and, in the limiting case below, $D_{\mathrm{total}}$) can show a small decrease even though $S$ rose.
- **A small $D_{\mathrm{pitch}}$ decrease under octave doubling is intended behaviour** — it encodes the *fusion vs. crowding* trade-off: an octave-related pitch adds little textural friction (it fuses into the harmonic series) relative to a dissonant addition at the same $S$. The harmonic damping is capped at 15 %, so the effect is bounded.
- **Composite decrease is possible only in one narrow regime:** when the added note contributes **negligible mass** (e.g. a `pppp` doubling, so $\sqrt{M_{\mathrm{sonic}}}$ barely moves) while **sharply raising harmonic fusion** (so the damping factor drops enough to overcome the rise in $S$). When the addition carries meaningful mass — including a register-isolated bass — the $\sqrt{M_{\mathrm{sonic}}}$ channel dominates and the composite rises. Adversarial probes for this regime live in `benchmarks/characterization/battery_cases.py` (category `MONO`) and report OK/DECREASED with the $S$/harm/entropy/mass/$D_{\mathrm{pitch}}$/composite deltas; they never abort the run.

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

### P. MusicXML transposition (concert / sounding pitch)

**Module:** `xml_loader.py` — `_apply_transpose_to_written_pitch()`.

MusicXML may declare **written** pitch in `<pitch>` and an offset in `<attributes><transpose>`. Textural Density converts written pitch to **sounding/concert pitch** before range validation and density lookup:

$$
m_{\mathrm{sounding}} = m_{\mathrm{written}} + \mathrm{chromatic} + 12 \times \mathrm{octave\_change}.
$$

Example: B♭ clarinet part with written C4 and `<chromatic>-2</chromatic>` — analysis uses **B♭3** (sounding), not C4. `InstrumentEvent` may retain `written_pitch` when it differs from `sounding_pitch`.

**Manual / GUI / legacy `notes[]`:** input is already **sounding/concert pitch**; registry `transposition` is notation metadata only and is not applied to legacy lists.

**Not used:** diatonic spelling-only transposition without chromatic offset; applying transpose twice.

See [TECHNICAL_MANUAL.md](TECHNICAL_MANUAL.md) §7.4 and `tests/test_transposing_instrument_sounding_pitch_contract.py`.

---

### Q. Verification properties (synthetic)

**Module:** `validation/verification.py` — `run_verification_suite()`.

These are **implementation correctness checks**, not empirical validation:

| Property | Expected behaviour |
|----------|-------------------|
| Finite outputs | All `density.*` scalars finite for synthetic cases |
| Chromatic vs wide | Interval density (compactness, intensive) higher for chromatic cluster than wide-spaced chord |
| Extensive composite (5.0.0) | Adding a distinct note does not decrease composite vertical density (`density.total`) or `pitch_structure`; register-isolated bass never lowers the total (`tests/test_extensive_density_monotonic.py`) |
| Player mass | Orchestral mass increases linearly with Qty; pressure-equivalent instrument density scales as RSS; interval/pitch-structure unchanged |
| Qty vs pitch structure | Qty does not increase pitch polyphony, interval pairs, or spectral entropy for unison doublings |
| Dynamic monotonicity | One-player density is positive; soft/loud tails are monotone into measured support; full `pppp→ffff` monotone except measured/interior humps left untouched (§F.1); `tests/test_adaptive_dynamic_tails.py` |
| Tail saturation | Register-adaptive log-domain tails with local $s(m)$ from measured pp/mf/ff and geometric shrink $\gamma=0.5$; whole tail ≤ one measured step; per-event warning records $s(m)$, $\gamma$, value (§F.1) |
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

*Last updated: 2026-07-12 (5.1.0-strict-symbolic: register-adaptive saturating dynamic tails §F.1; MusicXML sounding pitch §P; package 1.1.4).*
