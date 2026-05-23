# Formal construct axioms — systematic score-only symbolic method

Densidade Vertical defines **score-derived vertical-density constructs** with **testable axioms**. These are **formal/systematic score-based** statements — not psychoacoustic claims, not claims about listener perception, and not requirements for human-rating prediction.

Optional human/expert studies are **outside the required systematic rubric** (see [`score_only_90_readiness_checklist.md`](score_only_90_readiness_checklist.md)).

Property tests: [`tests/test_formal_construct_axioms.py`](../tests/test_formal_construct_axioms.py)

---

## 1. event_density

**Definition:** Density contribution from the number of active symbolic events and, where configured, player-weighted (and optionally duration-weighted) events in a vertical slice.

**Axioms:**

| ID | Axiom |
|----|--------|
| ED-1 | Adding an active event to the same slice must not decrease raw event count. |
| ED-2 | Increasing `player_count` for an existing event must not decrease player-weighted event density. |
| ED-3 | Equivalent pitch spellings (same sounding MIDI) must not change event count density. |
| ED-4 | Written dynamics must not affect raw event count (unless a documented duration-weighted variant is used). |

**Verification:** `core/event_density.py`, `density_subindices.event_count`

---

## 2. interval_compactness

**Definition:** Score-derived contribution from pairwise pitch distances among **distinct aggregated pitch bins** within a vertical slice (exponential decay model with documented λ). Exact unison doublings are merged before interval pairs are counted.

**Axioms:**

| ID | Axiom |
|----|--------|
| IC-1 | For the exponential model, compactness must decrease as pairwise pitch distance increases, all else equal. |
| IC-2 | A chromatic cluster must score higher in interval compactness than a wide-spaced chord with the same distinct pitch count. |
| IC-3 | Player count must not affect pitch-only interval compactness. |
| IC-4 | Written dynamics must not affect pitch-only interval compactness. |
| IC-5 | Microtonal pitch distances are treated as continuous semitone distances where supported. |
| IC-6 | Exact unison duplication must not increase reported interval compactness; `distinct_pitch_count < 2` → compactness = 0. |

**Verification:** `core/interval_compactness.py`, `densidade_intervalar`, regression tests

---

## 3. registral_density / registral compactness

**Definition:** Score-derived measure of register compression/dispersion (pitch span, band occupancy, entropy).

**Axioms:**

| ID | Axiom |
|----|--------|
| RD-1 | Increasing pitch span while keeping event count constant must not increase registral compression. |
| RD-2 | Concentrating events in one register band must differ from spreading events across several bands. |
| RD-3 | Register-band definitions are configurable (`config.DEFAULT_REGISTER_BANDS`) and recorded in outputs. |
| RD-4 | Registral metrics must remain distinct from interval compactness. |

**Verification:** `core/registral_density.py`, `density_subindices.registral`

---

## 4. orchestration_mass

**Definition:** Score-derived measure using instruments, families, player counts, and **written dynamics** (symbolic weights, not SPL). Per-event instrument density where GPR modules exist applies **externally sourced acoustic amplitude metadata** to notated pitch/dynamic pairs (no runtime audio).

**Axioms:**

| ID | Axiom |
|----|--------|
| OM-1 | Increasing player count must not decrease orchestration mass. |
| OM-2 | Raising written dynamic weight (e.g. p → ff) must not decrease orchestration mass. |
| OM-3 | Changing written dynamics alone must not change raw pitch-only interval compactness or event count. |
| OM-4 | Orchestration mass is **not** SPL, loudness, or acoustic power. |
| OM-5 | Mass scales **linearly** with player count: $M = \sum n_j d_j^{(1)}$. |
| OM-6 | Pressure-equivalent instrument density uses **incoherent RSS**: $\sqrt{\sum n_j (d_j^{(1)})^2}$ — not $n^{3/2}$ compounding. |
| OM-7 | Dynamic is applied **once** via instrument-module lookup; mass formula does not double-apply symbolic dynamic weights. |
| OM-8 | One row with Qty = N and N identical rows with Qty = 1 are equivalent for mass and pressure-equivalent density. |

**Verification:** `density.sonic_mass`, `density.instrument`, `tests/test_quantity_scaling.py`

---

## 5. timbral_orchestration_complexity

**Definition:** Symbolic diversity/complexity of notated instrumental resources (families, instruments, blend indices).

**Axioms:**

| ID | Axiom |
|----|--------|
| TO-1 | Adding a new instrument family should increase or maintain family-diversity measures. |
| TO-2 | Duplicating the same instrument affects mass/player count but not necessarily family diversity. |
| TO-3 | Unknown instruments must trigger warnings or symbolic fallback metadata. |
| TO-4 | This construct is symbolic orchestration metadata, **not** measured timbre. |

**Verification:** `density_subindices.timbral_heterogeneity`, instrument registry

---

## 6. temporal_vertical_density

**Definition:** Evolution of score-derived vertical-density constructs over score time (slices/windows).

**Axioms:**

| ID | Axiom |
|----|--------|
| TV-1 | Adding an overlapping event must affect slices/windows where it is active. |
| TV-2 | Adding a non-overlapping event must not affect unrelated slices. |
| TV-3 | Onset/offset slicing must be deterministic for the same input. |
| TV-4 | Fixed-window analysis must record window size and configuration when used. |

**Verification:** `core/temporal.py`, `core/score_analysis.py`

---

## 7. composite_symbolic_density

**Definition:** Transparent weighted/heuristic combination of score-only subindices and documented normalization (see [`constants_and_assumptions.md`](constants_and_assumptions.md)).

**Axioms:**

| ID | Axiom |
|----|--------|
| CS-1 | Composite output must be deterministic for identical input and config. |
| CS-2 | Component weights and normalization constants must be recorded in metadata. |
| CS-3 | Disabled legacy/proxy branches must not affect score-only composite results vs enabled-off baseline. |
| CS-4 | Sensitivity to component weights must be reportable (`core/sensitivity.py`) without changing the default formula. |
| CS-5 | Composite must not hide subindex values; all constructs remain accessible in `density_subindices`. |

**Verification:** `calculate_metrics`, `core/sensitivity.py`, regression baseline

---

## Known gaps / TODO

| Item | Status |
|------|--------|
| Full axiom-to-test matrix in CI report | Partial — see property tests |
| Documented sensitivity for all composite constants | In progress — `core/sensitivity.py` diagnostic weight sets |
| Representative benchmark corpus | Pending licensed excerpts — see `replication/benchmark_manifest.json` |

---

## Optional empirical extensions (not required)

Expert annotations, IRR, human-rating correlation, listening tests, psychoacoustic calibration — useful only if the research question shifts toward **judgment prediction**. Not part of the systematic score-only method.
