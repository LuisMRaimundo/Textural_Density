# Benchmark corpus intake

This folder is the **intake queue** for representative score excerpts used in the systematic score-only symbolic method benchmark.

## How to add a legitimate benchmark

1. Copy your score file into the appropriate subfolder:
   - `intake/` — unclassified queue (recommended first stop)
   - `musicxml/` — `.musicxml` files
   - `mxl/` — compressed MusicXML
   - `xml/` — other XML score formats
   - `midi/` — MIDI files

2. Ensure you can assign one of these **license_status** values:
   - `owned_by_project_author` — you created the score
   - `public_domain_verified` — PD with documented source
   - `openly_licensed` — explicit reusable license (e.g. CC-BY with attribution note)

3. Run the intake scanner:

```bash
python replication/scripts/scan_benchmark_intake.py
```

4. Complete metadata in `replication/benchmark_manifest.json` for any new entry:
   - composer, work_title, excerpt_label, measure_range, license_note

5. Set `include_in_official_benchmark: true` **only** when license is verified.

6. Generate frozen outputs:

```bash
python replication/scripts/reproduce_metrics.py
python replication/scripts/compare_to_frozen_outputs.py
python replication/scripts/reproduce_tables.py
```

## What does NOT qualify as official benchmark

| Status | Meaning |
|--------|---------|
| `synthetic_fixture` | Project-generated test input |
| `repository_example_unknown_license` | Example file without license documentation |
| `unknown_license_excluded` | Cannot be promoted until license is documented |

Synthetic fixtures earn **scaffold credit only** — they do not satisfy the representative corpus requirement for 90+ under the systematic score-only rubric.

## Current gap

**No official representative benchmark files are committed.** The corpus maturity flag in the manifest remains `synthetic_scaffold_only` until at least one licensed excerpt is added and frozen.
