"""
Additional contract tests for densidade_intervalar.py.

Protects mathematical and musicological invariants of symbolic interval density
without duplicating tests in test_densidade_intervalar.py, test_formal_construct_axioms.py,
or test_core_extraction.py.
"""

from __future__ import annotations

import ast
import math
from itertools import permutations
from pathlib import Path

import pytest

import densidade_intervalar as di
from core.interval_compactness import compute_interval_compactness
from data_processor import calculate_metrics

ROOT = Path(__file__).resolve().parents[1]
LAMB = 0.05
KW = {"lamb": LAMB, "use_optimization": False}


def _density(notes: list[str], **overrides) -> float:
    return di.calculate_interval_density(notes, **{**KW, **overrides})


def _dyad(a: str, b: str, **overrides) -> float:
    return _density([a, b], **overrides)


class TestUnisonAndIdentity:
    def test_empty_list_returns_zero(self):
        assert _density([]) == 0.0

    def test_blank_entries_filtered_to_zero(self):
        assert _density([""]) == 0.0
        assert _density(["", ""]) == 0.0

    def test_single_note_returns_zero(self):
        assert _density(["C4"]) == 0.0

    def test_unison_dyad_is_maximal_pair_contribution(self):
        assert _dyad("C4", "C4") == pytest.approx(1.0)

    def test_unison_stack_pair_count_scales_combinatorially(self):
        """Three duplicated unisons -> three pairs, each weight 1.0."""
        assert _density(["C4", "C4", "C4"]) == pytest.approx(3.0)

    def test_normalized_single_note_is_zero(self):
        assert di.calculate_interval_density_normalized(["C4"], lamb=LAMB) == 0.0


class TestSymmetry:
    def test_dyad_order_invariant(self):
        forward = _dyad("C4", "G4")
        backward = _dyad("G4", "C4")
        assert forward == pytest.approx(backward)

    def test_triad_permutation_invariant(self):
        notes = ["C4", "E4", "G4"]
        base = _density(notes)
        for perm in permutations(notes):
            assert _density(list(perm)) == pytest.approx(base)

    def test_get_intervals_count_is_pairwise_only(self):
        notes = ["C4", "E4", "G4", "B4"]
        n = len(notes)
        assert len(di.get_intervals(notes)) == n * (n - 1) // 2


class TestMonotonicityWithDistance:
    def test_semitone_cluster_gt_perfect_fifth_dyad(self):
        assert _dyad("C4", "C#4") > _dyad("C4", "G4")

    def test_perfect_fifth_gt_octave_dyad(self):
        assert _dyad("C4", "G4") > _dyad("C4", "C5")

    def test_chromatic_cluster_gt_wide_spread_tetrachord(self):
        cluster = _density(["C4", "C#4", "D4", "D#4"])
        spread = _density(["C3", "E4", "G4", "C6"])
        assert cluster > spread

    def test_higher_lambda_weakens_same_interval(self):
        low = _dyad("C4", "E4", lamb=0.01)
        high = _dyad("C4", "E4", lamb=0.5)
        assert low > high


SEMITONE_DYADS = [
    ("C4", "C#4"),
    ("C4", "D4"),
    ("C4", "Eb4"),
    ("C4", "E4"),
    ("C4", "G4"),
    ("C4", "C5"),
]


class TestMonotonicDyadChain:
    @pytest.mark.parametrize("left,right", zip(SEMITONE_DYADS, SEMITONE_DYADS[1:]))
    def test_wider_dyad_not_greater_than_narrower(self, left, right):
        narrow = _dyad(*left)
        wide = _dyad(*right)
        assert narrow >= wide


class TestMicrotonalAndCents:
    def test_cent_offset_produces_finite_density(self):
        value = _dyad("C4", "C4+50c")
        assert math.isfinite(value)
        assert value > 0.0

    def test_small_cent_offset_closer_than_large(self):
        small = _dyad("C4", "C4+10c")
        large = _dyad("C4", "C4+90c")
        assert small > large

    def test_microtonal_distinct_from_exact_unison(self):
        assert _dyad("C4", "C4+25c") < _dyad("C4", "C4")


class TestLambdaAndCalibration:
    def test_missing_config_returns_default_lambda(self, monkeypatch, tmp_path):
        monkeypatch.setattr(di, "CONFIG_PATH", str(tmp_path / "missing.json"))
        assert di.load_calibrated_parameters() == pytest.approx(di.DEFAULT_LAMBDA)

    def test_modified_exponential_decay_respects_lambda_direction(self):
        delta = 12.0
        assert di.modified_exponential_decay(delta, lamb=0.01) > di.modified_exponential_decay(
            delta, lamb=0.2
        )

    def test_calibrate_lambda_writes_only_temp_config(self, monkeypatch, tmp_path):
        cfg = tmp_path / "density_params.json"
        monkeypatch.setattr(di, "CONFIG_PATH", str(cfg))
        lamb = di.calibrate_lambda({0: 1.0, 5: 1.0})
        assert cfg.is_file()
        assert di.load_calibrated_parameters() == pytest.approx(lamb)
        assert 0.01 <= lamb <= 1.0


class TestInvalidAndDegenerateInputs:
    def test_invalid_note_does_not_crash_current_contract(self):
        """Current microtonal parser falls back; module returns finite density."""
        value = _density(["NOT_A_REAL_NOTE_XYZ", "C4"])
        assert math.isfinite(value)

    def test_invalid_dyad_raises_in_interval_labels(self):
        with pytest.raises(ValueError):
            di.get_intervals(["BADNOTE!!!", "E4"])

    def test_repeated_identical_pitch_increases_pair_sum(self):
        one_pair = _density(["C4", "E4"])
        with_dup = _density(["C4", "C4", "E4"])
        assert with_dup > one_pair


class TestRemovedFeatureBoundary:
    FORBIDDEN_TERMS = (
        "combination_tone",
        "resultant_tone",
        "virtual_tone",
        "generated_tone",
        "use_stevens",
        "use_psychoacoustic",
        "psychoacoustic_corrections",
        "Spectral_Analyser",
        "fft",
        "stft",
        "ewsd",
    )

    def test_module_source_has_no_forbidden_runtime_imports(self):
        tree = ast.parse((ROOT / "densidade_intervalar.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name.lower()
                    assert not any(term in name for term in self.FORBIDDEN_TERMS)
            elif isinstance(node, ast.ImportFrom):
                mod = (node.module or "").lower()
                assert not any(term in mod for term in self.FORBIDDEN_TERMS)

    def test_public_api_excludes_combination_tone_helpers(self):
        assert "combination" not in " ".join(di.__all__).lower()
        assert "resultant" not in " ".join(di.__all__).lower()

    def test_interval_list_derives_only_from_input_pitches(self):
        notes = ["C4", "E4", "G4"]
        assert len(di.get_intervals(notes)) == 3
        for label in di.get_intervals(notes):
            assert "interval" in label


class TestIntegrationConsistency:
    def _minimal_input(self, notes: list[str], nums: list[int] | None = None) -> dict:
        n = len(notes)
        return {
            "notes": notes,
            "dynamics": ["mf"] * n,
            "instruments": ["flauta"] * n,
            "num_instruments": nums or [1] * n,
        }

    def test_normalized_formula_matches_implementation(self):
        import numpy as np

        from config import USE_LOG_COMPRESSION

        notes = ["C4", "E4", "G4"]
        raw = _density(notes)
        n = len(notes)
        expected = float(2.0 * raw / (n * (n - 1)))
        if USE_LOG_COMPRESSION:
            expected = float(np.log10(1.0 + expected))
        assert di.calculate_interval_density_normalized(notes, lamb=LAMB) == pytest.approx(
            expected
        )

    def test_core_wrapper_raw_matches_direct_module(self):
        notes = ["D4", "F4", "A4"]
        wrapper = compute_interval_compactness(notes)
        assert wrapper["raw"] == pytest.approx(_density(notes))
        assert wrapper["source_type"] == "score_derived"

    def test_pipeline_interval_unchanged_by_player_count(self):
        notes = ["C4", "E4", "G4"]
        low, _, _ = calculate_metrics(self._minimal_input(notes, nums=[1, 1, 1]))
        high, _, _ = calculate_metrics(self._minimal_input(notes, nums=[1, 4, 2]))
        assert float(low["density"]["interval"]) == pytest.approx(float(high["density"]["interval"]))

    def test_pipeline_interval_unchanged_by_dynamics(self):
        notes = ["C4", "E4", "G4"]
        soft = {
            "notes": notes,
            "dynamics": ["pp", "pp", "pp"],
            "instruments": ["flauta"] * 3,
            "num_instruments": [1, 1, 1],
        }
        loud = {
            "notes": notes,
            "dynamics": ["ff", "ff", "ff"],
            "instruments": ["flauta"] * 3,
            "num_instruments": [1, 1, 1],
        }
        r_soft, _, _ = calculate_metrics(soft)
        r_loud, _, _ = calculate_metrics(loud)
        assert float(r_soft["density"]["interval"]) == pytest.approx(float(r_loud["density"]["interval"]))
