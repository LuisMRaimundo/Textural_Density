# Instrument models and registry

> **Metadata status:** The instrument corpus is **incomplete**. Many names resolve to coarse fallbacks; only a few modules embed sparse GPR tables. External acoustic/proxy metadata are curated gradually via the auxiliary Excel importer — not live analysis. Current tables must not be read as final calibrated models.

This package provides **instrument density** for the vertical density pipeline. Each note in a chord uses **its own** instrument module (Phase 2+), resolved via `instrumentos/registry.py` and loaded through `get_instrument_module()`.

## Acoustic-source metadata in instrument scripts

Dedicated modules (`flauta.py`, `clarinete.py`, `oboe.py`) embed **sparse amplitude tables** from external sources (partial digitization — **work in progress**, not final reference data). Those tables are stored in each script as `spectral_data` / `spectral_data_unicode` and interpolated by Gaussian-process regression (GPR) for intermediate dynamics.

| What | Source |
|------|--------|
| `flauta.spectral_data` | External acoustic measurements / literature (note × pp/mf/ff) |
| `clarinete.spectral_data_unicode` | External acoustic measurements / literature |
| `oboe.py` | Scaled proxy over flute acoustic tables (`OBOE_SCALE`) |
| Registry-only entries | **No** acoustic script — coarse register/dynamic model (`coarse_default.py`) |

**Important distinction:** the **analysis pipeline is score-only at runtime** (no audio input). The **instrument scripts** carry pre-loaded acoustic metadata that is looked up from notated pitch and dynamic markings.

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

**Pitch lookup:** `instrumentos/pitch_interpolation.py` provides unified continuous-pitch resolution; `instrumentos/spectral_lookup.py` wraps it for instrument modules. **Chromatic-only tables are the canonical model** — quarter-tones, arbitrary cents (`D3+7c`, `C4+125c`), and arrow notation are inferred at runtime via `microtonal.note_to_midi_strict()` and linear/PCHIP interpolation between chromatic anchors. Manually pasted microtonal rows are optional curated exact overrides only; flute/oboe pasted tables are not architectural requirements.

Strict pitch parsing (`note_to_midi_strict`, `parse_pitch_strict`) raises `InvalidPitchNotation` on malformed input and **never** falls back to C4. Legacy `note_to_midi()` remains permissive for backward compatibility; research/instrument paths use strict parsing.

Lookup order:

1. **Exact** — literal table key match (curated microtonal override rows, if present)
2. **Normalized exact** — enharmonic / equivalent MIDI match (e.g. `C♯4` ≡ `C#4`)
3. **Continuous interpolation** — local linear between bracketing chromatic anchors; PCHIP when ≥4 in-range anchors and `auto` mode

**Table validation:** duplicate MIDI coordinates with identical dynamic values are deduplicated deterministically; conflicting duplicates (e.g. `C#4` vs `Db4` with different `mf`) raise `MetadataTableConflictError`.

Provenance labels (`exact`, `normalized_exact`, `interpolated`, `extrapolated`, `fallback`) distinguish measured table entries from modelled microtonal estimates. Interpolated values are **not** labelled as directly measured.

Range policy: never collapse to the same pitch class in a distant octave (e.g. D♯6 ≠ D♯4). Deviations >1 semitone outside the table log `WARNING`; >1 octave log `ERROR` and use fallback (default 5.0) instead of silent misleading extrapolation.

Dynamic interpolation (pp/mf/ff GPR or linear) remains separate from pitch interpolation — each dynamic column is interpolated independently over pitch.

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

| Instrument | Module | `profile_status` | Acoustic metadata |
|------------|--------|------------------|-------------------|
| **Flauta** | `flauta.py` | `literature_derived` | `spectral_data` from external acoustic sources |
| **Clarinete** | `clarinete.py` | `literature_derived` | `spectral_data_unicode` from external acoustic sources |
| **Oboe** | `oboe.py` | `literature_derived` | Scaled proxy over flute acoustic tables |

These three are the only modules with full `calcular_densidade` tables in this directory.

---

## Registry profiles (`registry.py`)

~**28 orchestral instruments** are registered with metadata (family, ranges, register bands, `profile_status`, `uncertainty`, aliases). Examples:

| Family | IDs (sample) |
|--------|----------------|
| Woodwinds | `flauta`, `flautim`, `oboe`, `cor_anglais`, `clarinete`, `clarinete_baixo`, `fagote`, `contrafagote` |
| Strings | `violino`, `viola`, `violoncelo`, `contrabaixo` |
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
| `literature_derived` | Dedicated script with external acoustic-source tables (flauta, clarinete, oboe) |
| `empirical_source` | Documented measured acoustic corpus in `source_notes` |
| `coarse_default` | Register/dynamic coarse proxy — **no acoustic script tables** |

### Aliases

Names are normalised (`lower`, spaces/hyphens → `_`). Examples: `horn` → `trompa`, `cello` → `violoncelo`, `Corne_ingles` → `cor_anglais`.

---

## Coarse default (`coarse_default.py`)

Instruments **without** a dedicated acoustic script receive a **coarse register-based density proxy** derived from the profile’s sounding range, register bands, and dynamic curve. These profiles do **not** embed external acoustic amplitude tables. Outputs are finite and usable but labelled `confidence: low` in metadata.

---

## Adding a new instrument

### Option A — Full module with acoustic-source tables (preferred for research)

1. Add `novo_instrumento.py` in this directory implementing the module contract (copy structure from `violino.py` or `flauta.py`).
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
    module_name="novo_instrumento",
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

mod = get_instrument_module("clarinete")
d = mod.calcular_densidade("G4", "mf")

profile = get_instrument_profile("trompa")
print(profile.family, profile.profile_status, profile.uncertainty)
```

Used internally by `core/orchestration.py` during `calculate_metrics`.

---

## Related documentation

- [API.md](../docs/API.md) — `get_instrument_module`, registry functions
- [instrument_metadata_audit.md](../docs/instrument_metadata_audit.md) — profile provenance audit
- [MIGRATION.md](../docs/MIGRATION.md) — per-event instrument change (Phase 2)
- [TECHNICAL_MANUAL.md](../docs/TECHNICAL_MANUAL.md) §2.4 — instrument layer architecture
