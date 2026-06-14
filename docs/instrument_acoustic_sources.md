# Instrument acoustic source provenance

This document records **external acoustic metadata** embedded in `instrumentos/*.py`
modules. The analysis pipeline performs **score lookup** into these tables — not
live audio analysis.

## Scope and curation model

- **Runtime:** score-based symbolic lookup at **sounding pitch** and written dynamic markings.
- **Metadata source:** external/proxy tables curated gradually by the user. Values may be derived offline from SoundSpectrAnalyse outputs or other sources, but **SoundSpectrAnalyse is not imported or run** by Textural Density.
- **Incomplete data:** missing instrument profiles or sparse tables are expected during development; coarse fallbacks are valid when labelled honestly.
- **Labelling rule:** fallback/default/proxy values must **not** be presented as empirical measurement.
- **Sounding pitch rule:** all acoustic/proxy table entries must be stored in **real sounding / concert pitch**. Example: B-flat clarinet written D4 → store sounding C4 (MIDI 60), not written D4 (MIDI 62). Registry `transposition` is for score parsing only.
- **Auxiliary Excel importer:** offline validation/export via [`instrument_profile_importer.md`](instrument_profile_importer.md) — not part of the analytical core; does not change formulas; runtime should consume validated JSON artefacts, not raw `.xlsx` files.

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
