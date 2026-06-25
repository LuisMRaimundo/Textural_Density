# Instrument register audit

**Instruments audited:** 28

## Pitch contract

- **manual_legacy_input:** notes[] are script pitch as written on the part
- **musicxml:** written <pitch> used directly; <transpose> recorded but not applied
- **density_lookup:** sounding_pitch (same as script pitch on input paths)
- **range_validation:** script pitch vs registry.sounding_range
- **registry_transposition_field:** metadata_only_not_applied_at_runtime

## Per-instrument summary

| ID | Family | Sounding MIDI | Transposition | Table span | Discrepancy |
|----|--------|---------------|---------------|------------|-------------|
| bombo | percussion | 28–48 | 0 (A_non_transposing) | — | no_table |
| caixa | percussion | 60–72 | 0 (A_non_transposing) | — | no_table |
| celesta | keyboard_harp | 60–96 | 0 (A_non_transposing) | — | no_table |
| clarinete | woodwinds | 50–96 | 0 (A_non_transposing) | D3–C7 (50–96) | aligned |
| clarinete_baixo | woodwinds | 34–72 | 14 (D_interval_transposing) | — | no_table |
| contrabaixo | strings | 28–72 | 0 (A_non_transposing) | E1–C5 (28–72) | aligned |
| contrafagote | woodwinds | 22–77 | 0 (A_non_transposing) | — | no_table |
| cor_anglais | woodwinds | 52–76 | 7 (D_interval_transposing) | — | no_table |
| fagote | woodwinds | 34–72 | 0 (A_non_transposing) | — | no_table |
| flauta | woodwinds | 59–98 | 0 (A_non_transposing) | B3–D7 (59–98) | aligned |
| flautim | woodwinds | 74–108 | 0 (A_non_transposing) | — | no_table |
| harpa | keyboard_harp | 23–96 | 0 (A_non_transposing) | — | no_table |
| marimba | percussion | 45–84 | 0 (A_non_transposing) | — | no_table |
| metalofone | percussion | 72–108 | 0 (A_non_transposing) | — | no_table |
| oboe | woodwinds | 58–93 | 0 (A_non_transposing) | A#3–A6 (58–93) | aligned |
| piano | keyboard_harp | 21–108 | 0 (A_non_transposing) | — | no_table |
| pratos | percussion | 60–84 | 0 (A_non_transposing) | — | no_table |
| tamtam | percussion | 24–48 | 0 (A_non_transposing) | — | no_table |
| timpanos | percussion | 36–60 | 0 (A_non_transposing) | — | no_table |
| trombone | brass | 40–72 | 0 (A_non_transposing) | — | no_table |
| trombone_baixo | brass | 34–65 | 0 (A_non_transposing) | — | no_table |
| trompa | brass | 41–77 | 7 (D_interval_transposing) | — | no_table |
| trompete | brass | 55–84 | 2 (D_interval_transposing) | — | no_table |
| tuba | brass | 28–58 | 0 (A_non_transposing) | — | no_table |
| vibrafone | percussion | 53–84 | 0 (A_non_transposing) | — | no_table |
| viola | strings | 48–96 | 0 (A_non_transposing) | C3–C7 (48–96) | aligned |
| violino | strings | 55–103 | 0 (A_non_transposing) | G3–G7 (55–103) | aligned |
| violoncelo | strings | 36–84 | 0 (A_non_transposing) | C2–C6 (36–84) | aligned |
