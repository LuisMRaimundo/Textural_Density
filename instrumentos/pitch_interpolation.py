"""
Continuous-pitch interpolation for sparse instrument acoustic metadata tables.

Chromatic-only tables (C4, C#4, D4, … × pp/mf/ff) are sufficient; quarter-tones,
cents deviations, and equivalent spellings are resolved at runtime in MIDI float
space via ``microtonal.note_to_midi``.

Strictly symbolic: no audio analysis or signal processing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Literal

from microtonal import extract_cents, normalizar_simbolos_nota, note_to_midi

try:
    from scipy.interpolate import PchipInterpolator

    _HAS_PCHIP = True
except ImportError:  # pragma: no cover
    _HAS_PCHIP = False

WARN_DEVIATION_SEMITONES = 1.0
ERROR_DEVIATION_SEMITONES = 12.0
MIDI_MATCH_EPS = 1e-6

InterpolationMethod = Literal["auto", "linear", "pchip"]
LookupProvenance = Literal[
    "exact",
    "normalized_exact",
    "interpolated",
    "extrapolated",
    "fallback",
]


@dataclass(frozen=True)
class PitchLookupResult:
    """Result of a pitch×dynamic metadata lookup."""

    value: float
    provenance: LookupProvenance
    target_midi: float
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


def _note_to_target_midi(
    note: str,
    *,
    preprocess: Callable[[str], str] | None,
) -> tuple[float, str, str]:
    """
    Return (target_midi, normalized_note_without_cents, base_after_preprocess).

    Cents are applied on top of ``note_to_midi`` for the base spelling.
    """
    nota_norm = normalizar_simbolos_nota(note)
    base_note, cents_value = extract_cents(nota_norm)
    if preprocess is not None:
        base_note = preprocess(base_note)
    try:
        target_midi = float(note_to_midi(base_note))
        if cents_value != 0:
            target_midi += cents_value / 100.0
    except Exception as exc:
        raise ValueError(f"Cannot convert note {note!r} to MIDI: {exc}") from exc
    return target_midi, nota_norm, base_note


def _table_midi_for_key(
    table_key: str,
    *,
    preprocess: Callable[[str], str] | None,
) -> float | None:
    try:
        key_norm = normalizar_simbolos_nota(table_key)
        base, cents = extract_cents(key_norm)
        if preprocess is not None:
            base = preprocess(base)
        midi = float(note_to_midi(base))
        if cents != 0:
            midi += cents / 100.0
        return midi
    except Exception:
        return None


def _build_sorted_entries(
    spectral_data: dict[str, dict[str, float]],
    *,
    preprocess: Callable[[str], str] | None,
) -> list[tuple[float, str]]:
    entries: list[tuple[float, str]] = []
    for key in spectral_data:
        midi = _table_midi_for_key(key, preprocess=preprocess)
        if midi is not None:
            entries.append((midi, key))
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
    preprocess: Callable[[str], str] | None,
    prefer_key: str | None = None,
) -> tuple[float, str] | None:
    """Step 2 — enharmonic / equivalent-spelling match by MIDI float."""
    matches: list[tuple[float, str]] = []
    for key in spectral_data:
        midi = _table_midi_for_key(key, preprocess=preprocess)
        if midi is not None and abs(midi - target_midi) < MIDI_MATCH_EPS:
            matches.append((midi, key))
    if not matches:
        return None
    if prefer_key:
        for _, key in matches:
            if key == prefer_key:
                return _dynamic_value(spectral_data, key, dinamica), key
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
        if not (result == result and abs(result) < 1e12):  # NaN / inf guard
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
) -> PitchLookupResult:
    """
    Resolve instrument density from a sparse note×dynamic metadata table.

    Lookup order:
    1. Exact table key (original / normalized / preprocessed spelling)
    2. Normalised MIDI-equivalent match across table keys
    3. Continuous-pitch interpolation in MIDI float space

    Pitch and dynamic resolution are independent: dynamic is resolved per row,
    then pitch interpolation uses the selected dynamic column only.
    """
    log = logger or logging.getLogger(__name__)
    label = provenance_label or "instrument metadata"
    note_original = note
    warnings: list[str] = []
    dyn_resolved = _resolve_dynamic(dynamic)

    if not spectral_table:
        msg = f"Empty spectral table for {label}; fallback {fallback_value}"
        log.warning(msg)
        warnings.append(msg)
        return PitchLookupResult(
            value=float(fallback_value if fallback_value is not None else 0.0),
            provenance="fallback",
            target_midi=60.0,
            dynamic=dyn_resolved,
            warnings=tuple(warnings),
        )

    note_normalized = normalizar_simbolos_nota(note_original)
    base_preprocessed = note_original
    target_midi = 60.0
    try:
        target_midi, _, base_preprocessed = _note_to_target_midi(
            note_original, preprocess=preprocess
        )
    except ValueError as exc:
        msg = f"Invalid note {note_original!r} for {label}: {exc}"
        log.warning("%s — fallback", msg)
        warnings.append(msg)
        return PitchLookupResult(
            value=float(fallback_value if fallback_value is not None else 0.0),
            provenance="fallback",
            target_midi=60.0,
            dynamic=dyn_resolved,
            warnings=tuple(warnings),
        )

    exact = _exact_row_lookup(
        spectral_table,
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

    norm_match = _normalized_midi_lookup(
        spectral_table,
        target_midi,
        dynamic,
        preprocess=preprocess,
        prefer_key=base_preprocessed,
    )
    if norm_match is not None:
        value, matched_key = norm_match
        if matched_key != base_preprocessed and matched_key != note_original:
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

    entries = _build_sorted_entries(spectral_table, preprocess=preprocess)
    if not entries:
        msg = f"No parseable table keys for {label}; fallback"
        log.warning(msg)
        warnings.append(msg)
        return PitchLookupResult(
            value=float(fallback_value if fallback_value is not None else 0.0),
            provenance="fallback",
            target_midi=target_midi,
            dynamic=dyn_resolved,
            warnings=tuple(warnings),
        )

    value_at = lambda table_key: _dynamic_value(spectral_table, table_key, dynamic)
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
            return PitchLookupResult(
                value=float(fallback_value),
                provenance="fallback",
                target_midi=target_midi,
                dynamic=dyn_resolved,
                warnings=tuple(warnings),
            )
        lower, upper = _bracket_neighbors(target_midi, entries)
        clamp_midi = entries[0][0] if target_midi < entries[0][0] else entries[-1][0]
        clamp_key = lower[1] if target_midi < entries[0][0] else upper[1]
        return PitchLookupResult(
            value=float(value_at(clamp_key)),
            provenance="fallback",
            target_midi=target_midi,
            dynamic=dyn_resolved,
            lower_anchor_midi=clamp_midi,
            upper_anchor_midi=clamp_midi,
            lower_anchor_key=clamp_key,
            upper_anchor_key=clamp_key,
            warnings=tuple(warnings),
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
        return PitchLookupResult(
            value=float(value_at(edge_key)),
            provenance="fallback",
            target_midi=target_midi,
            dynamic=dyn_resolved,
            warnings=tuple(warnings),
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
    elif provenance == "interpolated":
        if lower[1] != upper[1]:
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
    """Public alias for sorted (midi, table_key) pairs."""
    return _build_sorted_entries(spectral_data, preprocess=preprocess)


__all__ = [
    "PitchLookupResult",
    "LookupProvenance",
    "InterpolationMethod",
    "resolve_density_from_table",
    "sorted_table_entries",
    "WARN_DEVIATION_SEMITONES",
    "ERROR_DEVIATION_SEMITONES",
]
