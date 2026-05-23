"""
Phase 0 regression baseline tests.

These tests snapshot documented current behaviour before refactors.
They must pass without importing GUI modules.

Scientific note: all metrics here are score-/symbolic-derived or metadata
proxies as implemented today — not acoustic measurements.
"""

from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path

import numpy as np
import pytest

from data_processor import (
    calcular_densidade_ponderada_normalizada,
    calculate_metrics,
)
from densidade_intervalar import (
    calculate_interval_density,
    modified_exponential_decay,
)
from microtonal import midi_to_hz, note_to_midi
from spectral_analysis import (
    calculate_chroma_vector,
    calculate_harmonic_ratio,
    calculate_spectral_moments,
)
from utils.notes import note_to_midi as note_to_midi_utils

FIXTURES_DIR = Path(__file__).parent / "fixtures"
BASELINE_PATH = FIXTURES_DIR / "regression_baseline.json"


def _load_baseline() -> dict:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def baseline_input_data():
    """Canonical vertical slice input used for golden regression."""
    return {
        "notes": ["C4", "E4", "G4", "C5"],
        "dynamics": ["mf", "f", "ff", "mf"],
        "instruments": ["flauta", "clarinete", "flauta", "clarinete"],
        "num_instruments": [1, 2, 1, 1],
        "weight_factor": 0.5,
        "save_results": False,
        "show_graphs": False,
    }


@pytest.fixture
def baseline():
    return _load_baseline()


# ---------------------------------------------------------------------------
# Public API inventory / signatures
# ---------------------------------------------------------------------------


class TestPublicAPIInventory:
    """Document and guard primary public entry points."""

    def test_calculate_metrics_signature(self):
        sig = inspect.signature(calculate_metrics)
        assert "input_data" in sig.parameters
        assert sig.return_annotation != inspect.Signature.empty

    def test_calcular_metricas_alias_exists(self):
        import data_processor

        assert hasattr(data_processor, "calculate_metrics")
        assert hasattr(data_processor, "calcular_metricas")
        assert data_processor.calcular_metricas is data_processor.calculate_metrics


# ---------------------------------------------------------------------------
# Golden regression (fixture-backed)
# ---------------------------------------------------------------------------


class TestGoldenRegression:
    def test_fixture_file_exists(self):
        assert BASELINE_PATH.is_file()

    def test_calculate_metrics_density_values(self, baseline_input_data, baseline):
        resultados, densidades, pitches = calculate_metrics(baseline_input_data)
        expected = baseline["density"]
        d = resultados["density"]
        for key, val in expected.items():
            assert float(d[key]) == pytest.approx(float(val), rel=1e-5, abs=1e-6), key

    def test_calculate_metrics_additional_metrics(self, baseline_input_data, baseline):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        add = resultados["additional_metrics"]
        assert float(add["harmonic_ratio"]) == pytest.approx(
            baseline["harmonic_ratio"], rel=1e-6
        )
        assert float(add["complexity"]) == pytest.approx(baseline["complexity"], rel=1e-6)

    def test_calculate_metrics_primary_pitches_count(self, baseline_input_data, baseline):
        _, _, pitches = calculate_metrics(baseline_input_data)
        assert len(pitches) == baseline["pitches_primary_count"]

    def test_calculate_metrics_instrument_densities(self, baseline_input_data, baseline):
        _, densidades, _ = calculate_metrics(baseline_input_data)
        assert len(densidades) == len(baseline["instrument_densities"])
        for got, exp in zip(densidades, baseline["instrument_densities"]):
            assert float(got) == pytest.approx(float(exp), rel=1e-5, abs=1e-6)

    def test_result_top_level_keys(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        for key in (
            "density",
            "spectral_moments",
            "additional_metrics",
            "texture",
            "timbre",
            "orchestration",
            "input_data",
        ):
            assert key in resultados

    def test_density_subkeys(self, baseline_input_data):
        resultados, _, _ = calculate_metrics(baseline_input_data)
        for key in (
            "interval",
            "instrument",
            "weighted",
            "refined",
            "total",
            "sonic_mass",
            "absolute",
        ):
            assert key in resultados["density"]


# ---------------------------------------------------------------------------
# Pitch / frequency conversion
# ---------------------------------------------------------------------------


class TestPitchConversionRegression:
    def test_note_to_midi_c4_microtonal_and_utils(self, baseline):
        assert float(note_to_midi("C4")) == pytest.approx(baseline["note_to_midi_C4"])
        assert float(note_to_midi_utils("C4")) == pytest.approx(baseline["note_to_midi_C4"])

    def test_midi_to_hz_a4(self, baseline):
        assert float(midi_to_hz(69)) == pytest.approx(baseline["midi_to_hz_A4"])

    def test_microtonal_cents_offset(self):
        assert note_to_midi("A4+50c") == pytest.approx(69.5, abs=1e-6)
        assert note_to_midi("A4-50c") == pytest.approx(68.5, abs=1e-6)


# ---------------------------------------------------------------------------
# Interval density behaviour
# ---------------------------------------------------------------------------


class TestIntervalDensityRegression:
    def test_dyad_c4_g4_baseline(self, baseline):
        d = calculate_interval_density(["C4", "G4"], lamb=0.05, use_optimization=False)
        assert float(d) == pytest.approx(baseline["interval_density_C4_G4"], rel=1e-9)

    def test_unison_pair_contribution_via_decay(self):
        assert modified_exponential_decay(0, lamb=0.05) == 1.0

    @pytest.mark.parametrize(
        "notes,label",
        [
            (["C4", "C4"], "unison"),
            (["C4", "Db4"], "minor_second"),
            (["C4", "D4"], "major_second"),
            (["C4", "Eb4"], "minor_third"),
            (["C4", "E4"], "major_third"),
            (["C4", "F4"], "perfect_fourth"),
            (["C4", "F#4"], "tritone"),
            (["C4", "G4"], "perfect_fifth"),
            (["C4", "C5"], "octave"),
        ],
    )
    def test_chromatic_dyad_positive_finite(self, notes, label):
        d = calculate_interval_density(notes, lamb=0.05, use_optimization=False)
        assert np.isfinite(d), label
        assert d >= 0.0, label

    def test_monotonic_decay_with_semitone_distance(self):
        """Exponential decay model: larger semitone distance -> lower pair weight."""
        lamb = 0.05
        note_pairs = [
            ["C4", "Db4"],   # 1 semitone
            ["C4", "D4"],    # 2
            ["C4", "Eb4"],   # 3
            ["C4", "E4"],    # 4
            ["C4", "F4"],    # 5
            ["C4", "F#4"],   # 6
            ["C4", "G4"],    # 7
            ["C4", "C5"],    # 12
        ]
        values = [
            calculate_interval_density(pair, lamb=lamb, use_optimization=False)
            for pair in note_pairs
        ]
        for i in range(len(values) - 1):
            assert values[i] > values[i + 1]

    def test_chromatic_cluster_greater_than_wide_spaced(self):
        cluster = calculate_interval_density(
            ["C4", "C#4", "D4", "D#4", "E4"],
            lamb=0.05,
            use_optimization=False,
        )
        wide = calculate_interval_density(
            ["C3", "G3", "D4", "A4", "E5"],
            lamb=0.05,
            use_optimization=False,
        )
        assert cluster > wide


# ---------------------------------------------------------------------------
# Weighted density
# ---------------------------------------------------------------------------


class TestWeightedDensityRegression:
    def test_minmax_linear_blend_baseline(self, baseline):
        out = calcular_densidade_ponderada_normalizada(50.0, 5.0, w=0.5)
        assert float(out) == pytest.approx(baseline["weighted_density_DI50_DV5"], rel=1e-9)


# ---------------------------------------------------------------------------
# Spectral metadata (symbolic weights)
# ---------------------------------------------------------------------------


class TestSpectralMetadataRegression:
    def test_spectral_moments_structure(self):
        moments = calculate_spectral_moments([60, 64, 67, 72], [1, 1, 1, 1])
        assert "centroid" in moments
        assert "frequency" in moments["centroid"]
        assert moments["centroid"]["frequency"] > 0

    def test_chroma_vector_sums_to_one(self, baseline):
        chroma = calculate_chroma_vector([60, 64, 67, 72], [1, 1, 1, 1])
        assert float(np.sum(chroma)) == pytest.approx(baseline["chroma_sum"], abs=1e-9)

    def test_harmonic_ratio_finite(self):
        hr = calculate_harmonic_ratio([60, 64, 67, 72], [1, 1, 1, 1])
        assert np.isfinite(hr)
        assert 0.0 <= hr <= 1.0


# ---------------------------------------------------------------------------
# Core must not depend on Tkinter (Phase 0 inventory guard)
# ---------------------------------------------------------------------------


CORE_MODULES_NO_GUI = [
    "densidade_intervalar",
    "spectral_analysis",
    "microtonal",
    "data_processor",
    "timbre_texture_analysis",
    "utils.notes",
    "utils.optimization",
    "utils.serialize_utils",
    "score_io.exporters",
    "data_processor",
    "core.pipeline",
]


def _module_imports_tkinter(module_name: str) -> bool:
    import ast
    import importlib
    from pathlib import Path

    mod = importlib.import_module(module_name)
    path = Path(mod.__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] == "tkinter" for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] == "tkinter":
                return True
    return False


class TestCoreGUICouplingInventory:
    @pytest.mark.parametrize("module_name", CORE_MODULES_NO_GUI)
    def test_core_module_does_not_import_tkinter(self, module_name):
        assert not _module_imports_tkinter(module_name)


class TestDataProcessorGUICouplingDocumented:
    """Phase 1: data_processor must not import Tkinter at load time."""

    def test_data_processor_does_not_import_tkinter(self):
        assert not _module_imports_tkinter("data_processor")
