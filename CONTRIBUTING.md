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
| **All tests** | Must pass on Python 3.9–3.11 (`pytest tests/ -m "not slow"`) |
| **`core/` + `validation/` coverage** | ≥ **80%** (`pytest -o addopts= --cov=core --cov=validation --cov-fail-under=80`) |
| **Full repository coverage** | ≥ **63%** (legacy modules still lower) |
| **Mypy** | Zero errors on `core` and `validation` with `--follow-imports=skip` |
| **Slow perf test** | 50-note slice < 5 s (marked `@pytest.mark.slow`) |

**We do not claim** full-repository mypy cleanliness or 80%+ coverage across legacy modules until extraction completes.

### Local commands

```bash
# Fast suite
pytest tests/ -q --no-cov -m "not slow"

# Core + validation coverage gate
pytest tests/ -q -o addopts= --cov=core --cov=validation --cov-fail-under=80

# Type check (core/validation only)
mypy core validation --ignore-missing-imports --follow-imports=skip
```

GUI code (`Main.py`, `gui_components.py`) is **best-effort** for typing unless CI expands later.

---

## Scientific Contribution Rules

1. **Score/information input only** — no audio waveform analysis; do not introduce acoustic-measurement claims.

2. **Dynamics (`p`, `mf`, `ff`, …)** are symbolic/ordinal markings, not measured SPL.

3. **New metrics** must include in metadata:
   - `source_type` (`score_derived`, `metadata_proxy`, `calibrated_proxy`, or `empirical`)
   - `validation_status`
   - `confidence`
   - `interpretation`, and where applicable `warnings` / `assumptions`

4. **New proxy metrics** must document assumptions and warnings; do not invent detailed instrument spectra.

5. **No metric** may use `externally_validated` unless expert/listening/corpus data exist under `validation/`.

6. **Distinct constructs** must remain separate (interval compactness ≠ roughness ≠ harmonicity ≠ timbral heterogeneity ≠ temporal density).

7. **No low-confidence proxy** should silently dominate the composite score without explicit configuration.

8. **No new default** may silently change scientific output. Align with [core/defaults.py](core/defaults.py) and update tests/docs/migration notes.

9. **No Tkinter imports** inside `core/` or `validation/`.

10. **Combination-tone analysis** was removed in 4.0.0-strict-symbolic; do not reintroduce virtual/resultant tone generation.

11. **GUI analysis** must use `AnalysisController` → `adapters.gui_adapter` → `AnalysisRequest` → `core.pipeline`. Do not call `data_processor.calculate_metrics` from GUI code.

12. **Qty (player count)** changes must follow [docs/qa_checklist.md](docs/qa_checklist.md) Qty semantics sign-off and update frozen outputs when formulas change.

13. **MusicXML intake** changes must update [docs/TECHNICAL_MANUAL.md](docs/TECHNICAL_MANUAL.md) §7.4, [docs/MIGRATION.md](docs/MIGRATION.md), and transpose tests in `tests/test_xml_loader.py`.

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
