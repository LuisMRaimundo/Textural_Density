# Instrument models and registry



> **Metadata status:** The instrument corpus is **incomplete**. Some names resolve to coarse fallbacks; table-backed modules are partial proxies. Full 10-dynamic ladders are committed for ordinary-sustain winds (flute, oboe, clarinet, bassoon), brass (trumpet, horn, tuba), arco strings, string technique/harmonic modules, and unpitched percussion. Ladders are **data-faithful** (Dynamics_predicter v1.5, 2026-08-08/09): measured pp/mf/ff anchors are committed verbatim, PCHIP interiors, tapered outers — they are *not* forced to be strictly monotone. External acoustic/proxy metadata are curated gradually — not live analysis.



This package provides **instrument density** for the vertical density pipeline. Each note in a chord uses **its own** instrument module (Phase 2+), resolved via `instrumentos/registry.py` and loaded through `get_instrument_module()`.



## Acoustic-source metadata in instrument scripts



Dedicated modules embed CDM tables from external sources (partial digitization — **work in progress**, not final reference data). Tables are stored as `spectral_data` and looked up by pitch × dynamic. Missing dynamics are **not** filled at runtime.



| Module | Table | Source |

|--------|-------|--------|

| `flute.py`, `clarinet.py`, `oboe.py`, `bassoon.py` | `spectral_data` (10 dynamics) | Dynamics_predicter `Results` ladders (IOWA+ORCH anchors) |
| `trumpet.py`, `horn.py`, `tuba.py` | `spectral_data` (10 dynamics) | Dynamics_predicter `Results` ladders (IOWA+ORCH sustain anchors) |
| `violin.py`, `cello.py`, `double_bass.py` | `spectral_data` (10 dynamics) | Dynamics_predicter `Results` ladders (IOWA+ORCH anchors) |
| `viola.py` | `spectral_data` (10 dynamics) | `OK_VIOLA_Arco ordinario_dynamics extrapolation.xlsx` Results ladder (measured pp/mf/ff anchors) |
| `violin_sordina.py` | `spectral_data` (10 dynamics) | `OK_VIOLIN_con sordina_dynamics extrapolation.xlsx` Results ladder (measured pp/mf/ff anchors) |
| `violin_sul_tasto.py` | `spectral_data` (10 dynamics) | `OK_VIOLIN_sul_tasto_dynamics extrapolation.xlsx` Results ladder (measured pp/mf/ff anchors) |
| `violin_sul_ponticello.py` | `spectral_data` (10 dynamics) | `OK_VIOLIN_sul_ponticello_dynamics extrapolation.xlsx` Results ladder (measured pp/mf/ff anchors) |
| `violin_harmonics.py` | `spectral_data` (10 dynamics) | `OK_VIOLIN_harmonics_dynamics extrapolation.xlsx` Results ladder (pooled harmonics; measured pp/mf/ff anchors) |
| `viola_sordina.py`, `viola_sul_tasto.py`, `viola_sul_ponticello.py` | `spectral_data` (10 dynamics) | STE `Viola_pp/mf/ff.xlsx` anchors (`estimate_mean`) + predictor ladder |
| `viola_harmonics.py` | `spectral_data` (10 dynamics) | `OK_VIOLA_harmonics_dynamics extrapolation.xlsx` Results ladder (pooled harmonics; measured pp/mf/ff anchors) |
| `cello_sordina.py`, `cello_sul_tasto.py`, `cello_sul_ponticello.py` | `spectral_data` (10 dynamics) | STE `Cello_pp/mf/ff.xlsx` anchors (`estimate_mean`) + predictor ladder |
| `double_bass_sordina.py`, `double_bass_sul_tasto.py`, `double_bass_sul_ponticello.py` | `spectral_data` (10 dynamics) | STE `Contrabass-pp/mf/ff.xlsx` anchors (`estimate_mean`) + predictor ladder |
| `bass_drum.py`, `cymbals.py`, `tamtam.py`, `gong.py` | `DYNAMIC_CDM` (10 dynamics; pitch-independent) | NonTunPerc MC anchors + committed former `internal_default` ladder |
| Registry-only entries | — | Coarse register/dynamic model (`coarse_default.py`) |

**Unpitched modules:** Profiles with `unpitched=True` (Bass drum, Cymbals, Tam-tam, Gong) use pitch-independent `DYNAMIC_CDM`; `calcular_densidade` ignores `nota`. A single `LOOKUP_NOTE` / `spectral_data` key remains for lookup-shape compatibility only (registry midpoint: `D2`, `C5`, `C2`, `C3`). Entry paths (GUI / MusicXML `<unpitched>` / MIDI channel 10) inject it; users never choose a sounding pitch. Cents/microtones are rejected. Mass/CDM and Event/Player Count contribute as usual; pitch-structure metrics and texture polyphony exclude these events in `core/unpitched_routing.partition_pitched_events` only. Aggregation contract: [TECHNICAL_MANUAL §7.5.1](../docs/TECHNICAL_MANUAL.md).

**Important distinction:** the **analysis pipeline is score-only at runtime** (no audio input). The **instrument scripts** carry pre-loaded acoustic metadata looked up from notation (pitch×dynamic for pitched modules; dynamics-only for unpitched).

**Media ingestion:** Zenodo `*_Media` workbook rows may use duplicate suffix labels (e.g. `F4 (2)`). Offline tooling applies `utils.notes.normalize_media_note_label()` before canonical parsing. See [instrument_acoustic_sources.md](../docs/instrument_acoustic_sources.md).

**Technique honesty:** registry `supported_techniques` lists organological capabilities. Modules declare `INSTRUMENT_SOURCE.source_technique` and `table_supported_techniques` for the committed numerical table only (e.g. `arco_sustain`, `arco_sordina`, `arco_sul_tasto`, `arco_sul_ponticello`, `arco_artificial_harmonic`, `ordinary_sustain`). Pizzicato, tremolo, natural harmonics, mute, and similar techniques are not acoustically modelled unless separate technique-specific tables exist.

**Technique ladders (2026-08-08 rebuild):** the string technique modules commit full 10-level ladders built by Dynamics_predicter v1.5 directly on the STE workbook anchors. Measured mf/ff (and pp where measured) match the committed `*_MEASURED` dicts verbatim; the earlier isotonic clamp (`tools/enforce_pitched_monotone_dynamic_ladders.py`, D6 hotfix 2026-08-03) is no longer applied.

**Range semantics:** distinguish `source_table_span` (committed table), `sounding_range` (validation), and `comfortable_range` (conservative orchestration band). Example: double bass table spans E1–C5 while comfortable range is G1–G3.

Audit: `python tools/audit_instrument_metadata_range_resolution.py` → `reports/instrument_metadata_range_resolution_audit.*`

**String verification (PR #13/#14):** musicological contract tests (`pytest -m musicological`) cover module contracts, source reconstruction (local workbooks), pitch spelling, committed-dynamics contracts, and score scenarios for violin, viola, cello, and double bass.



**GUI vs registry IDs:** The Tkinter GUI shows **English orchestral short names** (Fl, Ob, Cl, Bsn, Tpt, Hn, Tba, Vl, Vla, Vc, Db, …). Registry `instrument_id` keys remain stable internal identifiers (e.g. `flauta`, `violino`) with English aliases (`flute`, `violin`, …) and English **module filenames** (`flute.py`, `violin.py`, …). The former long display names (Flute, Violin, …) still resolve as aliases.



---



## Module contract



Every loadable instrument module must expose:



```python

def calcular_densidade(nota: str, dinamica: str) -> float:

    """Density for one note at one dynamic marking (committed table cell)."""

```



Unknown score dynamics are normalised to `mf`. Missing cells in `spectral_data`
raise `MissingCommittedDynamicError` — there is no runtime GPR/tail fill-in.



**Pitch lookup:** `instrumentos/pitch_interpolation.py` provides unified continuous-pitch resolution; `instrumentos/spectral_lookup.py` wraps it for instrument modules. **Chromatic-only tables are the canonical model** — quarter-tones, arbitrary cents (`D3+7c`, `C4+125c`), and arrow notation are inferred at runtime via `microtonal.note_to_midi_strict()` and linear/PCHIP interpolation between chromatic anchors. Manually pasted microtonal rows are optional curated exact overrides only.



Strict pitch parsing (`note_to_midi_strict`, `parse_pitch_strict`) raises `InvalidPitchNotation` on malformed input and **never** falls back to C4. Legacy `note_to_midi()` remains permissive for backward compatibility; research/instrument paths use strict parsing.



Lookup order:



1. **Exact** — literal table key match (curated microtonal override rows, if present)

2. **Normalized exact** — enharmonic / equivalent MIDI match (e.g. `C♯4` ≡ `C#4`)

3. **Continuous interpolation** — local linear between bracketing chromatic anchors; PCHIP when ≥4 in-range anchors and `auto` mode



**Table validation:** duplicate MIDI coordinates with identical dynamic values are deduplicated deterministically; conflicting duplicates (e.g. `C#4` vs `Db4` with different `mf`) raise `MetadataTableConflictError`.



Provenance labels (`exact`, `normalized_exact`, `interpolated`, `extrapolated`, `fallback`) distinguish measured table entries from modelled microtonal estimates. Interpolated values are **not** labelled as directly measured.



Range policy: never collapse to the same pitch class in a distant octave (e.g. D♯6 ≠ D♯4). Deviations >1 semitone outside the table log `WARNING`; >1 octave log `ERROR` and use fallback (default 5.0) instead of silent misleading extrapolation.



**Committed dynamic ladders:** production looks up exact `spectral_data` cells for
the requested dynamic. Pitched table-backed modules (winds, brass, arco strings,
string techniques/harmonics) and unpitched percussion commit all ten
`DYNAMIC_LEVELS`. Ladders are data-faithful: measured pp/mf/ff anchors verbatim,
PCHIP interiors bounded by their measured segment, geometrically tapered outer
levels — **not** forced monotone (real measurements are occasionally
non-monotone). Contract enforced by `tests/test_pitched_dynamic_monotone_ladders.py`.
The retired GPR + adaptive-tail implementation lives only at
`tools/legacy_gpr_dynamic_interpolation.py` for historical audits.



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



Warnings propagate into `resultados["metric_metadata"]` with `source_type=external_acoustic_metadata` when table-backed modules are used.



---



## Dedicated modules (committed acoustic-source tables)



| Instrument (GUI) | Module file | `profile_status` | Acoustic metadata |

|------------------|-------------|------------------|-------------------|

| **Flute** | `flute.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Clarinet** | `clarinet.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Oboe** | `oboe.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Bassoon** | `bassoon.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Trumpet (Tpt)** | `trumpet.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Horn (Hn)** | `horn.py` | `literature_derived` | IOWA+ORCH sustain CDM medians |

| **Tuba (Tba)** | `tuba.py` | `literature_derived` | IOWA+ORCH sustain CDM medians (C1–A#4) |

| **Violin** | `violin.py` | `literature_derived` | IOWA+ORCH arco CDM medians |
| **vl sord** | `violin_sordina.py` | `literature_derived` | OK_VIOLIN con sordina Results ladder, measured pp/mf/ff anchors (high uncertainty) |
| **vl st** | `violin_sul_tasto.py` | `literature_derived` | OK_VIOLIN sul tasto Results ladder, measured pp/mf/ff anchors (high uncertainty) |
| **vl sp** | `violin_sul_ponticello.py` | `literature_derived` | OK_VIOLIN sul ponticello Results ladder, measured pp/mf/ff anchors (high uncertainty) |
| **vl harm** | `violin_harmonics.py` | `literature_derived` | OK_VIOLIN pooled harmonics Results ladder, G4–G7 (high uncertainty) |
| **vla** | `viola.py` | `literature_derived` | OK_VIOLA arco ordinario Results ladder (IOWA+ORCH pp/mf/ff anchors) |
| **Viola sordina** | `viola_sordina.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |
| **Viola sul tasto** | `viola_sul_tasto.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |
| **Viola sul ponticello** | `viola_sul_ponticello.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |
| **vla harm** | `viola_harmonics.py` | `literature_derived` | OK_VIOLA pooled harmonics Results ladder, C4–B7 (high uncertainty) |

| **Cello** | `cello.py` | `literature_derived` | IOWA+ORCH arco CDM medians |
| **Cello sordina** | `cello_sordina.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |
| **Cello sul tasto** | `cello_sul_tasto.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |
| **Cello sul ponticello** | `cello_sul_ponticello.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |
| **Double bass** | `double_bass.py` | `literature_derived` | IOWA+ORCH arco CDM medians |
| **Double bass sordina** | `double_bass_sordina.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |
| **Double bass sul tasto** | `double_bass_sul_tasto.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |
| **Double bass sul ponticello** | `double_bass_sul_ponticello.py` | `literature_derived` | Extrapolation workbook pp/mf/ff (high uncertainty) |



Regenerate CDM modules from Zenodo workbooks:



```bash

python tools/populate_td_importer_sheets_from_zenodo_media.py   # AcousticTable + provenance sheets

python tools/generate_instrument_modules.py                     # instrumentos/*.py

```



See [instrument_acoustic_sources.md](../docs/instrument_acoustic_sources.md) for workbook paths and citations.



---



## Registry profiles (`registry.py`)



~**41 orchestral instruments / technique profiles** are registered with metadata (family, ranges, register bands, `profile_status`, `uncertainty`, aliases). Examples:



| Family | IDs (sample) |

|--------|----------------|

| Woodwinds | `flauta`, `flautim`, `oboe`, `cor_anglais`, `clarinete`, `clarinete_baixo`, `fagote`, `contrafagote` |

| Strings | `violino`, `violino_sordina`, `violino_sul_tasto`, `violino_sul_ponticello`, `violino_harm`, `viola`, `viola_sordina`, `viola_sul_tasto`, `viola_sul_ponticello`, `viola_harm`, `violoncelo`, `violoncelo_sordina`, `violoncelo_sul_tasto`, `violoncelo_sul_ponticello`, `contrabaixo`, `contrabaixo_sordina`, `contrabaixo_sul_tasto`, `contrabaixo_sul_ponticello` |

| Brass | `trompa`, `trompete`, `trombone`, `trombone_baixo`, `tuba` |

| Keyboard / harp | `piano`, `celesta`, `harpa` |

| Percussion | `timpanos`, `bombo`, `caixa`, `pratos`, `tamtam`, `gongo`, `vibrafone`, `marimba`, `metalofone` |



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

2. Populate `spectral_data` with **chromatic anchors only** (e.g. `C4`, `C#4`, …) carrying **all ten dynamic levels** per note — measured pp/mf/ff anchors from **documented external acoustic sources**, remaining levels committed offline via Dynamics_predicter; cite provenance in the module docstring and `registry.py` `source_notes`. Microtonal rows are optional — runtime interpolation fills quarter-tones and cents.

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

    source_notes="Committed 10-dynamic CDM ladder from [cite acoustic source].",

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

