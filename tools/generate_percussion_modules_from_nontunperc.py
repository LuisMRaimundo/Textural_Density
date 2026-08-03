"""
Generate Textural_Density percussion modules from NonTunPerc Analysis exports.

Primary metrical source
-----------------------
``replication/percussion_nontunperc/Analysis/density_profiles.csv``
(copied from Percussion Tool ``Analysis/``). Strike-phase
``composite_index`` becomes the **ff** CDM proxy for each specimen.

Dynamic shape
-------------
pp/mf are taken from NonTunPerc ``generate_profile`` with stroke+dynamic
excitation, then scaled so that **ff exactly equals** the Analysis strike
composite (plates already match; bass drum is renormalised).

Usage (from Textural_Density project root):
  python tools/generate_percussion_modules_from_nontunperc.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_CSV = ROOT / "replication" / "percussion_nontunperc" / "Analysis" / "density_profiles.csv"
NONTUNPERC = Path(r"C:\Users\lmr20\Desktop\Percussion Tool")

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
        "stroke": "bass_drum_beater",
        "midi_lo": 28,
        "midi_hi": 48,
        "technique": "struck_membrane",
    },
    {
        "module": "cymbals",
        "display": "Cymbals",
        "specimen": "cymbal_46cm_medium",
        "stroke": "unmarked",
        "midi_lo": 60,
        "midi_hi": 84,
        "technique": "struck_plate",
    },
    {
        "module": "tamtam",
        "display": "Tam-tam",
        "specimen": "tamtam_80cm_bronze",
        "stroke": "unmarked",
        "midi_lo": 24,
        "midi_hi": 48,
        "technique": "struck_plate",
    },
    {
        "module": "gong",
        "display": "Gong",
        "specimen": "gong_50cm_bronze",
        "stroke": "yarn_mallet",
        "midi_lo": 36,
        "midi_hi": 60,
        "technique": "struck_plate",
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


def analysis_strike_index(specimen: str) -> float:
    df = pd.read_csv(ANALYSIS_CSV)
    g = df[df["instrument"] == specimen]
    if g.empty:
        raise KeyError(f"{specimen} missing from {ANALYSIS_CSV}")
    return _composite_index(
        g["energy_w_strike"].fillna(0.0).to_numpy(),
        g["modes_per_band"].to_numpy(),
    )


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


def anchors_for(spec: dict) -> dict[str, float]:
    """ff from Analysis CSV; pp/mf from NonTunPerc scaled to that ff."""
    analysis_ff = analysis_strike_index(spec["specimen"])
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
        model[dyn] = float(profile.composite_index("strike"))
    scale = (analysis_ff / model["ff"]) if model["ff"] else 1.0
    return {
        "pp": round(model["pp"] * scale, 6),
        "mf": round(model["mf"] * scale, 6),
        "ff": round(analysis_ff, 6),
    }


def _spectral_block(midi_lo: int, midi_hi: int, anchors: dict[str, float]) -> str:
    lines = []
    for midi in range(midi_lo, midi_hi + 1):
        note = midi_to_note_name(float(midi))
        lines.append(
            f"    {note!r}: {{'pp': {anchors['pp']}, 'mf': {anchors['mf']}, "
            f"'ff': {anchors['ff']}}},"
        )
    return "\n".join(lines)


def _module_source(spec: dict, anchors: dict[str, float]) -> str:
    spectral = _spectral_block(spec["midi_lo"], spec["midi_hi"], anchors)
    citation = (
        f"NonTunPerc Analysis density_profiles.csv strike composite_index for "
        f"{spec['specimen']} (ff CDM proxy); pp/mf from NonTunPerc excitation-"
        f"filtered profiles scaled so ff matches the Analysis metrical export."
    )
    return f'''# instrumentos/{spec["module"]}.py
"""
{spec["display"]} instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM)
proxy values from **NonTunPerc Analysis** metrical exports
(``replication/percussion_nontunperc/Analysis/density_profiles.csv``).

- **ff:** strike-phase ``composite_index`` from Analysis ``density_profiles.csv``
- **pp/mf:** NonTunPerc excitation-filtered strike indices, scaled so ff
  matches the Analysis metrical value exactly

Unpitched strokes use a flat chromatic table over the registry nominal MIDI
sounding range; intermediate dynamics are interpolated via GPR.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="literature_derived",
    citation=({citation!r}),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles.csv"
    ),
    extraction_method=(
        "Analysis density_profiles.csv strike composite_index → ff; "
        "NonTunPerc generate_profile(stroke,dynamic) strike indices → pp/mf "
        "with scale so ff matches Analysis; flat chromatic CDM proxy; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=({spec["midi_lo"]}, {spec["midi_hi"]}),
    uncertainty="high",
    version="2026-08-03",
    source_technique="{spec["technique"]}",
    table_supported_techniques=("{spec["technique"]}",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("{spec["module"]}")

# Flat CDM proxy across nominal sounding range (unpitched; note is metadata only).
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


def predict_intermediate_dynamics(pitches, pp_values, mf_values, ff_values):
    """Predict intermediate dynamics using Gaussian Process Regression."""
    from instrumentos.gpr_dynamic_interpolation import predict_intermediate_dynamics_gpr

    return predict_intermediate_dynamics_gpr(
        pp_values, mf_values, ff_values, logger=logger
    )
'''


def main() -> int:
    if not ANALYSIS_CSV.is_file():
        print(f"Missing Analysis CSV: {ANALYSIS_CSV}", file=sys.stderr)
        return 1
    if not NONTUNPERC.is_dir():
        print(
            f"Missing NonTunPerc root (needed for pp/mf shape): {NONTUNPERC}",
            file=sys.stderr,
        )
        return 1
    out_dir = ROOT / "instrumentos"
    for spec in SPECS:
        anchors = anchors_for(spec)
        path = out_dir / f"{spec['module']}.py"
        path.write_text(_module_source(spec, anchors), encoding="utf-8")
        print(f"Wrote {path.name}: {anchors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
