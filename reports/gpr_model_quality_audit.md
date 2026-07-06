# GPR model-quality diagnostic audit

- Repository SHA: `6254bec2c9de09db9aedd980dc64627734c8e432`
- Classification: **PASS**
- Instruments: 8
- Source rows: 357
- Convex-hull departures (pp–mf): **58**
- Convex-hull departures (pp–mf–ff): **35**
- PCHIP available: True
- REVIEW REQUIRED rows: 88

> Diagnostic only. Production GPR unchanged. Linear/quadratic/PCHIP are comparison references.

## Per-instrument summary

- **bassoon**: 42 rows, hull departures=9 (21.4%), max |GPR−linear|=3.071
- **cello**: 49 rows, hull departures=12 (24.5%), max |GPR−linear|=2.897
- **clarinet**: 47 rows, hull departures=2 (4.3%), max |GPR−linear|=1.410
- **double_bass**: 45 rows, hull departures=7 (15.6%), max |GPR−linear|=3.258
- **flute**: 40 rows, hull departures=3 (7.5%), max |GPR−linear|=0.924
- **oboe**: 36 rows, hull departures=6 (16.7%), max |GPR−linear|=1.093
- **viola**: 49 rows, hull departures=10 (20.4%), max |GPR−linear|=0.580
- **violin**: 49 rows, hull departures=9 (18.4%), max |GPR−linear|=1.205

## Convex-hull departures (pp–mf)

- violin A3 (MIDI 57, low): pp=30.702 mp=28.329 mf=29.144 |Δlin|=1.205 |Δquad|=0.173 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- violin F4 (MIDI 65, low): pp=26.178 mp=25.887 mf=26.256 |Δlin|=0.349 |Δquad|=0.104 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull
- violin G#4 (MIDI 68, low): pp=21.368 mp=19.914 mf=20.041 |Δlin|=0.459 |Δquad|=0.129 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin A#4 (MIDI 70, low): pp=22.653 mp=20.411 mf=20.433 |Δlin|=0.577 |Δquad|=0.156 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin B4 (MIDI 71, low): pp=25.336 mp=25.050 mf=25.267 |Δlin|=0.234 |Δquad|=0.346 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin F#6 (MIDI 90, high): pp=8.188 mp=8.513 mf=8.468 |Δlin|=0.115 |Δquad|=0.156 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin A6 (MIDI 93, high): pp=7.428 mp=7.856 mf=7.846 |Δlin|=0.115 |Δquad|=0.233 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin B6 (MIDI 95, high): pp=6.432 mp=6.902 mf=6.888 |Δlin|=0.128 |Δquad|=0.189 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin F#7 (MIDI 102, high): pp=5.877 mp=5.862 mf=6.304 |Δlin|=0.335 |Δquad|=0.472 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola E4 (MIDI 64, low): pp=19.846 mp=20.048 mf=19.800 |Δlin|=0.237 |Δquad|=0.333 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors
- viola F4 (MIDI 65, middle): pp=16.887 mp=16.664 mf=16.821 |Δlin|=0.173 |Δquad|=0.239 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola F#4 (MIDI 66, middle): pp=17.865 mp=17.793 mf=18.148 |Δlin|=0.284 |Δquad|=0.394 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola C#5 (MIDI 73, middle): pp=13.606 mp=13.198 mf=13.242 |Δlin|=0.135 |Δquad|=0.220 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola E5 (MIDI 76, middle): pp=10.992 mp=11.153 mf=11.033 |Δlin|=0.130 |Δquad|=0.164 [REVIEW REQUIRED] mp outside pp–mf interval
- viola G5 (MIDI 79, middle): pp=10.177 mp=9.967 mf=10.066 |Δlin|=0.127 |Δquad|=0.165 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola F6 (MIDI 89, high): pp=5.551 mp=5.569 mf=5.111 |Δlin|=0.349 |Δquad|=0.492 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola G#6 (MIDI 92, high): pp=5.012 mp=5.185 mf=4.929 |Δlin|=0.235 |Δquad|=0.334 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors
- viola B6 (MIDI 95, high): pp=3.160 mp=3.464 mf=3.342 |Δlin|=0.167 |Δquad|=0.249 [REVIEW REQUIRED] mp outside pp–mf interval
- viola C7 (MIDI 96, high): pp=3.394 mp=3.239 mf=3.291 |Δlin|=0.078 |Δquad|=0.090 [REVIEW REQUIRED] mp outside pp–mf interval
- cello C3 (MIDI 48, low): pp=50.880 mp=54.662 mf=53.816 |Δlin|=1.580 |Δquad|=0.092 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors

## Top 20 |GPR−linear|

- double_bass A2 (MIDI 45, middle): pp=37.954 mp=54.323 mf=55.435 |Δlin|=3.258 |Δquad|=0.694 [OK] non-monotonic source anchors
- bassoon B1 (MIDI 35, low): pp=67.335 mp=66.719 mf=70.608 |Δlin|=3.071 |Δquad|=0.165 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- cello D2 (MIDI 38, low): pp=55.891 mp=74.351 mf=76.641 |Δlin|=2.897 |Δquad|=0.704 [OK] non-monotonic source anchors
- cello G2 (MIDI 43, low): pp=27.602 mp=29.130 mf=33.290 |Δlin|=2.738 |Δquad|=0.083 [OK] within expected diagnostic envelope
- double_bass G1 (MIDI 31, low): pp=38.375 mp=61.854 mf=66.293 |Δlin|=2.541 |Δquad|=1.075 [OK] non-monotonic source anchors
- cello D3 (MIDI 50, low): pp=34.827 mp=53.482 mf=56.424 |Δlin|=2.457 |Δquad|=0.842 [OK] non-monotonic source anchors
- bassoon C2 (MIDI 36, low): pp=61.505 mp=60.509 mf=63.452 |Δlin|=2.456 |Δquad|=0.172 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull
- double_bass C#3 (MIDI 49, middle): pp=45.548 mp=37.708 mf=37.697 |Δlin|=1.952 |Δquad|=0.460 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass F#1 (MIDI 30, low): pp=52.404 mp=70.341 mf=73.729 |Δlin|=1.943 |Δquad|=0.665 [OK] non-monotonic source anchors
- double_bass F1 (MIDI 29, low): pp=68.343 mp=66.155 mf=67.912 |Δlin|=1.864 |Δquad|=0.216 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- double_bass C2 (MIDI 36, low): pp=42.869 mp=38.582 mf=39.525 |Δlin|=1.779 |Δquad|=0.275 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- cello C3 (MIDI 48, low): pp=50.880 mp=54.662 mf=53.816 |Δlin|=1.580 |Δquad|=0.092 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- cello B2 (MIDI 47, low): pp=42.673 mp=56.132 mf=58.516 |Δlin|=1.577 |Δquad|=0.497 [OK] non-monotonic source anchors
- double_bass F#4 (MIDI 66, high): pp=22.610 mp=15.450 mf=15.154 |Δlin|=1.569 |Δquad|=0.498 [OK] non-monotonic source anchors
- double_bass C3 (MIDI 48, middle): pp=37.307 mp=48.238 mf=49.953 |Δlin|=1.446 |Δquad|=0.405 [OK] non-monotonic source anchors
- double_bass E1 (MIDI 28, low): pp=62.852 mp=65.379 mf=68.147 |Δlin|=1.445 |Δquad|=0.066 [OK] within expected diagnostic envelope
- clarinet D#3 (MIDI 51, low): pp=15.312 mp=39.920 mf=46.243 |Δlin|=1.410 |Δquad|=1.327 [OK] within expected diagnostic envelope
- clarinet E3 (MIDI 52, low): pp=12.956 mp=36.373 mf=42.307 |Δlin|=1.404 |Δquad|=1.318 [OK] within expected diagnostic envelope
- cello F#2 (MIDI 42, low): pp=36.935 mp=37.899 mf=40.087 |Δlin|=1.400 |Δquad|=0.059 [OK] within expected diagnostic envelope
- cello A#3 (MIDI 58, middle): pp=28.585 mp=34.347 mf=34.464 |Δlin|=1.353 |Δquad|=0.194 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors

## Top 20 |GPR−quadratic|

- clarinet D#3 (MIDI 51, low): pp=15.312 mp=39.920 mf=46.243 |Δlin|=1.410 |Δquad|=1.327 [OK] within expected diagnostic envelope
- clarinet E3 (MIDI 52, low): pp=12.956 mp=36.373 mf=42.307 |Δlin|=1.404 |Δquad|=1.318 [OK] within expected diagnostic envelope
- double_bass G1 (MIDI 31, low): pp=38.375 mp=61.854 mf=66.293 |Δlin|=2.541 |Δquad|=1.075 [OK] non-monotonic source anchors
- clarinet D3 (MIDI 50, low): pp=11.904 mp=30.942 mf=36.303 |Δlin|=0.738 |Δquad|=0.934 [OK] within expected diagnostic envelope
- cello D3 (MIDI 50, low): pp=34.827 mp=53.482 mf=56.424 |Δlin|=2.457 |Δquad|=0.842 [OK] non-monotonic source anchors
- clarinet F3 (MIDI 53, low): pp=11.828 mp=29.230 mf=34.489 |Δlin|=0.406 |Δquad|=0.747 [OK] within expected diagnostic envelope
- cello D2 (MIDI 38, low): pp=55.891 mp=74.351 mf=76.641 |Δlin|=2.897 |Δquad|=0.704 [OK] non-monotonic source anchors
- double_bass A2 (MIDI 45, middle): pp=37.954 mp=54.323 mf=55.435 |Δlin|=3.258 |Δquad|=0.694 [OK] non-monotonic source anchors
- double_bass F#1 (MIDI 30, low): pp=52.404 mp=70.341 mf=73.729 |Δlin|=1.943 |Δquad|=0.665 [OK] non-monotonic source anchors
- oboe C#4 (MIDI 61, low): pp=27.957 mp=18.391 mf=16.660 |Δlin|=1.093 |Δquad|=0.636 [OK] non-monotonic source anchors
- viola A#6 (MIDI 94, high): pp=4.864 mp=4.651 mf=4.026 |Δlin|=0.415 |Δquad|=0.593 [OK] non-monotonic source anchors
- clarinet A#3 (MIDI 58, low): pp=7.455 mp=17.983 mf=20.740 |Δlin|=0.564 |Δquad|=0.553 [OK] within expected diagnostic envelope
- flute C4 (MIDI 60, low): pp=12.595 mp=23.539 mf=25.955 |Δlin|=0.924 |Δquad|=0.553 [OK] non-monotonic source anchors
- clarinet F#3 (MIDI 54, low): pp=10.412 mp=25.980 mf=31.128 |Δlin|=0.031 |Δquad|=0.545 [OK] within expected diagnostic envelope
- oboe F6 (MIDI 89, high): pp=4.947 mp=4.758 mf=4.201 |Δlin|=0.371 |Δquad|=0.530 [OK] non-monotonic source anchors
- bassoon A4 (MIDI 69, high): pp=14.832 mp=8.450 mf=7.473 |Δlin|=0.863 |Δquad|=0.506 [OK] non-monotonic source anchors
- double_bass F#4 (MIDI 66, high): pp=22.610 mp=15.450 mf=15.154 |Δlin|=1.569 |Δquad|=0.498 [OK] non-monotonic source anchors
- cello B2 (MIDI 47, low): pp=42.673 mp=56.132 mf=58.516 |Δlin|=1.577 |Δquad|=0.497 [OK] non-monotonic source anchors
- viola F6 (MIDI 89, high): pp=5.551 mp=5.569 mf=5.111 |Δlin|=0.349 |Δquad|=0.492 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola G#5 (MIDI 80, high): pp=8.986 mp=9.480 mf=10.068 |Δlin|=0.317 |Δquad|=0.482 [OK] non-monotonic source anchors

## Top 20 |GPR−PCHIP|

- clarinet E3 (MIDI 52, low): pp=12.956 mp=36.373 mf=42.307 |Δlin|=1.404 |Δquad|=1.318 [OK] within expected diagnostic envelope
- clarinet D#3 (MIDI 51, low): pp=15.312 mp=39.920 mf=46.243 |Δlin|=1.410 |Δquad|=1.327 [OK] within expected diagnostic envelope
- bassoon B1 (MIDI 35, low): pp=67.335 mp=66.719 mf=70.608 |Δlin|=3.071 |Δquad|=0.165 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- double_bass G1 (MIDI 31, low): pp=38.375 mp=61.854 mf=66.293 |Δlin|=2.541 |Δquad|=1.075 [OK] non-monotonic source anchors
- bassoon C2 (MIDI 36, low): pp=61.505 mp=60.509 mf=63.452 |Δlin|=2.456 |Δquad|=0.172 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull
- cello G2 (MIDI 43, low): pp=27.602 mp=29.130 mf=33.290 |Δlin|=2.738 |Δquad|=0.083 [OK] within expected diagnostic envelope
- double_bass F1 (MIDI 29, low): pp=68.343 mp=66.155 mf=67.912 |Δlin|=1.864 |Δquad|=0.216 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- double_bass F#1 (MIDI 30, low): pp=52.404 mp=70.341 mf=73.729 |Δlin|=1.943 |Δquad|=0.665 [OK] non-monotonic source anchors
- clarinet D3 (MIDI 50, low): pp=11.904 mp=30.942 mf=36.303 |Δlin|=0.738 |Δquad|=0.934 [OK] within expected diagnostic envelope
- cello D3 (MIDI 50, low): pp=34.827 mp=53.482 mf=56.424 |Δlin|=2.457 |Δquad|=0.842 [OK] non-monotonic source anchors
- flute C4 (MIDI 60, low): pp=12.595 mp=23.539 mf=25.955 |Δlin|=0.924 |Δquad|=0.553 [OK] non-monotonic source anchors
- clarinet A#3 (MIDI 58, low): pp=7.455 mp=17.983 mf=20.740 |Δlin|=0.564 |Δquad|=0.553 [OK] within expected diagnostic envelope
- cello B2 (MIDI 47, low): pp=42.673 mp=56.132 mf=58.516 |Δlin|=1.577 |Δquad|=0.497 [OK] non-monotonic source anchors
- clarinet F3 (MIDI 53, low): pp=11.828 mp=29.230 mf=34.489 |Δlin|=0.406 |Δquad|=0.747 [OK] within expected diagnostic envelope
- double_bass G3 (MIDI 55, middle): pp=19.856 mp=28.759 mf=30.854 |Δlin|=0.654 |Δquad|=0.349 [OK] within expected diagnostic envelope
- double_bass F2 (MIDI 41, low): pp=32.057 mp=42.507 mf=44.577 |Δlin|=1.060 |Δquad|=0.387 [OK] non-monotonic source anchors
- double_bass G2 (MIDI 43, middle): pp=29.382 mp=39.819 mf=41.848 |Δlin|=1.087 |Δquad|=0.401 [OK] non-monotonic source anchors
- double_bass C2 (MIDI 36, low): pp=42.869 mp=38.582 mf=39.525 |Δlin|=1.779 |Δquad|=0.275 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- clarinet E4 (MIDI 64, low): pp=6.393 mp=13.386 mf=15.119 |Δlin|=0.449 |Δquad|=0.372 [OK] non-monotonic source anchors
- cello F#2 (MIDI 42, low): pp=36.935 mp=37.899 mf=40.087 |Δlin|=1.400 |Δquad|=0.059 [OK] within expected diagnostic envelope

## Top 20 GPR std (mp)

- double_bass A2 (MIDI 45, middle): pp=37.954 mp=54.323 mf=55.435 |Δlin|=3.258 |Δquad|=0.694 [OK] non-monotonic source anchors
- cello G2 (MIDI 43, low): pp=27.602 mp=29.130 mf=33.290 |Δlin|=2.738 |Δquad|=0.083 [OK] within expected diagnostic envelope
- bassoon B1 (MIDI 35, low): pp=67.335 mp=66.719 mf=70.608 |Δlin|=3.071 |Δquad|=0.165 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- double_bass G1 (MIDI 31, low): pp=38.375 mp=61.854 mf=66.293 |Δlin|=2.541 |Δquad|=1.075 [OK] non-monotonic source anchors
- cello D2 (MIDI 38, low): pp=55.891 mp=74.351 mf=76.641 |Δlin|=2.897 |Δquad|=0.704 [OK] non-monotonic source anchors
- clarinet D#3 (MIDI 51, low): pp=15.312 mp=39.920 mf=46.243 |Δlin|=1.410 |Δquad|=1.327 [OK] within expected diagnostic envelope
- clarinet E3 (MIDI 52, low): pp=12.956 mp=36.373 mf=42.307 |Δlin|=1.404 |Δquad|=1.318 [OK] within expected diagnostic envelope
- cello D3 (MIDI 50, low): pp=34.827 mp=53.482 mf=56.424 |Δlin|=2.457 |Δquad|=0.842 [OK] non-monotonic source anchors
- bassoon C2 (MIDI 36, low): pp=61.505 mp=60.509 mf=63.452 |Δlin|=2.456 |Δquad|=0.172 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull
- double_bass F#4 (MIDI 66, high): pp=22.610 mp=15.450 mf=15.154 |Δlin|=1.569 |Δquad|=0.498 [OK] non-monotonic source anchors
- double_bass C#3 (MIDI 49, middle): pp=45.548 mp=37.708 mf=37.697 |Δlin|=1.952 |Δquad|=0.460 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass C2 (MIDI 36, low): pp=42.869 mp=38.582 mf=39.525 |Δlin|=1.779 |Δquad|=0.275 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- double_bass F#1 (MIDI 30, low): pp=52.404 mp=70.341 mf=73.729 |Δlin|=1.943 |Δquad|=0.665 [OK] non-monotonic source anchors
- oboe C#4 (MIDI 61, low): pp=27.957 mp=18.391 mf=16.660 |Δlin|=1.093 |Δquad|=0.636 [OK] non-monotonic source anchors
- double_bass F1 (MIDI 29, low): pp=68.343 mp=66.155 mf=67.912 |Δlin|=1.864 |Δquad|=0.216 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- double_bass D#4 (MIDI 63, high): pp=23.600 mp=17.048 mf=16.538 |Δlin|=1.256 |Δquad|=0.430 [OK] non-monotonic source anchors
- clarinet D3 (MIDI 50, low): pp=11.904 mp=30.942 mf=36.303 |Δlin|=0.738 |Δquad|=0.934 [OK] within expected diagnostic envelope
- bassoon A4 (MIDI 69, high): pp=14.832 mp=8.450 mf=7.473 |Δlin|=0.863 |Δquad|=0.506 [OK] non-monotonic source anchors
- double_bass G#4 (MIDI 68, high): pp=16.931 mp=11.711 mf=11.427 |Δlin|=1.092 |Δquad|=0.365 [OK] non-monotonic source anchors
- cello B2 (MIDI 47, low): pp=42.673 mp=56.132 mf=58.516 |Δlin|=1.577 |Δquad|=0.497 [OK] non-monotonic source anchors

## Near pp

- violin B3 (MIDI 59, low): pp=39.784 mp=39.448 mf=39.101 |Δlin|=0.176 |Δquad|=0.097 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- violin C5 (MIDI 72, middle): pp=16.400 mp=16.553 mf=16.674 |Δlin|=0.053 |Δquad|=0.086 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- violin F#7 (MIDI 102, high): pp=5.877 mp=5.862 mf=6.304 |Δlin|=0.335 |Δquad|=0.472 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola F#4 (MIDI 66, middle): pp=17.865 mp=17.793 mf=18.148 |Δlin|=0.284 |Δquad|=0.394 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola F6 (MIDI 89, high): pp=5.551 mp=5.569 mf=5.111 |Δlin|=0.349 |Δquad|=0.492 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- cello G3 (MIDI 55, middle): pp=29.709 mp=29.554 mf=30.095 |Δlin|=0.445 |Δquad|=0.098 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- cello G4 (MIDI 67, middle): pp=21.700 mp=21.555 mf=21.163 |Δlin|=0.258 |Δquad|=0.070 [REVIEW REQUIRED] mp near pp anchor
- cello C5 (MIDI 72, high): pp=14.056 mp=13.938 mf=14.224 |Δlin|=0.244 |Δquad|=0.338 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- cello D#5 (MIDI 75, high): pp=13.026 mp=13.035 mf=13.103 |Δlin|=0.048 |Δquad|=0.194 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- double_bass D#3 (MIDI 51, middle): pp=38.369 mp=38.485 mf=38.854 |Δlin|=0.248 |Δquad|=0.111 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- flute G#6 (MIDI 92, high): pp=3.117 mp=3.106 mf=2.734 |Δlin|=0.276 |Δquad|=0.384 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- clarinet A6 (MIDI 93, high): pp=4.916 mp=4.908 mf=4.543 |Δlin|=0.272 |Δquad|=0.377 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- oboe E4 (MIDI 64, low): pp=16.198 mp=16.239 mf=16.184 |Δlin|=0.051 |Δquad|=0.216 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- bassoon B1 (MIDI 35, low): pp=67.335 mp=66.719 mf=70.608 |Δlin|=3.071 |Δquad|=0.165 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- bassoon C#2 (MIDI 37, low): pp=44.632 mp=44.497 mf=45.328 |Δlin|=0.657 |Δquad|=0.104 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- bassoon A3 (MIDI 57, middle): pp=15.105 mp=15.219 mf=15.357 |Δlin|=0.075 |Δquad|=0.145 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor

## Near mf

- violin B3 (MIDI 59, low): pp=39.784 mp=39.448 mf=39.101 |Δlin|=0.176 |Δquad|=0.097 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- violin G#4 (MIDI 68, low): pp=21.368 mp=19.914 mf=20.041 |Δlin|=0.459 |Δquad|=0.129 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin A4 (MIDI 69, low): pp=27.470 mp=23.938 mf=23.809 |Δlin|=0.787 |Δquad|=0.211 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- violin A#4 (MIDI 70, low): pp=22.653 mp=20.411 mf=20.433 |Δlin|=0.577 |Δquad|=0.156 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin B4 (MIDI 71, low): pp=25.336 mp=25.050 mf=25.267 |Δlin|=0.234 |Δquad|=0.346 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin C5 (MIDI 72, middle): pp=16.400 mp=16.553 mf=16.674 |Δlin|=0.053 |Δquad|=0.086 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- violin D#5 (MIDI 75, middle): pp=17.097 mp=16.607 mf=16.572 |Δlin|=0.096 |Δquad|=0.152 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- violin F#6 (MIDI 90, high): pp=8.188 mp=8.513 mf=8.468 |Δlin|=0.115 |Δquad|=0.156 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin A6 (MIDI 93, high): pp=7.428 mp=7.856 mf=7.846 |Δlin|=0.115 |Δquad|=0.233 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin B6 (MIDI 95, high): pp=6.432 mp=6.902 mf=6.888 |Δlin|=0.128 |Δquad|=0.189 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola G#3 (MIDI 56, low): pp=27.496 mp=28.389 mf=28.535 |Δlin|=0.114 |Δquad|=0.222 [REVIEW REQUIRED] mp near mf anchor
- viola B3 (MIDI 59, low): pp=23.328 mp=26.448 mf=26.714 |Δlin|=0.580 |Δquad|=0.131 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- viola D4 (MIDI 62, low): pp=27.954 mp=27.265 mf=27.252 |Δlin|=0.162 |Δquad|=0.138 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- viola F4 (MIDI 65, middle): pp=16.887 mp=16.664 mf=16.821 |Δlin|=0.173 |Δquad|=0.239 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola C#5 (MIDI 73, middle): pp=13.606 mp=13.198 mf=13.242 |Δlin|=0.135 |Δquad|=0.220 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola D5 (MIDI 74, middle): pp=14.207 mp=14.424 mf=14.498 |Δlin|=0.001 |Δquad|=0.021 [REVIEW REQUIRED] mp near mf anchor
- viola G5 (MIDI 79, middle): pp=10.177 mp=9.967 mf=10.066 |Δlin|=0.127 |Δquad|=0.165 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- cello A#2 (MIDI 46, low): pp=48.226 mp=44.220 mf=44.173 |Δlin|=0.966 |Δquad|=0.224 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello D#3 (MIDI 51, low): pp=39.887 mp=45.365 mf=45.686 |Δlin|=1.129 |Δquad|=0.182 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello A#3 (MIDI 58, middle): pp=28.585 mp=34.347 mf=34.464 |Δlin|=1.353 |Δquad|=0.194 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello B3 (MIDI 59, middle): pp=31.443 mp=32.273 mf=32.082 |Δlin|=0.351 |Δquad|=0.087 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello G#4 (MIDI 68, high): pp=18.692 mp=21.101 mf=21.259 |Δlin|=0.484 |Δquad|=0.116 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello A#4 (MIDI 70, high): pp=17.306 mp=18.367 mf=18.360 |Δlin|=0.271 |Δquad|=0.101 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello B4 (MIDI 71, high): pp=18.451 mp=19.171 mf=19.100 |Δlin|=0.234 |Δquad|=0.100 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello D#5 (MIDI 75, high): pp=13.026 mp=13.035 mf=13.103 |Δlin|=0.048 |Δquad|=0.194 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- double_bass C#2 (MIDI 37, low): pp=37.227 mp=35.143 mf=35.330 |Δlin|=0.661 |Δquad|=0.151 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- double_bass D2 (MIDI 38, low): pp=37.378 mp=34.335 mf=34.144 |Δlin|=0.618 |Δquad|=0.176 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass C#3 (MIDI 49, middle): pp=45.548 mp=37.708 mf=37.697 |Δlin|=1.952 |Δquad|=0.460 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass D#3 (MIDI 51, middle): pp=38.369 mp=38.485 mf=38.854 |Δlin|=0.248 |Δquad|=0.111 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- double_bass G#3 (MIDI 56, middle): pp=23.633 mp=24.141 mf=24.234 |Δlin|=0.057 |Δquad|=0.207 [REVIEW REQUIRED] mp near mf anchor
- double_bass A#3 (MIDI 58, high): pp=26.561 mp=25.309 mf=25.061 |Δlin|=0.127 |Δquad|=0.154 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass C#4 (MIDI 61, high): pp=27.734 mp=26.831 mf=26.875 |Δlin|=0.259 |Δquad|=0.126 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- double_bass E4 (MIDI 64, high): pp=23.261 mp=18.547 mf=18.548 |Δlin|=1.179 |Δquad|=0.297 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- flute E5 (MIDI 76, middle): pp=6.600 mp=7.250 mf=7.322 |Δlin|=0.108 |Δquad|=0.179 [REVIEW REQUIRED] mp near mf anchor
- clarinet A#6 (MIDI 94, high): pp=3.460 mp=3.900 mf=3.903 |Δlin|=0.107 |Δquad|=0.155 [REVIEW REQUIRED] mp near mf anchor
- oboe A#3 (MIDI 58, low): pp=20.844 mp=21.191 mf=21.132 |Δlin|=0.131 |Δquad|=0.269 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- oboe C4 (MIDI 60, low): pp=20.340 mp=18.847 mf=18.940 |Δlin|=0.443 |Δquad|=0.131 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- oboe D4 (MIDI 62, low): pp=18.022 mp=18.597 mf=18.680 |Δlin|=0.082 |Δquad|=0.217 [REVIEW REQUIRED] mp near mf anchor
- oboe E4 (MIDI 64, low): pp=16.198 mp=16.239 mf=16.184 |Δlin|=0.051 |Δquad|=0.216 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- oboe A5 (MIDI 81, middle): pp=5.734 mp=5.359 mf=5.359 |Δlin|=0.094 |Δquad|=0.140 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- oboe A#5 (MIDI 82, high): pp=5.015 mp=5.160 mf=5.188 |Δlin|=0.016 |Δquad|=0.175 [REVIEW REQUIRED] mp near mf anchor
- oboe F#6 (MIDI 90, high): pp=5.032 mp=5.471 mf=5.475 |Δlin|=0.107 |Δquad|=0.151 [REVIEW REQUIRED] mp near mf anchor
- bassoon A3 (MIDI 57, middle): pp=15.105 mp=15.219 mf=15.357 |Δlin|=0.075 |Δquad|=0.145 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- bassoon C#4 (MIDI 61, middle): pp=9.397 mp=9.271 mf=9.331 |Δlin|=0.077 |Δquad|=0.145 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- bassoon E4 (MIDI 64, high): pp=9.516 mp=9.918 mf=9.968 |Δlin|=0.064 |Δquad|=0.082 [REVIEW REQUIRED] mp near mf anchor
- bassoon G4 (MIDI 67, high): pp=13.695 mp=13.460 mf=13.581 |Δlin|=0.149 |Δquad|=0.127 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- bassoon G#4 (MIDI 68, high): pp=12.216 mp=13.905 mf=14.026 |Δlin|=0.332 |Δquad|=0.112 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors

## Outside pp–mf

- violin A3 (MIDI 57, low): pp=30.702 mp=28.329 mf=29.144 |Δlin|=1.205 |Δquad|=0.173 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- violin F4 (MIDI 65, low): pp=26.178 mp=25.887 mf=26.256 |Δlin|=0.349 |Δquad|=0.104 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull
- violin G#4 (MIDI 68, low): pp=21.368 mp=19.914 mf=20.041 |Δlin|=0.459 |Δquad|=0.129 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin A#4 (MIDI 70, low): pp=22.653 mp=20.411 mf=20.433 |Δlin|=0.577 |Δquad|=0.156 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin B4 (MIDI 71, low): pp=25.336 mp=25.050 mf=25.267 |Δlin|=0.234 |Δquad|=0.346 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin F#6 (MIDI 90, high): pp=8.188 mp=8.513 mf=8.468 |Δlin|=0.115 |Δquad|=0.156 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin A6 (MIDI 93, high): pp=7.428 mp=7.856 mf=7.846 |Δlin|=0.115 |Δquad|=0.233 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin B6 (MIDI 95, high): pp=6.432 mp=6.902 mf=6.888 |Δlin|=0.128 |Δquad|=0.189 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin F#7 (MIDI 102, high): pp=5.877 mp=5.862 mf=6.304 |Δlin|=0.335 |Δquad|=0.472 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola E4 (MIDI 64, low): pp=19.846 mp=20.048 mf=19.800 |Δlin|=0.237 |Δquad|=0.333 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors
- viola F4 (MIDI 65, middle): pp=16.887 mp=16.664 mf=16.821 |Δlin|=0.173 |Δquad|=0.239 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola F#4 (MIDI 66, middle): pp=17.865 mp=17.793 mf=18.148 |Δlin|=0.284 |Δquad|=0.394 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola C#5 (MIDI 73, middle): pp=13.606 mp=13.198 mf=13.242 |Δlin|=0.135 |Δquad|=0.220 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola E5 (MIDI 76, middle): pp=10.992 mp=11.153 mf=11.033 |Δlin|=0.130 |Δquad|=0.164 [REVIEW REQUIRED] mp outside pp–mf interval
- viola G5 (MIDI 79, middle): pp=10.177 mp=9.967 mf=10.066 |Δlin|=0.127 |Δquad|=0.165 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola F6 (MIDI 89, high): pp=5.551 mp=5.569 mf=5.111 |Δlin|=0.349 |Δquad|=0.492 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola G#6 (MIDI 92, high): pp=5.012 mp=5.185 mf=4.929 |Δlin|=0.235 |Δquad|=0.334 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors
- viola B6 (MIDI 95, high): pp=3.160 mp=3.464 mf=3.342 |Δlin|=0.167 |Δquad|=0.249 [REVIEW REQUIRED] mp outside pp–mf interval
- viola C7 (MIDI 96, high): pp=3.394 mp=3.239 mf=3.291 |Δlin|=0.078 |Δquad|=0.090 [REVIEW REQUIRED] mp outside pp–mf interval
- cello C3 (MIDI 48, low): pp=50.880 mp=54.662 mf=53.816 |Δlin|=1.580 |Δquad|=0.092 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors

## Model interpretation

### 1. Convex-hull departures by instrument
- Concentrated in **cello** (12 of 49 rows, 24.5%).
- **double_bass** and **cello** show the highest departure rates in low register rows.

### 2. Register concentration
- Highest absolute departure count in **high** register band (28 rows).
- Low-register string rows dominate convex-hull departures.

### 3. Non-monotonic source rows
- Non-monotonic pp/mf/ff rows: **162** of 357.
- Convex-hull departures overlapping non-monotonic rows: **34**.
- Departures are **associated** with non-monotonic anchors but also occur when mf lies between pp and ff.

### 4. Anchor geometry / uncertainty
- GPR fits only three anchors; high `gpr_std_mp` correlates with steep or non-monotonic local anchor geometry.

### 5. Reference closeness
- Mean |GPR−linear|: 0.3422; mean |GPR−quadratic|: 0.1945.
- Mean |GPR−PCHIP|: 0.3057.
- GPR is often closest to **quadratic** on average; case-by-case variation is large.

### 6. PCHIP conservatism
- PCHIP is shape-preserving on [pp, ff] and generally stays inside anchor hull for interior points.
- mp at x=4.5 is **interpolation** (not extrapolation) for PCHIP.

### 7–8. Plausibility vs artefacts
- Large GPR–linear gaps (e.g. double_bass G1) reflect Matérn smoothness with only three anchors — **model-quality review required**, not implementation failure.
- Extreme overshoot/undershoot is reproducible and concentrated in low strings.

### 9. Near-anchor collapse
- near_pp: 16; near_mf: 47.
- Few cases suggest practical anchor collapse; most mp values are distinct from pp and mf.

### 10. Future campaigns
- **method-comparison candidate**: a separate future campaign may compare PCHIP or constrained interpolation policies.
- **Do not** replace production GPR based on this diagnostic alone.

### Categories used
- acceptable behaviour: OK rows within diagnostic envelope
- benign diagnostic outlier: near-zero or mild shape quirks
- model-quality review required: convex-hull departure, large deviations, high uncertainty
- implementation failure: non-finite or negative production predictions (none found)
