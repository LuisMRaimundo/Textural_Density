# Benchmark corpus

| Status | Description |
|--------|-------------|
| **Current** | `synthetic_scaffold_only` — see [`benchmark_manifest.json`](../benchmark_manifest.json) |
| **Target** | Representative licensed MusicXML/MIDI excerpts with frozen outputs |

## Layout

- `intake/` — benchmark intake queue (see `intake/README.md`)
- `metadata/` — JSON input descriptors (synthetic or future licensed excerpts)
- `musicxml/`, `mxl/`, `midi/` — reserved for licensed score files

## Rules

- **Synthetic fixtures** — scaffold/replication tests only; not a mature representative corpus.
- **Unknown license** — inventory only; `include_in_official_benchmark: false`.
- **No fabricated scores** — do not add copyrighted material without permission.

Official benchmark promotion requires updating `benchmark_manifest.json` with `include_in_official_benchmark: true` and regenerating frozen outputs.
