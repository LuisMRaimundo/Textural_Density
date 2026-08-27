"""Shared helpers for the plausibility battery.

§H blend/composite formulas are re-implemented here from the Mathematical
Manual text only — this module must not import ``core.composite``.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from instrumentos.registry import REGISTRY, list_instrument_ids, list_profiles

# Documented constants (Mathematical Manual §H / Technical Manual / API).
REF = 193.0
DEFAULT_W = 0.5
DI_MAX = 100.0
DV_MAX_LEGACY = 10.0
BLEND_SCALE = 10.0
COMPOSITE_HARMONIC_DAMPING = 0.15
MIN_PCHIP_ANCHORS = 4
PITCH_MERGE_TOL = 1e-6
OCTAVE_CLASS_ATOL = 0.25
PCHIP_FALLBACK = 5.0
A4_HZ = 440.0
A4_MIDI = 69
REGISTER_BANDS = {
    "very_low": (0, 36),
    "low": (36, 48),
    "mid": (48, 72),
    "high": (72, 84),
    "very_high": (84, 128),
}
ORCH_BALANCE_REGIONS = ((0, 48), (48, 72), (72, 108))
DYNAMIC_LEVELS = (
    "pppp",
    "ppp",
    "pp",
    "p",
    "mp",
    "mf",
    "f",
    "ff",
    "fff",
    "ffff",
)
WITHDRAWN_IDS = (
    "violoncelo_sul_tasto",
    "contrabaixo_sul_tasto",
)
WITHDRAWN_MODULE_GLOBS = (
    "cello_sul_tasto.py",
    "double_bass_sul_tasto.py",
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = REPO_ROOT / "reports" / "plausibility_raw.json"


def classify_instruments() -> dict[str, Any]:
    """Re-derive table-backed vs coarse split from the live registry."""
    table_backed: list[str] = []
    coarse: list[str] = []
    for iid in list_instrument_ids():
        profile = REGISTRY[iid]
        if profile.module_name:
            table_backed.append(iid)
        else:
            coarse.append(iid)
    return {
        "all_ids": list(list_instrument_ids()),
        "table_backed": table_backed,
        "coarse": coarse,
        "n_table_backed": len(table_backed),
        "n_coarse": len(coarse),
        "n_profiles": len(list(list_profiles())),
    }


def instrument_status(instrument_id: str) -> str:
    profile = REGISTRY.get(instrument_id)
    if profile is None:
        return "unregistered"
    return "table-backed" if profile.module_name else "coarse"


def slice_input(
    notes: list[str],
    *,
    instruments: list[str] | str = "flauta",
    dynamics: list[str] | str = "mf",
    num_instruments: list[int] | int = 1,
    weight_factor: float = DEFAULT_W,
    **extra: Any,
) -> dict[str, Any]:
    n = len(notes)
    if isinstance(instruments, str):
        instruments = [instruments] * n
    if isinstance(dynamics, str):
        dynamics = [dynamics] * n
    if isinstance(num_instruments, int):
        num_instruments = [num_instruments] * n
    payload = {
        "notes": list(notes),
        "dynamics": list(dynamics),
        "instruments": list(instruments),
        "num_instruments": list(num_instruments),
        "weight_factor": float(weight_factor),
    }
    payload.update(extra)
    return payload


def independent_hz(midi: float) -> float:
    return A4_HZ * (2.0 ** ((float(midi) - A4_MIDI) / 12.0))


def independent_midi_from_hz(freq: float) -> float:
    if freq <= 0:
        return 0.0
    return A4_MIDI + 12.0 * math.log2(float(freq) / A4_HZ)


def independent_blend(
    di: float,
    dv: float,
    w: float,
    mass: float,
    *,
    di_max: float = DI_MAX,
    dv_max: float = DV_MAX_LEGACY,
    scale: float = BLEND_SCALE,
    ref: float = REF,
    use_log: bool = True,
) -> dict[str, float]:
    """Independent §H re-implementation (legacy divisors; no clamping)."""
    d_blend = scale * (w * (di / di_max) + (1.0 - w) * (dv / dv_max))
    raw = d_blend * math.sqrt(mass) / ref
    total = math.log10(1.0 + raw) if use_log else raw
    inst_term = scale * w * (di / di_max)
    int_term = scale * (1.0 - w) * (dv / dv_max)
    ratio = None
    if int_term != 0.0:
        ratio = inst_term / int_term
    return {
        "weighted": d_blend,
        "total_pre_log": raw,
        "total": total,
        "instrument_term": inst_term,
        "interval_term": int_term,
        "instrument_to_interval_ratio": ratio,
    }


def assert_jsonable(obj: Any, *, label: str) -> str:
    """HARD: production result dictionaries must serialise without NaN."""

    def _default(o: Any) -> Any:
        if hasattr(o, "item"):
            return o.item()
        raise TypeError(f"{label}: non-JSON type {type(o)!r}")

    return json.dumps(obj, allow_nan=False, default=_default)


def density_block(resultados: dict[str, Any]) -> dict[str, Any]:
    return dict(resultados.get("density") or {})


def spearman_rho(xs: list[float], ys: list[float]) -> float:
    """Spearman rank correlation without scipy (average ranks for ties)."""
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")

    def _ranks(vals: list[float]) -> list[float]:
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(vals):
            j = i
            while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        return ranks

    rx, ry = _ranks(xs), _ranks(ys)
    mx = sum(rx) / len(rx)
    my = sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    deny = math.sqrt(sum((b - my) ** 2 for b in ry))
    if denx == 0.0 or deny == 0.0:
        return float("nan")
    return num / (denx * deny)
