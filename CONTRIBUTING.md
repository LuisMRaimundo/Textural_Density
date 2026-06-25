# Contributing to Textural Density

Thank you for contributing to the **Textural Density**. The research API lives in `core/`; `data_processor.py` is a compatibility shim. Read [docs/MIGRATION.md](docs/MIGRATION.md), [docs/qa_checklist.md](docs/qa_checklist.md), and [docs/legacy_pipeline_extraction.md](docs/legacy_pipeline_extraction.md) before large refactors.

---

## Development Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Unix:    source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -q --no-cov
```

Optional package install: `pip install -e .`

---

## Quality Gates (CI policy)

The CI workflow (`.github/workflows/tests.yml`) enforces **tiered** gates — not a single global 80% / full-repo mypy bar.

| Scope | Requirement |
|-------|-------------|
| **All tests** | Must pass on Python 3.10–3.11 (`pytest tests/ -m "not slow"`) |
| **`core/` + `validation/` coverage** | ≥ **80%** (`pytest -o addopts= --cov=core --cov=validation --cov-fail-under=80`) |
| **Full repository coverage** | ≥ **63%** (current verified ~85% after PR #14) |
| **Mypy** | Zero errors on `core` and `validation` with `--follow-imports=skip` |
| **Slow perf test** | 50-note slice < 5 s (marked `@pytest.mark.slow`) |

**Verified suite size (2026-06-25):** 862 tests collected; 861 non-slow + 1 slow; GitHub Actions and CircleCI green on Python 3.10 and 3.11.

**We do not claim** full-repository mypy cleanliness, perceptual validation, or empirical proof that CDM values match perceived density.

### Local commands

```bash
# Fast suite
pytest tests/ -q --no-cov -m "not slow" -o addopts=

# String musicological battery
pytest -m musicological -q

# String modules directly
pytest tests/test_string_module_contracts.py tests/test_string_source_reproducibility.py \
  tests/test_string_musicological_invariants.py tests/test_string_score_scenarios.py -q

# Note-label normalization
pytest tests/test_notes.py -q

# Core + validation coverage gate
pytest tests/ -q -o addopts= --cov=core --cov=validation --cov-fail-under=80

# Type check (core/validation only)
mypy core validation --ignore-missing-imports --follow-imports=skip

# Import smoke
python -c "import importlib; importlib.import_module('Main'); print('OK')"
```

GUI code (`Main.py`, `gui_components.py`) is **best-effort** for typing unless CI expands later.

---

## Scientific Contribution Rules

1. **Score/information input only** — no audio waveform analysis; do not introduce acoustic-measurement claims.

2. **Dynamics (`p`, `mf`, `ff`, `mp`, …)** are symbolic/ordinal markings or modelled GPR values — not measured SPL. Source-table anchors are **pp, mf, ff** only.

3. **Dynamic interpolation changes** must preserve the production GPR path unless a dedicated policy PR explicitly adopts an alternative. Diagnostic linear/PCHIP references must not be described as production methods.

4. **New metrics** must include in metadata:
   - `source_type` (`score_derived`, `metadata_proxy`, `calibrated_proxy`, or `empirical`)
   - `validation_status`
   - `confidence`
   - `interpretation`, and where applicable `warnings` / `assumptions`

5. **New proxy metrics** must document assumptions and warnings; do not invent detailed instrument spectra.

6. **No metric** may use `externally_validated` unless expert/listening/corpus data exist under `validation/`.

7. **Distinct constructs** must remain separate (interval compactness ≠ roughness ≠ harmonicity ≠ timbral heterogeneity ≠ temporal density).

8. **No low-confidence proxy** should silently dominate the composite score without explicit configuration.

9. **No new default** may silently change scientific output. Align with [core/defaults.py](core/defaults.py) and update tests/docs/migration notes.

10. **No Tkinter imports** inside `core/` or `validation/`.

11. **Combination-tone analysis** was removed in 4.0.0-strict-symbolic; do not reintroduce virtual/resultant tone generation.

12. **GUI analysis** must use `AnalysisController` → `adapters.gui_adapter` → `AnalysisRequest` → `core.pipeline`. Do not call `data_processor.calculate_metrics` from GUI code.

13. **Qty (player count)** changes must follow [docs/qa_checklist.md](docs/qa_checklist.md) Qty semantics sign-off and update frozen outputs when formulas change.

14. **MusicXML intake** changes must update [docs/TECHNICAL_MANUAL.md](docs/TECHNICAL_MANUAL.md) §7.4, [docs/MIGRATION.md](docs/MIGRATION.md), and transpose tests in `tests/test_xml_loader.py`.

15. **Instrument tables** (GPR modules) require durable source provenance (`INSTRUMENT_SOURCE`, `docs/instrument_acoustic_sources.md`). Prefer repository-relative anchors (`docs/instrument_acoustic_sources.md#<module>`) over machine-local paths.

16. **Media workbook labels:** duplicate suffixes such as `F4 (2)` must be normalized via `normalize_media_note_label()` before canonical pitch parsing. Do not treat interpolation outputs as source data.

17. **Source reconstruction:** where Zenodo `*_Media` workbooks are available, supply tests comparing committed `spectral_data` to workbook rows (`tests/test_string_source_reproducibility.py` pattern). CI skips reconstruction when workbooks are absent.

18. **Exact anchor tests:** every committed table cell should match `calcular_densidade(pitch, dynamic)` at pp/mf/ff anchors.

19. **Registry aliases:** test both English and Portuguese alias resolution when applicable (`violino`/`violin`, `violoncelo`/`cello`, etc.).

20. **Technique honesty:** registry `supported_techniques` may list pizzicato, tremolo, harmonics, or mute, but current CDM tables represent **arco sustain** material only unless separate technique-specific tables exist.

21. **Scientific data changes** (formulas, `spectral_data`, registry ranges, provenance metadata) require human scientific review — not documentation-only PRs.

### Output-change checklist

Any change affecting scientific output must update **at least one** of:

- tests (including regression baseline if intentional),
- [docs/MATHEMATICAL_MANUAL.md](docs/MATHEMATICAL_MANUAL.md) or [docs/TECHNICAL_MANUAL.md](docs/TECHNICAL_MANUAL.md),
- report / `metric_metadata`,
- [docs/MIGRATION.md](docs/MIGRATION.md),
- [docs/qa_checklist.md](docs/qa_checklist.md) (Qty / GUI path when applicable).

---

## Coding Standards

- PEP 8, Google-style docstrings, type hints on new public functions
- Match existing module conventions
- Minimal scoped diffs — no drive-by refactors

Formatting (optional locally): `black`, `isort`

---

## Writing Tests

- Place tests in `tests/test_<module>.py`
- Prefer unit tests for pure helpers; integration tests for pipelines
- GUI: test `gui/analysis_adapter.py` and config normalizers — not full Tk rendering
- Regression: `tests/test_regression_baseline.py` — update fixture only for intentional formula changes
- **String GPR modules:** use `@pytest.mark.musicological` for module contracts, source reconstruction, pitch spelling, GPR diagnostics, and score scenarios (`tests/test_string_*.py`)
- **Media labels:** test `normalize_media_note_label()` when adding workbook ingestion (`tests/test_notes.py`)

Epistemic scope: tests verify software contracts and source consistency — not perceptual or psychoacoustic validation of CDM.

---

## Legacy Modules

| Module | Status |
|--------|--------|
| `data_processor.py` | Active legacy pipeline; wrapped by `core.pipeline` |
| `statistical_validation.py` | **Deprecated** — use `validation/` for research; emits `DeprecationWarning` at call time |
| `validation/` | Research verification scaffolding |

Do not extend `statistical_validation.py` for new research features.

---

## Pull Request Process

1. Branch from `main` / `master`
2. Implement change + tests + docs (as required by scientific rules above)
3. Run `pytest tests/ -q --no-cov -m "not slow"`
4. If touching `core/` or `validation/`, run the coverage and mypy commands above
5. Describe epistemic impact in the PR (proxy vs score-derived, default changes, etc.)

---

**Thank you for contributing.**
