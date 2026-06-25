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

_LOG = logging.getLogger(__name__)


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

        return {k: np.array(v, dtype=float) for k, v in predictions.items()}
    except Exception as exc:
        log.error("Error predicting intermediate dynamics: %s", exc)
        return {d: np.zeros_like(pp_values, dtype=float) for d in all_dynamics}


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
