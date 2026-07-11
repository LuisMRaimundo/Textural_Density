"""
Gaussian-process regression for modelled dynamics between pp/mf/ff anchors.

Source-table anchors remain pp, mf, ff only. Intermediate dynamics (p, mp, f,
extremes) are GPR predictions at fixed ordinal coordinates — not measured data.
"""

from __future__ import annotations

import logging
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


def tail_saturation_info(
    dynamic: str, measured_support: tuple[str, ...] = MEASURED_SUPPORT
) -> dict[str, Any] | None:
    """
    Metadata for a tail rule, or ``None`` when the level is inside measured support.

    Exposes the requested level, the boundary level used, the per-step ratio and
    the number of steps so callers can emit a visible, never-silent warning.
    """
    region, boundary, steps = classify_dynamic_support(dynamic, measured_support)
    if region == "interior":
        return None
    from config import DYN_TAIL_RATIO_LOUD, DYN_TAIL_RATIO_SOFT

    ratio = DYN_TAIL_RATIO_SOFT if region == "soft_tail" else DYN_TAIL_RATIO_LOUD
    return {
        "region": region,
        "requested_level": (dynamic or "mf").strip().lower(),
        "boundary_level": boundary,
        "ratio": float(ratio),
        "steps": int(steps),
    }


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
        return _apply_saturating_tails(result, pp_values, ff_values)
    except Exception as exc:
        log.error("Error predicting intermediate dynamics: %s", exc)
        return {d: np.zeros_like(pp_values, dtype=float) for d in all_dynamics}


def _apply_saturating_tails(
    predictions: dict[str, np.ndarray],
    pp_values: list[float] | np.ndarray,
    ff_values: list[float] | np.ndarray,
) -> dict[str, np.ndarray]:
    """
    Replace out-of-support tail predictions with saturating log-domain extrapolation.

    Interior (in-support) predictions are returned unchanged. Soft-tail levels
    saturate down from the measured pp boundary; loud-tail levels saturate up
    from the measured ff boundary. Strictly positive and monotone by algebra.
    """
    from config import DENSITY_FLOOR, DYN_TAIL_RATIO_LOUD, DYN_TAIL_RATIO_SOFT

    pp_arr = np.asarray(pp_values, dtype=float)
    ff_arr = np.asarray(ff_values, dtype=float)

    for dynamic in list(predictions.keys()):
        region, _boundary, steps = classify_dynamic_support(dynamic)
        if region == "soft_tail":
            boundary_arr = pp_arr
            values = pp_arr * (DYN_TAIL_RATIO_SOFT ** steps)
        elif region == "loud_tail":
            boundary_arr = ff_arr
            values = ff_arr * (DYN_TAIL_RATIO_LOUD ** steps)
        else:
            continue  # interior: GPR output unchanged
        # Unreachable safety assert: whenever the measured boundary is positive
        # the saturating construction is strictly positive. This guards against a
        # future regression; it is NOT the positivity mechanism.
        assert np.all(values[boundary_arr > 0] >= DENSITY_FLOOR), (
            f"saturated tail density below floor for {dynamic!r}"
        )
        predictions[dynamic] = np.asarray(values, dtype=float)
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
