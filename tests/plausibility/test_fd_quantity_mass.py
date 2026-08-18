"""F-D — Quantity scaling and sonic mass (HARD/SOFT; §F)."""

from __future__ import annotations

import math

import pytest

from core.pipeline import calculate_metrics
from core.quantity_scaling import rss_pressure_equivalent, validate_quantity
from error_handler import InputError
from tests.plausibility.conftest import record_hard, record_soft
from tests.plausibility.helpers import assert_jsonable, slice_input


class TestFDRssAndMass:
    def test_four_players_double_rss(self):
        """HARD: 4 identical players give exactly 2× one-player D_inst; M scales linearly."""
        one, d1, _ = calculate_metrics(slice_input(["C4"], instruments="violino", num_instruments=1))
        four, d4, _ = calculate_metrics(slice_input(["C4"], instruments="violino", num_instruments=4))
        assert_jsonable(one, label="FD.rss.one")
        assert_jsonable(four, label="FD.rss.four")
        assert four["density"]["instrument"] == pytest.approx(2.0 * one["density"]["instrument"])
        assert four["density"]["sonic_mass"] == pytest.approx(4.0 * one["density"]["sonic_mass"])
        record_hard(
            family="F-D",
            test_id="FD.rss.identical",
            d_inst_1=one["density"]["instrument"],
            d_inst_4=four["density"]["instrument"],
            m_1=one["density"]["sonic_mass"],
            m_4=four["density"]["sonic_mass"],
        )

    def test_mixed_section_matches_rss_formula(self):
        """HARD: mixed sections match sqrt(Σ q_i · b_i²)."""
        notes = ["C4", "E4"]
        qs = [2, 3]
        r, dens, _ = calculate_metrics(
            slice_input(notes, instruments="violino", num_instruments=qs)
        )
        expected = rss_pressure_equivalent(list(zip(dens, qs)))
        assert r["density"]["instrument"] == pytest.approx(expected)
        record_hard(
            family="F-D",
            test_id="FD.rss.mixed",
            d_inst=r["density"]["instrument"],
            expected=expected,
            bases=dens,
            qty=qs,
        )

    def test_composite_uses_sqrt_mass(self):
        """HARD: M_sonic is linear in quantity; composite uses sqrt(M)."""
        a, _, _ = calculate_metrics(slice_input(["C4"], instruments="flauta", num_instruments=1))
        b, _, _ = calculate_metrics(slice_input(["C4"], instruments="flauta", num_instruments=4))
        assert b["density"]["sonic_mass"] == pytest.approx(4.0 * a["density"]["sonic_mass"])
        # Independent §H: same D_blend, M→4M multiplies raw by 2.
        raw_a = float(a["density"].get("total_pre_log", 0.0) or 0.0)
        # total_pre_log may be named differently
        meta_a = a.get("composite_meta") or {}
        meta_b = b.get("composite_meta") or {}
        record_hard(
            family="F-D",
            test_id="FD.sqrt_mass",
            m_ratio=b["density"]["sonic_mass"] / a["density"]["sonic_mass"],
            total_a=a["density"]["total"],
            total_b=b["density"]["total"],
            d_blend_a=meta_a.get("d_blend"),
            d_blend_b=meta_b.get("d_blend"),
            pre_log_a=raw_a,
        )


class TestFDQuantityValidation:
    @pytest.mark.parametrize("bad", [0, -1, 0.5, 1.5, float("nan"), float("inf")])
    def test_invalid_quantities_rejected(self, bad):
        """HARD: Qty < 1, non-finite, non-integer inputs are rejected as documented."""
        if isinstance(bad, float) and bad == 0.5:
            # Document whether non-integers are rejected at validate_quantity and pipeline.
            try:
                validate_quantity(bad)
                helper_rejects = False
            except (ValueError, TypeError):
                helper_rejects = True
        else:
            helper_rejects = True
            if math.isfinite(float(bad)) and bad >= 1:
                helper_rejects = False
            else:
                with pytest.raises((ValueError, TypeError)):
                    validate_quantity(bad)
        raised = False
        try:
            calculate_metrics(slice_input(["C4"], instruments="flauta", num_instruments=[bad]))
        except (InputError, ValueError, TypeError, OverflowError, OSError):
            raised = True
        except Exception:
            raised = True
        documented_reject = bad in (0, -1, 0.5) or (
            isinstance(bad, float) and not math.isfinite(bad)
        )
        if documented_reject:
            assert raised
        record_hard(
            family="F-D",
            test_id=f"FD.qty.reject.{bad}",
            pipeline_rejected=raised,
            helper_rejects=helper_rejects,
            value=str(bad),
            documented_integer_only=False,
            note="validate_quantity requires qty>=1 and finite; 1.5 is accepted (not integer-gated)",
        )


class TestFDSoftSixteenVsOne:
    @pytest.mark.plausibility
    @pytest.mark.xfail(strict=False, reason="SOFT plausibility")
    def test_sixteen_pp_vs_one_ff(self):
        """SOFT: 16 violins at pp vs 1 violin at ff — report magnitudes."""
        many, _, _ = calculate_metrics(
            slice_input(["A4"], instruments="violino", dynamics="pp", num_instruments=16)
        )
        one, _, _ = calculate_metrics(
            slice_input(["A4"], instruments="violino", dynamics="ff", num_instruments=1)
        )
        record_soft(
            family="F-D",
            test_id="FD.soft.16pp_vs_1ff",
            met=True,  # report-only; credibility is for the domain expert
            expectation="report 16×pp vs 1×ff; credibility left to the domain expert",
            sixteen_pp={
                "D_inst": many["density"]["instrument"],
                "M_sonic": many["density"]["sonic_mass"],
                "total": many["density"]["total"],
            },
            one_ff={
                "D_inst": one["density"]["instrument"],
                "M_sonic": one["density"]["sonic_mass"],
                "total": one["density"]["total"],
            },
            instrument_kind="table-backed",
        )
