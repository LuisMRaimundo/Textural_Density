#!/usr/bin/env python3
"""Generate viola technique instrument modules from Desktop Excel workbooks.

Sources (assumption-based EWSD extrapolations from Strings_techniques_extrapolation):
  - c:\\Users\\lmr20\\Desktop\\Viola_pp.xlsx
  - c:\\Users\\lmr20\\Desktop\\Viola_mf.xlsx
  - c:\\Users\\lmr20\\Desktop\\Viola_ff.xlsx

Numeric techniques written:
  - con_sordino    → instrumentos/viola_sordina.py
  - sul_tasto      → instrumentos/viola_sul_tasto.py
  - sul_ponticello → instrumentos/viola_sul_ponticello.py

Harmonics are skipped: artificial/natural harmonic cells are unavailable
(no_harmonic_acoustic_calibration_data). No viola_art_harm module is created.

Unlike the violin generator, all three dynamics (pp/mf/ff) are taken directly
from workbook ``estimate_mean`` columns — no arco ratio transfer for pp.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_PP = Path(r"c:\Users\lmr20\Desktop\Viola_pp.xlsx")
SRC_MF = Path(r"c:\Users\lmr20\Desktop\Viola_mf.xlsx")
SRC_FF = Path(r"c:\Users\lmr20\Desktop\Viola_ff.xlsx")

TECHNIQUE_SPECS = {
    "con_sordino": {
        "module": "viola_sordina",
        "registry_id": "viola_sordina",
        "display": "Viola sordina",
        "source_technique": "arco_sordina",
        "logger": "viola_sordina",
        "doc_anchor": "viola-sordina",
        "pitch_range": (48, 96),
        "comfortable": (50, 69),
        "brightness": "neutral",
        "attack": "soft",
        "supported": ("arco", "mute"),
        "unsupported": ("pizzicato", "sul_ponticello", "sul_tasto"),
        "aliases": (
            "viola_sordina",
            "Viola_sordina",
            "viola con sordina",
            "viola_con_sordina",
            "viola sordina",
            "viola muted",
            "muted viola",
        ),
    },
    "sul_tasto": {
        "module": "viola_sul_tasto",
        "registry_id": "viola_sul_tasto",
        "display": "Viola sul tasto",
        "source_technique": "arco_sul_tasto",
        "logger": "viola_sul_tasto",
        "doc_anchor": "viola-sul-tasto",
        "pitch_range": (48, 96),
        "comfortable": (50, 69),
        "brightness": "dark",
        "attack": "soft",
        "supported": ("arco", "sul_tasto"),
        "unsupported": ("pizzicato", "mute", "sul_ponticello"),
        "aliases": (
            "viola_sul_tasto",
            "Viola_sul_tasto",
            "viola sul tasto",
            "sul tasto viola",
            "sul_tasto_viola",
        ),
    },
    "sul_ponticello": {
        "module": "viola_sul_ponticello",
        "registry_id": "viola_sul_ponticello",
        "display": "Viola sul ponticello",
        "source_technique": "arco_sul_ponticello",
        "logger": "viola_sul_ponticello",
        "doc_anchor": "viola-sul-ponticello",
        "pitch_range": (48, 96),
        "comfortable": (50, 69),
        "brightness": "bright",
        "attack": "hard",
        "supported": ("arco", "sul_ponticello"),
        "unsupported": ("pizzicato", "mute", "sul_tasto"),
        "aliases": (
            "viola_sul_ponticello",
            "Viola_sul_ponticello",
            "viola sul pont",
            "viola_sul_pont",
            "viola sul ponticello",
            "sul ponticello viola",
            "sul_ponticello_viola",
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
Viola ({technique_label}) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``pp``, ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Viola_pp.xlsx`` / ``Viola_mf.xlsx`` /
   ``Viola_ff.xlsx``), column ``estimate_mean`` / ``All_Results``.
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
        "Viola {technique} EWSD table from Strings_techniques_extrapolation "
        "workbooks Viola_pp.xlsx / Viola_mf.xlsx / Viola_ff.xlsx "
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
        "Extrapolation Viola_pp.xlsx / Viola_mf.xlsx / Viola_ff.xlsx "
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
    # Insert after base viola loop block ends — before violino_sordina if present,
    # otherwise after the strings for-loop that defines viola.
    marker = 'REGISTRY["violino_sordina"]'
    if marker in text:
        text = text.replace(marker, insert + marker, 1)
    else:
        # Fall back: after violino_art_harm block start is wrong; append before brass
        marker2 = "# --- Brass"
        if marker2 not in text:
            raise RuntimeError("Could not locate insertion point in registry.py")
        text = text.replace(marker2, insert + marker2, 1)

    registry_path.write_text(text, encoding="utf-8")
    print("registry: inserted viola technique profiles")


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
        "(unavailable in source workbooks). No viola_art_harm module created."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
