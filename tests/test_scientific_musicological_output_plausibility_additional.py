"""
High-priority scientific / musicological output plausibility tests.

Validates integrated symbolic-density outputs (``calculate_metrics``, ``analyze_score``)
for ordinally plausible relationships on controlled score scenarios.

This layer exercises near-final pipeline results — not isolated formula internals
(covered in densidade_intervalar contract and formal construct axiom tests).
Does not assert real-world acoustic ordering between curated instruments.
"""

from __future__ import annotations

import math
from unittest import mock

import pytest

from core.converters import legacy_input_to_vertical_slice, make_instrument_event
from core.pipeline import calculate_metrics
from core.registral_density import compute_registral_density
from core.score_analysis import analyze_score
from data_processor import calculate_metrics as dp_calculate_metrics
from instrumentos.registry import profile_for_event


def _slice_input(
    notes: list[str],
    *,
    dynamics: list[str] | None = None,
    instruments: list[str] | None = None,
    nums: list[int] | None = None,
    weight_factor: float = 0.5,
) -> dict:
    n = len(notes)
    return {
        "notes": notes,
        "dynamics": dynamics or ["mf"] * n,
        "instruments": instruments or ["flauta"] * n,
        "num_instruments": nums or [1] * n,
        "weight_factor": weight_factor,
    }


def _metrics(notes: list[str], **kwargs) -> dict:
    resultados, _, _ = calculate_metrics(_slice_input(notes, **kwargs))
    return resultados


# ---------------------------------------------------------------------------
# A. Vertical symbolic density plausibility
# ---------------------------------------------------------------------------


class TestVerticalSymbolicDensityPlausibility:
    """Dense chromatic textures rank above sparse dyads / isolated notes."""

    def test_sparse_to_dense_monotonic_pitch_structure(self):
        isolated = _metrics(["C4"])
        dyad = _metrics(["C4", "G4"])
        chromatic = _metrics(["C4", "C#4", "D4", "D#4", "E4"])

        assert isolated["pitch_aggregation"]["event_count"] == 1
        assert dyad["pitch_aggregation"]["event_count"] == 2
        assert chromatic["pitch_aggregation"]["event_count"] == 5

        assert isolated["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert dyad["pitch_aggregation"]["distinct_pitch_count"] == 2
        assert chromatic["pitch_aggregation"]["distinct_pitch_count"] == 5

        assert isolated["density"]["pitch_structure"] == pytest.approx(0.0)
        assert dyad["density"]["pitch_structure"] > isolated["density"]["pitch_structure"]
        assert chromatic["density"]["pitch_structure"] > dyad["density"]["pitch_structure"]

    def test_chromatic_cluster_exceeds_sparse_dyad_in_composite_total(self):
        dyad = _metrics(["C4", "G4"])
        chromatic = _metrics(["C4", "C#4", "D4", "E4"])
        assert chromatic["density"]["total"] > dyad["density"]["total"]
        assert chromatic["density"]["interval"] > dyad["density"]["interval"]

    def test_adding_notated_event_increases_event_count(self):
        two = _metrics(["C4", "E4"])
        three = _metrics(["C4", "E4", "G4"])
        assert three["pitch_aggregation"]["event_count"] == two["pitch_aggregation"]["event_count"] + 1
        assert three["pitch_aggregation"]["distinct_pitch_count"] == 3

    def test_unison_doubling_raises_mass_without_inflating_distinct_pitch_count(self):
        single = _metrics(["C4", "E4"])
        doubled = _metrics(["C4", "C4", "E4"])
        assert doubled["pitch_aggregation"]["distinct_pitch_count"] == 2
        assert doubled["pitch_aggregation"]["doubling_count"] == 1
        assert doubled["density"]["sonic_mass"] >= single["density"]["sonic_mass"]
        assert doubled["density"]["pitch_structure"] == pytest.approx(
            single["density"]["pitch_structure"], rel=1e-6
        )


# ---------------------------------------------------------------------------
# B. Interval / compactness plausibility (integrated pipeline outputs)
# ---------------------------------------------------------------------------


class TestIntervalCompactnessIntegratedPlausibility:
    """Close-position clusters outrank wide-spaced voicings in reported interval density."""

    def test_close_position_outranks_wide_dispersed_voicing(self):
        close = _metrics(["C4", "E4", "G4", "C5"])
        wide = _metrics(["C2", "E3", "G4", "C6"])
        assert close["pitch_aggregation"]["distinct_pitch_count"] == wide["pitch_aggregation"]["distinct_pitch_count"]
        assert close["density"]["interval"] > wide["density"]["interval"]
        assert close["density_subindices"]["interval_compactness"]["normalized"] >= wide["density_subindices"]["interval_compactness"]["normalized"]

    def test_compact_chromatic_beats_wide_same_cardinality(self):
        cluster = _metrics(["C4", "C#4", "D4", "D#4"])
        spread = _metrics(["C3", "E3", "G#3", "C4"])
        assert cluster["density"]["interval"] > spread["density"]["interval"]

    def test_dynamics_do_not_alter_integrated_interval_compactness(self):
        notes = ["C4", "E4", "G4"]
        soft = _metrics(notes, dynamics=["pp", "pp", "pp"])
        loud = _metrics(notes, dynamics=["ff", "ff", "ff"])
        assert soft["density"]["interval"] == pytest.approx(loud["density"]["interval"])
        assert soft["density_subindices"]["interval_compactness"]["normalized"] == pytest.approx(
            loud["density_subindices"]["interval_compactness"]["normalized"]
        )
        assert soft["density_subindices"]["registral"]["raw"]["pitch_span_semitones"] == pytest.approx(
            loud["density_subindices"]["registral"]["raw"]["pitch_span_semitones"]
        )

    def test_qty_does_not_alter_integrated_interval_compactness(self):
        base = _metrics(["C4", "E4", "G4"], nums=[1, 1, 1])
        heavy = _metrics(["C4", "E4", "G4"], nums=[8, 8, 8])
        assert base["density"]["interval"] == pytest.approx(heavy["density"]["interval"])
        assert base["pitch_aggregation"]["distinct_pitch_count"] == heavy["pitch_aggregation"]["distinct_pitch_count"]


# ---------------------------------------------------------------------------
# C. Registral density / dispersion plausibility
# ---------------------------------------------------------------------------


class TestRegistralDispersionIntegratedPlausibility:
    """Register spread lowers registral compactness without corrupting pitch counts."""

    def test_compact_register_higher_compression_than_wide_spread(self):
        compact = _metrics(["C4", "E4", "G4"])
        dispersed = _metrics(["C2", "E4", "G6"])
        compact_reg = compact["density_subindices"]["registral"]["raw"]
        dispersed_reg = dispersed["density_subindices"]["registral"]["raw"]
        assert compact_reg["pitch_span_semitones"] < dispersed_reg["pitch_span_semitones"]
        assert compact_reg["registral_compression"] > dispersed_reg["registral_compression"]

    def test_same_pitch_class_set_register_change_only_affects_registral_block(self):
        close = _metrics(["C4", "E4", "G4"])
        wide = _metrics(["C2", "E4", "G5"])
        assert close["pitch_aggregation"]["distinct_pitch_count"] == wide["pitch_aggregation"]["distinct_pitch_count"]
        assert close["density"]["interval"] != wide["density"]["interval"] or close["density_subindices"]["registral"]["raw"]["pitch_span_semitones"] != wide["density_subindices"]["registral"]["raw"]["pitch_span_semitones"]

    def test_registral_module_agrees_with_pipeline_subindex_span(self):
        notes = ["C2", "E4", "G6"]
        result = _metrics(notes)
        span = result["density_subindices"]["registral"]["raw"]["pitch_span_semitones"]
        vertical_slice = legacy_input_to_vertical_slice(_slice_input(notes))
        registral = compute_registral_density(vertical_slice, pitch_span_semitones=span)
        assert registral["pitch_span_semitones"] == pytest.approx(span)
        assert registral["source_type"] == "score_derived"
        assert result["pitch_aggregation"]["distinct_pitch_count"] == 3


# ---------------------------------------------------------------------------
# D. Dynamics semantics
# ---------------------------------------------------------------------------


class TestDynamicsSymbolicSemantics:
    """Louder markings scale orchestration mass; pitch structure stays symbolic."""

    def test_louder_dynamics_raise_instrument_density_and_sonic_mass(self):
        soft = _metrics(["C4", "E4", "G4"], dynamics=["pp", "pp", "pp"])
        loud = _metrics(["C4", "E4", "G4"], dynamics=["ff", "ff", "ff"])
        assert loud["density"]["instrument"] > soft["density"]["instrument"]
        assert loud["density"]["sonic_mass"] > soft["density"]["sonic_mass"]

    def test_dynamics_leave_interval_and_registral_span_untouched(self):
        soft = _metrics(["C4", "E4", "G4"], dynamics=["pp", "pp", "pp"])
        loud = _metrics(["C4", "E4", "G4"], dynamics=["ff", "ff", "ff"])
        assert loud["density"]["interval"] == pytest.approx(soft["density"]["interval"])
        assert loud["pitch_aggregation"]["distinct_pitch_count"] == soft["pitch_aggregation"]["distinct_pitch_count"]
        assert loud["density_subindices"]["registral"]["raw"]["pitch_span_semitones"] == pytest.approx(
            soft["density_subindices"]["registral"]["raw"]["pitch_span_semitones"]
        )

    def test_dynamic_markings_documented_as_symbolic_score_input(self):
        result = _metrics(["C4"], dynamics=["ff"])
        combined = " ".join(result["metric_metadata"]["assumptions"]).lower()
        assert result["metric_metadata"]["score_only_mode"] is True
        assert "symbolic" in combined
        assert "no audio waveforms were analysed" in combined or "does not analyse audio" in combined


# ---------------------------------------------------------------------------
# E. Qty / player-count semantics
# ---------------------------------------------------------------------------


class TestQtyPlayerCountIntegratedSemantics:
    """Player count scales mass; distinct pitch semantics stay notated-only."""

    def test_increasing_qty_raises_sonic_mass_on_same_pitch(self):
        one = _metrics(["C4"], nums=[1])
        section = _metrics(["C4"], nums=[12])
        assert section["density"]["sonic_mass"] > one["density"]["sonic_mass"]
        assert section["pitch_aggregation"]["total_player_count"] == 12
        assert section["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert section["pitch_aggregation"]["event_count"] == 1

    def test_qty_does_not_create_extra_distinct_pitches(self):
        section = _metrics(["C4", "C4"], nums=[6, 6])
        assert section["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert section["pitch_aggregation"]["event_count"] == 2

    def test_section_unison_differs_from_distinct_pitches_in_pitch_structure(self):
        unison_section = _metrics(["C4"], nums=[8])
        chromatic = _metrics(["C4", "C#4", "D4", "E4"], nums=[2, 2, 2, 2])
        assert chromatic["pitch_aggregation"]["distinct_pitch_count"] > unison_section["pitch_aggregation"]["distinct_pitch_count"]
        assert chromatic["density"]["pitch_structure"] > unison_section["density"]["pitch_structure"]
        assert unison_section["density"]["pitch_structure"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# F. Instrument metadata / acoustic-proxy honesty
# ---------------------------------------------------------------------------


class TestInstrumentMetadataHonestyIntegrated:
    """Unknown/coarse instruments remain finite; provenance labels stay honest."""

    def test_unknown_instrument_produces_finite_integrated_outputs(self):
        resultados, _, _ = dp_calculate_metrics(
            _slice_input(["C4", "E4"], instruments=["totally_unregistered_xyz", "also_unknown_abc"])
        )
        for key in ("interval", "instrument", "weighted", "total", "sonic_mass", "pitch_structure"):
            assert math.isfinite(float(resultados["density"][key]))
        sub = resultados["density_subindices"]
        for block in sub.values():
            raw = block.get("raw")
            if isinstance(raw, dict):
                for val in raw.values():
                    if isinstance(val, (int, float)):
                        assert math.isfinite(float(val))
            elif isinstance(raw, (int, float)):
                assert math.isfinite(float(raw))

    def test_unknown_instrument_metadata_proxy_not_empirical(self):
        resultados, _, _ = dp_calculate_metrics(
            _slice_input(["C4"], instruments=["totally_unregistered_xyz"])
        )
        inst = resultados["metric_metadata"]["metrics"]["density.instrument"]
        assert inst["source_type"] == "metadata_proxy"
        joined = " ".join(inst["assumptions"] + inst["warnings"] + resultados["metric_metadata"]["warnings"]).lower()
        assert "fully calibrated empirical" not in joined
        assert "measured spectrum" not in joined

    def test_curated_instrument_labelled_external_metadata_not_live_measurement(self):
        resultados, _, _ = dp_calculate_metrics(_slice_input(["C4"], instruments=["flauta"]))
        inst = resultados["metric_metadata"]["metrics"]["density.instrument"]
        assert inst["source_type"] == "external_acoustic_metadata"
        assert any("externally sourced" in a.lower() or "external acoustic" in a.lower() for a in inst["assumptions"])
        assert any("does not analyse audio" in a.lower() for a in inst["assumptions"])

    def test_monkeypatched_coarse_profile_never_reports_empirical_validation(self):
        coarse = profile_for_event("__synthetic_coarse_plausibility_xyz__")

        with mock.patch("core.metrics_metadata.resolve_profile", return_value=coarse):
            resultados, _, _ = dp_calculate_metrics(
                _slice_input(["G4"], instruments=["__synthetic_coarse_plausibility_xyz__"])
            )
        inst = resultados["metric_metadata"]["metrics"]["density.instrument"]
        assert inst["source_type"] == "metadata_proxy"
        assert inst["validation_status"] == "heuristic"
        assert "empirical_source" not in inst["validation_status"]
        assert resultados["pitch_aggregation"]["event_count"] == 1


# ---------------------------------------------------------------------------
# G. Microtonal / pitch-bin plausibility
# ---------------------------------------------------------------------------


class TestMicrotonalPitchBinIntegratedPlausibility:
    """Microtonal bins and enharmonic equivalence behave plausibly at pipeline level."""

    def test_enharmonic_spellings_share_one_distinct_pitch_bin(self):
        sharp = _metrics(["C#4", "E4"])
        flat = _metrics(["Db4", "E4"])
        assert sharp["pitch_aggregation"]["distinct_pitch_count"] == 2
        assert flat["pitch_aggregation"]["distinct_pitch_count"] == 2
        assert sharp["density"]["pitch_structure"] == pytest.approx(flat["density"]["pitch_structure"], rel=1e-6)

    def test_microtonal_offset_increases_distinct_bins_without_extra_events(self):
        exact = _metrics(["C4"])
        micro = _metrics(["C4", "C4+25c"])
        assert micro["pitch_aggregation"]["event_count"] == 2
        assert micro["pitch_aggregation"]["distinct_pitch_count"] == 2
        assert micro["density"]["pitch_structure"] > exact["density"]["pitch_structure"]

    def test_microtonal_notation_does_not_crash_and_stays_finite(self):
        result = _metrics(["C4", "C4+25c", "C#4-12c", "E4"])
        assert result["pitch_aggregation"]["distinct_pitch_count"] == 4
        assert math.isfinite(float(result["density"]["total"]))
        assert result["pitch_aggregation"]["event_count"] == 4


# ---------------------------------------------------------------------------
# H. Temporal / slice plausibility
# ---------------------------------------------------------------------------


class TestTemporalSliceIntegratedPlausibility:
    """Overlapping notation yields denser active slices; slicing stays deterministic."""

    @staticmethod
    def _overlap_events():
        return [
            make_instrument_event(
                idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=0.0, duration=2.0,
            ),
            make_instrument_event(
                idx=1, note="E4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=0.0, duration=2.0,
            ),
            make_instrument_event(
                idx=2, note="G4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=0.0, duration=2.0,
            ),
        ]

    @staticmethod
    def _sequential_events():
        return [
            make_instrument_event(
                idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=0.0, duration=1.0,
            ),
            make_instrument_event(
                idx=1, note="E4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=1.0, duration=1.0,
            ),
            make_instrument_event(
                idx=2, note="G4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=2.0, duration=1.0,
            ),
        ]

    def test_overlapping_slice_denser_than_isolated_non_overlapping_slices(self):
        overlap = analyze_score(self._overlap_events())
        sequential = analyze_score(self._sequential_events())
        assert len(overlap.slices) == 1
        assert len(sequential.slices) == 3
        overlap_density = float(overlap.time_series[0]["density_total"])
        sequential_max = max(float(ts["density_total"]) for ts in sequential.time_series)
        assert overlap_density > sequential_max
        assert overlap.time_series[0]["event_count"] == 3

    def test_temporal_aggregation_event_counts_sum_to_notated_assignments(self):
        sequential = analyze_score(self._sequential_events())
        assert sum(int(ts["event_count"]) for ts in sequential.time_series) == 3

    def test_analyze_score_temporal_output_is_deterministic(self):
        events = self._overlap_events()
        first = analyze_score(events)
        second = analyze_score(events)
        assert len(first.time_series) == len(second.time_series)
        for a, b in zip(first.time_series, second.time_series):
            assert a["density_total"] == pytest.approx(b["density_total"])
            assert a["event_count"] == b["event_count"]


# ---------------------------------------------------------------------------
# I. Composite-output plausibility
# ---------------------------------------------------------------------------


class TestCompositeOutputIntegratedPlausibility:
    """High-density symbolic textures outrank sparse ones; subindices stay finite."""

    def test_high_density_texture_ranks_above_low_density_in_total(self):
        sparse = _metrics(["C4"])
        dense = _metrics(["C4", "C#4", "D4", "E4", "G4"])
        assert dense["density"]["total"] > sparse["density"]["total"]
        assert dense["density"]["pitch_structure"] > sparse["density"]["pitch_structure"]

    def test_orchestration_boost_raises_total_without_altering_interval_compactness(self):
        pitch_only = _metrics(["C4", "E4", "G4"], dynamics=["mf"] * 3, nums=[1, 1, 1])
        boosted = _metrics(["C4", "E4", "G4"], dynamics=["ff"] * 3, nums=[4, 4, 4])
        assert boosted["density"]["interval"] == pytest.approx(pitch_only["density"]["interval"])
        assert boosted["density"]["total"] >= pitch_only["density"]["total"]
        assert boosted["density"]["sonic_mass"] > pitch_only["density"]["sonic_mass"]

    def test_all_reported_subindices_finite_and_interpretable(self):
        result = _metrics(["C4", "E4", "G4", "B4"])
        sub = result["density_subindices"]
        assert "interval_compactness" in sub
        assert "registral" in sub
        for name, block in sub.items():
            assert block.get("source_type") in (
                "score_derived",
                "metadata_proxy",
                "external_acoustic_metadata",
                "symbolic_metadata",
            )
            assert block.get("interpretation")
            raw = block.get("raw")
            if isinstance(raw, dict):
                for val in raw.values():
                    if isinstance(val, (int, float)):
                        assert math.isfinite(float(val))
            elif isinstance(raw, (int, float)):
                assert math.isfinite(float(raw))


# ---------------------------------------------------------------------------
# J. Export / metadata plausibility
# ---------------------------------------------------------------------------


class TestExportMetadataIntegratedPlausibility:
    """Exported metadata mirrors pipeline rankings and stays score-honest."""

    def test_required_scientific_metadata_fields_present(self):
        result = _metrics(["C4", "E4", "G4"])
        meta = result["metric_metadata"]
        assert meta["score_only_mode"] is True
        assert "metrics" in meta
        assert "normalization" in meta
        assert "input_hash" in meta
        assert "config_hash" in meta
        for field in ("density.interval", "density.instrument", "density.total", "density.refined"):
            assert field in meta["metrics"]

    def test_combination_tones_not_advertised_in_metadata_or_trace(self):
        result = _metrics(["C4", "E4"])
        meta = result["metric_metadata"]
        assert "combination_tones_enabled" not in meta
        assert "combination_tones" not in meta.get("metrics", {})
        trace = result.get("composite_trace", {})
        assert "combination" not in str(trace).lower()

    def test_exported_metadata_preserves_sparse_vs_dense_ranking(self):
        sparse = _metrics(["C4"])
        dense = _metrics(["C4", "C#4", "D4", "E4"])
        sparse_meta = float(sparse["metric_metadata"]["metrics"]["density.total"]["value"])
        dense_meta = float(dense["metric_metadata"]["metrics"]["density.total"]["value"])
        assert dense_meta > sparse_meta
        assert dense_meta == pytest.approx(float(dense["density"]["total"]))
        assert sparse_meta == pytest.approx(float(sparse["density"]["total"]))

    def test_validation_status_labels_remain_non_empirical_for_heuristic_paths(self):
        result, _, _ = dp_calculate_metrics(
            _slice_input(["C4"], instruments=["totally_unregistered_xyz"])
        )
        inst = result["metric_metadata"]["metrics"]["density.instrument"]
        assert inst["validation_status"] in ("heuristic", "partially_calibrated")
        assert inst["validation_status"] != "empirical_source"
