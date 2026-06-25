"""Build machine-readable instrument register audit reports for tests and tooling."""

from __future__ import annotations

import importlib
from typing import Any

from instrumentos import get_instrument_module
from instrumentos.registry import REGISTRY, list_profiles, resolve_profile
from microtonal import note_to_midi_strict

_GPR_MODULE_IDS = frozenset(
    {"violino", "viola", "violoncelo", "contrabaixo", "flauta", "clarinete", "oboe"}
)


def _classify_transposition(semitones: int) -> str:
    if semitones == 0:
        return "A_non_transposing"
    if semitones in (12, -12):
        return "B_octave_up" if semitones > 0 else "C_octave_down"
    return "D_interval_transposing"


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
    src = getattr(mod, "INSTRUMENT_SOURCE", None)
    pitch_range = getattr(src, "pitch_range", None) if src else None
    return {
        "first_note": notes[0],
        "last_note": notes[-1],
        "row_count": len(notes),
        "min_midi": lo,
        "max_midi": hi,
        "instrument_source_pitch_range": list(pitch_range) if pitch_range else None,
    }


def _range_discrepancy(profile, table: dict[str, Any] | None) -> str:
    if table is None:
        return "no_table"
    lo, hi = profile.sounding_range
    t_lo, t_hi = table["min_midi"], table["max_midi"]
    if lo <= t_lo and hi >= t_hi:
        if lo == t_lo and hi == t_hi:
            return "aligned"
        return "OK_registry_covers_table"
    if t_lo < lo or t_hi > hi:
        return "BUG_table_anchor_outside_registry"
    return "REVIEW_REQUIRED"


def build_instrument_register_audit() -> dict[str, Any]:
    instruments: list[dict[str, Any]] = []
    for profile in sorted(list_profiles(), key=lambda p: p.instrument_id):
        table = _table_span(profile.module_name)
        lo, hi = profile.sounding_range
        aliases = [profile.instrument_id, profile.display_name, *profile.aliases]
        instruments.append(
            {
                "instrument_id": profile.instrument_id,
                "display_name": profile.display_name,
                "aliases": list(profile.aliases),
                "family": profile.family,
                "transposition_semitones": profile.transposition,
                "transposition_class": _classify_transposition(profile.transposition),
                "registry_sounding_min_midi": int(lo),
                "registry_sounding_max_midi": int(hi),
                "comfortable_min_midi": int(profile.comfortable_range[0]),
                "comfortable_max_midi": int(profile.comfortable_range[1]),
                "module_name": profile.module_name,
                "profile_status": profile.profile_status,
                "table_span": table,
                "range_discrepancy": _range_discrepancy(profile, table),
                "validation_uses": "sounding_pitch_midi_vs_registry_sounding_range",
                "manual_input_convention": "sounding_concert_pitch",
                "musicxml_convention": "transpose_element_to_sounding_before_validation",
                "registry_transposition_applied_at_runtime": False,
            }
        )

    alias_rows: list[dict[str, str]] = []
    for profile in list_profiles():
        for alias in (profile.display_name, *profile.aliases):
            resolved = resolve_profile(alias)
            alias_rows.append(
                {
                    "alias": alias,
                    "canonical_id": profile.instrument_id,
                    "resolved_id": resolved.instrument_id if resolved else "MISSING",
                }
            )

    return {
        "instrument_count": len(instruments),
        "instruments": instruments,
        "alias_resolution": alias_rows,
        "pitch_contract": {
            "manual_legacy_input": "notes[] are sounding/concert pitch",
            "musicxml": "written pitch transposed via <transpose> before validation",
            "density_lookup": "sounding_pitch",
            "range_validation": "sounding_pitch vs registry.sounding_range",
            "registry_transposition_field": "metadata_only_not_applied_to_manual_input",
        },
    }


def gpr_module_ids() -> tuple[str, ...]:
    return tuple(sorted(_GPR_MODULE_IDS))
