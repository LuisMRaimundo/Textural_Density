"""
MIDI-space spectral table lookup with octave-preserving interpolation/extrapolation.

Avoids pitch-class / octave-collapse fallbacks that map D#6 → D#4 when the table
only spans a lower register.
"""

from __future__ import annotations

import logging
from typing import Callable

from microtonal import extract_cents, normalizar_simbolos_nota, note_to_midi

WARN_DEVIATION_SEMITONES = 1.0
ERROR_DEVIATION_SEMITONES = 12.0


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
    dyn = _resolve_dynamic(dinamica)
    row = spectral_data.get(table_key)
    if not row:
        raise KeyError(table_key)
    if dyn in row:
        return float(row[dyn])
    if "mf" in row:
        return float(row["mf"])
    return float(sum(row.values()) / len(row))


def _sorted_table_entries(
    spectral_data: dict[str, dict[str, float]],
) -> list[tuple[float, str]]:
    entries: list[tuple[float, str]] = []
    for key in spectral_data:
        try:
            entries.append((float(note_to_midi(key)), key))
        except Exception:
            continue
    entries.sort(key=lambda item: item[0])
    return entries


def _value_from_midi(
    target_midi: float,
    entries: list[tuple[float, str]],
    value_at: Callable[[str], float],
) -> tuple[float, float, str | None, str | None]:
    """Return (density, effective_midi, lower_key, upper_key) after MIDI fit."""
    if len(entries) == 1:
        midi, key = entries[0]
        return value_at(key), midi, key, key

    midis = [m for m, _ in entries]
    if target_midi <= midis[0]:
        m1, k1 = entries[0]
        m2, k2 = entries[1]
    elif target_midi >= midis[-1]:
        m1, k1 = entries[-2]
        m2, k2 = entries[-1]
    else:
        lower: tuple[float, str] | None = None
        upper: tuple[float, str] | None = None
        for midi, key in entries:
            if midi <= target_midi:
                lower = (midi, key)
            if midi >= target_midi and upper is None:
                upper = (midi, key)
        assert lower is not None and upper is not None
        m1, k1 = lower
        m2, k2 = upper
        if m1 == m2:
            return value_at(k1), m1, k1, k2

    v1 = value_at(k1)
    v2 = value_at(k2)
    if m2 == m1:
        return v2, m2, k1, k2
    t = (target_midi - m1) / (m2 - m1)
    return v1 + t * (v2 - v1), target_midi, k1, k2


def _log_lookup(
    logger: logging.Logger,
    *,
    nota_original: str,
    target_midi: float,
    lower_key: str | None,
    upper_key: str | None,
    table_entries: list[tuple[float, str]],
) -> None:
    if lower_key and upper_key and lower_key == upper_key:
        return

    if lower_key and upper_key and lower_key != upper_key:
        msg = (
            f"Nota {nota_original} (MIDI {target_midi:.2f}) ajustada por interpolação/extrapolação "
            f"entre {lower_key} e {upper_key}"
        )
    elif lower_key:
        msg = (
            f"Nota {nota_original} (MIDI {target_midi:.2f}) ajustada a partir de {lower_key}"
        )
    else:
        msg = f"Nota {nota_original} (MIDI {target_midi:.2f}) ajustada por tabela espectral"

    table_min = table_entries[0][0]
    table_max = table_entries[-1][0]
    if target_midi < table_min:
        deviation = table_min - target_midi
    elif target_midi > table_max:
        deviation = target_midi - table_max
    else:
        deviation = 0.0

    if deviation > ERROR_DEVIATION_SEMITONES:
        logger.error("%s — desvio %.1f semitons (>1 oitava); resultado pouco fiável", msg, deviation)
    elif deviation > WARN_DEVIATION_SEMITONES:
        logger.warning("%s — desvio %.1f semitons fora da tabela", msg, deviation)
    else:
        logger.info(msg)


def lookup_spectral_density(
    spectral_data: dict[str, dict[str, float]],
    nota: str,
    dinamica: str,
    *,
    logger: logging.Logger,
    preprocess: Callable[[str], str] | None = None,
) -> float:
    """
    Resolve instrument density from a sparse note×dynamic table in MIDI space.

    Never collapses to the same pitch class in a distant octave; uses linear
    interpolation or extrapolation along the MIDI axis instead.
    """
    nota_original = nota
    nota_norm = normalizar_simbolos_nota(nota)
    base_note, cents_value = extract_cents(nota_norm)
    if preprocess is not None:
        base_note = preprocess(base_note)

    dyn = _resolve_dynamic(dinamica)

    if cents_value == 0 and base_note in spectral_data:
        if dinamica in spectral_data[base_note]:
            return float(spectral_data[base_note][dinamica])
        if dyn in spectral_data[base_note]:
            return float(spectral_data[base_note][dyn])

    try:
        target_midi = float(note_to_midi(base_note))
        if cents_value != 0:
            target_midi += cents_value / 100.0
    except Exception as exc:
        logger.warning("Erro ao converter %s para MIDI: %s — fallback C4", base_note, exc)
        return _dynamic_value(spectral_data, "C4", dyn) if "C4" in spectral_data else 5.0

    entries = _sorted_table_entries(spectral_data)
    if not entries:
        logger.warning("Tabela espectral vazia; fallback 5.0 para %s", nota_original)
        return 5.0

    for midi, key in entries:
        if abs(midi - target_midi) < 1e-9 and dyn in spectral_data[key]:
            return float(spectral_data[key][dyn])

    value_at = lambda table_key: _dynamic_value(spectral_data, table_key, dyn)
    density, _, lower_key, upper_key = _value_from_midi(target_midi, entries, value_at)
    _log_lookup(
        logger,
        nota_original=nota_original,
        target_midi=target_midi,
        lower_key=lower_key,
        upper_key=upper_key,
        table_entries=entries,
    )
    return float(density)
