# Validation Report — Textural Density

Generated: 2026-06-21 17:00 UTC

## Status

- **Empirical validation:** No external validation data provided. **Current status: verified_only.**
- **Verification:** synthetic cases and property checks (implementation correctness).
- **Validation:** expert/listening/corpus comparison requires annotated data in `validation/` subfolders.

## Verification summary

- Synthetic cases executed: **1**
- Property/regression checks: **1/2 passed**

### Failed checks

- `synthetic.test.finite`: non-finite density

### Passed property checks (sample)

- `property.test`: ok

## External data inventory

| Source | Files/records |
|--------|---------------|
| Expert annotations (`validation/expert_annotations/`) | 0 |
| Listening tests (`validation/listening_tests/`) | 0 |
| Corpus examples (`validation/corpus_examples/`) | 1 |

## Known limitations

- Score/information input only — no measured audio spectra or SPL.
- Strictly symbolic analysis: no auditory, psychoacoustic, perceptual, or virtual-tone modelling.
- Instrument profiles may be `coarse_default` with high uncertainty.
- Lambda calibration validates one interval-decay component only.

## Calibration residuals

See `densidade_intervalar.calibrate_lambda` and `config/density_params.json`. Full model external validation pending annotated corpora.
