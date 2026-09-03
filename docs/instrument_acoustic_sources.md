# Instrument acoustic source provenance

> **Corpus status (2026-09-03):** The instrument metadata layer is **incomplete and under gradual curation**. Some registry entries lack dedicated acoustic tables; table-backed modules are **partial proxies**. Runtime no longer fills missing dynamics with GPR — table-backed pitched modules (winds including piccolo / English horn / bass clarinet / contrabassoon, brass incl. horn, trombone and tuba, arco strings, violin/viola/cello/double-bass techniques/harmonics) and unpitched percussion commit full 10-level ladders. Ladders are **data-faithful** (2026-08-08/09/18/27/30, dest-Zenodo refresh 2026-09-03, Dynamics_predicter v1.5.2.1): measured pp/mf/ff anchors verbatim, PCHIP interiors, tapered outers — **not** forced monotone. Cello and double-bass sul tasto remain withdrawn (2026-08-18). Missing or coarse values are expected when `source_type`, `profile_status`, and warnings remain honest.

This document records **external acoustic metadata** embedded in `instrumentos/*.py`
modules. The analysis pipeline performs **score lookup** into these tables — not
live audio analysis.

> **Workbook archiving.** Primary CDM workbooks for winds/brass (and the string
> Zenodo collections cited below) live at **private local paths** (e.g.
> `D:\MADEIRAS\…`, `D:\METAIS\…`, `D:\CORDAS\…`) and are **not** committed to this
> repository. Intention: deposit in-repo extracts or a citable external archive so
> reconstruction tests can run without a private machine. Until then,
> `tests/test_string_source_reproducibility.py` **skips** when a workbook file is
> absent; on a machine with the deposits present (2026-08-08 config fix), all four
> string reconstructions — **violin, viola, cello, double_bass** — verify against
> their curated `*_Media` sheets and **PASS** (0 value differences).
> Runtime dynamics lookup is table-only (2026-08-03). Historical GPR audits remain
> under `tools/legacy_gpr_dynamic_interpolation.py` / `reports/`.

## Flute (`flute`)

- **Module:** `instrumentos/flute.py`
- **Table:** `spectral_data` (40 chromatic rows, B3–D7; 120 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of flute sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Flute_Zenodo_collections_media.xlsx`
- **Dynamics (2026-08-08; refreshed 2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder committed (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers). Refresh source: `Flute_Zenodo_collections_ordinario_Dynamics10.xlsx`.
- **Uncertainty:** medium — sparse table, not full continuous spectrum.

## Clarinet (`clarinet`)

- **Module:** `instrumentos/clarinet.py`
- **Table:** `spectral_data` (47 chromatic rows, D3–C7; 141 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of clarinet sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Clarinet_Zenodo_collections_media.xlsx`
- **Dynamics (2026-08-08; refreshed 2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder committed (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers). Refresh source: `Clarinet_Zenodo_collections_Dynamics10.xlsx`.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Oboe (`oboe`)

- **Module:** `instrumentos/oboe.py`
- **Table:** `spectral_data` (36 chromatic rows, A#3–A6; 108 AcousticTable rows in source workbook)
- **Provenance:** Median/midpoint summary of oboe sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Oboe_Zenodo_collections_media.xlsx`
- **Dynamics (2026-08-08; refreshed 2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder committed (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers). Refresh source: `Oboe_Zenodo_collections_Dynamics10.xlsx`.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Bassoon (`fagote` → `bassoon.py`)

- **Module:** `instrumentos/bassoon.py`
- **Table (source_table_span):** `spectral_data` (42 chromatic rows, **A#1–D#5**, MIDI 34–75), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Provenance:** Median/midpoint summary of bassoon sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\MADEIRAS\Bassoon_Zenodo_collections_media.xlsx`
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-08-08; refreshed 2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder committed (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers). Refresh source: `Basson_Zenodo_collections_Dynamics10.xlsx`.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Piccolo (`flautim` → `piccolo.py`)

- **Module:** `instrumentos/piccolo.py`
- **GUI display name:** `Picc`
- **Table (source_table_span):** `spectral_data` (40 chromatic rows, **B3–D7**, MIDI 59–98)
- **Provenance:** Median/midpoint summary of piccolo sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `Piccolo_Zenodo_collections_ordinario_Dynamics10.xlsx` (sheet `Results`)
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## English horn (`cor_anglais` → `english_horn.py`)

- **Module:** `instrumentos/english_horn.py`
- **GUI display name:** `E_Horn`
- **Table (source_table_span):** `spectral_data` (35 chromatic rows, **A#3–G#6**, MIDI 58–92)
- **Provenance:** Median/midpoint summary of English-horn sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `English_horn_Zenodo_collections_ordinario_Dynamics10.xlsx` (sheet `Results`)
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Bass clarinet (`clarinete_baixo` → `bass_clarinet.py`)

- **Module:** `instrumentos/bass_clarinet.py`
- **GUI display name:** `Bass_Clar`
- **Table (source_table_span):** `spectral_data` (46 chromatic rows, **C#2–A#5**, MIDI 37–82)
- **Provenance:** Median/midpoint summary of bass-clarinet sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `Bass_clarinet_in_Bb_Zenodo_collections_ordinario_Dynamics10.xlsx` (sheet `Results`)
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Contrabassoon (`contrafagote` → `contrabassoon.py`)

- **Module:** `instrumentos/contrabassoon.py`
- **GUI display name:** `Contr_Basson`
- **Table (source_table_span):** `spectral_data` (42 chromatic rows, **A#1–D#5**, MIDI 34–75)
- **Provenance:** Median/midpoint summary of contrabassoon sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `Contrabassoon_Zenodo_collections_ordinario_Dynamics10.xlsx` (sheet `Results`)
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Trumpet (`trompete` → `trumpet.py`)

- **Module:** `instrumentos/trumpet.py`
- **Table (source_table_span):** `spectral_data` (36 chromatic rows, **E3–D#6**, MIDI 52–87), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Provenance:** Median/midpoint summary of trumpet (Bb) sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\METAIS\Trumpet_Zenodo_collections_media.xlsx`
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-08-08; refreshed 2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder committed (measured pp/mf/ff anchors verbatim; the earlier D6 isotonic clamp is no longer applied). Refresh source: `Trumpet_Zenodo_collections_Dynamics10.xlsx`.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Horn (`trompa` → `horn.py`)

- **Module:** `instrumentos/horn.py`
- **Table (source_table_span):** `spectral_data` (44 chromatic rows, **A#1–F5**, MIDI 34–77), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Provenance:** Median/midpoint summary of horn sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\METAIS\Horn_Zenodo_collections_media.xlsx` (sheet `Horn_Media`)
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-08-08; refreshed 2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder committed (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers). Refresh source: `Horn_in_F_Zenodo_collections_ordinario_Dynamics10.xlsx`.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Trombone (`trombone` → `trombone.py`)

- **Module:** `instrumentos/trombone.py`
- **GUI display name:** `Trb`
- **Table (source_table_span):** `spectral_data` (44 chromatic rows, **F1–C5**, MIDI 29–72), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`. C#1–E1 are omitted because dest books lack a complete pp/mf/ff triad.
- **Provenance:** Midpoint summary of trombone sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff) from dest Zenodo books.
- **Source workbook:** `D:\METAIS_2\Trombone_dynamics.xlsx` (sheet `Results`)
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-08-24; refreshed 2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder committed (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers). Refresh source: `Trombone_Zenodo_collections_Dynamics10.xlsx`.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Tuba (`tuba` → `tuba.py`)

- **Module:** `instrumentos/tuba.py`
- **Table (source_table_span):** `spectral_data` (47 chromatic rows, **C1–A#4**, MIDI 24–70), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Provenance:** Median/midpoint summary of tuba sustained-note Combined Density
  Metrics across IOWA and ORCH sound collections (pp, mf, ff).
- **Source workbook:** `D:\METAIS\Tuba_Zenodo_collections_media.xlsx` (sheet `Tuba_Media`)
- **Source technique:** `ordinary_sustain` (`table_supported_techniques`)
- **Dynamics (2026-08-09; refreshed 2026-09-03):** full 10-level data-faithful Dynamics_predicter v1.5.2.1 `Results` ladder committed (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers). Refresh source: `Tuba_Zenodo_collections_Dynamics10.xlsx`.
- **Uncertainty:** medium — sparse table, not full continuous spectrum

## Viola (`viola`)

- **Module:** `instrumentos/viola.py`
- **GUI display name:** `vla`
- **Table:** `spectral_data` (47 chromatic rows, C3–A#6 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `VIOLA_Zenodo_collections_Arco_normal_Dynamics10.xlsx`
  (Dynamics10 dest-Zenodo). Anchors are dest-Zenodo
  `VIOLA_Media` M:N:O (IOWA+Orchidea average) at pp/mf/ff.
- **Portable source anchor:** `docs/instrument_acoustic_sources.md#viola` (in `INSTRUMENT_SOURCE`; PR #14)
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Sounding range (registry):** MIDI 48–94 (C3–A#6), aligned with committed `spectral_data` table span; comfortable 50–69 (D3–A4)
- **Source technique:** `arco_sustain`
- **Uncertainty:** medium — sparse table, not full continuous spectrum
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Viola sordina (`viola_sordina`)

- **Module:** `instrumentos/viola_sordina.py`
- **GUI display name:** `vla sord` (aliases: `vla_sord`, `vla_con_sord`)
- **Table:** `spectral_data` (47 chromatic rows, C3–A#6 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Viola_Zenodo_collections_con_sordino_Dynamics10.xlsx`
  (dest Zenodo con sordino Media = average of available IOWA W and Orchidea F).
  No B6–C7 rows: dest Media stops at A#6.
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_sordina`
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Viola sul tasto — retired (2026-08-11)

The assumption-based STE module `viola_sul_tasto.py` (GUI "Viola sul tasto")
was removed together with its generator; no dest-Zenodo viola sul tasto
dynamics workbook exists. The technique will return once a measured-anchor
extrapolation workbook is available.

## Viola sul ponticello (`viola_sul_ponticello`)

- **Module:** `instrumentos/viola_sul_ponticello.py`
- **GUI display name:** `vla sp` (aliases: `vla_sp`, `vla_sul_pont`)
- **Table:** `spectral_data` (41 chromatic rows, C3–E6 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Viola_Zenodo_collections_sul_ponticello_Dynamics10.xlsx`
  (dest Zenodo sul ponticello Media). Dest Media stops at E6.
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_sul_ponticello`
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Viola harmonics (`viola_harmonics`)

- **Module:** `instrumentos/viola_harmonics.py`
- **GUI display name:** `vla harm` (aliases: `vla_harm`)
- **Table:** `spectral_data` (23 chromatic sounding rows, C5–A#6 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Viola_Zenodo_collections_harmonics_Dynamics10.xlsx`
  (dest Zenodo harmonics Media). Media harmonics start at C5 and stop at A#6.
  Do not invent C3–B4 or B6–B7 from older fills that are absent from Media.
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_harmonic` (pooled)
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Violin (`violin`)

- **Module:** `instrumentos/violin.py`
- **Table:** `spectral_data` (53 chromatic rows, G3–B7 × **all 10** dynamics)
- **Provenance (2026-09-03):** IOWA+ORCH measured anchors at pp/mf/ff, with the
  full dynamic ladder committed from Dynamics10 `VIOLIN_Zenodo_collections_Arco_normal_Dynamics10.xlsx`
  sheet **`Results`**. Runtime analysis looks up committed cells — it does
  **not** re-run GPR / adaptive-tail extrapolation for violin arco.
- **Authoritative ingestion sheet:** `Violin_Media` in the dest-Zenodo
  `VIOLIN_Zenodo_collections_Arco_normal.xlsx` book that Dynamics10 was built from.
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)
- **Uncertainty:** medium — non-anchor cells remain workbook-modelled, not lab measurements

## Violin sordina (`violin_sordina`)

- **Module:** `instrumentos/violin_sordina.py`
- **GUI display name:** `vl_con_sord` (aliases: `vl sord`, `vl_sord`)
- **Table:** `spectral_data` (42 chromatic rows, G3–C7 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Violin_Zenodo_collections_con_sordino_Dynamics10.xlsx`
  (dest Zenodo con sordino Media = average of available IOWA W and Orchidea F)
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8), Dynamics_predicter v1.5.2.1
- **Source technique:** `arco_sordina`
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Violin sul tasto (`violin_sul_tasto`)

- **Module:** `instrumentos/violin_sul_tasto.py`
- **GUI display name:** `vl_sul_tast` (aliases: `vl st`, `vl_st`)
- **Table:** `spectral_data` (53 chromatic rows, G3–B7 × **all 10** dynamics)
- **Provenance (2026-08-30):** `Results` sheet of
  `Violin_Dynamics10_sul_tasto.xlsx`
  (dest Zenodo sul tasto Media)
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8), Dynamics_predicter v1.5.2.1
- **Source technique:** `arco_sul_tasto`
- **Uncertainty:** high
- **Regeneration:** `tools/generate_violin_technique_modules_from_ok_workbooks.py --violin-only`

## Violin sul ponticello (`violin_sul_ponticello`)

- **Module:** `instrumentos/violin_sul_ponticello.py`
- **GUI display name:** `vl_sul_pont` (aliases: `vl sp`, `vl_sp`)
- **Table:** `spectral_data` (42 chromatic rows, G3–C7 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Violin_Zenodo_collections_sul_ponticello_Dynamics10.xlsx`
  (dest Zenodo sul ponticello Media)
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8), Dynamics_predicter v1.5.2.1
- **Source technique:** `arco_sul_ponticello`
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Violin harmonics (`violin_harmonics`)

- **Module:** `instrumentos/violin_harmonics.py`
- **GUI display name:** `vl_harm` (alias: `vl harm`)
- **Table:** `spectral_data` (29 chromatic sounding rows, G5–B7 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Violin_Zenodo_collections_harmonics_Dynamics10.xlsx`
  (dest Zenodo harmonics Media; notes with a complete pp/mf/ff triad only)
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8), Dynamics_predicter v1.5.2.1
- **Source technique:** `arco_harmonic` (pooled)
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)
- **History (2026-08-11):** replaces the retired split `violin_nat_harm` /
  `violin_art_harm` modules; their aliases now resolve to this pooled table

## Cello (`cello`)

- **Module:** `instrumentos/cello.py`
- **Table:** `spectral_data` (49 chromatic rows, C2–C6 × **all 10** dynamics)
- **Provenance (2026-09-03):** IOWA+ORCH arco sustain CDM medians at pp/mf/ff from
  Dynamics10 `CELLO_Zenodo_collections_Arco_normal_Dynamics10.xlsx` `Results`.
- **Source workbook:** dest-Zenodo `CELLO_Zenodo_collections_media.xlsx` (`Cello_Media`)
- **Dynamics (2026-09-03):** full 10-level data-faithful Dynamics10 `Results` ladder (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers).
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)
- **Uncertainty:** medium

## Cello sordina (`cello_sordina`)

- **Module:** `instrumentos/cello_sordina.py`
- **GUI display name:** `vlc_sord` (aliases: `vlc_con_sord`, `violoncelo_sordina`)
- **Table:** `spectral_data` (46 chromatic rows, C2–A5 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Cello_Zenodo_collections_con_sordino_Dynamics10.xlsx`
  (dest Zenodo con sordino Media = average of available IOWA W and Orchidea F).
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_sordina`
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Cello sul tasto — withdrawn (2026-08-18)

The assumption-based STE module `cello_sul_tasto.py` remains withdrawn; no
dest-Zenodo cello sul tasto dynamics workbook exists.

## Cello sul ponticello (`cello_sul_ponticello`)

- **Module:** `instrumentos/cello_sul_ponticello.py`
- **GUI display name:** `vlc_sp` (aliases: `vlc_sul_pont`, `violoncelo_sul_ponticello`)
- **Table:** `spectral_data` (46 chromatic rows, C2–A5 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Cello_Zenodo_collections_sul_ponticello_Dynamics10.xlsx`
  (dest Zenodo sul ponticello Media).
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_sul_ponticello`
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Cello harmonics (`cello_harmonics`)

- **Module:** `instrumentos/cello_harmonics.py`
- **GUI display name:** `vlc_harm`
- **Table:** `spectral_data` (25 chromatic sounding rows, C4–C6 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Cello_Zenodo_collections_harmonics_Dynamics10.xlsx`
  (dest Zenodo harmonics Media). Media harmonics start at C4 and stop at C6.
  C2–B3 and the old C#6–E7 tail are not invented.
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_harmonic` (pooled)
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Double bass (`double_bass`)

- **Module:** `instrumentos/double_bass.py`
- **Table (source_table_span):** `spectral_data` (45 chromatic rows, **E1–C5**, MIDI 28–72), matching `INSTRUMENT_SOURCE.pitch_range` and `registry.sounding_range`
- **Comfortable range:** MIDI 31–55 (G1–G3) — narrower orchestrational band, not a table limit
- **Source technique:** `arco_sustain` (`table_supported_techniques`)
- **Provenance (2026-09-03):** IOWA+ORCH arco sustain CDM medians at pp/mf/ff from
  Dynamics10 `DOUBLEBASS_Zenodo_collections_Arco_normal_Dynamics10.xlsx` `Results`.
- **Source workbook:** dest-Zenodo `DOUBLEBASS_Zenodo_collections_media.xlsx` (`DBass_Media`)
- **Dynamics (2026-09-03):** full 10-level data-faithful Dynamics10 `Results` ladder (measured pp/mf/ff anchors verbatim; PCHIP interiors, tapered outers).
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)
- **Uncertainty:** medium
- **Span status:** E1–A3 in older docs was obsolete; committed span is E1–C5 (**PASS**). Upper-register methodological QC (A♯3–C5) remains **REVIEW REQUIRED**.

Double-bass sul tasto remains withdrawn (2026-08-18; no dest-Zenodo sul tasto workbook).

## Double bass sordina (`double_bass_sordina`)

- **Module:** `instrumentos/double_bass_sordina.py`
- **GUI display name:** `cb_sord` (aliases: `cb_con_sord`, `contrabaixo_sordina`)
- **Table:** `spectral_data` (40 chromatic rows, E1–G4 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Double_bass_Zenodo_collections_con_sordino_Dynamics10.xlsx`
  (dest Zenodo con sordino Media).
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_sordina`
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Double bass sul tasto — withdrawn (2026-08-18)

The assumption-based STE module `double_bass_sul_tasto.py` remains withdrawn; no
dest-Zenodo double-bass sul tasto dynamics workbook exists.

## Double bass sul ponticello (`double_bass_sul_ponticello`)

- **Module:** `instrumentos/double_bass_sul_ponticello.py`
- **GUI display name:** `cb_sp` (aliases: `cb_sul_pont`, `contrabaixo_sul_ponticello`)
- **Table:** `spectral_data` (40 chromatic rows, E1–G4 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Double_bass_Zenodo_collections_sul_ponticello_Dynamics10.xlsx`
  (dest Zenodo sul ponticello Media).
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_sul_ponticello`
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Double bass harmonics (`double_bass_harmonics`)

- **Module:** `instrumentos/double_bass_harmonics.py`
- **GUI display name:** `cb_harm`
- **Table:** `spectral_data` (40 chromatic sounding rows, E3–G6 × **all 10** dynamics)
- **Provenance (2026-09-03):** `Results` sheet of
  `Double_bass_Zenodo_collections_harmonics_Dynamics10.xlsx`
  (dest Zenodo harmonics Media). Notes below E3 are not invented.
- **Workbook anchors:** measured pp, mf and ff committed verbatim in
  `spectral_data`; p/mp/f PCHIP interiors; pppp/ppp/fff/ffff tapered
  equal-log outers (r=0.8)
- **Source technique:** `arco_harmonic` (pooled)
- **Uncertainty:** high
- **Regeneration:** `tools/commit_dynamics_from_para_dinamicas.py` (2026-09-03 dest-Zenodo refresh)

## Generation tooling

Offline curation pipeline (not used at runtime):

1. `tools/commit_dynamics_from_para_dinamicas.py` — **current (2026-09-03)** commit path. Reads Desktop `para dinâmicas\*_Dynamics10.xlsx` `Results` (`status=ok`), normalizes note labels, clamps interiors into [pp,mf]/[mf,ff], and writes all table-backed pitched modules except violin sul tasto (no new book).
2. `tools/populate_td_importer_sheets_from_zenodo_media.py` — builds `AcousticTable`, `Registry`, and `Provenance` sheets from `*_Media` workbooks. Applies `normalize_media_note_label()` when reading media rows (strips trailing `(2)` duplicate markers).
3. `tools/generate_instrument_modules.py` — legacy 3-anchor generator; its `CONFIGS` also drive the source-reconstruction audit. All four string reconstructions read the curated Media sheets (`Violin_Media`, `VIOLA_Media`, `Cello_Media`, `DBass_Media`) via `load_spectral_data_from_media` (2026-08-08 config fix).
4. `tools/generate_violin_technique_modules_from_xlsx.py` — historical emitter for `violin_sordina.py`, `violin_sul_tasto.py`, `violin_sul_ponticello.py` from Desktop `Violin_mf.xlsx` / `Violin_ff.xlsx` (pp via arco ratio transfer). Violin sul tasto still uses this 2026-08-30 path.
5. `tools/generate_violin_technique_modules_from_ok_workbooks.py` — 2026-08-30 string Dynamics10 generator (`Desktop\\Código extrapolação\\<INSTR>\\Dynamics10`). Superseded for the 2026-09-03 refresh.
6. `tools/generate_full_dynamics_modules_from_xlsx.py` — earlier ordinary-sustain commit helper (`flute`, `clarinet`, `bassoon`, `oboe`, brass). Still imported by the 2026-09-03 commit tool for wind-module rendering.
7. `tools/generate_violin_arco_full_dynamics_from_xlsx.py` — legacy violin arco regenerator (superseded by the Dynamics10 generator).
8. `tools/refresh_regression_fixtures.py` — updates golden regression/snapshot/benchmark fixtures after intentional table changes.

The former cello / double-bass STE technique generators (`generate_cello_technique_modules_from_xlsx.py`, `generate_double_bass_technique_modules_from_xlsx.py`) were retired when those modules were withdrawn (2026-08-18).

**String techniques (2026-09-03):** violin, viola, cello, and double-bass ordinary arco plus sordina / sul ponticello / harmonics rebuilt from dest-Zenodo Dynamics10 `Results` ladders via `tools/commit_dynamics_from_para_dinamicas.py`. Violin arco G3–B7 (53); sordina/ponticello G3–C7 (42); tasto unchanged G3–B7 (53); harmonics G5–B7 (29). Viola arco/sordina C3–A#6 (47); ponticello C3–E6 (41); harmonics C5–A#6 (23). Cello arco C2–C6 (49); sordina/ponticello C2–A5 (46); harmonics C4–C6 (25). Double-bass arco E1–C5 (45); sordina/ponticello E1–G4 (40); harmonics E3–G6 (40). No cello/viola/double-bass sul tasto. Runtime GPR remains removed.

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
| `VIOLINO\VIOLIN_Zenodo_collections_Arco_normal.xlsx` | `Violin_Media` | 49 | **PASS** — 0 value differences vs committed module |
| `VIOLA_Zenodo_collections_Arco_normal.xlsx` | `VIOLA_Media` | 49 | **PASS** |
| `CELLO_Zenodo_collections_media.xlsx` | `Cello_Media` | 49 | **PASS** |
| `DOUBLEBASS_Zenodo_collections_media.xlsx` | `DBass_Media` | 45 | **PASS** |

**CI:** `tests/test_string_source_reproducibility.py` skips when workbooks are absent on the runner (see archiving note above). Local reconstruction status (2026-08-08) is **PASS for all four strings**. CI verifies committed modules and unit tests; independent reconstruction requires local workbooks or future canonical fixtures.

## Technique metadata vs source tables

Registry `supported_techniques` lists organological capabilities. Table-backed modules declare `INSTRUMENT_SOURCE.source_technique` and `table_supported_techniques` for the numerical table actually committed (e.g. `arco_sustain` for strings, `ordinary_sustain` for winds). Pizzicato, tremolo, harmonics, mute, flutter-tongue, etc. are **not** modelled unless separate technique-specific tables exist.

Audit: `tools/audit_instrument_metadata_range_resolution.py` → `reports/instrument_metadata_range_resolution_audit.*`

## Scientific review candidates (pending adjudication)

| ID | Topic | Status |
|----|-------|--------|
| DB-SPAN | Double-bass `source_table_span` E1–C5 aligns with committed table and registry; E1–A3 was obsolete documentation. Upper-register QC (A♯3–C5) open. | **PASS** (span); **REVIEW REQUIRED** (upper QC) |
| TECHNIQUE | `INSTRUMENT_SOURCE.table_supported_techniques` vs registry `supported_techniques`; tables do not overclaim technique coverage. | **PASS** |
| TUBA-RNG | Tuba now ships a committed table (`tuba.py`, C1–A#4); `registry.sounding_range` (MIDI 24–70) matches the table span (2026-08-09). | **PASS** |
| TBN-RNG | Trombone now ships a committed table (`trombone.py`, F1–C5); `registry.sounding_range` (MIDI 29–72) matches the table span (2026-08-24). Bass trombone remains coarse. | **PASS** |
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
