# instrumentos/uncalibrated_harmonic.py
"""Shared helpers for harmonic modules without acoustic calibration tables."""

from __future__ import annotations

from typing import Any


ACCEPTANCE_STATUS_UNCALIBRATED = "implemented_but_uncalibrated"

PP_MEASURED: dict[str, float] = {}
MF_MEASURED: dict[str, float] = {}
FF_MEASURED: dict[str, float] = {}
spectral_data: dict[str, dict[str, float]] = {}


def unavailable_density(_nota: Any, _dinamica: Any) -> None:
    """Explicit NA: modal registers may exist in STE, but TD has no EWSD table."""
    return None


def unavailable_gpr(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return {}
