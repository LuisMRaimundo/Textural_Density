# Instrument models and registry

This package provides **instrument density** for the vertical density pipeline. Each note in a chord uses **its own** instrument module (Phase 2+), resolved via `instrumentos/registry.py` and loaded through `get_instrument_module()`.

## Acoustic-source metadata in instrument scripts

Dedicated modules (`flauta.py`, `clarinete.py`, `oboe.py`) embed **sparse amplitude tables obtained from external acoustic sources** (published measurements, literature summaries). Those tables are stored in each script as `spectral_data` / `spectral_data_unicode` and interpolated by Gaussian-process regression (GPR) for intermediate dynamics.

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

1. Add `novo_instrumento.py` in this directory implementing the module contract (copy structure from `flauta.py`).
2. Populate `spectral_data` from **documented external acoustic sources**; cite provenance in the module docstring and `registry.py` `source_notes`.
3. Register in `registry.py`:

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

The package auto-discovers `.py` files on import (excluding `registry.py`, `coarse_default.py`, `__init__.py`).

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
