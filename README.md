# Densidade Vertical - Musical Density Analysis Application

**Version:** 1.1.1  
**Status:** Active Development  
**License:** MIT (see [pyproject.toml](pyproject.toml))  
**Documentation:** [Mathematical manual](docs/MATHEMATICAL_MANUAL.md) · [Technical manual](docs/TECHNICAL_MANUAL.md) · [Migration guide](docs/MIGRATION.md) · [API](docs/API.md) · [QA checklist](docs/qa_checklist.md)

> **Versioning note:** The package release (`1.1.x`) is independent of internal methodology phases documented in the changelog (`3.0.0-strict-symbolic`, `4.0.0-strict-symbolic`). See [MIGRATION.md](docs/MIGRATION.md) §10.

---

## Scientific scope

> **Densidade Vertical** is a strictly symbolic score-analysis framework. It computes analytical density indices from notated events at **runtime** without audio input. Interval, register, and event metrics are score-derived. **Instrument density** where GPR modules exist applies **externally sourced acoustic amplitude metadata** (sparse tables in `instrumentos/`, interpolated by GPR) to notated pitch and dynamic markings — this is not live acoustic analysis. The project does **not** generate non-notated virtual pitches and does **not** implement psychoacoustic or perceptual modelling. Written dynamics such as p, mf, and ff are **symbolic score markings**, not measured loudness or SPL.

**Removed in 3.0.0-strict-symbolic:** Stevens' Law power-law compression, psychoacoustic corrections, and perceptual interval weighting.

**Removed in 4.0.0-strict-symbolic:** Combination-tone / resultant-tone analysis (`calculate_combination_tones` and related keys). Analytical inputs containing those keys raise validation errors. `verified_by_tests` for many constructs; full `corpus_replicated` status requires a representative benchmark corpus. External expert ratings are **optional** empirical extensions, not required for the score-only line. See [`docs/revised_path_to_90_score_only.md`](docs/revised_path_to_90_score_only.md) and [`docs/score_only_upgrade_rubric.md`](docs/score_only_upgrade_rubric.md) (v2.0.0).

---

## Overview

**Densidade Vertical** (Simultaneity Density Analyser / SDA) is a **score- and information-based** musical density analysis system. It computes vertical density metrics from **note names, dynamics, instruments, and player counts** — not from audio waveforms.

The **public research API** lives in `core/` (`core/pipeline.calculate_metrics`). `data_processor.py` is a backward-compatibility shim. The GUI routes through `AnalysisController` → `adapters/gui_adapter` → `AnalysisRequest` → core pipeline (see [`docs/qa_checklist.md`](docs/qa_checklist.md)).

### Key Features

- **Vertical density metrics** — pitch-structure density (distinct bins), pressure-equivalent instrument density (RSS), linear sonic mass, composite total; Qty affects mass/player count only, not pitch polyphony
- **Qty semantics** — incoherent source addition; row-splitting invariant; documented in [`docs/MATHEMATICAL_MANUAL.md`](docs/MATHEMATICAL_MANUAL.md) §F
- **Epistemic metadata** — every metric labelled (`source_type`, `validation_status`, warnings)
- **Interpretable subindices** — registral, orchestration, harmonicity proxies, etc.
- **Temporal score analysis** — `analyze_score()` for timed XML/MIDI
- **Instrument registry** — ~28 orchestral profiles; per-event instrument resolution
- **MusicXML concert pitch** — `<transpose>` (chromatic + octave-change) applied for transposing instruments; `written_pitch` vs `sounding_pitch` on timed events
- **Verification scaffolding** — 517+ tests; formal score-based validation via property tests and frozen benchmarks
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
cd "Densidade vertical"

# Option A: Install dependencies and run directly
pip install -r requirements.txt
python Main.py

# Option B: Install as package (Phase 5) then run from anywhere
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

The research API is **core-native**: `core/pipeline.py` implements `calculate_metrics`. `data_processor.py` is a **32-line compatibility shim** (re-exports + legacy GUI helpers). Satellite modules (`densidade_intervalar.py`, `spectral_analysis.py`, `xml_loader.py`, …) remain as focused libraries called from core.

```
Densidade vertical/
├── core/                      # Research API: pipeline, models, temporal analysis, metadata
│   ├── pipeline.py            # calculate_metrics (canonical implementation)
│   ├── defaults.py            # Shared research API defaults
│   ├── metrics_metadata.py    # Epistemic labelling
│   ├── subindices.py          # Interpretable decomposition
│   ├── score_analysis.py      # analyze_score()
│   └── reporting.py           # Interpretability + sensitivity
├── validation/                # Verification / validation scaffolding (not GUI stats)
├── benchmarks/                # Project-authored MusicXML excerpts + frozen outputs
├── instrumentos/              # Instrument registry + GPR/coarse modules
├── gui/                       # GUI helpers (file I/O, analysis adapter)
├── score_io/                  # Result export
├── xml_loader.py              # Custom XML + MusicXML (with transpose → concert pitch)
├── Main.py                    # Tkinter application entry
├── data_processor.py          # Backward-compatibility shim only
├── densidade_intervalar.py    # Interval density library
├── spectral_analysis.py       # Spectral metadata proxies
└── tests/                     # 517+ tests, regression baseline, quality gates
```

**Call path (GUI):** `Main.py` → `AnalysisController` → `adapters/gui_adapter` → `core.pipeline.calculate_metrics`.

**Call path (programmatic):** `from core import calculate_metrics` (includes `metric_metadata`).

Optional future extractions: [docs/legacy_pipeline_extraction.md](docs/legacy_pipeline_extraction.md).

### Key Components

| Component | Role |
|-----------|------|
| `core.calculate_metrics` | Single vertical-slice analysis (research entry point) |
| `core.analyze_score` | Multi-slice timed score analysis |
| `gui/analysis_adapter.py` | GUI → core bridge; aligned defaults |
| `data_processor.py` | Compatibility shim (re-exports `core.pipeline`) |
| `xml_loader.py` | Custom densidade XML + MusicXML loader (transpose-aware) |
| `validation/` | Synthetic verification — **not** empirical validation |
| `DensityAnalyzerApp` | GUI orchestrator (`Main.py`) |

---

## Scientific scope

| Category | What SDA provides |
|----------|-------------------|
| **Score-derived** | Pitch-class structure, event counts, registral spread from symbolic input |
| **Metadata proxies** | Instrument GPR tables, spectral moments weighted by symbolic densities |
| **Calibrated proxies** | Interval decay λ (partially calibrated against consonance ratings) |
| **Formal validation** | Regression/property tests, benchmark replication scaffolding (`verified_by_tests`) |
| **Optional empirical** | Expert annotations, listening tests — only if pursuing judgment-prediction research |
| **Not provided** | Measured audio spectra, SPL, timbre measurement, mandatory human-rating validation |

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

MIT — see [pyproject.toml](pyproject.toml).

---

## Changelog

### Version 1.1.1 (2026-06-01)
- MusicXML `<transpose>` support: concert pitch from chromatic + octave-change offsets
- `InstrumentEvent.written_pitch` populated when written and sounding pitch differ
- Benchmark excerpt_003 (Bb clarinet transpose regression)
- CI workflow fixes; 517 tests; documentation aligned with core-native architecture

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

**Last Updated:** 2026-06-01

