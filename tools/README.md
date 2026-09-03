# Auxiliary tools (offline — not analytical core)

Scripts in this folder support **offline metadata curation and maintenance**. They are **not** part of the Textural Density runtime pipeline. They do **not** change density formulas, metric definitions, or runtime lookup logic. They do **not** analyse audio, run FFT/STFT, or invoke Spectral_Analyser.

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

## Dynamics10 dest-Zenodo commit (2026-09-03)

**Script:** `commit_dynamics_from_para_dinamicas.py`

Reads each `*_Dynamics10.xlsx` `Results` sheet in the Desktop `para dinâmicas` folder (`status=ok` rows only) and writes `instrumentos/<module>.py`. Note labels are collapsed with `normalize_media_note_label` (`Bb1` → `A#1`, `F4 (2)` → `F4`). Interior cells are clamped into their measured `[pp, mf]` / `[mf, ff]` segment.

```bash
python tools/commit_dynamics_from_para_dinamicas.py
```

This is the current official path for ordinary-sustain winds (including Picc, E_Horn, Bass_Clar, Contr_Basson), brass, arco strings, and string technique/harmonic modules. Violin sul tasto has no 2026-09-03 book and is left unchanged. Older generators (`generate_full_dynamics_modules_from_xlsx.py`, `generate_violin_technique_modules_from_ok_workbooks.py`) remain for history and for rendering helpers imported by this script.
