# Plausibility audit — Textural Density

**Date:** 2026-08-18  
**Scope:** read-only verification of commit `0bd9d7d` on `main` (package 1.1.5, methodology `5.1.0-strict-symbolic`). Production code was not modified.  
**Supporting dump:** `reports/plausibility_raw.json` (242 records). Every numeric claim below is taken from a test id in that dump or from the pytest session that produced it.

---

## 1. Environment and state

| Item | Value |
|---|---|
| Branch | `verify/plausibility-battery` (uncommitted tests and this report only) |
| `HEAD` / `main` | `0bd9d7d550963cdc4210fe7255a346850f36ed92` |
| Commit subject | `Remove cello and double-bass technique modules from the GUI and instrumentos corpus.` |
| `main` movement | none — `main` has not moved past the pinned commit |
| `get_package_version()` / `PACKAGE_VERSION` | `1.1.5` |
| `METRIC_SCHEMA_VERSION` (`core.defaults`) | `5.1.0-strict-symbolic` |
| Python | 3.10.11 (MSC v.1929, 64-bit) |
| OS | Windows 10.0.26200 |
| numpy | 2.2.6 |
| scipy | 1.13.1 (present; not skipped) |
| statsmodels | 0.14.5 (present; not skipped) |
| pytest | 7.4.4 |
| music21 | 9.9.1 |
| tkinter | present (not skipped) |

`main` matches the pinned state. The audit was **not** aborted.

**Skipped environment modules.** None. `scipy`, `statsmodels`, and `tkinter` imported successfully.

**Test skips (coverage, not missing dependencies).** Two HARD cases were skipped because the harmonics tables have no `C4`/`C#4` cell: `FC.enh.violin_harmonics`, `FC.interp.violin_harmonics`.

**Pytest command and runtime**

```text
python -m pytest tests/plausibility -o addopts="" --tb=line -q
======= 7 failed, 202 passed, 2 skipped, 23 xfailed, 9 xpassed in 6.65s =======
```

Coverage addopts from `pytest.ini` (`--cov-fail-under=63`) were disabled via `-o addopts=""` as specified. The `plausibility` marker is registered in `tests/plausibility/conftest.py`. `INTERVAL_BLEND_NORMALISATION` remained `"legacy"` except in the labelled `FE.unit_range` subset.

**Production diff.** The following command produced empty output:

```text
git diff --stat main -- core instrumentos spectral_analysis.py timbre_texture_analysis.py densidade_intervalar.py microtonal.py xml_loader.py config.py
```

`config/density_params.json` was left at the committed λ = 0.05. `calibrate_lambda()` in `FB.soft.spearman` was prevented from writing that file.

---

## 2. Summary table

Counts are recorded HARD/SOFT items in `reports/plausibility_raw.json`. SOFT “met / not met” follows the recorded status. For F-J the recorded predicate was written loosely and XPASSed; the *stated* qualitative ordering is treated as not met in §4 and §6.

| Family | HARD pass/fail | SOFT met/not met | Verdict |
|---|---:|---:|---|
| F-A Pitch grammar | 21 / 1 | — | One HARD defect: `Cb5` is not treated as enharmonic to `B4` in `density.*` |
| F-B Interval density | 8 / 0 | 2 / 1 | Documented interval identities hold; calibrated λ does not track `CONSONANCE_RATINGS` |
| F-C Instrument ladders | 87 / 6 | 1 / 22 | Table contracts hold; withdrawn ids fall back to the unknown coarse proxy; measured ladders invert and spike |
| F-D Quantity / mass | 9 / 0 | 1 / 0 | RSS and √M identities hold; Qty 1.5 is accepted |
| F-E Blend / composite | 54 / 0 | — | Independent §H grid matches to 0; `D_pitch` excluded from `total` |
| F-F Absolute / counts | 4 / 0 | — | `D_abs` formula and unpitched counting hold |
| F-G Spectral | 4 / 0 | 1 / 0 | Transposition, entropy, and F24 octave-class rule hold |
| F-H Registral / texture | 2 / 0 | 2 / 0 | Compression formula holds; compactness helper unused |
| F-I Temporal / score | 8 / 0 | 1 / 0 | Half-open activity and MusicXML transposition hold |
| F-J Repertoire | — | 1* / 0* | *Recorded XPASS under a relaxed predicate; stated ordering fails (see §6) |
| F-K Robustness | 6 / 0 | — | Finite JSON, determinism, and `composite_meta` keys hold |

Session: 243 collected items; 7 HARD failures (1 + 6 withdrawn ids).

---

## 3. HARD failures

Two defect classes were observed. No other HARD assertion failed in the final session.

### 3.1 `FA.enh.B4.Cb5` — enharmonic `density.*` (Mathematical Manual §A–§B)

**Input**

```python
{"notes": ["B4", "G4"], "dynamics": ["mf", "mf"], "instruments": ["flauta", "flauta"], "num_instruments": [1, 1], "weight_factor": 0.5}
{"notes": ["Cb5", "G4"], "dynamics": ["mf", "mf"], "instruments": ["flauta", "flauta"], "num_instruments": [1, 1], "weight_factor": 0.5}
```

**Observed vs expected**

| Quantity | `B4`+`G4` | `Cb5`+`G4` | Expected |
|---|---:|---:|---|
| `pitches` | `[71.0, 67.0]` | `[71.0, 67.0]` | identical |
| `parse_pitch_strict` | 71.0 | 71.0 | identical |
| `note_to_midi` (legacy) | 71 | **83** | identical (71) |
| `density.interval` | 0.222799693250 | 0.079867076986 | identical |
| `density.instrument` | 20.232410983373 | 16.771397262245 | identical |
| `density.total` | 0.013275066771 | 0.009080718642 | identical |
| `density.sonic_mass` | 28.45463490 | 21.54745989 | identical |

`C#4`/`Db4` and `F#4`/`Gb4` matched (`FA.enh.C#4.Db4`, `FA.enh.F#4.Gb4`). The `Cb5` spelling is accepted by `parse_pitch_strict` as MIDI 71 (B4) but the legacy `note_to_midi` path used for table lookup maps `Cb5` → MIDI 83 (B5). Instrument density, mass, interval compactness (via that lookup path / weighting), and therefore `density.total`, diverge. This contradicts the documented enharmonic-equivalence invariant for `pitches` **and** `density.*`.

The pairs `["F#3","Gb3"]` and `["B3","Cb4"]` from the brief were moved to flute-range `F#4`/`Gb4` and `B4`/`Cb5` so that range validation would not mask the grammar check.

### 3.2 `FC.withdrawn.resolve.*` — silent unknown-proxy fallback

For each withdrawn id the same pattern was recorded:

| Test id | `resolve_profile` | `calculate_metrics` | Resolved profile |
|---|---|---|---|
| `FC.withdrawn.resolve.violoncelo_sordina` | `None` | silent accept | `"unknown"` |
| `FC.withdrawn.resolve.violoncelo_sul_tasto` | `None` | silent accept | `"unknown"` |
| `FC.withdrawn.resolve.violoncelo_sul_ponticello` | `None` | silent accept | `"unknown"` |
| `FC.withdrawn.resolve.contrabaixo_sordina` | `None` | silent accept | `"unknown"` |
| `FC.withdrawn.resolve.contrabaixo_sul_tasto` | `None` | silent accept | `"unknown"` |
| `FC.withdrawn.resolve.contrabaixo_sul_ponticello` | `None` | silent accept | `"unknown"` |

**Minimal reproduction**

```python
{"notes": ["C3"], "dynamics": ["mf"], "instruments": ["violoncelo_sordina"], "num_instruments": [1]}
```

Log line: `Instrument 'violoncelo_sordina' not registered; using unknown coarse proxy.`  
`resolve_profile` is correctly `None` (the id is not aliased onto `violoncelo`). `profile_for_event` / `calculate_metrics` nevertheless serve `_UNKNOWN_PROFILE` (coarse) instead of raising. The brief required an explicit registry error.

Withdrawal of the module files and doc listings **did** hold: `FC.withdrawn.files`, `FC.withdrawn.docs`.

No other HARD failures were recorded.

---

## 4. SOFT deviations

### 4.1 `FB.soft.spearman` — calibrated λ vs `CONSONANCE_RATINGS`

**Expectation:** after `calibrate_lambda()`, Spearman ρ ≥ 0.8 between literature ratings and dyad densities.  
**Observed:** ρ = 0.02857; λ\* = 0.026068208731536858.  
Rating order (semitones): `[5, 0, 3, 4, 6, 2]` (P4, unison, m3, M3, tritone, M2).  
Density order: `[0, 2, 3, 4, 5, 6]` (strict decay with distance).  
P4 (rating 1.24) and tritone (−0.453) are the clearest exceptions: the exponential-decay model is monotone in interval size and cannot recover a P4 > M3 > m3 ranking.  
**Classification:** modelling choice (documented φ(δ; λ) in §B / §L).

### 4.2 Dynamic inversions (`FC.soft.monotone.*`) — table artefact

Non-decreasing `pppp…ffff` failed on every pitched table-backed module except trumpet (`FC.soft.monotone.trumpet`, 0 inversions). Counts:

| Module (registry id) | Kind | Inversions | of which > 5 % | Test id |
|---|---|---:|---:|---|
| clarinet (`clarinete`) | table-backed | 26 | 11 | `FC.soft.monotone.clarinet` |
| double_bass (`contrabaixo`) | table-backed | 96 | 25 | `FC.soft.monotone.double_bass` |
| bassoon (`fagote`) | table-backed | 37 | 21 | `FC.soft.monotone.bassoon` |
| flute (`flauta`) | table-backed | 64 | 26 | `FC.soft.monotone.flute` |
| oboe | table-backed | 53 | 8 | `FC.soft.monotone.oboe` |
| trombone | table-backed | 20 | 4 | `FC.soft.monotone.trombone` |
| horn (`trompa`) | table-backed | 5 | 1 | `FC.soft.monotone.horn` |
| trumpet (`trompete`) | table-backed | 0 | 0 | `FC.soft.monotone.trumpet` |
| tuba | table-backed | 40 | 10 | `FC.soft.monotone.tuba` |
| viola | table-backed | 192 | 20 | `FC.soft.monotone.viola` |
| viola_harmonics (`viola_harm`) | table-backed | 20 | 0 | `FC.soft.monotone.viola_harmonics` |
| viola_sordina | table-backed | 30 | 0 | `FC.soft.monotone.viola_sordina` |
| viola_sul_ponticello | table-backed | 30 | 0 | `FC.soft.monotone.viola_sul_ponticello` |
| violin (`violino`) | table-backed | 111 | 22 | `FC.soft.monotone.violin` |
| violin_harmonics (`violino_harm`) | table-backed | 20 | 0 | `FC.soft.monotone.violin_harmonics` |
| violin_sordina | table-backed | 53 | 9 | `FC.soft.monotone.violin_sordina` |
| violin_sul_ponticello | table-backed | 30 | 0 | `FC.soft.monotone.violin_sul_ponticello` |
| violin_sul_tasto | table-backed | 30 | 0 | `FC.soft.monotone.violin_sul_tasto` |
| cello (`violoncelo`) | table-backed | 182 | 87 | `FC.soft.monotone.cello` |

Example (cello C2, `FC.soft.monotone.cello`): `ff` 94.363 → `fff` 93.902 (rel 0.49 %); `fff` → `ffff` 93.534 (rel 0.39 %). Larger inversions (> 5 %) are stored in the raw dump (first 40 per module). README (2026-08-08) already notes that measured tables may invert.  
**Classification:** table artefact.

### 4.3 Technique variants (`FC.soft.techniques`) — table artefact

Agreement over the shared pitch × {`pppp`,`mf`,`ffff`} (all table-backed):

| Comparison | Rate | n |
|---|---:|---:|
| `violino_sul_ponticello` ≥ `violino` | 0.252 | 147 |
| `violino_sordina` ≤ `violino` | 0.660 | 147 |
| `violino_sul_tasto` ≤ `violino` | 0.966 | 147 |
| `violino_harm` ≤ `violino` | 0.973 | 111 |
| `viola_sul_ponticello` ≥ `viola` | 0.395 | 147 |
| `viola_sordina` ≤ `viola` | 0.993 | 147 |
| `viola_harm` ≤ `viola` | 0.901 | 111 |

Sul ponticello is **below** ordinario on most of the shared grid. Tasto / sordina / harmonics agree more often.  
**Classification:** table artefact (and a domain-expert question at `pppp`).

### 4.4 Register spikes (`FC.soft.spikes`) — table artefact

Every pitched table-backed module had at least one `mf` adjacent-semitone jump > 3× the module median. Largest recorded examples: trombone `F1`→`F#1` jump 58.21 (median 2.65); cello `C2`→`C#2` jump 43.28 (median 3.54); violin `G3`→`G#3` jump 25.65 (median 2.00); horn `A#1`→`B1` jump 23.82 (median 1.44). Full per-module lists: `FC.soft.spikes`.  
**Classification:** table artefact.

### 4.5 Cross-family and trombone placement — table artefact

`FC.soft.family_order` at mid-register:

| Instrument | Kind | note | mf | ff |
|---|---|---|---:|---:|
| trompete | table-backed | G4 | 23.100 | 36.127 |
| oboe | table-backed | G4 | 16.863 | 25.170 |
| flauta | table-backed | G4 | 15.730 | 18.278 |
| tuba | table-backed | C3 | 24.652 | 41.791 |
| trombone | table-backed | C3 | 41.079 | 78.938 |
| trompa | table-backed | C3 | 31.172 | 44.835 |

Woodwind/brass probe: trumpet ≥ oboe ≥ flute **holds**. tuba ≥ trombone ≥ horn **fails**. Observed brass order at C3 `mf`: trombone > horn > tuba.

`FC.soft.trombone_between`: 40 / 40 shared pitches lie **outside** the horn–tuba envelope at `mf`. In the recorded sample trombone exceeds both neighbours (e.g. C3-region `C2`: horn 64.77, trombone 93.06, tuba 56.29). The new trombone ladder is systematically louder than both horn and tuba on the overlap.  
**Classification:** table artefact.

### 4.6 Sixteen violins `pp` vs one violin `ff` (`FD.soft.16pp_vs_1ff`) — modelling choice

| Slice | Kind | `D_inst` | `M_sonic` | `density.total` |
|---|---|---:|---:|---:|
| 16 × violino A4 `pp` | table-backed | 109.881 | 439.524 | 0.20325 |
| 1 × violino A4 `ff` | table-backed | 30.798 | 30.798 | 0.01882 |

RSS and linear mass put the piano section well above a single forte. Whether that is musically credible for “sonic mass of a soft tutti vs one loud player” is left to the domain expert (§8). Recorded SOFT status is `met` because the case is report-only.

### 4.7 Repertoire qualitative ordering (`FJ.repertoire`) — modelling choice

See §6. Ligeti, not the Rite, has the highest `total` and `M_sonic`. Ligeti has a **low** `weighted_pitch` (wide chromatic set → small mean pairwise φ). Tristan’s harmonic ratio (0.496) is not distinctively low. The recorded test XPASSed under a relaxed predicate; the stated ordering is not met.  
**Classification:** modelling choice (intensive `D_int`, mass-dominated `D_total`).

SOFT cases that **met** their stated expectation: `FB.soft.cluster_rank` (0.2669 > 0.2455 > 0.2138 > 0.0401), `FB.soft.quarter_tone` (0.2835 ≥ 0.2669), `FG.soft.series` (HR 0.690 vs 0.185; entropy 2.412 vs 2.788), `FH.soft.low_high` (interval 0.27326 = 0.27326), `FH.soft.diversity` (1.0 > 0.333), `FI.soft.sustain_vs_staccato` (report-only; variance 0 vs 2.09×10⁻⁵).

---

## 5. Instrument-ladder audit tables

Live split from `FC.split`: **23 table-backed**, **13 coarse**, **36** profiles. Trombone is table-backed; `trombone_baixo` is coarse. Withdrawn cello/bass technique ids are absent from `list_instrument_ids()`.

### 5.1 Table-backed pitched modules

| Module | Registry id | n table pitches × 10 dyn | Dynamic inversions (>5 %) | Technique agreement | Kind |
|---|---|---:|---:|---|---|
| clarinet | clarinete | 47 | 26 (11) | — | table-backed |
| double_bass | contrabaixo | 45 | 96 (25) | — (technique tables withdrawn) | table-backed |
| bassoon | fagote | 42 | 37 (21) | — | table-backed |
| flute | flauta | 40 | 64 (26) | — | table-backed |
| oboe | oboe | 36 | 53 (8) | — | table-backed |
| trombone | trombone | 48 (MIDI 25–72; `FC.trombone.span`) | 20 (4) | — | table-backed |
| horn | trompa | 47 | 5 (1) | — | table-backed |
| trumpet | trompete | 36 | 0 (0) | — | table-backed |
| tuba | tuba | 47 | 40 (10) | — | table-backed |
| viola | viola | 49 | 192 (20) | see §4.3 | table-backed |
| viola_harmonics | viola_harm | 37 | 20 (0) | 0.901 ≤ ordinario | table-backed |
| viola_sordina | viola_sordina | 49 | 30 (0) | 0.993 ≤ ordinario | table-backed |
| viola_sul_ponticello | viola_sul_ponticello | 49 | 30 (0) | 0.395 ≥ ordinario | table-backed |
| violin | violino | 49 | 111 (22) | — | table-backed |
| violin_harmonics | violino_harm | 37 | 20 (0) | 0.973 ≤ ordinario | table-backed |
| violin_sordina | violino_sordina | 49 | 53 (9) | 0.660 ≤ ordinario | table-backed |
| violin_sul_ponticello | violino_sul_ponticello | 49 | 30 (0) | 0.252 ≥ ordinario | table-backed |
| violin_sul_tasto | violino_sul_tasto | 49 | 30 (0) | 0.966 ≤ ordinario | table-backed |
| cello | violoncelo | 49 | 182 (87) | — (technique tables withdrawn) | table-backed |

Lookup contract (`FC.lookup_contract`): three-anchor PCHIP still interpolates (linear fallback path); four-anchor interpolates; >12 st → fallback **5.0**; 1–12 st → `extrapolated` (near value 15.0 on the synthetic table); invalid pitch → **5.0**. `MIN_PCHIP_ANCHORS` = 4.

### 5.2 Unpitched table-backed (`FC.unpitched.*`)

Pitch argument ignored (C4 ≡ C8). Values at `mf`: bass drum / `bombo` 12.889; gong / `gongo` 2.108; cymbals / `pratos` 2.666; `tamtam` 4.097.

### 5.3 Coarse fallback (`FC.coarse.*`)

`IS_COARSE_DEFAULT` is true. Unknown dynamic uses the same magnitude as `mf` (weight 1.0).

| Id | Kind | mf (and unknown dyn) | Nearest table-backed `mf` |
|---|---|---:|---|
| trombone_baixo | coarse | 6.800 | trombone E3 = 35.430 |
| piano | coarse | 8.464 | violino C4 = 23.375 |
| harpa | coarse | 7.254 | violino C4 = 23.375 |
| cor_anglais | coarse | 6.800 | oboe C4 = 18.940 |

Coarse magnitudes sit well below the nearest measured neighbour. Plausibility only; not a defect.

---

## 6. Repertoire table (F-J)

Instrumentation notes: Tristan uses two oboes in place of cor anglais (**coarse**). Debussy uses `harpa` (**coarse**). Augurs F♭ spellings were accepted by `parse_pitch_strict`. All other ids are table-backed.

| Slice | `total` | `weighted_pitch` | `weighted_orchestral` | `pitch_structure` | `M_sonic` | entropy | harmonic ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tristan | 0.07035 | 0.05297 | 3.182 | 3.105 | 110.06 | 1.784 | 0.496 |
| Rite (strings + horns) | 0.36381 | 0.09230 | 9.024 | 24.605 | 770.36 | 2.692 | 0.273 |
| Rite + 3 trb + tuba | 0.51665 | 0.07457 | 12.991 | 42.319 | 1140.07 | 3.106 | 0.324 |
| Webern | 0.02169 | 0.05666 | 1.452 | 1.490 | 42.92 | 1.285 | 0.584 |
| Ligeti *Atmosphères* | **0.65154** | 0.05061 | 13.131 | 1373.23 | **2600.27** | 5.746 | 0.115 |
| Penderecki *Threnody* | 0.20858 | **0.09707** | 4.846 | 1170.59 | 579.38 | 5.218 | 0.058 |
| Debussy *La Mer* | 0.04867 | 0.06323 | 2.305 | 7.194 | 93.44 | 2.153 | 0.062 |
| Flute A4 `mf` | 0.00665 | 0.00000 | 0.762 | 0.000 | 15.24 | 0.000 | 1.000 |
| Two flutes octave | 0.00957 | 0.05717 | 0.847 | 0.422 | 22.63 | 0.911 | 1.000 |

**Expected vs observed ordering** (`FJ.repertoire`)

| Claim | Expected | Observed | Driver if it fails |
|---|---|---|---|
| Highest `weighted_pitch` | Ligeti, Penderecki | Penderecki, Rite, Rite+trb | Ligeti’s five-octave chromatic set has a **low** mean pairwise `D_int` (0.101); Penderecki’s tight quarter-tone cluster has the highest `D_int` (0.194) |
| Highest `M_sonic` / `total` | Rite, Rite+trb | **Ligeti**, Rite+trb, Rite | Ligeti divisi (61 pitches × Qty 2) dominates linear mass; composite follows √M |
| Lowest `total` | Webern, single flute | flute single, flute octave, Webern | holds for the named pair; the bare octave is still quieter than Webern |
| Intermediate + low HR | Tristan | Tristan is intermediate in `total` (0.070); HR 0.496 is **not** low (Penderecki 0.058, Debussy 0.062, Ligeti 0.115) | harmonic-ratio of F2–B2–D♯4–G♯4 is a mid value, not a distinctive minimum |

Register occupancy is stored under `density_subindices.registral` in the raw case blob (`FJ.repertoire`). Ligeti and Penderecki occupy the largest pitch-structure / entropy values, as expected for clusters; that does **not** transfer to `weighted_pitch`.

---

## 7. Cross-implementation results (F-E)

Independent §H implementation (manual text only; `tests/plausibility/helpers.independent_blend`; **does not import** `core.composite`):

$$
D_{\mathrm{blend}} = 10\bigl(w\cdot D_I/100 + (1-w)\cdot D_V/10\bigr),\quad
D_{\mathrm{total}}^{\mathrm{pre}} = D_{\mathrm{blend}}\sqrt{M}/193,\quad
D_{\mathrm{total}} = \log_{10}(1+D_{\mathrm{total}}^{\mathrm{pre}}).
$$

No clamping at `DI_max` / `DV_max`.

| Item | Result | Test id |
|---|---|---|
| Grid size | 3 weights × 4 quantities × 4 slices = **48** | `FE.grid.w*.q*.*` |
| max \|Δ `density.weighted`\| | **0** | same |
| max \|Δ `density.total`\| | **0** | same |
| `DI` above 100, no clamp | `DI` = 1128.167, `weighted` = 56.408 | `FE.noclamp` (8× trombone C3 `ffff`) |
| Ratio `None` when n<2 or w=1 | yes | `FE.ratio` |
| Ratio at w=0.5 | 13.781707371178 = `(DI/10)/DV` | `FE.ratio` |
| `D_pitch` excluded from `total` | `total` held at 0.084227; `D_pitch` 5.054 → 4.715 after harmonic-ratio monkeypatch | `FE.pitch_excluded` |
| Adding a pitch vs `total` | 50 / 50 viola chords non-decreasing | `FE.mono.total` |
| `D_pitch` can fall | `[G4,B4,C5]` 3.9906 → +`C2` 3.9166 | `FE.quasi_d_pitch` |

**`unit_range` subset** (`FE.unit_range`, flute C4–E4–G4, w=0.5):

| | `legacy` (default) | `unit_range` (`DV_max = log10 2`) |
|---|---:|---:|
| `density.total` | 0.030334024217 | 0.082187252065 |
| Independent reproduction of unit total | — | 0.082187252065 |
| Interval term `10·(1−w)·DV/DV_max` | 0.106879 | 3.550457 |

Default totals were bit-identical to an explicit `legacy` re-run. Switching to `unit_range` multiplies the interval term by `10 / log10(2) ≈ 33.2` relative to the legacy divisor 10. Instrument term is still `DI/100`. The two axes are therefore **not commensurable**; the numerical gap (0.030 vs 0.082) is the manual’s “approximate parity, not commensurability” caveat.

`USE_LOG_COMPRESSION` (`FB.log`): `D_int` obeys `log10(1+x)` exactly (raw 0.635908 → compressed 0.213759). `weighted_pitch` does **not** equal `log10(1+weighted_pitch_raw)` (0.31795 → 0.10688); it is the blend of the already-compressed `D_int`. Documented identity is on `D_int` (§B), not on the blend coordinate.

---

## 8. Items for the domain expert

1. **Sul ponticello ≥ ordinario at every dynamic, including `pppp`.** Agreement is 25 % (violin) and 39 % (viola) over the shared grid (`FC.soft.techniques`). Should the inequality be restricted to `mf`/`ff`, or is the measured ladder the intended source of truth?

2. **RSS for unison string sections.** Four violins give exactly 2× `D_inst` (`FD.rss.identical`: 23.375 → 46.750). Sixteen violins at `pp` out-score one violin at `ff` by an order of magnitude in `total` (0.203 vs 0.019; `FD.soft.16pp_vs_1ff`). Is incoherent addition acceptable for a muted/piano section?

3. **Qty as a non-integer.** `validate_quantity(1.5)` and the pipeline accept 1.5 (`FD.qty.reject.1.5`). Values `< 1` and non-finite values are rejected. Should player count be integer-gated?

4. **Octave-class tolerance 0.25 semitone (F24).** `[60, 72.2, 64]` → 2/3 and `[60, 72.3, 64]` → 1/3, symmetric in sign (`FG.harmonic.symmetric`). Is ±25 cents the intended octave-equivalence window?

5. **Spectral roll-off 0.85.** A single-bin input returns roll-off = the bin frequency 261.63 Hz (`FG.single_and_equal`). The 0.85 quantile is undefined for one bin; the implementation reports the bin itself.

6. **Trombone ladder magnitude.** On all 40 shared pitches the trombone `mf` cell exceeds both horn and tuba (`FC.soft.trombone_between`). At C3: trombone 41.08, horn 31.17, tuba 24.65 (`FC.soft.family_order`). Is a trombone louder than a tuba in CDM units expected from the Iowa/Orchidea source, or is the committed sheet high?

7. **Dynamic inversions on cello and viola.** 182 (cello) and 192 (viola) `pppp…ffff` descents, 87 and 20 of them > 5 % (`FC.soft.monotone.cello`, `FC.soft.monotone.viola`). Treated as measured-table artefacts; confirm they should remain.

8. **Register spikes at the bottom of brass/string tables.** Trombone `F1`→`F#1` jump 58.2; cello `C2`→`C#2` jump 43.3 (`FC.soft.spikes`). Acoustic, or edge-of-range measurement noise?

9. **Wide chromatic clusters vs tight ones in `weighted_pitch`.** Ligeti (five octaves) scores 0.0506; Penderecki (quarter-tone cluster) scores 0.0971 (`FJ.repertoire`). Mean-per-pair normalisation makes a *wider* cluster look *less* interval-dense. Is that the intended musicological reading of “textural density”?

10. **Tristan chord harmonic ratio 0.496** is higher than Ligeti (0.115) and Penderecki (0.058). The “distinctively low HR” expectation does not hold. Is the F2–B2–D♯4–G♯4 sonority expected to look more inharmonic under the 0.25-semitone octave rule?

11. **Silent unknown-instrument fallback.** Withdrawn technique ids resolve to the coarse unknown proxy rather than erroring (`FC.withdrawn.resolve.*`). From an editorial standpoint, should a misspelled or withdrawn id be hard-fail?

12. **`Cb` / `Fb` spellings in lookup.** `parse_pitch_strict("Cb5")` = 71, `note_to_midi("Cb5")` = 83 (`FA.enh.B4.Cb5`). Any score that writes C-flat (Augurs F♭-major, etc.) can hit the wrong table cell if it passes through the legacy converter.

---

## 9. Limitations of this battery

- Audio, measured spectra, and listening tests were not run. All “acoustic” claims are about **symbolic CDM tables** and formula outputs.
- GUI, MIDI file I/O, and live `analyze_score` on published MusicXML editions were not exercised beyond four synthetic transposition parts (`FI.xml.*`).
- `unit_range` was tested on one triad, not the 48-cell §H grid.
- Duration-weighted event count remained `None` even when `onsets`/`offsets`/`durations` were supplied on the legacy dict (`FF.duration_weighted`). The field may exist only on the timed `analyze_score` path; that path was not re-probed for the count.
- `orchestration_balance` was not resolved in `FH.soft.low_high` (recorded `null`); band occupancy was recorded under the nested `density_subindices` blob rather than a flat map.
- Random monotonicity (`FE.mono.total`) used 50 viola chords in C3–A4, not a uniform sample over all instruments or the full MIDI range.
- Coarse-instrument plausibility was sampled on four ids only (`trombone_baixo`, `piano`, `harpa`, `cor_anglais`).
- Repertoire slices are single vertical encodings, not published editions; cor anglais → oboe and harp → coarse `harpa` are substitutions.
- `calibrate_lambda()` was executed in-memory only; the committed λ = 0.05 remains the production default for all HARD interval numbers except the Spearman row.
- Property tests of the existing `tests/stress/` battery were not re-run.
- Coverage measurement was disabled (`-o addopts=""`).

---

## Files added

No production file was modified (`git diff --stat main -- core instrumentos … config.py` empty).

```
tests/plausibility/__init__.py
tests/plausibility/conftest.py
tests/plausibility/helpers.py
tests/plausibility/test_fa_pitch_grammar.py
tests/plausibility/test_fb_interval_density.py
tests/plausibility/test_fc_instrument_ladders.py
tests/plausibility/test_fd_quantity_mass.py
tests/plausibility/test_fe_blend_composite.py
tests/plausibility/test_ff_absolute_density.py
tests/plausibility/test_fg_spectral.py
tests/plausibility/test_fh_registral_texture.py
tests/plausibility/test_fi_temporal_score.py
tests/plausibility/test_fj_repertoire.py
tests/plausibility/test_fk_robustness.py
reports/plausibility_raw.json
reports/plausibility_audit_2026-08-18.md
```

These paths exist only on `verify/plausibility-battery` and have not been committed.
