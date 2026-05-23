"""
Export documented constants and score-only defaults for audit/replication.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import config
from core.defaults import METRIC_SCHEMA_VERSION, RESEARCH_ANALYSIS_DEFAULTS


def export_constants_and_assumptions() -> dict[str, Any]:
    """Return JSON-serializable inventory of constants and research defaults."""
    return {
        "metric_schema_version": METRIC_SCHEMA_VERSION,
        "research_defaults": dict(RESEARCH_ANALYSIS_DEFAULTS),
        "normalization": {
            "MAX_DENS_GLOBAL": config.MAX_DENS_GLOBAL,
            "USE_LOG_COMPRESSION": config.USE_LOG_COMPRESSION,
            "COMPOSITE_HARMONIC_DAMPING": config.COMPOSITE_HARMONIC_DAMPING,
        },
        "pitch": {
            "MIDI_BASE_FREQUENCY": config.MIDI_BASE_FREQUENCY,
            "MIDI_BASE_NOTE": config.MIDI_BASE_NOTE,
            "TAMANHO_OITAVA_MICROTONAL": config.TAMANHO_OITAVA_MICROTONAL,
            "module": "config.py",
            "role": "Symbolic pitch/MIDI mapping; not measured audio.",
        },
        "interval_compactness": {
            "DEFAULT_LAMBDA": config.DEFAULT_LAMBDA,
            "module": "config.py / densidade_intervalar.py",
            "role": "Exponential decay over pitch distance; score-derived compactness.",
            "configurable": True,
        },
        "register": {
            "DEFAULT_REGISTER_BANDS": {
                k: list(v) for k, v in config.DEFAULT_REGISTER_BANDS.items()
            },
            "module": "config.py",
            "role": "Register band occupancy for registral metrics.",
            "configurable": True,
        },
        "written_dynamics": {
            "DYNAMIC_LEVELS": list(config.DYNAMIC_LEVELS),
            "module": "config.py / instrumentos/registry.py",
            "role": "Symbolic dynamic weighting for score analysis; not SPL or loudness.",
            "configurable": False,
        },
        "composite": {
            "DEFAULT_WEIGHT_FACTOR": config.DEFAULT_WEIGHT_FACTOR,
            "module": "config.py",
            "role": "Linear blend of instrument vs interval density after min-max normalization.",
        },
        "limitations": [
            "Written dynamics are symbolic score metadata, not loudness.",
            "Instrument GPR modules use externally sourced acoustic amplitude metadata; "
            "coarse profiles lack such tables.",
            "Perceptual/acoustic proxy branches removed in 3.0.0–4.0.0 (strictly symbolic).",
        ],
    }


def write_constants_json(path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(export_constants_and_assumptions(), f, indent=2)
    return out
