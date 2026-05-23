"""Tests that removed perceptual/psychoacoustic and combination-tone options are rejected."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from core.defaults import apply_research_defaults
from core.input_validation import validate_no_removed_options, validate_no_removed_perceptual_options
from data_processor import calcular_densidade_ponderada_normalizada, calculate_metrics
from densidade_intervalar import calculate_interval_density, calculate_interval_density_normalized
from error_handler import InputError


MINIMAL = {
    "notes": ["C4", "E4", "G4"],
    "dynamics": ["mf", "mf", "mf"],
    "instruments": ["flauta", "flauta", "flauta"],
    "num_instruments": [1, 1, 1],
}

REMOVED_PERCEPTUAL_KEYS = [
    "use_stevens",
    "alpha",
    "beta",
    "use_psychoacoustic",
    "use_perceptual_weighting",
]

REMOVED_COMBO_KEYS = [
    "calculate_combination_tones",
    "combination_tones",
    "resultant_tones",
    "include_resultants",
    "include_combination_tones",
    "virtual_tones",
    "generated_tones",
]


@pytest.mark.parametrize("key", REMOVED_PERCEPTUAL_KEYS)
def test_removed_perceptual_keys_rejected(key):
    data = apply_research_defaults({**MINIMAL, key: True})
    with pytest.raises(InputError) as exc:
        calculate_metrics(data)
    assert "Removed option" in str(exc.value)


@pytest.mark.parametrize("key", REMOVED_COMBO_KEYS)
def test_removed_combination_keys_rejected(key):
    data = apply_research_defaults({**MINIMAL, key: True})
    with pytest.raises(InputError) as exc:
        calculate_metrics(data)
    assert "Removed option" in str(exc.value)
    assert "virtual" in str(exc.value).lower() or "resultant" in str(exc.value).lower()


def test_calculate_combination_tones_error_message():
    with pytest.raises(InputError) as exc:
        validate_no_removed_options({"calculate_combination_tones": True})
    assert "calculate_combination_tones" in str(exc.value)
    assert "strictly symbolic" in str(exc.value).lower()


def test_no_combination_tones_module():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("combination_tones")


def test_weighted_density_linear_blend_only():
    out = calcular_densidade_ponderada_normalizada(50.0, 5.0, w=0.5)
    assert out == pytest.approx(5.0)


def test_interval_density_pitch_only_invariant_under_dynamics():
    base = apply_research_defaults({**MINIMAL})
    loud = apply_research_defaults(
        {
            **MINIMAL,
            "dynamics": ["ff", "ff", "ff"],
        }
    )
    r1, _, _ = calculate_metrics(base)
    r2, _, _ = calculate_metrics(loud)
    assert r1["density"]["interval"] == pytest.approx(r2["density"]["interval"])


def test_interval_density_pitch_only_invariant_under_instrumentation():
    base = apply_research_defaults({**MINIMAL})
    varied = apply_research_defaults(
        {
            **MINIMAL,
            "instruments": ["flauta", "clarinete", "oboe"],
            "num_instruments": [1, 3, 2],
        }
    )
    r1, _, _ = calculate_metrics(base)
    r2, _, _ = calculate_metrics(varied)
    assert r1["density"]["interval"] == pytest.approx(r2["density"]["interval"])


def test_no_psychoacoustic_corrections_module():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("psychoacoustic_corrections")


def test_interval_compactness_uses_symbolic_path():
    notes = ["C4", "E4", "G4"]
    raw = calculate_interval_density(notes)
    norm = calculate_interval_density_normalized(notes)
    assert raw > 0
    assert norm >= 0


def test_gui_components_no_removed_controls():
    root = Path(__file__).resolve().parents[1]
    gui_sources = [
        root / "gui_components.py",
        root / "gui" / "app.py",
        root / "gui" / "calibration_window.py",
        * (root / "gui" / "widgets").glob("*.py"),
    ]
    source = "\n".join(p.read_text(encoding="utf-8") for p in gui_sources if p.is_file()).lower()
    for term in (
        "use_stevens",
        "use_psychoacoustic",
        "use_perceptual_weighting",
        "stevens",
        "psychoacoustic",
        "perceptual weighting",
        "critical_band",
        "roughness",
        "calculate_combination_tones",
        "combination tone",
        "resultant tone",
        "tartini",
        "virtual tone",
        "generated tone",
        "nonlinear distortion",
    ):
        assert term not in source

    with pytest.raises(InputError, match="use_stevens"):
        validate_no_removed_perceptual_options({"use_stevens": True})
    with pytest.raises(InputError, match="use_psychoacoustic"):
        validate_no_removed_perceptual_options({"use_psychoacoustic": True})
    with pytest.raises(InputError, match="use_perceptual_weighting"):
        validate_no_removed_perceptual_options({"use_perceptual_weighting": True})
