# Benchmark corpus (replication package)

Fixed symbolic score excerpts for reproducible thesis/research tables.

## Layout

- `replication/corpus/musicxml/` — preferred for notation-sensitive analysis
- `replication/corpus/midi/` — optional; weak notation/orchestration semantics
- `replication/corpus/metadata/` — per-excerpt metadata (composer, work, source, limitations)

## Current status

- **Replication package (`replication/corpus/`):** synthetic fixtures only until licensed excerpts are added to intake.
- **Benchmark package (`benchmarks/corpus/`):** three project-authored MusicXML excerpts (including Bb clarinet transpose regression `excerpt_003`).

Synthetic files are labelled `synthetic_fixture` in replication metadata. Benchmark excerpts use `owned_by_project_author` license.

See [`replication/README.md`](../replication/README.md) for reproduction scripts and frozen outputs.
