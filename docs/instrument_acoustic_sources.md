# Instrument acoustic source provenance

> **Corpus status (2026-06):** The instrument metadata layer is **incomplete and under gradual curation**. Most registry entries lack dedicated acoustic tables; committed GPR modules are **partial proxies**, not final calibrated reference data. Missing or coarse values are expected when `source_type`, `profile_status`, and warnings remain honest. Do not treat flute / clarinet / oboe tables as complete scientific corpora.

This document records **external acoustic metadata** embedded in `instrumentos/*.py`
modules. The analysis pipeline performs **score lookup** into these tables — not
live audio analysis.

## Flute (`flute`)

- **Module:** `instrumentos/flute.py`
- **Table:** `spectral_data` (40 chromatic rows, B3–D7; 120 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of flute sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Flute_Zenodo_collections_media.xlsx`
- **Interpolation:** Gaussian-process regression for intermediate dynamics.
- **Uncertainty:** medium — sparse table, not full continuous spectrum.

## Clarinet (`clarinet`)

- **Module:** `instrumentos/clarinet.py`
- **Table:** `spectral_data` (47 chromatic rows, D3–C7; 141 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of clarinet sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Clarinet_Zenodo_collections_media.xlsx`
- **Interpolation:** Gaussian-process regression for intermediate dynamics
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Oboe (`oboe`)

- **Module:** `instrumentos/oboe.py`
- **Table:** `spectral_data` (36 chromatic rows, A#3–A6; 108 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of oboe sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Oboe_Zenodo_collections_media.xlsx`
- **Interpolation:** Gaussian-process regression for intermediate dynamics
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Bassoon (`fagote` → `bassoon.py`)

- **Module:** `instrumentos/bassoon.py`
- **Table (source_table_span):** `spectral_data` (42 chromatic rows, **A#1–D#5**, MIDI 34–75), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Provenance:** Median/midpoint summary of bassoon sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Bassoon_Zenodo_collections_media.xlsx`
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Interpolation:** Gaussian-process regression for intermediate dynamics
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Trumpet (`trompete` → `trumpet.py`)

- **Module:** `instrumentos/trumpet.py`
- **Table (source_table_span):** `spectral_data` (36 chromatic rows, **E3–D#6**, MIDI 52–87), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Provenance:** Median/midpoint summary of trumpet (Bb) sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\METAIS\Trumpet_Zenodo_collections_media.xlsx`
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Interpolation:** Gaussian-process regression for intermediate dynamics
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Viola (`viola`)

- **Module:** `instrumentos/viola.py`
- **Table:** `spectral_data` (49 chromatic rows, C3–C7; 147 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of viola arco sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Portable source anchor:** `docs/instrument_acoustic_sources.md#viola` (in `INSTRUMENT_SOURCE`; PR #14)
- **Authoritative ingestion sheet:** `VIOLA_Media` in `D:\CORDAS\ViOLA_Zenodo_collections_media.xlsx`
  (Zenodo deposit name: `viola_arco_sustains_median_summary_v1.xlsx`)
- **Note-label normalization:** duplicate media labels such as `F4 (2)` are stripped by
  `normalize_media_note_label()` before canonical parsing (maps to `F4` with the same CDM values).
- **Sounding range (registry):** MIDI 48–96 (C3–C7), aligned with committed `spectral_data` table span; comfortable 50–69 (D3–A4)
- **Extraction:** CDM midpoint pass-through; no rescaling (`identity_v1`)
- **Interpolation:** Gaussian-process regression for intermediate dynamics
- **Uncertainty:** medium — sparse table with known QC flags on extreme-register rows

## Violin (`violin`)

- **Module:** `instrumentos/violin.py`
- **Table:** `spectral_data` (49 chromatic rows, G3–G7)
- **Provenance:** IOWA+ORCH arco sustain CDM medians at pp/mf/ff
- **Source workbook:** `D:\CORDAS\VIOLIN_Zenodo_collections_media.xlsx`
- **Interpolation:** GPR for intermediate dynamics
- **Uncertainty:** medium

## Violin sordina (`violin_sordina`)

- **Module:** `instrumentos/violin_sordina.py`
- **Table:** `spectral_data` (49 chromatic rows, G3–G7)
- **Provenance:** IOWA+ORCH arco sordina CDM `combined_sord_collection_raw` at pp/mf/ff
- **Source workbook:** `D:\CORDAS\VIOLIN Zenodo_Arco Sordina.xlsx` (sheets `SORDINA-pp`, `SORDINA-mf`, `SORDINA-ff`)
- **Source technique:** `arco_sordina`
- **Interpolation:** GPR for intermediate dynamics
- **Uncertainty:** medium

## Violin sul ponticello (`violin_sul_ponticello`)

- **Module:** `instrumentos/violin_sul_ponticello.py`
- **Table:** `spectral_data` (49 chromatic rows, G3–G7)
- **Measured anchor:** mf only (`MF_MEASURED` in module)
- **Extrapolated anchors:** pp and ff derived per note via violin arco pp/mf and ff/mf ratios (`instrumentos/mf_anchor_dynamic_extrapolation.py`)
- **GPR-modelled dynamics:** pppp, ppp, p, mp, f, fff, ffff (and other non-anchor markings) predicted by GPR on the pp/mf/ff anchor triple — same ordinal model as other GPR modules
- **Source technique:** `arco_sul_ponticello`
- **Interpolation:** GPR for intermediate dynamics
- **Uncertainty:** high (pp/ff are modelled from mf-only source)
- **Curation (2026-06-30):** corrected hand-curated `MF_MEASURED` mf rows (G3–G7); pp/ff anchors regenerated via violin arco ratio transfer

- **Module:** `instrumentos/violin_art_harm.py`
- **Table:** `spectral_data` (25 chromatic rows, G5–G7)
- **Measured anchor:** mf only (`MF_MEASURED` in module)
- **Extrapolated anchors:** pp and ff derived per note via violin arco pp/mf and ff/mf ratios (`instrumentos/mf_anchor_dynamic_extrapolation.py`)
- **GPR-modelled dynamics:** pppp, ppp, p, mp, f, fff, ffff predicted by GPR on the pp/mf/ff anchor triple
- **Source technique:** `arco_artificial_harmonic`
- **Interpolation:** GPR for intermediate dynamics
- **Uncertainty:** high (pp/ff are modelled from mf-only source; upper-register table only)

## Cello (`cello`)

- **Module:** `instrumentos/cello.py`
- **Table:** `spectral_data` (49 chromatic rows, C2–C6)
- **Provenance:** IOWA+ORCH arco sustain CDM medians at pp/mf/ff
- **Source workbook:** `D:\CORDAS\CELLO_Zenodo_collections_media.xlsx`
- **Interpolation:** GPR for intermediate dynamics
- **Uncertainty:** medium

## Double bass (`double_bass`)

- **Module:** `instrumentos/double_bass.py`
- **Table (source_table_span):** `spectral_data` (45 chromatic rows, **E1–C5**, MIDI 28–72), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Comfortable range:** MIDI 31–55 (G1–G3) — narrower orchestrational band, not a table limit
- **Source technique:** `arco_sustain` (`table_supported_techniques`)
- **Provenance:** IOWA+ORCH arco sustain CDM medians at pp/mf/ff
- **Source workbook:** `D:\CORDAS\DOUBLEBASS_Zenodo_collections_media.xlsx`
- **Interpolation:** GPR for intermediate dynamics
- **Uncertainty:** medium
- **Span status:** E1–A3 in older docs was obsolete; committed span is E1–C5 (**PASS**). Upper-register methodological QC (A♯3–C5) remains **REVIEW REQUIRED**.

## Generation tooling

Offline curation pipeline (not used at runtime):

1. `tools/populate_td_importer_sheets_from_zenodo_media.py` — builds `AcousticTable`, `Registry`, and `Provenance` sheets from `*_Media` workbooks. Applies `normalize_media_note_label()` when reading media rows (strips trailing `(2)` duplicate markers).
2. `tools/generate_instrument_modules.py` — emits `instrumentos/flute.py`, `oboe.py`, `clarinet.py`, `violin.py`, `viola.py`, `cello.py`, `double_bass.py`. Viola and double bass source reconstruction use the `VIOLA_Media` / `DBass_Media` sheets via `load_spectral_data_from_media` (their workbooks ship no `AcousticTable` sheet).
3. `tools/build_viola_table_from_media.py` — helper to regenerate viola `spectral_data` from `VIOLA_Media`.
4. `tools/refresh_regression_fixtures.py` — updates golden regression/snapshot/benchmark fixtures after intentional table changes.

**mf-only technique tables:** `violin_sul_ponticello.py` and `violin_art_harm.py` are hand-curated (not emitted by `generate_instrument_modules.py`). Measured mf rows live in `MF_MEASURED`; pp/ff anchors are built offline via `instrumentos/mf_anchor_dynamic_extrapolation.build_spectral_data_from_mf_anchor()` using violin arco per-note dynamic ratios. Intermediate and extreme dynamics (`pppp` … `ffff`) remain GPR-modelled at runtime in `calculate_metrics`.

## Media note-label normalization (PR #14)

External Zenodo `*_Media` sheets may label duplicate chromatic rows with a trailing `(2)` suffix (e.g. `F4 (2)`). Before canonical note parsing:

```python
from utils.notes import normalize_media_note_label

normalize_media_note_label("F4 (2)")  # → "F4"
```

Applied in `tools/populate_td_importer_sheets_from_zenodo_media.py` (`_read_media_rows`) and `tools/generate_instrument_modules.py`. This corrects **source-table parsing and alignment** — not acoustic meaning or perceptual validation.

## Source workbook reconstruction (local verification)

| Workbook | Media sheet | Rows | Local status |
|----------|-------------|------|--------------|
| `VIOLIN_Zenodo_collections_media.xlsx` | `Violin_Media` | 49 | PASS — 0 value differences vs committed module |
| `ViOLA_Zenodo_collections_media.xlsx` | `VIOLA_Media` | 49 | PASS — 0 value differences (C3–C7; `F4` from former `F4 (2)`) |
| `CELLO_Zenodo_collections_media.xlsx` | `Cello_Media` | 49 | PASS |
| `DOUBLEBASS_Zenodo_collections_media.xlsx` | `DBass_Media` | 45 | PASS |

**CI:** `tests/test_string_source_reproducibility.py` skips when workbooks are absent on the runner. CI verifies committed modules and tests; independent reconstruction requires local workbooks or future canonical fixtures.

## Technique metadata vs source tables

Registry `supported_techniques` lists organological capabilities. GPR modules declare `INSTRUMENT_SOURCE.source_technique` and `table_supported_techniques` for the numerical table actually committed (e.g. `arco_sustain` for strings, `ordinary_sustain` for winds). Pizzicato, tremolo, harmonics, mute, flutter-tongue, etc. are **not** modelled unless separate technique-specific tables exist.

Audit: `tools/audit_instrument_metadata_range_resolution.py` → `reports/instrument_metadata_range_resolution_audit.*`

## Scientific review candidates (pending adjudication)

| ID | Topic | Status |
|----|-------|--------|
| DB-SPAN | Double-bass `source_table_span` E1–C5 aligns with committed table and registry; E1–A3 was obsolete documentation. Upper-register QC (A♯3–C5) open. | **PASS** (span); **REVIEW REQUIRED** (upper QC) |
| TECHNIQUE | `INSTRUMENT_SOURCE.table_supported_techniques` vs registry `supported_techniques`; tables do not overclaim technique coverage. | **PASS** |
| TUBA-RNG | Tuba sounding_range MIDI 28–58 is coarse-default validation placeholder without source table. | **REVIEW REQUIRED** |
| TRANS-META | `registry.transposition` is metadata-only; manual input is sounding pitch; MusicXML `<transpose>` converts once. | **PASS** |
| GPR-DET | Production GPR uses explicit `random_state=GPR_RANDOM_STATE` (`0`) via `create_dynamic_gpr()`; determinism is numerical repeatability only, not general empirical validation. | **PASS** |
| GPR-MQ | GPR model-quality audit (`tools/audit_gpr_model_quality.py`): 357 source rows (8 GPR modules, incl. bassoon); 58 convex-hull departures (pp–mf); GPR–linear/quadratic/PCHIP diagnostic deviations. Production GPR unchanged; references not adopted. | **REVIEW REQUIRED** (local hull departures; low-register strings) |
| GPR-CMP | Interpolation method comparison (`tools/compare_dynamic_interpolation_methods.py`): GPR vs linear vs PCHIP — 357 source rows, 320+20 scenarios, 5 benchmark excerpts. **0** high/extreme scenario-level `density.instrument` cases; production GPR unchanged; linear/PCHIP not adopted. | **PASS** (diagnostic complete; policy selection deferred) |

**Resolved (PR #14):** viola `INSTRUMENT_SOURCE` portable provenance (`docs/instrument_acoustic_sources.md#viola`).

## Register-dependence audit (2026-07-12, read-only)

Findings of a read-only audit of register dependence and per-event propagation
(no code, config, or data changes; `METRIC_SCHEMA_VERSION` unchanged):

- **Provenance uniformity.** All module-backed tables encode the same class of
  datum — a **Combined Density Metric (CDM)**, a spectral-density-derived measure
  (midpoint/median of IOWA+ORCH sustain collections at pp/mf/ff). None are raw
  amplitude/SPL pressure and none are literature-derived. Two variants are flagged
  as partly synthetic: **`violin_sul_ponticello`** and **`violin_art_harm`** carry
  a **measured mf anchor only**, with pp/ff transferred from violin-arco per-note
  ratios (`uncertainty="high"`).
- **mf curve shapes.** One-player mf density sampled every 3 semitones is
  **non-monotone for every instrument** (downward-trending with local reversals,
  typically at register/string breaks — e.g. violin C#4→E4, cello F#2→C3,
  contrabass C#2→E2, bassoon C#4→G4). No instrument is cleanly monotone-decreasing;
  do not assume monotonicity when reasoning about register.
- **Per-event fidelity.** The pipeline resolves density at the **exact event MIDI**
  (`microtonal.note_to_midi_strict`, float — carries quarter-tones and cents).
  Interpolation between chromatic anchors is shape-preserving PCHIP in-range
  (≥4 anchors) else linear; edge extrapolation is linear, with constant fallback
  beyond 12 semitones (`pitch_interpolation.resolve_density_from_table`). There is
  **no cross-event averaging/banding** of the one-player weight (the only mean is
  the per-pitch-bin spectral-weight mean, which collapses exact-MIDI unisons only).
  At every module's sounding-range extremes the endpoints coincide with table
  anchors, so lookups return provenance `exact` with **Δ = 0** vs the raw table
  value; smoothing affects only microtonal between-anchor targets.
- **Deconfounded REG (REGNAT) sweep.** A fixed 3-semitone chromatic cluster at
  bottom/centre/top-3 positions for clarinete, fagote, violino, contrabaixo yields
  **S invariant** (= 2.6284; register-independent symbolic interval measure) and
  **mass/RSS/comp strictly decreasing** with ascent for all four — no violations at
  the sampled positions. (Local curve non-monotonicity above can still surface if a
  sweep samples adjacent to a reversal.)

## Epistemic limitations

- Verification tests validate implementation contracts, source consistency, provenance propagation, symbolic/musical invariants, and reproducibility under controlled conditions.
- Tests do **not** validate perceptual adequacy of the CDM model or prove correspondence to perceived density, loudness, salience, or timbral mass.
- Acoustic metadata are externally sourced and/or interpolated — not measured by Textural Density during score analysis.
- Note-label normalization corrects parsing and table-key alignment only.

## Registry-only instruments

Instruments without a dedicated module use `coarse_default.py` — register and
dynamic coarse models **without** external acoustic amplitude tables. Status:
`coarse_default` / audit label `symbolic_default`.

## Adding sourced profiles

1. Commit acoustic table + `INSTRUMENT_SOURCE` in the module.
2. Register in `instrumentos/registry.py`.
3. Document provenance in this file.

## Quantity (Qty) scaling

Textural Density treats `Qty` as player count for a symbolic event. Instrument modules return **one-player** density for a (note, dynamic) pair. Slice-level metrics apply:

- **Mass:** $\sum_j n_j \cdot d_j^{(1)}$ (linear)
- **Pressure-equivalent density:** $\sqrt{\sum_j n_j (d_j^{(1)})^2}$ (incoherent RSS)

Dynamics are encoded in the module lookup — not multiplied again in the mass formula. This is symbolic metadata, not measured SPL.

When adding profiles, also document citation and extraction method, register with honest `source_notes`, and ensure CI test `test_acoustic_instrument_modules_have_provenance` passes.
