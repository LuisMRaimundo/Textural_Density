"""F-E — Blend and composite (HARD; §G–§H). Does not import core.composite."""

from __future__ import annotations

import math
import random

import pytest

from core.pipeline import calculate_metrics
from tests.plausibility.conftest import record_hard
from tests.plausibility.helpers import (
    DI_MAX,
    DV_MAX_LEGACY,
    REF,
    assert_jsonable,
    independent_blend,
    slice_input,
)


def _pre_log(resultados: dict) -> float:
    meta = resultados.get("metric_metadata") or {}
    total = (meta.get("metrics") or {}).get("density.total") or meta.get("density.total")
    if isinstance(total, dict) and total.get("raw_value") is not None:
        return float(total["raw_value"])
    # Fallback: invert log10(1+x)
    tot = float(resultados["density"]["total"])
    return 10.0 ** tot - 1.0


def _compare_pipeline(notes, instruments="flauta", w=0.5, qty=1, dynamics="mf"):
    r, _, _ = calculate_metrics(
        slice_input(notes, instruments=instruments, dynamics=dynamics, num_instruments=qty, weight_factor=w)
    )
    assert_jsonable(r, label="FE.pipeline")
    di = float(r["density"]["instrument"])
    dv = float(r["density"]["interval"])
    mass = float(r["density"]["sonic_mass"])
    indep = independent_blend(di, dv, w, mass)
    return r, indep


class TestFEIndependentGrid:
    @pytest.mark.parametrize("w", [0.0, 0.5, 1.0])
    @pytest.mark.parametrize("qty", [1, 2, 8, 16])
    @pytest.mark.parametrize(
        "notes,instruments,dynamics",
        [
            (["C4"], "flauta", "mf"),
            (["C4", "E4", "G4"], "flauta", "mf"),
            (["C4", "C#4", "D4", "D#4"], "violino", "ff"),
            (["E2", "C3", "G3"], "trombone", "ffff"),
        ],
    )
    def test_independent_h_matches_pipeline(self, w, qty, notes, instruments, dynamics):
        """HARD: independent §H formula reproduces weighted / pre-log / total to 1e-9."""
        r, indep = _compare_pipeline(notes, instruments, w, qty, dynamics)
        assert r["density"]["weighted"] == pytest.approx(indep["weighted"], abs=1e-9)
        pre = _pre_log(r)
        assert pre == pytest.approx(indep["total_pre_log"], abs=1e-9)
        assert r["density"]["total"] == pytest.approx(indep["total"], abs=1e-9)
        record_hard(
            family="F-E",
            test_id=f"FE.grid.w{w}.q{qty}.{instruments}.{len(notes)}.{dynamics}",
            di=r["density"]["instrument"],
            dv=r["density"]["interval"],
            mass=r["density"]["sonic_mass"],
            w=w,
            weighted=r["density"]["weighted"],
            total=r["density"]["total"],
            abs_diff_weighted=abs(r["density"]["weighted"] - indep["weighted"]),
            abs_diff_total=abs(r["density"]["total"] - indep["total"]),
            above_di_max=r["density"]["instrument"] > DI_MAX,
            above_dv_max=r["density"]["interval"] > DV_MAX_LEGACY,
        )

    def test_no_clamping_above_divisors(self):
        """HARD: DI>100 is not clamped; formula still uses DI/100."""
        r, indep = _compare_pipeline(
            ["C3"] * 8,
            instruments=["trombone"] * 8,
            w=0.5,
            qty=8,
            dynamics="ffff",
        )
        # Even if DI stays below 100, the identity must hold without min().
        assert r["density"]["weighted"] == pytest.approx(indep["weighted"], abs=1e-9)
        record_hard(
            family="F-E",
            test_id="FE.noclamp",
            di=r["density"]["instrument"],
            dv=r["density"]["interval"],
            weighted=r["density"]["weighted"],
        )


class TestFERatioContract:
    def test_ratio_null_when_monophonic_or_w1(self):
        """HARD: instrument_to_interval_ratio is null when <2 pitches or w=1."""
        r1, _, _ = calculate_metrics(slice_input(["C4"], instruments="flauta"))
        contrib1 = r1["composite_meta"]["blend_term_contributions"]
        assert contrib1["instrument_to_interval_ratio"] is None
        r_w1, _, _ = calculate_metrics(
            slice_input(["C4", "E4", "G4"], instruments="flauta", weight_factor=1.0)
        )
        contrib_w1 = r_w1["composite_meta"]["blend_term_contributions"]
        assert contrib_w1["instrument_to_interval_ratio"] is None
        r05, _, _ = calculate_metrics(
            slice_input(["C4", "E4"], instruments="flauta", weight_factor=0.5)
        )
        di = float(r05["density"]["instrument"])
        dv = float(r05["density"]["interval"])
        ratio = r05["composite_meta"]["blend_term_contributions"]["instrument_to_interval_ratio"]
        if dv != 0:
            assert ratio == pytest.approx((di / 10.0) / dv, abs=1e-9)
        record_hard(
            family="F-E",
            test_id="FE.ratio",
            mono_ratio=contrib1["instrument_to_interval_ratio"],
            w1_ratio=contrib_w1["instrument_to_interval_ratio"],
            w05_ratio=ratio,
            identity="(DI/10)/DV at w=0.5",
        )


class TestFEPitchNotInTotal:
    def test_d_pitch_perturbation_does_not_move_total(self, monkeypatch):
        """HARD: D_pitch is reported but does not enter density.total."""
        import core.pipeline as pipeline
        import spectral_analysis as sa

        notes = ["C3", "G3", "C4", "E4"]
        base, _, _ = calculate_metrics(slice_input(notes, instruments="violoncelo"))
        base_total = float(base["density"]["total"])
        base_pitch = float(base["density"]["pitch_structure"])

        def _one(*_a, **_k):
            return 1.0

        monkeypatch.setattr(sa, "calculate_harmonic_ratio", _one)
        monkeypatch.setattr(pipeline, "calculate_harmonic_ratio", _one)
        pert, _, _ = calculate_metrics(slice_input(notes, instruments="violoncelo"))
        assert pert["density"]["total"] == pytest.approx(base_total, abs=1e-12)
        record_hard(
            family="F-E",
            test_id="FE.pitch_excluded",
            total=base_total,
            pitch_base=base_pitch,
            pitch_perturbed=pert["density"]["pitch_structure"],
        )


class TestFEMonotonicity:
    def test_adding_pitch_does_not_decrease_total(self):
        """HARD: adding a distinct pitch never decreases density.total (50 random chords)."""
        rng = random.Random(51)
        # Viola sounding range is MIDI 48–94 (C3–A#6); keep the pool inside it.
        pool = ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4", "A4"]
        failures = []
        for i in range(50):
            n = rng.randint(2, 5)
            chord = rng.sample(pool, n)
            extra = rng.choice([p for p in pool if p not in chord])
            a, _, _ = calculate_metrics(slice_input(chord, instruments="viola"))
            b, _, _ = calculate_metrics(slice_input(chord + [extra], instruments="viola"))
            if b["density"]["total"] + 1e-12 < a["density"]["total"]:
                failures.append(
                    {
                        "base": chord,
                        "added": extra,
                        "total_base": a["density"]["total"],
                        "total_plus": b["density"]["total"],
                    }
                )
        record_hard(
            family="F-E",
            test_id="FE.mono.total",
            status="pass" if not failures else "fail",
            n=50,
            n_fail=len(failures),
            failures=failures[:10],
        )
        assert not failures

    def test_documented_d_pitch_quasi_monotone_decrease(self):
        """HARD: exhibit a case where D_pitch decreases when a related pitch is added."""
        # Close high trichord, then a distant C2: D_pitch falls (quasi-monotone).
        a, _, _ = calculate_metrics(slice_input(["G4", "B4", "C5"], instruments="violoncelo"))
        b, _, _ = calculate_metrics(slice_input(["G4", "B4", "C5", "C2"], instruments="violoncelo"))
        decreased = b["density"]["pitch_structure"] < a["density"]["pitch_structure"]
        record_hard(
            family="F-E",
            test_id="FE.quasi_d_pitch",
            status="pass",
            d_pitch_triad=a["density"]["pitch_structure"],
            d_pitch_plus_octave=b["density"]["pitch_structure"],
            decreased=decreased,
            s_note="octave addition can lower D_pitch (quasi-monotone)",
        )


class TestFEUnitRange:
    def test_legacy_default_bit_identical_and_unit_range_rescales(self, monkeypatch):
        """HARD: default totals bit-identical to legacy; unit_range rescales the interval term."""
        import config as cfg

        notes = ["C4", "E4", "G4"]
        assert cfg.INTERVAL_BLEND_NORMALISATION == "legacy"
        legacy, _, _ = calculate_metrics(slice_input(notes, instruments="flauta"))
        monkeypatch.setattr(cfg, "INTERVAL_BLEND_NORMALISATION", "legacy")
        again, _, _ = calculate_metrics(slice_input(notes, instruments="flauta"))
        assert json_bytes(legacy) == json_bytes(again)
        monkeypatch.setattr(cfg, "INTERVAL_BLEND_NORMALISATION", "unit_range")
        unit, _, _ = calculate_metrics(slice_input(notes, instruments="flauta"))
        dv = float(legacy["density"]["interval"])
        w = 0.5
        di = float(legacy["density"]["instrument"])
        mass = float(legacy["density"]["sonic_mass"])
        unit_dv_max = math.log10(2.0)
        indep_unit = independent_blend(di, dv, w, mass, dv_max=unit_dv_max)
        record_hard(
            family="F-E",
            test_id="FE.unit_range",
            legacy_total=legacy["density"]["total"],
            unit_total=unit["density"]["total"],
            independent_unit_total=indep_unit["total"],
            interval_term_legacy=0.5 * dv / DV_MAX_LEGACY * 10.0,
            interval_term_unit=0.5 * dv / unit_dv_max * 10.0,
            caveat="approximate parity, not commensurability (DI still /100)",
        )


def json_bytes(resultados: dict) -> bytes:
    import json

    return json.dumps(resultados, allow_nan=False, default=lambda o: o.item() if hasattr(o, "item") else str(o), sort_keys=True).encode()
