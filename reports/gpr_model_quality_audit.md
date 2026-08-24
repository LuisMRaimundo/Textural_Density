# GPR model-quality diagnostic audit

- Repository SHA: `43cfa989ea540bed8fb0e0da8a4eddf376d16115`
- Classification: **PASS**
- Instruments: 8
- Source rows: 357
- Convex-hull departures (pp–mf): **49**
- Convex-hull departures (pp–mf–ff): **14**
- PCHIP available: True
- REVIEW REQUIRED rows: 124

> Diagnostic only. Production GPR unchanged. Linear/quadratic/PCHIP are comparison references.

## Per-instrument summary

- **bassoon**: 42 rows, hull departures=6 (14.3%), max |GPR−linear|=0.686
- **cello**: 49 rows, hull departures=6 (12.2%), max |GPR−linear|=1.330
- **clarinet**: 47 rows, hull departures=1 (2.1%), max |GPR−linear|=0.888
- **double_bass**: 45 rows, hull departures=8 (17.8%), max |GPR−linear|=1.102
- **flute**: 40 rows, hull departures=5 (12.5%), max |GPR−linear|=0.515
- **oboe**: 36 rows, hull departures=8 (22.2%), max |GPR−linear|=0.529
- **viola**: 49 rows, hull departures=9 (18.4%), max |GPR−linear|=0.629
- **violin**: 49 rows, hull departures=6 (12.2%), max |GPR−linear|=0.523

## Convex-hull departures (pp–mf)

- violin C4 (MIDI 60, low): pp=24.969 mp=24.076 mf=24.228 |Δlin|=0.337 |Δquad|=0.119 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin C#4 (MIDI 61, low): pp=23.567 mp=24.020 mf=23.995 |Δlin|=0.131 |Δquad|=0.184 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin A4 (MIDI 69, low): pp=22.034 mp=20.903 mf=21.085 |Δlin|=0.420 |Δquad|=0.121 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin G#5 (MIDI 80, middle): pp=18.060 mp=17.924 mf=18.111 |Δlin|=0.174 |Δquad|=0.229 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- violin D#6 (MIDI 87, high): pp=14.310 mp=14.593 mf=14.557 |Δlin|=0.097 |Δquad|=0.240 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin E7 (MIDI 100, high): pp=6.814 mp=6.652 mf=6.859 |Δlin|=0.196 |Δquad|=0.270 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors
- viola C#5 (MIDI 73, middle): pp=19.036 mp=19.272 mf=19.078 |Δlin|=0.205 |Δquad|=0.287 [REVIEW REQUIRED] mp outside pp–mf interval
- viola E5 (MIDI 76, middle): pp=18.010 mp=17.935 mf=18.313 |Δlin|=0.302 |Δquad|=0.424 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola G#5 (MIDI 80, high): pp=14.792 mp=15.090 mf=14.906 |Δlin|=0.212 |Δquad|=0.302 [REVIEW REQUIRED] mp outside pp–mf interval
- viola C#6 (MIDI 85, high): pp=13.236 mp=12.980 mf=13.046 |Δlin|=0.113 |Δquad|=0.151 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola E6 (MIDI 88, high): pp=12.670 mp=13.024 mf=12.871 |Δlin|=0.203 |Δquad|=0.295 [REVIEW REQUIRED] mp outside pp–mf interval
- viola F6 (MIDI 89, high): pp=9.387 mp=9.559 mf=9.443 |Δlin|=0.130 |Δquad|=0.167 [REVIEW REQUIRED] mp outside pp–mf interval
- viola F#6 (MIDI 90, high): pp=9.882 mp=10.198 mf=10.040 |Δlin|=0.198 |Δquad|=0.285 [REVIEW REQUIRED] mp outside pp–mf interval
- viola G6 (MIDI 91, high): pp=9.281 mp=9.417 mf=9.164 |Δlin|=0.224 |Δquad|=0.309 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors
- viola C7 (MIDI 96, high): pp=7.483 mp=7.227 mf=7.245 |Δlin|=0.077 |Δquad|=0.093 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- cello C2 (MIDI 36, low): pp=55.940 mp=56.461 mf=55.763 |Δlin|=0.654 |Δquad|=0.063 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- cello E2 (MIDI 40, low): pp=43.638 mp=39.499 mf=39.600 |Δlin|=1.110 |Δquad|=0.241 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello G3 (MIDI 55, middle): pp=29.856 mp=28.572 mf=28.740 |Δlin|=0.446 |Δquad|=0.126 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello G4 (MIDI 67, middle): pp=26.705 mp=27.946 mf=27.900 |Δlin|=0.344 |Δquad|=0.096 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello A4 (MIDI 69, high): pp=24.484 mp=24.190 mf=24.395 |Δlin|=0.227 |Δquad|=0.336 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor

## Top 20 |GPR−linear|

- cello B2 (MIDI 47, low): pp=39.672 mp=47.375 mf=48.168 |Δlin|=1.330 |Δquad|=0.264 [OK] non-monotonic source anchors
- cello E2 (MIDI 40, low): pp=43.638 mp=39.499 mf=39.600 |Δlin|=1.110 |Δquad|=0.241 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- double_bass A2 (MIDI 45, middle): pp=35.800 mp=37.439 mf=36.516 |Δlin|=1.102 |Δquad|=0.034 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- clarinet E3 (MIDI 52, low): pp=21.939 mp=35.960 mf=39.450 |Δlin|=0.888 |Δquad|=0.582 [OK] within expected diagnostic envelope
- cello D2 (MIDI 38, low): pp=49.338 mp=55.954 mf=56.976 |Δlin|=0.888 |Δquad|=0.210 [OK] non-monotonic source anchors
- cello D#2 (MIDI 39, low): pp=43.278 mp=50.515 mf=51.761 |Δlin|=0.875 |Δquad|=0.235 [OK] non-monotonic source anchors
- cello C3 (MIDI 48, low): pp=43.408 mp=49.236 mf=50.044 |Δlin|=0.851 |Δquad|=0.193 [OK] non-monotonic source anchors
- double_bass D#4 (MIDI 63, high): pp=22.065 mp=17.546 mf=17.068 |Δlin|=0.771 |Δquad|=0.272 [OK] non-monotonic source anchors
- bassoon F2 (MIDI 41, low): pp=46.104 mp=42.647 mf=42.410 |Δlin|=0.686 |Δquad|=0.187 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass C#3 (MIDI 49, middle): pp=28.027 mp=25.852 mf=26.008 |Δlin|=0.661 |Δquad|=0.154 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello C2 (MIDI 36, low): pp=55.940 mp=56.461 mf=55.763 |Δlin|=0.654 |Δquad|=0.063 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- viola A3 (MIDI 57, low): pp=25.629 mp=30.087 mf=30.735 |Δlin|=0.629 |Δquad|=0.170 [OK] non-monotonic source anchors
- cello F#2 (MIDI 42, low): pp=29.508 mp=34.749 mf=35.658 |Δlin|=0.628 |Δquad|=0.188 [OK] non-monotonic source anchors
- viola F#3 (MIDI 54, low): pp=32.519 mp=36.836 mf=37.448 |Δlin|=0.620 |Δquad|=0.158 [OK] non-monotonic source anchors
- cello A#2 (MIDI 46, low): pp=39.990 mp=44.211 mf=44.809 |Δlin|=0.606 |Δquad|=0.150 [OK] non-monotonic source anchors
- cello E3 (MIDI 52, low): pp=38.568 mp=44.177 mf=45.253 |Δlin|=0.595 |Δquad|=0.184 [OK] non-monotonic source anchors
- viola D#3 (MIDI 51, low): pp=38.789 mp=43.518 mf=44.328 |Δlin|=0.575 |Δquad|=0.162 [OK] non-monotonic source anchors
- double_bass A#4 (MIDI 70, high): pp=21.305 mp=23.875 mf=23.999 |Δlin|=0.550 |Δquad|=0.115 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- clarinet F3 (MIDI 53, low): pp=21.540 mp=32.636 mf=35.609 |Δlin|=0.544 |Δquad|=0.400 [OK] within expected diagnostic envelope
- viola G3 (MIDI 55, low): pp=40.863 mp=44.683 mf=45.237 |Δlin|=0.539 |Δquad|=0.140 [OK] non-monotonic source anchors

## Top 20 |GPR−quadratic|

- double_bass F#2 (MIDI 42, low): pp=28.817 mp=28.995 mf=29.647 |Δlin|=0.445 |Δquad|=0.628 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- viola G#6 (MIDI 92, high): pp=8.310 mp=8.170 mf=7.540 |Δlin|=0.438 |Δquad|=0.616 [OK] non-monotonic source anchors
- clarinet E3 (MIDI 52, low): pp=21.939 mp=35.960 mf=39.450 |Δlin|=0.888 |Δquad|=0.582 [OK] within expected diagnostic envelope
- cello A#4 (MIDI 70, high): pp=23.062 mp=22.823 mf=22.203 |Δlin|=0.405 |Δquad|=0.580 [OK] non-monotonic source anchors
- bassoon D2 (MIDI 38, low): pp=41.346 mp=41.736 mf=42.380 |Δlin|=0.386 |Δquad|=0.566 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- bassoon F#3 (MIDI 54, middle): pp=28.099 mp=28.050 mf=27.496 |Δlin|=0.403 |Δquad|=0.561 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- clarinet G6 (MIDI 91, high): pp=8.829 mp=8.705 mf=8.133 |Δlin|=0.398 |Δquad|=0.559 [OK] non-monotonic source anchors
- double_bass G#1 (MIDI 32, low): pp=30.405 mp=30.839 mf=31.432 |Δlin|=0.336 |Δquad|=0.502 [OK] non-monotonic source anchors
- flute G6 (MIDI 91, high): pp=7.611 mp=7.932 mf=8.483 |Δlin|=0.332 |Δquad|=0.486 [OK] non-monotonic source anchors
- viola G5 (MIDI 79, middle): pp=14.793 mp=15.104 mf=15.647 |Δlin|=0.330 |Δquad|=0.482 [OK] non-monotonic source anchors
- oboe A6 (MIDI 93, high): pp=8.676 mp=9.085 mf=9.649 |Δlin|=0.321 |Δquad|=0.479 [OK] non-monotonic source anchors
- cello D#5 (MIDI 75, high): pp=17.021 mp=17.479 mf=18.007 |Δlin|=0.281 |Δquad|=0.429 [OK] non-monotonic source anchors
- viola E5 (MIDI 76, middle): pp=18.010 mp=17.935 mf=18.313 |Δlin|=0.302 |Δquad|=0.424 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- bassoon E2 (MIDI 40, low): pp=43.364 mp=43.024 mf=42.531 |Δlin|=0.285 |Δquad|=0.424 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- viola A#4 (MIDI 70, middle): pp=25.492 mp=24.701 mf=24.069 |Δlin|=0.277 |Δquad|=0.417 [OK] non-monotonic source anchors
- clarinet E6 (MIDI 88, high): pp=9.978 mp=10.454 mf=10.971 |Δlin|=0.269 |Δquad|=0.413 [OK] non-monotonic source anchors
- clarinet F#6 (MIDI 90, high): pp=9.016 mp=8.976 mf=8.570 |Δlin|=0.294 |Δquad|=0.410 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- bassoon A#4 (MIDI 70, high): pp=19.190 mp=19.360 mf=19.033 |Δlin|=0.288 |Δquad|=0.409 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- clarinet F3 (MIDI 53, low): pp=21.540 mp=32.636 mf=35.609 |Δlin|=0.544 |Δquad|=0.400 [OK] within expected diagnostic envelope
- bassoon C#4 (MIDI 61, middle): pp=18.712 mp=18.939 mf=18.647 |Δlin|=0.276 |Δquad|=0.396 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors

## Top 20 |GPR−PCHIP|

- clarinet E3 (MIDI 52, low): pp=21.939 mp=35.960 mf=39.450 |Δlin|=0.888 |Δquad|=0.582 [OK] within expected diagnostic envelope
- double_bass A2 (MIDI 45, middle): pp=35.800 mp=37.439 mf=36.516 |Δlin|=1.102 |Δquad|=0.034 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- clarinet F3 (MIDI 53, low): pp=21.540 mp=32.636 mf=35.609 |Δlin|=0.544 |Δquad|=0.400 [OK] within expected diagnostic envelope
- flute C#4 (MIDI 61, low): pp=19.099 mp=27.448 mf=29.545 |Δlin|=0.515 |Δquad|=0.312 [OK] within expected diagnostic envelope
- clarinet D#3 (MIDI 51, low): pp=24.310 mp=35.510 mf=38.563 |Δlin|=0.510 |Δquad|=0.376 [OK] within expected diagnostic envelope
- clarinet E4 (MIDI 64, low): pp=16.122 mp=22.450 mf=23.981 |Δlin|=0.434 |Δquad|=0.248 [OK] within expected diagnostic envelope
- clarinet G4 (MIDI 67, middle): pp=15.708 mp=21.285 mf=22.510 |Δlin|=0.475 |Δquad|=0.230 [OK] non-monotonic source anchors
- double_bass B1 (MIDI 35, low): pp=41.341 mp=47.375 mf=48.741 |Δlin|=0.484 |Δquad|=0.183 [OK] within expected diagnostic envelope
- clarinet A3 (MIDI 57, low): pp=16.938 mp=24.360 mf=26.263 |Δlin|=0.428 |Δquad|=0.279 [OK] within expected diagnostic envelope
- cello C2 (MIDI 36, low): pp=55.940 mp=56.461 mf=55.763 |Δlin|=0.654 |Δquad|=0.063 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- double_bass F#2 (MIDI 42, low): pp=28.817 mp=28.995 mf=29.647 |Δlin|=0.445 |Δquad|=0.628 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- cello D#2 (MIDI 39, low): pp=43.278 mp=50.515 mf=51.761 |Δlin|=0.875 |Δquad|=0.235 [OK] non-monotonic source anchors
- flute C4 (MIDI 60, low): pp=17.809 mp=26.538 mf=28.908 |Δlin|=0.405 |Δquad|=0.312 [OK] within expected diagnostic envelope
- viola G#6 (MIDI 92, high): pp=8.310 mp=8.170 mf=7.540 |Δlin|=0.438 |Δquad|=0.616 [OK] non-monotonic source anchors
- flute A4 (MIDI 69, low): pp=17.942 mp=23.225 mf=24.489 |Δlin|=0.374 |Δquad|=0.201 [OK] within expected diagnostic envelope
- bassoon D2 (MIDI 38, low): pp=41.346 mp=41.736 mf=42.380 |Δlin|=0.386 |Δquad|=0.566 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- cello A#4 (MIDI 70, high): pp=23.062 mp=22.823 mf=22.203 |Δlin|=0.405 |Δquad|=0.580 [OK] non-monotonic source anchors
- clarinet D#4 (MIDI 63, low): pp=15.720 mp=21.947 mf=23.532 |Δlin|=0.368 |Δquad|=0.237 [OK] within expected diagnostic envelope
- flute D#4 (MIDI 63, low): pp=16.834 mp=24.824 mf=26.986 |Δlin|=0.376 |Δquad|=0.287 [OK] within expected diagnostic envelope
- cello E3 (MIDI 52, low): pp=38.568 mp=44.177 mf=45.253 |Δlin|=0.595 |Δquad|=0.184 [OK] non-monotonic source anchors

## Top 20 GPR std (mp)

- clarinet E3 (MIDI 52, low): pp=21.939 mp=35.960 mf=39.450 |Δlin|=0.888 |Δquad|=0.582 [OK] within expected diagnostic envelope
- cello E2 (MIDI 40, low): pp=43.638 mp=39.499 mf=39.600 |Δlin|=1.110 |Δquad|=0.241 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello B2 (MIDI 47, low): pp=39.672 mp=47.375 mf=48.168 |Δlin|=1.330 |Δquad|=0.264 [OK] non-monotonic source anchors
- double_bass D#4 (MIDI 63, high): pp=22.065 mp=17.546 mf=17.068 |Δlin|=0.771 |Δquad|=0.272 [OK] non-monotonic source anchors
- double_bass A2 (MIDI 45, middle): pp=35.800 mp=37.439 mf=36.516 |Δlin|=1.102 |Δquad|=0.034 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; non-monotonic source anchors
- clarinet F3 (MIDI 53, low): pp=21.540 mp=32.636 mf=35.609 |Δlin|=0.544 |Δquad|=0.400 [OK] within expected diagnostic envelope
- clarinet D#3 (MIDI 51, low): pp=24.310 mp=35.510 mf=38.563 |Δlin|=0.510 |Δquad|=0.376 [OK] within expected diagnostic envelope
- cello D#2 (MIDI 39, low): pp=43.278 mp=50.515 mf=51.761 |Δlin|=0.875 |Δquad|=0.235 [OK] non-monotonic source anchors
- cello D2 (MIDI 38, low): pp=49.338 mp=55.954 mf=56.976 |Δlin|=0.888 |Δquad|=0.210 [OK] non-monotonic source anchors
- cello C3 (MIDI 48, low): pp=43.408 mp=49.236 mf=50.044 |Δlin|=0.851 |Δquad|=0.193 [OK] non-monotonic source anchors
- bassoon F2 (MIDI 41, low): pp=46.104 mp=42.647 mf=42.410 |Δlin|=0.686 |Δquad|=0.187 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass C#3 (MIDI 49, middle): pp=28.027 mp=25.852 mf=26.008 |Δlin|=0.661 |Δquad|=0.154 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- flute C#4 (MIDI 61, low): pp=19.099 mp=27.448 mf=29.545 |Δlin|=0.515 |Δquad|=0.312 [OK] within expected diagnostic envelope
- flute C4 (MIDI 60, low): pp=17.809 mp=26.538 mf=28.908 |Δlin|=0.405 |Δquad|=0.312 [OK] within expected diagnostic envelope
- oboe E4 (MIDI 64, low): pp=28.715 mp=24.846 mf=24.263 |Δlin|=0.529 |Δquad|=0.206 [OK] non-monotonic source anchors
- flute D#4 (MIDI 63, low): pp=16.834 mp=24.824 mf=26.986 |Δlin|=0.376 |Δquad|=0.287 [OK] within expected diagnostic envelope
- clarinet A3 (MIDI 57, low): pp=16.938 mp=24.360 mf=26.263 |Δlin|=0.428 |Δquad|=0.279 [OK] within expected diagnostic envelope
- cello F#2 (MIDI 42, low): pp=29.508 mp=34.749 mf=35.658 |Δlin|=0.628 |Δquad|=0.188 [OK] non-monotonic source anchors
- viola A3 (MIDI 57, low): pp=25.629 mp=30.087 mf=30.735 |Δlin|=0.629 |Δquad|=0.170 [OK] non-monotonic source anchors
- clarinet E4 (MIDI 64, low): pp=16.122 mp=22.450 mf=23.981 |Δlin|=0.434 |Δquad|=0.248 [OK] within expected diagnostic envelope

## Near pp

- violin G#5 (MIDI 80, middle): pp=18.060 mp=17.924 mf=18.111 |Δlin|=0.174 |Δquad|=0.229 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola F3 (MIDI 53, low): pp=26.855 mp=26.935 mf=27.555 |Δlin|=0.445 |Δquad|=0.090 [REVIEW REQUIRED] mp near pp anchor
- viola G#3 (MIDI 56, low): pp=31.180 mp=31.254 mf=31.309 |Δlin|=0.023 |Δquad|=0.175 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- viola E5 (MIDI 76, middle): pp=18.010 mp=17.935 mf=18.313 |Δlin|=0.302 |Δquad|=0.424 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola F5 (MIDI 77, middle): pp=16.652 mp=16.671 mf=16.802 |Δlin|=0.093 |Δquad|=0.129 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- cello C2 (MIDI 36, low): pp=55.940 mp=56.461 mf=55.763 |Δlin|=0.654 |Δquad|=0.063 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- cello C#4 (MIDI 61, middle): pp=30.852 mp=30.598 mf=30.218 |Δlin|=0.222 |Δquad|=0.329 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- cello B4 (MIDI 71, high): pp=24.663 mp=24.551 mf=24.189 |Δlin|=0.243 |Δquad|=0.346 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- cello F5 (MIDI 77, high): pp=16.721 mp=16.888 mf=17.011 |Δlin|=0.051 |Δquad|=0.085 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- cello B5 (MIDI 83, high): pp=12.618 mp=12.653 mf=12.947 |Δlin|=0.212 |Δquad|=0.294 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- double_bass A1 (MIDI 33, low): pp=32.494 mp=32.676 mf=32.588 |Δlin|=0.112 |Δquad|=0.138 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; mp near mf anchor
- double_bass C2 (MIDI 36, low): pp=34.332 mp=34.295 mf=34.528 |Δlin|=0.184 |Δquad|=0.123 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor; mp near mf anchor
- double_bass C#2 (MIDI 37, low): pp=27.704 mp=27.747 mf=27.530 |Δlin|=0.174 |Δquad|=0.236 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- double_bass D#2 (MIDI 39, low): pp=30.738 mp=30.587 mf=30.263 |Δlin|=0.205 |Δquad|=0.296 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- double_bass F#2 (MIDI 42, low): pp=28.817 mp=28.995 mf=29.647 |Δlin|=0.445 |Δquad|=0.628 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- double_bass G2 (MIDI 43, middle): pp=27.016 mp=26.934 mf=26.551 |Δlin|=0.267 |Δquad|=0.375 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- double_bass G#2 (MIDI 44, middle): pp=22.323 mp=22.157 mf=22.468 |Δlin|=0.274 |Δquad|=0.391 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- flute C#6 (MIDI 85, high): pp=10.583 mp=10.630 mf=10.634 |Δlin|=0.008 |Δquad|=0.008 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- flute E6 (MIDI 88, high): pp=10.016 mp=10.086 mf=10.218 |Δlin|=0.082 |Δquad|=0.119 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- flute C#7 (MIDI 97, high): pp=6.887 mp=6.880 mf=6.682 |Δlin|=0.147 |Δquad|=0.204 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- clarinet F#6 (MIDI 90, high): pp=9.016 mp=8.976 mf=8.570 |Δlin|=0.294 |Δquad|=0.410 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- oboe G4 (MIDI 67, low): pp=27.900 mp=28.165 mf=28.578 |Δlin|=0.243 |Δquad|=0.359 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- oboe G#4 (MIDI 68, low): pp=28.171 mp=28.351 mf=28.316 |Δlin|=0.071 |Δquad|=0.139 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- oboe A4 (MIDI 69, low): pp=24.344 mp=24.222 mf=24.305 |Δlin|=0.093 |Δquad|=0.229 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; mp near mf anchor
- oboe G5 (MIDI 79, middle): pp=14.228 mp=14.119 mf=14.109 |Δlin|=0.020 |Δquad|=0.176 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- bassoon A#1 (MIDI 34, low): pp=74.360 mp=74.389 mf=74.304 |Δlin|=0.071 |Δquad|=0.144 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor; mp near mf anchor
- bassoon B1 (MIDI 35, low): pp=74.832 mp=74.352 mf=73.858 |Δlin|=0.251 |Δquad|=0.386 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- bassoon D2 (MIDI 38, low): pp=41.346 mp=41.736 mf=42.380 |Δlin|=0.386 |Δquad|=0.566 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- bassoon E2 (MIDI 40, low): pp=43.364 mp=43.024 mf=42.531 |Δlin|=0.285 |Δquad|=0.424 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- bassoon E3 (MIDI 52, middle): pp=24.664 mp=24.884 mf=25.410 |Δlin|=0.340 |Δquad|=0.092 [REVIEW REQUIRED] mp near pp anchor
- bassoon F#3 (MIDI 54, middle): pp=28.099 mp=28.050 mf=27.496 |Δlin|=0.403 |Δquad|=0.561 [REVIEW REQUIRED] mp near pp anchor; non-monotonic source anchors
- bassoon E4 (MIDI 64, high): pp=18.692 mp=18.556 mf=18.391 |Δlin|=0.090 |Δquad|=0.137 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- bassoon A#4 (MIDI 70, high): pp=19.190 mp=19.360 mf=19.033 |Δlin|=0.288 |Δquad|=0.409 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors

## Near mf

- violin G#3 (MIDI 56, low): pp=26.670 mp=27.718 mf=27.937 |Δlin|=0.097 |Δquad|=0.158 [REVIEW REQUIRED] mp near mf anchor
- violin B3 (MIDI 59, low): pp=35.052 mp=32.547 mf=32.236 |Δlin|=0.393 |Δquad|=0.153 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- violin C4 (MIDI 60, low): pp=24.969 mp=24.076 mf=24.228 |Δlin|=0.337 |Δquad|=0.119 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin C#4 (MIDI 61, low): pp=23.567 mp=24.020 mf=23.995 |Δlin|=0.131 |Δquad|=0.184 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin G#4 (MIDI 68, low): pp=23.874 mp=24.424 mf=24.434 |Δlin|=0.130 |Δquad|=0.258 [REVIEW REQUIRED] mp near mf anchor
- violin A4 (MIDI 69, low): pp=22.034 mp=20.903 mf=21.085 |Δlin|=0.420 |Δquad|=0.121 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin B4 (MIDI 71, low): pp=27.592 mp=28.380 mf=28.542 |Δlin|=0.076 |Δquad|=0.147 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- violin D5 (MIDI 74, middle): pp=20.666 mp=21.351 mf=21.402 |Δlin|=0.133 |Δquad|=0.245 [REVIEW REQUIRED] mp near mf anchor
- violin A#5 (MIDI 82, middle): pp=16.110 mp=16.565 mf=16.610 |Δlin|=0.080 |Δquad|=0.139 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- violin D6 (MIDI 86, middle): pp=13.319 mp=13.800 mf=13.834 |Δlin|=0.095 |Δquad|=0.131 [REVIEW REQUIRED] mp near mf anchor
- violin D#6 (MIDI 87, high): pp=14.310 mp=14.593 mf=14.557 |Δlin|=0.097 |Δquad|=0.240 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin G6 (MIDI 91, high): pp=10.117 mp=10.254 mf=10.280 |Δlin|=0.014 |Δquad|=0.008 [REVIEW REQUIRED] mp near mf anchor
- viola G#3 (MIDI 56, low): pp=31.180 mp=31.254 mf=31.309 |Δlin|=0.023 |Δquad|=0.175 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- viola D#4 (MIDI 63, low): pp=25.058 mp=25.864 mf=25.965 |Δlin|=0.126 |Δquad|=0.194 [REVIEW REQUIRED] mp near mf anchor
- viola F#4 (MIDI 66, middle): pp=25.874 mp=25.550 mf=25.398 |Δlin|=0.033 |Δquad|=0.067 [REVIEW REQUIRED] mp near mf anchor
- viola G#4 (MIDI 68, middle): pp=24.768 mp=24.481 mf=24.240 |Δlin|=0.108 |Δquad|=0.177 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- viola A4 (MIDI 69, middle): pp=24.760 mp=23.909 mf=23.720 |Δlin|=0.071 |Δquad|=0.166 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- viola F5 (MIDI 77, middle): pp=16.652 mp=16.671 mf=16.802 |Δlin|=0.093 |Δquad|=0.129 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- viola A5 (MIDI 81, high): pp=14.042 mp=13.874 mf=13.787 |Δlin|=0.024 |Δquad|=0.049 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- viola B5 (MIDI 83, high): pp=15.871 mp=15.492 mf=15.369 |Δlin|=0.003 |Δquad|=0.009 [REVIEW REQUIRED] mp near mf anchor
- viola C#6 (MIDI 85, high): pp=13.236 mp=12.980 mf=13.046 |Δlin|=0.113 |Δquad|=0.151 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola C7 (MIDI 96, high): pp=7.483 mp=7.227 mf=7.245 |Δlin|=0.077 |Δquad|=0.093 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- cello E2 (MIDI 40, low): pp=43.638 mp=39.499 mf=39.600 |Δlin|=1.110 |Δquad|=0.241 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello G2 (MIDI 43, low): pp=33.503 mp=35.525 mf=35.663 |Δlin|=0.403 |Δquad|=0.108 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello G#2 (MIDI 44, low): pp=37.719 mp=38.224 mf=38.259 |Δlin|=0.100 |Δquad|=0.136 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello G3 (MIDI 55, middle): pp=29.856 mp=28.572 mf=28.740 |Δlin|=0.446 |Δquad|=0.126 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello B3 (MIDI 59, middle): pp=31.007 mp=32.759 mf=33.043 |Δlin|=0.225 |Δquad|=0.122 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello C4 (MIDI 60, middle): pp=32.133 mp=29.878 mf=29.713 |Δlin|=0.440 |Δquad|=0.150 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello D4 (MIDI 62, middle): pp=32.167 mp=32.591 mf=32.600 |Δlin|=0.100 |Δquad|=0.134 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello G4 (MIDI 67, middle): pp=26.705 mp=27.946 mf=27.900 |Δlin|=0.344 |Δquad|=0.096 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello A4 (MIDI 69, high): pp=24.484 mp=24.190 mf=24.395 |Δlin|=0.227 |Δquad|=0.336 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- cello C#5 (MIDI 73, high): pp=17.604 mp=18.558 mf=18.688 |Δlin|=0.142 |Δquad|=0.128 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello D5 (MIDI 74, high): pp=20.732 mp=20.337 mf=20.250 |Δlin|=0.034 |Δquad|=0.039 [REVIEW REQUIRED] mp near mf anchor
- cello E5 (MIDI 76, high): pp=18.500 mp=19.857 mf=19.791 |Δlin|=0.388 |Δquad|=0.091 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello F5 (MIDI 77, high): pp=16.721 mp=16.888 mf=17.011 |Δlin|=0.051 |Δquad|=0.085 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- cello F#5 (MIDI 78, high): pp=16.902 mp=17.763 mf=17.924 |Δlin|=0.094 |Δquad|=0.141 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- cello G#5 (MIDI 80, high): pp=15.708 mp=15.285 mf=15.157 |Δlin|=0.010 |Δquad|=0.004 [REVIEW REQUIRED] mp near mf anchor
- cello A#5 (MIDI 82, high): pp=15.660 mp=15.410 mf=15.311 |Δlin|=0.012 |Δquad|=0.147 [REVIEW REQUIRED] mp near mf anchor
- cello C6 (MIDI 84, high): pp=13.207 mp=12.958 mf=12.947 |Δlin|=0.054 |Δquad|=0.057 [REVIEW REQUIRED] mp near mf anchor
- double_bass A1 (MIDI 33, low): pp=32.494 mp=32.676 mf=32.588 |Δlin|=0.112 |Δquad|=0.138 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; mp near mf anchor
- double_bass C2 (MIDI 36, low): pp=34.332 mp=34.295 mf=34.528 |Δlin|=0.184 |Δquad|=0.123 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor; mp near mf anchor
- double_bass C#2 (MIDI 37, low): pp=27.704 mp=27.747 mf=27.530 |Δlin|=0.174 |Δquad|=0.236 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- double_bass D2 (MIDI 38, low): pp=29.982 mp=30.595 mf=30.738 |Δlin|=0.047 |Δquad|=0.200 [REVIEW REQUIRED] mp near mf anchor
- double_bass A#2 (MIDI 46, middle): pp=28.708 mp=29.832 mf=29.613 |Δlin|=0.445 |Δquad|=0.081 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- double_bass C#3 (MIDI 49, middle): pp=28.027 mp=25.852 mf=26.008 |Δlin|=0.661 |Δquad|=0.154 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- double_bass F3 (MIDI 53, middle): pp=30.230 mp=32.806 mf=33.036 |Δlin|=0.471 |Δquad|=0.117 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass F#3 (MIDI 54, middle): pp=23.582 mp=24.280 mf=24.483 |Δlin|=0.023 |Δquad|=0.024 [REVIEW REQUIRED] mp near mf anchor
- double_bass A3 (MIDI 57, middle): pp=21.818 mp=24.045 mf=24.246 |Δlin|=0.406 |Δquad|=0.115 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass A#3 (MIDI 58, high): pp=20.330 mp=20.950 mf=21.091 |Δlin|=0.049 |Δquad|=0.064 [REVIEW REQUIRED] mp near mf anchor
- double_bass F#4 (MIDI 66, high): pp=24.351 mp=22.094 mf=21.922 |Δlin|=0.435 |Δquad|=0.153 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass A#4 (MIDI 70, high): pp=21.305 mp=23.875 mf=23.999 |Δlin|=0.550 |Δquad|=0.115 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- double_bass B4 (MIDI 71, high): pp=17.729 mp=18.219 mf=18.128 |Δlin|=0.191 |Δquad|=0.299 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- flute C#6 (MIDI 85, high): pp=10.583 mp=10.630 mf=10.634 |Δlin|=0.008 |Δquad|=0.008 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor
- flute D#6 (MIDI 87, high): pp=10.025 mp=10.320 mf=10.391 |Δlin|=0.020 |Δquad|=0.013 [REVIEW REQUIRED] mp near mf anchor
- flute F6 (MIDI 89, high): pp=7.903 mp=7.995 mf=7.986 |Δlin|=0.030 |Δquad|=0.034 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- flute G#6 (MIDI 92, high): pp=7.355 mp=7.615 mf=7.688 |Δlin|=0.011 |Δquad|=0.006 [REVIEW REQUIRED] mp near mf anchor
- flute A#6 (MIDI 94, high): pp=7.169 mp=7.309 mf=7.356 |Δlin|=0.000 |Δquad|=0.012 [REVIEW REQUIRED] mp near mf anchor
- flute C7 (MIDI 96, high): pp=6.562 mp=6.774 mf=6.758 |Δlin|=0.065 |Δquad|=0.072 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- oboe A#3 (MIDI 58, low): pp=34.650 mp=35.082 mf=35.298 |Δlin|=0.054 |Δquad|=0.091 [REVIEW REQUIRED] mp near mf anchor
- oboe B3 (MIDI 59, low): pp=32.447 mp=33.253 mf=33.408 |Δlin|=0.085 |Δquad|=0.144 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- oboe C#4 (MIDI 61, low): pp=32.433 mp=30.521 mf=30.414 |Δlin|=0.398 |Δquad|=0.141 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- oboe D4 (MIDI 62, low): pp=31.289 mp=31.615 mf=31.540 |Δlin|=0.138 |Δquad|=0.119 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- oboe F#4 (MIDI 66, low): pp=26.658 mp=26.256 mf=26.134 |Δlin|=0.009 |Δquad|=0.189 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- oboe G#4 (MIDI 68, low): pp=28.171 mp=28.351 mf=28.316 |Δlin|=0.071 |Δquad|=0.139 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- oboe A4 (MIDI 69, low): pp=24.344 mp=24.222 mf=24.305 |Δlin|=0.093 |Δquad|=0.229 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; mp near mf anchor
- oboe G5 (MIDI 79, middle): pp=14.228 mp=14.119 mf=14.109 |Δlin|=0.020 |Δquad|=0.176 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- oboe A5 (MIDI 81, middle): pp=14.436 mp=14.738 mf=14.699 |Δlin|=0.105 |Δquad|=0.139 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- oboe A#5 (MIDI 82, high): pp=13.257 mp=13.707 mf=13.811 |Δlin|=0.034 |Δquad|=0.039 [REVIEW REQUIRED] mp near mf anchor
- oboe C6 (MIDI 84, high): pp=13.381 mp=13.609 mf=13.553 |Δlin|=0.099 |Δquad|=0.126 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- oboe D6 (MIDI 86, high): pp=12.006 mp=12.286 mf=12.223 |Δlin|=0.118 |Δquad|=0.159 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- oboe E6 (MIDI 88, high): pp=10.180 mp=10.548 mf=10.469 |Δlin|=0.152 |Δquad|=0.274 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- oboe F#6 (MIDI 90, high): pp=11.223 mp=10.905 mf=10.805 |Δlin|=0.004 |Δquad|=0.188 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- bassoon A#1 (MIDI 34, low): pp=74.360 mp=74.389 mf=74.304 |Δlin|=0.071 |Δquad|=0.144 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor; mp near mf anchor
- bassoon B1 (MIDI 35, low): pp=74.832 mp=74.352 mf=73.858 |Δlin|=0.251 |Δquad|=0.386 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- bassoon C2 (MIDI 36, low): pp=64.591 mp=62.843 mf=62.779 |Δlin|=0.389 |Δquad|=0.133 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- bassoon F2 (MIDI 41, low): pp=46.104 mp=42.647 mf=42.410 |Δlin|=0.686 |Δquad|=0.187 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- bassoon F#2 (MIDI 42, low): pp=41.498 mp=42.399 mf=42.506 |Δlin|=0.146 |Δquad|=0.231 [REVIEW REQUIRED] mp near mf anchor
- bassoon G2 (MIDI 43, low): pp=36.259 mp=35.772 mf=35.670 |Δlin|=0.046 |Δquad|=0.173 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- bassoon G#2 (MIDI 44, low): pp=32.378 mp=30.701 mf=30.502 |Δlin|=0.270 |Δquad|=0.139 [REVIEW REQUIRED] mp near mf anchor; non-monotonic source anchors
- bassoon A2 (MIDI 45, low): pp=33.192 mp=33.682 mf=33.916 |Δlin|=0.053 |Δquad|=0.153 [REVIEW REQUIRED] mp near mf anchor
- bassoon B2 (MIDI 47, low): pp=30.639 mp=31.505 mf=31.729 |Δlin|=0.048 |Δquad|=0.066 [REVIEW REQUIRED] mp near mf anchor
- bassoon F3 (MIDI 53, middle): pp=30.592 mp=31.237 mf=31.483 |Δlin|=0.024 |Δquad|=0.161 [REVIEW REQUIRED] mp near mf anchor
- bassoon B3 (MIDI 59, middle): pp=17.235 mp=17.737 mf=17.793 |Δlin|=0.083 |Δquad|=0.113 [REVIEW REQUIRED] mp near mf anchor
- bassoon C4 (MIDI 60, middle): pp=19.462 mp=20.119 mf=20.139 |Δlin|=0.149 |Δquad|=0.228 [REVIEW REQUIRED] mp near mf anchor
- bassoon D4 (MIDI 62, high): pp=18.357 mp=18.602 mf=18.501 |Δlin|=0.137 |Δquad|=0.185 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- bassoon E4 (MIDI 64, high): pp=18.692 mp=18.556 mf=18.391 |Δlin|=0.090 |Δquad|=0.137 [REVIEW REQUIRED] mp near pp anchor; mp near mf anchor; non-monotonic source anchors
- bassoon B4 (MIDI 71, high): pp=17.577 mp=18.134 mf=18.180 |Δlin|=0.104 |Δquad|=0.147 [REVIEW REQUIRED] mp near mf anchor
- bassoon C5 (MIDI 72, high): pp=14.268 mp=14.575 mf=14.576 |Δlin|=0.076 |Δquad|=0.097 [REVIEW REQUIRED] mp near mf anchor
- bassoon D5 (MIDI 74, high): pp=14.368 mp=14.749 mf=14.665 |Δlin|=0.159 |Δquad|=0.225 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- bassoon D#5 (MIDI 75, high): pp=12.224 mp=12.069 mf=12.184 |Δlin|=0.125 |Δquad|=0.156 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor

## Outside pp–mf

- violin C4 (MIDI 60, low): pp=24.969 mp=24.076 mf=24.228 |Δlin|=0.337 |Δquad|=0.119 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin C#4 (MIDI 61, low): pp=23.567 mp=24.020 mf=23.995 |Δlin|=0.131 |Δquad|=0.184 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin A4 (MIDI 69, low): pp=22.034 mp=20.903 mf=21.085 |Δlin|=0.420 |Δquad|=0.121 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- violin G#5 (MIDI 80, middle): pp=18.060 mp=17.924 mf=18.111 |Δlin|=0.174 |Δquad|=0.229 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- violin D#6 (MIDI 87, high): pp=14.310 mp=14.593 mf=14.557 |Δlin|=0.097 |Δquad|=0.240 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- violin E7 (MIDI 100, high): pp=6.814 mp=6.652 mf=6.859 |Δlin|=0.196 |Δquad|=0.270 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors
- viola C#5 (MIDI 73, middle): pp=19.036 mp=19.272 mf=19.078 |Δlin|=0.205 |Δquad|=0.287 [REVIEW REQUIRED] mp outside pp–mf interval
- viola E5 (MIDI 76, middle): pp=18.010 mp=17.935 mf=18.313 |Δlin|=0.302 |Δquad|=0.424 [REVIEW REQUIRED] mp outside pp–mf interval; mp near pp anchor; non-monotonic source anchors
- viola G#5 (MIDI 80, high): pp=14.792 mp=15.090 mf=14.906 |Δlin|=0.212 |Δquad|=0.302 [REVIEW REQUIRED] mp outside pp–mf interval
- viola C#6 (MIDI 85, high): pp=13.236 mp=12.980 mf=13.046 |Δlin|=0.113 |Δquad|=0.151 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- viola E6 (MIDI 88, high): pp=12.670 mp=13.024 mf=12.871 |Δlin|=0.203 |Δquad|=0.295 [REVIEW REQUIRED] mp outside pp–mf interval
- viola F6 (MIDI 89, high): pp=9.387 mp=9.559 mf=9.443 |Δlin|=0.130 |Δquad|=0.167 [REVIEW REQUIRED] mp outside pp–mf interval
- viola F#6 (MIDI 90, high): pp=9.882 mp=10.198 mf=10.040 |Δlin|=0.198 |Δquad|=0.285 [REVIEW REQUIRED] mp outside pp–mf interval
- viola G6 (MIDI 91, high): pp=9.281 mp=9.417 mf=9.164 |Δlin|=0.224 |Δquad|=0.309 [REVIEW REQUIRED] mp outside pp–mf interval; non-monotonic source anchors
- viola C7 (MIDI 96, high): pp=7.483 mp=7.227 mf=7.245 |Δlin|=0.077 |Δquad|=0.093 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor
- cello C2 (MIDI 36, low): pp=55.940 mp=56.461 mf=55.763 |Δlin|=0.654 |Δquad|=0.063 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near pp anchor
- cello E2 (MIDI 40, low): pp=43.638 mp=39.499 mf=39.600 |Δlin|=1.110 |Δquad|=0.241 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello G3 (MIDI 55, middle): pp=29.856 mp=28.572 mf=28.740 |Δlin|=0.446 |Δquad|=0.126 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello G4 (MIDI 67, middle): pp=26.705 mp=27.946 mf=27.900 |Δlin|=0.344 |Δquad|=0.096 [REVIEW REQUIRED] mp outside pp–mf interval; mp outside pp–mf–ff hull; mp near mf anchor; non-monotonic source anchors
- cello A4 (MIDI 69, high): pp=24.484 mp=24.190 mf=24.395 |Δlin|=0.227 |Δquad|=0.336 [REVIEW REQUIRED] mp outside pp–mf interval; mp near mf anchor

## Model interpretation

### 1. Convex-hull departures by instrument
- Concentrated in **viola** (9 of 49 rows, 18.4%).
- **double_bass** and **cello** show the highest departure rates in low register rows.

### 2. Register concentration
- Highest absolute departure count in **high** register band (24 rows).
- Low-register string rows dominate convex-hull departures.

### 3. Non-monotonic source rows
- Non-monotonic pp/mf/ff rows: **160** of 357.
- Convex-hull departures overlapping non-monotonic rows: **20**.
- Departures are **associated** with non-monotonic anchors but also occur when mf lies between pp and ff.

### 4. Anchor geometry / uncertainty
- GPR fits only three anchors; high `gpr_std_mp` correlates with steep or non-monotonic local anchor geometry.

### 5. Reference closeness
- Mean |GPR−linear|: 0.1906; mean |GPR−quadratic|: 0.1781.
- Mean |GPR−PCHIP|: 0.2260.
- GPR is often closest to **quadratic** on average; case-by-case variation is large.

### 6. PCHIP conservatism
- PCHIP is shape-preserving on [pp, ff] and generally stays inside anchor hull for interior points.
- mp at x=4.5 is **interpolation** (not extrapolation) for PCHIP.

### 7–8. Plausibility vs artefacts
- Large GPR–linear gaps (e.g. double_bass G1) reflect Matérn smoothness with only three anchors — **model-quality review required**, not implementation failure.
- Extreme overshoot/undershoot is reproducible and concentrated in low strings.

### 9. Near-anchor collapse
- near_pp: 33; near_mf: 90.
- Few cases suggest practical anchor collapse; most mp values are distinct from pp and mf.

### 10. Future campaigns
- **method-comparison candidate**: a separate future campaign may compare PCHIP or constrained interpolation policies.
- **Do not** replace production GPR based on this diagnostic alone.

### Categories used
- acceptable behaviour: OK rows within diagnostic envelope
- benign diagnostic outlier: near-zero or mild shape quirks
- model-quality review required: convex-hull departure, large deviations, high uncertainty
- implementation failure: non-finite or negative production predictions (none found)
