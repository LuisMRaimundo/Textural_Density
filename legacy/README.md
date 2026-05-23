# Legacy / proxy branches



**Removed in 3.0.0-strict-symbolic (hard removal):**



- Stevens' Law / power-law compression (`use_stevens`, `alpha`, `beta`)

- Psychoacoustic corrections (`use_psychoacoustic`, masking, roughness, loudness, Bark)

- Perceptual interval weighting (`use_perceptual_weighting`)



**Removed in 4.0.0-strict-symbolic (hard removal):**



- Combination-tone / resultant-tone analysis (`calculate_combination_tones`, `combination_tones`, `resultant_tones`, `include_resultants`, `include_combination_tones`, `virtual_tones`, `generated_tones`)

- Module `combination_tones.py` deleted



Analytical inputs containing removed keys raise `InputError`. Saved GUI/XML preferences containing those keys are stripped with a migration warning and are not passed to the calculation pipeline.



Remaining optional visualization:



| Module | Branch |

|--------|--------|

| `plot_spectrogram.py` | Symbolic spectral-density visualization from input pitches (GUI opt-in) |



SDA / Densidade Vertical is a strictly symbolic score-analysis framework. It computes analytical density indices from notated/input symbolic events and symbolic metadata only. It does not generate non-notated virtual pitches and does not implement acoustic, psychoacoustic, or perceptual modelling.


