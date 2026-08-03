"""Task 8c: unified composite (blend × mass) — property acceptance tests."""

from __future__ import annotations

import math

import pytest

from config import MAX_DENS_GLOBAL
from core.formatting import format_output_string
from core.pipeline import calculate_metrics
from core.request import AnalysisRequest


def _total(
    notes: tuple[str, ...],
    dynamics: tuple[str, ...],
    instruments: tuple[str, ...],
    qtys: tuple[int, ...] | None = None,
    w: float = 0.5,
) -> float:
    req = AnalysisRequest(
        notes=notes,
        dynamics=dynamics,
        instruments=instruments,
        num_instruments=qtys or tuple(1 for _ in notes),
        weight_factor=w,
    )
    return float(calculate_metrics(req)[0]["density"]["total"])


def _result(notes, dynamics, instruments, qtys=None, w=0.5):
    return calculate_metrics(
        AnalysisRequest(
            notes=notes,
            dynamics=dynamics,
            instruments=instruments,
            num_instruments=qtys or tuple(1 for _ in notes),
            weight_factor=w,
        )
    )[0]


@pytest.mark.parametrize(
    "base,addition",
    [
        (
            (("C4",), ("mf",), ("Violin",), (1,)),
            ("E4", "mf", "Violin", 1),
        ),
        (
            (("C4", "E4"), ("mf", "mf"), ("Violin", "Violin"), (1, 1)),
            ("C5", "fff", "Cymbals", 1),
        ),
        (
            (("C5",), ("fff",), ("Cymbals",), (1,)),
            ("D2", "fff", "Bass drum", 1),
        ),
        (
            (("C2", "D2"), ("ffff", "ffff"), ("Tam-tam", "Bass drum"), (1, 1)),
            ("C2", "mf", "Cello", 1),
        ),
        (
            (("C4", "C#4", "D4"), ("mf", "mf", "mf"), ("Flute", "Flute", "Flute"), (1, 1, 1)),
            ("C6", "mf", "Flute", 1),
        ),
    ],
)
def test_composite_monotone_under_event_addition(base, addition):
    notes, dyns, insts, qtys = [list(x) for x in base]
    before = _total(tuple(notes), tuple(dyns), tuple(insts), tuple(qtys))
    n, d, i, q = addition
    notes.append(n)
    dyns.append(d)
    insts.append(i)
    qtys.append(q)
    after = _total(tuple(notes), tuple(dyns), tuple(insts), tuple(qtys))
    assert after + 1e-12 >= before


def test_composite_monotone_under_qty_increase():
    a = _total(("C4",), ("mf",), ("Violin",), (1,))
    b = _total(("C4",), ("mf",), ("Violin",), (3,))
    assert b + 1e-12 >= a


def test_screenshot_subset_order_mixed_dominates_parts():
    """mixed > pitched-only subset and mixed > unpitched-only subset."""
    pitched = _total(
        ("C2", "E2", "G2"),
        ("mf", "mf", "mf"),
        ("Cello", "Cello", "Cello"),
    )
    unpitched = _total(
        ("C2", "D2"),
        ("ffff", "ffff"),
        ("Tam-tam", "Bass drum"),
    )
    mixed = _total(
        ("C2", "E2", "G2", "C2", "D2"),
        ("mf", "mf", "mf", "ffff", "ffff"),
        ("Cello", "Cello", "Cello", "Tam-tam", "Bass drum"),
    )
    assert mixed > pitched
    assert mixed > unpitched
    # Comparable scale: all on the log-blend path (no raw-orchestral outlier).
    assert max(pitched, unpitched, mixed) < 1.0
    assert min(pitched, unpitched, mixed) > 0.0


def test_continuity_removing_last_pitched_no_large_jump():
    """Dropping the last pitched event must not jump more than that event's lift."""
    with_pitched = _result(
        ("C5", "D2", "C4"),
        ("fff", "fff", "mf"),
        ("Cymbals", "Bass drum", "Violin"),
    )
    without = _result(
        ("C5", "D2"),
        ("fff", "fff"),
        ("Cymbals", "Bass drum"),
    )
    pitched_only = _result(("C4",), ("mf",), ("Violin",))
    c_with = float(with_pitched["density"]["total"])
    c_without = float(without["density"]["total"])
    c_solo = float(pitched_only["density"]["total"])
    drop = c_with - c_without
    # Drop is non-negative (monotonicity) and not larger than the solo pitched
    # composite plus a small numerical slack (no discontinuous fallback jump).
    assert drop >= -1e-12
    assert drop <= c_solo + 1e-6


def test_no_event_kind_fallback_mode():
    r = _result(("C2", "D2"), ("ffff", "ffff"), ("Tam-tam", "Bass drum"))
    assert r["composite_meta"]["mode"] == "weighted_blend_mass_log"
    assert r["composite_meta"]["normalization_ref"] == pytest.approx(MAX_DENS_GLOBAL)
    # Must equal the unified formula, not raw weighted orchestral.
    w = float(r["density"]["weighted"])
    m = float(r["density"]["sonic_mass"])
    expected = math.log10(1.0 + w * math.sqrt(m) / MAX_DENS_GLOBAL)
    assert float(r["density"]["total"]) == pytest.approx(expected, rel=1e-12)
    assert float(r["density"]["total"]) != pytest.approx(
        float(r["density"]["weighted_orchestral"]), rel=1e-3
    )


def test_header_prints_single_formula_with_w_and_ref():
    r = _result(("C4", "E4"), ("mf", "mf"), ("Violin", "Violin"))
    text = format_output_string(r)
    assert "Composite: log10(1 + D_blend·√M / REF)" in text
    assert f"REF={MAX_DENS_GLOBAL:g}" in text
    assert "w=0.5" in text
    assert "fallback" not in text.lower()


def test_unpitched_only_spectral_section_na():
    r = _result(("C2", "D2"), ("ffff", "ffff"), ("Tam-tam", "Bass drum"))
    text = format_output_string(r)
    assert "n/a — no pitched content" in text
    assert "Invalid" not in text
    assert "0.00 Hz" not in text
