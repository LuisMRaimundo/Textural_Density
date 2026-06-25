# Instrument metadata audit

Human-readable summary of the **instrument profile provenance audit**. Machine-readable export:

```bash
python scripts/export_instrument_metadata_audit.py
```

→ `instrumentos/instrument_metadata_audit.json`

## Rules

- GPR-backed modules (`flute`, `oboe`, `clarinet`, `violin`, `viola`, `cello`, `double_bass`, …) use **externally sourced acoustic metadata** (sparse CDM tables, GPR-interpolated). This is applied at score-analysis time — **not** runtime audio analysis.
- Registry `coarse_default` profiles lack external acoustic tables; audit label **`symbolic_default`**.
- `literature_derived` / `literature_informed` profiles document external provenance in `source_notes`.
- Written dynamics use **symbolic weighting only** — not SPL or loudness.
- Unknown instruments resolve to a generic fallback with warnings (`instrument_id=unknown`).

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
- **Double-bass span adjudication:** committed `double_bass.py` table spans E1–C5; confirm methodological status of upper-register rows (see [instrument_acoustic_sources.md](instrument_acoustic_sources.md)).
- **Contrabassoon registry:** `sounding_range` is B♭0–F5 (MIDI 22–77), aligned with common orchestration references; coarse profile only (no CDM table). Manual/GUI input uses **sounding** pitch (not written); MusicXML may supply written pitch with optional `<transpose>`.
- **Manual vs written pitch:** legacy `notes[]` and the GUI validate **concert/sounding** MIDI against `sounding_range`. Registry `transposition` is score-metadata only unless MusicXML `<transpose>` is present.
- **Technique vs table scope:** arco sustain CDM tables must not be read as technique-specific measurements for pizzicato/tremolo/harmonics/mute without dedicated data.
- **GPR determinism:** production modules do not fix `random_state`; test reproducibility is conditional only.

**Resolved (PR #14):** viola portable provenance (`docs/instrument_acoustic_sources.md#viola`); viola table aligned to `VIOLA_Media` (C3–C7) with `(2)` label normalization.

See also [`instrumentos/registry.py`](../instrumentos/registry.py) and [`docs/constants_and_assumptions.md`](constants_and_assumptions.md).
