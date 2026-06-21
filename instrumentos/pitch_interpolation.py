"""
Continuous-pitch interpolation for sparse instrument acoustic metadata tables.

Chromatic-only tables (C4, C#4, D4, … × pp/mf/ff) are the canonical model.
Quarter-tones, arbitrary cent deviations, and enharmonic spellings resolve at
runtime in MIDI float space via ``microtonal.note_to_midi_strict``.

Strictly symbolic: no audio analysis or signal processing.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Callable, Literal

from microtonal import InvalidPitchNotation, normalizar_simbolos_nota, note_to_midi_strict

try:
    from scipy.interpolate import PchipInterpolator

    _HAS_PCHIP = True
except ImportError:  # pragma: no cover
    _HAS_PCHIP = False

WARN_DEVIATION_SEMITONES = 1.0
ERROR_DEVIATION_SEMITONES = 12.0
MIDI_MATCH_EPS = 1e-6
VALUE_MATCH_EPS = 1e-9

InterpolationMethod = Literal["auto", "linear", "pchip"]
LookupProvenance = Literal[
    "exact",
    "normalized_exact",
    "interpolated",
    "extrapolated",
    "fallback",
]


class MetadataTableConflictError(ValueError):
    """Raised when duplicate MIDI coordinates disagree on dynamic metadata values."""


@dataclass(frozen=True)
class PitchLookupResult:
    """Result of a pitch×dynamic metadata lookup."""

    value: float
    provenance: LookupProvenance
    target_midi: float | None
    dynamic: str
    lower_anchor_midi: float | None = None
    upper_anchor_midi: float | None = None
    lower_anchor_key: str | None = None
    upper_anchor_key: str | None = None
    warnings: tuple[str, ...] = ()


def _resolve_dynamic(dinamica: str) -> str:
    dyn = (dinamica or "mf").strip().lower()
    if dyn in ("pp", "mf", "ff"):
        return dyn
    if dyn in ("pppp", "ppp", "p"):
        return "pp"
    if dyn in ("f", "fff", "ffff"):
        return "ff"
    return "mf"


def _dynamic_value(
    spectral_data: dict[str, dict[str, float]],
    table_key: str,
    dinamica: str,
) -> float:
    """Resolve density for one table row and dynamic marking."""
    dyn = _resolve_dynamic(dinamica)
    row = spectral_data.get(table_key)
    if not row:
        raise KeyError(table_key)
    if dinamica in row:
        return float(row[dinamica])
    if dyn in row:
        return float(row[dyn])
    if "mf" in row:
        return float(row["mf"])
    return float(sum(row.values()) / len(row))


def _parse_table_key_midi(
    table_key: str,
    *,
    preprocess: Callable[[str], str] | None,
) -> float:
    candidate = normalizar_simbolos_nota(table_key)
    if preprocess is not None:
        candidate = preprocess(candidate)
    return float(note_to_midi_strict(candidate))


def _note_to_target_midi(
    note: str,
    *,
    preprocess: Callable[[str], str] | None,
) -> tuple[float, str, str]:
    """Return (target_midi, normalized_note, preprocessed_note)."""
    note_normalized = normalizar_simbolos_nota(note)
    candidate = note_normalized
    if preprocess is not None:
        candidate = preprocess(candidate)
    target_midi = float(note_to_midi_strict(candidate))
    return target_midi, note_normalized, candidate


def validate_metadata_table(
    spectral_table: dict[str, dict[str, float]],
    *,
    preprocess: Callable[[str], str] | None = None,
    logger: logging.Logger | None = None,
) -> tuple[dict[str, dict[str, float]], tuple[str, ...]]:
    """
    Validate and normalize a metadata table.

    - Unparsable keys are excluded with warnings.
    - Harmless duplicate MIDI rows (identical dynamic values) are deduplicated
      deterministically (lexicographically smallest key kept).
    - Conflicting duplicate MIDI rows raise ``MetadataTableConflictError``.
    """
    log = logger or logging.getLogger(__name__)
    warnings: list[str] = []
    parsed: list[tuple[float, str, dict[str, float]]] = []

    for key, row in spectral_table.items():
        try:
            midi = _parse_table_key_midi(key, preprocess=preprocess)
        except InvalidPitchNotation as exc:
            msg = f"Skipping unparsable metadata table key {key!r}: {exc}"
            log.warning(msg)
            warnings.append(msg)
            continue
        parsed.append((midi, key, dict(row)))

    by_midi: dict[float, list[tuple[str, dict[str, float]]]] = {}
    for midi, key, row in parsed:
        by_midi.setdefault(midi, []).append((key, row))

    normalized: dict[str, dict[str, float]] = {}
    for midi, items in sorted(by_midi.items(), key=lambda item: item[0]):
        items_sorted = sorted(items, key=lambda item: item[0])
        ref_key, ref_row = items_sorted[0]
        for key, row in items_sorted[1:]:
            dynamics = set(ref_row) | set(row)
            for dyn in dynamics:
                if dyn not in ref_row or dyn not in row:
                    continue
                if abs(float(ref_row[dyn]) - float(row[dyn])) > VALUE_MATCH_EPS:
                    raise MetadataTableConflictError(
                        f"Conflicting metadata at MIDI {midi:.4f}: "
                        f"{ref_key!r} ({dyn}={ref_row[dyn]}) vs "
                        f"{key!r} ({dyn}={row[dyn]})"
                    )
            msg = (
                f"Harmless duplicate MIDI {midi:.4f}: kept {ref_key!r}, "
                f"deduplicated {[k for k, _ in items_sorted[1:]]}"
            )
            log.info(msg)
            warnings.append(msg)
        normalized[ref_key] = ref_row

    return normalized, tuple(dict.fromkeys(warnings))


def _build_sorted_entries(
    spectral_data: dict[str, dict[str, float]],
    *,
    preprocess: Callable[[str], str] | None,
    logger: logging.Logger | None = None,
    validate_table: bool = True,
) -> list[tuple[float, str]]:
    if validate_table:
        validated, _ = validate_metadata_table(
            spectral_data, preprocess=preprocess, logger=logger
        )
    else:
        validated = spectral_data
    entries = [
        (_parse_table_key_midi(key, preprocess=preprocess), key)
        for key in validated
    ]
    entries.sort(key=lambda item: item[0])
    return entries


def _exact_row_lookup(
    spectral_data: dict[str, dict[str, float]],
    *,
    note_original: str,
    note_normalized: str,
    dinamica: str,
) -> float | None:
    """Step 1 — literal key match in table (no cents stripping)."""
    for candidate in (note_original, note_normalized):
        if not candidate or candidate not in spectral_data:
            continue
        row = spectral_data[candidate]
        if dinamica in row:
            return float(row[dinamica])
        dyn = _resolve_dynamic(dinamica)
        if dyn in row:
            return float(row[dyn])
    return None


def _normalized_midi_lookup(
    spectral_data: dict[str, dict[str, float]],
    target_midi: float,
    dinamica: str,
    *,
    entries: list[tuple[float, str]],
) -> tuple[float, str] | None:
    """Step 2 — MIDI-equivalent match against validated table anchors."""
    matches = [(midi, key) for midi, key in entries if abs(midi - target_midi) < MIDI_MATCH_EPS]
    if not matches:
        return None
    matches.sort(key=lambda item: item[1])
    key = matches[0][1]
    return _dynamic_value(spectral_data, key, dinamica), key


def _bracket_neighbors(
    target_midi: float,
    entries: list[tuple[float, str]],
) -> tuple[tuple[float, str], tuple[float, str]]:
    if len(entries) == 1:
        return entries[0], entries[0]
    midis = [m for m, _ in entries]
    if target_midi <= midis[0]:
        return entries[0], entries[1]
    if target_midi >= midis[-1]:
        return entries[-2], entries[-1]
    lower: tuple[float, str] | None = None
    upper: tuple[float, str] | None = None
    for midi, key in entries:
        if midi <= target_midi:
            lower = (midi, key)
        if midi >= target_midi and upper is None:
            upper = (midi, key)
    assert lower is not None and upper is not None
    return lower, upper


def _interpolate_linear(
    target_midi: float,
    lower: tuple[float, str],
    upper: tuple[float, str],
    value_at: Callable[[str], float],
) -> float:
    m1, k1 = lower
    m2, k2 = upper
    v1 = value_at(k1)
    if m1 == m2:
        return v1
    v2 = value_at(k2)
    t = (target_midi - m1) / (m2 - m1)
    return float(v1 + t * (v2 - v1))


def _interpolate_pchip(
    target_midi: float,
    entries: list[tuple[float, str]],
    value_at: Callable[[str], float],
) -> float | None:
    if not _HAS_PCHIP or len(entries) < 3:
        return None
    midis = [m for m, _ in entries]
    values = [value_at(k) for _, k in entries]
    if len(set(midis)) < 3:
        return None
    try:
        interpolator = PchipInterpolator(midis, values, extrapolate=False)
        result = float(interpolator(target_midi))
        if not math.isfinite(result) or abs(result) >= 1e12:
            return None
        return result
    except Exception:
        return None


def _range_deviation_semitones(
    target_midi: float,
    entries: list[tuple[float, str]],
) -> float:
    if not entries:
        return 0.0
    table_min = entries[0][0]
    table_max = entries[-1][0]
    if target_midi < table_min:
        return table_min - target_midi
    if target_midi > table_max:
        return target_midi - table_max
    return 0.0


def _fallback_result(
    *,
    value: float,
    dynamic: str,
    target_midi: float | None,
    warnings: list[str],
) -> PitchLookupResult:
    return PitchLookupResult(
        value=float(value),
        provenance="fallback",
        target_midi=target_midi,
        dynamic=dynamic,
        warnings=tuple(dict.fromkeys(warnings)),
    )


def resolve_density_from_table(
    spectral_table: dict[str, dict[str, float]],
    note: str,
    dynamic: str,
    *,
    interpolation_method: InterpolationMethod = "auto",
    allow_extrapolation: bool = True,
    provenance_label: str | None = None,
    fallback_value: float | None = 5.0,
    logger: logging.Logger | None = None,
    preprocess: Callable[[str], str] | None = None,
    validate_table: bool = True,
) -> PitchLookupResult:
    """
    Resolve instrument density from a sparse note×dynamic metadata table.

    Chromatic anchors define a continuous pitch-density function; microtonal
    curated rows are optional exact overrides. Lookup order:

    1. Exact table key
    2. Normalised MIDI-equivalent match
    3. Continuous interpolation in MIDI float space
    """
    log = logger or logging.getLogger(__name__)
    label = provenance_label or "instrument metadata"
    note_original = note
    warnings: list[str] = []
    dyn_resolved = _resolve_dynamic(dynamic)

    working_table = spectral_table
    if validate_table and spectral_table:
        try:
            working_table, table_warnings = validate_metadata_table(
                spectral_table, preprocess=preprocess, logger=log
            )
            warnings.extend(table_warnings)
        except MetadataTableConflictError:
            raise

    if not working_table:
        msg = f"Empty spectral table for {label}; fallback {fallback_value}"
        log.warning(msg)
        warnings.append(msg)
        return _fallback_result(
            value=float(fallback_value if fallback_value is not None else 0.0),
            dynamic=dyn_resolved,
            target_midi=None,
            warnings=warnings,
        )

    note_normalized = normalizar_simbolos_nota(note_original)
    try:
        target_midi, _, _ = _note_to_target_midi(note_original, preprocess=preprocess)
    except InvalidPitchNotation as exc:
        msg = f"Invalid note {note_original!r} for {label}: {exc}"
        log.warning("%s — fallback", msg)
        warnings.append(msg)
        return _fallback_result(
            value=float(fallback_value if fallback_value is not None else 0.0),
            dynamic=dyn_resolved,
            target_midi=None,
            warnings=warnings,
        )

    exact = _exact_row_lookup(
        working_table,
        note_original=note_original,
        note_normalized=note_normalized,
        dinamica=dynamic,
    )
    if exact is not None:
        return PitchLookupResult(
            value=float(exact),
            provenance="exact",
            target_midi=target_midi,
            dynamic=dyn_resolved,
            warnings=tuple(warnings),
        )

    entries = (
        [
            (_parse_table_key_midi(key, preprocess=preprocess), key)
            for key in working_table
        ]
        if validate_table
        else _build_sorted_entries(
            working_table,
            preprocess=preprocess,
            logger=log,
            validate_table=False,
        )
    )
    entries.sort(key=lambda item: item[0])

    if not entries:
        msg = f"No parseable table keys for {label}; fallback"
        log.warning(msg)
        warnings.append(msg)
        return _fallback_result(
            value=float(fallback_value if fallback_value is not None else 0.0),
            dynamic=dyn_resolved,
            target_midi=target_midi,
            warnings=warnings,
        )

    norm_match = _normalized_midi_lookup(
        working_table, target_midi, dynamic, entries=entries
    )
    if norm_match is not None:
        value, matched_key = norm_match
        if matched_key != note_original and matched_key != note_normalized:
            msg = (
                f"Note {note_original} (MIDI {target_midi:.4f}) matched table key "
                f"{matched_key!r} by MIDI equivalence"
            )
            log.info(msg)
        return PitchLookupResult(
            value=float(value),
            provenance="normalized_exact",
            target_midi=target_midi,
            dynamic=dyn_resolved,
            lower_anchor_key=matched_key,
            upper_anchor_key=matched_key,
            warnings=tuple(warnings),
        )

    value_at = lambda table_key: _dynamic_value(working_table, table_key, dynamic)
    deviation = _range_deviation_semitones(target_midi, entries)
    in_range = deviation < MIDI_MATCH_EPS

    if deviation > ERROR_DEVIATION_SEMITONES:
        msg = (
            f"Note {note_original} (MIDI {target_midi:.2f}) is {deviation:.1f} semitones "
            f"outside table range [{entries[0][0]:.2f}, {entries[-1][0]:.2f}] — "
            f"using fallback (no distant pitch-class collapse)"
        )
        log.error(msg)
        warnings.append(msg)
        if fallback_value is not None:
            return _fallback_result(
                value=float(fallback_value),
                dynamic=dyn_resolved,
                target_midi=target_midi,
                warnings=warnings,
            )
        lower, upper = _bracket_neighbors(target_midi, entries)
        clamp_key = lower[1] if target_midi < entries[0][0] else upper[1]
        clamp_midi = entries[0][0] if target_midi < entries[0][0] else entries[-1][0]
        return _fallback_result(
            value=float(value_at(clamp_key)),
            dynamic=dyn_resolved,
            target_midi=target_midi,
            warnings=warnings,
        )

    if not allow_extrapolation and not in_range:
        msg = (
            f"Note {note_original} (MIDI {target_midi:.2f}) outside table range "
            f"and extrapolation disabled"
        )
        log.warning(msg)
        warnings.append(msg)
        lower, upper = _bracket_neighbors(target_midi, entries)
        edge_key = lower[1] if target_midi < entries[0][0] else upper[1]
        return _fallback_result(
            value=float(value_at(edge_key)),
            dynamic=dyn_resolved,
            target_midi=target_midi,
            warnings=warnings,
        )

    lower, upper = _bracket_neighbors(target_midi, entries)
    density: float
    provenance: LookupProvenance

    if abs(lower[0] - target_midi) < MIDI_MATCH_EPS:
        density = float(value_at(lower[1]))
        provenance = "exact"
    elif abs(upper[0] - target_midi) < MIDI_MATCH_EPS:
        density = float(value_at(upper[1]))
        provenance = "exact"
    elif interpolation_method == "pchip" or (
        interpolation_method == "auto" and in_range and len(entries) >= 4
    ):
        pchip_val = _interpolate_pchip(target_midi, entries, value_at)
        if pchip_val is not None and in_range:
            density = pchip_val
            provenance = "interpolated"
        else:
            density = _interpolate_linear(target_midi, lower, upper, value_at)
            provenance = "extrapolated" if not in_range else "interpolated"
    else:
        density = _interpolate_linear(target_midi, lower, upper, value_at)
        provenance = "extrapolated" if not in_range else "interpolated"

    if not in_range:
        if deviation > WARN_DEVIATION_SEMITONES:
            level = logging.ERROR if deviation > ERROR_DEVIATION_SEMITONES else logging.WARNING
            msg = (
                f"Note {note_original} (MIDI {target_midi:.2f}) {provenance} "
                f"between {lower[1]!r} and {upper[1]!r} — "
                f"{deviation:.1f} semitones outside table"
            )
            log.log(level, msg)
            warnings.append(msg)
        else:
            msg = (
                f"Note {note_original} (MIDI {target_midi:.2f}) slightly outside table "
                f"({deviation:.2f} st) — controlled extrapolation"
            )
            log.info(msg)
    elif provenance == "interpolated" and lower[1] != upper[1]:
        msg = (
            f"Note {note_original} (MIDI {target_midi:.4f}) interpolated "
            f"between {lower[1]!r} and {upper[1]!r} — modelled from chromatic anchors"
        )
        log.info(msg)

    if provenance in ("interpolated", "extrapolated"):
        warnings.append(
            "Density value is a modelled estimate from chromatic metadata anchors, "
            "not a directly measured acoustic table entry."
        )

    return PitchLookupResult(
        value=float(density),
        provenance=provenance,
        target_midi=target_midi,
        dynamic=dyn_resolved,
        lower_anchor_midi=lower[0],
        upper_anchor_midi=upper[0],
        lower_anchor_key=lower[1],
        upper_anchor_key=upper[1],
        warnings=tuple(dict.fromkeys(warnings)),
    )


def sorted_table_entries(
    spectral_data: dict[str, dict[str, float]],
    *,
    preprocess: Callable[[str], str] | None = None,
) -> list[tuple[float, str]]:
    """Public alias for sorted (midi, table_key) pairs after validation."""
    return _build_sorted_entries(spectral_data, preprocess=preprocess)


__all__ = [
    "MetadataTableConflictError",
    "PitchLookupResult",
    "LookupProvenance",
    "InterpolationMethod",
    "resolve_density_from_table",
    "validate_metadata_table",
    "sorted_table_entries",
    "WARN_DEVIATION_SEMITONES",
    "ERROR_DEVIATION_SEMITONES",
]
