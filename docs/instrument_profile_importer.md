# Instrument profile Excel importer (Phase 1a)

> **Scope:** Auxiliary/offline metadata curation only. Textural Density remains a strictly symbolic score-based analyser at runtime. See [README.md](../README.md) (Scientific scope) and [instrument_acoustic_sources.md](instrument_acoustic_sources.md) (incomplete corpus status).

## Purpose

The importer in `tools/import_instrument_profiles_from_excel.py` converts human-curated **Excel workbooks** into **canonical JSON profile packages** for instrument acoustic/proxy metadata used by Textural Density at score lookup time.

This phase provides:

- validation and reporting (`--dry-run`, `--report`);
- JSON emission to an output directory (typically `instrumentos/data/`);
- no Python instrument module generation;
- no runtime `.xlsx` reads.

## Score-based scope

Textural Density is a **symbolic, score-based** textural-density analyser. Instrument tables are **pre-loaded metadata proxies** applied when resolving `sounding_pitch` from notated score events.

This pipeline does **not**:

- import or analyse audio;
- run FFT/STFT or spectral analysis;
- import SoundSpectrAnalyse or related audio stacks.

The importer itself is constrained the same way: it validates spreadsheet metadata only.

## Excel vs JSON

| Format | Role |
|--------|------|
| **Excel (`.xlsx`)** | Human-facing curation format — edit in a spreadsheet |
| **JSON (`.profile.json`)** | Canonical validated runtime/audit format produced by the importer |

Runtime code must not read `.xlsx` directly. Curate in Excel, import to JSON, then wire profiles through the normal instrument registry path in later phases.

## Pitch basis: sounding / concert pitch only

All acoustic/proxy table rows are in **real sounding pitch / concert pitch**.

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

The importer **never transposes** imported AcousticTable rows. Example: for a B-flat clarinet with `transposition = -2`, a row curated as sounding `C4` / MIDI `60` remains `C4` / MIDI `60` in the output JSON.

## Official template

Start from:

```text
instrumentos/templates/instrument_profiles_template.xlsx
```

Sheets:

| Sheet | Required | Purpose |
|-------|----------|---------|
| `WorkbookMeta` | yes | Global workbook keys (`acoustic_pitch_basis`, template version, notes) |
| `Registry` | yes | Instrument identity, ranges, transposition (score-only), profile status |
| `AcousticTable` | yes | Sounding-pitch proxy table rows |
| `Provenance` | yes | Source citation and import audit fields |
| `Aliases` | optional | Alternate instrument names |
| `ValidationRules` | optional | Human-readable curation rules (not machine-enforced beyond importer logic) |

### Registry columns

`instrument_id`, `display_name`, `family`, `subfamily`, `transposition`, `sounding_range_low_midi`, `sounding_range_high_midi`, `comfortable_range_low_midi`, `comfortable_range_high_midi`, `profile_status`, `source_type`, `uncertainty`, `source_notes`, `supported_techniques`, `aliases`

### AcousticTable columns

`instrument_id`, `note_sounding`, `midi_sounding`, `dynamic`, `value`, `value_kind`, `unit`, `cell_status`, `source_system`, `source_file`, `source_column`, `source_hash`, `transform_policy`, `uncertainty`, `validation_status`, `notes`, `note_written_optional`, `midi_written_optional`, `transposition_semitones_optional`

### Provenance columns

`instrument_id`, `source_type`, `citation`, `source_url_or_identifier`, `upstream_system`, `upstream_version`, `analysis_profile_hash`, `import_run_id`, `import_date`, `operator`, `transform_policy`, `transform_parameters`, `rows_accepted`, `rows_rejected`, `notes`

### Aliases columns

`instrument_id`, `alias`, `alias_kind`

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

## Provenance rules

- Every instrument should have a `Provenance` row with citation and source type.
- `measured_proxy` AcousticTable rows require `source_system`, `source_file`, and `source_column`.
- `profile_status` values such as `empirical_source` or `empirical_profile` require non-empty `source_notes` in Registry.
- Fallback/default values must **not** be labelled as empirical without honest source documentation.

## `transform_policy` rules

Default when omitted: `manual_review_required`.

Allowed values:

- `manual_review_required` (default)
- `identity_v1` (only when explicitly declared)
- `linear_rescale_v1`
- `log_rescale_v1`
- `rank_order_only_v1`
- `reject`

Use `identity_v1` only when a row is explicitly approved for pass-through without rescaling.

## Recommended workflow

1. Copy `instrumentos/templates/instrument_profiles_template.xlsx` to a **local working path outside Git** (or a private curation folder).
2. Fill Registry, AcousticTable, and Provenance using **sounding/concert pitch** throughout.
3. Run dry-run validation and save a report:

```bash
python tools/import_instrument_profiles_from_excel.py \
  --workbook path/to/workbook.xlsx \
  --output-dir instrumentos/data \
  --dry-run \
  --report reports/instrument_import_report.json
```

4. Review errors/warnings in the report JSON. Fix the workbook and repeat until clean.
5. Generate JSON to a temporary or staging output directory:

```bash
python tools/import_instrument_profiles_from_excel.py \
  --workbook path/to/workbook.xlsx \
  --output-dir instrumentos/data \
  --report reports/instrument_import_report.json
```

6. Inspect generated `*.profile.json` and `index.json` under the output directory.
7. Commit JSON profiles to the repository only after explicit review/approval in a later phase.

Use `--strict` to treat warnings (e.g. unknown `instrument_id` references) as errors.

## Why this PR has no real data

This template/documentation phase ships:

- header-only workbook structure;
- curation rules and importer usage docs;
- **no real acoustic metadata**;
- **no generated JSON profiles with real instrument values**.

Real curated `.xlsx` files should **normally stay outside Git** until explicitly approved. Likewise, do not commit ad-hoc user workbooks or local validation reports by default.

## Output JSON shape (summary)

Each `{instrument_id}.profile.json` includes:

- `schema_version`
- `acoustic_pitch_basis` (`sounding_concert`)
- `instrument_id`
- `registry`
- `acoustic_table`
- `provenance`
- `import_audit`

See `tools/import_instrument_profiles_from_excel.py` and `tests/test_instrument_profile_excel_importer_additional.py` for the validated contract.
