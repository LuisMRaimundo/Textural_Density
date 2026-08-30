#!/usr/bin/env python3
"""Generate string instrument modules from Dynamics10 Results workbooks.

Reads dest-Zenodo Dynamics_predicter exports under
``Desktop\\Código extrapolação\\<INSTRUMENT>\\Dynamics10``
(``Results`` sheet = data-faithful 10-dynamic ladder; Media pp/mf/ff anchors,
PCHIP interiors, tapered equal-log outers r=0.8). Note labels such as
``F4 (2)`` are collapsed via ``normalize_media_note_label``.

No cello / viola / double-bass sul tasto workbook. GUI names remain
``vl_sul_pont``, ``vl_sul_tast``, ``vl_con_sord``, ``vl_harm``, ``vla``,
``vla sord``, ``vla sp``, ``vla harm``, ``vlc_sord``, ``vlc_sp``,
``vlc_harm``, ``cb_sord``, ``cb_sp``, ``cb_harm``.

    python tools/generate_violin_technique_modules_from_ok_workbooks.py
    python tools/generate_violin_technique_modules_from_ok_workbooks.py --violin-only
"""

from __future__ import annotations

import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from microtonal import note_to_midi_strict  # noqa: E402
from utils.notes import normalize_media_note_label  # noqa: E402

DESK = Path(r"C:\Users\lmr20\Desktop\Código extrapolação")
VIOLIN_SRC_DIR = DESK / "VIOLIN_3" / "Dynamics10"
VIOLA_SRC_DIR = DESK / "VIOLA" / "Dynamics10"
CELLO_SRC_DIR = DESK / "CELLO" / "Dynamics10"
DBASS_SRC_DIR = DESK / "DOUBLE_BASS" / "Dynamics10"
SRC_DIR = VIOLIN_SRC_DIR

DYNAMIC_LEVELS = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")
VIOLIN_KEYS = ("violin_ordinario", "sul_ponticello", "sul_tasto", "con_sordina", "harmonics")
VIOLA_KEYS = ("viola_ordinario", "viola_con_sordina", "viola_sul_ponticello", "viola_harmonics")
CELLO_KEYS = ("cello_ordinario", "cello_con_sordina", "cello_sul_ponticello", "cello_harmonics")
DBASS_KEYS = ("dbass_ordinario", "dbass_con_sordina", "dbass_sul_ponticello", "dbass_harmonics")

TECHNIQUE_SPECS = {
    "violin_ordinario": {
        "workbook": "Violin_Dynamics10_Arco_normal.xlsx",
        "src_dir": str(VIOLIN_SRC_DIR),
        "instrument_label": "Violin",
        "module": "violin",
        "technique_label": "arco ordinario",
        "source_technique": "arco_sustain",
        "doc_anchor": "violin",
        "uncertainty": "medium",
        "citation_pool": (
            "Dynamics10 dest-Zenodo Violin_Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "sul_ponticello": {
        "workbook": "Violin_Dynamics10_sul_ponticello.xlsx",
        "src_dir": str(VIOLIN_SRC_DIR),
        "module": "violin_sul_ponticello",
        "technique_label": "arco sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "doc_anchor": "violin-sul-ponticello",
        "pitch_range": (55, 107),
        "citation_pool": (
            "dest Zenodo Violin_sul ponticello Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "sul_tasto": {
        "workbook": "Violin_Dynamics10_sul_tasto.xlsx",
        "src_dir": str(VIOLIN_SRC_DIR),
        "module": "violin_sul_tasto",
        "technique_label": "arco sul tasto",
        "source_technique": "arco_sul_tasto",
        "doc_anchor": "violin-sul-tasto",
        "pitch_range": (55, 103),
        "citation_pool": (
            "dest Zenodo Violin_sul tasto Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "con_sordina": {
        "workbook": "Violin_Dynamics10_con_sordino.xlsx",
        "src_dir": str(VIOLIN_SRC_DIR),
        "module": "violin_sordina",
        "technique_label": "arco con sordino",
        "source_technique": "arco_sordina",
        "doc_anchor": "violin-sordina",
        "pitch_range": (55, 103),
        "citation_pool": (
            "dest Zenodo Violin_con sordino Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "harmonics": {
        "workbook": "Violin_Dynamics10_harmonics.xlsx",
        "src_dir": str(VIOLIN_SRC_DIR),
        "module": "violin_harmonics",
        "technique_label": "arco harmonics",
        "source_technique": "arco_harmonic",
        "doc_anchor": "violin-harmonics",
        "pitch_range": (72, 107),
        "citation_pool": (
            "dest Zenodo Violin_harmonics Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "viola_harmonics": {
        "workbook": "Viola_Dynamics10_harmonics.xlsx",
        "src_dir": str(VIOLA_SRC_DIR),
        "instrument_label": "Viola",
        "module": "viola_harmonics",
        "technique_label": "arco harmonics",
        "source_technique": "arco_harmonic",
        "doc_anchor": "viola-harmonics",
        # dest-Zenodo Media harmonics start at C5; C#7–B7 are real measured rows.
        "pitch_range": (72, 107),
        "citation_pool": (
            "dest Zenodo Viola_harmonics Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "viola_ordinario": {
        "workbook": "Viola_Dynamics10_Arco_normal.xlsx",
        "src_dir": str(VIOLA_SRC_DIR),
        "instrument_label": "Viola",
        "module": "viola",
        "technique_label": "arco ordinario",
        "source_technique": "arco_sustain",
        "doc_anchor": "viola",
        "pitch_range": (48, 96),
        # Base arco table: dest-Zenodo Media anchors (IOWA+ORCH average).
        "uncertainty": "medium",
        "citation_pool": (
            "dest Zenodo VIOLA_Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "viola_con_sordina": {
        "workbook": "Viola_Dynamics10_con_sordino.xlsx",
        "src_dir": str(VIOLA_SRC_DIR),
        "instrument_label": "Viola",
        "module": "viola_sordina",
        "technique_label": "arco con sordino",
        "source_technique": "arco_sordina",
        "doc_anchor": "viola-sordina",
        "pitch_range": (48, 94),
        "citation_pool": (
            "dest Zenodo Viola_con sordino Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "viola_sul_ponticello": {
        "workbook": "Viola_Dynamics10_sul_ponticello.xlsx",
        "src_dir": str(VIOLA_SRC_DIR),
        "instrument_label": "Viola",
        "module": "viola_sul_ponticello",
        "technique_label": "arco sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "doc_anchor": "viola-sul-ponticello",
        "pitch_range": (48, 94),
        "citation_pool": (
            "dest Zenodo Viola_sul ponticello Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "cello_ordinario": {
        "workbook": "Cello_Dynamics10_Arco_normal.xlsx",
        "src_dir": str(CELLO_SRC_DIR),
        "instrument_label": "Cello",
        "module": "cello",
        "technique_label": "arco ordinario",
        "source_technique": "arco_sustain",
        "doc_anchor": "cello",
        "uncertainty": "medium",
        "citation_pool": (
            "Dynamics10 dest-Zenodo Cello_Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "cello_con_sordina": {
        "workbook": "Cello_Dynamics10_con_sordino.xlsx",
        "src_dir": str(CELLO_SRC_DIR),
        "instrument_label": "Cello",
        "module": "cello_sordina",
        "technique_label": "arco con sordino",
        "source_technique": "arco_sordina",
        "doc_anchor": "cello-sordina",
        "pitch_range": (36, 81),
        "version": "2026-08-27",
        "citation_pool": (
            "dest Zenodo Cello_con sordino Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "cello_sul_ponticello": {
        "workbook": "Cello_Dynamics10_sul_ponticello.xlsx",
        "src_dir": str(CELLO_SRC_DIR),
        "instrument_label": "Cello",
        "module": "cello_sul_ponticello",
        "technique_label": "arco sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "doc_anchor": "cello-sul-ponticello",
        "pitch_range": (36, 84),
        "version": "2026-08-27",
        "citation_pool": (
            "dest Zenodo Cello_sul ponticello Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "cello_harmonics": {
        "workbook": "Cello_Dynamics10_harmonics.xlsx",
        "src_dir": str(CELLO_SRC_DIR),
        "instrument_label": "Cello",
        "module": "cello_harmonics",
        "technique_label": "arco harmonics",
        "source_technique": "arco_harmonic",
        "doc_anchor": "cello-harmonics",
        "pitch_range": (60, 100),
        "version": "2026-08-27",
        "citation_pool": (
            "dest Zenodo Cello_harmonics Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "dbass_ordinario": {
        "workbook": "DoubleBass_Dynamics10_Arco_normal.xlsx",
        "src_dir": str(DBASS_SRC_DIR),
        "instrument_label": "Double bass",
        "module": "double_bass",
        "technique_label": "arco ordinario",
        "source_technique": "arco_sustain",
        "doc_anchor": "double-bass-double_bass",
        "uncertainty": "medium",
        "citation_pool": (
            "Dynamics10 dest-Zenodo DBass_Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "dbass_con_sordina": {
        "workbook": "DoubleBass_Dynamics10_con_sordino.xlsx",
        "src_dir": str(DBASS_SRC_DIR),
        "instrument_label": "Double bass",
        "module": "double_bass_sordina",
        "technique_label": "arco con sordino",
        "source_technique": "arco_sordina",
        "doc_anchor": "double-bass-sordina",
        "pitch_range": (29, 67),
        "version": "2026-08-27",
        "citation_pool": (
            "dest Zenodo DoubleBass_con sordino Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "dbass_sul_ponticello": {
        "workbook": "DoubleBass_Dynamics10_sul_ponticello.xlsx",
        "src_dir": str(DBASS_SRC_DIR),
        "instrument_label": "Double bass",
        "module": "double_bass_sul_ponticello",
        "technique_label": "arco sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "doc_anchor": "double-bass-sul-ponticello",
        "pitch_range": (28, 67),
        "version": "2026-08-27",
        "citation_pool": (
            "dest Zenodo DoubleBass_sul ponticello Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
    "dbass_harmonics": {
        "workbook": "DoubleBass_Dynamics10_harmonics.xlsx",
        "src_dir": str(DBASS_SRC_DIR),
        "instrument_label": "Double bass",
        "module": "double_bass_harmonics",
        "technique_label": "arco harmonics",
        "source_technique": "arco_harmonic",
        "doc_anchor": "double-bass-harmonics",
        "pitch_range": (28, 67),
        "version": "2026-08-27",
        "citation_pool": (
            "dest Zenodo DoubleBass_harmonics Media (IOWA+Orchidea average); "
            "Dynamics_predicter Results ladder"
        ),
    },
}

VERSION = "2026-08-30"


def load_results_ladder(path: Path) -> dict[str, dict[str, float]]:
    """Read the Results sheet into {note: {dynamic: value}} with sharp spellings."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb["Results"]
        rows = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()
    header = list(rows[0])
    col = {name: header.index(name) for name in ("note", *DYNAMIC_LEVELS)}
    ladder: dict[str, dict[str, float]] = {}
    for row in rows[1:]:
        raw_note = row[col["note"]]
        if not isinstance(raw_note, str) or not raw_note.strip():
            continue  # trailing annotation rows
        values = {dyn: row[col[dyn]] for dyn in DYNAMIC_LEVELS}
        if any(not isinstance(v, (int, float)) for v in values.values()):
            continue
        note = normalize_media_note_label(raw_note)
        row = {dyn: float(v) for dyn, v in values.items()}
        _clamp_interiors(note, row)
        ladder[note] = {dyn: round(v, 6) for dyn, v in row.items()}
    return dict(sorted(ladder.items(), key=lambda item: note_to_midi_strict(item[0])))


def _clamp_interiors(note: str, row: dict[str, float]) -> None:
    """Clamp interior dynamics into their measured segment (hygiene contract).

    Rare workbook artifacts leave an interior cell marginally outside the
    [pp, mf] / [mf, ff] measured segment (e.g. con sordina G7 mp 0.4% above
    mf); anchors themselves are never modified.
    """
    for dyns, a, b in ((("p", "mp"), "pp", "mf"), (("f",), "mf", "ff")):
        lo, hi = min(row[a], row[b]), max(row[a], row[b])
        for dyn in dyns:
            clamped = min(max(row[dyn], lo), hi)
            if clamped != row[dyn]:
                print(f"  clamp {note} {dyn}: {row[dyn]} -> {clamped}")
                row[dyn] = clamped


def _fmt_spectral(ladder: dict[str, dict[str, float]]) -> str:
    lines = ["{"]
    for note, row in ladder.items():
        cells = ", ".join(f"'{dyn}': {row[dyn]}" for dyn in DYNAMIC_LEVELS)
        lines.append(f"    '{note}': {{{cells}}},")
    lines.append("}")
    return "\n".join(lines)


def render_module(spec: dict, ladder: dict[str, dict[str, float]]) -> str:
    module = spec["module"]
    instrument_label = spec.get("instrument_label", "Violin")
    uncertainty = spec.get("uncertainty", "high")
    citation_pool = spec.get(
        "citation_pool", "CDM Technique Extrapolator METApool, IOWA+ORCHIDEA collections"
    )
    technique_label = spec["technique_label"]
    source_technique = spec["source_technique"]
    doc_anchor = spec["doc_anchor"]
    workbook = spec["workbook"]
    version = spec.get("version", VERSION)
    midis = [int(note_to_midi_strict(n)) for n in ladder]
    lo, hi = min(midis), max(midis)
    spectral_block = _fmt_spectral(ladder)
    return f'''# instrumentos/{module}.py
"""
{instrument_label} ({technique_label}) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``{workbook}``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "{instrument_label} {source_technique} CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "{workbook} "
        "({citation_pool})."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#{doc_anchor}',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels={DYNAMIC_LEVELS!r},
    pitch_range=({lo}, {hi}),
    uncertainty="{uncertainty}",
    version="{version}",
    source_technique="{source_technique}",
    table_supported_techniques=("{source_technique}",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("{module}")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {spectral_block}


def calcular_densidade(nota, dinamica):
    """Compute density from spectral CDM table (MIDI-space lookup, octave-safe)."""
    from instrumentos.spectral_lookup import lookup_spectral_density

    return lookup_spectral_density(
        spectral_data,
        nota,
        dinamica,
        logger=logger,
        preprocess=normalize_note_string,
    )
'''


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    specs = TECHNIQUE_SPECS
    if "--violin-only" in argv:
        specs = {k: TECHNIQUE_SPECS[k] for k in VIOLIN_KEYS}
    elif "--viola-only" in argv:
        specs = {k: TECHNIQUE_SPECS[k] for k in VIOLA_KEYS}
    elif "--cello-only" in argv:
        specs = {k: TECHNIQUE_SPECS[k] for k in CELLO_KEYS}
    elif "--dbass-only" in argv:
        specs = {k: TECHNIQUE_SPECS[k] for k in DBASS_KEYS}
    for technique, spec in specs.items():
        if spec.get("on_hold"):
            print(f"SKIP {technique}: on hold pending source-data verification", file=sys.stderr)
            continue
        src = Path(spec.get("src_dir", SRC_DIR)) / spec["workbook"]
        if not src.exists():
            print(f"SKIP {technique}: missing {src}", file=sys.stderr)
            continue
        ladder = load_results_ladder(src)
        if not ladder:
            print(f"SKIP {technique}: no numeric rows in {src}", file=sys.stderr)
            continue
        midis = [int(note_to_midi_strict(n)) for n in ladder]
        spec = {**spec, "pitch_range": (min(midis), max(midis))}
        code = render_module(spec, ladder)
        out = ROOT / "instrumentos" / f"{spec['module']}.py"
        out.write_text(code, encoding="utf-8")
        print(
            f"wrote {out.relative_to(ROOT)}  notes={len(ladder)}  "
            f"span={next(iter(ladder))}..{next(reversed(ladder))}  technique={technique}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
