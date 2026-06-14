# Auxiliary tools (offline — not analytical core)

Scripts in this directory support **metadata curation, validation, and export**. They are **not** part of the score-based Textural Density runtime pipeline in `core/`.

| Tool | Purpose |
|------|---------|
| [`import_instrument_profiles_from_excel.py`](import_instrument_profiles_from_excel.py) | Validate human-curated Excel instrument-profile workbooks; emit canonical JSON/audit artefacts offline |

These tools:

- do **not** analyse scores or audio at runtime;
- do **not** change density formulas or metric definitions;
- are **not** imported by `core.pipeline.calculate_metrics`.

Documentation: [`docs/instrument_profile_importer.md`](../docs/instrument_profile_importer.md)
