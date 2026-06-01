# Versioning and licensing

This document defines how **release versions**, **methodology phases**, and **schema versions** relate. They are **not interchangeable**.

---

## Product name vs package identifier

| Label | Value | Notes |
|-------|-------|-------|
| **Product / documentation name** | **Textural Density** | README, manuals, rubric, reports |
| **PyPI / console script** | `densidade-vertical` | Legacy package id in `pyproject.toml`; unchanged for install compatibility |
| **GitHub repository** | `Textural_Density` | Remote URL slug |

---

## Package release version (PyPI / GitHub releases)

| Field | Location | Current |
|-------|----------|---------|
| **Canonical value** | `[project].version` in `pyproject.toml` | **1.1.1** |
| **Runtime API** | `core.version.get_package_version()` / `core.__version__` | same |
| **License** | `LICENSE` (MIT) + `[project].license` in `pyproject.toml` | **MIT** |

**When to bump:** user-visible fixes, new features, documentation-only releases (patch), API additions (minor).

**Changelog:** [README.md](../README.md) § Changelog.

---

## Methodology / metric schema phases (research line)

These describe **scientific scope**, not Python package semver:

| Label | Meaning | Code constant |
|-------|---------|---------------|
| `3.0.0-strict-symbolic` | Removed Stevens' Law, psychoacoustic paths, perceptual interval weighting | historical |
| `4.0.0-strict-symbolic` | Removed combination-tone / resultant-tone analysis | `METRIC_SCHEMA_VERSION` in `core/defaults.py` |

Outputs embed `metric_schema_version` (currently **`4.0.0-strict-symbolic`**) in metadata and replication JSON. This is **independent** of package version `1.1.1`.

See [MIGRATION.md](MIGRATION.md) for phase history.

---

## Other version fields (do not confuse with package release)

| Field | Example | Purpose |
|-------|---------|---------|
| `benchmark_version` | `1.2.0` in `benchmarks/corpus/manifest.json` | Benchmark corpus layout schema |
| `manifest_version` | `1.1.1` in `replication/benchmark_manifest.json` | Replication manifest schema |
| `annotation_protocol_version` | `1.0.0` in score annotation JSON | Expert-rating file format |
| `audit_version` | `1.0.0` in instrument metadata audit | Instrument audit export format |
| `rubric_version` | `2.0.0` in score-only upgrade rubric | Rubric scoring JSON |

---

## Consistency checklist (maintainers)

When cutting a release **1.1.x**:

1. Update `[project].version` in `pyproject.toml`
2. Update `PACKAGE_VERSION` in `core/version.py`
3. Add README changelog entry
4. Update `docs/API.md` footer package version
5. Run tests (optional: `tests/test_version_consistency.py`)

When changing methodology scope (e.g. new strict-symbolic phase):

1. Bump `METRIC_SCHEMA_VERSION` in `core/defaults.py`
2. Update [MIGRATION.md](MIGRATION.md) and manuals — **do not** reuse package semver for this

---

*Last updated: 2026-06-01 (package 1.1.1, MIT license file added).*
