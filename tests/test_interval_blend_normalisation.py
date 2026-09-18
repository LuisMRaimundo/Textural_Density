"""Fixed-divisor blend: w*(DI/10) + (1-w)*DV."""

from __future__ import annotations

import json

import pytest

from core.composite import (
    INSTRUMENT_BLEND_DIVISOR,
    blend_term_contributions,
    compute_blend_density,
)
from core.defaults import apply_research_defaults
from core.pipeline import calculate_metrics


def test_blend_is_direct_fixed_divisor():
    di, dv, w = 34.5, 1.85, 0.5
    assert compute_blend_density(di, dv, w=w) == pytest.approx(
        w * di / INSTRUMENT_BLEND_DIVISOR + (1.0 - w) * dv, abs=1e-12
    )


def test_pipeline_emits_blend_term_contributions():
    input_data = apply_research_defaults(
        {
            "notes": ["C4", "E4", "G4"],
            "dynamics": ["mf", "mf", "mf"],
            "instruments": ["flauta", "flauta", "flauta"],
            "num_instruments": [1, 1, 1],
        }
    )
    resultados, _, _ = calculate_metrics(input_data)
    terms = resultados["composite_meta"]["blend_term_contributions"]
    assert "interval_blend_normalisation" not in terms
    assert terms["instrument_term"] == pytest.approx(
        float(resultados["density"]["weighted_orchestral"]), abs=1e-12
    )
    assert terms["interval_term"] == pytest.approx(
        float(resultados["density"]["weighted_pitch"]), abs=1e-12
    )


def test_blend_term_contributions_helper_matches_blend():
    di, dv, w = 40.0, 2.0, 0.5
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
