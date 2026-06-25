# Revised path to 90/100 — systematic score-only analysis

For Textural Density, **90/100 does not mean psychoacoustic calibration, listening-test validation, or mandatory expert human ratings**.

The research line is the **systematic score-only symbolic method**: formal construct definitions, reproducible score-derived outputs, internal consistency, canonical test cases, benchmark replication, transparent assumptions, and auditable architecture.

> **External human-rating studies** may be useful if the project later claims to predict expert or listener judgments. **They are not required** for the core score-only systematic research line.

## What 90/100 means here

| Criterion | Target |
|-----------|--------|
| Formal validation | Construct definitions, axioms, property/regression tests |
| Constructs | Event density, interval compactness, registral density, orchestration mass, timbral/orchestration complexity, temporal density, composite — **formally separated with metadata hooks** |
| Replication | **Representative licensed** symbolic corpus + frozen outputs + compare scripts |
| Architecture | Core-native auditable pipeline; GUI via typed adapter boundary |
| Claims | Score/information only — no audio, spectra, or hearing models |

## Current status (2026-06 — post validation layers + Excel template)

| Area | Status |
|------|--------|
| Defaults | Score-only mode global |
| Formal axioms | Documented + property tests (`test_formal_construct_axioms`, `test_quantity_scaling`) |
| Construct separation | Pitch aggregation vs orchestration mass vs Qty scaling — explicit modules |
| Core pipeline | **`calculate_metrics` in `core/pipeline.py`**; `data_processor` is shim |
| GUI boundary | `Main` → `AnalysisController` → `adapters/gui_adapter` → `AnalysisRequest` (tested) |
| Qty semantics | Incoherent RSS + linear mass; row-splitting invariance; docs + QA sign-off |
| Benchmark | Synthetic fixture + **5 project-authored excerpts** (`benchmarks/corpus/`); not yet a large licensed corpus |
| Test suite | **862 tests**; GitHub Actions + CircleCI green (Python 3.10/3.11) |
| Validation contracts | Interval-density, instrument scaffold, scientific/musicological plausibility, Excel importer tests |
| Instrument metadata | **Incomplete** — coarse fallbacks common; GPR modules for subset only; gradual curation via auxiliary Excel importer |
| Excel importer | Auxiliary offline tool + empty template on main; runtime does not read `.xlsx` |
| MusicXML transpose | **Implemented** — `<transpose>` → concert pitch; `excerpt_003`–`004` regression |
| Rubric estimate | **~89/100** (systematic line; licensed corpus still main gap) |

## Remaining for 92+ / reference implementation

1. Larger **representative licensed** benchmark corpus (beyond synthetic + 5 project-authored excerpts)
2. Official MusicXML/MIDI intake wired end-to-end in `reproduce_metrics.py`
3. Optional: merge `densidade_intervalar` into `core/` for full monolithic core layout
4. Optional: report integration for composite weight sensitivity section

## Completed since earlier drafts

- ~~Extract `calculate_metrics` to `core/pipeline.py`~~ ✅
- ~~Pitch-structure vs unison doublings~~ ✅
- ~~Qty^(3/2) removal; explicit quantity_scaling~~ ✅
- ~~GUI adapter audit + `test_gui_architecture.py`~~ ✅
- ~~Layered snapshot regression~~ ✅
- ~~MusicXML `<transpose>` → concert pitch + benchmark excerpts (`003`–`005`)~~ ✅

## Optional only

Expert annotations · IRR · human-rating correlation · listening tests · psychoacoustic calibration

## Commands

```bash
pytest tests/ -q
python replication/scripts/reproduce_metrics.py
python replication/scripts/compare_to_frozen_outputs.py
python validation/scripts/score_upgrade_rubric.py docs/examples/score_only_rubric_scores_example.json
```

See also: [`docs/qa_checklist.md`](qa_checklist.md), [`score_only_90_readiness_checklist.md`](score_only_90_readiness_checklist.md).

**Score reflects repository evidence, not aspiration.**
