#!/usr/bin/env python3
"""Reproduce interval-term and blend checks after 5.2.0.

H3: density.interval = effective interval cardinality (n_eff - 1).
H4: density.weighted = w * DI / 10 + (1 - w) * DV.

Writes JSON to stdout only. Does not modify repository files.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

from config import DEFAULT_WEIGHT_FACTOR, MAX_DENS_GLOBAL, USE_LOG_COMPRESSION
from core.composite import INSTRUMENT_BLEND_DIVISOR, compute_blend_density
from core.defaults import METRIC_SCHEMA_VERSION
from core.pipeline import calculate_metrics
from core.pitch_structure import (
    calculate_interval_density_from_distinct_midis,
    effective_interval_cardinality,
)
from core.version import PACKAGE_VERSION
from densidade_intervalar import load_calibrated_parameters, modified_exponential_decay
from instrumentos.registry import REGISTRY
from microtonal import note_to_midi_strict


def _case(notes, instruments=None, dynamics=None, qty=None, w=0.5):
    n = len(notes)
    return {
        "notes": list(notes),
        "instruments": instruments or ["flauta"] * n,
        "dynamics": dynamics or ["mf"] * n,
        "num_instruments": qty or [1] * n,
        "weight_factor": float(w),
    }


def run_metrics(payload):
    resultados, _, _ = calculate_metrics(payload)
    d = resultados["density"]
    return {
        "interval": float(d["interval"]),
        "instrument": float(d["instrument"]),
        "weighted": float(d["weighted"]),
        "weighted_orchestral": float(d["weighted_orchestral"]),
        "weighted_pitch": float(d["weighted_pitch"]),
        "sonic_mass": float(d["sonic_mass"]),
        "total": float(d["total"]),
        "pitch_structure": float(d["pitch_structure"]),
        "interval_raw": float(resultados["density_subindices"]["interval_compactness"]["raw"]),
        "schema": resultados.get("metric_metadata", {}).get("metric_schema_version"),
    }


def reconstruct_h3(notes):
    midis = sorted({float(note_to_midi_strict(n)) for n in notes})
    raw = calculate_interval_density_from_distinct_midis(midis)
    dv = effective_interval_cardinality(raw, len(midis))
    return {"S": raw, "DV": dv, "n": len(midis)}


def reconstruct_h4(di, dv, w, mass):
    blend = compute_blend_density(di, dv, w=w)
    direct = w * di / INSTRUMENT_BLEND_DIVISOR + (1.0 - w) * dv
    pre = blend * math.sqrt(mass) / MAX_DENS_GLOBAL
    total = math.log10(1.0 + pre) if USE_LOG_COMPRESSION else pre
    return {
        "weighted": blend,
        "weighted_direct": direct,
        "total_pre_log": pre,
        "total": total,
    }


def old_mean_log_dv(raw, n):
    if n < 2:
        return 0.0
    mean = 2.0 * raw / (n * (n - 1))
    return math.log10(1.0 + mean)


def kernel_scan():
    lamb = float(load_calibrated_parameters())
    rows = []
    ok = True
    for delta in [0.0, 0.001, 0.5, 1.0, 2.0, 12.0, 24.0, 48.0, 96.0]:
        k = float(modified_exponential_decay(delta, lamb))
        valid = (k == 1.0) if delta == 0.0 else (0.0 < k <= 1.0)
        if not valid:
            ok = False
        rows.append({"delta": delta, "K": k, "ok": valid})
    return {"lambda": lamb, "ok": ok, "rows": rows}


def table_coeff_scan():
    nonpositive = []
    n_cells = 0
    n_modules = 0
    for iid, profile in REGISTRY.items():
        if not profile.module_name:
            continue
        try:
            mod = __import__(f"instrumentos.{profile.module_name}", fromlist=["spectral_data"])
        except Exception as exc:
            nonpositive.append({"id": iid, "error": str(exc)})
            continue
        data = getattr(mod, "spectral_data", None)
        if not isinstance(data, dict):
            continue
        n_modules += 1
        for pitch, dyns in data.items():
            if not isinstance(dyns, dict):
                continue
            for dyn, val in dyns.items():
                n_cells += 1
                if not (isinstance(val, (int, float)) and val > 0.0):
                    nonpositive.append(
                        {"id": iid, "pitch": str(pitch), "dyn": str(dyn), "value": val}
                    )
    return {
        "n_table_modules": n_modules,
        "n_cells": n_cells,
        "nonpositive": nonpositive,
        "ok": not nonpositive,
    }


def before_after_row(notes, instruments=None, dynamics=None, qty=None, label=""):
    payload = _case(notes, instruments, dynamics, qty)
    live = run_metrics(payload)
    rec = reconstruct_h3(notes)
    old_dv = old_mean_log_dv(rec["S"], rec["n"])
    w = DEFAULT_WEIGHT_FACTOR
    di = live["instrument"]
    mass = live["sonic_mass"]
    old_blend = w * di / 10.0 + (1.0 - w) * old_dv
    old_total = math.log10(1.0 + old_blend * math.sqrt(mass) / MAX_DENS_GLOBAL)
    new_share = (0.5 * live["interval"]) / live["weighted"] if live["weighted"] else None
    old_share = (0.5 * old_dv) / old_blend if old_blend else None
    return {
        "label": label,
        "notes": list(notes),
        "S": rec["S"],
        "old_DV": old_dv,
        "new_DV": live["interval"],
        "h3_reconstructed": rec["DV"],
        "old_weighted": old_blend,
        "new_weighted": live["weighted"],
        "old_total": old_total,
        "new_total": live["total"],
        "old_interval_share": old_share,
        "new_interval_share": new_share,
        "instrument": di,
        "sonic_mass": mass,
    }


def main():
    out = {
        "constants": {
            "PACKAGE_VERSION": PACKAGE_VERSION,
            "METRIC_SCHEMA_VERSION": METRIC_SCHEMA_VERSION,
            "MAX_DENS_GLOBAL": MAX_DENS_GLOBAL,
            "lambda": float(load_calibrated_parameters()),
            "INSTRUMENT_BLEND_DIVISOR": INSTRUMENT_BLEND_DIVISOR,
            "USE_LOG_COMPRESSION": USE_LOG_COMPRESSION,
        },
        "P1_kernel": kernel_scan(),
        "P2_tables": table_coeff_scan(),
        "H3": {},
        "H4": {},
        "before_after": [],
    }

    triad = ["C4", "E4", "G4"]
    live = run_metrics(_case(triad))
    h3 = reconstruct_h3(triad)
    h4 = reconstruct_h4(live["instrument"], live["interval"], 0.5, live["sonic_mass"])
    out["H3"] = {
        "definition": "DV = (sqrt(1+8S)-1)/2 = n_eff-1; 0 when n<2",
        "production_interval": live["interval"],
        "reconstructed": h3,
        "abs_diff": abs(live["interval"] - h3["DV"]),
        "matches": abs(live["interval"] - h3["DV"]) < 1e-12,
    }
    out["H4"] = {
        "definition": "weighted = w*DI/10 + (1-w)*DV",
        "production_weighted": live["weighted"],
        "reconstructed": h4,
        "abs_diff": abs(live["weighted"] - h4["weighted"]),
        "matches": abs(live["weighted"] - h4["weighted_direct"]) < 1e-12,
    }

    chromatic = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]
    for n in (1, 2, 3, 4, 6, 12):
        out["before_after"].append(
            before_after_row(chromatic[:n], label=f"chromatic_n{n}")
        )

    for label, notes in (
        ("cluster_C4_Ds4", ["C4", "C#4", "D4", "D#4"]),
        ("major_thirds", ["C4", "E4", "G#4", "C5"]),
        ("fifths", ["C4", "G4", "D5", "A5"]),
        ("octaves_G3_G6", ["G3", "G4", "G5", "G6"]),
    ):
        out["before_after"].append(
            before_after_row(notes, instruments=["violino"] * 4, label=label)
        )

    out["before_after"].append(before_after_row(["C4", "C#4"], label="minor_second"))
    out["before_after"].append(
        before_after_row(
            ["C4", "C#4", "C8"],
            instruments=["piano"] * 3,
            label="minor_second_plus_far",
        )
    )

    tutti_notes = [
        "C5", "G4", "E4", "C3", "G3", "A4", "D4", "G2", "C4", "Bb3", "E3", "E2",
    ]
    tutti_inst = [
        "flauta", "oboe", "clarinete", "fagote", "trompa", "violino",
        "viola", "violoncelo", "trompete", "trombone", "piano", "contrabaixo",
    ]
    tutti_dyn = [
        "mf", "p", "mp", "f", "ff", "mf", "p", "mp", "f", "mf", "pp", "ff",
    ]
    out["before_after"].append(
        before_after_row(
            tutti_notes,
            instruments=tutti_inst,
            dynamics=tutti_dyn,
            label="tutti_12_mixed",
        )
    )

    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if not out["P1_kernel"]["ok"] or not out["P2_tables"]["ok"]:
        raise SystemExit(2)
    if not out["H3"]["matches"] or not out["H4"]["matches"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
