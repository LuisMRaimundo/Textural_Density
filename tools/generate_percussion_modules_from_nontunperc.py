"""
Generate Textural_Density percussion modules from NonTunPerc MC Analysis exports.

Primary metrical source
-----------------------
``replication/percussion_nontunperc/Analysis/density_profiles_mc.csv``
p50 band weights → strike/shimmer ``composite_index`` becomes the **ff** CDM
proxy (NonTunPerc deprecates deterministic point estimates for citation).

Phase choice (perceptually dominant for sustained-texture CDM)
-------------------------------------------------------------
- bass_drum → strike
- cymbals / tamtam / gong → shimmer

Dynamic shape
-------------
pp/mf/ff from ``generate_profile(stroke=<orchestral default>, dynamic=…)``,
scaled so ff equals the MC p50 phase composite. Orchestral defaults:
``bass_drum_beater`` (membrane), ``yarn_mallet`` (plates / suspended).

Usage:
  python tools/generate_percussion_modules_from_nontunperc.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "replication" / "percussion_nontunperc" / "Analysis"
MC_CSV = ANALYSIS_DIR / "density_profiles_mc.csv"
MC_META = ANALYSIS_DIR / "density_profiles_mc.meta.json"
NONTUNPERC = Path(r"C:\Users\lmr20\Desktop\Percussion Tool")
NONTUNPERC_COMMIT = "4a110dbbaab3af831c0987e99a4b7019b008bbd6"
NONTUNPERC_VERSION = "0.3.5"

sys.path.insert(0, str(NONTUNPERC))
sys.path.insert(0, str(ROOT))

from microtonal import midi_to_note_name  # noqa: E402
from model import (  # noqa: E402
    AmplitudeLayer,
    PlateInstrument,
    generate_profile,
    make_bassdrum_catalogue,
)

SPECS = (
    {
        "module": "bass_drum",
        "display": "Bass drum",
        "specimen": "bassdrum_82cm",
        "phase": "strike",
        "stroke": "bass_drum_beater",
        "midi_lo": 28,
        "midi_hi": 48,
        "technique": "struck_membrane",
        "phase_rationale": (
            "Phase = strike: the transient IS the instrument's density for "
            "membranophones; sustained-texture CDM still uses the strike "
            "composite as the proxy."
        ),
    },
    {
        "module": "cymbals",
        "display": "Cymbals",
        "specimen": "cymbal_46cm_medium",
        "phase": "shimmer",
        "stroke": "yarn_mallet",
        "midi_lo": 60,
        "midi_hi": 84,
        "technique": "struck_plate",
        "phase_rationale": (
            "Phase = shimmer: the CDM proxy feeds sustained-texture analysis; "
            "the strike window under-represents plates and, combined with the "
            "excitation filter, artificially collapses pp/mf."
        ),
    },
    {
        "module": "tamtam",
        "display": "Tam-tam",
        "specimen": "tamtam_80cm_bronze",
        "phase": "shimmer",
        "stroke": "yarn_mallet",
        "midi_lo": 24,
        "midi_hi": 48,
        "technique": "struck_plate",
        "phase_rationale": (
            "Phase = shimmer of the tam-tam template (post-bloom sustained "
            "regime). The CDM proxy feeds sustained-texture analysis; the "
            "strike window under-represents plates and, combined with the "
            "excitation filter, artificially collapses pp/mf."
        ),
    },
    {
        "module": "gong",
        "display": "Gong",
        "specimen": "gong_50cm_bronze",
        "phase": "shimmer",
        "stroke": "yarn_mallet",
        "midi_lo": 36,
        "midi_hi": 60,
        "technique": "struck_plate",
        "phase_rationale": (
            "Phase = shimmer (tam-tam-template sustained regime for plate "
            "gongs; wind-gong subtypes share the same post-bloom emphasis). "
            "The CDM proxy feeds sustained-texture analysis; the strike "
            "window under-represents plates and, combined with the excitation "
            "filter, artificially collapses pp/mf."
        ),
    },
)


def _composite_index(weights: np.ndarray, modes: np.ndarray) -> float:
    w = np.asarray(weights, dtype=float)
    modes = np.asarray(modes, dtype=float)
    nz = w > 0
    if not np.any(nz):
        return 0.0
    entropy = -np.sum(w[nz] * np.log(w[nz]))
    mean_occ = float(np.sum(w * modes))
    return float(np.exp(entropy) * mean_occ) ** 0.5


def mc_phase_ci(specimen: str, phase: str) -> dict[str, float]:
    df = pd.read_csv(MC_CSV)
    g = df[df["instrument"] == specimen]
    if g.empty:
        raise KeyError(f"{specimen} missing from {MC_CSV}")
    col = f"energy_w_{phase}"
    out = {}
    for label in ("p05", "p50", "p95"):
        w = g[f"{col}_{label}"].fillna(0.0).to_numpy()
        m = g[f"modes_per_band_{label}"].fillna(0.0).to_numpy()
        out[label] = round(_composite_index(w, m), 6)
    return out


def _mc_seed(specimen: str) -> int:
    meta = json.loads(MC_META.read_text(encoding="utf-8"))
    for row in meta.get("results", []):
        if row.get("instrument") == specimen:
            return int(row["seed"])
    return 20260803


def _build_instrument(specimen: str):
    if specimen.startswith("bassdrum"):
        mems = make_bassdrum_catalogue(NONTUNPERC / "data" / "source_constants.csv")
        return next(m for m in mems if m.name == specimen)
    plates = {
        "cymbal_46cm_medium": PlateInstrument(
            "cymbal_46cm_medium", 0.460, 0.0012, chladni=(14.93, 3.0, 1.557)
        ),
        "gong_50cm_bronze": PlateInstrument("gong_50cm_bronze", 0.500, 0.0020),
        "tamtam_80cm_bronze": PlateInstrument(
            "tamtam_80cm_bronze", 0.800, 0.0015, plate_class="tamtam"
        ),
    }
    return plates[specimen]


def anchors_for(spec: dict) -> tuple[dict[str, float], dict[str, float]]:
    ci = mc_phase_ci(spec["specimen"], spec["phase"])
    amp = AmplitudeLayer.default(NONTUNPERC)
    instr = _build_instrument(spec["specimen"])
    model: dict[str, float] = {}
    for dyn in ("pp", "mf", "ff"):
        profile = generate_profile(
            instr,
            amplitude_layer=amp,
            stroke=spec["stroke"],
            dynamic=dyn,
            csv_path=NONTUNPERC / "data" / "source_constants.csv",
        )
        model[dyn] = float(profile.composite_index(spec["phase"]))
    scale = (ci["p50"] / model["ff"]) if model["ff"] else 1.0
    anchors = {
        "pp": round(model["pp"] * scale, 6),
        "mf": round(model["mf"] * scale, 6),
        "ff": round(ci["p50"], 6),
    }
    return anchors, ci


def _spectral_block(midi_lo: int, midi_hi: int, anchors: dict[str, float]) -> str:
    lines = []
    for midi in range(midi_lo, midi_hi + 1):
        note = midi_to_note_name(float(midi))
        lines.append(
            f"    {note!r}: {{'pp': {anchors['pp']}, 'mf': {anchors['mf']}, "
            f"'ff': {anchors['ff']}}},"
        )
    return "\n".join(lines)


def _module_source(
    spec: dict,
    anchors: dict[str, float],
    ci: dict[str, float],
) -> str:
    spectral = _spectral_block(spec["midi_lo"], spec["midi_hi"], anchors)
    seed = _mc_seed(spec["specimen"])
    mf_ff_jump = anchors["ff"] / anchors["mf"] if anchors["mf"] else float("inf")
    citation = (
        f"theoretical model output (NonTunPerc v{NONTUNPERC_VERSION}, MC median), "
        f"anchored in Rossing 2000 / Fletcher & Rossing 1998 / Sivian et al. 1931; "
        f"validated against Iowa EMS recordings for mallet-excited plates and mf "
        f"tam-tams; NOT validated for striking-position-specific strokes. "
        f"Specimen {spec['specimen']} phase={spec['phase']} MC p50 "
        f"composite_index={ci['p50']} (p05={ci['p05']}, p95={ci['p95']}; "
        f"seed={seed})."
    )
    extraction = (
        f"density_profiles_mc.csv {spec['phase']} p50 band weights → "
        f"composite_index (ff); generate_profile(stroke={spec['stroke']!r}, "
        f"dynamic=pp|mf|ff) {spec['phase']} indices scaled so ff=MC p50; "
        f"flat chromatic CDM proxy; piecewise log-linear CDM interpolation "
        f"(internal_default; guarantees monotone pp…ff on cascade jumps). "
        f"Cross-family ratio caveat: NonTunPerc calibration bridge reports "
        f"NO CALIBRATION ACHIEVED; CDM comparisons between these four "
        f"instruments and empirically derived pitched-instrument tables are "
        f"rank-order indicative only, not ratio-valid."
    )
    return f'''# instrumentos/{spec["module"]}.py
"""
{spec["display"]} instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM)
proxy values from **NonTunPerc** MC Analysis exports
(``replication/percussion_nontunperc/Analysis/density_profiles_mc.csv``).

{spec["phase_rationale"]}

- **ff:** MC p50 ``composite_index`` for phase ``{spec["phase"]}``
  (p05={ci["p05"]}, p50={ci["p50"]}, p95={ci["p95"]}; seed={seed})
- **pp/mf:** ``generate_profile(stroke={spec["stroke"]!r}, dynamic=…)``
  {spec["phase"]} indices, scaled so ff matches MC p50 exactly
- **mf→ff jump:** ff/mf ≈ {mf_ff_jump:.3f} (physical cascade / ff plate bypass
  where applicable — retained; interior dynamics use log-CDM piecewise linear
  interpolation so ``f`` lies between mf and ff)
- **NonTunPerc:** v{NONTUNPERC_VERSION} commit ``{NONTUNPERC_COMMIT}``

Flat chromatic table: note key is notation-lookup convention only; no acoustic
meaning (see ``INSTRUMENT_SOURCE.unpitched`` / registry ``unpitched`` flag).
Intermediate dynamics use piecewise log-linear CDM interpolation
(``internal_default``; Matérn GPR cannot stay monotone on large mf→ff jumps).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="model_derived",
    citation=({citation!r}),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles_mc.csv"
    ),
    extraction_method=({extraction!r}),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=({spec["midi_lo"]}, {spec["midi_hi"]}),
    uncertainty="high",
    version="2026-08-03+nontunperc-{NONTUNPERC_VERSION}+mc{seed}",
    source_technique="{spec["technique"]}",
    table_supported_techniques=("{spec["technique"]}",),
    unpitched=True,
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("{spec["module"]}")

# MC composite_index CI for the chosen phase (scale reference; seed={seed}).
SPECTRAL_PHASE_CI = {{
    "phase": "{spec["phase"]}",
    "p05": {ci["p05"]},
    "p50": {ci["p50"]},
    "p95": {ci["p95"]},
    "mc_seed": {seed},
    "nontunperc_commit": "{NONTUNPERC_COMMIT}",
    "nontunperc_version": "{NONTUNPERC_VERSION}",
}}

# Parallel CI dict (same for every note; flat unpitched table).
spectral_data_ci = {{
    "p05": {ci["p05"]},
    "p50": {ci["p50"]},
    "p95": {ci["p95"]},
}}

# Flat CDM proxy. Range is notation-lookup convention only; no acoustic meaning
# (see unpitched flag).
spectral_data = {{
{spectral}
}}


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



    )
'''


def main() -> int:
    if not MC_CSV.is_file():
        print(f"Missing MC CSV: {MC_CSV}", file=sys.stderr)
        return 1
    if not NONTUNPERC.is_dir():
        print(f"Missing NonTunPerc root: {NONTUNPERC}", file=sys.stderr)
        return 1
    out_dir = ROOT / "instrumentos"
    for spec in SPECS:
        anchors, ci = anchors_for(spec)
        path = out_dir / f"{spec['module']}.py"
        path.write_text(_module_source(spec, anchors, ci), encoding="utf-8")
        print(f"Wrote {path.name}: {anchors}  CI={ci}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
