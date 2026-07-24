#!/usr/bin/env python3
"""Generate double bass technique instrument modules from Desktop Excel workbooks.

Sources (assumption-based EWSD extrapolations from Strings_techniques_extrapolation):
  - c:\\Users\\lmr20\\Desktop\\Contrabass-pp.xlsx   (hyphen in filename)
  - c:\\Users\\lmr20\\Desktop\\Contrabass_mf.xlsx
  - c:\\Users\\lmr20\\Desktop\\Contrabass_ff.xlsx

Numeric techniques written:
  - con_sordino    → instrumentos/double_bass_sordina.py
  - sul_tasto      → instrumentos/double_bass_sul_tasto.py
  - sul_ponticello → instrumentos/double_bass_sul_ponticello.py

Harmonics are skipped: artificial/natural harmonic cells are unavailable
(no_harmonic_acoustic_calibration_data). No double_bass_art_harm module is created.

All three dynamics (pp/mf/ff) are taken directly from workbook ``estimate_mean``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_PP = Path(r"c:\Users\lmr20\Desktop\Contrabass-pp.xlsx")
SRC_MF = Path(r"c:\Users\lmr20\Desktop\Contrabass_mf.xlsx")
SRC_FF = Path(r"c:\Users\lmr20\Desktop\Contrabass_ff.xlsx")

TECHNIQUE_SPECS = {
    "con_sordino": {
        "module": "double_bass_sordina",
        "registry_id": "contrabaixo_sordina",
        "display": "Double bass sordina",
        "source_technique": "arco_sordina",
        "logger": "double_bass_sordina",
        "doc_anchor": "double-bass-sordina",
        "pitch_range": (28, 72),
        "comfortable": (31, 55),
        "brightness": "neutral",
        "attack": "soft",
        "supported": ("arco", "mute"),
        "unsupported": ("pizzicato", "sul_ponticello", "sul_tasto"),
        "aliases": (
            "double_bass_sordina",
            "Double_bass_sordina",
            "double bass sordina",
            "contrabass sordina",
            "contrabass_sordina",
            "contrabaixo sordina",
            "contrabaixo_sordina",
            "bass sordina",
            "muted double bass",
            "muted contrabass",
        ),
    },
    "sul_tasto": {
        "module": "double_bass_sul_tasto",
        "registry_id": "contrabaixo_sul_tasto",
        "display": "Double bass sul tasto",
        "source_technique": "arco_sul_tasto",
        "logger": "double_bass_sul_tasto",
        "doc_anchor": "double-bass-sul-tasto",
        "pitch_range": (28, 72),
        "comfortable": (31, 55),
        "brightness": "dark",
        "attack": "soft",
        "supported": ("arco", "sul_tasto"),
        "unsupported": ("pizzicato", "mute", "sul_ponticello"),
        "aliases": (
            "double_bass_sul_tasto",
            "Double_bass_sul_tasto",
            "double bass sul tasto",
            "contrabass sul tasto",
            "contrabass_sul_tasto",
            "contrabaixo sul tasto",
            "contrabaixo_sul_tasto",
            "sul tasto double bass",
            "sul_tasto_double_bass",
        ),
    },
    "sul_ponticello": {
        "module": "double_bass_sul_ponticello",
        "registry_id": "contrabaixo_sul_ponticello",
        "display": "Double bass sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "logger": "double_bass_sul_ponticello",
        "doc_anchor": "double-bass-sul-ponticello",
        "pitch_range": (28, 72),
        "comfortable": (31, 55),
        "brightness": "bright",
        "attack": "hard",
        "supported": ("arco", "sul_ponticello"),
        "unsupported": ("pizzicato", "mute", "sul_tasto"),
        "aliases": (
            "double_bass_sul_ponticello",
            "Double_bass_sul_ponticello",
            "double bass sul ponticello",
            "contrabass sul ponticello",
            "contrabass_sul_ponticello",
            "contrabaixo sul ponticello",
            "contrabaixo_sul_ponticello",
            "sul ponticello double bass",
            "sul_ponticello_double_bass",
        ),
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


def build_spectral_data(
    pp_map: dict[str, float],
    mf_map: dict[str, float],
    ff_map: dict[str, float],
) -> tuple[dict[str, float], dict[str, float], dict[str, float], dict[str, dict[str, float]]]:
    notes = sorted(set(pp_map) & set(mf_map) & set(ff_map), key=_note_sort_key)
    pp_measured: dict[str, float] = {}
    mf_measured: dict[str, float] = {}
    ff_measured: dict[str, float] = {}
    spectral: dict[str, dict[str, float]] = {}
    for note in notes:
        pp = round(float(pp_map[note]), 6)
        mf = round(float(mf_map[note]), 6)
        ff = round(float(ff_map[note]), 6)
        pp_measured[note] = pp
        mf_measured[note] = mf
        ff_measured[note] = ff
        spectral[note] = {"pp": pp, "mf": mf, "ff": ff}
    return pp_measured, mf_measured, ff_measured, spectral


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
    pp_measured: dict[str, float],
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
    pp_block = _fmt_dict(pp_measured)
    mf_block = _fmt_dict(mf_measured)
    ff_block = _fmt_dict(ff_measured)
    spectral_block = _fmt_spectral(spectral)
    return f'''# instrumentos/{module}.py
"""
Double bass ({technique_label}) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``pp``, ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Contrabass-pp.xlsx`` / ``Contrabass_mf.xlsx`` /
   ``Contrabass_ff.xlsx``), column ``estimate_mean`` / ``All_Results``.
2. **GPR-modelled dynamics:** intermediate / extreme markings predicted by GPR
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
        "Double bass {technique} EWSD table from Strings_techniques_extrapolation "
        "workbooks Contrabass-pp.xlsx / Contrabass_mf.xlsx / Contrabass_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#{doc_anchor}",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
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

# Workbook pp / mf / ff anchors ({n} chromatic rows, {first}–{last}).
PP_MEASURED: dict[str, float] = {pp_block}

MF_MEASURED: dict[str, float] = {mf_block}

FF_MEASURED: dict[str, float] = {ff_block}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
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


def _fmt_tuple(items: tuple[str, ...]) -> str:
    return "(" + ", ".join(f'"{x}"' for x in items) + ")"


def ensure_registry() -> None:
    registry_path = ROOT / "instrumentos" / "registry.py"
    text = registry_path.read_text(encoding="utf-8")

    blocks: list[str] = []
    for technique, spec in TECHNIQUE_SPECS.items():
        rid = spec["registry_id"]
        if f'REGISTRY["{rid}"]' in text:
            print(f"registry: {rid} already present")
            continue
        module = spec["module"]
        lo, hi = spec["pitch_range"]
        clo, chi = spec["comfortable"]
        blocks.append(
            f'''
REGISTRY["{rid}"] = _profile(
    "{rid}",
    "{spec["display"]}",
    "strings",
    sounding=({lo}, {hi}),
    comfortable=({clo}, {chi}),
    brightness="{spec["brightness"]}",
    sustain="sustained",
    attack="{spec["attack"]}",
    status="literature_derived",
    uncertainty="high",
    module_name="{module}",
    supported={_fmt_tuple(spec["supported"])},
    unsupported={_fmt_tuple(spec["unsupported"])},
    source_notes=(
        "Sparse GPR table in instrumentos/{module}.py from Strings Techniques "
        "Extrapolation Contrabass-pp.xlsx / Contrabass_mf.xlsx / Contrabass_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers {spec["source_technique"]} only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases={_fmt_tuple(spec["aliases"])},
)
'''
        )

    if not blocks:
        return

    insert = "\n".join(blocks) + "\n"
    marker = "# --- Brass ---"
    if marker not in text:
        raise RuntimeError("Could not locate Brass section insertion point in registry.py")
    text = text.replace(marker, insert + marker, 1)
    registry_path.write_text(text, encoding="utf-8")
    print("registry: inserted double bass technique profiles")


def main() -> int:
    missing = [p for p in (SRC_PP, SRC_MF, SRC_FF) if not p.exists()]
    if missing:
        print(f"Missing workbook(s): {missing}", file=sys.stderr)
        return 1

    for technique, spec in TECHNIQUE_SPECS.items():
        pp_map = _load_technique_column(SRC_PP, technique)
        mf_map = _load_technique_column(SRC_MF, technique)
        ff_map = _load_technique_column(SRC_FF, technique)
        if not pp_map or not mf_map or not ff_map:
            print(f"SKIP {technique}: missing numeric rows in pp/mf/ff")
            continue
        pp_m, mf_m, ff_m, spectral = build_spectral_data(pp_map, mf_map, ff_map)
        if not spectral:
            print(f"SKIP {technique}: empty intersection of notes")
            continue
        code = render_module(
            technique=technique,
            spec=spec,
            pp_measured=pp_m,
            mf_measured=mf_m,
            ff_measured=ff_m,
            spectral=spectral,
        )
        out = ROOT / "instrumentos" / f"{spec['module']}.py"
        out.write_text(code, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}  notes={len(spectral)}  technique={technique}")

    ensure_registry()
    print(
        "NOTE: artificial_harmonic / natural_harmonic skipped "
        "(unavailable in source workbooks). No double_bass_art_harm module created."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
