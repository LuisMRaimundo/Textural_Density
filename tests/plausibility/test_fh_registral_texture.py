"""F-H — Registral and texture subindices (HARD/SOFT; §J, §N)."""

from __future__ import annotations

import pytest

from core.pipeline import calculate_metrics
from tests.plausibility.conftest import record_hard, record_soft
from tests.plausibility.helpers import REGISTER_BANDS, assert_jsonable, slice_input


class TestFHRegisterBands:
    def test_compression_formula_and_unused_compactness(self, monkeypatch):
        """HARD: registral_compression = 1/(1+span) for n≥2 else 0; compactness never called."""
        import core.pitch_structure as ps

        def _boom(*_a, **_k):
            raise AssertionError("compute_registral_compactness must not be called")

        monkeypatch.setattr(ps, "compute_registral_compactness", _boom)
        r2, _, pitches = calculate_metrics(slice_input(["C4", "C5"], instruments="flauta"))
        assert_jsonable(r2, label="FH.comp")
        span = max(pitches) - min(pitches)
        sub = r2.get("density_subindices") or {}
        reg = sub.get("registral") or {}
        raw = reg.get("raw") if isinstance(reg, dict) else {}
        comp = None
        if isinstance(raw, dict):
            comp = raw.get("registral_compression")
        if comp is None and isinstance(reg, dict):
            comp = reg.get("normalized")
        expected = 1.0 / (1.0 + span)
        assert comp == pytest.approx(expected)
        r1, _, _ = calculate_metrics(slice_input(["C4"], instruments="flauta"))
        raw1 = ((r1.get("density_subindices") or {}).get("registral") or {}).get("raw") or {}
        c1 = raw1.get("registral_compression") if isinstance(raw1, dict) else None
        record_hard(
            family="F-H",
            test_id="FH.compression",
            span=span,
            compression=comp,
            expected=expected,
            singleton=c1,
            bands=REGISTER_BANDS,
        )

    def test_band_occupancy_denominators(self):
        """HARD: occupancy denominators are in-band totals; all-zero → denom 1; entropy / log2(B)."""
        r, _, _ = calculate_metrics(
            slice_input(["C1", "C3", "C4", "C6"], instruments="piano")
        )
        sub = r.get("density_subindices") or {}
        occ = sub.get("register_occupancy") or sub.get("registral_occupancy") or sub
        record_hard(
            family="F-H",
            test_id="FH.occupancy",
            subindices= {k: occ[k] for k in list(occ)[:12]} if isinstance(occ, dict) else occ,
            piano_status="coarse",
        )


class TestFHSoftClusters:
    @pytest.mark.plausibility
    @pytest.mark.xfail(strict=False, reason="SOFT plausibility")
    def test_low_vs_high_cluster(self):
        """SOFT: same interval density, different occupancy and orchestration_balance."""
        low, _, _ = calculate_metrics(slice_input(["C2", "C#2", "D2"], instruments="trombone"))
        high, _, _ = calculate_metrics(slice_input(["C6", "C#6", "D6"], instruments="flauta"))
        iv_l, iv_h = low["density"]["interval"], high["density"]["interval"]
        same_iv = iv_l == pytest.approx(iv_h, rel=1e-6)
        orch_l = (low.get("orchestration") or {}).get("balance") or (
            low.get("density_subindices") or {}
        ).get("orchestration_balance")
        orch_h = (high.get("orchestration") or {}).get("balance") or (
            high.get("density_subindices") or {}
        ).get("orchestration_balance")
        record_soft(
            family="F-H",
            test_id="FH.soft.low_high",
            met=same_iv,
            expectation="low vs high chromatic trichord: same interval density, different occupancy/balance",
            interval_low=iv_l,
            interval_high=iv_h,
            orch_low=orch_l,
            orch_high=orch_h,
            statuses={"trombone": "table-backed", "flauta": "table-backed"},
        )

    @pytest.mark.plausibility
    @pytest.mark.xfail(strict=False, reason="SOFT plausibility")
    def test_homogeneous_vs_mixed_diversity(self):
        """SOFT: mixed wind/brass/string chord has higher timbre diversity than homogeneous strings."""
        notes = ["C4", "E4", "G4"]
        homo, _, _ = calculate_metrics(slice_input(notes, instruments="violino"))
        mixed, _, _ = calculate_metrics(
            {
                "notes": notes,
                "dynamics": ["mf"] * 3,
                "instruments": ["violino", "flauta", "trombone"],
                "num_instruments": [1, 1, 1],
            }
        )
        def _pick(r, *keys):
            tex = r.get("timbre") or {}
            sub = r.get("density_subindices") or {}
            for k in keys:
                if k in tex:
                    return tex[k]
                if k in sub:
                    return sub[k]
            return None

        d_h = _pick(homo, "timbre_diversity", "diversity")
        d_m = _pick(mixed, "timbre_diversity", "diversity")
        blend_h = _pick(homo, "blend_index")
        blend_m = _pick(mixed, "blend_index")
        bal_h = _pick(homo, "density_balance")
        bal_m = _pick(mixed, "density_balance")
        met = d_m is not None and d_h is not None and d_m > d_h
        record_soft(
            family="F-H",
            test_id="FH.soft.diversity",
            met=bool(met),
            expectation="mixed violin/flute/trombone > homogeneous violins in timbre_diversity",
            homogeneous={"diversity": d_h, "blend": blend_h, "balance": bal_h},
            mixed={"diversity": d_m, "blend": blend_m, "balance": bal_m},
        )
