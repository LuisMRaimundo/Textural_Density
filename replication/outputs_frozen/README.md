# Frozen replication outputs

JSON/CSV outputs from score-only default config runs.

**Current:** synthetic `synthetic_triad` fixture only.

Each frozen file should record:

- `metric_schema_version`
- `config_hash`, `input_hash`
- `synthetic_fixture` flag when applicable
- `density`, `density_subindices`, `metric_metadata`

Regenerate: `python replication/scripts/reproduce_metrics.py`  
Compare: `python replication/scripts/compare_to_frozen_outputs.py`

Do not silently overwrite frozen outputs without documenting the reason in
`tests/snapshots/MIGRATION.md` (especially after Qty or mass-formula changes).

Qty semantics sign-off: [`docs/qa_checklist.md`](../../docs/qa_checklist.md).
