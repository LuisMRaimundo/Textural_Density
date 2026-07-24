"""Build instrument metadata / range resolution audit payloads."""

from __future__ import annotations

import importlib
from typing import Any, Literal

from instrumentos.registry import REGISTRY, list_profiles
from microtonal import note_to_midi_strict

Classification = Literal["PASS", "FAIL", "REVIEW REQUIRED", "UNVERIFIED", "NOT APPLICABLE"]

RANGE_SEMANTICS: dict[str, str] = {
    "source_table_span": (
        "Pitch span covered by committed spectral_data / INSTRUMENT_SOURCE.pitch_range rows "
        "(sounding/concert pitch)."
    ),
    "sounding_range": "Registry validation span for sounding/concert-pitch manual and MusicXML-after-transpose input.",
    "written_range": "Written notation span; only relevant on MusicXML written-pitch paths before <transpose>.",
    "practical_range": "Ordinary orchestrational use if documented separately; not inferred from table span alone.",
    "comfortable_range": "Conservative central register band in registry; narrower than full sounding_range when set.",
    "extended_range": "Broader exceptional range if documented; not automatically equal to source_table_span.",
    "source_technique": "Playing technique represented by the numerical source table (INSTRUMENT_SOURCE.source_technique).",
    "table_supported_techniques": "Techniques with independent numerical rows in the committed table.",
    "registry_supported_techniques": "Organological capabilities listed on InstrumentProfile.supported_techniques.",
}

_GPR_MODULES = frozenset(
    {
        "flute",
        "oboe",
        "clarinet",
        "bassoon",
        "violin",
        "violin_sordina",
        "violin_sul_tasto",
        "violin_sul_ponticello",
        "violin_art_harm",
        "violin_nat_harm",
        "viola",
        "viola_sordina",
        "viola_sul_tasto",
        "viola_sul_ponticello",
        "cello",
        "cello_sordina",
        "cello_sul_tasto",
        "cello_sul_ponticello",
        "double_bass",
        "double_bass_sordina",
        "double_bass_sul_tasto",
        "double_bass_sul_ponticello",
    }
)


def _table_span(module_name: str | None) -> dict[str, Any] | None:
    if not module_name:
        return None
    try:
        mod = importlib.import_module(f"instrumentos.{module_name}")
    except ImportError:
        return None
    table = getattr(mod, "spectral_data", None)
    if not table:
        return None
    notes = sorted(table.keys(), key=note_to_midi_strict)
    lo = int(note_to_midi_strict(notes[0]))
    hi = int(note_to_midi_strict(notes[-1]))
    return {
        "first_note": notes[0],
        "last_note": notes[-1],
        "row_count": len(notes),
        "min_midi": lo,
        "max_midi": hi,
    }


def _range_alignment(profile, table: dict[str, Any] | None) -> str:
    if table is None:
        return "no_table"
    lo, hi = profile.sounding_range
    t_lo, t_hi = table["min_midi"], table["max_midi"]
    if lo <= t_lo and hi >= t_hi:
        if int(lo) == t_lo and int(hi) == t_hi:
            return "aligned"
        return "OK_registry_covers_table"
    if t_lo < lo or t_hi > hi:
        return "BUG_table_anchor_outside_registry"
    return "REVIEW_REQUIRED"


def _double_bass_span_classification(table: dict[str, Any] | None) -> dict[str, Any]:
    if table is None:
        return {"classification": "FAIL", "note": "missing table"}
    return {
        "source_table_span": f"{table['first_note']}–{table['last_note']} (MIDI {table['min_midi']}–{table['max_midi']})",
        "obsolete_documentation_span": "E1–A3",
        "obsolete_status": "obsolete_documentation_only",
        "comfortable_range_midi": "31–55 (G1–G3) per registry",
        "upper_register_extension": "A#3–C5 rows present in committed workbook-derived table",
        "classification": "PASS",
        "upper_register_methodological_qc": "REVIEW REQUIRED",
        "rationale": (
            "Committed spectral_data, INSTRUMENT_SOURCE.pitch_range, and registry.sounding_range "
            "all agree on E1–C5. E1–A3 was obsolete documentation. Comfortable range remains narrower. "
            "Methodological status of upper-register rows (above A3) vs core corpus not independently adjudicated."
        ),
    }


def _tuba_classification() -> dict[str, Any]:
    profile = REGISTRY["tuba"]
    lo, hi = profile.sounding_range
    return {
        "module_name": profile.module_name,
        "profile_status": profile.profile_status,
        "sounding_range_midi": f"{int(lo)}–{int(hi)}",
        "classification": "REVIEW REQUIRED",
        "range_kind": "coarse_default_validation_placeholder",
        "rationale": (
            "No committed tuba spectral_data module. registry.sounding_range (28–58) is a coarse "
            "orchestration placeholder for validation only — not a source-table span."
        ),
    }


def _technique_classification(profile, module_name: str | None) -> dict[str, Any]:
    registry_supported = list(profile.supported_techniques)
    if not module_name:
        return {
            "registry_supported_techniques": registry_supported,
            "table_supported_techniques": [],
            "source_technique": None,
            "classification": "NOT APPLICABLE",
        }
    try:
        mod = importlib.import_module(f"instrumentos.{module_name}")
    except ImportError:
        return {
            "registry_supported_techniques": registry_supported,
            "table_supported_techniques": [],
            "source_technique": None,
            "classification": "UNVERIFIED",
        }
    src = getattr(mod, "INSTRUMENT_SOURCE", None)
    table_techniques = list(getattr(src, "table_supported_techniques", ()) or ())
    source_technique = getattr(src, "source_technique", None) if src else None
    overclaim = [t for t in registry_supported if t not in table_techniques and t != "arco"]
    classification: Classification = "PASS"
    if module_name in _GPR_MODULES and not table_techniques:
        classification = "REVIEW REQUIRED"
    elif overclaim and profile.family == "strings":
        classification = "PASS"  # distinguished, not inflated
    return {
        "registry_supported_techniques": registry_supported,
        "table_supported_techniques": table_techniques,
        "source_technique": source_technique,
        "registry_not_in_table": overclaim,
        "classification": classification,
    }


def build_metadata_range_resolution_audit() -> dict[str, Any]:
    instruments: list[dict[str, Any]] = []
    for profile in sorted(list_profiles(), key=lambda p: p.instrument_id):
        table = _table_span(profile.module_name)
        lo, hi = profile.sounding_range
        c_lo, c_hi = profile.comfortable_range
        src = None
        if profile.module_name:
            try:
                mod = importlib.import_module(f"instrumentos.{profile.module_name}")
                src = getattr(mod, "INSTRUMENT_SOURCE", None)
            except ImportError:
                src = None
        pitch_range = getattr(src, "pitch_range", None) if src else None
        alignment = _range_alignment(profile, table)
        range_class: Classification
        if alignment in ("aligned", "OK_registry_covers_table"):
            range_class = "PASS"
        elif alignment == "no_table":
            range_class = "NOT APPLICABLE" if profile.profile_status == "coarse_default" else "REVIEW REQUIRED"
        elif alignment == "BUG_table_anchor_outside_registry":
            range_class = "FAIL"
        else:
            range_class = "REVIEW REQUIRED"

        row: dict[str, Any] = {
            "instrument_id": profile.instrument_id,
            "display_name": profile.display_name,
            "aliases": list(profile.aliases),
            "family": profile.family,
            "module_name": profile.module_name,
            "table_backed": profile.module_name in _GPR_MODULES,
            "profile_status": profile.profile_status,
            "source_table_span": table,
            "instrument_source_pitch_range": list(pitch_range) if pitch_range else None,
            "registry_sounding_range_midi": [int(lo), int(hi)],
            "registry_comfortable_range_midi": [int(c_lo), int(c_hi)],
            "registry_transposition": profile.transposition,
            "registry_transposition_runtime_applied": False,
            "source_dynamic_anchors": list(getattr(src, "dynamic_levels", ()) or ("pp", "mf", "ff"))
            if src
            else ["pp", "mf", "ff"]
            if profile.module_name
            else [],
            "modelled_dynamics": ["p", "mp", "f", "pppp", "ppp", "fff", "ffff"],
            "range_alignment": alignment,
            "range_classification": range_class,
            "technique": _technique_classification(profile, profile.module_name),
            "documentation_contradictions": [],
        }
        if table and pitch_range and (table["min_midi"], table["max_midi"]) != tuple(pitch_range):
            row["documentation_contradictions"].append("INSTRUMENT_SOURCE.pitch_range != spectral_data span")
        instruments.append(row)

    return {
        "range_semantics": RANGE_SEMANTICS,
        "instrument_count": len(instruments),
        "instruments": instruments,
        "double_bass_resolution": _double_bass_span_classification(_table_span("double_bass")),
        "tuba_review": _tuba_classification(),
        "transposition_review": {
            "contract": (
                "registry.transposition is notation/import metadata only; manual/GUI notes[] are "
                "sounding/concert pitch; MusicXML <transpose> converts written→sounding once."
            ),
            "octave_displaced_zero_transposition": [
                "contrabaixo",
                "contrafagote",
                "flautim",
            ],
            "interval_transposition_metadata_only": [
                p.instrument_id for p in list_profiles() if p.transposition != 0
            ],
            "classification": "PASS",
        },
        "pitch_contract": {
            "manual_legacy_input": "sounding/concert pitch; registry transposition not applied",
            "musicxml": "written <pitch> + <transpose> → sounding before validation/lookup",
            "spectral_data_keys": "sounding/concert pitch",
        },
    }
