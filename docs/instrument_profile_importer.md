# Instrument profile Excel importer (Phase 1a — auxiliary tooling)

## Auxiliary / offline scope

This document describes **auxiliary metadata-curation tooling**. It is **not** part of the Textural Density **analytical core**.

| Component | Role |
|-----------|------|
| **`core/` pipeline** | Score-based symbolic density analysis at runtime |
| **`tools/import_instrument_profiles_from_excel.py`** | Offline validator/exporter for human-curated Excel workbooks |

The importer:

- validates spreadsheet structure and metadata rules;
- can emit canonical JSON packages and audit reports;
- does **not** run analysis;
- does **not** change density formulas or metric definitions;
- does **not** transpose acoustic table rows;
- is **not** imported by the runtime analysis engine.

Excel (`.xlsx`) is a **user-facing curation format**. The runtime should consume **validated canonical artefacts** (e.g. `.profile.json`), not raw Excel files directly.

## Purpose

The script `tools/import_instrument_profiles_from_excel.py` converts human-curated **Excel workbooks** into **canonical JSON profile packages** for instrument acoustic/proxy metadata that may later be wired into score lookup. It is an offline helper for controlled metadata insertion/export — not the analysis engine.

Capabilities:

- validation and reporting (`--dry-run`, `--report`);
- JSON emission to an output directory (e.g. `instrumentos/data/`);
- no Python instrument module generation;
- no runtime `.xlsx` reads.

## Score-based scope

Textural Density is a **symbolic, score-based** textural-density analyser. At runtime it analyses **notated events** — instruments, dynamics, player counts, intervals, register, and vertical simultaneities — without live audio input.

Instrument tables are **external/proxy lookup data** applied when resolving **sounding pitch** from score events. They may be **derived offline** from SoundSpectrAnalyse outputs or other sources, but **SoundSpectrAnalyse code is not imported or executed** by Textural Density or this importer.

Neither the analytical core nor this importer:

- import or analyse live audio;
- run FFT/STFT or extract spectral partials;
- compute EWSD or SoundSpectrAnalyse H/I/S metrics.

Missing or incomplete instrument metadata are **not automatically bugs**. Fallback/default values must remain explicitly labelled as fallback/default/proxy — never as empirical measurement.

## Excel vs JSON

| Format | Role |
|--------|------|
| **Excel (`.xlsx`)** | Human-facing curation format — edit in a spreadsheet |
| **JSON (`.profile.json`)** | Canonical validated runtime/audit format produced by the importer |

Curate in Excel offline, import to JSON, then integrate profiles through the normal instrument registry path in later phases.

## Pitch basis: sounding / concert pitch only

All instrument metadata imported from Excel or SoundSpectrAnalyse-derived tables must be in **real sounding pitch / concert pitch**.

WorkbookMeta must declare:

```text
acoustic_pitch_basis = sounding_concert
```

AcousticTable primary columns:

- `note_sounding`
- `midi_sounding`

Do **not** use generic `note` / `midi` columns.

Optional written-pitch fields are **traceability only**:

- `note_written_optional`
- `midi_written_optional`
- `transposition_semitones_optional`

### No double transposition

`Registry.transposition` applies to **score parsing** (written → sounding), not to metadata import.

The importer **never transposes** imported AcousticTable rows.

**Example (B-flat clarinet):** written D4 sounds as concert C4 (MIDI 60). The metadata table must store **sounding** `C4` / MIDI `60`, not written `D4` / MIDI `62`. Optional written-pitch columns are traceability only.

## Workbook structure

When an optional header-only template is available (`instrumentos/templates/instrument_profiles_template.xlsx`), copy it to a **local working path outside Git** before curating.

| Sheet | Required | Purpose |
|-------|----------|---------|
| `WorkbookMeta` | yes | Global keys (`acoustic_pitch_basis`, template version, notes) |
| `Registry` | yes | Instrument identity, ranges, transposition (score-only), profile status |
| `AcousticTable` | yes | Sounding-pitch proxy table rows |
| `Provenance` | yes | Source citation and import audit fields |
| `Aliases` | optional | Alternate instrument names |
| `ValidationRules` | optional | Human-readable curation rules |

## Accepted `cell_status` values

| Value | Meaning |
|-------|---------|
| `measured_proxy` | Value derived from an external measured/proxy source (provenance required) |
| `interpolated` | Interpolated between known points |
| `manual_entry` | Hand-entered curation |
| `scaled_proxy` | Rescaled proxy value |
| `coarse_default` | Coarse default / placeholder proxy |
| `symbolic_default` | Symbolic default (non-empirical) |
| `missing` | Cell intentionally absent; no numeric value required |

## Provenance and transform rules

- `measured_proxy` rows require `source_system`, `source_file`, and `source_column`.
- Empirical profile statuses require honest `source_notes` in Registry.
- Default `transform_policy`: `manual_review_required` (use `identity_v1` only when explicitly declared).

## Example commands

Dry-run validation:

```bash
python tools/import_instrument_profiles_from_excel.py \
  --workbook path/to/workbook.xlsx \
  --output-dir instrumentos/data \
  --dry-run \
  --report reports/instrument_import_report.json
```

Generate JSON after review:

```bash
python tools/import_instrument_profiles_from_excel.py \
  --workbook path/to/workbook.xlsx \
  --output-dir instrumentos/data \
  --report reports/instrument_import_report.json
```

Real curated `.xlsx` files and local import reports should **normally stay outside Git** until explicitly approved.

## Output JSON shape (summary)

Each `{instrument_id}.profile.json` includes: `schema_version`, `acoustic_pitch_basis` (`sounding_concert`), `instrument_id`, `registry`, `acoustic_table`, `provenance`, `import_audit`.

See `tools/import_instrument_profiles_from_excel.py` and `tests/test_instrument_profile_excel_importer_additional.py` for the validated contract.
