# Instrument metadata / range resolution audit

**Instruments audited:** 36

## Executive summary

- **Double bass:** source_table_span E1–C5 (MIDI 28–72) aligns with committed table and registry; E1–A3 was obsolete documentation.
- **Violin sounding [55,103]:** table G3–G7 aligns (not a double-bass case).
- **Table excludes sounding range (partial):** 0 instrument(s): none.
- **Technique:** modules declare `source_technique` / `table_supported_techniques`; registry lists broader organological capabilities.
- **Trombone:** committed table (`trombone.py`, F1–C5) — **PASS** when registry matches the table span.
- **Tuba:** committed table (`tuba.py`, C1–A#4) — **PASS** when registry matches the table span.
- **Transposition:** registry field is metadata-only; manual input is sounding pitch; MusicXML applies `<transpose>` once.

## Range semantics

- **source_table_span:** Pitch span covered by committed spectral_data / INSTRUMENT_SOURCE.pitch_range rows (sounding/concert pitch).
- **sounding_range:** Registry validation span for sounding/concert-pitch manual and MusicXML-after-transpose input.
- **written_range:** Written notation span; only relevant on MusicXML written-pitch paths before <transpose>.
- **practical_range:** Ordinary orchestrational use if documented separately; not inferred from table span alone.
- **comfortable_range:** Conservative central register band in registry; narrower than full sounding_range when set.
- **extended_range:** Broader exceptional range if documented; not automatically equal to source_table_span.
- **source_technique:** Playing technique represented by the numerical source table (INSTRUMENT_SOURCE.source_technique).
- **table_supported_techniques:** Techniques with independent numerical rows in the committed table.
- **registry_supported_techniques:** Organological capabilities listed on InstrumentProfile.supported_techniques.

## Double-bass resolution

- Classification: **PASS**
- Source table span: E1–C5 (MIDI 28–72)
- Obsolete docs span: E1–A3 (obsolete_documentation_only)
- Upper-register QC: **REVIEW REQUIRED**
- Committed spectral_data, INSTRUMENT_SOURCE.pitch_range, and registry.sounding_range all agree on E1–C5. E1–A3 was obsolete documentation. Comfortable range remains narrower. Methodological status of upper-register rows (above A3) vs core corpus not independently adjudicated.

## Trombone review

- Classification: **PASS**
- Committed trombone spectral_data ladder (IOWA+ORCH medians via Dynamics_predicter); registry.sounding_range matches the committed table span.

## Tuba review

- Classification: **PASS**
- Committed tuba spectral_data ladder (IOWA+ORCH medians via Dynamics_predicter); registry.sounding_range matches the committed table span.

## Transposition review

- Classification: **PASS**
- registry.transposition is notation/import metadata only; manual/GUI notes[] are sounding/concert pitch; MusicXML <transpose> converts written→sounding once.

## Per-instrument summary

| ID | Table span | Sounding MIDI | Comfortable | Excludes range? | Range | Technique |
|----|------------|---------------|-------------|-----------------|-------|-----------|
| bombo | D2–D2 | 28–48 | 28–48 | not_applicable_unpitched | PASS | PASS |
| caixa | — | 60–72 | 60–72 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| celesta | — | 60–96 | 65–88 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| clarinete | D3–C7 | 50–96 | 55–80 | full_coverage | PASS | PASS |
| clarinete_baixo | — | 34–72 | 40–65 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| contrabaixo | E1–C5 | 28–72 | 31–55 | full_coverage | PASS | PASS |
| contrafagote | — | 22–77 | 28–65 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| cor_anglais | — | 52–76 | 55–72 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| fagote | A#1–D#5 | 34–75 | 40–65 | full_coverage | PASS | PASS |
| flauta | B3–D7 | 59–98 | 62–88 | full_coverage | PASS | PASS |
| flautim | — | 74–108 | 76–100 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| gongo | C3–C3 | 36–60 | 36–60 | not_applicable_unpitched | PASS | PASS |
| harpa | — | 23–96 | 40–88 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| marimba | — | 45–84 | 45–84 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| metalofone | — | 72–108 | 72–108 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| oboe | A#3–A6 | 58–93 | 60–81 | full_coverage | PASS | PASS |
| piano | — | 21–108 | 36–96 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| pratos | C5–C5 | 60–84 | 60–84 | not_applicable_unpitched | PASS | PASS |
| tamtam | C2–C2 | 24–48 | 24–48 | not_applicable_unpitched | PASS | PASS |
| timpanos | — | 36–60 | 36–60 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| trombone | F1–C5 | 29–72 | 43–65 | full_coverage | PASS | PASS |
| trombone_baixo | — | 34–65 | 36–58 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| trompa | A#1–F5 | 41–77 | 45–72 | full_coverage | FAIL | PASS |
| trompete | E3–D#6 | 52–87 | 58–80 | full_coverage | PASS | PASS |
| tuba | C1–A#4 | 24–70 | 30–50 | full_coverage | PASS | PASS |
| vibrafone | — | 53–84 | 53–84 | no_table | NOT APPLICABLE | NOT APPLICABLE |
| viola | C3–C7 | 48–96 | 50–69 | full_coverage | PASS | PASS |
| viola_harm | C5–B7 | 72–107 | 72–96 | full_coverage | PASS | PASS |
| viola_sordina | C3–A#6 | 48–94 | 50–69 | full_coverage | PASS | PASS |
| viola_sul_ponticello | C3–A#6 | 48–94 | 50–69 | full_coverage | PASS | PASS |
| violino | G3–G7 | 55–103 | 55–76 | full_coverage | PASS | PASS |
| violino_harm | C5–B7 | 72–107 | 72–96 | full_coverage | PASS | PASS |
| violino_sordina | G3–G7 | 55–103 | 55–76 | full_coverage | PASS | PASS |
| violino_sul_ponticello | G3–B7 | 55–107 | 55–76 | full_coverage | PASS | PASS |
| violino_sul_tasto | G3–G7 | 55–103 | 55–76 | full_coverage | PASS | PASS |
| violoncelo | C2–C6 | 36–84 | 40–65 | full_coverage | PASS | PASS |
