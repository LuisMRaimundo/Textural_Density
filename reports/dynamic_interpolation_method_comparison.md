# Dynamic interpolation method comparison

- SHA: `913a415e54f59ab8dbb8a2afc0172da6e998947d`
- Classification: **PASS**
- Production GPR: **unchanged**
- Source rows: 315
- Positive scenarios: 320
- Negative scenarios: 20
- High/extreme sensitivity scenarios: 0
- PCHIP available: True

## Executive summary

Diagnostic comparison of production GPR vs piecewise linear and PCHIP references.
Source anchors and density formulas unchanged. Method choice affects modelled dynamics
and can propagate into orchestral density metrics, especially for low-register string masses.

**Recommendation:** production GPR acceptable but must report method sensitivity; future selectable interpolation policy recommended for low-register strings

## Top source-row GPR–linear (mp)

- double_bass A2: GPR=54.323 linear=51.065 Δ=3.258
- cello D2: GPR=74.351 linear=71.454 Δ=2.897
- cello G2: GPR=29.130 linear=31.868 Δ=2.738
- double_bass G1: GPR=61.854 linear=59.313 Δ=2.541
- cello D3: GPR=53.482 linear=51.025 Δ=2.457
- double_bass C#3: GPR=37.708 linear=39.660 Δ=1.952
- double_bass F#1: GPR=70.341 linear=68.398 Δ=1.943
- double_bass F1: GPR=66.155 linear=68.020 Δ=1.864
- double_bass C2: GPR=38.582 linear=40.361 Δ=1.779
- cello C3: GPR=54.662 linear=53.082 Δ=1.580
- cello B2: GPR=56.132 linear=54.555 Δ=1.577
- double_bass F#4: GPR=15.450 linear=17.018 Δ=1.569
- double_bass C3: GPR=48.238 linear=46.792 Δ=1.446
- double_bass E1: GPR=65.379 linear=66.823 Δ=1.445
- clarinet D#3: GPR=39.920 linear=38.510 Δ=1.410
- clarinet E3: GPR=36.373 linear=34.969 Δ=1.404
- cello F#2: GPR=37.899 linear=39.299 Δ=1.400
- cello A#3: GPR=34.347 linear=32.994 Δ=1.353
- cello G#2: GPR=49.673 linear=48.369 Δ=1.304
- double_bass D#4: GPR=17.048 linear=18.304 Δ=1.256

## Top scenario GPR–linear (density.instrument)

- pos_0102_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0104_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0106_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0108_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0110_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0112_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0114_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0116_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0118_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0120_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0122_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0124_low_register_mass (low_register_mass): GPR=184.9184 Δ=4.0860 [low]
- pos_0054_very_sparse_aggregate (very_sparse_aggregate): GPR=72.9914 Δ=2.6841 [moderate]
- pos_0022_very_dense_chromatic (very_dense_chromatic): GPR=46.4590 Δ=2.6825 [moderate]
- pos_0278_all_four_strings (all_four_strings): GPR=116.5995 Δ=2.6747 [low]
- pos_0012_very_dense_chromatic (very_dense_chromatic): GPR=34.4458 Δ=2.3473 [moderate]
- pos_0011_very_dense_chromatic (very_dense_chromatic): GPR=118.0986 Δ=2.1739 [low]
- pos_0078_registrally_stratified (registrally_stratified): GPR=77.3534 Δ=1.9549 [low]
- pos_0083_registrally_stratified (registrally_stratified): GPR=77.3534 Δ=1.9549 [low]
- pos_0088_registrally_stratified (registrally_stratified): GPR=77.3534 Δ=1.9549 [low]

## Interpretation

1. GPR can materially alter density.instrument vs linear/PCHIP when mp/p/f differ strongly.
2. Differences propagate from source rows into chord/aggregate results.
3. Low-register string masses and heterogeneous aggregates show highest sensitivity.
4. PCHIP reduces convex-hull departures at row level but shifts scenario metrics.
5. Linear is a transparent baseline; GPR remains default pending future policy PR.
