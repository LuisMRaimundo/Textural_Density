#!/usr/bin/env python3
"""Generate string technique instrument modules from OK_* dynamics workbooks.

Sources (D:\\CORDAS\\VIOLINO and D:\\CORDAS\\VIOLA, Dynamics extrapolator
v1.5.2.1 exports, ``Results`` sheet = data-faithful full 10-dynamic ladder;
pp/mf/ff are measured anchors, p/mp/f PCHIP interiors, pppp/ppp/fff/ffff
tapered equal-log outers, r=0.8):

  - OK_VIOLIN_sul_ponticello_dynamics extrapolation.xlsx → violin_sul_ponticello.py
  - OK_VIOLIN_sul_tasto_dynamics extrapolation.xlsx      → violin_sul_tasto.py
  - OK_VIOLIN_con sordina_dynamics extrapolation.xlsx    → violin_sordina.py
  - OK_VIOLIN_harmonics_dynamics extrapolation.xlsx      → violin_harmonics.py
  - OK_VIOLA_harmonics_dynamics extrapolation.xlsx       → viola_harmonics.py
  - OK_VIOLA_Arco ordinario_dynamics extrapolation.xlsx  → viola.py
  - OK_VIOLA_con sordina_dynamics extrapolation.xlsx     → viola_sordina.py
  - OK_VIOLA_sul ponticello_dynamics extrapolation.xlsx  → viola_sul_ponticello.py

Registry display names (GUI): "vl sp", "vl st", "vl sord", "vl harm",
"vla harm", "vla", "vla sord", "vla sp" (registry edits are maintained
directly in ``instrumentos/registry.py``).
"""

from __future__ import annotations

import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.notes import normalize_note_string  # noqa: E402

SRC_DIR = Path(r"d:\CORDAS\VIOLINO")

DYNAMIC_LEVELS = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")

TECHNIQUE_SPECS = {
    "sul_ponticello": {
        "workbook": "OK_VIOLIN_sul_ponticello_dynamics extrapolation.xlsx",
        "module": "violin_sul_ponticello",
        "technique_label": "arco sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "doc_anchor": "violin-sul-ponticello",
        "pitch_range": (55, 103),
    },
    "sul_tasto": {
        "workbook": "OK_VIOLIN_sul_tasto_dynamics extrapolation.xlsx",
        "module": "violin_sul_tasto",
        "technique_label": "arco sul tasto",
        "source_technique": "arco_sul_tasto",
        "doc_anchor": "violin-sul-tasto",
        "pitch_range": (55, 103),
    },
    "con_sordina": {
        "workbook": "OK_VIOLIN_con sordina_dynamics extrapolation.xlsx",
        "module": "violin_sordina",
        "technique_label": "arco con sordina",
        "source_technique": "arco_sordina",
        "doc_anchor": "violin-sordina",
        "pitch_range": (55, 103),
    },
    "harmonics": {
        "workbook": "OK_VIOLIN_harmonics_dynamics extrapolation.xlsx",
        "module": "violin_harmonics",
        "technique_label": "arco harmonics",
        "source_technique": "arco_harmonic",
        "doc_anchor": "violin-harmonics",
        "pitch_range": (67, 103),
    },
    "viola_harmonics": {
        "workbook": "OK_VIOLA_harmonics_dynamics extrapolation.xlsx",
        "src_dir": r"d:\CORDAS\VIOLA",
        "instrument_label": "Viola",
        "module": "viola_harmonics",
        "technique_label": "arco harmonics",
        "source_technique": "arco_harmonic",
        "doc_anchor": "viola-harmonics",
        "pitch_range": (60, 107),
    },
    "viola_ordinario": {
        "workbook": "OK_VIOLA_Arco ordinario_dynamics extrapolation.xlsx",
        "src_dir": r"d:\CORDAS\VIOLA",
        "instrument_label": "Viola",
        "module": "viola",
        "technique_label": "arco ordinario",
        "source_technique": "arco_sustain",
        "doc_anchor": "viola",
        "pitch_range": (48, 96),
        # Base arco table: anchors are direct IOWA+ORCH medians (not a
        # technique-extrapolated METApool), hence medium uncertainty.
        "uncertainty": "medium",
        "citation_pool": "IOWA+ORCHIDEA Zenodo collections, Philharmonia removed",
    },
    "viola_con_sordina": {
        "workbook": "OK_VIOLA_con sordina_dynamics extrapolation.xlsx",
        "src_dir": r"d:\CORDAS\VIOLA",
        "instrument_label": "Viola",
        "module": "viola_sordina",
        "technique_label": "arco con sordina",
        "source_technique": "arco_sordina",
        "doc_anchor": "viola-sordina",
        "pitch_range": (48, 96),
        # 2026-08-11: workbook mf anchors duplicate the viola harmonics pool
        # (37/37 shared notes) and 22/49 ladders are inverted (ff < mf);
        # regeneration is on hold until the source data is verified.
        "on_hold": True,
    },
    "viola_sul_ponticello": {
        "workbook": "OK_VIOLA_sul ponticello_dynamics extrapolation.xlsx",
        "src_dir": r"d:\CORDAS\VIOLA",
        "instrument_label": "Viola",
        "module": "viola_sul_ponticello",
        "technique_label": "arco sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "doc_anchor": "viola-sul-ponticello",
        "pitch_range": (48, 96),
    },
}

VERSION = "2026-08-11"


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
        note = normalize_note_string(raw_note)
        row = {dyn: float(v) for dyn, v in values.items()}
        _clamp_interiors(note, row)
        ladder[note] = {dyn: round(v, 6) for dyn, v in row.items()}
    return ladder


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
    version = VERSION
    lo, hi = spec["pitch_range"]
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


def main() -> int:
    for technique, spec in TECHNIQUE_SPECS.items():
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
