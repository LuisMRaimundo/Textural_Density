#!/usr/bin/env python3
"""Generate violin harmonic instrument modules from Desktop Excel workbooks.

Sources (calibrated / assumption-based EWSD from Strings_techniques_extrapolation):
  - c:\\Users\\lmr20\\Desktop\\Violin_pp_hamro.xlsx
  - c:\\Users\\lmr20\\Desktop\\Violin_mf_harmo.xlsx
  - c:\\Users\\lmr20\\Desktop\\Violin_ff_harmo.xlsx

Techniques written:
  - artificial_harmonic → instrumentos/violin_art_harm.py
  - natural_harmonic    → instrumentos/violin_nat_harm.py

All three dynamics (pp/mf/ff) come from workbook ``estimate_mean`` / ``All_Results``.
Duplicate sounding pitches (natural harmonics) are averaged.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_PP = Path(r"c:\Users\lmr20\Desktop\Violin_pp_hamro.xlsx")
SRC_MF = Path(r"c:\Users\lmr20\Desktop\Violin_mf_harmo.xlsx")
SRC_FF = Path(r"c:\Users\lmr20\Desktop\Violin_ff_harmo.xlsx")

TECHNIQUE_SPECS = {
    "artificial_harmonic": {
        "module": "violin_art_harm",
        "registry_id": "violino_art_harm",
        "display": "Violin art harm",
        "source_technique": "arco_artificial_harmonic",
        "logger": "violin_art_harm",
        "doc_anchor": "violin-art-harm",
        "pitch_range": (79, 108),
        "comfortable": (79, 100),
        "brightness": "bright",
        "attack": "soft",
        "supported": ("arco", "harmonic"),
        "unsupported": ("pizzicato", "mute", "sul_ponticello", "sul_tasto"),
        "aliases": (
            "violin_art_harm",
            "Violin_art_harm",
            "violin artificial harmonics",
            "violin_artificial_harmonics",
            "violino art harm",
            "violino_art_harm",
            "violino artificial harmonics",
            "art harm violin",
            "art_harm_violin",
        ),
    },
    "natural_harmonic": {
        "module": "violin_nat_harm",
        "registry_id": "violino_nat_harm",
        "display": "Violin nat harm",
        "source_technique": "arco_natural_harmonic",
        "logger": "violin_nat_harm",
        "doc_anchor": "violin-nat-harm",
        "pitch_range": (67, 107),
        "comfortable": (67, 91),
        "brightness": "bright",
        "attack": "soft",
        "supported": ("arco", "harmonic"),
        "unsupported": ("pizzicato", "mute", "sul_ponticello", "sul_tasto"),
        "aliases": (
            "violin_nat_harm",
            "Violin_nat_harm",
            "violin natural harmonics",
            "violin_natural_harmonics",
            "violino nat harm",
            "violino_nat_harm",
            "violino natural harmonics",
            "nat harm violin",
            "nat_harm_violin",
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
    # Average duplicate sounding pitches (natural harmonics from multiple strings).
    grouped = sub.groupby(sub["pitch"].astype(str).str.strip(), as_index=True)["estimate_mean"].mean()
    return {str(note): float(val) for note, val in grouped.items()}


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
Violin ({technique_label}) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``pp``, ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Violin_pp_hamro.xlsx`` / ``Violin_mf_harmo.xlsx`` /
   ``Violin_ff_harmo.xlsx``), column ``estimate_mean`` / ``All_Results``.
2. **GPR-modelled dynamics:** intermediate / extreme markings predicted by GPR
   on the pp/mf/ff triple.

These workbook values are calibrated / assumption-based harmonic descriptor
lookups from Strings Techniques Extrapolation (not Zenodo ordinary CDM rows).
Uncertainty is therefore high.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin {technique} EWSD table from Strings_techniques_extrapolation "
        "workbooks Violin_pp_hamro.xlsx / Violin_mf_harmo.xlsx / Violin_ff_harmo.xlsx "
        "(calibrated harmonic descriptor lookup / assumption-based dynamic transfer)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#{doc_anchor}",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "duplicate sounding pitches averaged; GPR interpolation by pitch/dynamic"
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

# Workbook pp / mf / ff anchors ({n} chromatic sounding rows, {first}–{last}).
PP_MEASURED: dict[str, float] = {pp_block}

MF_MEASURED: dict[str, float] = {mf_block}

FF_MEASURED: dict[str, float] = {ff_block}

# GPR anchors: pp/mf/ff from Excel harmonic workbooks.
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


def _fmt_tuple(values: tuple[str, ...]) -> str:
    return "(" + ", ".join(f'"{v}"' for v in values) + ")"


def upsert_registry(spec: dict, *, n_notes: int, first: str, last: str) -> None:
    registry_path = ROOT / "instrumentos" / "registry.py"
    text = registry_path.read_text(encoding="utf-8")
    rid = spec["registry_id"]
    lo, hi = spec["pitch_range"]
    c_lo, c_hi = spec["comfortable"]
    aliases = ",\n        ".join(f'"{a}"' for a in spec["aliases"])
    block = f'''
REGISTRY["{rid}"] = _profile(
    "{rid}",
    "{spec["display"]}",
    "strings",
    sounding=({lo}, {hi}),
    comfortable=({c_lo}, {c_hi}),
    brightness="{spec["brightness"]}",
    sustain="sustained",
    attack="{spec["attack"]}",
    status="literature_derived",
    uncertainty="high",
    module_name="{spec["module"]}",
    supported={_fmt_tuple(spec["supported"])},
    unsupported={_fmt_tuple(spec["unsupported"])},
    source_notes=(
        "Sparse GPR table in instrumentos/{spec["module"]}.py from Strings Techniques "
        "Extrapolation Violin_pp_hamro.xlsx / Violin_mf_harmo.xlsx / Violin_ff_harmo.xlsx "
        "(calibrated harmonic descriptor EWSD); sounding pitches {first}–{last} ({n_notes} rows)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers {spec["source_technique"]} only; pp/mf/ff come from "
        "Strings Techniques Extrapolation harmonic workbooks (calibrated / assumption-based).",
        "Table span is harmonic sounding register ({first}–{last}); notes outside this range "
        "use controlled pitch extrapolation or fallback.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        {aliases},
    ),
)


'''
    marker = f'REGISTRY["{rid}"]'
    if marker in text:
        # Replace existing block through the blank line before the next REGISTRY[
        pattern = re.compile(
            rf'REGISTRY\["{re.escape(rid)}"\] = _profile\([\s\S]*?\n\)\n\n',
            re.MULTILINE,
        )
        new_text, n = pattern.subn(block.lstrip("\n"), text, count=1)
        if n != 1:
            raise RuntimeError(f"Failed to replace registry block for {rid}")
        text = new_text
        print(f"registry: updated {rid}")
    else:
        insert_at = 'REGISTRY["violoncelo_sordina"]'
        if insert_at not in text:
            raise RuntimeError("Could not locate insertion point for harmonic registry entries")
        text = text.replace(insert_at, block + insert_at, 1)
        print(f"registry: inserted {rid}")
    registry_path.write_text(text, encoding="utf-8")


def main() -> int:
    missing = [p for p in (SRC_PP, SRC_MF, SRC_FF) if not p.exists()]
    if missing:
        print("Missing harmonic workbooks:", ", ".join(str(p) for p in missing), file=sys.stderr)
        return 1

    for technique, spec in TECHNIQUE_SPECS.items():
        pp_map = _load_technique_column(SRC_PP, technique)
        mf_map = _load_technique_column(SRC_MF, technique)
        ff_map = _load_technique_column(SRC_FF, technique)
        if not pp_map or not mf_map or not ff_map:
            print(f"SKIP {technique}: missing numeric rows")
            continue
        pp_m, mf_m, ff_m, spectral = build_spectral_data(pp_map, mf_map, ff_map)
        if not spectral:
            print(f"SKIP {technique}: empty intersection across dynamics")
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
        first = next(iter(spectral))
        last = next(reversed(spectral))
        print(f"wrote {out.relative_to(ROOT)}  notes={len(spectral)}  {first}–{last}")
        upsert_registry(spec, n_notes=len(spectral), first=first, last=last)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
