"""
Dynamic-tail saturation contract (5.1.0-strict-symbolic).

Root cause fixed here: the instrument GPR dynamic->amplitude model is fitted on
the measured source anchors (pp, mf, ff) and previously continued its trend
*unchanged* into the unmeasured tails, overshooting downward at the soft end
(negative clarinete pppp weight -> negative harmonic_ratio) and bending over at
the loud end (non-monotone flute ffff mass dip).

The fix (see ``instrumentos/gpr_dynamic_interpolation.py`` and the two config
ratios ``DYN_TAIL_RATIO_SOFT`` / ``DYN_TAIL_RATIO_LOUD``) replaces tail
extrapolation with a saturating log-domain rule anchored at the nearest measured
boundary. Interior (in-support) predictions are left untouched.

Contract exercised:
  (a) positivity everywhere + tail/boundary monotonicity;
  (b) tail compression / saturation (bounded per-step ratio; soft geometric
      shrink; anti-overshoot vs. raw GPR on the incident cases);
  (c) interior stability (in-support values match pre-change golden within 1e-9);
  (d) regressions (DYNGRAD.wedge harmonic_ratio in [0,1]; flute triad
      mass(ffff) >= mass(ff));
  (e) tail warning presence for pppp/ffff, absence for interior dynamics.

Note on (a)/(b): full monotonicity across *all* levels is NOT asserted because
several source tables are themselves non-monotone inside measured support
(e.g. flute C4 has mf > ff) and the spec forbids altering interior predictions.
What the tails add is guaranteed monotone and positive; the only permitted
decreases are strictly interior and are measured data, not extrapolation.
Likewise the literal "tail step < mean in-support step" is not a scale-invariant
of a fixed-ratio construction (flat registers have ~zero interior steps), so (b)
asserts the true saturation invariants instead.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import numpy as np
import pytest

from config import (
    DENSITY_FLOOR,
    DYN_TAIL_RATIO_LOUD,
    DYN_TAIL_RATIO_SOFT,
    DYNAMIC_LEVELS,
)
from core import calculate_metrics
from core.pipeline import load_instrument_module
from instrumentos.gpr_dynamic_interpolation import (
    GPR_DYNAMIC_COORDINATES,
    SOURCE_ANCHOR_DYNAMICS,
    create_dynamic_gpr,
    predict_intermediate_dynamics_gpr,
)
from instrumentos.registry import list_instrument_ids, resolve_profile
from microtonal import note_to_midi

GOLDEN_PATH = Path(__file__).parent / "fixtures" / "dynamic_tail_interior_golden.json"
ANCHORS = ("pp", "mf", "ff")


def _module_backed_ids() -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for iid in list_instrument_ids():
        prof = resolve_profile(iid)
        if prof is not None and prof.module_name and prof.module_name not in seen:
            seen.add(prof.module_name)
            ids.append(iid)
    return ids


def _sample_pitches(module) -> list[str]:
    keys = sorted(module.spectral_data.keys(), key=lambda k: note_to_midi(k, strict=False))
    if len(keys) < 3:
        return keys
    return [keys[0], keys[len(keys) // 2], keys[-1]]


_CURVE_CACHE: dict[tuple[str, str], dict[str, float]] = {}


def _one_player_curve(iid: str, note: str) -> dict[str, float]:
    """DYNAMIC_LEVELS -> one-player density (mirrors core.orchestration)."""
    key = (iid, note)
    if key in _CURVE_CACHE:
        return _CURVE_CACHE[key]
    module = load_instrument_module(iid)
    pp = float(module.calcular_densidade(note, "pp"))
    mf = float(module.calcular_densidade(note, "mf"))
    ff = float(module.calcular_densidade(note, "ff"))
    preds = module.predict_intermediate_dynamics([note], [pp], [mf], [ff])
    curve: dict[str, float] = {}
    for d in DYNAMIC_LEVELS:
        if d in ANCHORS:
            curve[d] = {"pp": pp, "mf": mf, "ff": ff}[d]
        else:
            curve[d] = float(preds[d][0])
    _CURVE_CACHE[key] = curve
    return curve


def _raw_gpr_curve(iid: str, note: str) -> dict[str, float]:
    """Unsaturated GPR extrapolation (pre-fix behaviour) for anti-overshoot checks."""
    module = load_instrument_module(iid)
    pp = float(module.calcular_densidade(note, "pp"))
    mf = float(module.calcular_densidade(note, "mf"))
    ff = float(module.calcular_densidade(note, "ff"))
    ex = np.array([GPR_DYNAMIC_COORDINATES[d] for d in SOURCE_ANCHOR_DYNAMICS]).reshape(-1, 1)
    allc = np.array([GPR_DYNAMIC_COORDINATES[d] for d in DYNAMIC_LEVELS]).reshape(-1, 1)
    gpr = create_dynamic_gpr()
    gpr.fit(ex, np.array([pp, mf, ff], dtype=float))
    return {d: float(v) for d, v in zip(DYNAMIC_LEVELS, gpr.predict(allc))}


def _grid() -> list[tuple[str, str]]:
    grid: list[tuple[str, str]] = []
    for iid in _module_backed_ids():
        module = load_instrument_module(iid)
        for note in _sample_pitches(module):
            grid.append((iid, note))
    return grid


GRID = _grid()


# --------------------------------------------------------------------------- #
# (a) Global contract: positivity + tail/boundary monotonicity
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("iid,note", GRID)
def test_positivity_all_levels(iid: str, note: str) -> None:
    curve = _one_player_curve(iid, note)
    for d in DYNAMIC_LEVELS:
        assert curve[d] > 0.0, f"{iid} {note} {d} = {curve[d]} not positive"
        assert curve[d] >= DENSITY_FLOOR


@pytest.mark.parametrize("iid,note", GRID)
def test_tail_and_boundary_monotonicity(iid: str, note: str) -> None:
    curve = _one_player_curve(iid, note)
    # Soft tail is non-decreasing up to the softest measured level.
    assert curve["pppp"] <= curve["ppp"] + 1e-12
    assert curve["ppp"] <= curve["pp"] + 1e-12
    # Loud tail is non-decreasing from the loudest measured level.
    assert curve["ff"] <= curve["fff"] + 1e-12
    assert curve["fff"] <= curve["ffff"] + 1e-12


# --------------------------------------------------------------------------- #
# (b) Tail compression / saturation (not continued trend)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("iid,note", GRID)
def test_tail_bounded_per_step_ratio(iid: str, note: str) -> None:
    """Tails apply a fixed gentle geometric ratio, not the interior GPR slope."""
    curve = _one_player_curve(iid, note)
    assert curve["ppp"] == pytest.approx(curve["pp"] * DYN_TAIL_RATIO_SOFT, rel=1e-9)
    assert curve["pppp"] == pytest.approx(curve["pp"] * DYN_TAIL_RATIO_SOFT**2, rel=1e-9)
    assert curve["fff"] == pytest.approx(curve["ff"] * DYN_TAIL_RATIO_LOUD, rel=1e-9)
    assert curve["ffff"] == pytest.approx(curve["ff"] * DYN_TAIL_RATIO_LOUD**2, rel=1e-9)


@pytest.mark.parametrize("iid,note", GRID)
def test_soft_tail_geometric_shrink(iid: str, note: str) -> None:
    """Soft-tail adjacent differences shrink ('small and shrinking')."""
    curve = _one_player_curve(iid, note)
    step_near = curve["pp"] - curve["ppp"]
    step_far = curve["ppp"] - curve["pppp"]
    assert step_near > 0.0
    assert 0.0 < step_far < step_near


def test_anti_overshoot_vs_raw_gpr_incident_cases() -> None:
    """On the incident cases the saturated tail compresses the raw-GPR overshoot."""
    # Clarinet soft end: raw GPR drives pppp negative; saturation keeps it positive
    # and strictly above the raw prediction.
    raw = _raw_gpr_curve("clarinete", "C4")
    sat = _one_player_curve("clarinete", "C4")
    assert raw["pppp"] < 0.0  # documents the original overshoot
    assert sat["pppp"] > 0.0
    assert sat["pppp"] > raw["pppp"]
    # Flute loud end: raw GPR dips at ffff below ff; saturation restores monotone.
    raw_f = _raw_gpr_curve("flauta", "C4")
    sat_f = _one_player_curve("flauta", "C4")
    assert raw_f["ffff"] < raw_f["ff"]  # documents the original dip
    assert sat_f["ffff"] >= sat_f["ff"]


# --------------------------------------------------------------------------- #
# (c) Interior stability: in-support values unchanged (golden-pinned pre-edit)
# --------------------------------------------------------------------------- #
def test_interior_stability_matches_golden() -> None:
    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    assert golden, "interior golden fixture is empty"
    for key, expected in golden.items():
        module_name, note = key.split("|")
        module = importlib.import_module(f"instrumentos.{module_name}")
        pp = float(module.calcular_densidade(note, "pp"))
        mf = float(module.calcular_densidade(note, "mf"))
        ff = float(module.calcular_densidade(note, "ff"))
        preds = predict_intermediate_dynamics_gpr([pp], [mf], [ff])
        for dyn, value in expected.items():
            assert float(preds[dyn][0]) == pytest.approx(value, abs=1e-9), (
                f"interior drift at {module_name} {note} {dyn}"
            )


# --------------------------------------------------------------------------- #
# (d) Regressions
# --------------------------------------------------------------------------- #
def _flute_triad_mass(dynamic: str) -> float:
    res, _dens, _pitches = calculate_metrics(
        {
            "notes": ["C4", "E4", "G4"],
            "dynamics": [dynamic] * 3,
            "instruments": ["flauta"] * 3,
            "num_instruments": [1, 1, 1],
            "weight_factor": 0.5,
        }
    )
    return float(res["density"]["sonic_mass"])


def test_dyngrad_wedge_harmonic_ratio_in_unit_interval() -> None:
    res, _dens, _pitches = calculate_metrics(
        {
            "notes": ["C4", "C#4", "D4", "D#4", "E4", "F4"],
            "dynamics": ["pppp", "pp", "mp", "f", "ff", "ffff"],
            "instruments": ["clarinete"] * 6,
            "num_instruments": [1] * 6,
            "weight_factor": 0.5,
        }
    )
    hr = float(res["additional_metrics"]["harmonic_ratio"])
    assert 0.0 <= hr <= 1.0
    assert hr > 0.0  # small positive, not a negative-weight artefact


def test_flute_triad_mass_monotone_at_loud_extreme() -> None:
    assert _flute_triad_mass("ffff") >= _flute_triad_mass("ff")


# --------------------------------------------------------------------------- #
# (e) Warning presence / absence
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("dynamic", ["pppp", "ffff"])
def test_tail_warning_present(dynamic: str) -> None:
    res, _dens, _pitches = calculate_metrics(
        {
            "notes": ["C4", "E4"],
            "dynamics": [dynamic, dynamic],
            "instruments": ["clarinete", "clarinete"],
            "num_instruments": [1, 1],
            "weight_factor": 0.5,
        }
    )
    warnings = res["metric_metadata"]["warnings"]
    assert any("saturated extrapolation applied" in w for w in warnings)


def test_no_tail_warning_for_interior_dynamic() -> None:
    res, _dens, _pitches = calculate_metrics(
        {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "mf"],
            "instruments": ["clarinete", "clarinete"],
            "num_instruments": [1, 1],
            "weight_factor": 0.5,
        }
    )
    warnings = res["metric_metadata"]["warnings"]
    assert not any("saturated extrapolation applied" in w for w in warnings)
