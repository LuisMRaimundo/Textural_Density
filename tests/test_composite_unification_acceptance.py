"""
Acceptance freeze for Task 8c composite unification (GUI validation chain).

Documents the six progressive slices used to verify blend×mass unification:
  5 strings ff → +bass drum → +cymbals → +flute/oboe ffff → +tam-tam ffff
  → Qty expansion 4/5/5/3/10 on the strings (others Qty=1).

Goldens are live pipeline totals at w=0.5, REF=193. Refrozen 2026-08-25 after
committing dest-Zenodo IOWA+ORCH midpoint CDM ladders (measured pp/mf/ff
anchors, PCHIP interiors) for ordinary-sustain table-backed instruments.
Player Count 32 / Player Doubling 22 unchanged.
"""

from __future__ import annotations

import math
import re

import pytest

from config import MAX_DENS_GLOBAL, USE_LOG_COMPRESSION
from core.composite import (
    BLEND_SCALE,
    WEIGHTED_DI_MAX,
    WEIGHTED_DV_MAX,
    compute_blend_density,
    compute_composite_from_blend,
)
from core.formatting import format_output_string
from core.pipeline import calculate_metrics
from core.request import AnalysisRequest
from core.unpitched_labels import format_unpitched_exclusion_note

# --- fixture: progressive GUI chain -------------------------------------------------

STRING_NOTES = ("B3", "D4", "G3", "D3", "G2")
STRING_INSTS = ("Violin", "Violin", "Viola", "Cello", "Double bass")
STRING_DYNS = ("ff",) * 5

SLICES: list[dict] = [
    {
        "label": "5 strings ff",
        "notes": STRING_NOTES,
        "dynamics": STRING_DYNS,
        "instruments": STRING_INSTS,
        "qtys": (1, 1, 1, 1, 1),
        "expected_total": 0.11097263710915733,
    },
    {
        "label": "+bass drum",
        "notes": STRING_NOTES + ("D2",),
        "dynamics": STRING_DYNS + ("ff",),
        "instruments": STRING_INSTS + ("Bass drum",),
        "qtys": (1, 1, 1, 1, 1, 1),
        "expected_total": 0.12076759726730982,
    },
    {
        "label": "+cymbals",
        "notes": STRING_NOTES + ("D2", "C5"),
        "dynamics": STRING_DYNS + ("ff", "ff"),
        "instruments": STRING_INSTS + ("Bass drum", "Cymbals"),
        "qtys": (1, 1, 1, 1, 1, 1, 1),
        "expected_total": 0.12909176148013493,
    },
    {
        "label": "+flute/oboe ffff",
        "notes": STRING_NOTES + ("D2", "C5", "D5", "G5"),
        "dynamics": STRING_DYNS + ("ff", "ff", "ffff", "ffff"),
        "instruments": STRING_INSTS + ("Bass drum", "Cymbals", "Flute", "Oboe"),
        "qtys": (1, 1, 1, 1, 1, 1, 1, 1, 1),
        "expected_total": 0.14015473034620063,
    },
    {
        "label": "+tam-tam ffff",
        "notes": STRING_NOTES + ("D2", "C5", "D5", "G5", "C2"),
        "dynamics": STRING_DYNS + ("ff", "ff", "ffff", "ffff", "ffff"),
        "instruments": STRING_INSTS
        + ("Bass drum", "Cymbals", "Flute", "Oboe", "Tam-tam"),
        "qtys": (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        "expected_total": 0.14692821688654636,
    },
    {
        "label": "Qty expansion 4/5/5/3/10",
        "notes": STRING_NOTES + ("D2", "C5", "D5", "G5", "C2"),
        "dynamics": STRING_DYNS + ("ff", "ff", "ffff", "ffff", "ffff"),
        "instruments": STRING_INSTS
        + ("Bass drum", "Cymbals", "Flute", "Oboe", "Tam-tam"),
        "qtys": (4, 5, 5, 3, 10, 1, 1, 1, 1, 1),
        "expected_total": 0.4067549748899126,
    },
]

TOL = 5e-5


def _result(slice_def: dict):
    return calculate_metrics(
        AnalysisRequest(
            notes=slice_def["notes"],
            dynamics=slice_def["dynamics"],
            instruments=slice_def["instruments"],
            num_instruments=slice_def["qtys"],
            weight_factor=0.5,
        )
    )[0]


@pytest.fixture(scope="module")
def chain_results():
    return [_result(s) for s in SLICES]


def test_composite_values_match_acceptance_goldens(chain_results):
    for s, r in zip(SLICES, chain_results):
        got = float(r["density"]["total"])
        assert got == pytest.approx(s["expected_total"], abs=TOL), s["label"]


def test_strict_monotone_increase_along_chain(chain_results):
    totals = [float(r["density"]["total"]) for r in chain_results]
    for i in range(1, len(totals)):
        assert totals[i] > totals[i - 1] + 1e-12


def test_final_slice_player_counts(chain_results):
    agg = chain_results[-1]["pitch_aggregation"]
    assert int(agg["player_count"]) == 32
    assert int(agg["player_doubling_count"]) == 22


def test_pitch_block_invariant_under_qty_expansion(chain_results):
    """All pitch / spectral / timbre-variance metrics bit-identical across Qty pair."""
    before, after = chain_results[-2], chain_results[-1]
    pitch_keys = (
        "interval",
        "pitch_structure",
        "refined",
    )
    for key in pitch_keys:
        assert before["density"][key] == after["density"][key]

    for key in ("centroid", "spread", "skewness", "kurtosis", "flatness", "rolloff"):
        b, a = before["spectral_moments"].get(key), after["spectral_moments"].get(key)
        assert b == a

    assert before["spectral_moments"].get("spectral_entropy") == after[
        "spectral_moments"
    ].get("spectral_entropy")
    assert before["additional_metrics"].get("harmonic_ratio") == after[
        "additional_metrics"
    ].get("harmonic_ratio")
    assert before["additional_metrics"].get("complexity") == after[
        "additional_metrics"
    ].get("complexity")
    assert before["timbre"].get("density_variance") == after["timbre"].get(
        "density_variance"
    )


UNPITCHED_ONLY = {
    "label": "unpitched-only",
    "notes": ("D2", "C5"),
    "dynamics": ("ffff", "ffff"),
    "instruments": ("Bass drum", "Cymbals"),
    "qtys": (1, 1),
}


@pytest.mark.parametrize(
    "slice_def",
    [SLICES[0], UNPITCHED_ONLY, SLICES[4]],
    ids=["pitched-only", "unpitched-only", "mixed"],
)
def test_header_formula_evaluates_to_reported_composite(slice_def):
    """Parse printed header; eval with DI, DV, M, w, REF → Composite within 1e-6."""
    r = _result(slice_def)
    text = format_output_string(r)
    header = next(ln for ln in text.splitlines() if ln.startswith("Composite:"))

    assert "D_blend=" in header
    assert f"REF={MAX_DENS_GLOBAL:g}" in header

    m = re.search(
        r"w=(?P<w>[0-9.]+), REF=(?P<ref>[0-9.]+), "
        r"D_blend=(?P<d_blend>[0-9.]+), M=(?P<M>[0-9.]+)",
        header,
    )
    assert m, header
    w = float(m.group("w"))
    ref = float(m.group("ref"))
    d_blend_printed = float(m.group("d_blend"))
    sonic_mass = float(m.group("M"))

    di = float(r["density"]["instrument"])
    dv = float(r["density"]["interval"])
    d_blend = compute_blend_density(
        di, dv, w, DI_max=WEIGHTED_DI_MAX, DV_max=WEIGHTED_DV_MAX, scale=BLEND_SCALE
    )
    assert d_blend == pytest.approx(d_blend_printed, abs=5e-5)
    assert d_blend == pytest.approx(float(r["density"]["weighted"]), rel=1e-12)

    # Evaluate the blend definition substring from the header (last "(D_blend = …)").
    blend_def = re.search(r"\(D_blend = (.+)\)$", header)
    assert blend_def, header
    expr = blend_def.group(1)
    # Safe eval over the printed definition with DI, DV, w bound.
    local = {"w": w, "DI": di, "DV": dv}
    d_blend_from_label = float(eval(expr, {"__builtins__": {}}, local))  # noqa: S307
    assert d_blend_from_label == pytest.approx(d_blend, rel=1e-12)

    composite_from_label = compute_composite_from_blend(
        d_blend_from_label,
        sonic_mass,
        ref,
        use_log_compression=USE_LOG_COMPRESSION,
    )
    # Also eval the outer skeleton with bound symbols.
    outer = re.match(r"Composite: (.+) with w=", header)
    assert outer, header
    outer_expr = outer.group(1)
    outer_val = float(
        eval(  # noqa: S307
            outer_expr,
            {"__builtins__": {}, "log10": math.log10, "sqrt": math.sqrt},
            {"D_blend": d_blend_from_label, "M": sonic_mass, "REF": ref},
        )
    )
    reported = float(r["density"]["total"])
    assert composite_from_label == pytest.approx(reported, abs=1e-6)
    assert outer_val == pytest.approx(reported, abs=1e-6)


def test_unpitched_exclusion_singular_plural():
    assert format_unpitched_exclusion_note(1).startswith("1 unpitched event excluded")
    assert format_unpitched_exclusion_note(2).startswith("2 unpitched events excluded")
    r = _result(SLICES[1])  # one unpitched
    text = format_output_string(r)
    assert "1 unpitched event excluded from pitch metrics by type" in text
    assert "1 unpitched events excluded" not in text
