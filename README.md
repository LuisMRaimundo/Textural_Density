# Textural Density - Musical Density Analysis Application

**Version:** 1.1.3  
**Status:** Active Development  
**License:** [MIT](LICENSE)  
**Documentation:** [Mathematical manual](docs/MATHEMATICAL_MANUAL.md) · [Technical manual](docs/TECHNICAL_MANUAL.md) · [Migration guide](docs/MIGRATION.md) · [Versioning & license](docs/VERSIONING.md) · [API](docs/API.md) · [Instrument profile importer](docs/instrument_profile_importer.md) · [QA checklist](docs/qa_checklist.md)

> **Versioning:** Package release **1.1.3** (`pyproject.toml`) is separate from methodology phases **3.0.0** / **4.0.0-strict-symbolic** (`METRIC_SCHEMA_VERSION`). See [docs/VERSIONING.md](docs/VERSIONING.md).

---

## Scientific scope

> **Textural Density** is a strictly symbolic score-analysis framework. It computes analytical density indices from **notated events** at runtime — vertical simultaneities, intervals, register, dynamics, instruments, Qty/player counts, and other score-derived density metrics — **without audio input**. Interval, register, and event metrics are score-derived. **Instrument density** where GPR modules exist applies **externally sourced acoustic amplitude metadata** (sparse tables in `instrumentos/`, interpolated by GPR) to notated pitch and dynamic markings — this is not live acoustic analysis. The project does **not** analyse live audio, process waveforms, run FFT/STFT, extract spectral partials, compute EWSD, use H/I/S constructs, or generate resultant tones, combination tones, or other non-notated virtual pitches. It does **not** implement psychoacoustic or perceptual modelling. Written dynamics such as p, mf, and ff are **symbolic score markings**, not measured loudness or SPL.

**Removed in 3.0.0-strict-symbolic:** Stevens' Law power-law compression, psychoacoustic corrections, and perceptual interval weighting.

**Removed in 4.0.0-strict-symbolic:** Combination-tone / resultant-tone analysis (`calculate_combination_tones` and related keys). Analytical inputs containing those keys raise validation errors. `verified_by_tests` for many constructs; full `corpus_replicated` status requires a representative benchmark corpus. External expert ratings are **optional** empirical extensions, not required for the score-only line. See [`docs/revised_path_to_90_score_only.md`](docs/revised_path_to_90_score_only.md) and [`docs/score_only_upgrade_rubric.md`](docs/score_only_upgrade_rubric.md) (v2.0.0).

---

## Overview

**Textural Density** is an **independent symbolic textural-density analyser**. It is score- and information-based — not a live audio or signal-processing pipeline.

The **public research API** lives in `core/` (`core.pipeline.calculate_metrics`). **`data_processor.py` is not an analytical module** — it re-exports `core.pipeline.calculate_metrics` and legacy helpers only; all metric computation runs in `core/pipeline.py`. The GUI routes through `AnalysisController` → `adapters/gui_adapter` → `AnalysisRequest` → core pipeline (see [`docs/qa_checklist.md`](docs/qa_checklist.md)).

### Key Features

- **Vertical density metrics** — pitch-structure density (distinct bins), pressure-equivalent instrument density (RSS), linear sonic mass, composite total; Qty affects mass/player count only, not pitch polyphony
- **Qty semantics** — incoherent source addition; row-splitting invariant; documented in [`docs/MATHEMATICAL_MANUAL.md`](docs/MATHEMATICAL_MANUAL.md) §F
- **Epistemic metadata** — every metric labelled (`source_type`, `validation_status`, warnings)
- **Interpretable subindices** — registral, orchestration, harmonicity proxies, etc.
- **Temporal score analysis** — `analyze_score()` for timed XML/MIDI
- **Instrument registry** — orchestral profile scaffolding (~28 entries); **metadata corpus incomplete** — many instruments use coarse fallbacks; GPR tables for a few modules only
- **Auxiliary Excel importer** — offline human curation of instrument profiles (`tools/import_instrument_profiles_from_excel.py`); not part of the analytical core; runtime does not read raw `.xlsx`
- **MusicXML concert pitch** — `<transpose>` (chromatic + octave-change) applied for transposing instruments; `written_pitch` vs `sounding_pitch` on timed events
- **Verification scaffolding** — **689 tests** (687 passing; GitHub Actions + CircleCI green); strict pitch parsing, pitch-interpolation, interval-density contracts, instrument scaffold tests, and frozen benchmarks (five project-authored MusicXML excerpts)
- **Tkinter GUI** — panel/controller composition; audited adapter boundary (`tests/test_gui_architecture.py`)

---

## Installation

### Requirements

- Python 3.8+
- Required packages (see `requirements.txt`):
  - numpy
  - pandas
  - matplotlib
  - scipy
  - tkinter (usually included with Python)

### Setup

```bash
# Clone or navigate to the project directory
cd Textural_Density

# Option A: Install dependencies and run directly
pip install -r requirements.txt
python Main.py

# Option B: Install as package then run from anywhere (console script: densidade-vertical)
pip install -e .
densidade-vertical

# Option C: Use the launcher script (sets working directory)
python run.py
```

### Building a standalone executable (Windows)

To build a single-folder or one-file `.exe` so users can run the app without installing Python:

```bash
pip install pyinstaller
python build_exe.py
```

Or run PyInstaller directly:

```bash
pyinstaller --name densidade-vertical --windowed --onefile run.py
```

The executable will be in `dist/densidade-vertical.exe`. For a one-folder bundle (faster startup), edit `build_exe.py` and use `--onedir` instead of `--onefile`. See [PyInstaller docs](https://pyinstaller.org/) for options.

---

## Quick Start

1. **Launch the application:**
   ```bash
   python Main.py
   ```

2. **Enter musical data:**
   - Check the boxes for active notes
   - Select note, octave, cents (optional)
   - Choose dynamics and instruments
   - Set number of instruments

3. **Configure analysis:**
   - Adjust weight factor slider

4. **Calculate:**
   - Click "Calculate" button
   - View results in the results tab
   - Check advanced metrics in the metrics tree
   - Generate scientific reports if needed

---

## Architecture

The research API is **core-native**. **`core/pipeline.py`** is the single source of truth for vertical-slice analysis: it validates input, aggregates events by pitch, computes instrument/orchestration mass, interval compactness, registral span, spectral proxies, subindices, composite density, and attaches epistemic metadata — without importing Tkinter or GUI code.

**`data_processor.py`** is a **compatibility shim only** (~32 lines). It re-exports `calculate_metrics` / `calcular_metricas` from `core.pipeline` plus legacy helpers in `data_processor_legacy.py` (file I/O, validation text, note normalisation). **Do not add new analytical logic there** — extend `core/` instead.

Satellite modules (`densidade_intervalar.py`, `spectral_analysis.py`, `xml_loader.py`, …) are focused libraries called from core.

```
Textural_Density/
├── core/                      # Research API (canonical)
│   ├── pipeline.py            # calculate_metrics — orchestrates full vertical slice
│   ├── pitch_aggregation.py   # Distinct-bin pitch structure + Qty invariants
│   ├── orchestration.py       # One-player densities, orchestral balance inputs
│   ├── defaults.py            # Shared research API defaults
│   ├── metrics_metadata.py    # Epistemic labelling (source_type, validation_status)
│   ├── subindices.py          # Interpretable decomposition
│   ├── score_analysis.py      # analyze_score() — timed multi-slice analysis
│   └── reporting.py           # Interpretability + sensitivity
├── validation/                # Verification / validation scaffolding (not GUI stats)
├── benchmarks/                # Five project-authored MusicXML excerpts + frozen outputs
├── instrumentos/              # Instrument registry + GPR/coarse modules (metadata layer incomplete)
├── tools/                     # Auxiliary offline tools (Excel profile importer — not runtime)
├── gui/                       # Tkinter panels + AnalysisController (no metric math)
├── adapters/                  # gui_adapter → AnalysisRequest → core.pipeline
├── score_io/                  # Result export
├── xml_loader.py              # Custom XML + MusicXML (transpose → concert pitch)
├── Main.py                    # Tkinter application entry
├── data_processor.py          # Shim: re-exports core.pipeline + legacy helpers only
├── data_processor_legacy.py   # Legacy I/O and validation text (not the metric pipeline)
├── densidade_intervalar.py    # Interval density library
├── spectral_analysis.py       # Spectral metadata proxies
└── tests/                     # 689 tests, regression baseline, quality gates
```

**Call path (GUI):** `Main.py` → `AnalysisController` → `adapters/gui_adapter.build_analysis_request` → `core.pipeline.calculate_metrics`.

**Call path (programmatic):** `from core import calculate_metrics` (preferred) or `from core.pipeline import calculate_metrics`.

**Call path (legacy scripts):** `from data_processor import calculate_metrics` — same function object, forwarded from core.

Optional future extractions: [docs/legacy_pipeline_extraction.md](docs/legacy_pipeline_extraction.md).

### Key Components

| Component | Role |
|-----------|------|
| `core.pipeline.calculate_metrics` | **Canonical** vertical-slice analysis (research entry point) |
| `core.analyze_score` | Multi-slice timed score analysis |
| `adapters/gui_adapter.py` | GUI → `AnalysisRequest` → core; aligned defaults |
| `data_processor.py` | **Compatibility only** — re-exports `core.pipeline`; no independent metric logic |
| `data_processor_legacy.py` | Legacy save/validate/normalise helpers used by shim and GUI text |
| `xml_loader.py` | Custom densidade XML + MusicXML loader (transpose-aware) |
| `validation/` | Synthetic verification — **not** empirical validation |
| `DensityAnalyzerApp` | GUI orchestrator (`Main.py`) |

---

## Scientific scope

| Category | What Textural Density provides |
|----------|-------------------|
| **Score-derived** | Pitch-class structure, event counts, registral spread from symbolic input |
| **Metadata proxies** | Instrument GPR tables, spectral moments weighted by symbolic densities |
| **Calibrated proxies** | Interval decay λ (partially calibrated against consonance ratings) |
| **Formal validation** | Regression/property tests, benchmark replication scaffolding (`verified_by_tests`) |
| **Optional empirical** | Expert annotations, listening tests — only if pursuing judgment-prediction research |
| **Not provided** | Measured audio spectra, SPL, timbre measurement, live waveform/FFT/STFT analysis, SoundSpectrAnalyse-style signal processing, mandatory human-rating validation, final cross-instrument acoustic calibration |

**Instrument metadata status:** External acoustic/proxy tables are **incomplete** and curated gradually. Missing or coarse instrument data are **expected** at this stage — not runtime bugs when fallback labels and provenance remain honest. Do not treat current GPR modules (e.g. flauta, clarinete, oboe) as final scientific reference corpora.

**Sounding-pitch rule:** All instrument metadata imported from Excel (or derived tables) must be in **real sounding / concert pitch**. Example: a B♭ clarinet written D4 sounds C4 — the metadata table stores **C4 / MIDI 60**, not written D4 / MIDI 62. Transposition applies during **score parsing** only; the Excel importer does **not** transpose acoustic rows.

**Auxiliary Excel importer:** Human-facing curation format only. Validates workbooks and can emit canonical JSON/audit artefacts. Does not change density formulas or runtime lookup logic. Real curated `.xlsx` files should normally stay outside Git. See [`docs/instrument_profile_importer.md`](docs/instrument_profile_importer.md).

Symbolic spectral summaries use **notated/input pitches only** — not measured audio spectra or virtual/resultant tones.

---

## Usage Examples

### Basic Calculation

```python
from core import calculate_metrics

input_data = {
    'notes': ['C4', 'E4', 'G4'],
    'dynamics': ['mf', 'f', 'mf'],
    'instruments': ['flauta', 'clarinete', 'flauta'],
    'num_instruments': [1, 2, 1],
    'weight_factor': 0.5,
}

resultados, densidades, pitches = calculate_metrics(input_data)
print(f"Total density: {resultados['density']['total']:.4f}")
print(f"Input pitches only: {len(pitches)} notes")
```

---

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_removed_perceptual_options.py -v
```

### Test Coverage

Current status: **689 tests** in suite (**687 passing**); GitHub Actions (`test` 3.10/3.11, `quality`) and CircleCI (`tests-3.10`, `tests-3.11`) green.

**Known unrelated failures (outside strict-pitch scope):**

- `tests/test_benchmark_corpus.py` — pre-existing frozen output drift (`excerpt_005`)
- `tests/test_version_consistency.py` — installed package version mismatch when an older editable install is present (e.g. 1.1.1 vs `pyproject.toml` 1.1.3)

Tiered CI policy (see [CONTRIBUTING.md](CONTRIBUTING.md)):

- **`core/` + `validation/`:** ≥ 80% (enforced in CI)
- **Full repository:** ~78% while legacy modules remain; gate at 63%
- **Mypy:** clean on `core/` and `validation/` only (`--follow-imports=skip`)

---

## Configuration

### Key Configuration Files

- **`config.py`**: Centralized configuration
  - Dynamic levels
  - Instrument lists
  - UI settings
  - Calculation parameters

- **`config/density_params.json`**: Calibration parameters
  - Lambda values
  - Calibration data

---

## Scientific Background

Metrics decompose **vertical simultaneity** into interval compactness, orchestration mass, registral spread, and composite heuristics. **Qty (player count)** affects mass and pressure-equivalent instrument density only — not pitch polyphony or vertical pitch-structure metrics. See [MATHEMATICAL_MANUAL.md](docs/MATHEMATICAL_MANUAL.md) for formulas and epistemic taxonomy.

**GUI analysis path:** `Main.py` → `AnalysisController` → `adapters/gui_adapter` → `AnalysisRequest` → `core.pipeline.calculate_metrics`. See [`docs/qa_checklist.md`](docs/qa_checklist.md) for Qty semantics sign-off.

**We do not claim:** full empirical validation, measured acoustic analysis, or that proxy metrics equal perception.

---

## Contributing

See `CONTRIBUTING.md` for guidelines.

### Code Style

- Use Google-style docstrings
- Follow PEP 8
- Add type hints
- Write tests for new features

---

## License

MIT — see [LICENSE](LICENSE) and [docs/VERSIONING.md](docs/VERSIONING.md).

---

## Changelog

### Version 1.1.3 (2026-06-21)
- Strict pitch parsing: `InvalidPitchNotation`, `ParsedPitch`, `parse_pitch_strict()`, `note_to_midi_strict()`
- Decimal/signed cents (`+7.5c`, `+125c`, `+7¢`); chromatic-only metadata canonical with duplicate MIDI validation
- Instrument lookup uses strict parsing; invalid targets return `target_midi=None` with provenance fallback
- Tests: `tests/test_microtonal_strict.py` and extended `tests/test_pitch_interpolation.py`

### Version 1.1.2 (2026-06-21)
- Unified continuous-pitch interpolation for instrument metadata (`instrumentos/pitch_interpolation.py`)
- Chromatic-only acoustic tables are sufficient; quarter-tones and cents resolved at runtime in MIDI space
- Provenance labels distinguish exact, interpolated, extrapolated, and fallback density values
- `coarse_default` uses `microtonal.note_to_midi` for microtonal notes; 19 new tests in `tests/test_pitch_interpolation.py`

### Version 1.1.1 (2026-06-01)
- MusicXML `<transpose>` support: concert pitch from chromatic + octave-change offsets
- `InstrumentEvent.written_pitch` populated when written and sounding pitch differ
- Benchmark corpus expanded to five excerpts (transpose persistence, multi-instrument dynamics)
- CI workflow fixes (headless tkinter smoke check); 521+ tests; documentation aligned with core-native architecture
- **LICENSE** (MIT) added; [docs/VERSIONING.md](docs/VERSIONING.md) clarifies package vs methodology versions; `core.version` single source at runtime

### Version 4.0.0-strict-symbolic (2026-05-21)
- Hard removal of combination-tone / resultant-tone analysis
- Post-removal consolidation: dead code, stale docs, obsolete examples cleaned
- See [Migration guide](docs/MIGRATION.md)

### Version 3.0.0-strict-symbolic (2026-05-20)
- Hard removal of Stevens' Law, psychoacoustic corrections, perceptual interval weighting
- Weighted density is linear min-max blend only

### Version 1.1.0 (2026-05-20)
- Twelve-phase upgrade: `core/` API, epistemic metadata, subindices, temporal analysis, instrument registry, validation framework, quality gates
- See [Migration guide](docs/MIGRATION.md) for backward compatibility

### Version 1.0.0 (2025-12-27)
- Initial release
- Microtonal support
- Scientific reporting

---

## Support

For issues and questions, please [create an issue] or [contact maintainers].

---

**Last Updated:** 2026-06-21

