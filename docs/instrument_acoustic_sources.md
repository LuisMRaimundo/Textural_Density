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
2. `tools/generate_instrument_modules.py` — emits `instrumentos/flute.py`, `oboe.py`, `clarinet.py`, `violin.py`, `viola.py`, `cello.py`, `double_bass.py`. Viola source reconstruction uses `VIOLA_Media` via `load_spectral_data_from_media`.
3. `tools/build_viola_table_from_media.py` — helper to regenerate viola `spectral_data` from `VIOLA_Media`.
4. `tools/refresh_regression_fixtures.py` — updates golden regression/snapshot/benchmark fixtures after intentional table changes.

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
| GPR-MQ | GPR model-quality audit (`tools/audit_gpr_model_quality.py`): 315 source rows; 49 convex-hull departures (pp–mf); GPR–linear/quadratic/PCHIP diagnostic deviations. Production GPR unchanged; references not adopted. | **REVIEW REQUIRED** (local hull departures; low-register strings) |
| GPR-CMP | Interpolation method comparison (`tools/compare_dynamic_interpolation_methods.py`): GPR vs linear vs PCHIP — 315 source rows, 320+20 scenarios, 5 benchmark excerpts. **0** high/extreme scenario-level `density.instrument` cases; production GPR unchanged; linear/PCHIP not adopted. | **PASS** (diagnostic complete; policy selection deferred) |

**Resolved (PR #14):** viola `INSTRUMENT_SOURCE` portable provenance (`docs/instrument_acoustic_sources.md#viola`).

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
