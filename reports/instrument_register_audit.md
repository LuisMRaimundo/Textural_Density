# Instrument register audit

**Instruments audited:** 42

## Pitch contract

- **manual_legacy_input:** notes[] are sounding/concert pitch; registry transposition is not applied
- **musicxml:** written <pitch> converted via <transpose> once before validation and lookup
- **density_lookup:** sounding_pitch (concert pitch after MusicXML transpose when applicable)
- **range_validation:** sounding/concert pitch vs registry.sounding_range
- **registry_transposition_field:** metadata_only_not_applied_at_runtime
- **spectral_data_tables:** sounding/concert pitch keys only

## Per-instrument summary

| ID | Family | Sounding MIDI | Transposition | Table span | Discrepancy |
|----|--------|---------------|---------------|------------|-------------|
| bombo | percussion | 28–48 | 0 (A_non_transposing) | D2–D2 (38–38) | OK_registry_covers_table |
| caixa | percussion | 60–72 | 0 (A_non_transposing) | — | no_table |
| celesta | keyboard_harp | 60–96 | 0 (A_non_transposing) | — | no_table |
| clarinete | woodwinds | 50–96 | 0 (A_non_transposing) | D3–C7 (50–96) | aligned |
| clarinete_baixo | woodwinds | 34–82 | 14 (D_interval_transposing) | C#2–A#5 (37–82) | OK_registry_covers_table |
| contrabaixo | strings | 28–72 | 0 (A_non_transposing) | E1–C5 (28–72) | aligned |
| contrabaixo_harm | strings | 52–91 | 0 (A_non_transposing) | E3–G6 (52–91) | aligned |
| contrabaixo_sordina | strings | 28–72 | 0 (A_non_transposing) | E1–G4 (28–67) | OK_registry_covers_table |
| contrabaixo_sul_ponticello | strings | 28–72 | 0 (A_non_transposing) | E1–G4 (28–67) | OK_registry_covers_table |
| contrafagote | woodwinds | 22–77 | 0 (A_non_transposing) | A#1–D#5 (34–75) | OK_registry_covers_table |
| cor_anglais | woodwinds | 52–92 | 7 (D_interval_transposing) | A#3–G#6 (58–92) | OK_registry_covers_table |
| fagote | woodwinds | 34–75 | 0 (A_non_transposing) | A#1–D#5 (34–75) | aligned |
| flauta | woodwinds | 59–98 | 0 (A_non_transposing) | B3–D7 (59–98) | aligned |
| flautim | woodwinds | 59–108 | 0 (A_non_transposing) | B3–D7 (59–98) | OK_registry_covers_table |
| gongo | percussion | 36–60 | 0 (A_non_transposing) | C3–C3 (48–48) | OK_registry_covers_table |
| harpa | keyboard_harp | 23–96 | 0 (A_non_transposing) | — | no_table |
| marimba | percussion | 45–84 | 0 (A_non_transposing) | — | no_table |
| metalofone | percussion | 72–108 | 0 (A_non_transposing) | — | no_table |
| oboe | woodwinds | 58–93 | 0 (A_non_transposing) | A#3–A6 (58–93) | aligned |
| piano | keyboard_harp | 21–108 | 0 (A_non_transposing) | — | no_table |
| pratos | percussion | 60–84 | 0 (A_non_transposing) | C5–C5 (72–72) | OK_registry_covers_table |
| tamtam | percussion | 24–48 | 0 (A_non_transposing) | C2–C2 (36–36) | OK_registry_covers_table |
| timpanos | percussion | 36–60 | 0 (A_non_transposing) | — | no_table |
| trombone | brass | 29–72 | 0 (A_non_transposing) | F1–C5 (29–72) | aligned |
| trombone_baixo | brass | 34–65 | 0 (A_non_transposing) | — | no_table |
| trompa | brass | 34–77 | 7 (D_interval_transposing) | A#1–F5 (34–77) | aligned |
| trompete | brass | 52–87 | 2 (D_interval_transposing) | E3–D#6 (52–87) | aligned |
| tuba | brass | 24–70 | 0 (A_non_transposing) | C1–A#4 (24–70) | aligned |
| vibrafone | percussion | 53–84 | 0 (A_non_transposing) | — | no_table |
| viola | strings | 48–94 | 0 (A_non_transposing) | C3–A#6 (48–94) | aligned |
| viola_harm | strings | 72–94 | 0 (A_non_transposing) | C5–A#6 (72–94) | aligned |
| viola_sordina | strings | 48–94 | 0 (A_non_transposing) | C3–A#6 (48–94) | aligned |
| viola_sul_ponticello | strings | 48–93 | 0 (A_non_transposing) | C3–E6 (48–88) | OK_registry_covers_table |
| violino | strings | 55–107 | 0 (A_non_transposing) | G3–B7 (55–107) | aligned |
| violino_harm | strings | 79–107 | 0 (A_non_transposing) | G5–B7 (79–107) | aligned |
| violino_sordina | strings | 55–107 | 0 (A_non_transposing) | G3–C7 (55–96) | OK_registry_covers_table |
| violino_sul_ponticello | strings | 55–107 | 0 (A_non_transposing) | G3–C7 (55–96) | OK_registry_covers_table |
| violino_sul_tasto | strings | 55–107 | 0 (A_non_transposing) | G3–B7 (55–107) | aligned |
| violoncelo | strings | 36–84 | 0 (A_non_transposing) | C2–C6 (36–84) | aligned |
| violoncelo_harm | strings | 60–84 | 0 (A_non_transposing) | C4–C6 (60–84) | aligned |
| violoncelo_sordina | strings | 36–84 | 0 (A_non_transposing) | C2–A5 (36–81) | OK_registry_covers_table |
| violoncelo_sul_ponticello | strings | 36–84 | 0 (A_non_transposing) | C2–A5 (36–81) | OK_registry_covers_table |
