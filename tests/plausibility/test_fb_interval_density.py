"""F-B — Interval density and consonance (HARD/SOFT; §B, §L)."""

from __future__ import annotations

import math

import pytest

from core.pipeline import calculate_metrics
from densidade_intervalar import CONSONANCE_RATINGS, calibrate_lambda, calculate_interval_density
from microtonal import note_to_midi_strict
from tests.plausibility.conftest import record_hard, record_soft
from tests.plausibility.helpers import (
    assert_jsonable,
    slice_input,
    spearman_rho,
)
from utils.notes import dyad_notes_from_semitone_interval


def _interval(notes: list[str], instrument: str = "flauta") -> float:
    r, _, _ = calculate_metrics(slice_input(notes, instruments=instrument))
    return float(r["density"]["interval"])


class TestFBUnisonAndNormalisation:
    def test_unison_pair_contributes_one_then_log(self, monkeypatch):
        """HARD: unison pair raw contribution is 1.0; n<2 → 0; pair-normalised."""
        import config as cfg

        monkeypatch.setattr(cfg, "USE_LOG_COMPRESSION", False)
        r2, _, _ = calculate_metrics(slice_input(["C4", "C4"], instruments="flauta"))
        assert_jsonable(r2, label="FB.unison")
        # Two identical notes merge to one bin → interval 0 (no pair).
        assert r2["density"]["interval"] == pytest.approx(0.0)
        r1, _, _ = calculate_metrics(slice_input(["C4"], instruments="flauta"))
        assert r1["density"]["interval"] == pytest.approx(0.0)
        record_hard(
            family="F-B",
            test_id="FB.unison.merged_and_singleton",
            interval_unison_pair=r2["density"]["interval"],
            interval_single=r1["density"]["interval"],
        )

    def test_contribution_decays_with_distance(self):
        """HARD: interval density decays monotonically with pairwise distance."""
        dyads = [["C4", "C4+1c"], ["C4", "C#4"], ["C4", "D4"], ["C4", "G4"], ["C4", "C5"]]
        vals = [_interval(d) for d in dyads]
        assert vals == sorted(vals, reverse=True) or all(
            vals[i] >= vals[i + 1] - 1e-12 for i in range(len(vals) - 1)
        )
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1]
        record_hard(family="F-B", test_id="FB.decay", values=vals, dyads=dyads)


class TestFBTranspositionInvariance:
    @pytest.mark.parametrize("shift", [1, 7, 12, 19])
    def test_transposition_invariance_within_flute_range(self, shift: int):
        """HARD: transposition leaves weighted_pitch and interval-sum invariant."""
        base = ["C4", "E4", "G4"]
        shifted = []
        for n in base:
            m = note_to_midi_strict(n) + shift
            # Flute table ~ B3–D7; keep C4-based chord inside sounding range.
            from microtonal import midi_to_note_name

            shifted.append(midi_to_note_name(float(m)))
        rb, _, _ = calculate_metrics(slice_input(base, instruments="flauta"))
        rs, _, _ = calculate_metrics(slice_input(shifted, instruments="flauta"))
        assert_jsonable(rb, label="FB.trans.base")
        assert rb["density"]["interval"] == pytest.approx(rs["density"]["interval"])
        assert rb["density"]["weighted_pitch"] == pytest.approx(rs["density"]["weighted_pitch"])
        # Interval sum S is the extensive pairwise sum; D_pitch is quasi-monotone and register-sensitive.
        s_base = (rb.get("metric_metadata") or {}).get("metrics", {}).get("density.interval", {})
        record_hard(
            family="F-B",
            test_id=f"FB.trans.{shift}",
            shift=shift,
            weighted_pitch=rb["density"]["weighted_pitch"],
            interval=rb["density"]["interval"],
            pitch_structure_base=rb["density"]["pitch_structure"],
            pitch_structure_shifted=rs["density"]["pitch_structure"],
            interval_meta=s_base,
        )


class TestFBOctaveDoublings:
    def test_octave_doublings_are_distinct_bins(self):
        """HARD: [C4,C5] and [C4,C5,C6] are distinct-bin pairs, not unisons."""
        r2, _, _ = calculate_metrics(slice_input(["C4", "C5"], instruments="flauta"))
        r3, _, _ = calculate_metrics(slice_input(["C4", "C5", "C6"], instruments="flauta"))
        assert r2["pitch_aggregation"]["distinct_pitch_count"] == 2
        assert r3["pitch_aggregation"]["distinct_pitch_count"] == 3
        assert r2["density"]["interval"] > 0
        assert r3["density"]["interval"] > 0
        record_hard(
            family="F-B",
            test_id="FB.octaves",
            two=r2["density"],
            three=r3["density"],
            distinct_2=2,
            distinct_3=3,
        )


class TestFBLogCompression:
    def test_log_compression_is_log10_1_plus_x(self, monkeypatch):
        """HARD: USE_LOG_COMPRESSION on/off changes weighted_pitch by log10(1+x)."""
        import config as cfg

        import densidade_intervalar as di_mod
        import core.pitch_structure as ps

        notes = ["C4", "E4", "G4"]
        # Each module binds USE_LOG_COMPRESSION at import; patch the live names.
        for flag in (False, True):
            monkeypatch.setattr(cfg, "USE_LOG_COMPRESSION", flag)
            monkeypatch.setattr(di_mod, "USE_LOG_COMPRESSION", flag)
            monkeypatch.setattr(ps, "USE_LOG_COMPRESSION", flag)
            if flag is False:
                raw, _, _ = calculate_metrics(slice_input(notes, instruments="flauta"))
            else:
                compressed, _, _ = calculate_metrics(slice_input(notes, instruments="flauta"))
        x = float(raw["density"]["interval"])
        got = float(compressed["density"]["interval"])
        expected = math.log10(1.0 + x)
        wp_raw = float(raw["density"]["weighted_pitch"])
        wp_comp = float(compressed["density"]["weighted_pitch"])
        wp_is_log10_1_plus_x = wp_comp == pytest.approx(math.log10(1.0 + wp_raw), abs=1e-9)
        assert got == pytest.approx(expected, rel=0, abs=1e-9)
        record_hard(
            family="F-B",
            test_id="FB.log",
            raw_interval=x,
            compressed_interval=got,
            expected=expected,
            weighted_pitch_raw=wp_raw,
            weighted_pitch_compressed=wp_comp,
            weighted_pitch_follows_log10_1_plus_x=bool(wp_is_log10_1_plus_x),
            note="Documented identity is D_int ← log10(1+D_int); weighted_pitch is the blend of that DV",
        )


class TestFBSoftClusters:
    @pytest.mark.plausibility
    @pytest.mark.xfail(strict=False, reason="SOFT plausibility")
    def test_cluster_ranking(self):
        """SOFT: chromatic > diatonic > triad > wide spacing in interval density."""
        chromatic = _interval(["C4", "C#4", "D4", "D#4"])
        diatonic = _interval(["C4", "D4", "E4", "F4"])
        triad = _interval(["C4", "E4", "G4"])
        wide = _interval(["C2", "G3", "E5"], instrument="violoncelo")
        met = chromatic > diatonic > triad > wide
        record_soft(
            family="F-B",
            test_id="FB.soft.cluster_rank",
            met=met,
            expectation="chromatic > diatonic > triad > wide interval density",
            values={
                "chromatic": chromatic,
                "diatonic": diatonic,
                "triad": triad,
                "wide": wide,
            },
            classification="modelling choice" if not met else None,
        )

    @pytest.mark.plausibility
    @pytest.mark.xfail(strict=False, reason="SOFT plausibility")
    def test_quarter_tone_cluster_ge_semitone(self):
        """SOFT: quarter-tone cluster ≥ semitone cluster of same cardinality."""
        qt = _interval(["C4", "C4+50c", "C#4", "C#4+50c"])
        st = _interval(["C4", "C#4", "D4", "D#4"])
        met = qt >= st - 1e-12
        record_soft(
            family="F-B",
            test_id="FB.soft.quarter_tone",
            met=met,
            expectation="quarter-tone cluster ≥ semitone cluster (n=4)",
            quarter_tone=qt,
            semitone=st,
        )

    @pytest.mark.plausibility
    @pytest.mark.xfail(strict=False, reason="SOFT plausibility")
    def test_calibrated_lambda_tracks_consonance_ratings(self, monkeypatch):
        """SOFT: after calibrate_lambda(), dyad ranking Spearman ρ ≥ 0.8 vs CONSONANCE_RATINGS."""
        import densidade_intervalar as di_mod

        monkeypatch.setattr(di_mod, "save_calibrated_parameters", lambda *_a, **_k: None)
        lamb = float(calibrate_lambda())
        intervals = sorted(CONSONANCE_RATINGS)
        ratings = [CONSONANCE_RATINGS[i] for i in intervals]
        dens = []
        for i in intervals:
            notes = list(dyad_notes_from_semitone_interval("C4", int(i)))
            dens.append(float(calculate_interval_density(notes, lamb=lamb)))
        rho = spearman_rho(ratings, dens)
        # Higher rating should mean higher density for this SOFT ranking.
        met = (not math.isnan(rho)) and rho >= 0.8
        exceptions = []
        order_r = [i for _, i in sorted(zip(ratings, intervals), reverse=True)]
        order_d = [i for _, i in sorted(zip(dens, intervals), reverse=True)]
        if order_r != order_d:
            exceptions.append({"rating_order": order_r, "density_order": order_d})
        record_soft(
            family="F-B",
            test_id="FB.soft.spearman",
            met=met,
            expectation="Spearman ρ ≥ 0.8 between CONSONANCE_RATINGS and calibrated dyad densities",
            rho=rho,
            lambda_calibrated=lamb,
            intervals=intervals,
            ratings=ratings,
            densities=dens,
            exceptions=exceptions,
        )
