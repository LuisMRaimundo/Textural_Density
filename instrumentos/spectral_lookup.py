"""
MIDI-space spectral table lookup with octave-preserving interpolation/extrapolation.

Delegates to ``instrumentos.pitch_interpolation`` for unified continuous-pitch
resolution. Avoids pitch-class / octave-collapse fallbacks that map D#6 → D#4
when the table only spans a lower register.
"""

from __future__ import annotations

import logging
from typing import Callable

from instrumentos.pitch_interpolation import (
    ERROR_DEVIATION_SEMITONES,
    WARN_DEVIATION_SEMITONES,
    PitchLookupResult,
    resolve_density_from_table,
    sorted_table_entries,
)

__all__ = [
    "lookup_spectral_density",
    "lookup_spectral_density_detailed",
    "PitchLookupResult",
    "WARN_DEVIATION_SEMITONES",
    "ERROR_DEVIATION_SEMITONES",
    "_sorted_table_entries",
]


def _sorted_table_entries(
    spectral_data: dict[str, dict[str, float]],
    *,
    preprocess: Callable[[str], str] | None = None,
) -> list[tuple[float, str]]:
    """Backward-compatible sorted (midi, key) entries for tests and tooling."""
    return sorted_table_entries(spectral_data, preprocess=preprocess)


def lookup_spectral_density_detailed(
    spectral_data: dict[str, dict[str, float]],
    nota: str,
    dinamica: str,
    *,
    logger: logging.Logger,
    preprocess: Callable[[str], str] | None = None,
    interpolation_method: str = "auto",
    allow_extrapolation: bool = True,
) -> PitchLookupResult:
    """Resolve density with full provenance metadata."""
    return resolve_density_from_table(
        spectral_data,
        nota,
        dinamica,
        interpolation_method=interpolation_method,  # type: ignore[arg-type]
        allow_extrapolation=allow_extrapolation,
        logger=logger,
        preprocess=preprocess,
    )


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

    Never collapses to the same pitch class in a distant octave; uses continuous
    pitch interpolation or controlled extrapolation along the MIDI axis instead.
    """
    result = lookup_spectral_density_detailed(
        spectral_data,
        nota,
        dinamica,
        logger=logger,
        preprocess=preprocess,
    )
    return float(result.value)
