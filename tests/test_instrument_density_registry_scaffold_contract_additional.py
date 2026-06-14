"""
Additional contract tests for instrument-density registry/scaffold machinery.

Validates safe, honest behaviour under incomplete external instrument metadata.
Does not assert final acoustic-instrument values — only machinery, provenance,
determinism, and non-crashing fallbacks.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from unittest import mock

import pytest

from core.converters import legacy_input_to_vertical_slice, make_instrument_event
from core.metrics_metadata import _instrument_density_epistemics
from core.orchestration import (
    compute_event_one_player_density,
    compute_slice_orchestral_metrics,
)
from core.pipeline import load_instrument_module
from data_processor import calculate_metrics as dp_calculate_metrics
from instrumentos import get_instrument_module
from instrumentos.metadata_audit import audit_instrument_profile, build_instrument_metadata_audit
from instrumentos.registry import profile_for_event, resolve_profile
from instrumentos.spectral_lookup import _sorted_table_entries, lookup_spectral_density


REPO_ROOT = Path(__file__).resolve().parents[1]


def _symbolic_input(
    notes: list[str],
    *,
    instruments: list[str] | None = None,
    dynamics: list[str] | None = None,
    nums: list[int] | None = None,
) -> dict:
    n = len(notes)
    return {
        "notes": notes,
        "dynamics": dynamics or ["mf"] * n,
        "instruments": instruments or ["flauta"] * n,
        "num_instruments": nums or [1] * n,
    }


class TestMissingInstrumentDataScaffold:
    def test_unknown_instrument_full_metrics_does_not_crash(self):
        resultados, densidades, _ = dp_calculate_metrics(
            _symbolic_input(["C4", "E4"], instruments=["totally_unregistered_xyz", "also_unknown_abc"])
        )
        assert math.isfinite(float(resultados["density"]["instrument"]))
        assert len(densidades) == 2

    def test_unknown_instrument_density_finite_and_positive(self):
        mod = get_instrument_module("instrument_not_in_registry_999")
        density = mod.calcular_densidade("G4", "mf")
        assert math.isfinite(density)
        assert density > 0.0

    def test_unknown_instrument_warnings_do_not_claim_empirical_measurement(self):
        resultados, _, _ = dp_calculate_metrics(
            _symbolic_input(["C4"], instruments=["totally_unregistered_xyz"])
        )
        warnings = resultados["metric_metadata"]["warnings"]
        joined = " ".join(warnings).lower()
        assert "coarse" in joined or "proxy" in joined or "registry" in joined or "unknown" in joined
        assert "fully calibrated empirical" not in joined
        assert "measured spectrum" not in joined

    def test_empty_spectral_table_returns_documented_fallback(self, caplog):
        logger = logging.getLogger("test.scaffold.empty_table")
        caplog.set_level(logging.WARNING, logger="test.scaffold.empty_table")
        value = lookup_spectral_density({}, "G4", "mf", logger=logger)
        assert value == pytest.approx(5.0)
        assert any("vazia" in rec.message.lower() or "fallback" in rec.message.lower() for rec in caplog.records)

    def test_unknown_profile_coarse_module_is_marked(self):
        mod = get_instrument_module("__nonexistent_registry_name__")
        assert getattr(mod, "IS_COARSE_DEFAULT", False) is True
        profile = getattr(mod, "PROFILE", None)
        assert profile is not None
        assert profile.instrument_id == "unknown"


class TestPartialInstrumentDataScaffold:
    def test_registered_coarse_instrument_resolves_without_acoustic_table(self):
        mod = get_instrument_module("violin")
        assert getattr(mod, "IS_COARSE_DEFAULT", False) is True
        density = mod.calcular_densidade("A4", "mf")
        assert math.isfinite(density)
        assert density > 0.0

    def test_synthetic_in_range_table_lookup_finite(self):
        logger = logging.getLogger("test.scaffold.in_range")
        table = {
            "C4": {"mf": 10.0, "pp": 8.0, "ff": 12.0},
            "G4": {"mf": 9.0, "pp": 7.0, "ff": 11.0},
        }
        value = lookup_spectral_density(table, "E4", "mf", logger=logger)
        assert math.isfinite(value)
        assert 7.0 <= value <= 12.0

    def test_synthetic_out_of_range_extrapolation_finite_with_warning(self, caplog):
        logger = logging.getLogger("test.scaffold.out_of_range")
        caplog.set_level(logging.WARNING, logger="test.scaffold.out_of_range")
        table = {
            "C4": {"mf": 10.0},
            "C5": {"mf": 8.0},
        }
        value = lookup_spectral_density(table, "C6", "mf", logger=logger)
        assert math.isfinite(value)
        assert any(rec.levelno >= logging.WARNING for rec in caplog.records)

    def test_flauta_sparse_table_lookup_finite_without_asserting_acoustic_truth(self):
        mod = get_instrument_module("flauta")
        density = mod.calcular_densidade("G4", "mf")
        assert math.isfinite(density)
        assert density > 0.0


class TestSourceProvenanceLabelling:
    def test_coarse_only_slice_labels_metadata_proxy(self):
        vs = legacy_input_to_vertical_slice(
            _symbolic_input(["G4", "D4"], instruments=["violin", "viola"])
        )
        source_type, validation, _, warnings = _instrument_density_epistemics(vs)
        assert source_type == "metadata_proxy"
        assert validation == "heuristic"
        assert warnings

    def test_gpr_table_instrument_slice_labels_external_acoustic_metadata(self):
        vs = legacy_input_to_vertical_slice(_symbolic_input(["G4"], instruments=["flauta"]))
        source_type, validation, assumptions, _ = _instrument_density_epistemics(vs)
        assert source_type == "external_acoustic_metadata"
        assert validation in ("partially_calibrated", "heuristic")
        assert any("does not analyse audio" in a.lower() for a in assumptions)

    def test_unknown_profile_audit_status_is_symbolic_default_not_empirical(self):
        audited = audit_instrument_profile(profile_for_event("__missing_instrument_xyz__"))
        assert audited["profile_status"] == "symbolic_default"
        assert audited["profile_status"] != "empirical_profile"
        assert audited["claims_empirical_without_notes"] is False

    def test_unknown_profile_source_notes_admit_generic_proxy(self):
        profile = profile_for_event("__missing_instrument_xyz__")
        assert "proxy" in profile.source_notes.lower() or "unregistered" in profile.source_notes.lower()
        assert profile.missing_data_warnings

    def test_calculate_metrics_instrument_density_metadata_has_source_type(self):
        resultados, _, _ = dp_calculate_metrics(_symbolic_input(["C4"], instruments=["violin"]))
        inst_meta = resultados["metric_metadata"]["metrics"]["density.instrument"]
        assert inst_meta["source_type"] in ("metadata_proxy", "external_acoustic_metadata")
        assert inst_meta["validation_status"] in ("heuristic", "partially_calibrated")


class TestScoreBasedBoundary:
    def test_event_count_matches_notated_inputs_only(self):
        resultados, _, _ = dp_calculate_metrics(
            _symbolic_input(["C4", "E4", "G4"], instruments=["flauta", "violin", "unknown_xyz"])
        )
        assert resultados["pitch_aggregation"]["event_count"] == 3

    def test_no_extra_pitches_beyond_notated_score_events(self):
        resultados, _, _ = dp_calculate_metrics(_symbolic_input(["C4"], instruments=["flauta"]))
        assert resultados["pitch_aggregation"]["distinct_pitch_count"] == 1

    def test_proc_audio_entry_point_absent_in_repository(self):
        assert not (REPO_ROOT / "proc_audio.py").exists()

    def test_instrument_lookup_does_not_read_audio_files(self):
        mod = get_instrument_module("flauta")
        with mock.patch("builtins.open", side_effect=AssertionError("audio file open attempted")):
            density = mod.calcular_densidade("C4", "mf")
        assert math.isfinite(density)

    def test_metric_metadata_declares_score_only_mode(self):
        resultados, _, _ = dp_calculate_metrics(_symbolic_input(["C4"]))
        meta = resultados["metric_metadata"]
        assert meta.get("score_only_mode") is True


class TestDeterminismScaffold:
    def test_synthetic_lookup_idempotent(self):
        logger = logging.getLogger("test.scaffold.determinism")
        table = {"C4": {"mf": 10.0}, "G4": {"mf": 9.0}}
        first = lookup_spectral_density(table, "D4", "mf", logger=logger)
        second = lookup_spectral_density(table, "D4", "mf", logger=logger)
        assert first == pytest.approx(second)

    def test_unknown_coarse_density_idempotent(self):
        mod = get_instrument_module("unknown_repeat_test_inst")
        a = mod.calcular_densidade("F4", "f")
        b = mod.calcular_densidade("F4", "f")
        assert a == pytest.approx(b)

    def test_empty_table_fallback_stable(self):
        logger = logging.getLogger("test.scaffold.empty_stable")
        values = [
            lookup_spectral_density({}, "A4", "mf", logger=logger),
            lookup_spectral_density({}, "B4", "ff", logger=logger),
        ]
        assert values[0] == pytest.approx(5.0)
        assert values[1] == pytest.approx(5.0)


class TestQtyPlayerCountSemantics:
    def test_one_player_density_independent_of_event_player_count(self):
        event_qty1 = make_instrument_event(
            idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=1
        )
        event_qty8 = make_instrument_event(
            idx=0, note="C4", dynamic="mf", instrument_name="flauta", player_count=8
        )
        d1 = compute_event_one_player_density(event_qty1, load_instrument_module)
        d8 = compute_event_one_player_density(event_qty8, load_instrument_module)
        assert d1 == pytest.approx(d8)

    def test_slice_pressure_scales_with_qty_via_rss_not_at_lookup(self):
        base_density = 10.0
        pressure_one, mass_one, _ = compute_slice_orchestral_metrics(
            ["C4"], ["mf"], ["flauta"], [1], [base_density]
        )
        pressure_four, mass_four, _ = compute_slice_orchestral_metrics(
            ["C4"], ["mf"], ["flauta"], [4], [base_density]
        )
        assert pressure_one == pytest.approx(base_density)
        assert pressure_four == pytest.approx(base_density * 2.0)
        assert mass_four == pytest.approx(mass_one * 4.0)

    def test_high_qty_does_not_increase_pitch_polyphony_count(self):
        resultados, _, _ = dp_calculate_metrics(
            _symbolic_input(["C4"], instruments=["flauta"], nums=[8])
        )
        assert resultados["pitch_aggregation"]["event_count"] == 1
        assert resultados["pitch_aggregation"]["distinct_pitch_count"] == 1
        assert resultados["pitch_aggregation"]["total_player_count"] == 8


class TestMalformedTableHandling:
    def test_unparseable_table_keys_do_not_crash_lookup(self):
        table = {
            "not_a_valid_note!!!": {"mf": 99.0},
            "C4": {"mf": 10.0},
            "G4": {"mf": 8.0},
        }
        entries = _sorted_table_entries(table)
        assert len(entries) >= 2
        logger = logging.getLogger("test.scaffold.malformed_keys")
        value = lookup_spectral_density(table, "E4", "mf", logger=logger)
        assert math.isfinite(value)

    def test_missing_dynamic_row_falls_back_to_mf_or_mean(self):
        logger = logging.getLogger("test.scaffold.missing_dyn")
        table = {"C4": {"mf": 6.5}}
        value = lookup_spectral_density(table, "C4", "ppp", logger=logger)
        assert value == pytest.approx(6.5)

    def test_single_entry_table_returns_finite_value(self):
        logger = logging.getLogger("test.scaffold.single_entry")
        table = {"D4": {"pp": 4.0, "mf": 6.0, "ff": 8.0}}
        value = lookup_spectral_density(table, "D4", "mf", logger=logger)
        assert value == pytest.approx(6.0)

    def test_registry_listing_does_not_require_complete_acoustic_tables(self):
        audit = build_instrument_metadata_audit()
        coarse_count = sum(
            1
            for p in audit["profiles"]
            if p["registry_profile_status"] in ("coarse_default", "symbolic_default")
            or p["profile_status"] == "symbolic_default"
        )
        assert coarse_count > 0
        assert audit["instrument_count"] == len(audit["profiles"])
