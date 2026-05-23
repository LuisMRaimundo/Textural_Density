# Replication package (score-only symbolic validation)

Reproduce thesis/research tables from symbolic score inputs with frozen outputs for regression.

## Layout

| Path | Purpose |
|------|---------|
| `corpus/` | MusicXML/MIDI excerpts + metadata |
| `configs/` | Score-only default and thesis table configs |
| `outputs_frozen/` | Frozen JSON/CSV outputs per benchmark input |
| `scripts/` | Reproduce, compare, table generation |
| `tables/` | Generated research tables |
| `checksums/` | Input/config checksum records |

## Quick start

```bash
# Recompute metrics for all corpus metadata entries
python replication/scripts/reproduce_metrics.py

# Compare current outputs to frozen baselines
python replication/scripts/compare_to_frozen_outputs.py

# Generate summary tables
python replication/scripts/reproduce_tables.py
```

## Current corpus

Only **synthetic fixtures** are included (`corpus/metadata/synthetic_triad.json`).
Do not treat synthetic outputs as externally validated results.

## Frozen output policy

If metrics change intentionally, update frozen files and document the reason.
Do not silently overwrite without updating `metric_schema_version` / config hash.

**Qty / player-count formula changes:** refresh regression baseline, snapshots, benchmark
`expected_outputs/`, and replication frozen JSON; complete the Qty semantics sign-off in
[`docs/qa_checklist.md`](../docs/qa_checklist.md) and [`score_only_90_readiness_checklist.md`](../docs/score_only_90_readiness_checklist.md).
