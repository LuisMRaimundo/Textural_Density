# Characterization battery — provenance

- Generated: 2026-07-11 22:52:34 UTC
- Tool: `benchmarks/characterization/run_battery.py`
- METRIC_SCHEMA_VERSION: `5.1.0-strict-symbolic`
- Package version (pyproject): `1.1.4`
- Cases: 123 valued / 142 total; errors: 19

## Resolved instrument map

- `WW_HI` -> `flauta`
- `WW_MID` -> `clarinete`
- `WW_LO` -> `fagote`
- `BRASS` -> `trompete`
- `STR_HI` -> `violino`
- `STR_LO` -> `double_bass`

## Substitutions

- none (all preferred role keys resolved)

## Outputs

- `characterization_battery.md` — grouped human-readable tables + header + diagnostics
- `characterization_battery.csv` — flat union of all valued rows (curated columns)
- `characterization_battery_full.json` — per case: input + full `resultados` + curated + flags

Read-only characterization of the current build; config/core/metric logic untouched.
