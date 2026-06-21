# Instrument acoustic source provenance

> **Corpus status (2026-06):** The instrument metadata layer is **incomplete and under gradual curation**. Most registry entries lack dedicated acoustic tables; committed GPR modules are **partial proxies**, not final calibrated reference data. Missing or coarse values are expected when `source_type`, `profile_status`, and warnings remain honest. Do not treat flauta / clarinete / oboe tables as complete scientific corpora.

This document records **external acoustic metadata** embedded in `instrumentos/*.py`
modules. The analysis pipeline performs **score lookup** into these tables — not
live audio analysis.

## Flute (`flauta`)

- **Module:** `instrumentos/flauta.py`
- **Table:** `spectral_data` (note × pp/mf/ff amplitudes)
- **Provenance:** Sparse amplitude values digitized from external acoustic
  measurement / literature summaries used in the original research implementation.
- **Interpolation:** Gaussian-process regression for intermediate dynamics.
- **Uncertainty:** medium — sparse table, not full continuous spectrum.

## Clarinet (`clarinete`)

- **Module:** `instrumentos/clarinete.py`
- **Table:** `spectral_data_unicode`
- **Provenance:** External acoustic-source amplitude summaries (measurement /
  literature digitization).
- **Interpolation:** GPR by pitch and dynamic.
- **Uncertainty:** medium.

## Oboe (`oboe`)

- **Module:** `instrumentos/oboe.py`
- **Provenance:** Scaled proxy (`OBOE_SCALE = 1.05`) over flute acoustic table.
  Oboe-specific measured corpus not yet committed.
- **Uncertainty:** medium — literature-derived scaling proxy.

## Viola (`viola`)

- **Module:** `instrumentos/viola.py`
- **Table:** `spectral_data` (49 chromatic rows, C2–C6; 147 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of viola arco sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\CORDAS\ViOLA_Zenodo_collections_media.xlsx`
  (Zenodo deposit name: `viola_arco_sustains_median_summary_v1.xlsx`)
- **Sounding range (registry):** MIDI 48–76 (C3–E5); comfortable 50–69 (D3–A4)
- **Extraction:** CDM midpoint pass-through; no rescaling (`identity_v1`)
- **Interpolation:** Gaussian-process regression for intermediate dynamics
- **Uncertainty:** medium — sparse table with known QC flags on extreme-register rows

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
