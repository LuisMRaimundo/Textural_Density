# Instrument acoustic source provenance

> **Corpus status (2026-08):** The instrument metadata layer is **incomplete and under gradual curation**. Most registry entries lack dedicated acoustic tables; table-backed modules are **partial proxies**. Runtime no longer fills missing dynamics with GPR — full ladders committed for violin arco, viola, cello, double bass, flute, clarinet, bassoon, oboe, and unpitched percussion (trumpet / technique modules still migrating). Missing or coarse values are expected when `source_type`, `profile_status`, and warnings remain honest.

This document records **external acoustic metadata** embedded in `instrumentos/*.py`
modules. The analysis pipeline performs **score lookup** into these tables — not
live audio analysis.

> **Workbook archiving.** Primary CDM workbooks for winds/brass (and the string
> Zenodo collections cited below) live at **private local paths** (e.g.
> `D:\MADEIRAS\…`, `D:\METAIS\…`, `D:\CORDAS\…`) and are **not** committed to this
> repository. Intention: deposit in-repo extracts or a citable external archive so
> reconstruction tests can run without a private machine. Until then,
> `tests/test_string_source_reproducibility.py` **skips** when a workbook file is
> absent; on a machine with the deposits present, **cello** and **double_bass**
> workbook reconstruction currently **PASS**, while **violin** and **viola** are
> the two suite skips that will activate once those workbooks are deposited for CI.
> Runtime dynamics lookup is table-only (2026-08-03). Historical GPR audits remain
> under `tools/legacy_gpr_dynamic_interpolation.py` / `reports/`.

## Flute (`flute`)

- **Module:** `instrumentos/flute.py`
- **Table:** `spectral_data` (40 chromatic rows, B3–D7; 120 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of flute sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Flute_Zenodo_collections_media.xlsx`
- **Dynamics (2026-08-03):** full 10-level Dynamics_predicter `Results` ladder committed.
- **Uncertainty:** medium — sparse table, not full continuous spectrum.

## Clarinet (`clarinet`)

- **Module:** `instrumentos/clarinet.py`
- **Table:** `spectral_data` (47 chromatic rows, D3–C7; 141 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of clarinet sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Clarinet_Zenodo_collections_media.xlsx`
- **Dynamics (2026-08-03):** full 10-level Dynamics_predicter `Results` ladder committed.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Oboe (`oboe`)

- **Module:** `instrumentos/oboe.py`
- **Table:** `spectral_data` (36 chromatic rows, A#3–A6; 108 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of oboe sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Oboe_Zenodo_collections_media.xlsx`
- **Dynamics (2026-08-03):** full 10-level Dynamics_predicter `Results` ladder committed
  (`Oboe_iowa_orchidea_dynamics.xlsx`).
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Bassoon (`fagote` → `bassoon.py`)

- **Module:** `instrumentos/bassoon.py`
- **Table (source_table_span):** `spectral_data` (42 chromatic rows, **A#1–D#5**, MIDI 34–75), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Provenance:** Median/midpoint summary of bassoon sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Bassoon_Zenodo_collections_media.xlsx`
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-08-03):** full 10-level Dynamics_predicter `Results` ladder committed.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Trumpet (`trompete` → `trumpet.py`)

- **Module:** `instrumentos/trumpet.py`
- **Table (source_table_span):** `spectral_data` (36 chromatic rows, **E3–D#6**, MIDI 52–87), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Provenance:** Median/midpoint summary of trumpet (Bb) sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\METAIS\Trumpet_Zenodo_collections_media.xlsx`
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Viola (`viola`)

- **Module:** `instrumentos/viola.py`
- **Table:** `spectral_data` (49 chromatic rows, C3–C7; 147 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of viola arco sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Portable source anchor:** `docs/instrument_acoustic_sources.md#viola` (in `INSTRUMENT_SOURCE`; PR #14)
- **Authoritative ingestion sheet:** `VIOLA_Media` in `D:\CORDAS\ViOLA_Zenodo_collections_media.xlsx`
  (Zenodo deposit name: `viola_arco_sustains_median_summary_v1.xlsx`)
- **Note-label normalization:** duplicate media labels such as `F4 (2)` are stripped by
  `normalize_media_note_label()` before canonical parsing (maps to `F4` with the same CDM values).
- **Sounding range (registry):** MIDI 48–96 (C3–C7), aligned with committed `spectral_data` table span; comfortable 50–69 (D3–A4)
- **Extraction:** CDM midpoint pass-through; no rescaling (`identity_v1`)
- **Dynamics (2026-08-03):** full 10-level Dynamics_predicter `Results` ladder committed.
- **Uncertainty:** medium — sparse table with known QC flags on extreme-register rows

## Viola sordina (`viola_sordina`)

- **Module:** `instrumentos/viola_sordina.py`
- **GUI display name:** `Viola sordina`
- **Table:** `spectral_data` (49 chromatic rows, C3–C7)
- **Provenance (2026-07-24):** assumption-based EWSD extrapolations from
  `Viola_pp.xlsx` / `Viola_mf.xlsx` / `Viola_ff.xlsx` (`All_Results.estimate_mean`,
  technique `con_sordino`); **not** Zenodo-measured CDM
- **Workbook anchors:** pp, mf and ff (`PP_MEASURED`, `MF_MEASURED`, `FF_MEASURED`)
- **Source technique:** `arco_sordina`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_viola_technique_modules_from_xlsx.py`

## Viola sul tasto (`viola_sul_tasto`)

- **Module:** `instrumentos/viola_sul_tasto.py`
- **GUI display name:** `Viola sul tasto`
- **Table:** `spectral_data` (49 chromatic rows, C3–C7)
- **Provenance:** assumption-based EWSD extrapolations from
  `Viola_pp.xlsx` / `Viola_mf.xlsx` / `Viola_ff.xlsx` (technique `sul_tasto`)
- **Workbook anchors:** pp, mf and ff
- **Source technique:** `arco_sul_tasto`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_viola_technique_modules_from_xlsx.py`

## Viola sul ponticello (`viola_sul_ponticello`)

- **Module:** `instrumentos/viola_sul_ponticello.py`
- **GUI display name:** `Viola sul ponticello`
- **Table:** `spectral_data` (49 chromatic rows, C3–C7)
- **Provenance:** assumption-based EWSD extrapolations from
  `Viola_pp.xlsx` / `Viola_mf.xlsx` / `Viola_ff.xlsx` (technique `sul_ponticello`)
- **Workbook anchors:** pp, mf and ff
- **Source technique:** `arco_sul_ponticello`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_viola_technique_modules_from_xlsx.py`
- **Skipped:** artificial/natural harmonics remain `unavailable` in the source
  workbooks — no `viola_art_harm` module

## Violin (`violin`)

- **Module:** `instrumentos/violin.py`
- **Table:** `spectral_data` (49 chromatic rows, G3–G7 × **all 10** dynamics)
- **Provenance (2026-08-03):** IOWA+ORCH measured anchors at pp/mf/ff, with the
  full dynamic ladder committed from Dynamics_predicter sheet **`Results`**
  (data-faithful imputation). Runtime analysis looks up committed cells — it does
  **not** re-run GPR / adaptive-tail extrapolation for violin arco.
- **Source workbook (committed ladder):** Desktop
  `Violino - extrapol/Dynamics_predicter/outputs/iowa_orchidea_dynamics.xlsx`
  (`Results`). Anchor corpus also documented at
  `D:\CORDAS\VIOLIN_Zenodo_collections_media.xlsx`.
- **Regeneration:** `tools/generate_violin_arco_full_dynamics_from_xlsx.py`
  (`--sheet Results`; switch later if needed).
- **Uncertainty:** medium — non-anchor cells remain workbook-modelled, not lab measurements

## Violin sordina (`violin_sordina`)

- **Module:** `instrumentos/violin_sordina.py`
- **Table:** `spectral_data` (49 chromatic rows, G3–G7)
- **Provenance (2026-07-24):** assumption-based EWSD extrapolations from
  `Violin_mf.xlsx` / `Violin_ff.xlsx` (`All_Results.estimate_mean`, technique
  `con_sordino`); **not** Zenodo-measured CDM
- **pp anchors:** derived from violin arco pp/mf ratios applied to workbook mf
- **Source technique:** `arco_sordina`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_violin_technique_modules_from_xlsx.py`

## Violin sul tasto (`violin_sul_tasto`)

- **Module:** `instrumentos/violin_sul_tasto.py`
- **GUI display name:** `Violin sul tasto`
- **Table:** `spectral_data` (49 chromatic rows, G3–G7)
- **Provenance:** assumption-based EWSD extrapolations from
  `Violin_mf.xlsx` / `Violin_ff.xlsx` (technique `sul_tasto`)
- **pp anchors:** derived from violin arco pp/mf ratios applied to workbook mf
- **Source technique:** `arco_sul_tasto`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_violin_technique_modules_from_xlsx.py`

## Violin sul ponticello (`violin_sul_ponticello`)

- **Module:** `instrumentos/violin_sul_ponticello.py`
- **Table:** `spectral_data` (49 chromatic rows, G3–G7)
- **Provenance (2026-07-24):** assumption-based EWSD extrapolations from
  `Violin_mf.xlsx` / `Violin_ff.xlsx` (technique `sul_ponticello`); replaces the
  earlier mf-only hand-curated Zenodo-style table
- **Workbook anchors:** mf and ff (`MF_MEASURED`, `FF_MEASURED`)
- **pp anchors:** derived from violin arco pp/mf ratios applied to workbook mf
- **Non-anchor dynamics:** require committed ladder cells (runtime GPR removed)
- **Source technique:** `arco_sul_ponticello`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_violin_technique_modules_from_xlsx.py`

## Violin art harm (`violin_art_harm`)

- **Module:** `instrumentos/violin_art_harm.py`
- **GUI display name:** `Violin art harm`
- **Table:** `spectral_data` (30 sounding rows, G5–C8)
- **Provenance (2026-07-24):** Strings Techniques Extrapolation harmonic workbooks
  `Violin_pp_hamro.xlsx` / `Violin_mf_harmo.xlsx` / `Violin_ff_harmo.xlsx`
  (`All_Results.estimate_mean`, technique `artificial_harmonic`)
- **Workbook anchors:** pp, mf and ff (`PP_MEASURED`, `MF_MEASURED`, `FF_MEASURED`)
- **Source technique:** `arco_artificial_harmonic`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_violin_harmonic_modules_from_xlsx.py`

## Violin nat harm (`violin_nat_harm`)

- **Module:** `instrumentos/violin_nat_harm.py`
- **GUI display name:** `Violin nat harm`
- **Table:** `spectral_data` (20 sounding rows, G4–B7; duplicate string productions averaged)
- **Provenance (2026-07-24):** same harmonic workbooks as art harm
  (`All_Results.estimate_mean`, technique `natural_harmonic`)
- **Workbook anchors:** pp, mf and ff (`PP_MEASURED`, `MF_MEASURED`, `FF_MEASURED`)
- **Source technique:** `arco_natural_harmonic`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_violin_harmonic_modules_from_xlsx.py`

## Cello (`cello`)

- **Module:** `instrumentos/cello.py`
- **Table:** `spectral_data` (49 chromatic rows, C2–C6)
- **Provenance:** IOWA+ORCH arco sustain CDM medians at pp/mf/ff
- **Source workbook:** `D:\CORDAS\CELLO_Zenodo_collections_media.xlsx`
- **Dynamics (2026-08-03):** full 10-level Dynamics_predicter `Results` ladder committed.
- **Uncertainty:** medium

## Cello sordina (`cello_sordina`)

- **Module:** `instrumentos/cello_sordina.py`
- **GUI display name:** `Cello sordina`
- **Table:** `spectral_data` (49 chromatic rows, C2–C6)
- **Provenance (2026-07-24):** assumption-based EWSD extrapolations from
  `Cello_pp.xlsx` / `Cello_mf.xlsx` / `Cello_ff.xlsx` (`All_Results.estimate_mean`,
  technique `con_sordino`); **not** Zenodo-measured CDM
- **Workbook anchors:** pp, mf and ff (`PP_MEASURED`, `MF_MEASURED`, `FF_MEASURED`)
- **Source technique:** `arco_sordina`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_cello_technique_modules_from_xlsx.py`

## Cello sul tasto (`cello_sul_tasto`)

- **Module:** `instrumentos/cello_sul_tasto.py`
- **GUI display name:** `Cello sul tasto`
- **Table:** `spectral_data` (49 chromatic rows, C2–C6)
- **Provenance:** assumption-based EWSD extrapolations from
  `Cello_pp.xlsx` / `Cello_mf.xlsx` / `Cello_ff.xlsx` (technique `sul_tasto`)
- **Workbook anchors:** pp, mf and ff
- **Source technique:** `arco_sul_tasto`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_cello_technique_modules_from_xlsx.py`

## Cello sul ponticello (`cello_sul_ponticello`)

- **Module:** `instrumentos/cello_sul_ponticello.py`
- **GUI display name:** `Cello sul ponticello`
- **Table:** `spectral_data` (49 chromatic rows, C2–C6)
- **Provenance:** assumption-based EWSD extrapolations from
  `Cello_pp.xlsx` / `Cello_mf.xlsx` / `Cello_ff.xlsx` (technique `sul_ponticello`)
- **Workbook anchors:** pp, mf and ff
- **Source technique:** `arco_sul_ponticello`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_cello_technique_modules_from_xlsx.py`
- **Skipped:** artificial/natural harmonics remain `unavailable` in the source
  workbooks — no `cello_art_harm` module

## Double bass (`double_bass`)

- **Module:** `instrumentos/double_bass.py`
- **Table (source_table_span):** `spectral_data` (45 chromatic rows, **E1–C5**, MIDI 28–72), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Comfortable range:** MIDI 31–55 (G1–G3) — narrower orchestrational band, not a table limit
- **Source technique:** `arco_sustain` (`table_supported_techniques`)
- **Provenance:** IOWA+ORCH arco sustain CDM medians at pp/mf/ff
- **Source workbook:** `D:\CORDAS\DOUBLEBASS_Zenodo_collections_media.xlsx`
- **Dynamics (2026-08-03):** full 10-level Dynamics_predicter `Results` ladder committed.
- **Uncertainty:** medium
- **Span status:** E1–A3 in older docs was obsolete; committed span is E1–C5 (**PASS**). Upper-register methodological QC (A♯3–C5) remains **REVIEW REQUIRED**.

## Double bass sordina (`double_bass_sordina`)

- **Module:** `instrumentos/double_bass_sordina.py`
- **GUI display name:** `Double bass sordina`
- **Table:** `spectral_data` (45 chromatic rows, E1–C5)
- **Provenance (2026-07-24):** assumption-based EWSD extrapolations from
  `Contrabass-pp.xlsx` / `Contrabass_mf.xlsx` / `Contrabass_ff.xlsx`
  (`All_Results.estimate_mean`, technique `con_sordino`); **not** Zenodo-measured CDM
- **Workbook anchors:** pp, mf and ff (`PP_MEASURED`, `MF_MEASURED`, `FF_MEASURED`)
- **Source technique:** `arco_sordina`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_double_bass_technique_modules_from_xlsx.py`

## Double bass sul tasto (`double_bass_sul_tasto`)

- **Module:** `instrumentos/double_bass_sul_tasto.py`
- **GUI display name:** `Double bass sul tasto`
- **Table:** `spectral_data` (45 chromatic rows, E1–C5)
- **Provenance:** assumption-based EWSD extrapolations from
  `Contrabass-pp.xlsx` / `Contrabass_mf.xlsx` / `Contrabass_ff.xlsx` (technique `sul_tasto`)
- **Workbook anchors:** pp, mf and ff
- **Source technique:** `arco_sul_tasto`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_double_bass_technique_modules_from_xlsx.py`

## Double bass sul ponticello (`double_bass_sul_ponticello`)

- **Module:** `instrumentos/double_bass_sul_ponticello.py`
- **GUI display name:** `Double bass sul ponticello`
- **Table:** `spectral_data` (45 chromatic rows, E1–C5)
- **Provenance:** assumption-based EWSD extrapolations from
  `Contrabass-pp.xlsx` / `Contrabass_mf.xlsx` / `Contrabass_ff.xlsx`
  (technique `sul_ponticello`)
- **Workbook anchors:** pp, mf and ff
- **Source technique:** `arco_sul_ponticello`
- **Dynamics:** sparse pp/mf/ff until a full ladder is committed (missing cells error)
- **Uncertainty:** high
- **Regeneration:** `tools/generate_double_bass_technique_modules_from_xlsx.py`
- **Skipped:** artificial/natural harmonics remain `unavailable` in the source
  workbooks — no `double_bass_art_harm` module

## Generation tooling

Offline curation pipeline (not used at runtime):

1. `tools/populate_td_importer_sheets_from_zenodo_media.py` — builds `AcousticTable`, `Registry`, and `Provenance` sheets from `*_Media` workbooks. Applies `normalize_media_note_label()` when reading media rows (strips trailing `(2)` duplicate markers).
2. `tools/generate_instrument_modules.py` — emits `instrumentos/flute.py`, `oboe.py`, `clarinet.py`, `violin.py`, `viola.py`, `cello.py`, `double_bass.py`. Viola and double bass source reconstruction use the `VIOLA_Media` / `DBass_Media` sheets via `load_spectral_data_from_media` (their workbooks ship no `AcousticTable` sheet).
3. `tools/generate_violin_technique_modules_from_xlsx.py` — emits / replaces `violin_sordina.py`, `violin_sul_tasto.py`, `violin_sul_ponticello.py` from Desktop `Violin_mf.xlsx` / `Violin_ff.xlsx` (pp via arco ratio transfer).
4. `tools/generate_viola_technique_modules_from_xlsx.py` — emits `viola_sordina.py`, `viola_sul_tasto.py`, `viola_sul_ponticello.py` from Desktop `Viola_pp.xlsx` / `Viola_mf.xlsx` / `Viola_ff.xlsx` (pp/mf/ff direct from `estimate_mean`).
5. `tools/generate_cello_technique_modules_from_xlsx.py` — emits `cello_sordina.py`, `cello_sul_tasto.py`, `cello_sul_ponticello.py` from Desktop `Cello_pp.xlsx` / `Cello_mf.xlsx` / `Cello_ff.xlsx` (pp/mf/ff direct from `estimate_mean`).
6. `tools/generate_double_bass_technique_modules_from_xlsx.py` — emits `double_bass_sordina.py`, `double_bass_sul_tasto.py`, `double_bass_sul_ponticello.py` from Desktop `Contrabass-pp.xlsx` / `Contrabass_mf.xlsx` / `Contrabass_ff.xlsx` (pp/mf/ff direct from `estimate_mean`).
7. `tools/build_viola_table_from_media.py` — helper to regenerate viola `spectral_data` from `VIOLA_Media`.
8. `tools/generate_full_dynamics_modules_from_xlsx.py` — commits Dynamics_predicter sheet `Results` ladders into ordinary-sustain modules (`viola`, `cello`, `double_bass`, `flute`, `clarinet`, `bassoon`, `oboe`).
9. `tools/generate_violin_arco_full_dynamics_from_xlsx.py` — violin arco `Results` ladder regenerator.
10. `tools/refresh_regression_fixtures.py` — updates golden regression/snapshot/benchmark fixtures after intentional table changes.

**Violin harmonics:** `violin_art_harm.py` and `violin_nat_harm.py` are regenerated from Strings Techniques Extrapolation harmonic workbooks (pp/mf/ff). Violin/viola/cello/double-bass sordina, sul tasto, and sul ponticello modules are regenerated from STE technique workbooks (assumption-based EWSD; high uncertainty). Non-anchor dynamics on those sparse modules raise `MissingCommittedDynamicError` until full ladders are committed (runtime GPR removed 2026-08-03).

## Media note-label normalization (PR #14)

External Zenodo `*_Media` sheets may label duplicate chromatic rows with a trailing `(2)` suffix (e.g. `F4 (2)`). Before canonical note parsing:

```python
from utils.notes import normalize_media_note_label

normalize_media_note_label("F4 (2)")  # → "F4"
```

Applied in `tools/populate_td_importer_sheets_from_zenodo_media.py` (`_read_media_rows`) and `tools/generate_instrument_modules.py`. This corrects **source-table parsing and alignment** — not acoustic meaning or perceptual validation.

## Source workbook reconstruction (local verification)

| Workbook | Media sheet | Rows | Local status |
|----------|-------------|------|--------------|
| `VIOLIN_Zenodo_collections_media.xlsx` | `Violin_Media` | 49 | **SKIPPED** in suite — workbook path not accessible on this machine (`UNVERIFIED — SOURCE WORKBOOK NOT ACCESSIBLE`); will activate once deposited |
| `ViOLA_Zenodo_collections_media.xlsx` | `VIOLA_Media` | 49 | **SKIPPED** in suite — workbook path not accessible; will activate once deposited |
| `CELLO_Zenodo_collections_media.xlsx` | `Cello_Media` | 49 | **PASS** — 0 value differences vs committed module |
| `DOUBLEBASS_Zenodo_collections_media.xlsx` | `DBass_Media` | 45 | **PASS** |

**CI:** `tests/test_string_source_reproducibility.py` skips when workbooks are absent on the runner (see archiving note above). Local reconstruction status for cello and double_bass currently **PASS**; violin and viola skip in the suite until deposited. CI verifies committed modules and unit tests; independent reconstruction requires local workbooks or future canonical fixtures.

## Technique metadata vs source tables

Registry `supported_techniques` lists organological capabilities. Table-backed modules declare `INSTRUMENT_SOURCE.source_technique` and `table_supported_techniques` for the numerical table actually committed (e.g. `arco_sustain` for strings, `ordinary_sustain` for winds). Pizzicato, tremolo, harmonics, mute, flutter-tongue, etc. are **not** modelled unless separate technique-specific tables exist.

Audit: `tools/audit_instrument_metadata_range_resolution.py` → `reports/instrument_metadata_range_resolution_audit.*`

## Scientific review candidates (pending adjudication)

| ID | Topic | Status |
|----|-------|--------|
| DB-SPAN | Double-bass `source_table_span` E1–C5 aligns with committed table and registry; E1–A3 was obsolete documentation. Upper-register QC (A♯3–C5) open. | **PASS** (span); **REVIEW REQUIRED** (upper QC) |
| TECHNIQUE | `INSTRUMENT_SOURCE.table_supported_techniques` vs registry `supported_techniques`; tables do not overclaim technique coverage. | **PASS** |
| TUBA-RNG | Tuba sounding_range MIDI 28–58 is coarse-default validation placeholder without source table. | **REVIEW REQUIRED** |
| TRANS-META | `registry.transposition` is metadata-only; manual input is sounding pitch; MusicXML `<transpose>` converts once. | **PASS** |
| LEGACY-GPR | Runtime GPR retired 2026-08-03; historical code at `tools/legacy_gpr_dynamic_interpolation.py`. | **N/A (retired)** |
| GPR-MQ | GPR model-quality audit (`tools/audit_gpr_model_quality.py`): 357 source rows (8 GPR modules, incl. bassoon); 58 convex-hull departures (pp–mf); GPR–linear/quadratic/PCHIP diagnostic deviations. Production GPR unchanged; references not adopted. | **REVIEW REQUIRED** (local hull departures; low-register strings) |
| GPR-CMP | Interpolation method comparison (`tools/compare_dynamic_interpolation_methods.py`): GPR vs linear vs PCHIP — 357 source rows, 320+20 scenarios, 5 benchmark excerpts. **0** high/extreme scenario-level `density.instrument` cases; production GPR unchanged; linear/PCHIP not adopted. | **PASS** (diagnostic complete; policy selection deferred) |

**Resolved (PR #14):** viola `INSTRUMENT_SOURCE` portable provenance (`docs/instrument_acoustic_sources.md#viola`).

## Register-dependence audit (2026-07-12, read-only)

Findings of a read-only audit of register dependence and per-event propagation
(no code, config, or data changes; `METRIC_SCHEMA_VERSION` unchanged):

- **Provenance uniformity.** All module-backed tables encode the same class of
  datum — a **Combined Density Metric (CDM)**, a spectral-density-derived measure
  (midpoint/median of IOWA+ORCH sustain collections at pp/mf/ff). None are raw
  amplitude/SPL pressure and none are literature-derived. Two variants are flagged
  as partly synthetic: **`violin_sul_ponticello`** and **`violin_art_harm`** carry
  a **measured mf anchor only**, with pp/ff transferred from violin-arco per-note
  ratios (`uncertainty="high"`).
- **mf curve shapes.** One-player mf density sampled every 3 semitones is
  **non-monotone for every instrument** (downward-trending with local reversals,
  typically at register/string breaks — e.g. violin C#4→E4, cello F#2→C3,
  contrabass C#2→E2, bassoon C#4→G4). No instrument is cleanly monotone-decreasing;
  do not assume monotonicity when reasoning about register.
- **Per-event fidelity.** The pipeline resolves density at the **exact event MIDI**
  (`microtonal.note_to_midi_strict`, float — carries quarter-tones and cents).
  Interpolation between chromatic anchors is shape-preserving PCHIP in-range
  (≥4 anchors) else linear; edge extrapolation is linear, with constant fallback
  beyond 12 semitones (`pitch_interpolation.resolve_density_from_table`). There is
  **no cross-event averaging/banding** of the one-player weight (the only mean is
  the per-pitch-bin spectral-weight mean, which collapses exact-MIDI unisons only).
  At every module's sounding-range extremes the endpoints coincide with table
  anchors, so lookups return provenance `exact` with **Δ = 0** vs the raw table
  value; smoothing affects only microtonal between-anchor targets.
- **Deconfounded REG (REGNAT) sweep.** A fixed 3-semitone chromatic cluster at
  bottom/centre/top-3 positions for clarinete, fagote, violino, contrabaixo yields
  **S invariant** (= 2.6284; register-independent symbolic interval measure) and
  **mass/RSS/comp strictly decreasing** with ascent for all four — no violations at
  the sampled positions. (Local curve non-monotonicity above can still surface if a
  sweep samples adjacent to a reversal.)

## Epistemic limitations

- Verification tests validate implementation contracts, source consistency, provenance propagation, symbolic/musical invariants, and reproducibility under controlled conditions.
- Tests do **not** validate auditory adequacy of the CDM model or prove correspondence to listener judgments of textural density, symbolic-dynamic mass, salience, or timbral mass.
- Acoustic metadata are externally sourced and/or interpolated — not measured by Textural Density during score analysis.
- Note-label normalization corrects parsing and table-key alignment only.

## Percussion — NonTunPerc MC Analysis (`bass_drum`, `cymbals`, `tamtam`, `gong`)

Unpitched idiophone / membranophone modules backed by Percussion Tool
(NonTunPerc) **MC median** Analysis exports. Registry / `INSTRUMENT_SOURCE`
set `unpitched=True`; core excludes their note keys from pitch-structure
metrics (`core/unpitched_routing.py`).

| Module | Registry ID | Specimen | Phase | Placeholder | Technique |
|--------|-------------|----------|-------|-------------|-----------|
| `bass_drum.py` | `bombo` | `bassdrum_82cm` | **strike** | `D2` | `struck_membrane` |
| `cymbals.py` | `pratos` | `cymbal_46cm_medium` | **shimmer** | `C5` | `struck_plate` |
| `tamtam.py` | `tamtam` | `tamtam_80cm_bronze` | **shimmer** | `C2` | `struck_plate` |
| `gong.py` | `gongo` | `gong_50cm_bronze` | **shimmer** | `C3` | `struck_plate` |

- **ff anchor:** MC p50 `composite_index` for the chosen phase from
  `replication/percussion_nontunperc/Analysis/density_profiles_mc.csv`
  (p05/p95 retained as `SPECTRAL_PHASE_CI` / `spectral_data_ci`).
- **pp / mf:** `generate_profile(stroke=bass_drum_beater|yarn_mallet, dynamic=…)`
  phase indices, scaled so ff matches MC p50. ff plate bypass / cascade
  discontinuity is retained (documented mf→ff jump).
- **Dynamics (2026-08-03):** full 10-level `DYNAMIC_CDM` committed offline from the
  former `internal_default` piecewise log-linear CDM + adaptive tails
  (`log_cdm_space=True` — not Matérn GPR). No runtime fill-in.
- **Pitch:** not used. GUI/MusicXML/MIDI have no sounding pitch for these
  instruments; `calcular_densidade` ignores `nota`. One canonical placeholder
  key remains in `spectral_data` for lookup-shape compatibility only.
- **Provenance:** `source_type=model_derived`; NonTunPerc
  v0.3.5 commit `4a110db…`; MC seed `20260803`. Calibration bridge reports
  **NO CALIBRATION ACHIEVED** — cross-family CDM ratios are rank-order only.
- **Regenerate:** `python tools/generate_percussion_modules_from_nontunperc.py`
- **Placeholder keys (lookup only, no acoustic meaning):** Bass drum `D2`, Cymbals `C5`, Tam-tam `C2`, Gong `C3` (registry `sounding_range` midpoints via `canonical_unpitched_note`).
- **Entry paths:** GUI, MusicXML `<unpitched>`, and MIDI channel-10 all emit `InstrumentEvent.unpitched=True` plus that placeholder. Display-step/octave and GM key numbers are never treated as sounding pitch. Unmappable events are skipped with a warning (part + measure for MusicXML; key for MIDI) — no pitched fallback. Pitch-structure exclusion is only in `partition_pitched_events`. Full map: `docs/TECHNICAL_MANUAL.md` §7.5.
- **Aggregation (PR #31 / Task 8b + PR #33 / Task 8c):** Event/Player Count and texture player/CDM averages **include** these events; interval / pitch-structure / texture polyphony do **not**. Composite uses the **unified** blend×mass path for all regimes (`log10(1 + density.weighted*sqrt(M)/REF)`, `REF=193`; `D_blend = w*(DI/10)+(1−w)*DV` at defaults) — no unpitched-only fallback. Header / exclusion labels: PR #35 (`core.composite`, `core.unpitched_labels`). Contract table: `docs/TECHNICAL_MANUAL.md` §7.5.1; traceability: `CHANGES.md`.

## Registry-only instruments

Instruments without a dedicated module use `coarse_default.py` — register and
dynamic coarse models **without** external acoustic amplitude tables. Status:
`coarse_default` / audit label `symbolic_default`.

## Adding sourced profiles

1. Commit acoustic table + `INSTRUMENT_SOURCE` in the module.
2. Register in `instrumentos/registry.py`.
3. Document provenance in this file.

## Quantity (Qty) scaling

Textural Density treats `Qty` as player count for a symbolic event. Instrument modules return **one-player** density for a (note, dynamic) pair. Slice-level metrics apply:

- **Mass:** $\sum_j n_j \cdot d_j^{(1)}$ (linear)
- **Pressure-equivalent density:** $\sqrt{\sum_j n_j (d_j^{(1)})^2}$ (incoherent RSS)

Dynamics are encoded in the module lookup — not multiplied again in the mass formula. This is symbolic metadata, not measured SPL.

When adding profiles, also document citation and extraction method, register with honest `source_notes`, and ensure CI test `test_acoustic_instrument_modules_have_provenance` passes.
