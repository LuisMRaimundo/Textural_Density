"""Tests for core registral_density, interval_compactness, orchestration_mass, composite."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from core.composite import compute_weighted_density_normalized
from core.converters import legacy_input_to_vertical_slice
from core.interval_compactness import compute_interval_compactness
from core.orchestration_mass import compute_orchestration_mass
from core.registral_density import compute_registral_density
from data_processor import (
    calcular_densidade_ponderada_normalizada,
    calcular_massa_sonora,
    calculate_metrics,
)
from densidade_intervalar import calculate_interval_density


def test_interval_compactness_matches_pipeline_score_only():
    notes = ["C4", "E4", "G4"]
    from densidade_intervalar import calculate_interval_density_normalized

    wrapper = compute_interval_compactness(notes)
    direct = calculate_interval_density(notes)
    normalized = calculate_interval_density_normalized(notes)
    assert wrapper["raw"] == pytest.approx(float(direct))
    assert wrapper["value"] == pytest.approx(float(normalized))


def test_registral_matches_subindices_entropy():
    data = {
        "notes": ["C4", "E4", "G4", "C5"],
        "dynamics": ["mf"] * 4,
        "instruments": ["flauta"] * 4,
        "num_instruments": [1] * 4,
    }
    resultados, _, _ = calculate_metrics(data)
    sub = resultados["density_subindices"]["registral"]["raw"]
    vs = legacy_input_to_vertical_slice(data)
    reg = compute_registral_density(vs, pitch_span_semitones=float(sub["pitch_span_semitones"]))
    assert reg["register_entropy"] == pytest.approx(float(sub["register_entropy"]))


def test_registral_module_no_tkinter():
    for module in ("registral_density", "interval_compactness", "orchestration_mass", "composite"):
        tree = ast.parse(
            Path(__file__).resolve().parents[1]
            .joinpath(f"core/{module}.py")
            .read_text(encoding="utf-8-sig")
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] != "tkinter"


def test_orchestration_mass_matches_data_processor():
    notas = ["C4", "E4", "G4"]
    din = ["mf", "f", "ff"]
    nums = [1, 2, 1]
    dens = [1.0, 1.5, 1.2]
    assert compute_orchestration_mass(notas, din, nums, dens) == pytest.approx(
        calcular_massa_sonora(notas, din, nums, dens)
    )


def test_composite_weighted_matches_data_processor():
    di, dv = 75.0, 6.5
    assert compute_weighted_density_normalized(di, dv, w=0.5) == pytest.approx(
        calcular_densidade_ponderada_normalizada(di, dv, w=0.5)
    )
