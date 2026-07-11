# Instrument models and registry



> **Metadata status:** The instrument corpus is **incomplete**. Many names resolve to coarse fallbacks; only a few modules embed sparse GPR tables. External acoustic/proxy metadata are curated gradually via the auxiliary Excel importer — not live analysis. Current tables must not be read as final calibrated models.



This package provides **instrument density** for the vertical density pipeline. Each note in a chord uses **its own** instrument module (Phase 2+), resolved via `instrumentos/registry.py` and loaded through `get_instrument_module()`.



## Acoustic-source metadata in instrument scripts



Dedicated modules embed **sparse CDM tables** from external sources (partial digitization — **work in progress**, not final reference data). Tables are stored as `spectral_data` and interpolated by Gaussian-process regression (GPR) for intermediate dynamics.



| Module | Table | Source |

|--------|-------|--------|

| `flute.py` | `spectral_data` | IOWA+ORCH flute sustain CDM medians (Zenodo workbook) |

| `clarinet.py` | `spectral_data` | IOWA+ORCH clarinet sustain CDM medians (Zenodo workbook) |

| `oboe.py` | `spectral_data` | IOWA+ORCH oboe sustain CDM medians (Zenodo workbook) |

| `bassoon.py` | `spectral_data` | IOWA+ORCH bassoon sustain CDM medians (Zenodo workbook) |

| `trumpet.py` | `spectral_data` | IOWA+ORCH trumpet sustain CDM medians (Zenodo workbook) |

| `violin.py`, `viola.py`, `cello.py`, `double_bass.py` | `spectral_data` | IOWA+ORCH arco sustain CDM medians (Zenodo workbooks) |
| `violin_sordina.py` | `spectral_data` | IOWA+ORCH arco sordina CDM (`combined_sord_collection_raw`, pp/mf/ff) |
| `violin_sul_ponticello.py`, `violin_art_harm.py` | `spectral_data` | Measured **mf only**; pp/ff extrapolated via `mf_anchor_dynamic_extrapolation.py` (violin arco ratio transfer) |
| Registry-only entries | — | Coarse register/dynamic model (`coarse_default.py`) |



**Important distinction:** the **analysis pipeline is score-only at runtime** (no audio input). The **instrument scripts** carry pre-loaded acoustic metadata that is looked up from notated pitch and dynamic markings.

**Media ingestion:** Zenodo `*_Media` workbook rows may use duplicate suffix labels (e.g. `F4 (2)`). Offline tooling applies `utils.notes.normalize_media_note_label()` before canonical parsing. See [instrument_acoustic_sources.md](../docs/instrument_acoustic_sources.md).

**Technique honesty:** registry `supported_techniques` lists organological capabilities. GPR modules declare `INSTRUMENT_SOURCE.source_technique` and `table_supported_techniques` for the committed numerical table only (e.g. `arco_sustain`, `arco_sordina`, `arco_sul_ponticello`, `arco_artificial_harmonic`, `ordinary_sustain`). Pizzicato, tremolo, harmonics, mute, and similar techniques are not acoustically modelled unless separate technique-specific tables exist.

**mf-only technique modules:** `violin_sul_ponticello.py` and `violin_art_harm.py` commit measured mf rows in `MF_MEASURED`. pp and ff GPR anchors are extrapolated per note from violin arco pp/mf and ff/mf ratios (`instrumentos/mf_anchor_dynamic_extrapolation.py`). All other dynamics (`pppp` … `ffff`, including `mp`) are GPR-modelled in the production pipeline — same ordinal model as full-table modules. Direct `calcular_densidade` calls on these modules collapse non-anchor markings to the nearest table row; GUI / `calculate_metrics` uses GPR.

**Range semantics:** distinguish `source_table_span` (committed table), `sounding_range` (validation), and `comfortable_range` (conservative orchestration band). Example: double bass table spans E1–C5 while comfortable range is G1–G3.

Audit: `python tools/audit_instrument_metadata_range_resolution.py` → `reports/instrument_metadata_range_resolution_audit.*`

**String verification (PR #13/#14):** musicological contract tests (`pytest -m musicological`) cover module contracts, source reconstruction (local workbooks), pitch spelling, GPR diagnostics, and score scenarios for violin, viola, cello, and double bass.



**GUI vs registry IDs:** The Tkinter GUI shows **English display names** (Flute, Violin, …). Registry `instrument_id` keys remain stable internal identifiers (e.g. `flauta`, `violino`) with English aliases (`flute`, `violin`, …) and English **module filenames** (`flute.py`, `violin.py`, …).



---



## Module contract



Every loadable instrument module must expose:



```python

def calcular_densidade(nota: str, dinamica: str) -> float:

    """Density for one note at one dynamic marking."""



def predict_intermediate_dynamics(

    pitches: list,

    pp_values: list,

    mf_values: list,

    ff_values: list,

) -> dict[str, list[float]]:

    """Interpolate pp/mf/ff for dynamics not in the table."""

```



Unknown dynamics are normalised to `mf` or interpolated via `predict_intermediate_dynamics`.



**Pitch lookup:** `instrumentos/pitch_interpolation.py` provides unified continuous-pitch resolution; `instrumentos/spectral_lookup.py` wraps it for instrument modules. **Chromatic-only tables are the canonical model** — quarter-tones, arbitrary cents (`D3+7c`, `C4+125c`), and arrow notation are inferred at runtime via `microtonal.note_to_midi_strict()` and linear/PCHIP interpolation between chromatic anchors. Manually pasted microtonal rows are optional curated exact overrides only.



Strict pitch parsing (`note_to_midi_strict`, `parse_pitch_strict`) raises `InvalidPitchNotation` on malformed input and **never** falls back to C4. Legacy `note_to_midi()` remains permissive for backward compatibility; research/instrument paths use strict parsing.



Lookup order:



1. **Exact** — literal table key match (curated microtonal override rows, if present)

2. **Normalized exact** — enharmonic / equivalent MIDI match (e.g. `C♯4` ≡ `C#4`)

3. **Continuous interpolation** — local linear between bracketing chromatic anchors; PCHIP when ≥4 in-range anchors and `auto` mode



**Table validation:** duplicate MIDI coordinates with identical dynamic values are deduplicated deterministically; conflicting duplicates (e.g. `C#4` vs `Db4` with different `mf`) raise `MetadataTableConflictError`.



Provenance labels (`exact`, `normalized_exact`, `interpolated`, `extrapolated`, `fallback`) distinguish measured table entries from modelled microtonal estimates. Interpolated values are **not** labelled as directly measured.



Range policy: never collapse to the same pitch class in a distant octave (e.g. D♯6 ≠ D♯4). Deviations >1 semitone outside the table log `WARNING`; >1 octave log `ERROR` and use fallback (default 5.0) instead of silent misleading extrapolation.



Dynamic interpolation — **production GPR only** (`create_dynamic_gpr()`, `GPR_RANDOM_STATE = 0`) — remains separate from pitch interpolation; each dynamic column is modelled independently over pitch. Piecewise linear and PCHIP appear only in diagnostic audit tools, not in `calcular_densidade` lookup.

**Source vs modelled dynamics:** `INSTRUMENT_SOURCE.dynamic_levels` remains `("pp", "mf", "ff")` — the only columns in committed CDM tables. Modelled dynamics (`p`, `mp`, `f`, `pppp`, `ppp`, `fff`, `ffff`) are GPR predictions at fixed ordinal coordinates via `instrumentos/gpr_dynamic_interpolation.py` (Matérn kernel). `mp` uses coordinate **4.5** between `p` (4.0) and `mf` (5.0) and is **not** mapped to `mf`. These coordinates are ordinal modelling controls, not dB, SPL, or perceptual intensity; values need not be monotonic across dynamics.

**Determinism and diagnostics:** GPR is deterministic by construction (PR #22). Model-quality and method-comparison audits (`tools/audit_gpr_model_quality.py`, `tools/compare_dynamic_interpolation_methods.py`) document local method sensitivity — especially low-register strings — without changing production interpolation. Linear and PCHIP were diagnostic references only (PR #24); not adopted.



```python

from instrumentos.pitch_interpolation import resolve_density_from_table



result = resolve_density_from_table(spectral_data, "C4+50c", "mf", logger=logger)

# result.value, result.provenance, result.warnings

```



Per-event modules return **one-player** density $d^{(1)}$ for `(note, dynamic)`. Quantity scaling is applied at slice level in `core/quantity_scaling.py` and `core/source_aggregation.py`:



- Pressure-equivalent instrument density: $\sqrt{\sum_j n_j (d_j^{(1)})^2}$

- Sonic mass: $\sum_j n_j d_j^{(1)}$



See [TECHNICAL_MANUAL.md](../docs/TECHNICAL_MANUAL.md) §3.3–§3.6.



---



## Resolution order (`get_instrument_module`)



1. **Registry alias** → dedicated `.py` module if `InstrumentProfile.module_name` is set and importable

2. **Registry entry without module** → `coarse_default.build_coarse_module(profile)` bound to that profile

3. **Legacy direct import** by raw lowercase module name

4. **Unknown name** → unknown coarse proxy with warning



Warnings propagate into `resultados["metric_metadata"]` with `source_type=external_acoustic_metadata` when GPR modules are used.



---



## Dedicated modules (acoustic-source tables + GPR)



| Instrument (GUI) | Module file | `profile_status` | Acoustic metadata |

|------------------|-------------|------------------|-------------------|

| **Flute** | `flute.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Clarinet** | `clarinet.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Oboe** | `oboe.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Bassoon** | `bassoon.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Trumpet** | `trumpet.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Violin** | `violin.py` | `literature_derived` | IOWA+ORCH arco CDM medians |
| **Violin sordina** | `violin_sordina.py` | `literature_derived` | IOWA+ORCH arco sordina CDM (pp/mf/ff) |
| **Violin sul ponticello** | `violin_sul_ponticello.py` | `literature_derived` | mf measured; pp/ff extrapolated (high uncertainty) |
| **Violin art harm** | `violin_art_harm.py` | `literature_derived` | mf measured G5–G7; pp/ff extrapolated (high uncertainty) |
| **Viola** | `viola.py` | `literature_derived` | IOWA+ORCH arco CDM medians |

| **Cello** | `cello.py` | `literature_derived` | IOWA+ORCH arco CDM medians |

| **Double bass** | `double_bass.py` | `literature_derived` | IOWA+ORCH arco CDM medians |



Regenerate CDM modules from Zenodo workbooks:



```bash

python tools/populate_td_importer_sheets_from_zenodo_media.py   # AcousticTable + provenance sheets

python tools/generate_instrument_modules.py                     # instrumentos/*.py

```



See [instrument_acoustic_sources.md](../docs/instrument_acoustic_sources.md) for workbook paths and citations.



---



## Registry profiles (`registry.py`)



~**28 orchestral instruments** are registered with metadata (family, ranges, register bands, `profile_status`, `uncertainty`, aliases). Examples:



| Family | IDs (sample) |

|--------|----------------|

| Woodwinds | `flauta`, `flautim`, `oboe`, `cor_anglais`, `clarinete`, `clarinete_baixo`, `fagote`, `contrafagote` |

| Strings | `violino`, `violino_sordina`, `violino_sul_ponticello`, `violino_art_harm`, `viola`, `violoncelo`, `contrabaixo` |

| Brass | `trompa`, `trompete`, `trombone`, `trombone_baixo`, `tuba` |

| Keyboard / harp | `piano`, `celesta`, `harpa` |

| Percussion | `timpanos`, `bombo`, `caixa`, `pratos`, `tamtam`, `vibrafone`, `marimba`, `metalofone` |



List programmatically:



```python

from instrumentos.registry import list_instrument_ids, list_profiles



print(list_instrument_ids())

for p in list_profiles():

    print(p.instrument_id, p.profile_status, p.module_name)

```



### `profile_status` values



| Status | Meaning |

|--------|---------|

| `literature_derived` | Dedicated script with external acoustic-source tables |

| `empirical_source` | Documented measured acoustic corpus in `source_notes` |

| `coarse_default` | Register/dynamic coarse proxy — **no acoustic script tables** |



### Aliases



Names are normalised (`lower`, spaces/hyphens → `_`). Display names (e.g. `Flute`, `Double bass`) also resolve. Examples: `horn` → `trompa`, `cello` → `violoncelo`, `flute` → `flauta`, `English horn` → `cor_anglais`.



---



## Coarse default (`coarse_default.py`)



Instruments **without** a dedicated acoustic script receive a **coarse register-based density proxy** derived from the profile’s sounding range, register bands, and dynamic curve. These profiles do **not** embed external acoustic amplitude tables. Outputs are finite and usable but labelled `confidence: low` in metadata.



---



## Adding a new instrument



### Option A — Full module with acoustic-source tables (preferred for research)



1. Add `new_instrument.py` in this directory implementing the module contract (copy structure from `violin.py` or `flute.py`).

2. Populate `spectral_data` with **chromatic anchors only** (e.g. `C4`, `C#4`, … × `pp`/`mf`/`ff`) from **documented external acoustic sources**; cite provenance in the module docstring and `registry.py` `source_notes`. Microtonal rows are optional — runtime interpolation fills quarter-tones and cents.

3. Use `lookup_spectral_density` from `instrumentos/spectral_lookup.py` inside `calcular_densidade` (see existing modules).



```python

REGISTRY["novo_instrumento"] = _profile(

    "novo_instrumento",

    "Display Name",

    "family_name",

    sounding=(low_midi, high_midi),

    comfortable=(low_midi, high_midi),

    status="literature_derived",  # or empirical_source when validated

    uncertainty="medium",

    module_name="new_instrument",  # English module filename

    source_notes="Sparse GPR table from [cite acoustic source].",

    aliases=("alias1", "alias2"),

)

```



4. Add tests under `tests/test_instrument_registry.py` or a dedicated module test.



The package auto-discovers `.py` files on import (excluding `registry.py`, `coarse_default.py`, `pitch_interpolation.py`, `spectral_lookup.py`, `__init__.py`).



### Option B — Registry-only (coarse proxy)



Add a `_profile(...)` entry without `module_name`. `get_instrument_module` will use `coarse_default` automatically. Suitable for orchestration tagging before acoustic-source tables exist.



---



## API quick reference



```python

from instrumentos import get_instrument_module, get_instrument_profile



mod = get_instrument_module("flute")  # or "flauta", "Flute"

d = mod.calcular_densidade("G4", "mf")



profile = get_instrument_profile("Horn")

print(profile.family, profile.profile_status, profile.uncertainty)

```



Used internally by `core/orchestration.py` during `calculate_metrics`.



---



## Related documentation



- [API.md](../docs/API.md) — `get_instrument_module`, registry functions

- [instrument_acoustic_sources.md](../docs/instrument_acoustic_sources.md) — workbook provenance per module

- [instrument_metadata_audit.md](../docs/instrument_metadata_audit.md) — profile provenance audit

- [MIGRATION.md](../docs/MIGRATION.md) — per-event instrument change (Phase 2)

- [TECHNICAL_MANUAL.md](../docs/TECHNICAL_MANUAL.md) §2.4 — instrument layer architecture

