"""C1/C2: unit_range is opt-in; legacy default stays bit-identical."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from core.composite import (
    WEIGHTED_DI_MAX,
    WEIGHTED_DV_MAX,
    blend_term_contributions,
    compute_blend_density,
    resolve_interval_dv_max,
)
from core.defaults import apply_research_defaults
from core.pipeline import calculate_metrics

SNAPSHOT = (
    Path(__file__).resolve().parent
    / "snapshots"
    / "numeric_outputs"
    / "synthetic_triad.json"
)
META = (
    Path(__file__).resolve().parents[1]
    / "replication"
    / "corpus"
    / "metadata"
    / "synthetic_triad.json"
)
CONFIG = (
    Path(__file__).resolve().parents[1]
    / "replication"
    / "configs"
    / "score_only_default.json"
)


def test_legacy_resolve_keeps_weighted_dv_max():
    assert resolve_interval_dv_max() == WEIGHTED_DV_MAX


def test_legacy_blend_matches_committed_triad_weighted():
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    di = float(snap["density"]["instrument"])
    dv = float(snap["density"]["interval"])
    blend = compute_blend_density(di, dv, w=0.5)
    assert blend == pytest.approx(float(snap["density"]["weighted"]), abs=1e-12)


def test_unit_range_rescales_dv_only(monkeypatch):
    import config as cfg

    monkeypatch.setattr(cfg, "INTERVAL_BLEND_NORMALISATION", "unit_range")
    monkeypatch.setattr(cfg, "USE_LOG_COMPRESSION", True)
    dv_max = resolve_interval_dv_max()
    assert dv_max == pytest.approx(math.log10(2.0), abs=1e-12)
    di, dv, w = 34.5, 0.2137588382139519, 0.5
    legacy = 10.0 * (w * di / WEIGHTED_DI_MAX + (1.0 - w) * dv / WEIGHTED_DV_MAX)
    unit = compute_blend_density(di, dv, w=w)
    expected = 10.0 * (w * di / WEIGHTED_DI_MAX + (1.0 - w) * dv / math.log10(2.0))
    assert unit == pytest.approx(expected, abs=1e-12)
    assert unit != pytest.approx(legacy, rel=1e-3)


def test_pipeline_emits_blend_term_contributions():
    meta = json.loads(META.read_text(encoding="utf-8"))
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    input_data = apply_research_defaults({**cfg, **meta.get("input", {})})
    resultados, _, _ = calculate_metrics(input_data)
    terms = resultados["composite_meta"]["blend_term_contributions"]
    assert terms["interval_blend_normalisation"] == "legacy"
    assert terms["instrument_term"] == pytest.approx(
        float(resultados["density"]["weighted_orchestral"]), abs=1e-12
    )
    assert terms["interval_term"] == pytest.approx(
        float(resultados["density"]["weighted_pitch"]), abs=1e-12
    )
    # Density fields stay on the committed snapshot values.
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    orch = float(snap["density"]["weighted_orchestral"])
    pitch = float(snap["density"]["weighted_pitch"])
    assert terms["instrument_to_interval_ratio"] == pytest.approx(orch / pitch, abs=0.05)
    assert float(resultados["density"]["total"]) == pytest.approx(
        float(snap["density"]["total"]), abs=1e-12
    )


def test_blend_term_contributions_helper_matches_blend():
    di, dv, w = 40.0, 0.2, 0.5
    terms = blend_term_contributions(DI=di, DV=dv, w=w)
    assert terms["instrument_term"] + terms["interval_term"] == pytest.approx(
        compute_blend_density(di, dv, w=w), abs=1e-12
    )


def test_ratio_is_null_when_interval_term_is_zero():
    zero_dv = blend_term_contributions(DI=34.5, DV=0.0, w=0.5)
    full_w = blend_term_contributions(DI=34.5, DV=0.2, w=1.0)
    assert zero_dv["interval_term"] == 0.0
    assert full_w["interval_term"] == 0.0
    assert zero_dv["instrument_to_interval_ratio"] is None
    assert full_w["instrument_to_interval_ratio"] is None


def test_ratio_null_survives_json_without_nan_or_inf():
    terms = blend_term_contributions(DI=10.0, DV=0.0, w=0.5)
    payload = json.dumps(terms, allow_nan=False)
    loaded = json.loads(payload)
    assert "inf" not in payload.lower()
    assert "nan" not in payload.lower()
    assert loaded["instrument_to_interval_ratio"] is None


def test_monophonic_slice_emits_json_null_ratio():
    input_data = apply_research_defaults(
        {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
        }
    )
    resultados, _, _ = calculate_metrics(input_data)
    terms = resultados["composite_meta"]["blend_term_contributions"]
    assert float(resultados["density"]["interval"]) == 0.0
    assert terms["instrument_to_interval_ratio"] is None
    dumped = json.dumps(resultados["composite_meta"], allow_nan=False)
    assert json.loads(dumped)["blend_term_contributions"][
        "instrument_to_interval_ratio"
    ] is None
