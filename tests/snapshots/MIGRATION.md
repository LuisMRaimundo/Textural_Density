# Snapshot migration notes

## 2026-05-21 — Epistemic relabelling (instrument density)

Frozen output updated after epistemic relabelling: instrument density is now marked
`external_acoustic_metadata` (lookup into pre-loaded acoustic-source tables) rather
than described as purely symbolic metadata.

**Numerical density values did not change** for `synthetic_triad` — only metadata
text, `source_type` labels, and subindex assumptions were updated.

Regression is split into two layers under `tests/snapshots/`:

| Layer | Path | Guards |
|-------|------|--------|
| Numeric | `numeric_outputs/` | Formula stability (`density`, subindex numbers) |
| Metadata | `metadata_outputs/` | `source_type`, assumptions, epistemic labels |
| Full JSON | `replication/outputs_frozen/json/` | Optional end-to-end fixture (updated with note) |

When updating metadata wording intentionally, refresh `metadata_outputs/` only.
When formulas change, refresh `numeric_outputs/` and document the reason.

## 2026-05-21 — Pitch aggregation & construct separation (unison doublings)

**Formula change (intentional):** exact unison doublings no longer inflate vertical
pitch-structure metrics.

- New module `core/pitch_aggregation.py` merges events by exact MIDI pitch bin.
- Interval compactness, spectral entropy, chroma, harmonic ratio, registral span, and
  composite vertical density use **distinct pitch bins** only.
- Orchestral / sonic mass remains **event-based** (doublings still increase mass).
- Removed: `refined_density = weighted_density / span` and cohesion `10/(1+span)` double-count.
- New: `pitch_structure_density` and `composite = pitch_structure × sqrt(sonic_mass) / MAX_DENS_GLOBAL`.
- Exact unison (`distinct_pitch_count < 2`) → `pitch_structure_density = 0`.

**Refresh:** `numeric_outputs/`, `replication/outputs_frozen/json/`, benchmark
`expected_outputs/`, and `tests/fixtures/regression_baseline.json`.

## 2026-05-21 — Quantity scaling (incoherent source addition)

**Formula change (intentional):** removed effective $n^{3/2}$ compounding from Qty.

Previously: per-event density used $\sqrt{n}$, then sonic mass multiplied by $n$ again
(and optionally a second dynamic factor), yielding $\approx d \cdot n^{3/2}$ for unison
doublings.

**New model** (`core/quantity_scaling.py`, `core/source_aggregation.py`):

- `one_player_density` from instrument module (dynamic applied once)
- Source groups: (MIDI pitch, instrument, dynamic) — row-splitting invariant
- Pressure-equivalent instrument density: $\sqrt{\sum n_j (d_j^{(1)})^2}$
- Sonic mass: $\sum n_j d_j^{(1)}$ (linear)
- Qty does **not** affect pitch-structure metrics
- Texture: `pitch_polyphony` = distinct pitch count (not mean Qty)

**Refresh:** all frozen outputs, benchmarks, regression baseline, metadata snapshots.
