"""Contracts for committed dynamic ladders (runtime GPR removed)."""

from __future__ import annotations

import importlib
from unittest import mock

import pytest

from config import DYNAMIC_LEVELS
from core.metrics_metadata import collect_slice_warnings
from core.models import AnalysisConfig
from core.orchestration import _normalize_dynamic, compute_event_one_player_density
from instrumentos.pitch_interpolation import MissingCommittedDynamicError
from tests.string_constants import STRING_INSTRUMENTS, StringInstrumentSpec

FLOAT_TOL = 1e-5


def _load_module(name: str):
    return importlib.import_module(f"instrumentos.{name}")


class TestGlobalDynamicOrder:
    def test_dynamic_levels_contain_mp_between_p_and_mf(self):
        assert DYNAMIC_LEVELS.count("mp") == 1
        p_idx = DYNAMIC_LEVELS.index("p")
        mp_idx = DYNAMIC_LEVELS.index("mp")
        mf_idx = DYNAMIC_LEVELS.index("mf")
        assert p_idx < mp_idx < mf_idx


class TestNormalizeDynamic:
    def test_normalize_dynamic_mp_returns_mp(self):
        assert _normalize_dynamic("mp", tuple(DYNAMIC_LEVELS)) == "mp"

    def test_unknown_dynamic_still_maps_to_mf(self):
        assert _normalize_dynamic("xyz", tuple(DYNAMIC_LEVELS)) == "mf"


class TestUnknownDynamicWarnings:
    def test_mp_does_not_emit_unknown_dynamic_warning(self):
        from core.converters import analysis_config_from_input, legacy_input_to_vertical_slice

        slice_ = legacy_input_to_vertical_slice(
            {
                "notes": ["A3"],
                "dynamics": ["mp"],
                "instruments": ["violino"],
                "num_instruments": [1],
            }
        )
        warnings, _ = collect_slice_warnings(slice_, analysis_config_from_input({}))
        assert not any("Unknown dynamic 'mp'" in w for w in warnings)

    def test_genuinely_unknown_dynamic_emits_warning(self):
        from core.converters import legacy_input_to_vertical_slice

        slice_ = legacy_input_to_vertical_slice(
            {
                "notes": ["A3"],
                "dynamics": ["xyzzy"],
                "instruments": ["violino"],
                "num_instruments": [1],
            }
        )
        warnings, _ = collect_slice_warnings(slice_, AnalysisConfig())
        assert any("Unknown dynamic" in w and "mapped to 'mf'" in w for w in warnings)


class TestCommittedLadderLookup:
    def test_violin_pipeline_uses_table_for_non_anchor_dynamics(self):
        from core.converters import make_instrument_event

        mod = _load_module("violin")
        pitch = "A3"
        for dyn in ("pppp", "p", "mp", "f", "ffff"):
            event = make_instrument_event(
                idx=0,
                note=pitch,
                dynamic=dyn,
                instrument_name="violino",
                player_count=1,
            )
            density = compute_event_one_player_density(event, lambda _: mod)
            assert density == pytest.approx(mod.spectral_data[pitch][dyn], abs=FLOAT_TOL)

    def test_missing_committed_dynamic_still_raises_on_sparse_row(self):
        # Production modules now commit full ladders; keep the error contract on
        # a synthetic sparse row (engine still refuses silent fill-in).
        from instrumentos.pitch_interpolation import _dynamic_value

        sparse = {"C4": {"pp": 1.0, "mf": 2.0, "ff": 3.0}}
        with pytest.raises(MissingCommittedDynamicError, match="not committed"):
            _dynamic_value(sparse, "C4", "mp")

    @pytest.mark.parametrize(
        "module_name,pitch",
        [
            ("violin", "A3"),
            ("viola", "C4"),
            ("cello", "C3"),
            ("double_bass", "A1"),
            ("flute", "C5"),
            ("clarinet", "C4"),
            ("bassoon", "C3"),
            ("oboe", "C5"),
            ("trumpet", "C4"),
        ],
    )
    def test_full_ladder_modules_lookup_mp(self, module_name: str, pitch: str):
        mod = _load_module(module_name)
        assert mod.INSTRUMENT_SOURCE.dynamic_levels == tuple(DYNAMIC_LEVELS)
        assert mod.calcular_densidade(pitch, "mp") == pytest.approx(
            mod.spectral_data[pitch]["mp"], abs=FLOAT_TOL
        )

    def test_modules_do_not_expose_runtime_gpr_helper(self):
        for name in ("violin", "flute", "viola", "cello", "clarinet", "bassoon", "oboe", "trumpet"):
            mod = _load_module(name)
            assert not hasattr(mod, "predict_intermediate_dynamics")


class TestPipelineMpRouting:
    def test_pipeline_mp_matches_violin_table(self):
        from core.pipeline import calculate_metrics

        mod = _load_module("violin")
        pitch = "A4"
        expected = float(mod.spectral_data[pitch]["mp"])
        _, one_player, _ = calculate_metrics(
            {
                "notes": [pitch],
                "dynamics": ["mp"],
                "instruments": ["violino"],
                "num_instruments": [1],
                "weight_factor": 0.5,
            }
        )
        assert one_player[0] == pytest.approx(expected, rel=0, abs=FLOAT_TOL)

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_anchor_dynamics_still_match_table(self, spec: StringInstrumentSpec):
        mod = _load_module(spec.module_name)
        for pitch, dynamics in mod.spectral_data.items():
            for dyn in ("pp", "mf", "ff"):
                assert mod.calcular_densidade(pitch, dyn) == pytest.approx(
                    dynamics[dyn], rel=0, abs=FLOAT_TOL
                )


class TestDefectRegressionRouting:
    def test_without_mp_in_known_dynamics_routes_to_mf_anchor(self):
        from core.converters import make_instrument_event

        mod = _load_module("violin")
        pitch = "G4"
        event = make_instrument_event(
            idx=0,
            note=pitch,
            dynamic="mp",
            instrument_name="violin",
            player_count=1,
        )
        known_without_mp = tuple(d for d in DYNAMIC_LEVELS if d != "mp")
        density = compute_event_one_player_density(
            event, lambda _: mod, known_without_mp
        )
        assert density == pytest.approx(mod.calcular_densidade(pitch, "mf"))
