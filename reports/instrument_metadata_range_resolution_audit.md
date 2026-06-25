# Instrument metadata / range resolution audit

**Instruments audited:** 28

## Executive summary

- **Double bass:** source_table_span E1–C5 aligns with committed table and registry; E1–A3 was obsolete documentation.
- **Technique:** GPR modules declare `source_technique` / `table_supported_techniques`; registry lists broader organological capabilities.
- **Tuba:** coarse-default validation placeholder (MIDI 28–58) — **REVIEW REQUIRED** for authoritative range.
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

## Tuba review

- Classification: **REVIEW REQUIRED**
- No committed tuba spectral_data module. registry.sounding_range (28–58) is a coarse orchestration placeholder for validation only — not a source-table span.

## Transposition review

- Classification: **PASS**
- registry.transposition is notation/import metadata only; manual/GUI notes[] are sounding/concert pitch; MusicXML <transpose> converts written→sounding once.

## Per-instrument summary

| ID | Table span | Sounding MIDI | Comfortable | Range | Technique |
|----|------------|---------------|-------------|-------|-----------|
| bombo | — | 28–48 | 28–48 | NOT APPLICABLE | NOT APPLICABLE |
| caixa | — | 60–72 | 60–72 | NOT APPLICABLE | NOT APPLICABLE |
| celesta | — | 60–96 | 65–88 | NOT APPLICABLE | NOT APPLICABLE |
| clarinete | D3–C7 | 50–96 | 55–80 | PASS | PASS |
| clarinete_baixo | — | 34–72 | 40–65 | NOT APPLICABLE | NOT APPLICABLE |
| contrabaixo | E1–C5 | 28–72 | 31–55 | PASS | PASS |
| contrafagote | — | 22–77 | 28–65 | NOT APPLICABLE | NOT APPLICABLE |
| cor_anglais | — | 52–76 | 55–72 | NOT APPLICABLE | NOT APPLICABLE |
| fagote | — | 34–72 | 40–65 | NOT APPLICABLE | NOT APPLICABLE |
| flauta | B3–D7 | 59–98 | 62–88 | PASS | PASS |
| flautim | — | 74–108 | 76–100 | NOT APPLICABLE | NOT APPLICABLE |
| harpa | — | 23–96 | 40–88 | NOT APPLICABLE | NOT APPLICABLE |
| marimba | — | 45–84 | 45–84 | NOT APPLICABLE | NOT APPLICABLE |
| metalofone | — | 72–108 | 72–108 | NOT APPLICABLE | NOT APPLICABLE |
| oboe | A#3–A6 | 58–93 | 60–81 | PASS | PASS |
| piano | — | 21–108 | 36–96 | NOT APPLICABLE | NOT APPLICABLE |
| pratos | — | 60–84 | 60–84 | NOT APPLICABLE | NOT APPLICABLE |
| tamtam | — | 24–48 | 24–48 | NOT APPLICABLE | NOT APPLICABLE |
| timpanos | — | 36–60 | 36–60 | NOT APPLICABLE | NOT APPLICABLE |
| trombone | — | 40–72 | 43–65 | NOT APPLICABLE | NOT APPLICABLE |
| trombone_baixo | — | 34–65 | 36–58 | NOT APPLICABLE | NOT APPLICABLE |
| trompa | — | 41–77 | 45–72 | NOT APPLICABLE | NOT APPLICABLE |
| trompete | — | 55–84 | 58–80 | NOT APPLICABLE | NOT APPLICABLE |
| tuba | — | 28–58 | 30–50 | NOT APPLICABLE | NOT APPLICABLE |
| vibrafone | — | 53–84 | 53–84 | NOT APPLICABLE | NOT APPLICABLE |
| viola | C3–C7 | 48–96 | 50–69 | PASS | PASS |
| violino | G3–G7 | 55–103 | 55–76 | PASS | PASS |
| violoncelo | C2–C6 | 36–84 | 40–65 | PASS | PASS |
