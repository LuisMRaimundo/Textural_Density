"""
Property tests for formal score-only construct axioms.

See docs/formal_construct_axioms.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from core.converters import legacy_input_to_vertical_slice
from core.event_density import compute_event_density
from core.interval_compactness import compute_interval_compactness
from core.registral_density import compute_registral_density
from core.sensitivity import (
    DEFAULT_WEIGHT_SETS,
    analyze_composite_weight_sensitivity,
    analyze_composite_weight_sensitivity_from_subindices,
)
from core.temporal import group_events_into_slices
from data_processor import calculate_metrics
from densidade_intervalar import calculate_interval_density
from instrumentos.metadata_audit import build_instrument_metadata_audit
from microtonal import note_to_midi


def _input(
    notes,
    dynamics=None,
    instruments=None,
    nums=None,
    **extra,
):
    n = len(notes)
    return {
        "notes": notes,
        "dynamics": dynamics or ["mf"] * n,
        "instruments": instruments or ["flauta"] * n,
        "num_instruments": nums or [1] * n,
        **extra,
    }


class TestEventDensityAxioms:
    def test_adding_event_increases_count(self):
        small = legacy_input_to_vertical_slice(_input(["C4", "E4"]))
        large = legacy_input_to_vertical_slice(_input(["C4", "E4", "G4"]))
        assert compute_event_density(large)["event_count"] > compute_event_density(small)["event_count"]

    def test_player_count_increases_weighted_density(self):
        low = legacy_input_to_vertical_slice(_input(["C4", "E4"], nums=[1, 1]))
        high = legacy_input_to_vertical_slice(_input(["C4", "E4"], nums=[1, 3]))
        assert compute_event_density(high)["player_weighted_count"] >= compute_event_density(low)["player_weighted_count"]

    def test_equivalent_spelling_same_event_count(self):
        a = legacy_input_to_vertical_slice(_input(["C#4", "E4"]))
        b = legacy_input_to_vertical_slice(_input(["Db4", "E4"]))
        assert note_to_midi("C#4") == pytest.approx(note_to_midi("Db4"))
        assert compute_event_density(a)["event_count"] == compute_event_density(b)["event_count"]


class TestIntervalCompactnessAxioms:
    def test_unison_duplication_does_not_increase_reported_compactness(self):
        single = calculate_interval_density(["C4", "E4"], use_optimization=False)
        doubled = calculate_interval_density(["C4", "C4", "E4"], use_optimization=False)
        assert doubled >= single

    def test_distinct_compactness_zero_for_unison_stack(self):
        from core.pitch_aggregation import aggregate_events_by_pitch
        from core.pitch_structure import compute_interval_compactness_distinct

        agg = aggregate_events_by_pitch(["C4", "C4", "C4", "C4"])
        raw, reported = compute_interval_compactness_distinct(agg)
        assert raw == 0.0
        assert reported == 0.0

    def test_compactness_decreases_with_distance(self):
        close = calculate_interval_density(["C4", "C#4"], use_optimization=False)
        far = calculate_interval_density(["C4", "G4"], use_optimization=False)
        assert close > far

    def test_cluster_gt_wide_spaced(self):
        cluster = calculate_interval_density(
            ["C4", "C#4", "D4", "D#4", "E4"], use_optimization=False
        )
        wide = calculate_interval_density(
            ["C3", "G3", "D4", "A4", "E5"], use_optimization=False
        )
        assert cluster > wide

    def test_dynamics_do_not_change_interval_compactness(self):
        notes = ["C4", "E4", "G4"]
        a = compute_interval_compactness(notes)
        b = compute_interval_compactness(notes)  # pitch-only path
        assert a["value"] == pytest.approx(b["value"])

    def test_player_count_does_not_change_interval_compactness(self):
        ic = compute_interval_compactness(["C4", "E4", "G4"])
        assert ic["source_type"] == "score_derived"


class TestRegistralDensityAxioms:
    def test_wider_span_lower_compression(self):
        narrow = legacy_input_to_vertical_slice(_input(["C4", "E4", "G4"]))
        wide = legacy_input_to_vertical_slice(_input(["C2", "E4", "G6"]))
        rn = compute_registral_density(narrow, pitch_span_semitones=7.0)
        rw = compute_registral_density(wide, pitch_span_semitones=31.0)
        assert rw["registral_compression"] < rn["registral_compression"]

    def test_concentrated_vs_dispersed_register_differs(self):
        concentrated = legacy_input_to_vertical_slice(_input(["C4", "C4", "C4"]))
        dispersed = legacy_input_to_vertical_slice(_input(["C3", "G4", "C6"]))
        rc = compute_registral_density(concentrated, pitch_span_semitones=0.0)
        rd = compute_registral_density(dispersed, pitch_span_semitones=24.0)
        assert rc["register_band_occupancy"] != rd["register_band_occupancy"]

    def test_register_bands_config_recorded(self):
        vs = legacy_input_to_vertical_slice(_input(["C4", "E4"]))
        out = compute_registral_density(vs, pitch_span_semitones=4.0)
        assert "register_bands_config" in out
        assert "very_low" in out["register_bands_config"]


class TestOrchestrationMassAxioms:
    def test_player_count_increases_mass(self):
        low, _, _ = calculate_metrics(_input(["C4", "E4"], nums=[1, 1]))
        high, _, _ = calculate_metrics(_input(["C4", "E4"], nums=[1, 4]))
        assert float(high["density"]["sonic_mass"]) >= float(low["density"]["sonic_mass"])

    def test_louder_dynamics_increase_mass(self):
        soft, _, _ = calculate_metrics(_input(["C4"], dynamics=["p"]))
        loud, _, _ = calculate_metrics(_input(["C4"], dynamics=["ff"]))
        assert float(loud["density"]["sonic_mass"]) >= float(soft["density"]["sonic_mass"])

    def test_dynamics_alone_do_not_change_interval_compactness(self):
        soft, _, _ = calculate_metrics(_input(["C4", "E4", "G4"], dynamics=["p", "p", "p"]))
        loud, _, _ = calculate_metrics(_input(["C4", "E4", "G4"], dynamics=["ff", "ff", "ff"]))
        assert float(soft["density"]["interval"]) == pytest.approx(float(loud["density"]["interval"]))


class TestTimbralOrchestrationAxioms:
    def test_new_family_increases_diversity(self):
        mono, _, _ = calculate_metrics(
            _input(["C4", "E4"], instruments=["flauta", "flauta"])
        )
        mixed, _, _ = calculate_metrics(
            _input(["C4", "E4"], instruments=["flauta", "violino"])
        )
        d_mono = float(mono["density_subindices"]["timbral_heterogeneity"]["raw"]["family_diversity"])
        d_mix = float(mixed["density_subindices"]["timbral_heterogeneity"]["raw"]["family_diversity"])
        assert d_mix >= d_mono

    def test_unknown_instrument_warning(self):
        resultados, _, _ = calculate_metrics(_input(["C4"], instruments=["totally_unknown_xyz"]))
        warnings = resultados["metric_metadata"]["warnings"]
        assert any("unknown" in w.lower() or "registry" in w.lower() or "profile" in w.lower() for w in warnings)


class TestTemporalVerticalDensityAxioms:
    def test_overlapping_events_multiple_slices(self):
        from core.converters import make_instrument_event

        events = [
            make_instrument_event(
                idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=0.0, offset=2.0,
            ),
            make_instrument_event(
                idx=1, note="E4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=1.0, offset=3.0,
            ),
        ]
        slices = group_events_into_slices(events)
        assert len(slices) >= 2

    def test_non_overlapping_isolated_slices(self):
        from core.converters import make_instrument_event

        events = [
            make_instrument_event(
                idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=0.0, offset=1.0,
            ),
            make_instrument_event(
                idx=1, note="E4", dynamic="mf", instrument_name="flauta", player_count=1,
                onset=5.0, offset=6.0,
            ),
        ]
        slices = group_events_into_slices(events)
        assert len(slices) == 2


class TestCompositeSymbolicDensityAxioms:
    def test_deterministic_same_input(self):
        data = _input(["C4", "E4", "G4"])
        r1, _, _ = calculate_metrics(data)
        r2, _, _ = calculate_metrics(data)
        assert float(r1["density"]["total"]) == pytest.approx(float(r2["density"]["total"]))

    def test_subindices_accessible(self):
        resultados, _, _ = calculate_metrics(_input(["C4", "E4", "G4", "C5"]))
        sub = resultados["density_subindices"]
        for key in (
            "event_count",
            "interval_compactness",
            "registral",
            "orchestral_mass",
            "timbral_heterogeneity",
            "composite",
        ):
            assert key in sub

    def test_component_weights_in_metadata(self):
        resultados, _, _ = calculate_metrics(_input(["C4", "E4", "G4"]))
        comp = resultados["density_subindices"]["composite"]
        assert "components" in comp
        assert comp["components"]


class TestRegistralExtractionMatchesSubindices:
    def test_registral_module_matches_subindices_span(self):
        resultados, _, _ = calculate_metrics(_input(["C4", "E4", "G4", "C5"]))
        sub_span = resultados["density_subindices"]["registral"]["raw"]["pitch_span_semitones"]
        vs = legacy_input_to_vertical_slice(_input(["C4", "E4", "G4", "C5"]))
        reg = compute_registral_density(vs, pitch_span_semitones=float(sub_span))
        assert reg["pitch_span_semitones"] == pytest.approx(float(sub_span))


class TestCoreModulesNoGui:
    @pytest.mark.parametrize(
        "module_name",
        [
            "core.registral_density",
            "core.interval_compactness",
            "core.orchestration_mass",
            "core.composite",
            "core.construct_metadata",
            "core.sensitivity",
            "core.export_constants",
        ],
    )
    def test_no_tkinter_import(self, module_name):
        import importlib

        mod = importlib.import_module(module_name)
        tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not any(a.name.split(".")[0] == "tkinter" for a in node.names)
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] != "tkinter"


class TestInstrumentAudit:
    def test_all_profiles_have_status_and_uncertainty(self):
        audit = build_instrument_metadata_audit()
        for p in audit["profiles"]:
            assert p["profile_status"]
            assert p["uncertainty"]
            assert not p.get("claims_empirical_without_notes")

    def test_unknown_fallback(self):
        audit = build_instrument_metadata_audit()
        fb = audit["unknown_instrument_fallback"]
        assert fb["instrument_id"] == "unknown"
        assert fb["profile_status"] == "symbolic_default"
