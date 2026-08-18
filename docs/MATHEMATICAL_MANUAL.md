# Mathematical Manual & Tutorial — Textural Density

This document is the **canonical reference** for **equations, algorithms, and models** implemented in **Textural Density**, plus a **pedagogical tutorial** for reading results and tuning parameters.

> **PDF:** `docs/MATHEMATICAL_MANUAL.pdf` is an archival snapshot from the 2026-05-23 initial import (`a439f2c`) and predates later alignment commits. This `.md` file is the source of truth.

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
   - [F.1 Dynamic tables (committed ladders)](#f1-dynamic-tables-committed-ladders)
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

> **Legacy-path-only minimum step (0.25 st).** The legacy `densidade_intervalar.calculate_interval_density` still contains a guard that, for two *different* note strings whose $\Delta_{\mathrm{st}} < 0.01$ semitones, forces $\Delta_{\mathrm{st}} \leftarrow \max(\Delta_{\mathrm{st}}, 0.25)$ before computing $\delta$. This floor is **not reachable from `core.calculate_metrics`** — the pipeline uses the distinct-bin path above. The legacy function is invoked only by $\lambda$-calibration internals (`densidade_intervalar.calibrate_lambda`), offline tooling (`tools/refresh_regression_fixtures.py`), `validation/verification.py`, and unit tests. The paragraph is retained (not deleted) because that function and its floor still exist and are exercised by those non-core call sites; deleting the note would leave their behaviour undocumented.

**$\lambda$-calibration and the legacy floor (inert divergence).** $\lambda$ is fitted by `calibrate_lambda` via the **legacy (floored)** `calculate_interval_density`. The 12-EDO calibration dyads in `CONSONANCE_RATINGS` are all integer semitone intervals with $\Delta_{\mathrm{st}} \geq 1$ (keys $0,2,3,4,5,6$; the unison key contributes no pairwise floor path). The $0.25$-st floor therefore **never triggers** on the calibration set, so the fitted $\lambda$ is numerically identical to what a floor-free path would produce. The two-path divergence (core distinct-bin vs legacy floored) is documented as **inert** for the published $\lambda$; it would matter only if calibration were extended to sub-cent experimental dyads.

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

### F.1 Dynamic tables (committed ladders)

**Production (2026-08-03):** instrument density looks up committed spectral_data cells for the requested dynamic. There is **no** runtime GPR or adaptive-tail fill-in.

| Case | Behaviour |
|------|-----------|
| Dynamic present in row | Exact cell value |
| Dynamic absent | MissingCommittedDynamicError |
| Pitched table-backed modules (winds, brass incl. horn/trombone/tuba, strings, techniques) | Full 10-level **data-faithful** Dynamics_predicter v1.5 ladders (2026-08-08/09/18): measured pp/mf/ff anchors verbatim, PCHIP interiors, tapered outers — not forced monotone. Violin harmonics still carry D6 monotone ladders |
| Unpitched percussion (`bass_drum`, `cymbals`, `tamtam`, `gong`) | Pitch-independent `DYNAMIC_CDM` (former `internal_default` log-linear ladder) |

Pitch interpolation (MIDI-space linear/PCHIP between chromatic anchors) is unchanged and independent of the dynamic column.

**Historical note:** older releases used Matérn GPR on pp/mf/ff anchors plus register-adaptive saturating tails (5.1.0-strict-symbolic). That implementation is preserved only at `tools/legacy_gpr_dynamic_interpolation.py` for audits; it is not on the production path. See [CHANGES.md](../CHANGES.md) and [TECHNICAL_MANUAL §2.4.1](TECHNICAL_MANUAL.md).


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

Here $S$ is the **raw accumulating pairwise interval sum** over distinct pitch bins (the same sum whose mean-per-pair normalisation gives the reported compactness $D_{\mathrm{int}}^{\mathrm{norm}}$). Because $S$ accumulates over pairs, **adding a distinct note never decreases $S$**. $D_{\mathrm{pitch}}$ is only **quasi-monotone** in $S$ (entropy and harmonic-ratio factors can fall). Registral span $A_{\mathrm{st}}$ is **not** applied here — the pairwise exponential decay $e^{-\lambda\delta}$ already attenuates distant pairs, so a second $1/(1+A_{\mathrm{st}}/12)$ damping would penalise ambitus twice. $A_{\mathrm{st}}$ remains a separately reported subindex (`registral`), not a factor in $D_{\mathrm{pitch}}$ or $D_{\mathrm{total}}$.

If $n_{\mathrm{distinct}} < 2$, $D_{\mathrm{pitch}} = 0$.

**Composite vertical density (Task 8c — unified):**

$$
D_{\mathrm{blend}} = 10\cdot\bigl(w\,\widehat{D}_{\mathrm{inst}}+(1-w)\,\widehat{D}_{\mathrm{int}}\bigr)
= w\cdot\frac{D_{\mathrm{inst}}}{10} + (1-w)\cdot D_{\mathrm{int}}
= \texttt{density.weighted},
\quad
D_{\mathrm{total}}^{\mathrm{raw}} = \frac{D_{\mathrm{blend}} \cdot \sqrt{M_{\mathrm{sonic}}}}{\mathrm{REF}},
\quad
D_{\mathrm{total}} = \log_{10}(1+D_{\mathrm{total}}^{\mathrm{raw}}).
$$

| Symbol | Default | Role |
|--------|---------|------|
| $\mathrm{REF}$ = `MAX_DENS_GLOBAL` | **193** | Task 8c re-freeze: chosen so frozen all-pitched baselines keep pre-unification order of magnitude (match ≈192.6→193); see `CHANGES.md` / `config.py` |
| $w$ = `weight_factor` | **0.5** (`DEFAULT_WEIGHT_FACTOR`) | Instrument vs interval blend inside $D_{\mathrm{blend}}$ |
| $\mathrm{DI\_max}$, $\mathrm{DV\_max}$ | 100, 10 | Normalisation divisors in `core.composite` (**no clamping applied**). Under `INTERVAL_BLEND_NORMALISATION = "legacy"` (default) $\mathrm{DV\_max}=10$ even though compressed $D_{\mathrm{int}}$ cannot exceed $\log_{10}(2)\approx 0.301$. `"unit_range"` is opt-in and divides DV by that attainable maximum so $w$ approaches **approximate parity** of the two axes (see below). |

**Known asymmetry (do not “fix” by changing `USE_LOG_COMPRESSION`).** `USE_LOG_COMPRESSION` is applied twice to the interval/composite path and never to instrument density:

1. $D_{\mathrm{int}}$ is already $\log_{10}(1+\bar{D})$ inside `normalize_interval_density` before it enters the blend as DV.
2. $D_{\mathrm{total}}$ applies $\log_{10}(1+D_{\mathrm{blend}}\sqrt{M}/\mathrm{REF})$ again in `compute_composite_vertical_density`.
3. $D_{\mathrm{inst}}$ (DI) is compressed in neither place.

The default blend therefore compares a raw-scale DI (typical tens) to a log-compressed DV ($\le 0.301$) after dividing them by 100 and 10 respectively. Per-slice realised terms `w·DI/DI_max·scale` and `(1−w)·DV/DV_max·scale` and their ratio are emitted on `composite_meta.blend_term_contributions` so the imbalance is visible. When the interval term is exactly zero (monophonic / unpitched-only slices, or $w=1$), the ratio field is JSON `null`, never `inf`/`nan`. Changing the double-log or compressing DI would move frozen totals; it is documented here and pinned by `tests/test_log_compression_asymmetry.py`.

**`unit_range` is approximate parity, not strict commensurability.** Under that opt-in, DV is divided by its true attainable maximum and therefore lies in $[0,1]$. DI is still divided by $\mathrm{DI\_max}=100$, an empirical reference rather than a bound (DI is unclamped). $w=0.5$ then gives equal *weight* to a bounded quantity and an unbounded one. Results under `"legacy"` and `"unit_range"` are not comparable; the mode used for any analysis must be stated. The identity $\mathrm{orch}/\mathrm{pitch}=(\mathrm{DI}/10)/\mathrm{DV}$ holds only at $w=0.5$, where $w$ cancels; it must not be generalised to other weightings.

$D_{\mathrm{pitch}}$ remains a reported axis; it is **not** the composite product. Zero interval contribution (unpitched-only) is a numeric zero — no event-kind branch.

**Acceptance criterion:** property tests in `tests/test_unified_composite_contract.py` (monotonicity under event/Qty addition, mixed > subsets, continuity when dropping the last pitched event) plus the GUI-chain freeze `tests/test_composite_unification_acceptance.py`. Header text is generated from the same expression as the computation (`core.composite.format_composite_header_line`).

> **Removed:** mean-per-pair normalisation $D_{\mathrm{int}}^{\mathrm{norm}}$ as the aggregate's interval term (replaced by the raw sum $S$); redundant registral-span damping $1/(1+A_{\mathrm{st}}/12)$ in the composite product; earlier `D_{\mathrm{ref}} = D_{\mathrm{pond}}/A_{\mathrm{st}}` with zero-span exemption and cohesion factor $10/(1+A_{\mathrm{st}})$. The reported compactness axis $D_{\mathrm{int}}^{\mathrm{norm}}$ (`density.interval`) is unchanged and remains **intensive** (falls with spread).

**Monotonicity semantics.**

- **Raw interval sum $S$ — hard guarantee.** $S$ is **non-decreasing** under addition of a distinct pitch bin.
- **Pitch-structure density $D_{\mathrm{pitch}}$ — quasi-monotone (reported axis only).** Modulated by $\bigl(1+\ln(1+H)\bigr)$ and $\bigl(1-0.15\cdot\mathrm{harmonicRatio}\bigr)$. An octave-related addition can lower $D_{\mathrm{pitch}}$ even if $S$ rose. This does **not** enter $D_{\mathrm{total}}$.
- **Composite $D_{\mathrm{total}}$ (Task 8c).** $D_{\mathrm{total}}=\log_{10}(1+D_{\mathrm{blend}}\sqrt{M}/\mathrm{REF})$. It moves with $D_{\mathrm{blend}}$ (instrument RSS + interval compactness) and $\sqrt{M}$, **not** with the entropy/harmonic factors inside $D_{\mathrm{pitch}}$. Property tests: `tests/test_unified_composite_contract.py`.

**Absolute density** (reference scalar; **not** an input to $D_{\mathrm{total}}$):

If $n_{\mathrm{distinct}} < 2$, the implementation returns $D_{\mathrm{abs}} = 0$ (`core/pipeline.py`). This is an **implementation guard**.

Otherwise:

$$
D_{\mathrm{abs}} = D_{\mathrm{blend}} \cdot \ln(1 + N_{\mathrm{pitched}}),
$$

where $N_{\mathrm{pitched}}$ is the **pitched** event-row count (`pitched_event_count`). Unpitched events are excluded from this count. Natural logarithm (`np.log1p`).

---

### I. Spectral moments, chroma, harmonic ratio

**Module:** `spectral_analysis.py`.

**Moments** are computed in **MIDI** space with weights $a_i$ (weighted **population** moments: divide by $S=\sum a_i$):

$$
\mu = \frac{1}{S}\sum_i a_i m_i, \quad
\sigma^2 = \frac{1}{S}\sum_i a_i (m_i-\mu)^2, \quad
\gamma_1 = \frac{\frac{1}{S}\sum_i a_i (m_i-\mu)^3}{\sigma^3}\ (\sigma>0).
$$

**Returned representation.** `centroid.frequency` is $f(\mu)$ in Hz. `spread.deviation` is **not** $\sigma$ in MIDI. It is

$$
\texttt{spread["deviation"]} = f(\mu+\sigma) - f(\mu),
$$

with $f(m)=440\cdot 2^{(m-69)/12}$.

**Excess kurtosis:**

$$
\gamma_2 = \frac{\frac{1}{S}\sum_i a_i (m_i-\mu)^4}{\sigma^4} - 3.
$$

**Flatness:** ratio of geometric to arithmetic mean of amplitudes (on $a_i > 10^{-10}$).

**Roll-off (85%):** cumulative sum of $a_i$ in array order; MIDI at 85% cumulative energy mapped to Hz.

**Entropy:** $H = -\sum_i p_i \log_2 p_i$, $p_i = a_i/S$, with small $p_i$ filtered.

**Chroma:** $c_i = \mathrm{round}(m_i) \bmod 12$, energies summed per class and normalised.

**Harmonic ratio:** fundamental $m_{\min}$. Bin $i$ is harmonic when $\min(r,\,12-r)\le 0.25$ with $r=(m_i-m_{\min})\bmod 12$ (symmetric octave-class distance in `spectral_analysis.calculate_harmonic_ratio`; locked by `tests/fixtures/microtonal_harmonic_ratio.json`).

---

### J. Texture, timbre blend, orchestration

**Module:** `timbre_texture_analysis.py`.

**Texture** (`calculate_texture_density`):

- `player_count` / `player_weighted_texture_mass` $= \sum n_j$ over the **full slice** (pitched + unpitched Qty)
- `average_texture_density` = Qty-weighted mean one-player CDM over the **full slice** (includes unpitched). This is a **per-player mean**, not a total: it may fall when low-CDM instruments are added and rise under Qty expansion toward high-CDM instruments. Monotone under growth are the **totals** (Sonic Mass, RSS, Composite) — see Technical Manual §3.12.1.
- `pitch_polyphony` / `texture_polyphony` $= n_{\mathrm{distinct}}$ (**pitched** bins only)
- `texture_variability` $= \mathrm{std}(m_i)$ over pitched bins
- `texture_contrast` $= \max m_i - \min m_i$ over pitched bins

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

Reference ratings `CONSONANCE_RATINGS` map interval classes to empirical scores. Dyad intervals are built with `utils/notes.dyad_notes_from_semitone_interval()` (Phase 4 fix). For candidate $\lambda$, minimise squared error between predicted normalised density and ratings (see [Technical Manual](TECHNICAL_MANUAL.md), Section 3.15). Optimal $\lambda$ is saved to `config/density_params.json`. Calibration calls the **legacy** floored `calculate_interval_density`; as noted in §B, the $0.25$-st floor never fires on these 12-EDO dyads ($\Delta_{\mathrm{st}}\geq 1$), so the fitted $\lambda$ is unaffected by the legacy/core path split.

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

**Rule:** Instrument CDM tables are **`external_acoustic_metadata`** (committed `pppp`…`ffff` ladders looked up at analysis time). Runtime analysis does **not** run GPR or adaptive tails; missing cells raise `MissingCommittedDynamicError`. Offline/historical GPR lives in `tools/legacy_gpr_dynamic_interpolation.py`. Registry-only coarse profiles are **`metadata_proxy`**. Removed branches (Stevens' Law, psychoacoustic corrections, perceptual interval weighting, combination tones) are no longer available.

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

**Register band occupancy** (`register_band_occupancy`; default bands in `config.DEFAULT_REGISTER_BANDS`): half-open $[L_b, U_b)$. Each input MIDI is assigned to at most one band. Let $c_b$ be the in-band count. Then

$$
O_b = \frac{c_b}{\sum_{b'} c_{b'}},
$$

with denominator $1$ if every count is zero. **Out-of-band midis are excluded** from both numerator and denominator. Production subindices pass **distinct pitched-bin** midis, not raw event rows.

**Register entropy** (normalised):

$$
H_{\mathrm{reg}} = \frac{-\sum_b O_b \log_2 O_b}{\log_2 B}, \quad B = \text{number of bands}.
$$

**Registral compression** (production subindex; **not** compactness):

$$
C_{\mathrm{reg}} = \begin{cases}
\dfrac{1}{1 + A_{\mathrm{st}}} & n_{\mathrm{distinct}} \ge 2 \\
0 & n_{\mathrm{distinct}} < 2.
\end{cases}
$$

**Registral compactness** $1/(1+A_{\mathrm{st}}/12)$ is an unused helper (`compute_registral_compactness`). Neither enters $D_{\mathrm{total}}$.

**Duration-weighted event count** (when all events have resolvable duration $d_i$):

$$
N_{\mathrm{dur}} = \sum_i n_{\mathrm{instr},i} \cdot d_i.
$$

**Composite vertical density** (current assembly — same as §H Task 8c):

$$
D_{\mathrm{total}}^{\mathrm{raw}} = \frac{D_{\mathrm{blend}} \cdot \sqrt{M_{\mathrm{sonic}}}}{\mathrm{REF}}, \quad \mathrm{REF}=193.
$$

$D_{\mathrm{pitch}}$ is a reported axis only. `COMPOSITE_HARMONIC_DAMPING = 0.15` applies **inside** $D_{\mathrm{pitch}}$, not in $D_{\mathrm{total}}$. Final total applies $\log_{10}(1+x)$ when `USE_LOG_COMPRESSION`.

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

**Module:** `xml_loader.py` — `_transpose_semitones_from_attributes()` (chromatic $+ 12\times$ octave_change), `_apply_semitone_transpose()` (applies the offset), called from `_extract_musicxml_notes()`.

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
| Raw interval sum $S$ | **Non-decreasing** under addition of a distinct pitch bin (hard guarantee; §H) |
| Composite `density.total` (Task 8c) | Monotonicity is the tested property of the current blend×mass composite (`tests/test_unified_composite_contract.py`); register-isolated bass with meaningful mass must not lower the total |
| Pitch-structure `density.pitch_structure` | **Quasi-monotone** only (§H): $S$ never falls, but entropy and harmonic-ratio factors can lower $D_{\mathrm{pitch}}$. No general non-decrease guarantee. `tests/test_extensive_density_monotonic.py` is a 5.0.0 regression vestige, not a general description of the current formula |
| Player mass | Orchestral mass increases linearly with Qty; pressure-equivalent instrument density scales as RSS; interval/pitch-structure unchanged |
| Qty vs pitch structure | Qty does not increase pitch polyphony, interval pairs, or spectral entropy for unison doublings |
| Dynamic ladder hygiene | One-player density is positive; committed pitched ladders carry all 10 levels with interiors inside their measured segments and tapered, non-zigzag outers (§F.1; data-faithful — measured anchors may be locally non-monotone); `tests/test_pitched_dynamic_monotone_ladders.py` |
| Tail saturation (historical) | Pre-2026-08-03 runtime adaptive tails retired; offline rebuild uses legacy `internal_default` path only when regenerating committed ladders (§F.1) |
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
  W --> TOT
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
2. Check **`density.weighted`** ($D_{\mathrm{blend}}$, the composite numerator) and **`density.refined`** / **`density.pitch_structure`** (reported axis only; **does not** divide by pitch span and **does not** enter $D_{\mathrm{total}}$).
3. Open **`density_subindices`**: inspect `interval_compactness`, `registral`, `orchestral_mass`, and `composite.components` for a decomposed reading.
4. Read **`metric_metadata`**: check `source_type`, `validation_status`, and `warnings` before citing a value in research writing.
5. **Spectral entropy** and **harmonic ratio** modulate $D_{\mathrm{pitch}}$ only. They do **not** appear in the Task 8c composite $D_{\mathrm{blend}}\sqrt{M}/\mathrm{REF}$.

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
| **Metadata proxy** | Symbolic estimate standing in for a quantity that would otherwise require external measurement — not a measured acoustic value |
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

*Last updated: 2026-08-18 (symmetric octave-class harmonic ratio; §H blend-normalisation note; `.md` canonical over archival PDF).*
