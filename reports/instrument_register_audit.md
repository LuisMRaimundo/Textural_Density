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
| clarinete_baixo | woodwinds | 34–72 | 14 (D_interval_transposing) | — | no_table |
| contrabaixo | strings | 28–72 | 0 (A_non_transposing) | E1–C5 (28–72) | aligned |
| contrabaixo_harm | strings | 28–67 | 0 (A_non_transposing) | E1–G4 (28–67) | aligned |
| contrabaixo_sordina | strings | 29–67 | 0 (A_non_transposing) | F1–G4 (29–67) | aligned |
| contrabaixo_sul_ponticello | strings | 28–67 | 0 (A_non_transposing) | E1–G4 (28–67) | aligned |
| contrafagote | woodwinds | 22–77 | 0 (A_non_transposing) | — | no_table |
| cor_anglais | woodwinds | 52–76 | 7 (D_interval_transposing) | — | no_table |
| fagote | woodwinds | 34–75 | 0 (A_non_transposing) | A#1–D#5 (34–75) | aligned |
| flauta | woodwinds | 59–98 | 0 (A_non_transposing) | B3–D7 (59–98) | aligned |
| flautim | woodwinds | 74–108 | 0 (A_non_transposing) | — | no_table |
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
| trompa | brass | 41–77 | 7 (D_interval_transposing) | A#1–F5 (34–77) | BUG_table_anchor_outside_registry |
| trompete | brass | 52–87 | 2 (D_interval_transposing) | E3–D#6 (52–87) | aligned |
| tuba | brass | 24–70 | 0 (A_non_transposing) | C1–A#4 (24–70) | aligned |
| vibrafone | percussion | 53–84 | 0 (A_non_transposing) | — | no_table |
| viola | strings | 48–96 | 0 (A_non_transposing) | C3–C7 (48–96) | aligned |
| viola_harm | strings | 72–107 | 0 (A_non_transposing) | C5–B7 (72–107) | aligned |
| viola_sordina | strings | 48–94 | 0 (A_non_transposing) | C3–A#6 (48–94) | aligned |
| viola_sul_ponticello | strings | 48–94 | 0 (A_non_transposing) | C3–A#6 (48–94) | aligned |
| violino | strings | 55–103 | 0 (A_non_transposing) | G3–G7 (55–103) | aligned |
| violino_harm | strings | 72–107 | 0 (A_non_transposing) | C5–B7 (72–107) | aligned |
| violino_sordina | strings | 55–103 | 0 (A_non_transposing) | G3–G7 (55–103) | aligned |
| violino_sul_ponticello | strings | 55–107 | 0 (A_non_transposing) | G3–B7 (55–107) | aligned |
| violino_sul_tasto | strings | 55–103 | 0 (A_non_transposing) | G3–G7 (55–103) | aligned |
| violoncelo | strings | 36–84 | 0 (A_non_transposing) | C2–C6 (36–84) | aligned |
| violoncelo_harm | strings | 60–100 | 0 (A_non_transposing) | C4–E7 (60–100) | aligned |
| violoncelo_sordina | strings | 36–81 | 0 (A_non_transposing) | C2–A5 (36–81) | aligned |
| violoncelo_sul_ponticello | strings | 36–84 | 0 (A_non_transposing) | C2–C6 (36–84) | aligned |

## REVIEW REQUIRED / discrepancies

- **trompa:** BUG_table_anchor_outside_registry
