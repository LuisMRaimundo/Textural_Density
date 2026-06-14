# Auxiliary tools (offline — not analytical core)

Scripts in this folder support **offline metadata curation and maintenance**. They are **not** part of the Textural Density runtime pipeline. They do **not** change density formulas, metric definitions, or runtime lookup logic. They do **not** analyse audio, run FFT/STFT, or invoke SoundSpectrAnalyse.

## Instrument profile Excel importer

**Script:** `import_instrument_profiles_from_excel.py`

| Aspect | Detail |
|--------|--------|
| Purpose | Validate human-curated Excel workbooks; emit canonical JSON profile packages |
| Runtime | Must **not** read raw `.xlsx` — import to JSON first |
| Pitch basis | All acoustic rows in **sounding/concert pitch** (`note_sounding`, `midi_sounding`) |
| Transposition | **Never** applied during import; registry transposition is for score parsing only |
| Output | `instrumentos/data/*.profile.json` (Phase 1a — no Python module generation) |

**Template:** [`instrumentos/templates/instrument_profiles_template.xlsx`](../instrumentos/templates/instrument_profiles_template.xlsx) (empty, no real data)

**Documentation:** [`docs/instrument_profile_importer.md`](../docs/instrument_profile_importer.md)

Real curated workbooks should normally remain **outside Git** unless explicitly approved.
