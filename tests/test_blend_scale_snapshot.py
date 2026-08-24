"""A2: committed triad snapshot encodes the DV/10 vs DI/100 scale mismatch."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.composite import WEIGHTED_DI_MAX, WEIGHTED_DV_MAX

SNAPSHOT = (
    Path(__file__).resolve().parent
    / "snapshots"
    / "numeric_outputs"
    / "synthetic_triad.json"
)


def test_synthetic_triad_weighted_orch_over_pitch_ratio():
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    orch = float(snap["density"]["weighted_orchestral"])
    pitch = float(snap["density"]["weighted_pitch"])
    di = float(snap["density"]["instrument"])
    dv = float(snap["density"]["interval"])

    assert WEIGHTED_DI_MAX == 100.0
    assert WEIGHTED_DV_MAX == 10.0
    # At w=0.5: orch = 0.5 * DI/10, pitch = 0.5 * DV; ratio = (DI/10)/DV.
    assert orch / pitch == pytest.approx((di / 10.0) / dv, rel=1e-12)
