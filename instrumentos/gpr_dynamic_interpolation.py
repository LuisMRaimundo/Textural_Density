"""
Gaussian-process regression for modelled dynamics between pp/mf/ff anchors.

Source-table anchors remain pp, mf, ff only. Intermediate dynamics (p, mp, f)
are GPR predictions at fixed ordinal coordinates — not measured data.

Out-of-support tails (pppp/ppp below pp; fff/ffff above ff) use a
register-adaptive saturating log-domain extension whose local step derives
from the measured pp/mf/ff spread at the event's pitch (see config.DYN_TAIL_SHRINK).
"""

from __future__ import annotations

import logging
import math
from typing import Any, Final

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C, Matern

# Ordinal modelling coordinates (not dB / SPL / perceptual intensity).
GPR_RANDOM_STATE: Final[int] = 0

GPR_DYNAMIC_COORDINATES: dict[str, float] = {
    "pppp": 1.0,
    "ppp": 2.0,
    "pp": 3.0,
    "p": 4.0,
    "mp": 4.5,
    "mf": 5.0,
    "f": 6.0,
    "ff": 7.0,
    "fff": 8.0,
    "ffff": 9.0,
}

SOURCE_ANCHOR_DYNAMICS: tuple[str, ...] = ("pp", "mf", "ff")

# Dynamic levels backed by actual acoustic data points. For every GPR module the
# sparse source tables are measured at pp/mf/ff only; every other level is a
# model output (interior GPR interpolation, or saturating tail extrapolation).
MEASURED_SUPPORT: tuple[str, ...] = SOURCE_ANCHOR_DYNAMICS

# Technique modules whose pp/ff columns are transferred (not independently measured).
TRANSFERRED_ANCHOR_MODULES: frozenset[str] = frozenset(
    {"violin_sul_ponticello", "violin_art_harm"}
)

_LOG = logging.getLogger(__name__)


def _dynamic_order() -> list[str]:
    """DYNAMIC_LEVELS ordering (softest -> loudest), config-driven with fallback."""
    from config import DYNAMIC_LEVELS

    if DYNAMIC_LEVELS:
        return [d.strip().lower() for d in DYNAMIC_LEVELS]
    return ["pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff"]


def _support_bounds(
    measured_support: tuple[str, ...], order: list[str]
) -> tuple[str, str, int, int]:
    """Return (softest, loudest, softest_index, loudest_index) of measured support."""
    indices = {lvl: order.index(lvl) for lvl in measured_support if lvl in order}
    if not indices:
        raise ValueError(f"No measured-support level found in dynamic order: {measured_support}")
    softest = min(indices, key=indices.get)
    loudest = max(indices, key=indices.get)
    return softest, loudest, indices[softest], indices[loudest]


def measured_interior_step_counts(
    measured_support: tuple[str, ...] = MEASURED_SUPPORT,
) -> tuple[int, int]:
    """
    Return ``(N_soft, N_loud)``: DYNAMIC_LEVELS steps from softest→mf and mf→loudest.

    With default order and support ``(pp, mf, ff)`` this is ``(3, 2)``.
    """
    order = _dynamic_order()
    softest, loudest, i_soft, i_loud = _support_bounds(measured_support, order)
    if "mf" not in order:
        raise ValueError("DYNAMIC_LEVELS must include 'mf' for adaptive tails")
    i_mf = order.index("mf")
    if softest != "pp" or loudest != "ff":
        # Still define steps relative to mf when support is the standard triple.
        pass
    n_soft = i_mf - i_soft
    n_loud = i_loud - i_mf
    if n_soft <= 0 or n_loud <= 0:
        raise ValueError(
            f"Invalid measured-support spacing: N_soft={n_soft}, N_loud={n_loud}"
        )
    return n_soft, n_loud


def classify_dynamic_support(
    dynamic: str, measured_support: tuple[str, ...] = MEASURED_SUPPORT
) -> tuple[str, str | None, int]:
    """
    Classify a dynamic level relative to the measured support.

    Returns ``(region, boundary_level, steps)`` where ``region`` is one of
    ``"interior"``, ``"soft_tail"`` (below the softest measured level) or
    ``"loud_tail"`` (above the loudest measured level). ``boundary_level`` is the
    nearest measured level (softest or loudest) for tails, else ``None``.
    ``steps`` is the integer number of dynamic steps outside the support.
    """
    order = _dynamic_order()
    dyn = (dynamic or "mf").strip().lower()
    if dyn not in order:
        return ("interior", None, 0)
    softest, loudest, i_soft, i_loud = _support_bounds(measured_support, order)
    i = order.index(dyn)
    if i < i_soft:
        return ("soft_tail", softest, i_soft - i)
    if i > i_loud:
        return ("loud_tail", loudest, i - i_loud)
    return ("interior", None, 0)


def geometric_tail_sum(gamma: float, steps: int) -> float:
    """Σ_{i=1..j} γ^i = γ (1 − γ^j) / (1 − γ) for γ ≠ 1; else j."""
    j = int(steps)
    if j <= 0:
        return 0.0
    if abs(gamma - 1.0) < 1e-15:
        return float(j)
    return float(gamma * (1.0 - gamma**j) / (1.0 - gamma))


def local_tail_steps(
    a_pp: float,
    a_mf: float,
    a_ff: float,
    *,
    n_soft: int | None = None,
    n_loud: int | None = None,
) -> dict[str, Any]:
    """
    Compute register-adaptive per-step sizes from measured anchors at pitch m.

    Returns ``s_soft``, ``s_loud``, and inversion flags. Inversions clamp the
    corresponding step to 0 (flat unusable differentiation at that pitch).
    """
    if n_soft is None or n_loud is None:
        n_soft_r, n_loud_r = measured_interior_step_counts()
        n_soft = n_soft if n_soft is not None else n_soft_r
        n_loud = n_loud if n_loud is not None else n_loud_r

    soft_inverted = False
    loud_inverted = False
    s_soft = 0.0
    s_loud = 0.0

    if a_pp > 0.0 and a_mf > 0.0:
        if a_pp > a_mf:
            soft_inverted = True
            s_soft = 0.0
        else:
            s_soft = max(0.0, math.log(a_mf / a_pp) / float(n_soft))
    elif a_pp > 0.0 and a_mf <= 0.0:
        soft_inverted = True
        s_soft = 0.0

    if a_mf > 0.0 and a_ff > 0.0:
        if a_ff < a_mf:
            loud_inverted = True
            s_loud = 0.0
        else:
            s_loud = max(0.0, math.log(a_ff / a_mf) / float(n_loud))
    elif a_mf > 0.0 and a_ff <= 0.0:
        loud_inverted = True
        s_loud = 0.0

    return {
        "s_soft": float(s_soft),
        "s_loud": float(s_loud),
        "soft_inverted": soft_inverted,
        "loud_inverted": loud_inverted,
        "n_soft": int(n_soft),
        "n_loud": int(n_loud),
    }


def adaptive_tail_amplitude(
    boundary: float,
    step: float,
    steps: int,
    *,
    side: str,
    gamma: float | None = None,
) -> float:
    """
    Saturating register-adaptive tail amplitude in the log domain.

    soft: ln A = ln A_pp − s · Σ γ^i
    loud: ln A = ln A_ff + s · Σ γ^i
    """
    from config import DYN_TAIL_SHRINK

    g = DYN_TAIL_SHRINK if gamma is None else float(gamma)
    if boundary <= 0.0:
        return float(boundary)
    cum = geometric_tail_sum(g, steps)
    if side == "soft":
        return float(boundary * math.exp(-step * cum))
    if side == "loud":
        return float(boundary * math.exp(+step * cum))
    raise ValueError(f"side must be 'soft' or 'loud', got {side!r}")


def tail_saturation_info(
    dynamic: str,
    *,
    a_pp: float | None = None,
    a_mf: float | None = None,
    a_ff: float | None = None,
    measured_support: tuple[str, ...] = MEASURED_SUPPORT,
    module_name: str | None = None,
) -> dict[str, Any] | None:
    """
    Metadata for a tail evaluation, or ``None`` when the level is inside support.

    When anchors are supplied, records local ``s(m)``, ``γ``, and the resulting
    amplitude. Without anchors, returns classification-only fields (``s``/value
    left ``None``) for callers that only need region/boundary/steps.
    """
    from config import DYN_TAIL_SHRINK

    region, boundary, steps = classify_dynamic_support(dynamic, measured_support)
    if region == "interior":
        return None

    info: dict[str, Any] = {
        "region": region,
        "requested_level": (dynamic or "mf").strip().lower(),
        "boundary_level": boundary,
        "steps": int(steps),
        "gamma": float(DYN_TAIL_SHRINK),
        "s": None,
        "value": None,
        "soft_inverted": False,
        "loud_inverted": False,
        "transferred_anchors": bool(
            module_name and module_name in TRANSFERRED_ANCHOR_MODULES
        ),
        "description": (
            "saturating register-adaptive tail; differentiation derived from "
            "local measured pp/mf/ff spread"
        ),
    }

    if a_pp is None or a_mf is None or a_ff is None:
        return info

    local = local_tail_steps(float(a_pp), float(a_mf), float(a_ff))
    info["soft_inverted"] = local["soft_inverted"]
    info["loud_inverted"] = local["loud_inverted"]
    if region == "soft_tail":
        info["s"] = local["s_soft"]
        info["value"] = adaptive_tail_amplitude(
            float(a_pp), local["s_soft"], steps, side="soft"
        )
    else:
        info["s"] = local["s_loud"]
        info["value"] = adaptive_tail_amplitude(
            float(a_ff), local["s_loud"], steps, side="loud"
        )
    return info


def create_dynamic_gpr() -> GaussianProcessRegressor:
    """Construct the production GPR estimator with fixed hyperparameters and RNG."""
    matern_kernel = C(1.0) * Matern(length_scale=1.0, nu=1.5)
    return GaussianProcessRegressor(
        kernel=matern_kernel,
        n_restarts_optimizer=10,
        alpha=1e-1,
        random_state=GPR_RANDOM_STATE,
    )


def predict_intermediate_dynamics_gpr(
    pp_values: list[float] | np.ndarray,
    mf_values: list[float] | np.ndarray,
    ff_values: list[float] | np.ndarray,
    *,
    logger: logging.Logger | None = None,
) -> dict[str, np.ndarray]:
    """
    Predict all modelled dynamics via GPR fitted on pp/mf/ff anchor values.

    ``mp`` uses coordinate 4.5 between ``p`` (4.0) and ``mf`` (5.0).
    Out-of-support tails are replaced by the register-adaptive saturating rule.
    """
    log = logger or _LOG
    dynamic_levels = GPR_DYNAMIC_COORDINATES
    all_dynamics = list(dynamic_levels.keys())
    predictions: dict[str, list[float]] = {dynamic: [] for dynamic in all_dynamics}

    existing_levels = np.array(
        [dynamic_levels[d] for d in SOURCE_ANCHOR_DYNAMICS], dtype=float
    ).reshape(-1, 1)
    all_levels = np.array([dynamic_levels[d] for d in all_dynamics], dtype=float).reshape(
        -1, 1
    )

    try:
        y_train = np.array([pp_values, mf_values, ff_values], dtype=float).T
        if y_train.size == 0 or np.isnan(y_train).any():
            log.warning("Insufficient or invalid training data for GPR")
            return {d: np.zeros_like(pp_values, dtype=float) for d in all_dynamics}

        gpr = create_dynamic_gpr()

        for y in y_train:
            gpr.fit(existing_levels, y)
            y_pred = gpr.predict(all_levels)
            for j, dynamic in enumerate(all_dynamics):
                predictions[dynamic].append(float(y_pred[j]))

        result = {k: np.array(v, dtype=float) for k, v in predictions.items()}
        return _apply_adaptive_tails(result, pp_values, mf_values, ff_values)
    except Exception as exc:
        log.error("Error predicting intermediate dynamics: %s", exc)
        return {d: np.zeros_like(pp_values, dtype=float) for d in all_dynamics}


def _apply_adaptive_tails(
    predictions: dict[str, np.ndarray],
    pp_values: list[float] | np.ndarray,
    mf_values: list[float] | np.ndarray,
    ff_values: list[float] | np.ndarray,
) -> dict[str, np.ndarray]:
    """
    Replace out-of-support tail predictions with register-adaptive saturation.

    Interior (in-support) predictions are returned unchanged. Soft/loud tails
    use local measured steps ``s_soft(m)`` / ``s_loud(m)`` and geometric shrink γ.
    """
    from config import DENSITY_FLOOR, DYN_TAIL_SHRINK

    pp_arr = np.asarray(pp_values, dtype=float)
    mf_arr = np.asarray(mf_values, dtype=float)
    ff_arr = np.asarray(ff_values, dtype=float)
    n = pp_arr.shape[0]
    n_soft, n_loud = measured_interior_step_counts()

    for dynamic in list(predictions.keys()):
        region, _boundary, steps = classify_dynamic_support(dynamic)
        if region == "interior":
            continue

        values = np.empty(n, dtype=float)
        for i in range(n):
            local = local_tail_steps(
                float(pp_arr[i]),
                float(mf_arr[i]),
                float(ff_arr[i]),
                n_soft=n_soft,
                n_loud=n_loud,
            )
            if region == "soft_tail":
                values[i] = adaptive_tail_amplitude(
                    float(pp_arr[i]),
                    local["s_soft"],
                    steps,
                    side="soft",
                    gamma=DYN_TAIL_SHRINK,
                )
                boundary_ok = pp_arr[i] > 0.0
            else:
                values[i] = adaptive_tail_amplitude(
                    float(ff_arr[i]),
                    local["s_loud"],
                    steps,
                    side="loud",
                    gamma=DYN_TAIL_SHRINK,
                )
                boundary_ok = ff_arr[i] > 0.0
            if boundary_ok:
                assert values[i] >= DENSITY_FLOOR, (
                    f"saturated tail density below floor for {dynamic!r}"
                )
        predictions[dynamic] = values
    return predictions


def gpr_prediction_at_dynamic(
    note: str,
    dynamic: str,
    calcular_densidade: Any,
    *,
    logger: logging.Logger | None = None,
) -> float:
    """Resolve a modelled dynamic via GPR; anchors use ``calcular_densidade`` directly."""
    dyn = (dynamic or "mf").strip().lower()
    if dyn in SOURCE_ANCHOR_DYNAMICS:
        return float(calcular_densidade(note, dyn))
    if dyn not in GPR_DYNAMIC_COORDINATES:
        raise ValueError(f"Unsupported dynamic: {dynamic!r}")
    pp = float(calcular_densidade(note, "pp"))
    mf = float(calcular_densidade(note, "mf"))
    ff = float(calcular_densidade(note, "ff"))
    preds = predict_intermediate_dynamics_gpr([pp], [mf], [ff], logger=logger)
    return float(preds[dyn][0])
