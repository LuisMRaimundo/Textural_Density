#!/usr/bin/env python3
"""Generate / replace violin technique instrument modules from Desktop Excel workbooks.

Sources (assumption-based EWSD extrapolations from Strings_techniques_extrapolation):
  - c:\\Users\\lmr20\\Desktop\\Violin_mf.xlsx
  - c:\\Users\\lmr20\\Desktop\\Violin_ff.xlsx

Numeric techniques written:
  - con_sordino  → instrumentos/violin_sordina.py          (replace)
  - sul_tasto    → instrumentos/violin_sul_tasto.py        (create/replace)
  - sul_ponticello → instrumentos/violin_sul_ponticello.py (replace)

Harmonics are handled separately by
``tools/generate_violin_harmonic_modules_from_xlsx.py`` (Violin_*_harmo workbooks).

pp anchors are derived from violin arco pp/mf ratios applied to the mf column;
mf and ff come from the Excel estimate_mean columns.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_MF = Path(r"c:\Users\lmr20\Desktop\Violin_mf.xlsx")
SRC_FF = Path(r"c:\Users\lmr20\Desktop\Violin_ff.xlsx")

TECHNIQUE_SPECS = {
    "con_sordino": {
        "module": "violin_sordina",
        "display": "Violin sordina",
        "source_technique": "arco_sordina",
        "logger": "violin_sordina",
        "doc_anchor": "violin-sordina",
        "pitch_range": (55, 103),
    },
    "sul_tasto": {
        "module": "violin_sul_tasto",
        "display": "Violin sul tasto",
        "source_technique": "arco_sul_tasto",
        "logger": "violin_sul_tasto",
        "doc_anchor": "violin-sul-tasto",
        "pitch_range": (55, 103),
    },
    "sul_ponticello": {
        "module": "violin_sul_ponticello",
        "display": "Violin sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "logger": "violin_sul_ponticello",
        "doc_anchor": "violin-sul-ponticello",
        "pitch_range": (55, 103),
    },
}

NOTE_ORDER = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]


def _note_sort_key(note: str) -> tuple[int, int]:
    m = re.fullmatch(r"([A-G]#?)(-?\d+)", str(note).strip())
    if not m:
        return (99, 0)
    pc, octv = m.group(1), int(m.group(2))
    return (octv, NOTE_ORDER.index(pc) if pc in NOTE_ORDER else 99)


def _load_technique_column(path: Path, technique: str) -> dict[str, float]:
    df = pd.read_excel(path, sheet_name="All_Results")
    sub = df[df["technique"].astype(str) == technique].copy()
    sub["estimate_mean"] = pd.to_numeric(sub["estimate_mean"], errors="coerce")
    sub = sub[sub["estimate_mean"].notna()]
    out: dict[str, float] = {}
    for _, row in sub.iterrows():
        note = str(row["pitch"]).strip()
        out[note] = float(row["estimate_mean"])
    return out


def _median_pp_ratio(reference_table: dict) -> float:
    ratios = []
    for row in reference_table.values():
        mf = float(row["mf"])
        if mf:
            ratios.append(float(row["pp"]) / mf)
    ratios.sort()
    if not ratios:
        return 1.0
    mid = len(ratios) // 2
    if len(ratios) % 2:
        return ratios[mid]
    return (ratios[mid - 1] + ratios[mid]) / 2.0


def build_spectral_data(
    mf_map: dict[str, float],
    ff_map: dict[str, float],
    *,
    reference_module_name: str = "violin",
) -> tuple[dict[str, float], dict[str, float], dict[str, dict[str, float]]]:
    sys.path.insert(0, str(ROOT))
    reference = importlib.import_module(f"instrumentos.{reference_module_name}")
    reference_table = reference.spectral_data
    fallback_pp = _median_pp_ratio(reference_table)

    notes = sorted(set(mf_map) & set(ff_map), key=_note_sort_key)
    mf_measured: dict[str, float] = {}
    ff_measured: dict[str, float] = {}
    spectral: dict[str, dict[str, float]] = {}
    for note in notes:
        mf = round(float(mf_map[note]), 6)
        ff = round(float(ff_map[note]), 6)
        ref = reference_table.get(note)
        if ref and ref.get("mf"):
            pp = round(mf * float(ref["pp"]) / float(ref["mf"]), 6)
        else:
            pp = round(mf * fallback_pp, 6)
        mf_measured[note] = mf
        ff_measured[note] = ff
        spectral[note] = {"pp": pp, "mf": mf, "ff": ff}
    return mf_measured, ff_measured, spectral


def _fmt_dict(d: dict[str, float], indent: str = "    ") -> str:
    lines = ["{"]
    for k, v in d.items():
        lines.append(f"{indent}'{k}': {v},")
    lines.append("}")
    return "\n".join(lines)


def _fmt_spectral(spectral: dict[str, dict[str, float]], indent: str = "    ") -> str:
    lines = ["{"]
    for note, row in spectral.items():
        lines.append(
            f"{indent}'{note}': {{'pp': {row['pp']}, 'mf': {row['mf']}, 'ff': {row['ff']}}},"
        )
    lines.append("}")
    return "\n".join(lines)


def render_module(
    *,
    technique: str,
    spec: dict,
    mf_measured: dict[str, float],
    ff_measured: dict[str, float],
    spectral: dict[str, dict[str, float]],
) -> str:
    module = spec["module"]
    source_technique = spec["source_technique"]
    logger_name = spec["logger"]
    doc_anchor = spec["doc_anchor"]
    lo, hi = spec["pitch_range"]
    n = len(spectral)
    first = next(iter(spectral))
    last = next(reversed(spectral))
    technique_label = source_technique.replace("_", " ")
    mf_block = _fmt_dict(mf_measured)
    ff_block = _fmt_dict(ff_measured)
    spectral_block = _fmt_spectral(spectral)
    return f'''# instrumentos/{module}.py
"""
Violin ({technique_label}) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Violin_mf.xlsx`` / ``Violin_ff.xlsx``),
   column ``estimate_mean`` / ``All_Results``.
2. **Derived pp anchor:** per-note violin arco pp/mf ratio applied to the mf
   workbook value (``instrumentos.mf_anchor_dynamic_extrapolation`` style).
3. **GPR-modelled dynamics:** intermediate / extreme markings predicted by GPR
   on the pp/mf/ff triple.

These workbook values are **assumption-based extrapolations**
(``value_kind=assumption_based_extrapolation``), not Zenodo-measured CDM rows.
Uncertainty is therefore high.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin {technique} EWSD table from Strings_techniques_extrapolation "
        "workbooks Violin_mf.xlsx / Violin_ff.xlsx (assumption-based extrapolation); "
        "pp derived from violin arco pp/mf ratios."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#{doc_anchor}",
    extraction_method=(
        "estimate_mean from All_Results for dynamics mf and ff; "
        "pp via violin arco pp/mf ratio transfer; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=({lo}, {hi}),
    uncertainty="high",
    version="2026-07-24",
    source_technique="{source_technique}",
    table_supported_techniques=("{source_technique}",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("{logger_name}")

# Workbook mf / ff anchors ({n} chromatic rows, {first}–{last}).
MF_MEASURED: dict[str, float] = {mf_block}

FF_MEASURED: dict[str, float] = {ff_block}

# GPR anchors: mf/ff from Excel; pp extrapolated from violin arco dynamic ratios.
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


def predict_intermediate_dynamics(pitches, pp_values, mf_values, ff_values):
    """Predict intermediate dynamics using Gaussian Process Regression."""
    from instrumentos.gpr_dynamic_interpolation import predict_intermediate_dynamics_gpr

    return predict_intermediate_dynamics_gpr(pp_values, mf_values, ff_values, logger=logger)
'''


def ensure_sul_tasto_registry() -> None:
    registry_path = ROOT / "instrumentos" / "registry.py"
    text = registry_path.read_text(encoding="utf-8")
    if 'REGISTRY["violino_sul_tasto"]' in text:
        print("registry: violino_sul_tasto already present")
        return

    block = '''
REGISTRY["violino_sul_tasto"] = _profile(
    "violino_sul_tasto",
    "Violin sul tasto",
    "strings",
    sounding=(55, 103),
    comfortable=(55, 76),
    brightness="dark",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="violin_sul_tasto",
    supported=("arco", "sul_tasto"),
    unsupported=("pizzicato", "mute", "sul_ponticello"),
    source_notes=(
        "Sparse GPR table in instrumentos/violin_sul_tasto.py from Strings Techniques "
        "Extrapolation Violin_mf.xlsx / Violin_ff.xlsx (assumption-based EWSD); "
        "pp derived from violin arco per-note dynamic ratios."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_tasto only; mf/ff come from assumption-based "
        "extrapolation workbooks; pp anchors are extrapolated from mf using violin arco ratios.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "violin_sul_tasto",
        "Violin_sul_tasto",
        "violin sul tasto",
        "violino sul tasto",
        "violino_sul_tasto",
        "sul tasto violin",
        "sul_tasto_violin",
    ),
)

'''
    # Insert before art harm or after sul ponticello
    marker = 'REGISTRY["violino_art_harm"]'
    if marker not in text:
        raise RuntimeError("Could not locate violino_art_harm registry entry for insertion")
    text = text.replace(marker, block + marker, 1)

    # Refresh provenance notes on sordina / sul ponticello
    text = text.replace(
        "Sparse GPR table in instrumentos/violin_sordina.py from IOWA+ORCH arco sordina "
        "Combined Density Metric combined_sord_collection_raw (pp/mf/ff); not a full measured spectrum.",
        "Sparse GPR table in instrumentos/violin_sordina.py from Strings Techniques "
        "Extrapolation Violin_mf.xlsx / Violin_ff.xlsx (assumption-based EWSD); "
        "pp derived from violin arco per-note dynamic ratios.",
    )
    text = text.replace(
        "Sparse GPR table in instrumentos/violin_sul_ponticello.py with measured mf CDM "
        "anchor only; pp/ff extrapolated from violin arco per-note dynamic ratios.",
        "Sparse GPR table in instrumentos/violin_sul_ponticello.py from Strings Techniques "
        "Extrapolation Violin_mf.xlsx / Violin_ff.xlsx (assumption-based EWSD); "
        "pp derived from violin arco per-note dynamic ratios.",
    )
    text = text.replace(
        '"Numerical CDM table covers arco_sul_ponticello only; pp/ff anchors are "\n'
        '        "extrapolated from mf using violin arco dynamic ratios.",',
        '"Numerical CDM table covers arco_sul_ponticello only; mf/ff come from assumption-based "\n'
        '        "extrapolation workbooks; pp anchors are extrapolated from mf using violin arco ratios.",',
    )
    # Raise uncertainty for sordina after replacing measured table
    text = re.sub(
        r'(REGISTRY\["violino_sordina"\] = _profile\(\n'
        r'(?:.*\n)*?'
        r'    uncertainty=)"medium"',
        r'\1"high"',
        text,
        count=1,
    )
    registry_path.write_text(text, encoding="utf-8")
    print("registry: inserted violino_sul_tasto and refreshed sordina/sul ponticello notes")


def main() -> int:
    if not SRC_MF.exists() or not SRC_FF.exists():
        print("Missing Violin_mf.xlsx or Violin_ff.xlsx on Desktop", file=sys.stderr)
        return 1

    for technique, spec in TECHNIQUE_SPECS.items():
        mf_map = _load_technique_column(SRC_MF, technique)
        ff_map = _load_technique_column(SRC_FF, technique)
        if not mf_map or not ff_map:
            print(f"SKIP {technique}: no numeric rows")
            continue
        mf_m, ff_m, spectral = build_spectral_data(mf_map, ff_map)
        code = render_module(
            technique=technique,
            spec=spec,
            mf_measured=mf_m,
            ff_measured=ff_m,
            spectral=spectral,
        )
        out = ROOT / "instrumentos" / f"{spec['module']}.py"
        out.write_text(code, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}  notes={len(spectral)}  technique={technique}")

    ensure_sul_tasto_registry()
    print(
        "NOTE: harmonics → tools/generate_violin_harmonic_modules_from_xlsx.py"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
