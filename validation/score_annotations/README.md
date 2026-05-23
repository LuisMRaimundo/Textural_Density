# Expert score annotations (optional empirical extension)

> **Optional only.** This folder supports **optional** empirical studies if the project later claims to predict expert judgments of vertical density. It is **not required** for the systematic score-only research line. Primary validation is **formal score-based validation** via construct definitions, axioms, tests, and benchmark replication.

When used, annotations target **expert judgments of vertical density on the score page**, not listening tests.

## Rating dimensions

Each slice should be rated separately on:

- `overall_symbolic_vertical_density`
- `event_density`
- `interval_compactness`
- `registral_density`
- `orchestration_mass`
- `timbral_orchestration_complexity`

Raters evaluate symbolic excerpts using the same information available to the program (notes, register, instrumentation, written dynamics, measure/beat, simultaneity). **No listening required.**

## Schema

See [`schema.json`](schema.json). Required fields include corpus/piece/slice identifiers, rater metadata, rating dimension/value, scale bounds, and `annotation_protocol_version`.

## Examples

- [`examples/toy_fixture.json`](examples/toy_fixture.json) — **schema test only**; must never appear in validation tables as real results.

## Status labels

| Label | Meaning |
|-------|---------|
| `verified_only` | Tests and synthetic cases only |
| `score_validated` | Correlated with external expert score annotations |
| `partially_score_validated` | Some constructs or small corpus validated |
| `unvalidated` | No tests or annotations |
| `legacy_proxy` | Optional out-of-scope proxy branch |

Current repository status: **verified_only** (no external expert corpus committed).
