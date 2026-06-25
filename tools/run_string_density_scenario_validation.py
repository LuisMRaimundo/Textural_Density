#!/usr/bin/env python3
"""
String-only density scenario validation campaign.

Generates a deterministic matrix of string ensemble scenarios using
sounding/concert-pitch notes and runs them through core.pipeline.calculate_metrics.

Outputs:
  reports/string_density_scenario_validation.json
  reports/string_density_scenario_validation.csv
  reports/string_density_scenario_validation.md
  reports/string_density_scenario_validation_summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import combinations, permutations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from microtonal import midi_to_note_name, note_to_midi_strict  # noqa: E402

from core.pipeline import calculate_metrics  # noqa: E402
from error_handler import InputError  # noqa: E402
from instrumentos.registry import REGISTRY, resolve_profile  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CANONICAL_INSTRUMENTS: dict[str, dict[str, Any]] = {
    "violin": {
        "canonical_id": "violino",
        "display": "Violin",
        "alias": "violin",
        "open_strings": ("G3", "D4", "A4", "E5"),
    },
    "viola": {
        "canonical_id": "viola",
        "display": "Viola",
        "alias": "viola",
        "open_strings": ("C3", "G3", "D4", "A4"),
    },
    "cello": {
        "canonical_id": "violoncelo",
        "display": "Cello",
        "alias": "cello",
        "open_strings": ("C2", "G2", "D3", "A3"),
    },
    "double_bass": {
        "canonical_id": "contrabaixo",
        "display": "Double bass",
        "alias": "double_bass",
        "open_strings": ("E1", "A1", "D2", "G2"),  # sounding/concert pitch
    },
}

CAMPAIGN_DYNAMICS = ("pp", "p", "mp", "mf", "f", "ff")
SOURCE_ANCHOR_DYNAMICS = frozenset({"pp", "mf", "ff"})

REGISTER_BANDS = (
    "low",
    "low_mid",
    "middle",
    "upper_mid",
    "high",
    "near_lower_boundary",
    "near_upper_boundary",
)

AGGREGATE_TYPES = (
    "single_note",
    "exact_unison",
    "same_instrument_unison_qty",
    "octave_doubling",
    "compact_dyad",
    "compact_trichord",
    "compact_chromatic_cluster",
    "very_dense_chromatic",
    "diatonic_aggregate",
    "sparse_aggregate",
    "very_sparse_aggregate",
    "registrally_stratified",
    "homogeneous_instrument",
    "heterogeneous_string",
    "sectional_string",
    "quartet_voicing",
    "cluster_plus_octave",
    "low_register_mass",
    "high_register_mass",
    "mixed_dynamics",
    "cross_dynamic_comparison",
    "instrument_substitution",
    "quantity_scaling",
    "event_order_invariance",
    "pitch_collection_invariance",
    "register_shift_comparison",
    "boundary_safe",
    "negative_out_of_range",
)

DENSITY_METRIC_KEYS = (
    "instrument",
    "interval",
    "pitch_structure",
    "sonic_mass",
    "total",
    "weighted",
    "weighted_orchestral",
    "weighted_pitch",
    "absolute",
    "refined",
)

FLOAT_TOL = 1e-9


@dataclass
class ScenarioSpec:
    scenario_id: str
    scenario_group: str
    aggregate_type: str
    register_band: str
    dynamic_profile: str
    notes: list[str]
    dynamics: list[str]
    instruments: list[str]
    quantities: list[int]
    expected_validity: str  # "positive" | "negative"
    invariant_group_id: str | None = None
    comparison_baseline_id: str | None = None
    aliases_used: list[str] = field(default_factory=list)
    interpretation_note: str = ""


def _registry_span(canonical_id: str) -> tuple[int, int]:
    lo, hi = REGISTRY[canonical_id].sounding_range
    return int(lo), int(hi)


def _midi_to_note(midi: int) -> str:
    return midi_to_note_name(float(midi))


def _note_midi(note: str) -> float:
    return float(note_to_midi_strict(note))


def _band_midi(canonical_id: str, band: str) -> int:
    lo, hi = _registry_span(canonical_id)
    if band == "near_lower_boundary":
        return lo
    if band == "near_upper_boundary":
        return hi
    span = hi - lo
    fractions = {
        "low": 0.12,
        "low_mid": 0.30,
        "middle": 0.50,
        "upper_mid": 0.70,
        "high": 0.88,
    }
    return int(round(lo + span * fractions[band]))


def _note_in_range(note: str, canonical_id: str) -> bool:
    lo, hi = _registry_span(canonical_id)
    m = _note_midi(note)
    return lo - 1e-6 <= m <= hi + 1e-6


def _clamp_note_to_instrument(note: str, canonical_id: str) -> str:
    lo, hi = _registry_span(canonical_id)
    m = int(round(max(lo, min(hi, _note_midi(note)))))
    return _midi_to_note(m)


def _instrument_band_note(key: str, band: str) -> str:
    canonical = CANONICAL_INSTRUMENTS[key]["canonical_id"]
    midi = _band_midi(canonical, band)
    lo, hi = _registry_span(canonical)
    midi = max(lo, min(hi, midi))
    return _midi_to_note(midi)


def _trio_range_intersection() -> tuple[int, int]:
    ids = ("violino", "viola", "violoncelo")
    lo = max(_registry_span(i)[0] for i in ids)
    hi = min(_registry_span(i)[1] for i in ids)
    return lo, hi


def _all_instrument_keys() -> list[str]:
    return list(CANONICAL_INSTRUMENTS.keys())


def _canonical_names(keys: list[str]) -> list[str]:
    return [CANONICAL_INSTRUMENTS[k]["canonical_id"] for k in keys]


def _build_input(
    notes: list[str],
    dynamics: list[str],
    instrument_keys: list[str],
    quantities: list[int],
    *,
    alias_for_index: dict[int, str] | None = None,
) -> dict[str, Any]:
    inst_names = []
    aliases: list[str] = []
    for i, k in enumerate(instrument_keys):
        if alias_for_index and i in alias_for_index:
            name = alias_for_index[i]
            aliases.append(name)
        else:
            name = CANONICAL_INSTRUMENTS[k]["display"]
        inst_names.append(name)
    return {
        "notes": notes,
        "dynamics": dynamics,
        "instruments": inst_names,
        "num_instruments": quantities,
        "weight_factor": 0.5,
        "_aliases_used": aliases,
    }


def _extract_numeric(obj: Any, prefix: str = "") -> dict[str, float]:
    out: dict[str, float] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            out.update(_extract_numeric(v, p))
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if math.isfinite(float(obj)):
            out[prefix] = float(obj)
    return out


def _run_scenario(spec: ScenarioSpec) -> dict[str, Any]:
    row: dict[str, Any] = {
        "scenario_id": spec.scenario_id,
        "scenario_group": spec.scenario_group,
        "aggregate_type": spec.aggregate_type,
        "register_band": spec.register_band,
        "dynamic_profile": spec.dynamic_profile,
        "expected_validity": spec.expected_validity,
        "invariant_group_id": spec.invariant_group_id,
        "comparison_baseline_id": spec.comparison_baseline_id,
        "interpretation_note": spec.interpretation_note,
        "instruments": [],
        "canonical_instruments": [],
        "aliases_used": spec.aliases_used,
        "quantities": spec.quantities,
        "note_names": spec.notes,
        "midi_values": [],
        "pitch_classes": [],
        "per_event_dynamics": spec.dynamics,
        "global_dynamic": spec.dynamic_profile if len(set(spec.dynamics)) == 1 else None,
        "number_of_events": len(spec.notes),
        "total_quantity": sum(spec.quantities),
        "actual_status": "pending",
        "exception_type": None,
        "exception_message": None,
        "warnings": [],
        "provenance_status": None,
        "density_output_raw": None,
        "selected_density_metrics": {},
        "all_numeric_output_fields": {},
        "pass_fail": "PENDING",
    }

    try:
        midis = [_note_midi(n) for n in spec.notes]
        row["midi_values"] = midis
        row["pitch_classes"] = [int(round(m)) % 12 for m in midis]
        row["lowest_note"] = spec.notes[min(range(len(midis)), key=lambda i: midis[i])]
        row["highest_note"] = spec.notes[max(range(len(midis)), key=lambda i: midis[i])]
        row["registral_span_semitones"] = max(midis) - min(midis) if midis else 0.0
        row["unique_pitch_count"] = len({round(m, 6) for m in midis})
        row["pitch_class_count"] = len(set(row["pitch_classes"]))

        alias_map = {0: spec.aliases_used[0]} if spec.aliases_used else None
        input_data = _build_input(
            spec.notes, spec.dynamics, spec.instruments, spec.quantities,
            alias_for_index=alias_map,
        )
        row["aliases_used"] = list(spec.aliases_used) + input_data.pop("_aliases_used", [])
        row["instruments"] = input_data["instruments"]
        row["canonical_instruments"] = [
            resolve_profile(n).instrument_id if resolve_profile(n) else n
            for n in input_data["instruments"]
        ]

        resultados, densities, pitches = calculate_metrics(input_data)
        row["density_output_raw"] = resultados
        row["selected_density_metrics"] = {
            k: float(resultados["density"][k])
            for k in DENSITY_METRIC_KEYS
            if k in resultados.get("density", {})
        }
        row["all_numeric_output_fields"] = _extract_numeric(resultados)
        row["per_event_densities"] = [float(d) for d in densities]
        row["output_pitches"] = [float(p) for p in pitches]

        meta = resultados.get("metric_metadata", {})
        row["warnings"] = list(meta.get("warnings", []))
        row["provenance_status"] = meta.get("density.instrument.source_type")
        pa = resultados.get("pitch_aggregation", {})
        row["output_distinct_pitch_count"] = pa.get("distinct_pitch_count")
        row["output_event_count"] = pa.get("event_count")
        row["output_player_count"] = pa.get("player_count")

        if spec.expected_validity == "negative":
            row["actual_status"] = "unexpected_success"
            row["pass_fail"] = "FAIL"
            row["interpretation_note"] = (
                spec.interpretation_note or "Expected range validation failure."
            )
        else:
            finite = all(
                math.isfinite(v) for v in row["selected_density_metrics"].values()
            )
            if not finite:
                row["actual_status"] = "non_finite_output"
                row["pass_fail"] = "FAIL"
            else:
                row["actual_status"] = "success"
                row["pass_fail"] = "PASS"

    except InputError as exc:
        row["exception_type"] = type(exc).__name__
        row["exception_message"] = str(exc)
        if spec.expected_validity == "negative":
            row["actual_status"] = "expected_range_error"
            row["pass_fail"] = "PASS"
        else:
            row["actual_status"] = "error"
            row["pass_fail"] = "FAIL"
    except Exception as exc:
        row["exception_type"] = type(exc).__name__
        row["exception_message"] = str(exc)
        row["actual_status"] = "error"
        row["pass_fail"] = "FAIL"
        row["traceback"] = traceback.format_exc()

    return row


# ---------------------------------------------------------------------------
# Scenario generators
# ---------------------------------------------------------------------------

_counter = 0


def _sid(agg: str, band: str, dyn: str, parts: str, seq: int) -> str:
    return f"STRINGS_{agg}_{band}_{dyn}_{parts}_{seq:04d}"


def _next_id(agg: str, band: str, dyn: str, parts: str) -> str:
    global _counter
    _counter += 1
    return _sid(agg, band, dyn, parts, _counter)


def generate_positive_scenarios(rng: random.Random, target: int) -> list[ScenarioSpec]:
    specs: list[ScenarioSpec] = []
    keys = _all_instrument_keys()

    # 1. Single note — 4 × 6 × 7 = 168
    for key in keys:
        for band in REGISTER_BANDS:
            note = _instrument_band_note(key, band)
            for dyn in CAMPAIGN_DYNAMICS:
                specs.append(
                    ScenarioSpec(
                        scenario_id=_next_id("SINGLE", band.upper(), dyn.upper(), key.upper()),
                        scenario_group="single_note",
                        aggregate_type="single_note",
                        register_band=band,
                        dynamic_profile=dyn,
                        notes=[note],
                        dynamics=[dyn],
                        instruments=[key],
                        quantities=[1],
                        expected_validity="positive",
                    )
                )

    # 2. Exact unison across instruments (same sounding pitch, middle register)
    for dyn in CAMPAIGN_DYNAMICS:
        note = _instrument_band_note("viola", "middle")
        for n_inst in (2, 3, 4):
            inst_subset = keys[:n_inst]
            specs.append(
                ScenarioSpec(
                    scenario_id=_next_id("UNISON", "MID", dyn.upper(), f"N{n_inst}"),
                    scenario_group="exact_unison",
                    aggregate_type="exact_unison",
                    register_band="middle",
                    dynamic_profile=dyn,
                    notes=[note] * n_inst,
                    dynamics=[dyn] * n_inst,
                    instruments=inst_subset,
                    quantities=[1] * n_inst,
                    expected_validity="positive",
                )
            )

    # 3. Qty row-splitting pairs
    for dyn in ("pp", "mf", "ff"):
        note = _instrument_band_note("violin", "middle")
        base_id = _next_id("QTY_SPLIT", "MID", dyn.upper(), "VLN")
        specs.append(
            ScenarioSpec(
                scenario_id=base_id,
                scenario_group="quantity_row_splitting",
                aggregate_type="same_instrument_unison_qty",
                register_band="middle",
                dynamic_profile=dyn,
                notes=[note],
                dynamics=[dyn],
                instruments=["violin"],
                quantities=[4],
                expected_validity="positive",
                invariant_group_id=f"qty_split_{base_id}",
                interpretation_note="One row Qty=4 baseline for row-splitting invariant.",
            )
        )
        specs.append(
            ScenarioSpec(
                scenario_id=_next_id("QTY_SPLIT", "MID", dyn.upper(), "VLN4"),
                scenario_group="quantity_row_splitting",
                aggregate_type="same_instrument_unison_qty",
                register_band="middle",
                dynamic_profile=dyn,
                notes=[note] * 4,
                dynamics=[dyn] * 4,
                instruments=["violin"] * 4,
                quantities=[1, 1, 1, 1],
                expected_validity="positive",
                invariant_group_id=f"qty_split_{base_id}",
                comparison_baseline_id=base_id,
            )
        )

    # 4. Octave doubling
    for key in keys:
        base = _instrument_band_note(key, "low_mid")
        base_midi = int(round(_note_midi(base)))
        high = _midi_to_note(min(base_midi + 12, _registry_span(CANONICAL_INSTRUMENTS[key]["canonical_id"])[1]))
        for dyn in ("mp", "mf", "f"):
            specs.append(
                ScenarioSpec(
                    scenario_id=_next_id("OCTAVE", "LOWMID", dyn.upper(), key.upper()),
                    scenario_group="octave_doubling",
                    aggregate_type="octave_doubling",
                    register_band="low_mid",
                    dynamic_profile=dyn,
                    notes=[base, high],
                    dynamics=[dyn, dyn],
                    instruments=[key, key],
                    quantities=[1, 1],
                    expected_validity="positive",
                )
            )

    # 5. Compact dyad / trichord / cluster
    for key in keys:
        mid = int(round(_note_midi(_instrument_band_note(key, "middle"))))
        lo, hi = _registry_span(CANONICAL_INSTRUMENTS[key]["canonical_id"])
        for dyn in CAMPAIGN_DYNAMICS:
            dyad = [_midi_to_note(mid), _midi_to_note(min(mid + 1, hi))]
            specs.append(
                ScenarioSpec(
                    scenario_id=_next_id("DYAD", "MID", dyn.upper(), key.upper()),
                    scenario_group="compact_dyad",
                    aggregate_type="compact_dyad",
                    register_band="middle",
                    dynamic_profile=dyn,
                    notes=dyad,
                    dynamics=[dyn, dyn],
                    instruments=[key, key],
                    quantities=[1, 1],
                    expected_validity="positive",
                )
            )
            tri = [_midi_to_note(max(lo, mid - 1)), _midi_to_note(mid), _midi_to_note(min(mid + 1, hi))]
            specs.append(
                ScenarioSpec(
                    scenario_id=_next_id("TRICHORD", "MID", dyn.upper(), key.upper()),
                    scenario_group="compact_trichord",
                    aggregate_type="compact_trichord",
                    register_band="middle",
                    dynamic_profile=dyn,
                    notes=tri,
                    dynamics=[dyn] * 3,
                    instruments=[key] * 3,
                    quantities=[1, 1, 1],
                    expected_validity="positive",
                )
            )
            cluster_midis = list(range(max(lo, mid - 2), min(hi, mid + 2) + 1))
            cluster = [_midi_to_note(m) for m in cluster_midis[:6]]
            specs.append(
                ScenarioSpec(
                    scenario_id=_next_id("CLUSTER", "MID", dyn.upper(), key.upper()),
                    scenario_group="compact_chromatic_cluster",
                    aggregate_type="compact_chromatic_cluster",
                    register_band="middle",
                    dynamic_profile=dyn,
                    notes=cluster,
                    dynamics=[dyn] * len(cluster),
                    instruments=[key] * len(cluster),
                    quantities=[1] * len(cluster),
                    expected_validity="positive",
                )
            )

    # 6. Very dense chromatic — distribute across instruments by range
    for dyn in ("mf", "f", "ff"):
        midis = list(range(55, 65))
        notes = [_midi_to_note(m) for m in midis]
        inst_cycle = ["violin", "viola", "cello", "double_bass"]
        instruments = []
        for m in midis:
            note = _midi_to_note(m)
            for k in inst_cycle:
                cid = CANONICAL_INSTRUMENTS[k]["canonical_id"]
                if _note_in_range(note, cid):
                    instruments.append(k)
                    break
            else:
                instruments.append("viola")
        specs.append(
            ScenarioSpec(
                scenario_id=_next_id("VDENSE", "MID", dyn.upper(), "ALL4"),
                scenario_group="very_dense_chromatic",
                aggregate_type="very_dense_chromatic",
                register_band="middle",
                dynamic_profile=dyn,
                notes=notes,
                dynamics=[dyn] * len(notes),
                instruments=instruments,
                quantities=[1] * len(notes),
                expected_validity="positive",
            )
        )

    # 7. Diatonic / sparse / very sparse
    diatonic = ["C4", "D4", "E4", "F4", "G4"]
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("DIATONIC", "MID", "MF", "MIX"),
            scenario_group="diatonic_aggregate",
            aggregate_type="diatonic_aggregate",
            register_band="middle",
            dynamic_profile="mf",
            notes=diatonic,
            dynamics=["mf"] * 5,
            instruments=["violin", "viola", "cello", "double_bass", "violin"],
            quantities=[1] * 5,
            expected_validity="positive",
        )
    )
    sparse = ["G2", "D4", "A5"]
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("SPARSE", "WIDE", "MF", "MIX"),
            scenario_group="sparse_aggregate",
            aggregate_type="sparse_aggregate",
            register_band="middle",
            dynamic_profile="mf",
            notes=sparse,
            dynamics=["mf"] * 3,
            instruments=["double_bass", "viola", "violin"],
            quantities=[1, 1, 1],
            expected_validity="positive",
        )
    )
    very_sparse = ["E1", "G3", "C5", "G7"]
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("VSPARSE", "WIDE", "MF", "ALL4"),
            scenario_group="very_sparse_aggregate",
            aggregate_type="very_sparse_aggregate",
            register_band="low",
            dynamic_profile="mf",
            notes=very_sparse,
            dynamics=["mf"] * 4,
            instruments=["double_bass", "viola", "cello", "violin"],
            quantities=[1, 1, 1, 1],
            expected_validity="positive",
        )
    )

    # 8. Registrally stratified / heterogeneous / sectional / quartet
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("STRATIFIED", "LOWHIGH", "MF", "ALL4"),
            scenario_group="registrally_stratified",
            aggregate_type="registrally_stratified",
            register_band="low",
            dynamic_profile="mf",
            notes=["E1", "C2", "G3", "E5"],
            dynamics=["mf"] * 4,
            instruments=["double_bass", "cello", "viola", "violin"],
            quantities=[1, 1, 1, 1],
            expected_validity="positive",
        )
    )
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("HETEROG", "MID", "MF", "ALL4"),
            scenario_group="heterogeneous_string",
            aggregate_type="heterogeneous_string",
            register_band="middle",
            dynamic_profile="mf",
            notes=["G4", "D4", "C3", "G2"],
            dynamics=["mf"] * 4,
            instruments=keys,
            quantities=[1, 1, 1, 1],
            expected_validity="positive",
        )
    )
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("SECTION", "MID", "MF", "8284"),
            scenario_group="sectional_string",
            aggregate_type="sectional_string",
            register_band="middle",
            dynamic_profile="mf",
            notes=["G4", "D4", "C3", "G2"],
            dynamics=["mf"] * 4,
            instruments=keys,
            quantities=[8, 6, 4, 2],
            expected_validity="positive",
        )
    )
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("QUARTET", "MID", "MF", "2211"),
            scenario_group="quartet_voicing",
            aggregate_type="quartet_voicing",
            register_band="middle",
            dynamic_profile="mf",
            notes=["E5", "G4", "C4", "G2"],
            dynamics=["mf"] * 4,
            instruments=["violin", "violin", "viola", "double_bass"],
            quantities=[1, 1, 1, 1],
            expected_validity="positive",
        )
    )

    # 9. Cluster + octave / low mass / high mass
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("CLUSTOCT", "MID", "F", "MIX"),
            scenario_group="cluster_plus_octave",
            aggregate_type="cluster_plus_octave",
            register_band="middle",
            dynamic_profile="f",
            notes=["G3", "G4", "Ab3", "Ab4", "A3"],
            dynamics=["f"] * 5,
            instruments=["cello", "violin", "cello", "violin", "viola"],
            quantities=[1] * 5,
            expected_validity="positive",
        )
    )
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("LOWMASS", "LOW", "MF", "VCDB"),
            scenario_group="low_register_mass",
            aggregate_type="low_register_mass",
            register_band="low",
            dynamic_profile="mf",
            notes=["E1", "A1", "C2", "G2"],
            dynamics=["mf"] * 4,
            instruments=["double_bass", "double_bass", "cello", "double_bass"],
            quantities=[2, 2, 2, 2],
            expected_validity="positive",
        )
    )
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("HIGHMASS", "HIGH", "MF", "VLVA"),
            scenario_group="high_register_mass",
            aggregate_type="high_register_mass",
            register_band="high",
            dynamic_profile="mf",
            notes=["A5", "E5", "C6", "G6"],
            dynamics=["mf"] * 4,
            instruments=["violin", "violin", "viola", "violin"],
            quantities=[3, 3, 2, 2],
            expected_validity="positive",
        )
    )

    # 10. Mixed / cross-dynamic
    base_notes = ["G3", "D4", "B4"]
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("MIXDYN", "MID", "MIXED", "TRIO"),
            scenario_group="mixed_dynamics",
            aggregate_type="mixed_dynamics",
            register_band="middle",
            dynamic_profile="mixed",
            notes=base_notes,
            dynamics=["pp", "mf", "ff"],
            instruments=["violin", "viola", "cello"],
            quantities=[1, 1, 1],
            expected_validity="positive",
        )
    )
    for dyn in ("pp", "mp", "mf", "f", "ff"):
        specs.append(
            ScenarioSpec(
                scenario_id=_next_id("XDYN", "MID", dyn.upper(), "TRIO"),
                scenario_group="cross_dynamic_comparison",
                aggregate_type="cross_dynamic_comparison",
                register_band="middle",
                dynamic_profile=dyn,
                notes=base_notes,
                dynamics=[dyn] * 3,
                instruments=["violin", "viola", "cello"],
                quantities=[1, 1, 1],
                expected_validity="positive",
                invariant_group_id="cross_dynamic_trio",
            )
        )

    # 11. Instrument substitution (same pitches, different assignments)
    pitches = ["G4", "D4"]
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("SUBST", "MID", "MF", "VLN"),
            scenario_group="instrument_substitution",
            aggregate_type="instrument_substitution",
            register_band="middle",
            dynamic_profile="mf",
            notes=pitches,
            dynamics=["mf", "mf"],
            instruments=["violin", "violin"],
            quantities=[1, 1],
            expected_validity="positive",
            invariant_group_id="subst_g4_d4",
        )
    )
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("SUBST", "MID", "MF", "VLA"),
            scenario_group="instrument_substitution",
            aggregate_type="instrument_substitution",
            register_band="middle",
            dynamic_profile="mf",
            notes=pitches,
            dynamics=["mf", "mf"],
            instruments=["viola", "viola"],
            quantities=[1, 1],
            expected_validity="positive",
            invariant_group_id="subst_g4_d4",
        )
    )

    # 12. Quantity scaling
    note = _instrument_band_note("violin", "middle")
    for qty in (1, 2, 4, 8, 12):
        specs.append(
            ScenarioSpec(
                scenario_id=_next_id("QTYSCALE", "MID", "MF", f"Q{qty}"),
                scenario_group="quantity_scaling",
                aggregate_type="quantity_scaling",
                register_band="middle",
                dynamic_profile="mf",
                notes=[note],
                dynamics=["mf"],
                instruments=["violin"],
                quantities=[qty],
                expected_validity="positive",
                invariant_group_id="qty_scale_vln_g4",
            )
        )

    # 13. Event-order / pitch-collection invariance
    trio_notes = ["C4", "E4", "G4"]
    trio_inst = ["violin", "viola", "cello"]
    base_order_id = _next_id("EVORDER", "MID", "MF", "BASE")
    specs.append(
        ScenarioSpec(
            scenario_id=base_order_id,
            scenario_group="event_order_invariance",
            aggregate_type="event_order_invariance",
            register_band="middle",
            dynamic_profile="mf",
            notes=trio_notes,
            dynamics=["mf"] * 3,
            instruments=trio_inst,
            quantities=[1, 1, 1],
            expected_validity="positive",
            invariant_group_id="event_order_trio",
        )
    )
    perm = ["G4", "C4", "E4"]
    specs.append(
        ScenarioSpec(
            scenario_id=_next_id("EVORDER", "MID", "MF", "PERM"),
            scenario_group="event_order_invariance",
            aggregate_type="event_order_invariance",
            register_band="middle",
            dynamic_profile="mf",
            notes=perm,
            dynamics=["mf", "mf", "mf"],
            instruments=["cello", "violin", "viola"],
            quantities=[1, 1, 1],
            expected_validity="positive",
            invariant_group_id="event_order_trio",
            comparison_baseline_id=base_order_id,
        )
    )

    # 14. Register shift comparison (notes must fit violin, viola, cello together)
    shape = [0, 4, 7]
    trio_lo, trio_hi = _trio_range_intersection()
    for band, label in (("low", "LOW"), ("middle", "MID"), ("high", "HIGH")):
        root_midi = int(round(_note_midi(_instrument_band_note("viola", band))))
        root_midi = max(trio_lo, min(trio_hi - max(shape), root_midi))
        notes = [_midi_to_note(max(trio_lo, min(trio_hi, root_midi + s))) for s in shape]
        specs.append(
            ScenarioSpec(
                scenario_id=_next_id("REGSHIFT", label, "MF", "TRIAD"),
                scenario_group="register_shift_comparison",
                aggregate_type="register_shift_comparison",
                register_band=band,
                dynamic_profile="mf",
                notes=notes,
                dynamics=["mf"] * 3,
                instruments=["violin", "viola", "cello"],
                quantities=[1, 1, 1],
                expected_validity="positive",
                invariant_group_id="register_shift_triad",
            )
        )

    # 15. Pairs and trios — stratified sampling to fill toward target
    for pair in combinations(keys, 2):
        for dyn in ("mp", "mf"):
            n1 = _instrument_band_note(pair[0], "middle")
            n2 = _instrument_band_note(pair[1], "middle")
            specs.append(
                ScenarioSpec(
                    scenario_id=_next_id("PAIR", "MID", dyn.upper(), "_".join(p[:3].upper() for p in pair)),
                    scenario_group="pair_combination",
                    aggregate_type="heterogeneous_string",
                    register_band="middle",
                    dynamic_profile=dyn,
                    notes=[n1, n2],
                    dynamics=[dyn, dyn],
                    instruments=list(pair),
                    quantities=[1, 1],
                    expected_validity="positive",
                )
            )

    for trio in combinations(keys, 3):
        dyn = "mf"
        notes = [_instrument_band_note(k, "middle") for k in trio]
        specs.append(
            ScenarioSpec(
                scenario_id=_next_id("TRIO", "MID", "MF", "_".join(t[:2].upper() for t in trio)),
                scenario_group="trio_combination",
                aggregate_type="heterogeneous_string",
                register_band="middle",
                dynamic_profile=dyn,
                notes=notes,
                dynamics=[dyn] * 3,
                instruments=list(trio),
                quantities=[1, 1, 1],
                expected_validity="positive",
            )
        )

    # 16. Alias validation subset
    for key in keys:
        dyn = "mf"
        note = _instrument_band_note(key, "middle")
        specs.append(
            ScenarioSpec(
                scenario_id=_next_id("ALIAS", "MID", "MF", key.upper()),
                scenario_group="alias_validation",
                aggregate_type="single_note",
                register_band="middle",
                dynamic_profile=dyn,
                notes=[note],
                dynamics=[dyn],
                instruments=[key],
                quantities=[1],
                expected_validity="positive",
                aliases_used=[CANONICAL_INSTRUMENTS[key]["alias"]],
            )
        )

    # Deduplicate by scenario_id and trim/sample to at least target
    seen: set[str] = set()
    unique: list[ScenarioSpec] = []
    for s in specs:
        if s.scenario_id not in seen:
            seen.add(s.scenario_id)
            unique.append(s)

    if len(unique) < target:
        raise RuntimeError(f"Generator produced only {len(unique)} scenarios; need {target}")

    rng.shuffle(unique)
    return unique[: max(target, len(unique))]


def generate_negative_scenarios(count: int) -> list[ScenarioSpec]:
    specs: list[ScenarioSpec] = []
    cases = [
        ("violin", "G2", "below violin low"),
        ("violin", "A7", "above violin high"),
        ("viola", "B2", "below viola low"),
        ("viola", "D7", "above viola high"),
        ("cello", "B1", "below cello low"),
        ("cello", "D6", "above cello high"),
        ("double_bass", "D0", "below bass low"),
        ("double_bass", "D5", "above bass high"),
    ]
    for i, (key, note, note_text) in enumerate(cases):
        for dyn in ("pp", "mf", "ff")[: max(1, count // len(cases) + 1)]:
            if len(specs) >= count:
                break
            specs.append(
                ScenarioSpec(
                    scenario_id=_next_id("NEG_RANGE", "OOR", dyn.upper(), key.upper()),
                    scenario_group="negative_out_of_range",
                    aggregate_type="negative_out_of_range",
                    register_band="out_of_range",
                    dynamic_profile=dyn,
                    notes=[note],
                    dynamics=[dyn],
                    instruments=[key],
                    quantities=[1],
                    expected_validity="negative",
                    interpretation_note=note_text,
                )
            )
        if len(specs) >= count:
            break
    while len(specs) < count:
        specs.append(
            ScenarioSpec(
                scenario_id=_next_id("NEG_RANGE", "OOR", "MF", f"X{len(specs)}"),
                scenario_group="negative_out_of_range",
                aggregate_type="negative_out_of_range",
                register_band="out_of_range",
                dynamic_profile="mf",
                notes=["C1"],
                dynamics=["mf"],
                instruments=["violin"],
                quantities=[1],
                expected_validity="negative",
                interpretation_note="Generic below-range violin C1.",
            )
        )
    return specs[:count]


def check_invariants(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {r["scenario_id"]: r for r in results}
    checks: list[dict[str, Any]] = []

    # Event-order invariance
    groups: dict[str, list[dict]] = {}
    for r in results:
        gid = r.get("invariant_group_id")
        if gid and r.get("aggregate_type") == "event_order_invariance":
            groups.setdefault(gid, []).append(r)
    for gid, rows in groups.items():
        passed = True
        detail = ""
        if len(rows) >= 2:
            m0 = rows[0].get("selected_density_metrics", {})
            m1 = rows[1].get("selected_density_metrics", {})
            for k in ("pitch_structure", "interval"):
                v0, v1 = m0.get(k), m1.get(k)
                if v0 is None or v1 is None or abs(v0 - v1) > 1e-6:
                    passed = False
                    detail = f"{k} differs: {v0} vs {v1}"
        checks.append(
            {
                "check": "event_order_invariance",
                "group_id": gid,
                "pass_fail": "PASS" if passed else "FAIL",
                "detail": detail or "pitch_structure and interval matched",
            }
        )

    # Qty row-splitting
    qty_groups: dict[str, list[dict]] = {}
    for r in results:
        gid = r.get("invariant_group_id")
        if gid and "qty_split" in str(gid):
            qty_groups.setdefault(gid, []).append(r)
    for gid, rows in qty_groups.items():
        passed = True
        detail = ""
        if len(rows) >= 2:
            s0 = rows[0].get("selected_density_metrics", {}).get("sonic_mass")
            s1 = rows[1].get("selected_density_metrics", {}).get("sonic_mass")
            if s0 is None or s1 is None or abs(s0 - s1) > 1e-4:
                passed = False
                detail = f"sonic_mass differs: {s0} vs {s1}"
        checks.append(
            {
                "check": "quantity_row_splitting",
                "group_id": gid,
                "pass_fail": "PASS" if passed else "FAIL",
                "detail": detail or "sonic_mass matched",
            }
        )

    # Unison distinct pitch count
    for r in results:
        if r.get("aggregate_type") == "exact_unison" and r.get("pass_fail") == "PASS":
            dpc = r.get("output_distinct_pitch_count")
            ok = dpc == 1
            checks.append(
                {
                    "check": "unison_distinct_pitch",
                    "scenario_id": r["scenario_id"],
                    "pass_fail": "PASS" if ok else "FAIL",
                    "detail": f"distinct_pitch_count={dpc}",
                }
            )

    # Octave doubling
    for r in results:
        if r.get("aggregate_type") == "octave_doubling" and r.get("pass_fail") == "PASS":
            dpc = r.get("output_distinct_pitch_count")
            ok = dpc is not None and dpc >= 2
            checks.append(
                {
                    "check": "octave_distinct_pitch",
                    "scenario_id": r["scenario_id"],
                    "pass_fail": "PASS" if ok else "FAIL",
                    "detail": f"distinct_pitch_count={dpc}",
                }
            )

    return checks


def _stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0, "max": 0, "mean": 0, "median": 0, "stdev": 0}
    vals = sorted(values)
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    mid = n // 2
    median = vals[mid] if n % 2 else (vals[mid - 1] + vals[mid]) / 2
    return {
        "min": vals[0],
        "max": vals[-1],
        "mean": mean,
        "median": median,
        "stdev": math.sqrt(var),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    flat_keys: set[str] = set()
    for r in rows:
        flat_keys.update(r.keys())
        for k, v in r.get("selected_density_metrics", {}).items():
            flat_keys.add(f"density.{k}")
    # flatten for CSV
    flat_rows = []
    for r in rows:
        fr = {k: v for k, v in r.items() if k not in ("density_output_raw", "all_numeric_output_fields", "traceback")}
        for k, v in r.get("selected_density_metrics", {}).items():
            fr[f"density.{k}"] = v
        for k in ("warnings", "note_names", "midi_values", "instruments", "canonical_instruments", "quantities", "per_event_dynamics"):
            if k in fr and isinstance(fr[k], list):
                fr[k] = json.dumps(fr[k])
        flat_rows.append(fr)
    fieldnames = sorted({k for fr in flat_rows for k in fr.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(flat_rows)


def write_markdown(
    path: Path,
    *,
    sha: str,
    summary: dict[str, Any],
    results: list[dict[str, Any]],
    invariants: list[dict[str, Any]],
) -> None:
    pos = [r for r in results if r["expected_validity"] == "positive"]
    neg = [r for r in results if r["expected_validity"] == "negative"]
    inst_dens = _stats(
        [r["selected_density_metrics"].get("instrument", 0) for r in pos if r.get("selected_density_metrics")]
    )

    lines = [
        "# String density scenario validation report",
        "",
        f"**Date (UTC):** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Repository SHA:** `{sha}`",
        "",
        "## Scope",
        "",
        "- Strings only: violin, viola, cello, double bass",
        "- Sounding/concert pitch only (double bass uses sounding notes, e.g. E1 not written octave)",
        "- Score-grounded symbolic density model",
        "- **Not** perceptual validation",
        "",
        "## API",
        "",
        "`core.pipeline.calculate_metrics` with legacy dict input (`notes`, `dynamics`, `instruments`, `num_instruments`, `weight_factor`).",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
    ]
    for k, v in summary.items():
        lines.append(f"| {k} | {v} |")

    lines.extend(
        [
            "",
            "## Instrument ranges (registry sounding_range)",
            "",
        ]
    )
    for key, cfg in CANONICAL_INSTRUMENTS.items():
        lo, hi = _registry_span(cfg["canonical_id"])
        lines.append(f"- **{key}:** MIDI {lo}–{hi}")

    lines.extend(
        [
            "",
            "## Dynamics",
            "",
            ", ".join(CAMPAIGN_DYNAMICS),
            f" (source anchors: {', '.join(sorted(SOURCE_ANCHOR_DYNAMICS))})",
            "",
            "## Aggregate types",
            "",
            ", ".join(AGGREGATE_TYPES),
            "",
            "## Positive scenario summary",
            "",
            f"- Total: {len(pos)}",
            f"- Passed: {sum(1 for r in pos if r['pass_fail'] == 'PASS')}",
            f"- Failed: {sum(1 for r in pos if r['pass_fail'] == 'FAIL')}",
            "",
            "## Negative scenario summary",
            "",
            f"- Total: {len(neg)}",
            f"- Passed (clean failure): {sum(1 for r in neg if r['pass_fail'] == 'PASS')}",
            f"- Failed: {sum(1 for r in neg if r['pass_fail'] == 'FAIL')}",
            "",
            "## Density statistics (instrument density, positive scenarios)",
            "",
            f"- min: {inst_dens['min']:.6f}",
            f"- max: {inst_dens['max']:.6f}",
            f"- mean: {inst_dens['mean']:.6f}",
            f"- median: {inst_dens['median']:.6f}",
            f"- stdev: {inst_dens['stdev']:.6f}",
            "",
            "## Invariant checks",
            "",
        ]
    )
    for c in invariants:
        lines.append(f"- **{c['check']}** ({c.get('group_id') or c.get('scenario_id')}): {c['pass_fail']} — {c.get('detail', '')}")

    anomalies = [r for r in results if r["pass_fail"] == "FAIL" or r.get("warnings")]
    lines.extend(["", "## Anomalies", ""])
    if not anomalies:
        lines.append("No significant anomalies detected.")
    else:
        for r in anomalies[:30]:
            lines.append(
                f"- `{r['scenario_id']}`: {r['pass_fail']} status={r['actual_status']} warnings={len(r.get('warnings', []))}"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Results demonstrate internal consistency of the string density pipeline under controlled",
            "symbolic scenarios. They do not validate perceptual density or empirical listening outcomes.",
            "",
            "## Files",
            "",
            "- `reports/string_density_scenario_validation.json`",
            "- `reports/string_density_scenario_validation.csv`",
            "- `reports/string_density_scenario_validation_summary.json`",
            "",
            f"## Conclusion: **{summary.get('campaign_conclusion', 'PENDING')}**",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_campaign(
    *,
    positive: int,
    negative: int,
    seed: int,
    output_prefix: Path,
    include_timestamp: bool = True,
) -> dict[str, Any]:
    global _counter
    _counter = 0
    rng = random.Random(seed)

    specs = generate_positive_scenarios(rng, positive) + generate_negative_scenarios(negative)
    results = [_run_scenario(s) for s in specs]
    invariants = check_invariants(results)

    pos = [r for r in results if r["expected_validity"] == "positive"]
    neg = [r for r in results if r["expected_validity"] == "negative"]
    inv_fail = sum(1 for c in invariants if c["pass_fail"] == "FAIL")
    scenario_fail = sum(1 for r in results if r["pass_fail"] == "FAIL")

    try:
        import subprocess

        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        sha = "unknown"

    summary = {
        "repository_sha": sha,
        "seed": seed,
        "scenarios_generated": len(specs),
        "scenarios_executed": len(results),
        "positive_scenarios": len(pos),
        "negative_scenarios": len(neg),
        "scenarios_passed": sum(1 for r in results if r["pass_fail"] == "PASS"),
        "scenarios_failed": scenario_fail,
        "invariant_checks": len(invariants),
        "invariant_failures": inv_fail,
        "warnings_count": sum(len(r.get("warnings", [])) for r in results),
        "instruments_covered": list(CANONICAL_INSTRUMENTS.keys()),
        "dynamics_covered": list(CAMPAIGN_DYNAMICS),
        "register_bands_covered": list(REGISTER_BANDS),
        "aggregate_types_covered": sorted({r["aggregate_type"] for r in results}),
        "campaign_conclusion": "PASS" if scenario_fail == 0 and inv_fail == 0 else "REVIEW REQUIRED",
    }

    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat() if include_timestamp else None,
            "repository_sha": sha,
            "seed": seed,
            "api": "core.pipeline.calculate_metrics",
            "pitch_convention": "sounding_concert_pitch",
        },
        "summary": summary,
        "invariant_checks": invariants,
        "scenarios": results,
    }

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix(".json")
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    write_csv(output_prefix.with_suffix(".csv"), results)
    write_markdown(
        output_prefix.with_suffix(".md"),
        sha=sha,
        summary=summary,
        results=results,
        invariants=invariants,
    )
    summary_path = output_prefix.parent / "string_density_scenario_validation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return payload


def compare_determinism(path1: Path, path2: Path, *, float_tol: float = 1e-5) -> dict[str, Any]:
    d1 = json.loads(path1.read_text(encoding="utf-8"))
    d2 = json.loads(path2.read_text(encoding="utf-8"))

    skip_keys = {"density_output_raw", "all_numeric_output_fields", "traceback"}

    def normalize_row(s: dict) -> dict:
        row = {k: v for k, v in s.items() if k not in skip_keys}
        return row

    r1 = [normalize_row(s) for s in d1["scenarios"]]
    r2 = [normalize_row(s) for s in d2["scenarios"]]

    if len(r1) != len(r2):
        return {
            "deterministic_match": False,
            "reason": "scenario_count_mismatch",
            "scenario_count_1": len(r1),
            "scenario_count_2": len(r2),
        }

    mismatches: list[str] = []
    for a, b in zip(r1, r2):
        if a.get("scenario_id") != b.get("scenario_id"):
            mismatches.append(f"id:{a.get('scenario_id')} vs {b.get('scenario_id')}")
            continue
        for key in ("pass_fail", "actual_status", "output_distinct_pitch_count"):
            if a.get(key) != b.get(key):
                mismatches.append(f"{a['scenario_id']}:{key}")
        m1 = a.get("selected_density_metrics") or {}
        m2 = b.get("selected_density_metrics") or {}
        for k in set(m1) | set(m2):
            v1, v2 = m1.get(k), m2.get(k)
            if v1 is None and v2 is None:
                continue
            if not isinstance(v1, (int, float)) or not isinstance(v2, (int, float)):
                if v1 != v2:
                    mismatches.append(f"{a['scenario_id']}:metric.{k}")
            elif abs(float(v1) - float(v2)) > float_tol:
                mismatches.append(f"{a['scenario_id']}:metric.{k} delta={abs(float(v1)-float(v2))}")

    return {
        "deterministic_match": len(mismatches) == 0,
        "float_tolerance": float_tol,
        "scenario_count_1": len(r1),
        "scenario_count_2": len(r2),
        "mismatch_count": len(mismatches),
        "mismatch_samples": mismatches[:10],
        "note": "GPR interpolation may exhibit tiny floating-point drift between runs; tolerance applied.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="String density scenario validation campaign")
    parser.add_argument("--positive", type=int, default=300)
    parser.add_argument("--negative", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260625)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "string_density_scenario_validation",
    )
    parser.add_argument("--determinism-check", action="store_true")
    args = parser.parse_args()

    out = args.output
    payload = run_campaign(
        positive=args.positive,
        negative=args.negative,
        seed=args.seed,
        output_prefix=out,
    )

    exit_code = 0
    if payload["summary"]["scenarios_failed"] > 0:
        exit_code = 1
    if payload["summary"]["invariant_failures"] > 0:
        exit_code = 1

    if args.determinism_check:
        import shutil

        run1_path = out.parent / "string_density_scenario_validation_run1.json"
        shutil.copy2(out.with_suffix(".json"), run1_path)
        run2_prefix = out.parent / "string_density_scenario_validation_run2"
        run_campaign(
            positive=args.positive,
            negative=args.negative,
            seed=args.seed,
            output_prefix=run2_prefix,
            include_timestamp=False,
        )
        diff = compare_determinism(run1_path, run2_prefix.with_suffix(".json"))
        diff_path = out.parent / "string_density_scenario_validation_determinism.json"
        diff_path.write_text(json.dumps(diff, indent=2), encoding="utf-8")
        print(json.dumps(diff, indent=2))
        if not diff["deterministic_match"]:
            exit_code = 1

    print(json.dumps(payload["summary"], indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
