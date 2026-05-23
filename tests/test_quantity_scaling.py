"""
Regression tests for quantity (Qty) scaling — incoherent source addition model.

Cases A–F from quantity-scaling specification.
"""

from __future__ import annotations

import math

import pytest

from core.orchestration_mass import compute_orchestration_mass
from core.pipeline import calculate_metrics
from core.quantity_scaling import (
    quantity_pressure_gain,
    quantity_power_gain,
    rss_pressure_equivalent,
    validate_quantity,
)


def _slice_input(notes: list[str], **kwargs):
    n = len(notes)
    return {
        "notes": notes,
        "dynamics": kwargs.get("dynamics", ["mf"] * n),
        "instruments": kwargs.get("instruments", ["Flauta"] * n),
        "num_instruments": kwargs.get("num_instruments", [1] * n),
        "weight_factor": kwargs.get("weight_factor", 0.5),
    }


class TestQuantityScalingHelpers:
    def test_validate_quantity_rejects_invalid(self):
        assert validate_quantity(1) == 1.0
        assert validate_quantity(10) == 10.0
        with pytest.raises(ValueError):
            validate_quantity(0)
        with pytest.raises(ValueError):
            validate_quantity(-1)

    def test_power_and_pressure_gains(self):
        assert quantity_power_gain(4) == 4.0
        assert quantity_pressure_gain(4) == pytest.approx(2.0)
        assert rss_pressure_equivalent([(10.0, 4)]) == pytest.approx(20.0)


class TestCaseAOnePlayerBaseline:
    """One C4 flute, mf, Qty = 1."""

    @pytest.fixture
    def result(self):
        resultados, _, _ = calculate_metrics(_slice_input(["C4"]))
        return resultados

    def test_counts(self, result):
        agg = result["pitch_aggregation"]
        assert agg["event_count"] == 1
        assert agg["player_count"] == 1
        assert agg["distinct_pitch_count"] == 1
        assert agg["pitch_polyphony"] == 1
        assert agg["player_doubling_count"] == 0
        assert result["density"]["interval"] == pytest.approx(0.0)
        assert result["density"]["pitch_structure"] == pytest.approx(0.0)


class TestCaseBQtyFour:
    """One C4 flute, mf, Qty = 4 — relative to Qty = 1."""

    def test_scaling_ratios(self):
        base, _, _ = calculate_metrics(_slice_input(["C4"], num_instruments=[1]))
        four, _, _ = calculate_metrics(_slice_input(["C4"], num_instruments=[4]))

        b_inst = float(base["density"]["instrument"])
        b_mass = float(base["density"]["sonic_mass"])
        f_inst = float(four["density"]["instrument"])
        f_mass = float(four["density"]["sonic_mass"])

        assert four["pitch_aggregation"]["player_count"] == 4
        assert four["pitch_aggregation"]["pitch_polyphony"] == 1
        assert four["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert four["spectral_moments"]["spectral_entropy"] == pytest.approx(0.0)
        assert four["pitch_aggregation"]["interval_pairs_count_distinct"] == 0
        assert four["density"]["pitch_structure"] == pytest.approx(0.0)

        if b_inst > 0 and b_mass > 0:
            assert f_inst / b_inst == pytest.approx(2.0, rel=0.02)
            assert f_mass / b_mass == pytest.approx(4.0, rel=0.02)
            assert f_mass / b_mass != pytest.approx(8.0, rel=0.05)


class TestCaseCTenPlayers:
    """One C4 flute, mf, Qty = 10."""

    def test_no_qty_three_halves(self):
        one, _, _ = calculate_metrics(_slice_input(["C4"], num_instruments=[1]))
        ten, _, _ = calculate_metrics(_slice_input(["C4"], num_instruments=[10]))

        b_inst = float(one["density"]["instrument"])
        b_mass = float(one["density"]["sonic_mass"])
        t_inst = float(ten["density"]["instrument"])
        t_mass = float(ten["density"]["sonic_mass"])

        assert ten["pitch_aggregation"]["player_count"] == 10
        assert ten["pitch_aggregation"]["player_doubling_count"] == 9
        assert ten["pitch_aggregation"]["pitch_polyphony"] == 1

        if b_inst > 0 and b_mass > 0:
            assert t_inst / b_inst == pytest.approx(math.sqrt(10), rel=0.02)
            assert t_mass / b_mass == pytest.approx(10.0, rel=0.02)
            ratio_32 = (t_mass / b_mass) / (t_inst / b_inst)
            assert ratio_32 == pytest.approx(math.sqrt(10), rel=0.05)
            assert t_mass / b_mass != pytest.approx(math.pow(10, 1.5), rel=0.05)


class TestCaseDRowSplittingInvariance:
    """Four C4 rows Qty=1 vs one row Qty=4."""

    def test_mass_and_pressure_equivalent_match(self):
        one_row, _, _ = calculate_metrics(_slice_input(["C4"], num_instruments=[4]))
        four_rows, _, _ = calculate_metrics(
            _slice_input(["C4", "C4", "C4", "C4"], num_instruments=[1, 1, 1, 1])
        )

        assert four_rows["pitch_aggregation"]["player_count"] == 4
        assert four_rows["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert four_rows["pitch_aggregation"]["pitch_polyphony"] == 1
        assert four_rows["spectral_moments"]["spectral_entropy"] == pytest.approx(0.0)

        assert one_row["density"]["sonic_mass"] == pytest.approx(
            four_rows["density"]["sonic_mass"], rel=1e-6
        )
        assert one_row["density"]["instrument"] == pytest.approx(
            four_rows["density"]["instrument"], rel=1e-6
        )
        assert one_row["density"]["pitch_structure"] == pytest.approx(0.0)
        assert four_rows["density"]["pitch_structure"] == pytest.approx(0.0)


class TestCaseEFourDistinctPitches:
    """C4, C#4, D4, E4 — each flute, mf, Qty = 1."""

    def test_pitch_structure(self):
        resultados, _, _ = calculate_metrics(
            _slice_input(["C4", "C#4", "D4", "E4"])
        )
        agg = resultados["pitch_aggregation"]
        assert agg["player_count"] == 4
        assert agg["distinct_pitch_count"] == 4
        assert agg["pitch_polyphony"] == 4
        assert agg["interval_pairs_count_distinct"] == 6
        assert resultados["spectral_moments"]["spectral_entropy"] > 0
        assert resultados["density"]["pitch_structure"] > 0

        unison, _, _ = calculate_metrics(_slice_input(["C4"], num_instruments=[4]))
        assert resultados["density"]["pitch_structure"] > unison["density"]["pitch_structure"]


class TestCaseFDynamicAppliedOnce:
    """Dynamics encoded in instrument module — no second multiplier in mass."""

    def test_mass_uses_module_dynamics_only(self):
        soft, _, _ = calculate_metrics(_slice_input(["C4"], dynamics=["pp"]))
        loud, _, _ = calculate_metrics(_slice_input(["C4"], dynamics=["ff"]))
        assert float(loud["density"]["sonic_mass"]) > float(soft["density"]["sonic_mass"])

    def test_orchestration_mass_no_double_dynamic(self):
        """Legacy API: densities are one-player; mass is linear in qty only."""
        mass = compute_orchestration_mass(
            ["C4"],
            ["mf"],
            [2],
            [5.0],
        )
        assert mass == pytest.approx(10.0)

    def test_same_dynamic_same_pitch_structure(self):
        soft, _, _ = calculate_metrics(
            _slice_input(["C4", "E4", "G4"], dynamics=["p", "p", "p"])
        )
        loud, _, _ = calculate_metrics(
            _slice_input(["C4", "E4", "G4"], dynamics=["ff", "ff", "ff"])
        )
        assert float(soft["density"]["interval"]) == pytest.approx(
            float(loud["density"]["interval"])
        )


class TestQuantityMetadata:
    def test_quantity_scaling_in_results(self):
        resultados, _, _ = calculate_metrics(_slice_input(["C4"], num_instruments=[3]))
        qs = resultados.get("quantity_scaling") or {}
        meta = resultados.get("metric_metadata") or {}
        assert qs.get("quantity_scaling_model") == "incoherent_source_addition"
        assert qs.get("coherent_phase_locked_addition_assumed") is False
        assert qs.get("dynamic_applied_once") is True
        assert meta.get("quantity_scaling_model") == "incoherent_source_addition"
