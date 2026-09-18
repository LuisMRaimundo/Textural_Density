# Textural Density — mathematical reference (implementation audit)

This document records **mathematics as implemented** in the working tree of Textural Density. It is a traceability audit, not a proof of scientific validity, acoustic correctness, or musicological adequacy.

---

## 1. Source provenance

| Field | Value |
|-------|--------|
| Audit date | 2026-09-18 (Europe/Lisbon); interval-cardinality patch |
| Active repository | `E:\PYTHON CODES\CÓDIGOS FINAIS - GIT HUB\Textural_Density-git` |
| Branch | `feat/interval-effective-cardinality` (uncommitted patch; not pushed) |
| Baseline HEAD (pre-patch) | `0c5cab945a9c3f83b55ac9b723bf62939fad0b1b` (`main` / GitHub default) |
| Package version (declared) | `1.2.0` (`pyproject.toml`) |
| Methodology / schema label (declared) | `5.2.0-strict-symbolic` (`core/defaults.py`) |
| Working-tree source vs baseline | **Patched working tree.** `density.interval` is $n_{\mathrm{eff}}-1$. This document is **not** a self-referential final commit hash. |
| Uncommitted / untracked (non-source) | Pre-existing `build/`; `reports/density_probe/`; extra `reports/gpr_model_quality_plots/review_*.png`. Research analyses were **not** regenerated. |
| Generated document excluded from fingerprint | this file (`docs/Textural_Density_math_formula.md`) |

Baseline `872d1d4` is the identity of the **pre-patch tracked source**. §9 lists those hashes and a working-tree refresh for files changed by this patch.

### Declared vs installed dependencies

Declared ranges (`pyproject.toml` / `requirements.txt`):

- `numpy>=1.20.0,<3.0.0`
- `pandas>=1.3.0,<3.0.0`
- `matplotlib>=3.4.0,<4.0.0`
- `scipy>=1.7.0,<2.0.0`
- `scikit-learn>=1.0.0`
- `seaborn>=0.11.0`
- `openpyxl>=3.1.0`
- `mido>=1.2.0`
- `statsmodels>=0.13.0`

Versions importable in the audit environment (not installed by this audit; not a lockfile):

- numpy 2.2.6, pandas 2.3.3, matplotlib 3.8.4, scipy 1.13.1, scikit-learn 1.7.2, seaborn 0.13.2, openpyxl 3.1.5, mido 1.3.3, statsmodels 0.14.5

Library-default remarks below refer to these installed versions when a default was checked.

---

## 2. Scope, exclusions, and reading guide

**Included:** every distinct first-party calculation with scientific or metric meaning found on the production pipeline, optional configuration branches, legacy/unused helpers, research/validation utilities, and test-oriented generators that implement formulas.

**Excluded (ordinary software arithmetic):** loop indices, GUI layout/fonts/padding, progress percentages, file-path joining, logging timestamps, hash-of-bytes for export identity (`core/hash_utils.py`), and report pagination — unless they change a scientific result.

**Identifiers:**

- `M-xxx` — project-defined mathematics (including NumPy primitives used to express a project formula).
- `L-xxx` — mathematics delegated to an external package; the package’s internal derivation is **not** reproduced.

**Status labels:** *production* (on `calculate_metrics` / `analyze_score`), *optional* (reachable only with a non-default flag), *legacy/unused* (present but not called by the production pipeline), *research/test-only* (tools, validation, calibration, tests).

**Units:** when the code does not name a physical unit, this document writes **unclear / dimensionless software unit**. Instrument “CDM” table cells are **not** claimed to be SPL, RMS, or sones.

**Tests:** “Verification evidence” names existing test files. **No test in this audit was executed.**

---

## 3. Implemented analysis flow (production)

Public entry: [`core/pipeline.py`](../core/pipeline.py) `calculate_metrics` (alias `calcular_metricas`). GUI and `data_processor.py` re-export this path.

1. Defaults: `weight_factor = 0.5` if omitted ([`core/defaults.py`](../core/defaults.py)).
2. Convert input → `VerticalSlice` ([`core/converters.py`](../core/converters.py)).
3. Per-event one-player density = committed table lookup ([`core/orchestration.py`](../core/orchestration.py) → instrument `calcular_densidade`).
4. Merge identical (MIDI, instrument, dynamic) sources; **RSS** instrument density and **linear** sonic mass ([`core/source_aggregation.py`](../core/source_aggregation.py)).
5. Drop unpitched events from pitch structure only ([`core/unpitched_routing.py`](../core/unpitched_routing.py)).
6. Aggregate remaining events into MIDI bins ([`core/pitch_aggregation.py`](../core/pitch_aggregation.py)).
7. Pairwise interval compactness on **distinct bins** ([`core/pitch_structure.py`](../core/pitch_structure.py) + [`densidade_intervalar.py`](../densidade_intervalar.py)).
8. Spectral moments, chroma, harmonic-ratio **proxy** on bin MIDI + mean bin weights ([`spectral_analysis.py`](../spectral_analysis.py)).
9. Texture / timbre / orchestration descriptors ([`timbre_texture_analysis.py`](../timbre_texture_analysis.py)).
10. Blend $D_{\mathrm{blend}}$ then composite $\log_{10}(1 + D_{\mathrm{blend}}\sqrt{M}/\mathrm{REF})$ ([`core/composite.py`](../core/composite.py), [`core/pitch_structure.py`](../core/pitch_structure.py)).
11. Attach metadata and subindices ([`core/metrics_metadata.py`](../core/metrics_metadata.py), [`core/subindices.py`](../core/subindices.py)).

Temporal scores ([`core/score_analysis.py`](../core/score_analysis.py)) group events into slices, then call `calculate_metrics` per slice.

**What this software does not compute at runtime:** audio FFT/STFT, live SPL, Stevens’ law, combination tones, or GPR / adaptive-tail fill-in. `config.DYN_TAIL_SHRINK` documents a **removed** runtime model; production tables are already committed 10-dynamic ladders.

---

## 4. Project formulas

### M-001 — Strict note → MIDI (production)

**A. Status.** Production pitch axis for aggregation, lookup, and range checks.

**B. Source.** [`microtonal.py`](../microtonal.py) `note_to_midi_strict_from_parsed`, lines 584–590; `note_to_midi_strict`, lines 593–595.

**C. Excerpt.**

```python
def note_to_midi_strict_from_parsed(parsed: ParsedPitch) -> float:
    semitone, octave_adjustment = _pitch_class_semitone(parsed.letter, parsed.accidental)
    octave = parsed.octave + octave_adjustment
    midi = (octave + 1) * 12 + semitone + parsed.quarter_offset
    if parsed.cents:
        midi += parsed.cents / 100.0
    return float(midi)
```

**D. LaTeX.**

$$
m = 12(o + a + 1) + s + q + \frac{c}{100}
$$

where $o$ is the written octave, $a$ is the wrap-around octave adjustment (for example B♯ / C♭), $s$ is the chromatic pitch-class index, $q \in \{-0.5,0,0.5\}$ is a quarter-tone offset, and $c$ is cents.

**E. Symbols.** $m$: MIDI float (`midi`). $o$: `parsed.octave`. $s$: `semitone`. $q$: `parsed.quarter_offset`. $c$: `parsed.cents`. Units: MIDI (dimensionless pitch number); cents are 1/100 semitone.

**F. Layman.** Turns a written note such as `C4` or `G#5+25c` into one number on the piano-key scale so intervals and tables share an axis.

**G. Specialist.** Scientific pitch notation with $C4 = 60$. Enharmonic wrap-around is applied before the MIDI formula. Failure raises `InvalidPitchNotation` (no silent $C4$ fallback). This is notation conversion, not an acoustic measurement.

**H. Conditions.** Used by pitch aggregation, table interpolation, range validation, and unpitched placeholder construction. Invalid strings abort the lookup/aggregation path that called the strict parser.

**I. Verification evidence.** `tests/test_microtonal_strict.py`, `tests/test_notes.py`, `tests/test_wraparound_enharmonics.py`. Not executed in this audit.

---

### M-002 — Legacy note → MIDI with $C4$ fallback (optional / non-MusicXML)

**A. Status.** Legacy helper. Production aggregation uses M-001. MusicXML transpose **no longer** calls this function (see M-005).

**B. Source.** [`microtonal.py`](../microtonal.py) `note_to_midi`, lines 598–680.

**C. Excerpt (failure branch).**

```python
    # Falhou? Avisa e devolve C4
    logger.warning(f"Formato de nota não reconhecido: {note}")
    return 60.0
```

Empty/non-string input returns `60.0` at lines 603–604.

**D. LaTeX.** Same MIDI formula as M-001 when the regex path matches; otherwise

$$
m = 60 \quad \text{(unrecognised or empty input)}.
$$

**E. Symbols.** Same as M-001. Fallback is MIDI 60 ($C4$).

**F. Layman.** Older converter: if it cannot read the note, it pretends the note is middle C.

**G. Specialist.** Silent substitution can still shift calculations on callers that use `note_to_midi` (legacy interval path, some offline tools). MusicXML concert pitch uses M-001 / M-005.

**H. Conditions.** Used when `strict=False` (default). Not used by `note_to_midi_strict`.

**I. Verification evidence.** `tests/test_notes.py`, `tests/test_xml_loader.py`. Not executed.

---

### M-003 — MIDI → frequency

**A. Status.** Production (spectral moment labels in Hz).

**B. Source.** [`microtonal.py`](../microtonal.py) `midi_to_hz`, lines 733–743. Constants: `A4_FREQ = 440.0`, `A4_MIDI = 69` (lines 74–75).

**C. Excerpt.**

```python
    return A4_FREQ * (2 ** ((midi_pitch - A4_MIDI) / 12))
```

**D. LaTeX.**

$$
f = 440 \cdot 2^{(m-69)/12}
$$

**E. Symbols.** $f$: hertz (`midi_to_hz`). $m$: MIDI (`midi_pitch`). Equal-tempered A4 = 440 Hz.

**F. Layman.** Converts the MIDI number into a frequency assuming twelve-tone equal temperament and A4 = 440 Hz.

**G. Specialist.** Standard 12-TET mapping. Not a measured frequency. Used after MIDI-domain moments to report centroid/spread/roll-off in Hz.

**H. Conditions.** Called from `calculate_spectral_moments` and roll-off. No guard for non-finite $m$ here.

**I. Verification evidence.** `tests/test_spectral_analysis.py`. Not executed.

---

### M-004 — Frequency → MIDI

**A. Status.** Production helper for note labels from Hz.

**B. Source.** [`microtonal.py`](../microtonal.py) `hz_to_midi`, lines 746–758.

**C. Excerpt.**

```python
    if frequency <= 0:
        return 0
    return A4_MIDI + 12 * math.log2(frequency / A4_FREQ)
```

**D. LaTeX.**

$$
m =
\begin{cases}
0 & f \le 0 \\
69 + 12\log_2(f/440) & f > 0
\end{cases}
$$

**E. Symbols.** $f$: Hz. $m$: MIDI. $\log_2$ is binary log (`math.log2`).

**F. Layman.** Inverse of M-003. Non-positive frequencies become 0.

**G. Specialist.** Returning MIDI 0 for $f\le 0$ is a software policy, not a physical pitch.

**H. Conditions.** Used by `frequency_to_note_name`.

**I. Verification evidence.** `tests/test_spectral_analysis.py`. Not executed.

---

### M-005 — MusicXML written → sounding pitch

**A. Status.** Production for MusicXML loads that apply `<transpose>`. **Corrected 2026-09-17:** written MIDI from step/octave/alter; transpose applied once in MIDI space; no C4 fallback.

**B. Source.** [`xml_loader.py`](../xml_loader.py) `musicxml_written_midi`, `parse_musicxml_written_pitch`, `_transpose_semitones_from_attributes`, `apply_written_midi_transpose`.

**C. Excerpt.**

```python
    return float((int(octave) + 1) * 12 + _MUSICXML_STEP_SEMITONE[letter] + float(alter))
```

```python
    return float(chromatic + 12 * octave_change)
```

**D. LaTeX.**

$$
m_{\mathrm{written}} = 12(o+1)+s+a,\qquad
\Delta = c_{\mathrm{chrom}} + 12\,o_{\Delta},\qquad
m_{\mathrm{sound}} = m_{\mathrm{written}} + \Delta
$$

**E. Symbols.** $s$: MusicXML step pitch-class (C=0). $a$: `<alter>` in semitones (not rounded). $c_{\mathrm{chrom}}$: `<chromatic>`. $o_{\Delta}$: integer `<octave-change>`.

**F. Layman.** Transposing-instrument parts are shifted to concert pitch before density lookup.

**G. Specialist.** $\mathrm{Cb}5 \to 71$, $\mathrm{B}\sharp 3 \to 60$. Double accidentals are $a=\pm 2$. Invalid step/octave/alter/chromatic raise `InputError`. This is a **behaviour change** for wrap-around and unsupported spellings, not a terminology-only edit.

**H. Conditions.** Applied when a part declares `<transpose>` and the loader’s apply path is taken. Zero transpose keeps a strict-parseable written spelling.

**I. Verification evidence.** `tests/test_musicxml_pitch_transpose.py`, `tests/test_xml_loader.py`, `tests/test_transposing_instrument_sounding_pitch_contract.py`.

---

### M-006 — Unpitched placeholder lookup key

**A. Status.** Production entry convention for unpitched instruments.

**B. Source.** [`core/unpitched_routing.py`](../core/unpitched_routing.py) `canonical_unpitched_note`, lines 45–61.

**C. Excerpt.**

```python
    lo, hi = profile.sounding_range
    mid = int((int(lo) + int(hi)) // 2)
    return midi_to_note_name(float(mid))
```

**D. LaTeX.**

$$
m_{\mathrm{ph}} = \left\lfloor \frac{\lfloor m_{\mathrm{lo}}\rfloor + \lfloor m_{\mathrm{hi}}\rfloor}{2} \right\rfloor
$$

integer midpoint of the registry sounding-range MIDI pair; then converted to a note name.

**E. Symbols.** $m_{\mathrm{lo}},m_{\mathrm{hi}}$: `profile.sounding_range`. The code comment states this is **lookup convention only — no acoustic meaning**.

**F. Layman.** Unpitched rows still need a table key; the software invents a note in the middle of a declared range.

**G. Specialist.** Floor-average of integer bounds. Not a sounding pitch. Microtonal spellings on unpitched instruments are rejected (`reject_unpitched_microtones`).

**H. Conditions.** GUI/XML/MIDI entry for unpitched profiles. Pitch-structure still excludes these events (M-007).

**I. Verification evidence.** `tests/test_unpitched_entry_paths.py`, `tests/test_unpitched_pitch_exclusion.py`. Not executed.

---

### M-007 — Unpitched exclusion from pitch bins

**A. Status.** Production eligibility rule.

**B. Source.** [`core/unpitched_routing.py`](../core/unpitched_routing.py) `partition_pitched_events`, lines 141–161.

**C. Excerpt.**

```python
        if instrument_is_unpitched(inst):
            warnings.append(
                f"Unpitched instrument '{inst}' note key '{note}' excluded from "
                "pitch-structure bins (interval compactness, registral span, "
                "distinct pitch count); retained for orchestration mass and "
                "instrument CDM lookup only."
            )
            continue
```

**D. LaTeX.** Let $E$ be events with non-empty note strings. Pitched set

$$
E_{\mathrm{p}} = \{ e\in E : \neg \mathrm{unpitched}(\mathrm{instrument}(e)) \}.
$$

Unpitched events remain in $E$ for CDM lookup and mass.

**E. Symbols.** Predicate `instrument_is_unpitched` from the registry `unpitched` flag.

**F. Layman.** Drums and cymbals count toward loudness-like mass, not toward “how many different pitches.”

**G. Specialist.** Software policy, not an acoustic definition of unpitchedness.

**H. Conditions.** Always in `calculate_metrics` after one-player densities are computed.

**I. Verification evidence.** `tests/test_unpitched_pitch_exclusion.py`, `tests/test_unpitched_aggregation_contract.py`. Not executed.

---

### M-008 — Pitch-bin aggregation

**A. Status.** Production.

**B. Source.** [`core/pitch_aggregation.py`](../core/pitch_aggregation.py) `aggregate_events_by_pitch`, lines 158–217. Tolerance `DEFAULT_PITCH_TOLERANCE = 1e-6` (line 15).

**C. Excerpt.**

```python
        idx = _find_bin_index(midi, bin_midis, tolerance)
        if idx is None:
            bin_midis.append(midi)
            ...
        else:
            bin_event_counts[idx] += 1
            bin_weights[idx] += w
            bin_players[idx] += pc
```

```python
    doubling = max(0, event_count - distinct)
    distinct_ratio = distinct / event_count if event_count else 0.0
    diff_ratio = (distinct - 1) / max(event_count - 1, 1) if event_count > 1 else 0.0
    pairs = distinct * (distinct - 1) // 2 if distinct >= 2 else 0
```

**D. LaTeX.** Events $i,j$ merge if $|m_i-m_j|\le \varepsilon$ with $\varepsilon=10^{-6}$. After merge,

$$
n_{\mathrm{dbl}}=\max(0,N-K),\quad
r_{\mathrm{dist}}=\frac{K}{N}\ (N>0),\quad
r_{\mathrm{diff}}=\frac{K-1}{\max(N-1,1)}\ (N>1),\quad
P=\binom{K}{2}.
$$

Bin weight $W_k=\sum_{i\in B_k} w_i$. Player count in a bin sums Qty.

**E. Symbols.** $N$: `event_count`. $K$: `distinct_pitch_count`. $w_i$: per-event one-player density when the pipeline passes `weights`. $\varepsilon$: MIDI.

**F. Layman.** Exact unisons become one pitch. Extra players on the same pitch are doublings, not new notes.

**G. Specialist.** $\varepsilon$ is a numerical identity tolerance, not a psychoacoustic unison threshold. Qty does not create new bins (`qty_affects_pitch_structure` is False in the result dict).

**H. Conditions.** Always after M-007. Empty notes are skipped.

**I. Verification evidence.** `tests/test_pitch_aggregation.py`, `tests/test_unison_construct_separation.py`, `tests/test_near_unison_semantics.py`. Not executed.

---

### M-009 — Mean spectral weight per pitch bin

**A. Status.** Production input to spectral/chroma/harmonic-ratio helpers.

**B. Source.** [`core/pipeline.py`](../core/pipeline.py) `_bin_spectral_weights`, lines 62–64.

**C. Excerpt.**

```python
    return [b.total_weight / max(1, b.event_count) for b in pitch_agg.pitch_bins]
```

**D. LaTeX.**

$$
\bar{w}_k = \frac{W_k}{\max(1, n_k)}
$$

**E. Symbols.** $W_k$: `total_weight`. $n_k$: `event_count` in the bin.

**F. Layman.** Unison doublings do not inflate the spectral weight of a pitch: the bin uses the average of the event weights.

**G. Specialist.** Makes spectral moments invariant to exact unison row-splitting when weights are one-player densities.

**H. Conditions.** Always before spectral calls in `calculate_metrics`.

**I. Verification evidence.** Indirectly `tests/test_pitch_aggregation.py`, `tests/test_spectral_analysis.py`. Not executed.

---

### M-010 — Modified exponential decay

**A. Status.** Production kernel for interval compactness. Also used by the legacy event-level interval function.

**B. Source.** [`densidade_intervalar.py`](../densidade_intervalar.py) `modified_exponential_decay`, lines 225–243.

**C. Excerpt.**

```python
    if lamb is None:
        lamb = load_calibrated_parameters()
    if delta == 0:
        return 1.0
    return math.exp(-lamb * delta)
```

**D. LaTeX.**

$$
d(\delta;\lambda)=
\begin{cases}
1 & \delta=0 \\
e^{-\lambda\delta} & \delta\neq 0
\end{cases}
$$

Natural exponential (`math.exp`). $\lambda$ defaults to the JSON value (M-011).

**E. Symbols.** $\delta$: `delta` — **microtonal steps** when callers pass `2\times` semitones. $\lambda$: `lamb`. $d$: dimensionless weight.

**F. Layman.** Close pitches contribute almost 1; far pitches contribute almost 0. A true unison is forced to 1.

**G. Specialist.** This is a **software distance kernel**, not a sensory consonance model. The special case $\delta=0$ matches $e^{0}=1$, so it is redundant except for documenting intent. Comments elsewhere that cite Hutchinson / Malmberg / Kameoka are **not** implemented in this function.

**H. Conditions.** Called for every distinct-bin pair (M-012) and by legacy `calculate_interval_density`.

**I. Verification evidence.** `tests/test_densidade_intervalar.py`, `tests/plausibility/test_fb_interval_density.py`. Not executed.

---

### M-011 — Interval decay parameter $\lambda$

**A. Status.** Production constant load.

**B. Source.** [`densidade_intervalar.py`](../densidade_intervalar.py) `load_calibrated_parameters`, lines 71–93; file [`parameters/density_params.json`](../parameters/density_params.json) (`"lambda": 0.05`). Fallback `DEFAULT_LAMBDA = 0.05` (line 50). Duplicate default in [`config.py`](../config.py) `DEFAULT_LAMBDA = 0.05` (line 253) is **not** read by this loader.

**C. Excerpt.**

```python
                value = params.get('lambda', DEFAULT_LAMBDA)
```

**D. LaTeX.**

$$
\lambda = 0.05
$$

in the committed working tree (JSON). If the file is missing or unreadable, the same numeric fallback is used.

**E. Symbols.** $\lambda$: dimensionless per microtonal step.

**F. Layman.** A small number that decides how quickly far intervals “stop counting.”

**G. Specialist.** Not fitted at runtime. `calibrate_lambda` (M-055) can overwrite the JSON; that is a research tool, not the production path.

**H. Conditions.** Cached per resolved path. Tests may call `clear_lambda_cache`.

**I. Verification evidence.** `tests/test_densidade_intervalar.py`. Not executed.

---

### M-012 — Distinct-bin interval sum (raw $S$)

**A. Status.** Production.

**B. Source.** [`core/pitch_structure.py`](../core/pitch_structure.py) `calculate_interval_density_from_distinct_midis`, lines 18–38.

**C. Excerpt.**

```python
    for i in range(n):
        for j in range(i + 1, n):
            delta_semitones = abs(float(midis[i]) - float(midis[j]))
            delta = delta_semitones * 2.0
            total += modified_exponential_decay(delta, lamb)
```

**D. LaTeX.** For distinct-bin MIDI values $m_1,\ldots,m_K$ ($K\ge 2$; else $S=0$):

$$
S=\sum_{1\le i<j\le K} d\bigl(2|m_i-m_j|;\lambda\bigr)
$$

with $d$ from M-010.

**E. Symbols.** $S$: `raw` / `interval_sum_raw`. Factor $2$ converts semitones to the 24-step-per-octave microtonal scale used by the kernel.

**F. Layman.** Add a closeness score for every pair of different pitches.

**G. Specialist.** Extensive (grows when a new distinct pitch is added, all else equal, because new pairs are added and existing pair terms are unchanged). Exact unisons never appear as pairs. **Does not** apply the legacy “force $\delta\ge 0.25$” rule in M-051.

**H. Conditions.** `distinct_pitch_count < 2` → $(0,0)$ from `compute_interval_compactness_distinct`.

**I. Verification evidence.** `tests/test_interval_density_bound.py`, `tests/test_extensive_density_monotonic.py`, `tests/test_interval_blend_normalisation.py`. Not executed.

---

### M-013 — Effective interval cardinality (reported $D_V$)

**A. Status.** Production (`density.interval`).

**B. Source.** [`core/pitch_structure.py`](../core/pitch_structure.py) `effective_interval_cardinality`, lines 43–53. No log compression on $D_V$.

**C. Excerpt.**

```python
    if distinct_pitch_count < 2:
        return 0.0
    s = max(0.0, float(raw))
    return float((math.sqrt(1.0 + 8.0 * s) - 1.0) / 2.0)
```

**D. LaTeX.** For raw pair sum $S$ (M-012) and $K\ge 2$:

$$
D_V=\frac{\sqrt{1+8S}-1}{2}=n_{\mathrm{eff}}-1,
\qquad
\frac{n_{\mathrm{eff}}(n_{\mathrm{eff}}-1)}{2}=S.
$$

If $K<2$, $D_V=0$. Exact unison doublings do not change $S$ or $D_V$.

**E. Symbols.** $D_V$: `densidade_intervalar_val`. $n_{\mathrm{eff}}$ is the fully-adjacent pitch count ($K=1$ for every pair) that would yield the same $S$. Dimensionless.

**F. Layman.** How many fully packed neighbouring pitches would produce the same total closeness.

**G. Specialist.** Inverse of the triangular-number map. Adding a distinct pitch strictly increases $D_V$ because $S$ gains strictly positive pair terms ($0<K(\Delta)\le 1$). At fixed $n$, narrower intervals increase $S$ and therefore $D_V$. No $\log_{10}(1+x)$ is applied here.

**H. Conditions.** Always after M-012. Feeds the blend (M-023).

**I. Verification evidence.** `tests/test_effective_interval_cardinality.py` (T1–T7), `tests/test_interval_density_bound.py`.

---

### M-014 — Registral span

**A. Status.** Production subindex input; **not** a factor in $S_{\mathrm{ps}}$ (M-027).

**B. Source.** [`core/pitch_structure.py`](../core/pitch_structure.py) `compute_registral_span_distinct`, lines 65–70.

**C. Excerpt.**

```python
    return float(max(midis) - min(midis))
```

**D. LaTeX.**

$$
R=\max_k m_k-\min_k m_k\quad (K\ge 2);\qquad R=0\ (K<2).
$$

**E. Symbols.** $R$: semitones (`amplitude_st`).

**F. Layman.** Distance from the lowest to the highest distinct pitch.

**G. Specialist.** Distinct bins only. Unpitched excluded (M-007).

**H. Conditions.** Always computed; used in subindices and composite trace, not in $S$.

**I. Verification evidence.** `tests/test_subindices.py`, `tests/plausibility/test_fh_registral_texture.py`. Not executed.

---

### M-015 — Unknown dynamic → `mf`

**A. Status.** Production lookup precondition.

**B. Source.** [`core/orchestration.py`](../core/orchestration.py) `_normalize_dynamic`, lines 34–36.

**C. Excerpt.**

```python
    dyn = (dynamic or "mf").strip().lower()
    return dyn if dyn in known_dynamics else "mf"
```

**D. LaTeX.**

$$
\mathrm{dyn}'=
\begin{cases}
\mathrm{mf} & \text{empty or not in }\{\texttt{pppp},\ldots,\texttt{ffff}\}\\
\mathrm{lowercase}(\mathrm{dyn}) & \text{otherwise.}
\end{cases}
$$

**E. Symbols.** Known set from `config.DYNAMIC_LEVELS`.

**F. Layman.** A blank or unknown marking is treated as mezzo-forte.

**G. Specialist.** Software policy. Changes which table column is read (M-016).

**H. Conditions.** Before every `calcular_densidade` call in the slice helpers.

**I. Verification evidence.** `tests/test_instrument_registry.py`, `tests/test_unknown_instrument_policy.py`. Not executed.

---

### M-016 — Committed table lookup / interpolation (one-player CDM)

**A. Status.** Production for table-backed pitched instruments.

**B. Source.** Algorithm: [`instrumentos/pitch_interpolation.py`](../instrumentos/pitch_interpolation.py) `resolve_density_from_table` (lines 329–564), `_interpolate_linear` (261–274). Wrapper: [`instrumentos/spectral_lookup.py`](../instrumentos/spectral_lookup.py) `lookup_spectral_density` (63–84). Call site example: [`instrumentos/flute.py`](../instrumentos/flute.py) `calcular_densidade`, lines 88–98. **Equivalent locations:** all table-backed `instrumentos/*.py` `calcular_densidade` functions that call `lookup_spectral_density` (winds, brass, arco/technique strings).

**C. Excerpt (linear step).**

```python
    t = (target_midi - m1) / (m2 - m1)
    return float(v1 + t * (v2 - v1))
```

Lookup order (docstring + code): exact key → MIDI-equivalent key → interpolate/extrapolate. Missing dynamic raises `MissingCommittedDynamicError` (no runtime GPR). Empty table or unparsable note can fall back to `5.0` (`fallback_value` default, line 337). Deviation $>12$ semitones (`ERROR_DEVIATION_SEMITONES`) uses fallback 5.0 when that default is left in place.

**D. LaTeX.** Exact cell: $D=T(\mathrm{note},\mathrm{dyn})$ (tabulated; **no formula**). Interior linear interpolation between MIDI anchors $m_1<m_2$ with values $v_1,v_2$:

$$
t=\frac{m-m_1}{m_2-m_1},\qquad D=v_1+t(v_2-v_1).
$$

In-range `auto` with $\ge 4$ distinct anchors uses SciPy PCHIP (L-001) instead of this line. Outside-range uses the same linear formula on the edge pair (`provenance="extrapolated"`).

**E. Symbols.** $D$: one-player density (unclear physical unit; project name “CDM”). $T$: `spectral_data`. Fallback $5.0$ is a software constant, not a measured density.

**F. Layman.** Look up this instrument’s stored number for this written pitch and dynamic. If the table skipped that pitch, slide between neighbours.

**G. Specialist.** Tables are **reference data** (see §6). Interpolation is a metadata model. Comments in modules claim Dynamics_predicter / dest-Zenodo provenance; this audit does not re-derive those cells. Runtime does **not** implement the tail formulas still printed in `config.py`.

**H. Conditions.** Production `interpolation_method="auto"`, `allow_extrapolation=True`. Qty is **not** applied here.

**I. Verification evidence.** `tests/test_pitch_interpolation.py`, `tests/test_spectral_lookup.py`, `tests/test_dynamic_interpolation_contracts.py`, instrument contract tests. Not executed.

---

### M-017 — Unpitched pitch-independent CDM

**A. Status.** Production for bass drum, cymbals, gong, tam-tam.

**B. Source.** Example [`instrumentos/bass_drum.py`](../instrumentos/bass_drum.py) `DYNAMIC_CDM` line 68; `calcular_densidade` lines 75–83. Same pattern in `cymbals.py`, `gong.py`, `tamtam.py`.

**C. Excerpt.**

```python
    return float(DYNAMIC_CDM[dyn])
```

**D. LaTeX.** $D=\mathrm{CDM}(\mathrm{dyn})$ — **tabulated**, pitch-independent. No interpolation.

**E. Symbols.** `DYNAMIC_CDM` maps the ten dynamic names to floats. Units unclear. Module comments state NonTunPerc calibration “NO CALIBRATION ACHIEVED” versus pitched tables — recorded as in-repo provenance, not verified here.

**F. Layman.** For these instruments only the written dynamic matters, not the placeholder note.

**G. Specialist.** Lookup metadata, not a waveform analysis.

**H. Conditions.** After M-015. Note argument is ignored.

**I. Verification evidence.** `tests/test_percussion_nontunperc_modules.py`. Not executed.

---

### M-018 — Coarse-default instrument density

**A. Status.** Production only for registry names **without** a table-backed module.

**B. Source.** [`instrumentos/coarse_default.py`](../instrumentos/coarse_default.py) `_comfort_factor` 39–45; `calcular_densidade_for_profile` 53–64.

**C. Excerpt.**

```python
    base = 8.0
    comfort = _comfort_factor(midi, profile.comfortable_range)
    ...
    return float(base * comfort * brightness * attack * sustain * dynamic)
```

```python
    if midi < low:
        return max(0.45, 1.0 - (low - midi) / 24.0)
    return max(0.45, 1.0 - (midi - high) / 24.0)
```

**D. LaTeX.**

$$
D=8\cdot C\cdot B\cdot A\cdot S\cdot W_{\mathrm{dyn}}
$$

$$
C=
\begin{cases}
1 & m\in[m_L,m_H]\\
\max\bigl(0.45,\,1-(m_L-m)/24\bigr) & m<m_L\\
\max\bigl(0.45,\,1-(m-m_H)/24\bigr) & m>m_H.
\end{cases}
$$

$B,A,S,W_{\mathrm{dyn}}$ are discrete class multipliers (`_BRIGHTNESS`, `_ATTACK`, `_SUSTAIN`, `default_dynamic_response_curve`). Percussion family forces $S=0.8$.

**E. Symbols.** All factors dimensionless. $D$ is a heuristic score, not a table CDM.

**F. Layman.** If the project has no measured table, it invents a density from “how comfortable the register is” and a few style tags.

**G. Specialist.** Explicitly **not** external acoustic metadata. Can produce values on a different scale from table-backed instruments.

**H. Conditions.** Registry scaffold / unknown dedicated module (`IS_COARSE_DEFAULT`).

**I. Verification evidence.** `tests/test_instrument_density_registry_scaffold_contract_additional.py`, `tests/test_unknown_instrument_policy.py`. Not executed.

---

### M-019 — Quantity validation

**A. Status.** Production.

**B. Source.** [`core/quantity_scaling.py`](../core/quantity_scaling.py) `validate_quantity`, lines 32–41.

**C. Excerpt.**

```python
    if value < 1.0:
        raise ValueError(f"quantity must be >= 1, got {qty!r}")
    return value
```

**D. LaTeX.** Require $q\in\mathbb{R}$, finite, $q\ge 1$. Otherwise raise.

**E. Symbols.** $q$: Qty / player count (count of players, not a physical unit).

**F. Layman.** You cannot have zero or a fraction-of-a-player below 1.

**G. Specialist.** Software constraint. Rejects NaN/inf.

**H. Conditions.** All mass/RSS aggregations.

**I. Verification evidence.** `tests/test_quantity_scaling.py`. Not executed.

---

### M-020 — Linear sonic mass $M$

**A. Status.** Production (`density.sonic_mass`).

**B. Source.** [`core/quantity_scaling.py`](../core/quantity_scaling.py) `linear_orchestral_mass`, lines 71–75; applied in [`core/source_aggregation.py`](../core/source_aggregation.py) 112–126.

**C. Excerpt.**

```python
    return sum(float(base) * validate_quantity(qty) for base, qty in contributions)
```

**D. LaTeX.** After source merge (M-022),

$$
M=\sum_i q_i D_i
$$

**E. Symbols.** $D_i$: one-player density. $q_i$: Qty. $M$: `massa_sonora_val`. **Not** joules or kg; a linear player-weighted sum of table scores.

**F. Layman.** More players, or louder table cells, increase “mass.”

**G. Specialist.** Dynamics are **not** multiplied again here (`DYNAMIC_APPLIED_IN_MASS_FORMULA = False`). `SYMBOLIC_DYNAMIC_FACTORS` in `orchestration_mass.py` are unused on this path.

**H. Conditions.** Always in `compute_slice_orchestral_metrics`. Empty sources → $M=0$.

**I. Verification evidence.** `tests/test_quantity_scaling.py`, `tests/plausibility/test_fd_quantity_mass.py`. Not executed.

---

### M-021 — RSS instrument density $D_I$

**A. Status.** Production (`density.instrument`).

**B. Source.** [`core/quantity_scaling.py`](../core/quantity_scaling.py) `rss_pressure_equivalent`, lines 54–68.

**C. Excerpt.**

```python
        total += q * b * b
    return math.sqrt(total)
```

**D. LaTeX.**

$$
D_I=\sqrt{\sum_i q_i D_i^2}
$$

Identical incoherent sources with common $D$ reduce to $D\sqrt{Q}$ via `quantity_pressure_gain`.

**E. Symbols.** $D_I$: `densidade_instrumento_val`. Labelled “pressure-equivalent” in comments — **heuristic RSS**, not measured sound pressure.

**F. Layman.** Combining several sources the way one combines uncorrelated amplitudes: they do not simply add.

**G. Specialist.** Software model of incoherent addition. Not a physical microphone measurement. Coherent addition is explicitly not assumed (`COHERENT_PHASE_LOCKED_ADDITION_ASSUMED = False`).

**H. Conditions.** Same source list as $M$. Empty → $0$.

**I. Verification evidence.** `tests/test_quantity_scaling.py`, `tests/test_unpitched_aggregation_contract.py`. Not executed.

---

### M-022 — Source-group merge (row-splitting invariance)

**A. Status.** Production.

**B. Source.** [`core/source_aggregation.py`](../core/source_aggregation.py) `aggregate_event_sources`, lines 54–109.

**C. Excerpt.**

```python
            entry["player_count"] = float(entry["player_count"]) + qty
            ...
            if abs(existing - density) > 1e-9:
                raise ValueError(...)
```

**D. LaTeX.** Group key $(m,\mathrm{inst},\mathrm{dyn})$. Within a group $q\leftarrow\sum q$, $D$ must agree within $10^{-9}$ or the run fails.

**E. Symbols.** $m$ from `note_to_midi_strict`. Instrument lowercased.

**F. Layman.** One row “4 flutes on C4 mf” equals four rows of one flute on C4 mf.

**G. Specialist.** Invariance is a software contract, not an ensemble-acoustic theorem.

**H. Conditions.** Always before RSS/mass.

**I. Verification evidence.** `tests/test_quantity_scaling.py`. Not executed.

---

### M-023 — Blend $D_{\mathrm{blend}}$ (fixed-divisor, production)

**A. Status.** Production (`density.weighted`).

**B. Source.** [`core/composite.py`](../core/composite.py) `compute_blend_density` 27–40; `INSTRUMENT_BLEND_DIVISOR=10` (line 22). Called from `calculate_metrics` with `w=weight_factor` (default 0.5).

**C. Excerpt.**

```python
    return float(
        w * (float(DI) / INSTRUMENT_BLEND_DIVISOR) + (1.0 - w) * float(DV)
    )
```

**D. LaTeX.**

$$
D_{\mathrm{blend}}= w\frac{D_I}{10}+(1-w)D_V.
$$

No clamping of $D_I$ or $D_V$. No `unit_range` mode.

**E. Symbols.** $w$: `weight_factor` $\in\mathbb{R}$ (GUI typically $[0,1]$, not enforced here). $D_I$, $D_V$ from M-021, M-013.

**F. Layman.** A slider mixes “instrument-table strength” with effective interval cardinality.

**G. Specialist.** Fixed-divisor combination, not a data-dependent min–max. The instrument divisor 10 is a **software reference**, not a proven maximum.

**H. Conditions.** Always. Also computed with $(D_I,0)$ and $(0,D_V)$ as `weighted_orchestral` / `weighted_pitch`.

**I. Verification evidence.** `tests/test_unified_composite_contract.py`, `tests/test_blend_scale_snapshot.py`, `tests/plausibility/test_fe_blend_composite.py`.

---

### M-024 — Optional unit-range $D_V$ divisor

**A. Status.** **Removed in 5.2.0.** The flag `INTERVAL_BLEND_NORMALISATION` and `resolve_interval_dv_max` no longer exist.

**B. Source.** [`core/composite.py`](../core/composite.py) `resolve_interval_dv_max`, lines 29–41; flag in [`config.py`](../config.py) line 36.

**C. Excerpt.**

```python
    if mode == "unit_range":
        return math.log10(2.0) if cfg.USE_LOG_COMPRESSION else 1.0
```

**D. LaTeX.**

$$
D_{V,\max}=
\begin{cases}
\log_{10}2 & \text{unit\_range and log compression}\\
1 & \text{unit\_range and no log compression}\\
10 & \text{legacy.}
\end{cases}
$$

**E. Symbols.** Common log for $\log_{10}2$.

**F. Layman.** An alternate setting that treats the compressed interval score as if its ceiling were $\log_{10}2$.

**G. Specialist.** Approximate parity only: $D_I$ still uses 100. Results are not comparable across modes (`config.py` comment).

**H. Conditions.** Only if the config flag is changed.

**I. Verification evidence.** `tests/test_interval_blend_normalisation.py`. Not executed.

---

### M-025 — Optional z-score blend

**A. Status.** **Removed in 5.2.0.** `compute_weighted_density_normalized` no longer exists; production uses `compute_blend_density` only.

**B. Source.** [`core/composite.py`](../core/composite.py) `compute_weighted_density_normalized`, lines 207–212.

**C. Excerpt.**

```python
        DI_mean, DI_std = 50, 25
        DV_mean, DV_std = 5, 2.5
        DI_norm = (DI - DI_mean) / DI_std if DI_std > 0 else 0
        DV_norm = (DV - DV_mean) / DV_std if DV_std > 0 else 0
        return float(BLEND_SCALE * (w * DI_norm + (1 - w) * DV_norm))
```

**D. LaTeX.**

$$
D_z=10\left(w\frac{D_I-50}{25}+(1-w)\frac{D_V-5}{2.5}\right).
$$

**E. Symbols.** Hard-coded means/sds — not estimated from data.

**F. Layman.** A leftover alternate mixer using fake “typical” averages.

**G. Specialist.** Not a statistical z-score of a corpus. Dead production path unless a caller passes `metodo="z-score"`.

**H. Conditions.** Not used by the pipeline.

**I. Verification evidence.** `tests/test_core_extraction.py` (API surface). Not executed.

---

### M-026 — Composite vertical density

**A. Status.** Production (`density.total`).

**B. Source.** [`core/pitch_structure.py`](../core/pitch_structure.py) `compute_composite_vertical_density`, lines 107–127. `MAX_DENS_GLOBAL = 193.0` ([`config.py`](../config.py) line 28). `USE_LOG_COMPRESSION = True`.

**C. Excerpt.**

```python
    mass_boost = float(np.sqrt(max(0.0, sonic_mass)))
    pre_log = float(blend_density) * mass_boost / float(max_dens_global)
    total = pre_log
    if apply_log_compression:
        total = float(np.log10(1.0 + pre_log))
```

**D. LaTeX.**

$$
\beta=\sqrt{\max(0,M)},\qquad
T_{\mathrm{pre}}=\frac{D_{\mathrm{blend}}\,\beta}{193},\qquad
T=\log_{10}(1+T_{\mathrm{pre}}).
$$

If `USE_LOG_COMPRESSION` were false, $T=T_{\mathrm{pre}}$.

**E. Symbols.** $T$: `densidade_total_val`. $T_{\mathrm{pre}}$: `densidade_total_pre_log`. REF $=193$ is a **re-freeze calibration constant** (comment: least-squares match $\approx 192.6$), not a derived physical scale.

**F. Layman.** Mix the blend with “how much mass,” shrink by 193, then log-compress.

**G. Specialist.** Unified path for pitched and unpitched: **no** event-kind fallback. Heuristic composite. $\sqrt{M}$ is labelled “pressure-like” in comments but is applied to the software mass $M$.

**H. Conditions.** Always. $\beta$ is also stored as `dynamic_boost` (name is historical; it is $\sqrt{M}$).

**I. Verification evidence.** `tests/test_composite_unification_acceptance.py`, `tests/test_unified_composite_contract.py`, `tests/test_composite_from_blend_delegation.py`. Not executed.

---

### M-027 — Pitch-structure density $S_{\mathrm{ps}}$

**A. Status.** Production reported axis (`density.pitch_structure` / `refined`). **Not** the composite $T$.

**B. Source.** [`core/pitch_structure.py`](../core/pitch_structure.py) `compute_pitch_structure_density`, lines 86–104. `COMPOSITE_HARMONIC_DAMPING = 0.15` ([`config.py`](../config.py) line 82).

**C. Excerpt.**

```python
    entropy_factor = 1.0 + float(np.log1p(max(0.0, spectral_entropy)))
    harmonic_adjustment = 1.0 - float(harmonic_ratio) * COMPOSITE_HARMONIC_DAMPING
    return float(interval_sum_raw * entropy_factor * harmonic_adjustment)
```

**D. LaTeX.** For $K\ge 2$:

$$
S_{\mathrm{ps}}=S\cdot\bigl(1+\ln(1+\max(0,H))\bigr)\cdot\bigl(1-0.15\,\rho\bigr)
$$

where $H$ is spectral entropy (M-033), $\rho$ is the harmonic-ratio proxy (M-036), and $\ln$ is `np.log1p` (natural log). If $K<2$, $S_{\mathrm{ps}}=0$. Registral span is **not** a factor.

**E. Symbols.** $S$: raw interval sum (M-012). $\rho\in[0,1]$ by construction of M-036 when totals are positive.

**F. Layman.** Start from pairwise closeness, bump it if the pitch-weight distribution is more “spread out” in entropy, and slightly reduce it if pitches sit on the same pitch-class octaves.

**G. Specialist.** Heuristic product. Natural log here vs common log on $D_V$ and $T$. “Harmonic damping” is a software coefficient, not a tonal-harmony theory.

**H. Conditions.** Always computed; excluded from the unified composite product.

**I. Verification evidence.** `tests/test_extensive_density_monotonic.py`, `tests/test_subindices.py`. Not executed.

---

### M-028 — Absolute density

**A. Status.** Production (`density.absolute`).

**B. Source.** [`core/pipeline.py`](../core/pipeline.py) lines 247–251.

**C. Excerpt.**

```python
    if pitch_agg.distinct_pitch_count < 2:
        densidade_absoluta_val = 0.0
    else:
        densidade_absoluta_val = densidade_ponderada_val * np.log1p(total_tones_count)
```

with `total_tones_count = pitched_event_count` (line 247).

**D. LaTeX.**

$$
D_{\mathrm{abs}}=
\begin{cases}
0 & K<2\\
D_{\mathrm{blend}}\ln(1+N_{\mathrm{p}}) & K\ge 2
\end{cases}
$$

$N_{\mathrm{p}}$ is pitched **event** count (unisons count), not $K$.

**E. Symbols.** Natural log (`np.log1p`). $D_{\mathrm{abs}}$ dimensionless software unit.

**F. Layman.** If there are at least two different pitches, scale the blend by how many pitched notes (including doubles) are present.

**G. Specialist.** Mixed: threshold uses distinct bins; multiplier uses event cardinality. Name “absolute” is software vocabulary, not an absolute physical density.

**H. Conditions.** Always.

**I. Verification evidence.** `tests/plausibility/test_ff_absolute_density.py`. Not executed.

---

### M-029 — Complexity factor (metadata)

**A. Status.** Production metadata / subindex, **not** a factor in $T$.

**B. Source.** [`core/pipeline.py`](../core/pipeline.py) line 243.

**C. Excerpt.**

```python
    complexity_factor = 1.0 + float(np.log1p(spectral_entropy))
```

**D. LaTeX.**

$$
C=1+\ln(1+H)
$$

**E. Symbols.** Same $H$ as M-033. Natural log.

**F. Layman.** A second copy of the entropy bump, stored for explanation.

**G. Specialist.** Matches the entropy factor inside $S_{\mathrm{ps}}$ but is not multiplied into $T$. `cohesion_factor` is hard-coded `1.0` in the same assembly.

**H. Conditions.** Always attached to metadata.

**I. Verification evidence.** `tests/test_metric_metadata.py`. Not executed.

---

### M-030 — Spectral centroid, spread, skewness (MIDI domain)

**A. Status.** Production.

**B. Source.** [`spectral_analysis.py`](../spectral_analysis.py) `calculate_spectral_moments`, lines 59–101.

**C. Excerpt.**

```python
    centroid_midi = (pitches * amps).sum() / total
    spread_midi = np.sqrt(np.maximum(0, ((pitches - centroid_midi) ** 2 * amps).sum() / total))
    if spread_midi > 0:
        skew_num = ((pitches - centroid_midi) ** 3 * amps).sum() / total
        skewness = skew_num / (spread_midi ** 3)
```

```python
    centroid_freq = midi_to_hz(centroid_midi)
    spread_freq = midi_to_hz(centroid_midi + spread_midi) - centroid_freq if spread_midi > 0 else 0.0
```

Non-finite pitches/amps zeroed; `total<=0` → zeros and note `"Invalid"`.

**D. LaTeX.** Weights $a_i=\bar{w}_k$ (M-009), $A=\sum a_i$:

$$
\mu=\frac{\sum a_i m_i}{A},\quad
\sigma=\sqrt{\frac{\sum a_i(m_i-\mu)^2}{A}},\quad
\gamma_1=\frac{\sum a_i(m_i-\mu)^3}{A\,\sigma^3}\ (\sigma>0).
$$

Reported centroid $f(\mu)$ via M-003; reported spread $f(\mu+\sigma)-f(\mu)$ Hz.

**E. Symbols.** $m_i$: MIDI. $a_i$: software weights, not spectral magnitudes of a DFT.

**F. Layman.** Average pitch, how spread the pitches are, and whether the cloud leans high or low.

**G. Specialist.** Population-weighted moments in MIDI space. Hz spread is **not** the standard deviation of frequencies. Not an audio spectral centroid.

**H. Conditions.** Always on pitched bins. Empty → zeros.

**I. Verification evidence.** `tests/test_spectral_analysis.py`, `tests/plausibility/test_fg_spectral.py`. Not executed.

---

### M-031 — Excess spectral kurtosis

**A. Status.** Production (`spectral_kurtosis`).

**B. Source.** [`spectral_analysis.py`](../spectral_analysis.py) lines 164–169.

**C. Excerpt.**

```python
        kurt_num = ((pitches - centroid_midi) ** 4 * amps).sum() / total
        kurtosis = kurt_num / (spread_midi ** 4) - 3
```

**D. LaTeX.**

$$
\gamma_2=\frac{\sum a_i(m_i-\mu)^4}{A\,\sigma^4}-3\qquad(\sigma>0;\ \text{else }0).
$$

**E. Symbols.** Excess kurtosis (Gaussian $\to 0$). MIDI domain.

**F. Layman.** Whether pitch weights pile in the middle or sit in the tails.

**G. Specialist.** Same caveats as M-030.

**H. Conditions.** Part of `calculate_extended_spectral_moments`.

**I. Verification evidence.** `tests/test_spectral_analysis.py`. Not executed.

---

### M-032 — Spectral flatness

**A. Status.** Production.

**B. Source.** [`spectral_analysis.py`](../spectral_analysis.py) lines 171–177.

**C. Excerpt.**

```python
    nz_amps = amps[amps > 1e-10]
    if len(nz_amps) > 0:
        flatness = np.exp(np.log(nz_amps).mean()) / nz_amps.mean()
```

**D. LaTeX.** Over $\{a_i:a_i>10^{-10}\}$:

$$
F=\frac{\exp(\overline{\ln a})}{\bar a}.
$$

Empty → $0$.

**E. Symbols.** Geometric/arithmetic mean ratio. $\ln$ natural (`np.log`).

**F. Layman.** 1 if all (positive) weights are equal; lower if a few dominate.

**G. Specialist.** Wiener-like flatness on **weights**, not a power spectrum. Threshold $10^{-10}$ is a numerical policy.

**H. Conditions.** Extended moments.

**I. Verification evidence.** `tests/test_spectral_analysis.py`. Not executed.

---

### M-033 — Spectral entropy $H$

**A. Status.** Production; feeds M-027 and M-029.

**B. Source.** [`spectral_analysis.py`](../spectral_analysis.py) lines 189–203.

**C. Excerpt.**

```python
    prob = amps / total
    valid_mask = prob > 1e-10
    ...
            entropy = float(-np.sum(valid_probs * np.log2(valid_probs)))
    entropy = max(0.0, float(entropy))
```

One or fewer valid bins → $0$.

**D. LaTeX.**

$$
p_i=a_i/A,\qquad
H=-\sum_{p_i>10^{-10}} p_i\log_2 p_i,\qquad
H\leftarrow\max(0,H).
$$

**E. Symbols.** $H$: bits (`spectral_entropy`).

**F. Layman.** How evenly the weights are spread across the pitches.

**G. Specialist.** Shannon entropy of the weight distribution. Not audio spectral entropy. Clamped at 0 to suppress $-0$ from rounding.

**H. Conditions.** Extended moments; empty spectrum → 0.

**I. Verification evidence.** `tests/test_spectral_analysis.py`. Not executed.

---

### M-034 — Input-order 85% cumulative note-weight frequency

**A. Status.** Production descriptor. Canonical key `input_order_weight_quantile_hz`. Deprecated compatibility alias `spectral_rolloff` (same number). **Terminology correction 2026-09-17; numeric definition unchanged.** Existing workbooks keep the historical `spectral_rolloff` label. A frequency-sorted acoustic roll-off is a possible future feature only.

**B. Source.** [`spectral_analysis.py`](../spectral_analysis.py) `calculate_extended_spectral_moments` (input-order 85% weight quantile).

**C. Excerpt.**

```python
        cumsum = np.cumsum(amps)
        threshold = 0.85 * cumsum[-1]
        idx = np.searchsorted(cumsum, threshold)
        rolloff_midi = pitches[min(idx, len(pitches)-1)]
        rolloff_freq = midi_to_hz(rolloff_midi)
```

**D. LaTeX.** In **input order** (not sorted by MIDI):

$$
i^*=\min\{i: \sum_{j=0}^{i} a_j \ge 0.85\sum a\},\qquad
f_{\mathrm{ro}}=f(m_{i^*}).
$$

**E. Symbols.** $f_{\mathrm{ro}}$: Hz. Order-dependence is a real implementation fact.

**F. Layman.** Walk along the list of pitches until 85% of the weight is accumulated; report that pitch’s frequency.

**G. Specialist.** **Not** classical spectral roll-off (which sorts by frequency). Bin order follows aggregation insertion order (first occurrence of each MIDI).

**H. Conditions.** Extended moments.

**I. Verification evidence.** `tests/test_input_order_weight_quantile.py`, `tests/test_spectral_analysis.py`.

---

### M-035 — Chroma vector

**A. Status.** Production.

**B. Source.** [`spectral_analysis.py`](../spectral_analysis.py) `calculate_chroma_vector`, lines 249–265.

**C. Excerpt.**

```python
            chroma[int(round(p)) % 12] += a
    ...
        chroma /= total
```

**D. LaTeX.**

$$
c_{r}=\sum_{i:\, \mathrm{round}(m_i)\bmod 12 = r} a_i,\quad
\mathbf{c}\leftarrow \mathbf{c}/\|\mathbf{c}\|_1
\quad(\|\mathbf{c}\|_1>0).
$$

**E. Symbols.** 12-class vector, sum 1. Microtones snap via `round`.

**F. Layman.** How much weight sits on C vs C♯ vs D …

**G. Specialist.** Pitch-class histogram of rounded MIDI. Not a CQ chroma from audio.

**H. Conditions.** Always. Empty → zeros.

**I. Verification evidence.** `tests/test_spectral_analysis.py`. Not executed.

---

### M-036 — Harmonic-ratio **proxy** (octave-class)

**A. Status.** Production (`additional_metrics.harmonic_ratio`).

**B. Source.** [`spectral_analysis.py`](../spectral_analysis.py) `calculate_harmonic_ratio`.

**C. Excerpt.**

```python
        fundamental = pitches.min()
    intervals = pitches - fundamental
    residue = np.mod(intervals, 12.0)
    oct_dist = np.minimum(residue, 12.0 - residue)
    harmonic_mask = oct_dist <= 0.25
    ...
    return float(harm_energy / total_energy) if total_energy > 0 else 0.0
```

**D. LaTeX.** Let $m_0=\min_i m_i$ (unless an explicit fundamental is passed; production does not).

$$
r_i=(m_i-m_0)\bmod 12,\quad
\delta_i=\min(r_i,12-r_i),\quad
\rho=\frac{\sum_{i:\,\delta_i\le 0.25} a_i}{\sum a_i}.
$$

**E. Symbols.** $\rho$: dimensionless $[0,1]$. Threshold $0.25$ semitone.

**F. Layman.** Fraction of weight that sits on the same piano key-class as the lowest note (including octaves), within a quarter-semitone.

**G. Specialist.** **Not** integer frequency ratios $kf_0$. Terminology clarified 2026-09-17; the calculation is unchanged. A C–G fifth is **not** octave-class under this rule. Lowest MIDI is a software reference, not an acoustic $f_0$. Export key `harmonic_ratio` is a compatibility name.

**H. Conditions.** Always on pitched bins. Empty → 0.

**I. Verification evidence.** `tests/test_harmonic_ratio_octave_class.py`, `tests/test_microtonal_harmonic_ratio_fixture.py`.

---

### M-037 — Texture descriptors

**A. Status.** Production (`texture`).

**B. Source.** [`timbre_texture_analysis.py`](../timbre_texture_analysis.py) `calculate_texture_density`, lines 13–71.

**C. Excerpt.**

```python
        average_texture_density = float(mass / player_count)
    ...
        texture_variability = float(np.std(pitched))
        texture_contrast = float(max(pitched) - min(pitched))
```

Pipeline passes `all_player_counts=numeros_instr` and `all_densities=one_player_densities`.

**D. LaTeX.** $Q=\sum_e \max(1,q_e)$. Qty-weighted mean CDM $\bar{D}=(\sum_e D_e q_e)/Q$. Polyphony $K$ (pitched bins). If $K>1$, $\mathrm{sd}=$ sample/population **NumPy default** std of bin MIDI (L-006), contrast $=\max m-\min m$.

**E. Symbols.** `player_weighted_texture_mass` is set equal to $Q$ (not $M$). `texture_polyphony` aliases pitch polyphony.

**F. Layman.** How many players, average table-density, how many different pitches, and how wide those pitches sit.

**G. Specialist.** `np.std` default `ddof=0` (population). Contrast duplicates M-014 when bins match. Average uses full-slice Qty including unpitched.

**H. Conditions.** Always.

**I. Verification evidence.** `tests/test_timbre_texture.py`, `tests/plausibility/test_fh_registral_texture.py`. Not executed.

---

### M-038 — Timbre blend / diversity / dominance

**A. Status.** Production (`timbre`).

**B. Source.** [`timbre_texture_analysis.py`](../timbre_texture_analysis.py) `calculate_timbre_blend`, lines 76–192.

**C. Excerpt.**

```python
    timbre_diversity = len(unique_instruments) / len(instruments) if len(instruments) > 0 else 0
    density_variance = np.var(density_values) if len(density_values) > 1 else 0
    blend_index = 1 / (1 + density_variance) if density_variance != 0 else 1
    ...
    timbre_dominance = max_count / len(instruments) if len(instruments) > 0 else 0.0
```

**D. LaTeX.** Let $U$ be unique instrument name strings, $N$ events:

$$
\mathrm{div}=U/N,\quad
v=\mathrm{Var}(\{\bar D_u\}),\quad
B=\frac{1}{1+v}\ (v\neq 0;\ \text{else }1),\quad
\mathrm{dom}=\frac{\max_u n_u}{N}.
$$

`timbre_balance` $=B$. Family shares use a **hard-coded incomplete** family list (winds list + `violino` only).

**E. Symbols.** Variance is `np.var` default `ddof=0` over **per-instrument mean densities**. Names are compared as raw strings (case-sensitive).

**F. Layman.** More different instrument names → higher diversity. If their average table-densities are similar, “blend” is high.

**G. Specialist.** Heuristic. Family contributions are incomplete relative to the live registry (brass, most strings, percussion omitted). Not timbre in the acoustic sense.

**H. Conditions.** Always; uses full instrument list including unpitched.

**I. Verification evidence.** `tests/test_timbre_texture.py`. Not executed.

---

### M-039 — Orchestration register balance / Gini-like evenness

**A. Status.** Production (`orchestration`).

**B. Source.** [`timbre_texture_analysis.py`](../timbre_texture_analysis.py) `calculate_orchestration_balance`, lines 197–361. Bands: baixo $[0,48)$, médio $[48,72)$, agudo $[72,108)$.

**C. Excerpt.**

```python
        register_balance = -sum(d * np.log2(d) for d in nonzero_densities) / np.log2(len(registers))
    density_balance = 1 - (max(normalized_densities.values()) - min(normalized_densities.values()))
        gini = sum((2*i - n - 1) * sorted_densities[i] for i in range(n)) / (n * sum(sorted_densities))
        orchestration_evenness = 1 - abs(gini)
```

**D. LaTeX.** Let $p_r$ be density-share in register $r$ (MIDI vs **bin weights**, zip of `bin_midis` and `bin_weights_spectral`; instruments argument is unused in the arithmetic).

$$
B_{\mathrm{reg}}=\frac{-\sum_{p_r>0}p_r\log_2 p_r}{\log_2 3},\quad
B_{\mathrm{dens}}=1-(\max p-\min p).
$$

On sorted $p_{(0)}\le p_{(1)}\le p_{(2)}$:

$$
G=\frac{\sum_{i=0}^{2}(2i-3-1)p_{(i)}}{3\sum p},\quad
E=1-|G|.
$$

Aliases: `orchestration_balance=E`, `pitch_balance=B_{\mathrm{reg}}`, `instrument_balance=B_{\mathrm{dens}}`.

**E. Symbols.** Pitches $\ge 108$ fall into **no** band (loop `break` never assigns). Weights are mean bin CDMs, not Qty.

**F. Layman.** Is the weight piled in the bass, middle, or treble, or spread around?

**G. Specialist.** Three-band Shannon evenness and a three-point Gini-like index. Different bands than `DEFAULT_REGISTER_BANDS` (M-040). `instruments` is unused — a code/docs mismatch.

**H. Conditions.** Always; empty pitches → zeros.

**I. Verification evidence.** `tests/test_timbre_texture.py`. Not executed.

---

### M-040 — Subindex register occupancy and entropy

**A. Status.** Production subindices (`density_subindices.registral`).

**B. Source.** [`core/registral_density.py`](../core/registral_density.py) 17–41; assembled in [`core/subindices.py`](../core/subindices.py) 117–128. Bands from `DEFAULT_REGISTER_BANDS` (`config.py` 73–79): very_low $[0,36)$, low $[36,48)$, mid $[48,72)$, high $[72,84)$, very_high $[84,128)$.

**C. Excerpt.**

```python
    return {name: counts[name] / total for name in bands}
...
    return float(-sum(p * np.log2(p) for p in values))
```

`register_entropy` returns 0 if $\le 1$ positive proportion.

Production compression:

```python
    registral_compression = 1.0 / (1.0 + pitch_span) if distinct_pitch_count >= 2 else 0.0
    registral_dispersion = pitch_span / max(1, distinct_pitch_count - 1) if distinct_pitch_count > 1 else 0.0
```

**D. LaTeX.** Occupancy $p_b=n_b/\sum n_{b'}$ over **in-band** distinct-bin midis only.

$$
H_{\mathrm{reg}}=-\sum_{p_b>0}p_b\log_2 p_b,\quad
\tilde H=H_{\mathrm{reg}}/\log_2 5,
$$

$$
\kappa=\frac{1}{1+R}\ (K\ge 2),\quad
\Delta=\frac{R}{\max(1,K-1)}\ (K>1).
$$

**E. Symbols.** $R$ from M-014. Five bands vs three in M-039.

**F. Layman.** Which register shelves are occupied, and how squeezed the chord is.

**G. Specialist.** `compute_registral_density` (same file, lines 44–81) is **not** on the production path: it uses all event midis and $\kappa=1/(1+R)$ without the $K<2\to 0$ guard.

**H. Conditions.** Subindex assembly always.

**I. Verification evidence.** `tests/test_subindices.py`. Not executed.

---

### M-041 — Non-production registral compactness

**A. Status.** Legacy / unused by `calculate_metrics`.

**B. Source.** [`core/pitch_structure.py`](../core/pitch_structure.py) `compute_registral_compactness`, lines 77–83.

**C. Excerpt.**

```python
    return 1.0 / (1.0 + registral_span_semitones / 12.0)
```

**D. LaTeX.**

$$
\kappa_{12}=\frac{1}{1+R/12}.
$$

**E. Symbols.** Octave-scaled. Distinct from production $\kappa=1/(1+R)$.

**F. Layman.** A leftover “tighter if within an octave” score.

**G. Specialist.** File comments forbid wiring this into the pipeline.

**H. Conditions.** Not called from `calculate_metrics`.

**I. Verification evidence.** Comments / unit tests of the helper if present. `tests/test_subindices.py` checks production $\kappa$. Not executed.

---

### M-042 — Event / duration-weighted counts

**A. Status.** Production subindex / optional construct helper.

**B. Source.** [`core/subindices.py`](../core/subindices.py) 91–115; [`core/event_density.py`](../core/event_density.py) 15–37; duration from [`core/temporal.py`](../core/temporal.py) 27–34.

**C. Excerpt.**

```python
    player_weighted_count = float(sum(player_counts))
    ...
        duration_weighted_count = float(
            sum(pc * d for pc, d in zip(player_counts, durations))
        )
```

**D. LaTeX.** $N=|E|$, $Q=\sum \max(1,q_e)$. If every event has duration $t_e>0$:

$$
Q_t=\sum_e q_e t_e.
$$

`event_density.py` requires `len(durations)==event_count`; subindices also allow a second branch when all durations resolve.

**E. Symbols.** $t_e$: seconds when onset/offset/duration exist; otherwise $Q_t$ is `None`.

**F. Layman.** Headcount of notes and players; optionally weight by how long each note lasts.

**G. Specialist.** Duration is score/MIDI time metadata, not acoustic duration of decay.

**H. Conditions.** $Q_t$ only with complete timing. Untimed GUI slices omit it.

**I. Verification evidence.** `tests/test_event_density.py`, `tests/test_score_analysis.py`. Not executed.

---

### M-043 — Temporal slice membership

**A. Status.** Production for `analyze_score`.

**B. Source.** [`core/temporal.py`](../core/temporal.py) `event_is_active_at` 79–86; `group_events_into_slices` 93–153.

**C. Excerpt.**

```python
    return float(event.onset) <= time + epsilon < float(offset)
```

with $\varepsilon=10^{-9}$. `event_boundary`: one slice per distinct onset; duration to next onset. `instantaneous` or no onsets: single slice of all events.

**D. LaTeX.** Active set at boundary $t$:

$$
A(t)=\{e: o_e \le t+\varepsilon < \mathrm{off}_e\}
$$

half-open $[o,\mathrm{off})$. If offset missing, membership is $|o_e-t|\le\varepsilon$.

**E. Symbols.** Times in seconds. Slice duration $\Delta t=t_{k+1}-t_k$ when a next boundary exists.

**F. Layman.** At each new note start, collect everything still sounding.

**G. Specialist.** Standard half-open interval policy. Does not parse MusicXML divisions itself (comment).

**H. Conditions.** `analyze_score` only.

**I. Verification evidence.** `tests/test_score_analysis.py`, `tests/plausibility/test_fi_temporal_score.py`. Not executed.

---

### M-044 — Time-series summary of $T$

**A. Status.** Production score summary.

**B. Source.** [`core/temporal.py`](../core/temporal.py) `summarize_time_series`, lines 156–175.

**C. Excerpt.**

```python
        "density_total_mean": float(np.mean(arr)),
        "density_total_median": float(np.median(arr)),
        "density_total_max": float(np.max(arr)),
        "density_total_min": float(np.min(arr)),
        "density_total_variance": float(np.var(arr)),
```

**D. LaTeX.** Over slice totals $T_k$: mean, median, min, max, population variance (`np.var` ddof 0).

**E. Symbols.** Same $T$ as M-026.

**F. Layman.** Average / typical / extreme composite density across the piece’s slices.

**G. Specialist.** Unweighted by slice duration.

**H. Conditions.** After all slices.

**I. Verification evidence.** `tests/test_score_analysis.py`. Not executed.

---

### M-045 — Subindex chroma concentration and family diversity

**A. Status.** Production subindices.

**B. Source.** [`core/subindices.py`](../core/subindices.py) lines 130–136.

**C. Excerpt.**

```python
    chroma_concentration = float(np.max(chroma)) if chroma.size else 0.0
    family_diversity = len(family_ids) / max(1, event_count)
```

**D. LaTeX.** $\mathrm{conc}=\max_r c_r$. $\mathrm{fam}=|\{\mathrm{family}(e)\}|/\max(1,N)$.

**E. Symbols.** Families from event metadata, not M-038’s incomplete map.

**F. Layman.** Is one pitch class dominating? How many instrument families?

**G. Specialist.** Heuristic descriptors.

**H. Conditions.** Always in subindex block.

**I. Verification evidence.** `tests/test_subindices.py`. Not executed.

---

### M-046 — Diagnostic sensitivity weighted sum

**A. Status.** Research / diagnostic (`run_sensitivity_analysis`). **Does not** change `calculate_metrics`.

**B. Source.** [`core/sensitivity.py`](../core/sensitivity.py) `_weighted_sum` 115–128; weights `DEFAULT_WEIGHT_SETS` 14–62.

**C. Excerpt.**

```python
        total += float(w) * val
        weight_sum += float(w)
    if weight_sum > 0:
        total /= weight_sum
```

**D. LaTeX.** Over available normalised subindices $x_c$ with weights $w_c$:

$$
\tilde T=\frac{\sum_c w_c x_c}{\sum_c w_c}.
$$

Missing constructs are skipped (warning), not zero-filled.

**E. Symbols.** $x_c$ from `normalized` or selected raw fields. Baseline set sums to 1.0; `balanced_equal_weights` uses $1/6$.

**F. Layman.** “What if we re-weighted the explanation ingredients?” — a thought experiment.

**G. Specialist.** Explicitly not empirical validation. Different construct than production $T$.

**H. Conditions.** Reporting / GUI sensitivity, not the core total.

**I. Verification evidence.** `tests/test_export_and_sensitivity.py`. Not executed.

---

### M-047 — RMSE / MAE (validation utilities)

**A. Status.** Research/validation.

**B. Source.** [`validation/metrics.py`](../validation/metrics.py) 45–68.

**C. Excerpt.**

```python
    return float(np.sqrt(np.mean((x - y) ** 2)))
...
    return float(np.mean(np.abs(x - y)))
```

**D. LaTeX.**

$$
\mathrm{RMSE}=\sqrt{\frac{1}{n}\sum(x_i-y_i)^2},\qquad
\mathrm{MAE}=\frac{1}{n}\sum|x_i-y_i|.
$$

**E. Symbols.** $x$ predicted, $y$ observed. Empty / length mismatch raise.

**F. Layman.** Average size of prediction mistakes.

**G. Specialist.** Standard errors; not used inside `calculate_metrics`.

**H. Conditions.** When expert/listening data are supplied to validation scripts.

**I. Verification evidence.** `tests/test_validation_framework.py`. Not executed.

---

### M-048 — Bootstrap CI for the mean

**A. Status.** Research/validation.

**B. Source.** [`validation/metrics.py`](../validation/metrics.py) `bootstrap_ci`, lines 71–94.

**C. Excerpt.**

```python
        sample = rng.choice(arr, size=arr.size, replace=True)
        means.append(float(np.mean(sample)))
    alpha = 1.0 - confidence
    lower = float(np.quantile(means, alpha / 2))
    upper = float(np.quantile(means, 1 - alpha / 2))
    return float(np.mean(arr)), lower, upper
```

Defaults: $B=2000$, confidence $0.95$, seed $42$.

**D. LaTeX.** Percentile bootstrap of the mean: resample $n$ with replacement $B$ times; report sample mean and the $\alpha/2$ and $1-\alpha/2$ quantiles of bootstrap means.

**E. Symbols.** `np.random.default_rng`. Quantiles: NumPy default quantile interpolation (L-007).

**F. Layman.** A range for the average if we re-drew the same-sized sample many times.

**G. Specialist.** i.i.d. resampling assumption. Not a CI for a metric inside the pipeline.

**H. Conditions.** Validation scripts.

**I. Verification evidence.** `tests/test_validation_framework.py`. Not executed.

---

### M-049 — Mean pairwise Pearson (optional IRR)

**A. Status.** Research stub. **Not** Krippendorff’s $\alpha$. Canonical name `mean_pairwise_pearson`; `krippendorff_alpha_placeholder` is a deprecated alias.

**B. Source.** [`validation/metrics.py`](../validation/metrics.py) `mean_pairwise_pearson`.

**C. Excerpt.**

```python
                r = float(np.corrcoef(rows[i], rows[j])[0, 1])
    return float(np.mean(correlations))
```

Returns `None` if shape is insufficient or no pair has positive variance.

**D. LaTeX.** Mean of pairwise Pearson $r_{ij}$ over rater rows with $\sigma>0$. No closed $\alpha$ formula is implemented.

**E. Symbols.** `ratings_matrix` rows = raters.

**F. Layman.** “Do raters move together?” — a rough hint only.

**G. Specialist.** Canonical name is now `mean_pairwise_pearson`. `krippendorff_alpha_placeholder` is a deprecated alias. Printed labels must not say Krippendorff’s $\alpha$.

**H. Conditions.** Optional IRR script only; unused until multi-rater corpora exist.

**I. Verification evidence.** `tests/test_validation_framework.py`.

---

### M-050 — Rubric total

**A. Status.** Research (score-only upgrade rubric).

**B. Source.** [`validation/rubric_scoring.py`](../validation/rubric_scoring.py) `score_submission` 116–125; band check 108–113.

**C. Excerpt.**

```python
    total = sum(dimension_scores.values())
```

```python
        if band["min"] <= total <= band["max"]:
            return str(band["label"])
```

**D. LaTeX.** $T_{\mathrm{rub}}=\sum_d s_d$ with each $s_d\in[0,w_d]$. Interpretation: first band with $T_{\mathrm{rub}}\in[\min,\max]$.

**E. Symbols.** Integer weights from rubric JSON. Not a density metric.

**F. Layman.** Add checklist points and read the band label.

**G. Specialist.** Documentation/process score, not an acoustic calculation.

**H. Conditions.** `validation/scripts/score_upgrade_rubric.py`.

**I. Verification evidence.** `tests/test_rubric_scoring.py`. Not executed.

---

### M-051 — Legacy event-level interval density

**A. Status.** Legacy. **Not** used by `calculate_metrics` (which uses M-012 on bins).

**B. Source.** [`densidade_intervalar.py`](../densidade_intervalar.py) `calculate_interval_density`, lines 274–355; normalized wrapper 358–372.

**C. Excerpt.**

```python
            if delta_semitons < 0.01:
                if notas[i] != notas[j]:
                    delta_semitons = max(delta_semitons, 0.25)
            delta = delta_semitons * 2
            densidade_base = modified_exponential_decay(delta, lamb)
```

For $n>10$ and `use_optimization=True`, may use `vectorized_density_calculation` (M-052) **without** the 0.25-semitone force.

**D. LaTeX.** Pairwise sum over **events** (unisons included as $\delta=0\to 1$). If two **different strings** have $|m_i-m_j|<0.01$, $\Delta_{\mathrm{st}}\leftarrow\max(\Delta_{\mathrm{st}},0.25)$ on the loop path only.

**E. Symbols.** Same kernel as M-010.

**F. Layman.** Older “count every note row, even two people on the same pitch.”

**G. Specialist.** Scientifically different from M-012. Vectorised shortcut can **disagree** with the loop on near-unison different spellings.

**H. Conditions.** Tests, calibration, visualisation — not the pipeline.

**I. Verification evidence.** `tests/test_densidade_intervalar.py`. Not executed.

---

### M-052 — Vectorised pairwise interval sum

**A. Status.** Optional acceleration for M-051.

**B. Source.** [`utils/optimization.py`](../utils/optimization.py) 16–80.

**C. Excerpt.**

```python
    distances = np.abs(pitches[:, np.newaxis] - pitches[np.newaxis, :])
    return np.triu(distances, k=1)
```

Density: apply `decay_func` where distances $>0$, then sum (remaining lines 78+).

**D. LaTeX.** $S=\sum_{i<j} d_{\mathrm{func}}(|m_i-m_j|)$ with the caller’s `decay_func`. In M-051 the caller passes $\delta=2|m_i-m_j|$ into M-010.

**E. Symbols.** Upper triangle only.

**F. Layman.** Same pair sum, computed in a matrix instead of nested loops.

**G. Specialist.** `mask = distances > 0` drops exact unisons. Combined with M-051’s loop-only 0.25-semitone patch, the two implementations can diverge.

**H. Conditions.** `calculate_interval_density` when $n>10$ and import succeeds.

**I. Verification evidence.** `tests/test_optimization.py`. Not executed.

---

### M-053 — $\lambda$ calibration objective

**A. Status.** Research/test-only (`calibrate_lambda`). Can overwrite `parameters/density_params.json`.

**B. Source.** [`densidade_intervalar.py`](../densidade_intervalar.py) 114–151.

**C. Excerpt.**

```python
            density = calculate_interval_density(notes, lamb=lambda_val)
            density_norm = 2 * (density / max(experimental_data.values())) - 1
            error_sum += (density_norm - exp_val) ** 2
```

Bounds $\lambda\in[0.01,1]$, start `DEFAULT_LAMBDA`, method `L-BFGS-B` (L-002). Default data `CONSONANCE_RATINGS` (lines 40–47).

**D. LaTeX.**

$$
\hat\lambda=\arg\min_{\lambda\in[0.01,1]}\sum_k\left(2\frac{S_k(\lambda)}{\max_j y_j}-1-y_k\right)^2
$$

where $S_k$ is M-051 on a C4-dyad and $y_k$ are the dict values (not re-derived here).

**E. Symbols.** $y_k$ stored as “consonance” in $[-1,1]$ style, but several keys are **semitone numbers** 0,2,3,… while `dyad_notes_from_semitone_interval` uses those integers. Comments cite literature names; this audit does **not** treat those citations as verified sources of the numbers.

**F. Layman.** Tweak $\lambda$ so the old interval function roughly matches a small table of target scores.

**G. Specialist.** Uses the **legacy** event-level $S$, not production M-012. Fitting is optional and offline.

**H. Conditions.** Manual / demo (`demonstrate_calibration`). Not called by `calculate_metrics`.

**I. Verification evidence.** `tests/test_densidade_intervalar.py`. Not executed.

---

### M-054 — mf-anchor ratio table builder

**A. Status.** Research/tooling (offline table generation). Not a runtime lookup.

**B. Source.** [`instrumentos/mf_anchor_dynamic_extrapolation.py`](../instrumentos/mf_anchor_dynamic_extrapolation.py) 8–62.

**C. Excerpt.**

```python
            pp_ratio = float(ref["pp"]) / float(ref["mf"])
            ff_ratio = float(ref["ff"]) / float(ref["mf"])
        ...
            "pp": round(mf * pp_ratio, 6),
            "mf": mf,
            "ff": round(mf * ff_ratio, 6),
```

Fallback ratios: median of $T_{\mathrm{ref}}(\cdot,\mathrm{pp})/T_{\mathrm{ref}}(\cdot,\mathrm{mf})$ across the reference module (default violin).

**D. LaTeX.** For each note with measured $D_{\mathrm{mf}}$:

$$
D_{\mathrm{pp}}=\mathrm{round}(D_{\mathrm{mf}}\cdot r_{\mathrm{pp}},6),\quad
D_{\mathrm{ff}}=\mathrm{round}(D_{\mathrm{mf}}\cdot r_{\mathrm{ff}},6)
$$

with $r$ from the same note in the reference table, else the median ratio.

**E. Symbols.** Six-decimal rounding is a software policy. Only three dynamics are produced.

**F. Layman.** If only mezzo-forte was measured, copy the violin’s soft/loud proportions.

**G. Specialist.** Offline heuristic. Production modules now commit 10-level ladders; this helper is not the live path.

**H. Conditions.** Import-time tooling / generation scripts.

**I. Verification evidence.** Indirect instrument generation tests. Not executed.

---

### M-055 — Unused symbolic dynamic multipliers

**A. Status.** Legacy / unused on the production mass path.

**B. Source.** [`core/orchestration_mass.py`](../core/orchestration_mass.py) `SYMBOLIC_DYNAMIC_FACTORS`, lines 24–34.

**C. Excerpt.**

```python
SYMBOLIC_DYNAMIC_FACTORS: dict[str, float] = {
    "pppp": 0.2,
    ...
    "ffff": 3.0,
}
```

Comments: not applied when instrument modules already encode dynamics.

**D. LaTeX.** A map $W_{\mathrm{legacy}}(\mathrm{dyn})\in\{0.2,\ldots,3.0\}$. **Not multiplied** in `compute_orchestration_mass`.

**E. Symbols.** Dimensionless software weights. `mp` is absent from the dict.

**F. Layman.** An old “p is quieter than ff” table that the live mass formula no longer uses.

**G. Specialist.** Documented to prevent readers from assuming a second dynamic law.

**H. Conditions.** Not in `calculate_metrics`.

**I. Verification evidence.** `tests/test_quantity_scaling.py` (dynamic-once contract). Not executed.

---

### M-056 — Config tail formulas (not executed at runtime)

**A. Status.** Documentation / historical. **Not implemented** in production lookup.

**B. Source.** Comments only in [`config.py`](../config.py) lines 38–62 (`DYN_TAIL_SHRINK = 0.5`). Contrast: [`instrumentos/pitch_interpolation.py`](../instrumentos/pitch_interpolation.py) lines 83–86 (`MissingCommittedDynamicError` — runtime GPR/tail removed).

**C. Excerpt (comment, not executable).**

```python
#     s_soft(m) = max(0, ln(A_mf/A_pp) / N_soft)   # N_soft = steps pp→mf (=3)
#     soft:  ln A = ln A_pp − s_soft · Σ_{i=1..j} γ^i
```

**D. LaTeX.** The comments describe, for $j$ steps outside $[pp,ff]$ and $\gamma=0.5$:

$$
s_{\mathrm{soft}}(m)=\max\bigl(0,\ln(A_{\mathrm{mf}}/A_{\mathrm{pp}})/3\bigr),\quad
\ln A=\ln A_{\mathrm{pp}}-s_{\mathrm{soft}}\sum_{i=1}^{j}\gamma^i
$$

(and the loud-side analogue). **This audit does not treat those equations as live code.** They remain in `tools/legacy_gpr_dynamic_interpolation.py` as research/offline history.

**E. Symbols.** $A$ in the comments is an amplitude-like table value. $\gamma=$ `DYN_TAIL_SHRINK`.

**F. Layman.** An old idea for inventing pppp/ffff from measured pp/mf/ff. The running app no longer does that.

**G. Specialist.** Implementation/documentation discrepancy: config still explains a removed model. `DENSITY_FLOOR=1e-9` is described as an unreachable assert, not the positivity mechanism.

**H. Conditions.** Not on `calcular_densidade`.

**I. Verification evidence.** `tests/test_removed_perceptual_options.py`, `tests/test_dynamic_interpolation_contracts.py`. Not executed.

---

### M-057 — Range eligibility

**A. Status.** Production validation (rejects out-of-range notes).

**B. Source.** [`core/pitch_range_validation.py`](../core/pitch_range_validation.py) `_midi_in_sounding_range` 14–15.

**C. Excerpt.**

```python
    return (low - _RANGE_EPS) <= midi <= (high + _RANGE_EPS)
```

**D. LaTeX.** Accept if $m\in[m_L-\varepsilon,m_H+\varepsilon]$ with $\varepsilon=10^{-6}$ (`_RANGE_EPS`, line 11).

**E. Symbols.** MIDI. This is an eligibility gate, not a density formula.

**F. Layman.** A note far outside the instrument’s declared sounding range is rejected.

**G. Specialist.** Registry ranges are modelling assumptions (`config.py` also says register bands are not universal acoustic truth).

**H. Conditions.** Slice validation before/with analysis depending on caller.

**I. Verification evidence.** `tests/test_instrument_metadata_range_contracts.py`, `tests/test_instrument_register_contracts.py`. Not executed.

---

## 5. External-library operations

Project-defined scaling around these calls is already in the `M-` entries. Here the **library call** is recorded without reproducing the vendor derivation.

### L-001 — SciPy PCHIP interpolator

- **Call site:** [`instrumentos/pitch_interpolation.py`](../instrumentos/pitch_interpolation.py) `_interpolate_pchip`, lines 277–295.
- **Import:** `from scipy.interpolate import PchipInterpolator` (lines 20–25); `_HAS_PCHIP` false if import fails.
- **Call:** `PchipInterpolator(midis, values, extrapolate=False)` then `interpolator(target_midi)`.
- **Explicit arguments:** monotone cubic interpolant on sorted MIDI anchors; **no extrapolation** (`extrapolate=False`). Requires `MIN_PCHIP_ANCHORS = 4`.
- **Defaults (scipy 1.13.1):** `axis=0`, `extrapolate` default would be True if omitted — here it is **explicitly False**.
- **Layman.** Draw a smooth curve through the table that does not overshoot like a wild polynomial.
- **Specialist.** PCHIP is a shape-preserving cubic. Behaviour of the cubic pieces is SciPy’s; this project only supplies the knots and refuses out-of-range evaluation (then falls back to M-016 linear).
- **Docs consulted:** SciPy `scipy.interpolate.PchipInterpolator` (installed 1.13.1).
- **Limitations:** non-finite or $|D|\ge 10^{12}$ → treat as failure and use linear.

### L-002 — SciPy L-BFGS-B

- **Call site:** [`densidade_intervalar.py`](../densidade_intervalar.py) `minimize`, lines 142–147.
- **Import:** `from scipy.optimize import minimize`.
- **Call:** `minimize(objective, [DEFAULT_LAMBDA], bounds=bounds, method='L-BFGS-B')`.
- **Layman.** Automatically search for a $\lambda$ that reduces the squared error.
- **Specialist.** Bound-constrained quasi-Newton. Objective is M-053. Not on the production path.
- **Docs consulted:** SciPy `scipy.optimize.minimize` (1.13.1).

### L-003 — SciPy Gaussian KDE

- **Call site:** [`spectral_analysis.py`](../spectral_analysis.py) `robust_gaussian_kde`, lines 39–48.
- **Import:** `from scipy.stats import gaussian_kde`.
- **Call:** `gaussian_kde(data, weights=weights, bw_method=bw_method)`; on `LinAlgError`, retry with $\mathcal{N}(0,10^{-6})$ jitter (`np.random.normal`).
- **Production:** **not called** from `calculate_metrics`.
- **Layman.** Optional smooth density estimate of a 1-D sample.
- **Specialist.** Silverman/Scott bandwidth if `bw_method` is None (SciPy default). Jitter is a project safeguard. Random jitter is **not seeded**.
- **Docs consulted:** SciPy `scipy.stats.gaussian_kde`.

### L-004 — SciPy Spearman / Kendall

- **Call site:** [`validation/metrics.py`](../validation/metrics.py) `stats.spearmanr` / `stats.kendalltau` (lines 26, 41).
- **Import:** `from scipy import stats`.
- **Explicit:** arrays `x,y`; require $n\ge 3$ and equal length (project checks).
- **Defaults (scipy 1.13.1):** Spearman `nan_policy='propagate'`; Kendall `variant='b'`, `alternative='two-sided'`.
- **Layman.** Rank-correlation between predictions and ratings.
- **Specialist.** Library statistics; not a Textural Density metric.
- **Docs consulted:** SciPy `stats.spearmanr`, `stats.kendalltau`.

### L-005 — NumPy `log1p` / `log10` / `log2` / `sqrt` / `exp`

Used as **primitives** inside M-013, M-026–M-029, M-032–M-033, M-021. The **formulas** are project-defined; NumPy supplies the elementary functions (`numpy` 2.2.6). `np.log` / `np.log1p` are natural logs; `np.log10` common; `np.log2` binary.

### L-006 — NumPy `std` / `var` / `mean` / `median`

- Texture variability: `np.std(pitched)` — default `ddof=0` (numpy 2.2.6).
- Timbre density variance: `np.var(density_values)` — `ddof=0`.
- Time-series: `np.mean`, `np.median`, `np.var` in M-044.
- **Layman.** Ordinary average / spread of a list of numbers.
- **Specialist.** Population (divide by $n$), not sample ($n-1$), unless a caller sets `ddof`.

### L-007 — NumPy `quantile` / `choice` / `corrcoef` / `cumsum` / `searchsorted`

- Bootstrap (M-048): `default_rng(42).choice(..., replace=True)`, `np.quantile` (numpy 2.2.6 default interpolation `linear`).
- Placeholder IRR: `np.corrcoef`.
- Roll-off (M-034): `np.cumsum`, `np.searchsorted`.
- **Docs consulted:** NumPy 2.2.6 `numpy.quantile`, `numpy.random.Generator.choice`.

### L-008 — NumPy `nan_to_num` / `isfinite` masks

- [`spectral_analysis.py`](../spectral_analysis.py) `_safe_array` and finite masks. Behaviour: NaNs → 0.0 (default `nan=0.0`).
- **Layman.** Treat broken numbers as zero so the rest of the sum still runs.

### L-009 — pandas DataFrame (research plots)

- [`densidade_intervalar.py`](../densidade_intervalar.py) `analyze_consonance_vs_lambda` / `test_calibrated_model` construct `pd.DataFrame`. No production metric.
- **Package:** pandas 2.3.3. Tabular container only.

### L-010 — matplotlib plotting

- Visualization helpers in `densidade_intervalar.py`, `timbre_texture_analysis.py`, `plot_spectrogram.py`, `plot_metr_espectrais.py`. Geometry/DPI excluded except that they do not change numeric metrics.
- matplotlib 3.8.4.

### L-011 — scikit-learn / statsmodels / seaborn / openpyxl / mido

Declared dependencies. **Production `calculate_metrics` does not import them.**

- **mido:** MIDI file parsing in `midi_loader.py` (event times/notes — input construction, not a density formula).
- **openpyxl:** Excel importers under `tools/` (offline profile curation).
- **statsmodels / sklearn / seaborn:** used in `statistical_validation.py` and plotting/research modules if those files are run; they are **not** on the core pipeline. Classification: library operations in research files (see coverage). This audit does not reproduce sklearn/statsmodels estimator formulas.

---

## 6. Reference data and scientific claims

| Data | Path | Role |
|------|------|------|
| $\lambda$ | [`parameters/density_params.json`](../parameters/density_params.json) | Single float `0.05` for M-010 |
| Pitched CDM tables | `instrumentos/*.py` `spectral_data` | Note × dynamic floats; interpolated by M-016 |
| Unpitched CDM | `DYNAMIC_CDM` in percussion modules | Dynamic-only floats (M-017) |
| `CONSONANCE_RATINGS` | `densidade_intervalar.py` 40–47 | Calibration targets only (M-053) |
| Register bands | `config.DEFAULT_REGISTER_BANDS` vs three-band map in M-039 | Two different partitions |
| REF | `MAX_DENS_GLOBAL=193` | Composite divisor (M-026) |

**No formula is invented for tabulated CDM cells.** Provenance strings inside modules (Zenodo, Dynamics_predicter, NonTunPerc) are **repository claims**, not independently verified by this audit.

Written dynamics are symbolic markings. Instrument density applies **committed external amplitude metadata** to those markings. The project does not analyse waveforms at runtime (see root `README.md` scientific scope).

---

## 7. Ambiguities and implementation / documentation discrepancies

1. **`config.py` tail / GPR text vs live lookup.** **Clarified 2026-09-17:** comments and API now mark `DYN_TAIL_SHRINK` as offline/legacy; production raises if a dynamic is missing (M-056 vs M-016).
2. **`harmonic_ratio` name vs octave-class test.** **Terminology clarified 2026-09-17.** M-036 is not $kf_0$ harmonicity. Export key unchanged.
3. **Roll-off uses list order, not sorted frequency** (M-034). **Relabelled 2026-09-17** as `input_order_weight_quantile_hz`; `spectral_rolloff` kept as alias.
4. **`calculate_orchestration_balance(..., instruments)` ignores `instruments`.**
5. **Two register partitions** (5-band subindices vs 3-band orchestration).
6. **Two interval implementations** (distinct-bin M-012 vs event-level M-051 with optional 0.25-semitone patch and a vectorised shortcut).
7. **Two MIDI converters** (strict vs fallback-to-C4). **MusicXML transpose now uses written MIDI + strict conversion (2026-09-17).** Legacy `note_to_midi` remains on the event-level interval path.
8. **`visualize_decay_function` x-label says “semitones”** while $\delta$ is microtonal steps (`densidade_intervalar.py` ~599).
9. **`density.absolute` mixes $K$ (gate) with pitched event count (multiplier)** (M-028).
10. **`player_weighted_texture_mass` equals player count $Q$, not sonic mass $M$** (M-037).
11. **`dynamic_boost` is $\sqrt{M}$, not a dynamic marking factor** (M-026).
12. **Timbre “families” list is incomplete** relative to the instrument registry (M-038).
13. **Literature names in `CONSONANCE_RATINGS` comments** are not treated as verified citations of the stored numbers.
14. **`mean_pairwise_pearson`** is mean Pearson, not Krippendorff’s $\alpha$ (M-049). Alias retained.
15. **`INTERVAL_BLEND_NORMALISATION` / `unit_range`.** **Removed 2026-09-18** (M-024). Blend is the fixed-divisor combination only.
16. **Coarse-default $D$ (M-018) is not on the same scale** as table CDM.

Confirmed implementation facts above are separated from interpretation. This document does not claim that any index equals perceived density, loudness, or dissonance.

---

## 8. Coverage appendix

Classification of **tracked** first-party Python files (`git ls-files '*.py'`). `build/` copies are **not** inspected as sources.

### Mathematical implementation documented

`core/pipeline.py`, `core/pitch_structure.py`, `core/composite.py`, `core/quantity_scaling.py`, `core/source_aggregation.py`, `core/orchestration.py`, `core/orchestration_mass.py`, `core/pitch_aggregation.py`, `core/unpitched_routing.py`, `core/subindices.py`, `core/registral_density.py`, `core/event_density.py`, `core/temporal.py`, `core/sensitivity.py`, `core/pitch_range_validation.py`, `core/interval_compactness.py` (delegates to M-012), `densidade_intervalar.py`, `spectral_analysis.py`, `timbre_texture_analysis.py`, `microtonal.py`, `xml_loader.py` (transpose), `instrumentos/pitch_interpolation.py`, `instrumentos/spectral_lookup.py`, `instrumentos/coarse_default.py`, `instrumentos/mf_anchor_dynamic_extrapolation.py`, `instrumentos/bass_drum.py`, `instrumentos/cymbals.py`, `instrumentos/gong.py`, `instrumentos/tamtam.py`, `utils/optimization.py`, `validation/metrics.py`, `validation/rubric_scoring.py`, `config.py` (constants + unused tail comments), `parameters` JSON consumed by M-011.

Table-backed `instrumentos/{flute,piccolo,oboe,english_horn,clarinet,bass_clarinet,bassoon,contrabassoon,trumpet,horn,trombone,tuba,violin,viola,cello,double_bass}+technique modules`: **duplicate of M-016** (same `lookup_spectral_density` call). Documented as locations, not separate formulas.

### External-library operations documented

Sites listed in §5 (`PchipInterpolator`, `minimize`, `gaussian_kde`, `spearmanr`/`kendalltau`, NumPy elementary/stat functions, pandas/matplotlib research plots).

### Non-mathematical (inspected; no distinct scientific formula)

`core/__init__.py`, `core/version.py`, `core/defaults.py` (defaults only), `core/request.py`, `core/models.py`, `core/converters.py` (string assembly), `core/input_validation.py`, `core/formatting.py`, `core/export_constants.py`, `core/hash_utils.py`, `core/reporting.py` (text; pair ranking reuses M-010), `core/composite_trace.py`, `core/construct_metadata.py`, `core/metrics_metadata.py` (strings), `core/instrument_lookup_trace.py`, `core/unpitched_labels.py`, `adapters/*`, `gui/**`, `gui_components.py`, `gui_calibration.py`, `Main.py`, `run.py`, `run.bat` N/A, `error_handler.py`, `logging_config.py`, `data_processor.py`, `data_processor_legacy.py` (re-exports), `build_exe.py`, `parameters/__init__.py`, `score_io/*`, `utils/__init__.py`, `utils/notes.py` (spelling), `utils/plotting_style.py`, `utils/serialize_utils.py`, `instrumentos/__init__.py`, `instrumentos/registry.py`, `instrumentos/provenance.py`, `instrumentos/table_coverage.py`, `instrumentos/metadata_audit.py`, `instrumentos/metadata_range_audit.py`, `validation/__init__.py`, `validation/gui_validation.py`, `validation/report.py`, `validation/schemas.py`, `validation/score_schemas.py`, `validation/verification.py`.

### Duplicate / legacy / research documented elsewhere

`core/score_analysis.py` — orchestration of M-026 + M-043–M-044.  
`benchmarks/characterization/battery_cases.py`, `run_battery.py` — case lists calling `calculate_metrics` (no new production formula).  
`run_stress_battery.py`, `tests/stress/*` — public-API stress, no new core formula.  
`replication/scripts/*` — compare/reproduce frozen outputs.  
`tools/*` — offline generation/audits; GPR/PCHIP table builders reuse L-001 / M-054 / M-056 history. `tools/legacy_gpr_dynamic_interpolation.py` holds the removed runtime model (see M-056).  
`calibration.py`, `gui_calibration.py` — UI around $\lambda$ / M-053.  
`scientific_report_generator.py` — reporting.  
`plot_spectrogram.py`, `plot_metr_espectrais.py` — plots.  
`statistical_validation.py` — research stats (sklearn/statsmodels); not re-derived (L-011).  
`validation/scripts/*`, `validation/synthetic_cases.py` — fixtures / IRR wrappers.  
`midi_loader.py` — MIDI I/O (mido).  
`tests/**` — assertions and fixtures; test-only generators that only call production APIs are not given new `M-` IDs. Plausibility helpers construct slices, not new metrics.

### Not inspected as mathematics (reason)

- `build/lib/**` — generated copies of the same tree.  
- Untracked `reports/**` — outputs, not source.  
- Binary/PDF manuals — archival; `.md` + code are canonical (`docs/VERSIONING.md`).  
- Every individual `spectral_data` numeric cell — tabulated reference data, not a derived formula (hashes of the `.py` files are still in §9).

**Coverage claim:** all tracked first-party `.py` files were classified. Distinct production formulas are assigned `M-`/`L-` IDs. Offline tool internals (full GPR fitting, Excel importers, dest-Zenodo sheet math) are **summarised**, not expanded cell-by-cell; that is an intentional remaining gap for generator scripts under `tools/`.

---

## 9. Source-file hashes

SHA-256 of documented **tracked** source files (working tree bytes). This generated document is excluded. Computed after the text above was drafted; see the hash block at the end of this file (filled by the audit script).

---

## 10. References actually consulted

- Working-tree source files cited per entry.
- [`README.md`](../README.md), [`docs/VERSIONING.md`](VERSIONING.md), [`docs/CONTRIBUTING.md`](../CONTRIBUTING.md), [`config.py`](../config.py) comments, [`CHANGES.md`](../CHANGES.md) (REF=193 provenance comment).
- [`docs/MATHEMATICAL_MANUAL.md`](MATHEMATICAL_MANUAL.md) — **orientation only**; equations in *this* file follow the code when they disagree.
- Installed package versions listed in §1.
- SciPy 1.13.1 docs for `PchipInterpolator`, `minimize`, `gaussian_kde`, `spearmanr`, `kendalltau`.
- NumPy 2.2.6 docs for `quantile`, `std`/`var` defaults, `log1p`/`log10`/`log2`.

No StackEdit upload was performed. Local Markdown/LaTeX delimiters were checked for balance in the editor, not in stackedit.io.

---

## 11. Verification performed

- Discovery: full `git ls-files '*.py'` plus caller trace from `calculate_metrics` / `analyze_score`.
- 2026-09-17 semantics/MusicXML patch: focused tests plus `pytest tests --ignore=tests/plausibility` (1709 passed, 8 skipped). Existing research outputs were not regenerated.
- Isolated numerical spot checks (outside the repo; not a corpus run):
  - M-003: $f(69)=440$.
  - M-005: $\mathrm{Cb}5$ written $=71$; concert $=69$ after chromatic $-2$.
  - M-034: reviewed order-sensitive sequences unchanged; alias equals canonical key.
  - M-036: C4+G4 $=0.5$, C4+C5 $=1.0$ at equal weights.

Hash appendix follows.

### SHA-256 inventory (tracked sources used by this audit)

| Path | Bytes | SHA-256 |
|------|------:|---------|
| Main.py | 20436 | 1d15cff798e85b43b43a478e963b8d333283ed36d38ee0db57459dd8be0b0877 |
| adapters/__init__.py | 335 | fecc9a31c9be8f7995ebabc6b555c204405b3962ec41a698934a6233746fb85a |
| adapters/gui_adapter.py | 2549 | 0779e12d6d5f20b8ebe62ba885404d93935d149983fcb406ce186285f29d908f |
| adapters/legacy_input.py | 770 | f4d763fbb1d5c71b79cfd82c4184790e1589f9356961126395ab9dcd1ac67de3 |
| benchmarks/__init__.py | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| benchmarks/characterization/battery_cases.py | 29228 | eb80e622eab3b92c880158394f794affb1847d109fcaf11372e6022b288ce3bf |
| benchmarks/characterization/run_battery.py | 32814 | 97651e8afc4e92f1f5c5b25352b4f3e866b2275a550f69caac1445c9f297268f |
| benchmarks/scripts/freeze_outputs.py | 857 | 52b6b75bc49979dc164a0cdc86bca75643c4199e6128842cb327f9325503ec61 |
| benchmarks/scripts/run_benchmarks.py | 2279 | 9abf86183bb15f3fba1622992a4c81336d1e928fa15d90ed088fe76d63a41ddf |
| build_exe.py | 802 | aa8e84adfcd341181f9ea773c42bf91c5f1e229c37e7d2b4857fb41a0314daf1 |
| calibration.py | 8789 | 45315cdbb1f46302910ec767e86c6b1216ddcffef5c5b824faa010803f918db3 |
| config.py | 9828 | a2f7b4c2db5cb8eb4b2bd1e8ebadb6232316bcbbf778ab8fbdd43957ff74d4c9 |
| core/__init__.py | 2625 | 777ddeb3cec0a3785f17a9d72e6da9ec49cf0de82b1d8842da2fd0451e240cfd |
| core/composite.py | 8803 | a10cc4558a1724bb3da14050561605c1e7c587d0d8ff0903b22f49200e8b4d6a |
| core/composite_trace.py | 3092 | 47e2864ffe502ba0fe0c0e37369e3d649802fc6bddb317172812b0af0d70cab2 |
| core/construct_metadata.py | 4363 | 90515c559beadf9bf8d07742ee9b3db312fccc85e424c764d7d91f2ef802955f |
| core/converters.py | 7358 | cdd28243b058b0506124492a5c883522634c2acfeac9ebc373a1d3346e218fd9 |
| core/defaults.py | 902 | 713c7ce5fa6df7c7397c5fff3d30c20aeb42a6948e6ece56eea3c994bc487b6f |
| core/event_density.py | 1638 | ed0eabf0ad3ee180bcf8e2912d534445e5caaedd9c8394be197852cfa8bfc823 |
| core/export_constants.py | 2892 | ee7ba2d383e406eb7005f76c689b8ec5e23d7ec3d43deed23830e82b2e665d8f |
| core/formatting.py | 6533 | 8a57b403a3a1a1fbfd2254354a49a2fd053e38b1837563c02e2d180dc274dad2 |
| core/hash_utils.py | 1554 | f9bc232418eddc3bbe95a3575786e93defe08d2d680f709f31b3d4f0823ce236 |
| core/input_validation.py | 4462 | eabbed719a1e13ab37d5fc33bec1bbfa0b0e55ed69ec601c8b073d860f11bc7c |
| core/instrument_lookup_trace.py | 1164 | 7d6008eff16e507cb73047bcccd408f2e9f74a6a6dd9c037f9deffa269a5d314 |
| core/interval_compactness.py | 1595 | 898f8c0a4a0360252c5f3e64fdf51c18465d2ed24d04cd86076691b7a2e681ad |
| core/metrics_metadata.py | 20032 | 0613ad53727dfcdf01e31931d26deeaab63facadafca51f0ca6dbe04b2bf469c |
| core/models.py | 5065 | 838833779fb796d7c18654a85d3e3bfdefd69006bfb954e1446727988737f516 |
| core/orchestration.py | 4902 | 325e97ea2fcfd03e8121abf3c212d194a3fb1ec6c2b9eaa222b7118177e2011d |
| core/orchestration_mass.py | 3580 | 76fc38adaf6fe6b2d9d0a787671ae1da085218a83ed434ee34d289e7172da4ff |
| core/pipeline.py | 15278 | 2955135e5c57605e8c6e1af48fe17cb420dd716382e0f3656d4b7da7c772599f |
| core/pitch_aggregation.py | 7730 | 64b640747c954c395ae560988d84548f75c96378e4fd85196c98eb519aa8ff56 |
| core/pitch_range_validation.py | 2799 | 2d063f8c0718ef12a5b2cc94917f72e59f280a9710baaba55df8d62d5f362730 |
| core/pitch_structure.py | 4933 | 35e8de67a518a87a913a034c3577e4dc1e3e023a9a62085beb76925c276d9095 |
| core/quantity_scaling.py | 3569 | 13484a4b51ff313058fe89abfa2e38d0550278065c0e0e4c0b539e500ed45465 |
| core/registral_density.py | 3051 | 05db966339c4e519da1738084baddd6ef23d01960968a09201b1aa6ea969fc7e |
| core/reporting.py | 14835 | e4b088836bdcc8ab8d9d924cc806db24a88f65c4a82f6b9562c1ce2545d7f805 |
| core/request.py | 4078 | 1abff5f9f559c027f480600e7518626e52007e31c05deb503cfd586e63672dc9 |
| core/score_analysis.py | 10197 | b96b1fe3938079c4e95352a751cd07121930d325db3aa32bba86a18ea688787b |
| core/sensitivity.py | 7126 | 939fa95a4966836c1cad07eeba758e3770f56d409ac5d3971c4f9d9dd9a6dfe7 |
| core/source_aggregation.py | 3985 | 35ea2bd1c1121246a6edf32a36b1ac983976492d669eacff20eab80c8bfa5219 |
| core/subindices.py | 12834 | 2588369bcb45c8eb3296cb4dd4998b9fae1c3be663bf4d632da3bcfaa237ad70 |
| core/temporal.py | 6325 | 8adf05825e6e3511912b24a8786608a1f00783e3be8587efd03a05a298963db6 |
| core/unpitched_labels.py | 637 | 1fd6df8af721ed29c1106f2fecfb78e07131380ba43a6aed325eebbcbc9276f0 |
| core/unpitched_routing.py | 6204 | 735222cb9db9e38df41a680b9563da7a43b09dd9525d07d41617361ef7adcbd7 |
| core/version.py | 745 | 59991ff6054844bc5d8a7acce684d86998a70db0f29231402969aaf5551c9f41 |
| data_processor.py | 1187 | 65e20613ddb6ae5e768195ba28ce34fdb58a7ec544c1b7f308fc293c9551a16d |
| data_processor_legacy.py | 3893 | 81d63e0d91011a267be9f9ce9b9ad7cba76aa6314f245a96c9ced837ec1efe5e |
| densidade_intervalar.py | 22951 | eca085156a9bdf8b1c13da09e421abc9a616a43ec8729624aeb31ce38f1b89c6 |
| error_handler.py | 10276 | a3403a5f5c6eca9ddebd404b4dd08df599b0c22080c13cb13a45e4a4648a80e4 |
| gui/__init__.py | 389 | dbb9a364a9d5d30b2d1b0550561b73acac4175714ec06303bd550943990cc5df |
| gui/analysis_adapter.py | 584 | 346b53fbc449e9a437fe6958016d4035eee8e427b1d6921aa5784a9e30f1861f |
| gui/app.py | 4977 | 552c8f023a802bd301b264d35ef45989e6517433683bb893177e30fbf03b3fe6 |
| gui/calibration_window.py | 8283 | a044985da4639e763c82871a561f3079e9c90b0cedcc0d46261bb221fedde602 |
| gui/controllers/__init__.py | 188 | 7e470f5c61e493a4fdc0aacb6fa2edd52e0647c166090573d44d0c391a032bc7 |
| gui/controllers/analysis_controller.py | 1076 | 9abee4d9a799c3221965a61e15d9a6641327593b196f9b3c0c707d31e54424f0 |
| gui/file_io.py | 716 | 5ac62462ff75823ebab513bd3d5c6c86f3af3c216628dbabf79d9c29b520e4e1 |
| gui/state.py | 2364 | 34f002a6a39210d2502baed7e42d4d611689c4bff43348768a7c5693b1b4d2c5 |
| gui/types.py | 836 | da2543fac4e49f3717519689c480d378f19b91b27f611bff0b9c6c86a99c047b |
| gui/widgets/__init__.py | 342 | 08368e260c54d1be2706e4cc8fcd7c2e904c2bf588fe59d56c215cb3aa43d7b4 |
| gui/widgets/action_bar.py | 1084 | 62d7baa3c27161d9ab323ddd0d87d5594843d39d8da4f7d3dc8406024973f522 |
| gui/widgets/input_panel.py | 14088 | 3fdaf5e27308f479948c9995dc0e59f084ca51c5c73b95c005bba9dd23c8ac69 |
| gui/widgets/report_panel.py | 5403 | cab13cb1b47d1f778023795664a5180a6b7dd282fed23d84f9345643fb1e1131 |
| gui/widgets/results_panel.py | 10482 | a40f4ce55b7bb429a338dbf9ef0911d85e286b5ecb8e4b81e1784dc646ea2417 |
| gui_calibration.py | 18399 | a27accaf8023a8a7f504b88ee75c3b459c58ce2362f7ad070287adda4af0c39e |
| gui_components.py | 385 | a7391f5da6e06ea5a4e0272f0e20689c4c3a6dbc9c2bb3b35f99f85fc80f9590 |
| instrumentos/__init__.py | 3483 | de73d120fd30f2925d24b8e3cf3139dc69d051933117b5ce08338a12c8d056fd |
| instrumentos/bass_clarinet.py | 11127 | 35dbe8f7b26e6fea36fd15b04eb81f16741ed0d0d81da6d2cdeab322f6db821b |
| instrumentos/bass_drum.py | 4184 | 1db3412e3e0716a6977ca9ae33fbecefbdf8728766cf6d458005908baac17219 |
| instrumentos/bassoon.py | 10289 | 8698b66462a964edce058879d10fd9e910f8047f1bf7547d142a3f6d794ddde8 |
| instrumentos/cello.py | 11458 | 3475fa8f05dd6b44d2e3162e42509189cb54a982bd2fb61c51c5d5fa6af6ed6a |
| instrumentos/cello_harmonics.py | 7026 | c87e3d43f18560c99d66258150007bd1f3f0efaee6dbeb9ca03178e9b32fc43e |
| instrumentos/cello_sordina.py | 10947 | 53cb746de8e67b14cf5bd49a08e8f2374580c6c9ac7cb7f18000bba94048ba9c |
| instrumentos/cello_sul_ponticello.py | 10995 | ba57ca9d1d5989076258f535209efbdc4ba18eae31885a36349919641a4a4df5 |
| instrumentos/clarinet.py | 11251 | d8081f27e001c2c8d57d70457c5bd62258bd70aea3669dcf71087afe3e629223 |
| instrumentos/coarse_default.py | 2304 | ce4b23531f874066237a6406236d2463bb03656482332c992494b6c4eae72cf2 |
| instrumentos/contrabassoon.py | 10319 | 7ccd215c0eac09178b24559359e0b12cfcbc5188fb13757ccc335bbf3c3e8fa7 |
| instrumentos/cymbals.py | 4202 | 6d03167bde4b5f83a23309074635ec42288e628b923dd4f8d577197d552ca087 |
| instrumentos/double_bass.py | 10756 | a3143fb7c75220764534dfa9cfa505c93bd62151d095ce4f4edd2cab9f1a4874 |
| instrumentos/double_bass_harmonics.py | 9812 | 0a26461d8ea8e51cbd0fbc4374504a9bccfbd8af1122e8c9334387453bae47f5 |
| instrumentos/double_bass_sordina.py | 9875 | 6c34cfcb54d2b83fbe41ca9430957be034ea2873453298499f58fd8c9273ee2a |
| instrumentos/double_bass_sul_ponticello.py | 9920 | a1be7824e85339f6afd034a42d4d810f286f648b45e4e6899f45534ac7847568 |
| instrumentos/english_horn.py | 8944 | cebf293098f0ae3755076fe0f46a58d04923695f01b26aa8dc1d43d2440fd598 |
| instrumentos/flute.py | 9875 | e426b8c9f3a6e6fedec0156b08dcc3fdd565e67af01cb74a73156c7f377dc6c5 |
| instrumentos/gong.py | 4294 | 55acaaed0cac64d8a38eea3646b99bcee06e01c0c9d30d9b33702ad5d184c0ef |
| instrumentos/horn.py | 10637 | cfc8a9c022d111c92d46d32e92bc7ff1ac908a676b15e38c77530d4d4a34a4ba |
| instrumentos/metadata_audit.py | 3264 | cd5e55473b640cf51bc6aeaec922e004adf2b693a51ade060192cb2e9b14183c |
| instrumentos/metadata_range_audit.py | 14349 | aabca3c00c3a98d3912160c6148e59ada07be6f33896700a7c5a9de90db16b7b |
| instrumentos/mf_anchor_dynamic_extrapolation.py | 1946 | 209001b89df1b3db69a2852295f354d83112bc9d1439ee9d0979cd10b21cdda2 |
| instrumentos/oboe.py | 9090 | 42f8c760fbf3ca54099e32f209c00acbef67ceacba58173ad63d03fff4446f45 |
| instrumentos/piccolo.py | 9871 | ae6ef295b2ea26fb2f339281ab68ebe1c7f9bddc529fbcd28e0f19222cc11761 |
| instrumentos/pitch_interpolation.py | 20325 | 8ca131f4def04f3e74bfb1c80ca7b52c4000e8122b803484b26cf5b8b5390681 |
| instrumentos/provenance.py | 802 | 1596952fdebccf5b4da2def0fbda39687ff9f14f79da993501b01be6c9767637 |
| instrumentos/registry.py | 48880 | fd3bae8c58f17089549ebfca9329932542f14272cbacc93edc5632bea7c27b49 |
| instrumentos/spectral_lookup.py | 2486 | 0ec9b5bb8f0f36e9ee35fcb3958d14f86dfe65d01ce225c9ee4d3c2a1825db87 |
| instrumentos/table_coverage.py | 3520 | b6c2707838e7c29da19d24f7ed22efafcf6f8c7f57a135a9e03257b7b80ea606 |
| instrumentos/tamtam.py | 4249 | 96d888245327fedaaf0da1b0c903b5a6527429aa82da5e52cd6835a98a75fb9e |
| instrumentos/trombone.py | 10679 | 30573fc11ab5266286a2d20c5b287bb8e267f94c6e91a2012955777048c0e2d1 |
| instrumentos/trumpet.py | 9101 | 88521aedd7482d235f5678ccc58a30c5fc8ce648376921969c173ce2aa9f4822 |
| instrumentos/tuba.py | 11242 | e906a353762db31b3bbcabe128a5bba1130da43cd1bfbaa468ed563cba7f7314 |
| instrumentos/viola.py | 11040 | 51bfd9af1cd2b2d9ec4eadf6df6ff87cc7313d10bc5ffe68d44a9f1e8404ed5b |
| instrumentos/viola_harmonics.py | 6598 | f9278495a152e6b03c0b19312d9e15f5dd1fcc32e515fc9ea2615d3b7517bd3d |
| instrumentos/viola_sordina.py | 11072 | 2704ea7469d4d29efcedcb188db45bba1aa71800f849e97e1deb54cf0460729b |
| instrumentos/viola_sul_ponticello.py | 10055 | 9f0498b5b2ad8b67a4e079df1bdab9122bbd2dd5d313adadcff5f1b6e173f0ce |
| instrumentos/violin.py | 12067 | d97de9ccf20d6db0c80253aadf0f771e0cbdb0a1f9eef176e75904357d891a22 |
| instrumentos/violin_harmonics.py | 7597 | fbc171c5c4edcf7beaac252a2b0bc6b413cca7c0d857973e77cddf297d5fab4e |
| instrumentos/violin_sordina.py | 10170 | 91668294f03bf7cb612e4fb09c0b2ad9f54172af441ef6d474be7cf0afc94c04 |
| instrumentos/violin_sordina_diagnostics.py | 8718 | 290f4102442e8c350bcfb2fda27f6a826aabb5322dd846d34acc5b4aeb039bc5 |
| instrumentos/violin_sul_ponticello.py | 10249 | 3047e0744bb82d00a754a1a5ad26f02ca78ba8bd3643c629f14454291ca70047 |
| instrumentos/violin_sul_tasto.py | 12078 | d0fe2ab6b961a7ce1cb31620b56959c9cc21dbbaf1bce4382a1d641d058c4727 |
| logging_config.py | 176 | c94daa6e974610f283836c94ce60c2718546614ae4285b13c4ab0a1ef7eb6979 |
| microtonal.py | 33708 | 51bdd7bc6489c368f8ad474d0a6a725d91ca65f7f6ef89b06c1f98be6e520f75 |
| midi_loader.py | 8951 | 3846d6b53fddafcd06fde1192b5807629bcd13c8ec010f93829a40a4a8c4ca9d |
| parameters/__init__.py | 71 | 237e7c7bf57c0cf5537340634e02dd9463245d3fd1dd72449a3fda604a453dda |
| parameters/density_params.json | 24 | 151a6eae5a49f309ca922ac27773edcb0626e95a0b135dca342eaafcff9658b7 |
| plot_metr_espectrais.py | 14977 | fadabf101f99e312fbe25df3c3622f20a0ef9f368fb304392911a6eba581c01f |
| plot_spectrogram.py | 8587 | 57db50c9049e260a2f775fcfc98370c30bc12fb1534745df8da9aceac9f8db84 |
| pyproject.toml | 2681 | f1874ba2f3bbe5601ebc2a9e95f73839377d92b04bb2e781ef85fb48f86b2886 |
| replication/scripts/compare_to_frozen_outputs.py | 3936 | a6499ac972f747e55f232a1a59fd5b040ce9955a7779dcc5f4effd33e55e9772 |
| replication/scripts/reproduce_metrics.py | 6403 | b4bfe5ca239636df461c75b0842047f5280748b95f220695b851a2fa83359e59 |
| replication/scripts/reproduce_tables.py | 3859 | 450b2dd248c377f1930b06f37b15a96834d413c06d95ca9046707f702925b253 |
| replication/scripts/scan_benchmark_intake.py | 3431 | 36bd4d7f101eba87c2ffe1bd6a6de98b5246d6e10ff85f5aa97397f33ea65494 |
| requirements.txt | 488 | acc51991c321d72a4c88b5a4ae0e897b95f46cd6e09e3570717e472d80f85d73 |
| run.py | 1498 | 014915a35bbc3d92d746b24cc788e307468774e9d9e81a7181d3ba698512f6bc |
| run_stress_battery.py | 6843 | 0b1033e570599f3fab0362fb9654f3aab231f33ed77ae756c64bcff03d6e77ec |
| scientific_report_generator.py | 36967 | 2e20d6b947409390ce2e852139cb1a872f06b3788488460a8b879882e7b9819a |
| score_io/__init__.py | 206 | cc8c1dac6922d0f500318d004c54bdbb00b9dbf8f5eae54a23511376a96508b8 |
| score_io/exporters.py | 2433 | 5eca3ee30f284d912e11e97fafa593a6c88b0d85b99621c56987adfbc09f44fb |
| scripts/export_constants_assumptions.py | 591 | 4e2fe139be463e9d2c835d633097a67e3d01082098bfabdf71191883c9c70eda |
| scripts/export_instrument_metadata_audit.py | 734 | ce9c332e3d57955efc9898091b81fbfecedf62817957bb8bc548e3577d34c96b |
| spectral_analysis.py | 14146 | a9c1fe9bc78c9db1a785a1d712086ff3e2bb83ce6c7ded80404b0b9e40dfefa2 |
| statistical_validation.py | 18480 | 46e741e3f20cd31a47d4fd3b4aec0c6879cecfad37e963252739e4d97863c21f |
| tests/__init__.py | 425 | 55197c4599abc95605ada99c76bbe603fb4b1c326f9a1b9ba8bd0fc6df1707e2 |
| tests/conftest.py | 1903 | f8bcff0eb8e811d65614e8b78da0602e44be9b3dc7249cc19379b76ef8c1db5f |
| tests/instrument_register_audit.py | 4972 | b1a8d5d3d1b44bb50c3da4483a77ee5df6e2213303b7ef1b2f84d07f79be2dac |
| tests/plausibility/__init__.py | 78 | 0df6029151cf6927cbcc9736a10a77d6b31c0f2716a5394aa313abbfb00a0eb8 |
| tests/plausibility/conftest.py | 2177 | 009c1a30bfc3f08aba262cb669a8ba7d2b81fad5ee97660382e8073e6f900e7f |
| tests/plausibility/helpers.py | 5738 | c18900d4066afb0f119e3c65a82a825dc65d45887e53effaa59676ed5cb2c128 |
| tests/plausibility/test_fa_pitch_grammar.py | 5529 | c66687a69fd08e3bdf31f7ba3e8f58a8ed1be9f6bdd6ca1b44693d32d7db501b |
| tests/plausibility/test_fb_interval_density.py | 9566 | 491f111ad2dc51d6ccc6ddfc4ebe73729969728c0f35172ac04aeb7dbddba75b |
| tests/plausibility/test_fc_instrument_ladders.py | 19639 | 0f628922f84414e2e3aa121b66a56293500cc233ae76930cdadfeeff3d05640b |
| tests/plausibility/test_fd_quantity_mass.py | 6061 | 441bf3c58c0704c8804cda700ba8788b0fdc7fb30a24481b614b4b0295d98278 |
| tests/plausibility/test_fe_blend_composite.py | 10232 | 415b061979653daa1150b9575f1579c5250073b62670514b2cc23d00e2eda2f7 |
| tests/plausibility/test_ff_absolute_density.py | 3577 | 1eac9baa1cb5a7479aa39d45e276d9f64bf86955b822744a4395b214fa6839b0 |
| tests/plausibility/test_fg_spectral.py | 5400 | c0bcd6c0dd2c69f6f3c9cfc80a52b5281adcad8c14dfab80793da0ce1379b00d |
| tests/plausibility/test_fh_registral_texture.py | 5482 | 8344e02830d7669c0fd35038ea4f66c167b4ec307ce12c87923613a6af1d8e12 |
| tests/plausibility/test_fi_temporal_score.py | 7550 | 3381683922ab1dd984ca0ea9a00b9eccafdbfd91090d94d5033cd9c0ae29f48e |
| tests/plausibility/test_fj_repertoire.py | 7225 | 4f32e00e6ace08bbf30e6e3aa58c754274f0af24dce8d64906bd623c06dbcc55 |
| tests/plausibility/test_fk_robustness.py | 3788 | bb05e1830d04e2bee73753d5a40d0f5414a321b6d26802be757c75c0fffaf2a8 |
| tests/snapshot_utils.py | 2355 | 1ca9e67041f929d8f56acbbbbaa208d362b51dfab3192b3c6b6b61081388573f |
| tests/stress/__init__.py | 203 | 91138835a45824e92875f768a948024c80a5f58259365b9c5cccb270c688c810 |
| tests/stress/engine.py | 28684 | 73cf979188219fa5e7e0b12b159af984ad782d8e5ad1e4a263b692fe3fb8ff29 |
| tests/stress/figures.py | 4366 | d0a39efbd8f8dd9f7d58a95699eaa297706372302d943b0d8b73567eefb5f29f |
| tests/stress/registry_check.py | 659 | 21ebdd9ba8fd99c097a5f8ca7e0e17e3ecef8fabada97158c43a1e79df6abc79 |
| tests/stress/report.py | 11809 | 77693930e3928d00aba5994101dd49f19ac0dd489b6add76fd1418c522b4fc0c |
| tests/stress/scenarios.py | 12484 | 6ca35a950ebd1d898351adf3e21dd56d11061a630b0939c21ab9e3dc62755a94 |
| tests/string_constants.py | 2192 | 4daf5809f5733cc9d74e6daa6da9f905d891179b7798efbf849fbd8d529f9fa1 |
| tests/test_analysis_controller.py | 1715 | 900a0203151215f65f09bbe9524b1a67c165c3fc3051a7388b34d4dc3408ebb0 |
| tests/test_analysis_request.py | 2292 | 6955ff2d980880d21653ea78dfb6754bc2ce5cc1c9cb5c01b1e5272c4a2c1858 |
| tests/test_benchmark_corpus.py | 2000 | c141abb029ef5a2818632f853342d284c387d6ebc69d675a54cd7d28cd66d047 |
| tests/test_benchmark_manifest.py | 2686 | 842bc64170832d402a98a0da35d292bcadfb9acf0bb0e1ef62276d94bc43ca39 |
| tests/test_blend_scale_snapshot.py | 919 | 2d276ac4b829ff94b2f79c970891a046c519947d6a18c03d24c937cc3ba75712 |
| tests/test_cello_technique_modules.py | 4906 | df538d174a94a0a7cc4266f7349c040a41ac0983513b307f79fde09b66eb0380 |
| tests/test_composite_from_blend_delegation.py | 771 | 8ea065d119ec7355a83ab2cecdd1cac33ed9e43779d44363b16e0e1aeb6b11b0 |
| tests/test_composite_unification_acceptance.py | 8617 | 3404abd04d3ff7467be2c42e40762358c549c641c95321fc0efe21060a472c75 |
| tests/test_construct_metadata.py | 3419 | bf780ec7e5d9e066948d1f6734e0224444426685c2116384f1d5999bfa64b1cb |
| tests/test_core_extraction.py | 2773 | bf18d5e1159dcf81a0297f18e8ecac633cf9fff28402f6f1cfce824033c44e25 |
| tests/test_core_gui_separation.py | 5592 | f73f30a087bf3ee42c9a58e16e75831fe37cf0bb898b4bd12f888a2bead855d0 |
| tests/test_core_models.py | 8011 | 5ed7c27efbf58842c3c4f02d6c47773084d4aa6a538b1f092be77a77f810b107 |
| tests/test_data_processor.py | 7129 | 0ce065d3c69d2af7cbe0acd7baffcec7a0ab3a51cf4688233f0e5e18b92c45f5 |
| tests/test_dbass_technique_modules.py | 5064 | 543f3bc7b77588aea844c5dbf6432b4aa9e8e5a5d715e086dcd94492774336bb |
| tests/test_densidade_intervalar.py | 3329 | 7475e24d48c7acd586f544176c5928fc8708060e5f4975b3eb168cbf32c2d778 |
| tests/test_densidade_intervalar_contract_additional.py | 8969 | ee1b918a4ffe2b594eb1f180d3adfb3b479a49b3c547d9e6767785a9a35c5938 |
| tests/test_dynamic_interpolation_contracts.py | 6357 | 88e5164e6f5d5f7e2b9551f03ed0277ba2502149dda9213b45d90e4427a9a6a8 |
| tests/test_dynamic_interpolation_method_comparison.py | 5384 | ee6332f6b47c720a60eeef12b3ea6557c10b48c327f9761975590ce240fb12d9 |
| tests/test_event_density.py | 708 | dd6037a11746b88a5c194f9c94f8057911c13c99b3ab84acaed6f98d7e35022b |
| tests/test_export_and_sensitivity.py | 2803 | 60c93303a6d383469de48e961cebdf622d3cab21557bde617db97ed24151d976 |
| tests/test_extensive_density_monotonic.py | 3873 | aec50cd04c3e0c68ee409d223241a0368f801af8cd8ea4b4a008a9f7f60c91b8 |
| tests/test_formal_construct_axioms.py | 11472 | 939e9639f5fec7d3a3ede1eeec941834eca21430ac410c88bd82a08cd1cf3507 |
| tests/test_gpr_model_quality_audit.py | 4700 | e2e037e3ec9ec1162c4d5cf55c1fe00faf84ee0311bef77ed9e93bbb38a2e2ac |
| tests/test_gui_alignment.py | 5479 | d7ec1194fb4936c536272fcf7ec0d9c5ecdb547c89e2f0cd3866d494a189d6f5 |
| tests/test_gui_architecture.py | 9000 | 9cbe47f96518b86e66713fbc02a5969c02e62c2dc2ac2063e9ebe241ad6a49fc |
| tests/test_harmonic_ratio_octave_class.py | 1491 | 2ea6f5f919344d955509719643000065ebc225bc9058471229360bd8b7a9c4c3 |
| tests/test_instrument_alias_registers.py | 1707 | 5a4f86a65c9c0c8306da6ddfee50a0eabdd12b6bf5a5189c86bad68062f23df9 |
| tests/test_instrument_density_registry_scaffold_contract_additional.py | 13213 | 057ef2dcd1e275679b5484587ab3b060bc41259b2dd84856c88909ed23474592 |
| tests/test_instrument_metadata_audit.py | 2133 | 10629054bb8def38351a179762bc394d0fe96a6d5d5fd403cd3e111796c98dc9 |
| tests/test_instrument_metadata_range_contracts.py | 5656 | d41c9d49a680771a21e7e20e046b9103c6b94af56619f4de6ab41c65f2c40f87 |
| tests/test_instrument_profile_excel_importer_additional.py | 14582 | c62979b68b1a488f3f445389c94ff85cd9c68f7920accbd34f453d89ea7abd7c |
| tests/test_instrument_provenance.py | 1003 | 908b0f5d3ae0dcf865a9c03754fd354430afc39f276256fb7c6b6cd3a2cebb4d |
| tests/test_instrument_register_contracts.py | 7577 | 7a485fc0d3b09f7a6ad548ddb5a727f5d31338f2e5386abde688e8fb0f6ed453 |
| tests/test_instrument_registry.py | 5057 | 583b1189217f2bfcfbca2a186af9e28eb1cf0efa36c6d60b465de179cef5860d |
| tests/test_instrument_technique_metadata_contracts.py | 3216 | f8731fc82464c3e7f410f263ee429c950c78a2e5137a8db8d6d312ffde373929 |
| tests/test_instrument_transposition_contracts.py | 4173 | 24ea9e1072292cb429aa742df3f916d1222255272e3926f0870f2a1ce7fe4111 |
| tests/test_integration.py | 5771 | 271a26942565dda0c379a76e9833084bb45332a893c382cb131bd358effe3105 |
| tests/test_interval_blend_normalisation.py | 4869 | e3d8bee4968543c703a09b2a3bca17dc914669a26b220bc10b5ecbee9bfd4283 |
| tests/test_interval_density_bound.py | 1678 | 1248e8d17624526bbfb683d472608b04bf0e1cce105fdbfb6fa30fa3f967ab77 |
| tests/test_log_compression_asymmetry.py | 1944 | 48aa7ff9b7a72d2e812c51a94ab945ae8178b7042e40028c7d22a55ad64b8cef |
| tests/test_metric_metadata.py | 5847 | 0e2b079ac55d73d16881e7b5334628fbb2ce7e3cc0fbfa77b09aa5f67c8c3b43 |
| tests/test_microtonal_harmonic_ratio_fixture.py | 1474 | b7568057b22f94d15d5a4e763216cecf8ae4d82bbe93a780e88baac8472bfa2f |
| tests/test_microtonal_strict.py | 8834 | aac1d0f64b950591d36339ef7c4200f6088bf52339396bd744980052974a5634 |
| tests/test_musicxml_transposing_instruments.py | 5162 | c3d5693ad9f0a9f6270a0be71c68948668075584a8c5d1b4451c3cf277bb6757 |
| tests/test_near_unison_semantics.py | 3206 | 52c8f9b52ac78b5c173cf167baa34db300a331fa98fd498deeb491b984de2b8d |
| tests/test_notes.py | 4580 | ead7b478535658052c63ffecd18746770ab79c3578584a153e9ad6df5c5dbf1e |
| tests/test_optimization.py | 6719 | 12a824ea715557a5590cf0c1d115b86f0af8646d72f127b8466243f736c7cccc |
| tests/test_percussion_nontunperc_modules.py | 4856 | ea453cae6072229e2692d8f3c399308719c5e8691a4d9078dc59d51491075db9 |
| tests/test_pitch_aggregation.py | 1217 | 0a54a6ce8d16f91091a35ecd77397720843687f1198cb70f84ff5b1719fb2449 |
| tests/test_pitch_interpolation.py | 10167 | 936726f57345468879e4bbb0befb97891cfe3cd6a23cf25b523a15f78baaa49b |
| tests/test_pitched_dynamic_monotone_ladders.py | 5786 | ec1714df9d499de3aedaa26464f8b6c72a80e4877ebf8143026c6353f2bc17f3 |
| tests/test_quality_gates.py | 7447 | c441ca8e9b3a8c5f153d4717649b36e55c0ed31c8237d13317988c8aee6f5947 |
| tests/test_quantity_scaling.py | 8047 | 0b2db5aecc667c9fcfe65e46cadcd018476f260e48fe8cd051450bc44a8221e2 |
| tests/test_regression_baseline.py | 11197 | 7bb030a31d25987adea77420863476d63d543fc1b0fea5f8e42ac93954a109cc |
| tests/test_removed_perceptual_options.py | 5005 | 5710457b582284f7c3410c41af3e227d79fdc67acace5d522f1a16ae336a3ee2 |
| tests/test_replication.py | 2778 | ad7e790eefb7281b53cb68a89416f0475040f02937961883cc8ebbb8c6670c58 |
| tests/test_reporting.py | 3721 | 6f58eae859ca5b76e041676edaedcb0a4acafbb478773964cb090da0f6c4aaee |
| tests/test_rubric_scoring.py | 8092 | 69ea96e2c0ed4373d562a84b6cfbdb80e859df3324bb15db97419f76a3586585 |
| tests/test_scientific_musicological_output_plausibility_additional.py | 24103 | cf184fb923a8d38c0f4e0d534ee0e3dbc22dc59b9602010d6a196927f817d0ef |
| tests/test_score_analysis.py | 5586 | ceb19535c3b22b9cc8975490b060277ea2cf8832544ea9a042e77790e684ec78 |
| tests/test_score_only_defaults.py | 4729 | 700e88625c87b69d287c1563d80b8c580d1f4d86e694591ec9ddbc04fc828ae1 |
| tests/test_score_validation.py | 3650 | bdf2921c2be87968b3c2f17b2fbcb04d73023f33f733b05f36bba066fe9ec715 |
| tests/test_snapshot_regression.py | 2952 | 2a6a3f16e71dca6faf8227f068c0c5f41a994d36ceb98519ba634cc1fae0310f |
| tests/test_spectral_analysis.py | 6662 | b5862bbaee9e20a248af4aa919e6509f002ca2dbb319673d941a91775198f55c |
| tests/test_spectral_lookup.py | 2043 | 49d04e2b95e8c5993fb6540b29065dc3141e8e7636c7a524217bbc8426657954 |
| tests/test_statistical_validation_legacy.py | 1236 | 5d1ba22c7123ec81e69addfcc7511a2db9530235fb9900f508e9436c8903c5e1 |
| tests/test_string_module_contracts.py | 7160 | 3e243547cd139e29da93fdab66d5fe783822ce22f3cd6624c2a78a944361cb66 |
| tests/test_string_musicological_invariants.py | 7197 | 330f0886220785880c31966473c2904fbf7485a90bd936982db4283c2a53f79b |
| tests/test_string_score_scenarios.py | 6849 | 1e854d48575913e2eba967b6ec0b95089adb8f50b2c817e9acb59adb2962d42a |
| tests/test_string_source_reproducibility.py | 3536 | b0710b946ac38fbfb8876009a29eb5282e1cb1dc75038925389c623bdc7d8df4 |
| tests/test_subindices.py | 6053 | fcdca7436b5e30f8a3ec53d1f78db7676699386b5d6eddca47182e03e0937b15 |
| tests/test_timbre_texture.py | 7082 | 49e0b4080c2bf02327dabf9b6c07fd0fadcb48dc087a2fde047e7bce2cc7a138 |
| tests/test_transposing_instrument_sounding_pitch_contract.py | 9951 | 3d16abb1694b0c94dfaf4431035d10a2a3a33bf413094a521959bd3b9af63337 |
| tests/test_unified_composite_contract.py | 5495 | f06b4b449624a638ba8b58185b61efa537f2e33f5dd755dc101b9f7cc5e922f0 |
| tests/test_unison_construct_separation.py | 7248 | 17c9d02eaa3588ba11d7c65505086efb8b4f752ecc7fe54606108a833f039129 |
| tests/test_unknown_instrument_policy.py | 5116 | 82c55d085add99aa435793729c2103da72549cc508f3b6a0f20a106bdd1c233e |
| tests/test_unpitched_aggregation_contract.py | 3972 | 601cc3222d948e51e123640a003a458c0a67a335729a80e9245010b113c658df |
| tests/test_unpitched_entry_paths.py | 6213 | 241f795b45b7c0d9b1bf5f419f0e80404687f411b90151eb630831e665435e11 |
| tests/test_unpitched_pitch_exclusion.py | 2994 | df546df0be1520273a4d902483b2bbc27d900e618d3fce454bf2d274735bb7e6 |
| tests/test_validation_framework.py | 2952 | 785efddbdcbab3cec63f5712511a0b9796b4f64da976b0e15fe87ef507a69c43 |
| tests/test_version_consistency.py | 1192 | e7fab1e951684e142f571889a6fded22ced4fcea5ad7297fbf67a7aae205e4b9 |
| tests/test_viola_harmonics.py | 2205 | fc2e0204ed6631cacbe9a3b5f8c59043e08e79a3b0e82bbcb461e0dfc55a22c1 |
| tests/test_viola_technique_modules.py | 4216 | 1897fad65409240fe79dfcbb93ff32cdac367b79766c1ea7b1bf1f8bc66dcc4e |
| tests/test_violin_full_dynamics_table.py | 1315 | a99ae73a43e73b5263ec5026b7e96c5da2f667ffd17c9169c31bde33aa7ffbc2 |
| tests/test_violin_harmonics.py | 2175 | c22945db4385099155d6548b03ca1b6f1dbff0309604b648adbead164888b5aa |
| tests/test_violin_sordina_diagnostics.py | 4647 | 609ce6604435cbb4f7ce7ed9d42bd7892eed397e3feda85cd78ff50398e603be |
| tests/test_violin_sul_ponticello.py | 3260 | fca3c16958ba2e4b793ff6ec9660d9494ca6ca8efe85d35d306a45631c76a359 |
| tests/test_violin_sul_tasto.py | 2138 | d9ecdd7ad5879903f08b2146d151101967c11f563428f5920ce866199512e79e |
| tests/test_wraparound_enharmonics.py | 3633 | 294ca181acfb36df4ff698d6cce8a7885ae96eec12470aa9631a865b2336dc25 |
| tests/test_xml_loader.py | 7053 | 2aefbe1a7323601cfb618ac2d2afdb526eda38b398e6fe9189e9f80da8a688b1 |
| timbre_texture_analysis.py | 21687 | d0c4e9c88f9e10ad26b40b0a52e59f5e2b983eea42e0c4f8822f7d143acc12f5 |
| tools/audit_gpr_determinism.py | 15210 | 653f22ce3025eeb6622b1fd3fd574228f88f3df9a89fd2295cf46984bc97a728 |
| tools/audit_gpr_model_quality.py | 26729 | f82cfe786aa08010ae26be9a4813e2ac498c1f5ee7edb54127a893602d4b3201 |
| tools/audit_instrument_metadata_range_resolution.py | 8266 | 8497b2e7828a79a98a0b34afa78c27b38b01196eaa77bbaadeb786d7ae8488aa |
| tools/audit_mp_dynamic_interpolation.py | 7925 | 2d749e582f864a021f2d242f91cd49c411e131aba5fc620d609fd89737fa8eed |
| tools/audit_transposing_instrument_pitch_contract.py | 4239 | 4708c505f4e38d0cfc8479ead4875f1edc95188effa7603436b9ad68d25a2935 |
| tools/commit_dynamics_from_dest2.py | 3610 | bc1e56ceb930c5e31642a9c6a5719e7204803a029cd5a1f4b7eea41781973fd4 |
| tools/commit_dynamics_from_para_dinamicas.py | 19529 | ae31514cb3912e0828ddfd262d199dcd992c725a29e06714b6c7096b417ab654 |
| tools/compare_dynamic_interpolation_methods.py | 31852 | f479cba6b04f0be56d138bec52dedcb6b9f992a24082839cd650611c5486b777 |
| tools/enforce_pitched_monotone_dynamic_ladders.py | 5702 | c276e0ed2bb59b5a5caeb2615a8bab22ffe5c1f31a45e51ecd60fd4b36a3cfe1 |
| tools/generate_full_dynamics_modules_from_xlsx.py | 9289 | 43735cef0e84927b46b174a06daf8d5f7be455381cd52a580663d7d37589026c |
| tools/generate_instrument_modules.py | 8514 | ff7673e1424f9ef21ee2226d843fd5febd572d07ddbb4a6b09d772c3cef15aef |
| tools/generate_instrument_register_audit.py | 2567 | d90c44617200bb381af39406c1f3ef5f066b19d4bb70177eeaca0dbe5cd0709e |
| tools/generate_percussion_modules_from_nontunperc.py | 12895 | 6f1686fe762988315156e2830a9a52da3eee84688ba8cc4dc6877d1aa921c2a5 |
| tools/generate_string_instrument_modules.py | 6902 | 42898dd10752f829018f48c462d4750ce4a0cb2fd49dc4853a4a323cf33d6c3e |
| tools/generate_violin_arco_full_dynamics_from_xlsx.py | 7090 | f7552696e3f1fda6cef30964ec2e02cda9532233b0e2f17a9de99873d31d8887 |
| tools/generate_violin_technique_modules_from_ok_workbooks.py | 18343 | c4477f3d22badc77627c08715518f080db4a896492ebbd185cc9bc86ead96f9a |
| tools/import_instrument_profiles_from_excel.py | 31240 | ce024dd756cfa286f40d476fd33d1a9ea74b18467ef3486e2082a1aa1618418b |
| tools/legacy_gpr_dynamic_interpolation.py | 16924 | 6670456e7816ac92d77897f3c6494b3a19570acef7be92f1d3902356f9472073 |
| tools/populate_td_importer_sheets_from_zenodo_media.py | 18034 | 15fdb90e34d7d0e7bab4d8c391ff5be9530f3a2b9415fb40800e3c8e24f7e04e |
| tools/refresh_regression_fixtures.py | 3813 | da656c504898173c4ef658db437f1500bf8f9856cb7030c765ac46edb8c86a7b |
| tools/rename_docs_branding.py | 2021 | cc2f13ff350be85c00dc2d4df678fc512d186d4647c8cf3156cabdca50f8445a |
| tools/run_mp_string_scenario_comparison.py | 7987 | 000ea49f549cdf0fa1898a63dbaf028a0b7b1e001f982e60dcd9dff5a7e7d40d |
| tools/run_string_density_scenario_validation.py | 52199 | 3786a64bfd45b939a3c946969be1bae0e750fe4b482383ebc7fcf6f48c8f4e9b |
| utils/__init__.py | 10 | 9c28a83690b8fc6015bb21b820735507402d8869a7bae78c3133bcaad8622433 |
| utils/notes.py | 8029 | fa01b9845a683e75de4a5e52dc671465a105d8e8e0a8f6bab182f9532b94ea67 |
| utils/optimization.py | 6051 | 6350c5d454a86710da5fe9f3b4efcc964aaefdd3c1a0c236a1e69ce3367245a9 |
| utils/plotting_style.py | 11471 | 949fae31535e22005ae1ee6a294db59b852f641d96692c8c24b0c32883d8f966 |
| utils/serialize_utils.py | 34651 | fa82700be490b57bef261a01063b4b76969660034f059a846c365e4cf70394ba |
| validation/__init__.py | 997 | 1754497e167aa1d638fbce78df6d5bace1aa0382fffbf4c6d10491c6628b59c9 |
| validation/gui_validation.py | 1904 | 7beea94cdbaa936f50275a286d16cc56fb0ef03ec32ffeb9db1b6b8ff42e8773 |
| validation/metrics.py | 3909 | b029c06a1195578a0f64a6e8b28e8da998b2c2c81052cd93a1e30ebe5e527d96 |
| validation/report.py | 4775 | bb716d1534ddddd69ff3ffdea000c776342df05b439a699f4fedca60b46eb66a |
| validation/rubric_scoring.py | 6286 | b4fba08592418f7e12b78e591551e8a4ad493f4b6259228547c05c2572e31eee |
| validation/schemas.py | 2038 | d6a7978dd3b2abce39eb70fff49752074bd21602818b76bb21e01f85ef38cc4e |
| validation/score_schemas.py | 4039 | c7bfc845512e428ff309468e8adf5c7082a3b77f66e23b39b0e13771acd53800 |
| validation/scripts/compute_inter_rater_reliability.py | 1976 | a0623bf698dac6c0932199f49fe221607a1ab7218aabdc867b8d1ff3709b86b6 |
| validation/scripts/correlate_metrics_with_ratings.py | 3363 | 61905755614ce5a32de0349a8f3c330191afc091b6ed396a178e49b72d37d957 |
| validation/scripts/score_upgrade_rubric.py | 1977 | bd16bce4fd78b122aca8b18885296dc76a655273f472dadea7c20e3386fdc498 |
| validation/scripts/validate_score_annotations.py | 1042 | 74368a855bb999eadc1239e24f9718d13777069a51adec9fcb0c829998814501 |
| validation/synthetic_cases.py | 4187 | e270426ddcf810e3ee9b28f7324d07cb1c007f54ba88099b8e1e83f1cb3a0bf2 |
| validation/verification.py | 8690 | d9faeaf1d73de348ebbeea8329b217e6ea2406207e03ab42fa69a01bf35e19bc |
| xml_loader.py | 25977 | 60b27565a77721eec6a433fcf89b7acc86b0cc5ee62e97ffcd3553b31d48f1ac |

Total files hashed: 289.

### Working-tree hash refresh (2026-09-17 patch; not a commit)

Baseline column above remains `872d1d4131037cd94fed1a2f4ae69543cb6ab3d7`. Files changed by this patch:

| Path | Bytes | SHA-256 |
|------|------:|---------|
| xml_loader.py | 31192 | ad9916cd15346a23c4ff89210ca4134f9df3b1ecb6fa24bf4172642c5154e719 |
| spectral_analysis.py | 15057 | 4239edf0f68c4a3d4b3098336515bf08f1bc8f08e02a20b56524f14d7bea2107 |
| validation/metrics.py | 4239 | 34a29de3ef2ea1b98f045f48b0a2334cc3d0c66a7e113720da50880f05f1ae7c |
| validation/__init__.py | 1055 | 294af54759ab5348651db40cef454cad34b1d64c9738b021a3671cfdafaaf455 |
| validation/scripts/compute_inter_rater_reliability.py | 2242 | b84971036c5d97a6d04f91d79e60a3370501820b969d7b670be317aaf7972f44 |
| gui/widgets/results_panel.py | 11296 | 6792940599895f11e5b5d653009f2432244e5c474bae30ecd1503cb37972dff1 |
| config.py | 8947 | bd860ebd8a7c8d07bde7ba3c1aac3b32fd57b4cfab989b152f2994005e66d3a5 |
| instrumentos/registry.py | 49604 | 73b420b197f28c817aeba08ef7a09492e54c09a6b79bb1bb72155c70965cb998 |
| core/metrics_metadata.py | 20185 | 51e9468c368e5b489b14e9bc6ebbb452ec25a2dc1c81b348a8532c753cc44c5a |
| docs/API.md | 18599 | a04ad27e7335f699241967e8210294abaf1f96b964acc1d6d879e30126258047 |
| docs/TECHNICAL_MANUAL.md | 57756 | b2c824bdce107d4f4cb6f8a3203d12d320e423917777e4dfb9b4ee445ed17149 |
| docs/MATHEMATICAL_MANUAL.md | 38494 | 2651c8c34382f7cabdf9064c54ec47b2050d3c2debfde061d1346d7de5da2902 |
| CHANGES.md | 24845 | a99ccd47d1f913f6c3fa66f8af4b5b07d4d928833f241342586e8d442c1e1571 |
| README.md | 39519 | a419140b6552895c4d0bca84a20a14be47cf1b8c9c032e3f9c03908af1644da3 |
| tests/test_musicxml_pitch_transpose.py | 7277 | 48823dec44e22cf078a51f62926f75770a264a6c6519b2eac7ac33865bc49bad |
| tests/test_input_order_weight_quantile.py | 2723 | 8bd69abb48e85228eb099582d6df8d5518ad9da2f1355a958b953e3fa797f8bf |
| tests/test_harmonic_ratio_octave_class.py | 1824 | 4f8dec87200b488678e24be383461d09afd187e1f3376321fb460eca967844b0 |
| tests/test_validation_framework.py | 3743 | 060e1bfcf880231f202a11cb1a0426dd30731eb6a38be09a34972c03d1331534 |

This document itself is excluded from the fingerprint. No final commit hash is claimed.

