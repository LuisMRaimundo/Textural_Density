# Calibration report — scale commensurability bridge

Bridge instruments are quasi-harmonic fixtures only (partials at
`n·f0`). They are **not** a pitched-instrument model.

**Model index** — theory only: partial histogram with
equal-energy-per-partial weighting (`internal_default`). Does
**not** reuse AmplitudeLayer measured band weights.

**Empirical index** — measured bands only (ERB bands whose
remapped energy is >50% from digitized `peak_power_band` rows;
threshold `internal_default`). Residual equal-density fill is
excluded.

**NO CALIBRATION ACHIEVED - factor undefined until the needs_manual_reading Sivian histograms are completed**

Surviving bridge instruments: **1** (need >= 2).

> Complete the `needs_manual_reading` Sivian histogram
> cells in `data/README.md` before a conversion factor
> can be defined.

## Per-instrument bridge results

| instrument | fill_fraction | n_measured | model index (theory) | empirical index (measured bands) | factor |
|---|---:|---:|---:|---:|---:|
| bass_viol | 0.000 | 2 | 4.11878 | 2.27231 | — |

## Excluded from bridge

- **trumpet**: AmplitudeLayer coverage refused (fill_fraction=0.701, n_measured=2)
- **clarinet**: fewer than 2 measured bands (n=1); degenerate empirical index excluded (fill_fraction=0.900, n_measured=1)
- **flute**: AmplitudeLayer coverage refused (fill_fraction=0.836, n_measured=2)

## Notes

- Violin full-band peak spectrum is not in Sivian et al. (1931);
  `bass_viol` stands in as the string-family bridge member.
- Soft violin average pressure (0.52 bars at 3 ft) is recorded
  in `data/source_constants.csv` but is not used as a spectral
  bridge weight.
- Reference distance for Sivian absolute levels: 3 ft (0.9144 m)
  unless a row states otherwise.
- Instruments with fill_fraction > 0.60 are refused by
  AmplitudeLayer (mostly residual fill) and cannot enter the
  bridge via measured absolute weights.
