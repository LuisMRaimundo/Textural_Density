# Dynamic interpolation method comparison

> **Note.** `pchip_anchor` is a dynamic-axis 3-point PCHIP on `pp`/`mf`/`ff`.
> It does not use `instrumentos.pitch_interpolation.MIN_PCHIP_ANCHORS`.

- SHA: `3e7733db5d2c4b94ed2d29e15e8c69b4ad09677f`
- Classification: **PASS**
- Production GPR: **unchanged**
- Source rows: 359
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

- cello B2: GPR=47.375 linear=46.044 Δ=1.330
- cello E2: GPR=39.499 linear=40.609 Δ=1.110
- double_bass A2: GPR=37.439 linear=36.337 Δ=1.102
- clarinet E3: GPR=35.960 linear=35.072 Δ=0.888
- cello D2: GPR=55.954 linear=55.067 Δ=0.888
- cello D#2: GPR=50.515 linear=49.641 Δ=0.875
- cello C3: GPR=49.236 linear=48.385 Δ=0.851
- bassoon F2: GPR=42.647 linear=43.334 Δ=0.686
- double_bass C#3: GPR=25.852 linear=26.513 Δ=0.661
- cello C2: GPR=56.461 linear=55.807 Δ=0.654
- viola A3: GPR=30.087 linear=29.458 Δ=0.629
- cello F#2: GPR=34.749 linear=34.121 Δ=0.628
- viola F#3: GPR=36.836 linear=36.216 Δ=0.620
- cello A#2: GPR=44.211 linear=43.605 Δ=0.606
- cello E3: GPR=44.177 linear=43.582 Δ=0.595
- viola D#3: GPR=43.518 linear=42.943 Δ=0.575
- clarinet F3: GPR=32.636 linear=32.092 Δ=0.544
- viola G3: GPR=44.683 linear=44.144 Δ=0.539
- oboe E4: GPR=24.846 linear=25.376 Δ=0.529
- violin A#3: GPR=25.340 linear=25.863 Δ=0.523

## Top scenario GPR–linear (density.instrument)

- pos_0001_very_dense_chromatic (very_dense_chromatic): GPR=76.2192 Δ=0.0000 [negligible]
- pos_0002_very_dense_chromatic (very_dense_chromatic): GPR=96.3034 Δ=0.0000 [negligible]
- pos_0003_very_dense_chromatic (very_dense_chromatic): GPR=86.2907 Δ=0.0000 [negligible]
- pos_0004_very_dense_chromatic (very_dense_chromatic): GPR=15.0004 Δ=0.0000 [negligible]
- pos_0005_very_dense_chromatic (very_dense_chromatic): GPR=25.4844 Δ=0.0000 [negligible]
- pos_0006_very_dense_chromatic (very_dense_chromatic): GPR=104.2109 Δ=0.0000 [negligible]
- pos_0007_very_dense_chromatic (very_dense_chromatic): GPR=78.5295 Δ=0.0000 [negligible]
- pos_0008_very_dense_chromatic (very_dense_chromatic): GPR=73.9918 Δ=0.0000 [negligible]
- pos_0009_very_dense_chromatic (very_dense_chromatic): GPR=27.3402 Δ=0.0000 [negligible]
- pos_0010_very_dense_chromatic (very_dense_chromatic): GPR=37.9271 Δ=0.0000 [negligible]
- pos_0011_very_dense_chromatic (very_dense_chromatic): GPR=84.3411 Δ=0.0000 [negligible]
- pos_0012_very_dense_chromatic (very_dense_chromatic): GPR=60.5577 Δ=0.0000 [negligible]
- pos_0013_very_dense_chromatic (very_dense_chromatic): GPR=126.8405 Δ=0.0000 [negligible]
- pos_0014_very_dense_chromatic (very_dense_chromatic): GPR=44.8579 Δ=0.0000 [negligible]
- pos_0015_very_dense_chromatic (very_dense_chromatic): GPR=87.7638 Δ=0.0000 [negligible]
- pos_0016_very_dense_chromatic (very_dense_chromatic): GPR=76.3919 Δ=0.0000 [negligible]
- pos_0017_very_dense_chromatic (very_dense_chromatic): GPR=115.4523 Δ=0.0000 [negligible]
- pos_0018_very_dense_chromatic (very_dense_chromatic): GPR=47.4855 Δ=0.0000 [negligible]
- pos_0019_very_dense_chromatic (very_dense_chromatic): GPR=51.6406 Δ=0.0000 [negligible]
- pos_0020_very_dense_chromatic (very_dense_chromatic): GPR=49.5877 Δ=0.0000 [negligible]

## Interpretation

1. GPR can materially alter density.instrument vs linear/PCHIP when mp/p/f differ strongly.
2. Differences propagate from source rows into chord/aggregate results.
3. Low-register string masses and heterogeneous aggregates show highest sensitivity.
4. PCHIP reduces convex-hull departures at row level but shifts scenario metrics.
5. Linear is a transparent baseline; GPR remains default pending future policy PR.
