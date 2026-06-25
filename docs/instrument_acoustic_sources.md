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
- **Source workbook:** `D:\CORDAS\ViOLA_Zenodo_collections_media.xlsx`
  (Zenodo deposit name: `viola_arco_sustains_median_summary_v1.xlsx`)
- **Sounding range (registry):** MIDI 48–76 (C3–E5); comfortable 50–69 (D3–A4)
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

## Cello (`cello`)

- **Module:** `instrumentos/cello.py`
- **Table:** `spectral_data` (49 chromatic rows, C2–C6)
- **Provenance:** IOWA+ORCH arco sustain CDM medians at pp/mf/ff
- **Source workbook:** `D:\CORDAS\CELLO_Zenodo_collections_media.xlsx`
- **Interpolation:** GPR for intermediate dynamics
- **Uncertainty:** medium

## Double bass (`double_bass`)

- **Module:** `instrumentos/double_bass.py`
- **Table:** `spectral_data` (45 chromatic rows, E1–A3)
- **Provenance:** IOWA+ORCH arco sustain CDM medians at pp/mf/ff
- **Source workbook:** `D:\CORDAS\DOUBLEBASS_Zenodo_collections_media.xlsx`
- **Interpolation:** GPR for intermediate dynamics
- **Uncertainty:** medium

## Generation tooling

Offline curation pipeline (not used at runtime):

1. `tools/populate_td_importer_sheets_from_zenodo_media.py` — builds `AcousticTable`, `Registry`, and `Provenance` sheets from `*_Media` workbooks.
2. `tools/generate_instrument_modules.py` — emits `instrumentos/flute.py`, `oboe.py`, `clarinet.py`, `violin.py`, `viola.py`, `cello.py`, `double_bass.py`.
3. `tools/refresh_regression_fixtures.py` — updates golden regression/snapshot/benchmark fixtures after intentional table changes.

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
