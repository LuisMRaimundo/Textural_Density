"""
Extensive composite vertical density — monotonicity acceptance tests
(5.0.0-strict-symbolic).

Regression guard for the defect where ``density.total`` *decreased* when a
distinct note was added to a sonority. After the fix, the pitch-structure
aggregate is built from the raw accumulating pairwise interval sum (extensive,
non-decreasing on distinct-note addition) while the reported compactness axis
(``density.interval``) remains intensive (mean-per-pair, falls with spread).

Public entry point only: ``from core import calculate_metrics``.
All events ``mf`` / ``Qty 1`` unless stated otherwise.
"""

from __future__ import annotations

import math

import pytest

from core import calculate_metrics


def _metrics(notes, instruments, dynamics=None, num_instruments=None):
    n = len(notes)
    data = {
        "notes": notes,
        "dynamics": dynamics if dynamics is not None else ["mf"] * n,
        "instruments": instruments,
        "num_instruments": num_instruments if num_instruments is not None else [1] * n,
        "weight_factor": 0.5,
        "save_results": False,
        "show_graphs": False,
    }
    resultados, _, _ = calculate_metrics(data)
    return resultados["density"]


def test_no_decrease_on_note_addition():
    """Adding distinct notes never decreases total or pitch_structure density."""
    a = _metrics(["C4", "D4", "E4"], ["Trumpet"] * 3)
    b = _metrics(["C4", "D4", "E4", "F4", "A#4"], ["Trumpet"] * 5)
    c = _metrics(
        ["C4", "D4", "E4", "F4", "A#4", "E1"],
        ["Trumpet"] * 5 + ["Double bass"],
    )

    assert a["total"] <= b["total"] <= c["total"]
    assert a["pitch_structure"] <= b["pitch_structure"] <= c["pitch_structure"]


def test_register_isolated_bass_never_lowers_total():
    """A far-below bass note added to a cluster does not lower the total."""
    without_bass = _metrics(["C4", "D4", "E4", "F4", "A#4"], ["Trumpet"] * 5)
    with_bass = _metrics(
        ["C4", "D4", "E4", "F4", "A#4", "E1"],
        ["Trumpet"] * 5 + ["Double bass"],
    )
    assert with_bass["total"] >= without_bass["total"]


def test_compactness_axis_remains_intensive():
    """Reported density.interval (compactness) stays intensive: tight > wide."""
    tight = _metrics(["C4", "C#4", "D4"], ["Flute"] * 3)
    wide = _metrics(["C4", "E5", "C7"], ["Flute"] * 3)
    assert tight["interval"] > wide["interval"]


def test_unison_doubling_invariance_preserved():
    """Exact unison doubling must not change pitch_structure density."""
    base = _metrics(["C4", "E4", "G4"], ["Flute"] * 3)
    doubled = _metrics(["C4", "C4", "E4", "G4"], ["Flute"] * 4)
    assert doubled["pitch_structure"] == pytest.approx(base["pitch_structure"], abs=1e-9)


def test_two_note_minimum_preserved():
    """A single distinct pitch yields zero pitch_structure density."""
    single = _metrics(["C4"], ["Flute"])
    assert single["pitch_structure"] == 0.0


def test_all_density_scalars_finite():
    """Every density.* scalar is finite across the acceptance cases."""
    cases = [
        (["C4", "D4", "E4"], ["Trumpet"] * 3),
        (["C4", "D4", "E4", "F4", "A#4"], ["Trumpet"] * 5),
        (["C4", "D4", "E4", "F4", "A#4", "E1"], ["Trumpet"] * 5 + ["Double bass"]),
        (["C4", "C#4", "D4"], ["Flute"] * 3),
        (["C4", "E5", "C7"], ["Flute"] * 3),
        (["C4", "C4", "E4", "G4"], ["Flute"] * 4),
        (["C4"], ["Flute"]),
    ]
    for notes, instruments in cases:
        density = _metrics(notes, instruments)
        for key, value in density.items():
            if isinstance(value, (int, float)):
                assert math.isfinite(float(value)), f"{key} not finite for {notes}"
