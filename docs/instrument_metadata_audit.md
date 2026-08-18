# Instrument metadata audit

Human-readable summary of the **instrument profile provenance audit**. Machine-readable export:

```bash
python scripts/export_instrument_metadata_audit.py
```

→ `instrumentos/instrument_metadata_audit.json`

## Rules

- Table-backed modules (`flute`, `oboe`, `clarinet`, `bassoon`, `trumpet`, `horn`, `trombone`, `tuba`, `violin`, `viola`, `cello`, `double_bass`, …) use **externally sourced acoustic metadata** (committed 10-dynamic CDM ladders; no runtime interpolation of dynamics). This is applied at score-analysis time — **not** runtime audio analysis.
- Registry `coarse_default` profiles lack external acoustic tables; audit label **`symbolic_default`**.
- `literature_derived` / `literature_informed` profiles document external provenance in `source_notes`.
- Written dynamics use **symbolic weighting only** — not SPL or loudness.
- The generic unknown proxy (`instrument_id=unknown`) is audit-only (`profile_for_event(..., allow_unknown=True)`). Analysis rejects unregistered ids.

## Audit fields (per instrument)

`instrument_id`, `display_name`, `family`, `profile_status`, `uncertainty`, `source_notes`, `limitations`, `has_range_metadata`, `has_register_metadata`, `has_dynamic_weight_metadata`, `has_technique_metadata`, `warnings`

## Allowed audit statuses

| Status | Meaning |
|--------|---------|
| `symbolic_default` | Coarse register/dynamic model; no external acoustic table |
| `literature_informed` | External acoustic metadata (sparse GPR tables or literature-derived model) |
| `empirical_profile` | Documented empirical acoustic source in `source_notes` |
| `unknown_needs_review` | Missing or inconsistent metadata |

## Current action items

- Review all `symbolic_default` profiles with `uncertainty=high` before claiming registry maturity.
- Do not upgrade status to `empirical_profile` without committing supporting source notes in the repository.
- **Double-bass span:** `source_table_span` E1–C5 (**PASS**); obsolete E1–A3 documentation; upper-register QC **REVIEW REQUIRED** (see [instrument_acoustic_sources.md](instrument_acoustic_sources.md))
- **Tuba range:** coarse-default validation placeholder MIDI 28–58 — **REVIEW REQUIRED**
- **Sounding/concert pitch:** legacy `notes[]`, GUI, and manual input use sounding pitch. MusicXML written `<pitch>` is converted via `<transpose>` to sounding pitch before validation and lookup.
- **Technique metadata:** `INSTRUMENT_SOURCE.source_technique` / `table_supported_techniques` on table-backed modules; registry lists broader organological capabilities without implying technique-specific numerical tables.
- **Runtime dynamics:** committed 10-level ladder lookup only. Historical GPR (`create_dynamic_gpr`) lives in `tools/legacy_gpr_dynamic_interpolation.py` and is **not** called from `calculate_metrics`.

**Resolved (PR #14):** viola portable provenance (`docs/instrument_acoustic_sources.md#viola`); viola table aligned to `VIOLA_Media` (C3–C7) with `(2)` label normalization.

See also [`instrumentos/registry.py`](../instrumentos/registry.py) and [`docs/constants_and_assumptions.md`](constants_and_assumptions.md).
