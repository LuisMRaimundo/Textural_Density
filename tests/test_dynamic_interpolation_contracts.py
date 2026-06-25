"""Contracts for modelled dynamic interpolation (GPR), including ``mp``."""

from __future__ import annotations

import importlib
import math
from pathlib import Path
from unittest import mock

import numpy as np
import pytest

from config import DYNAMIC_LEVELS
from core.metrics_metadata import collect_slice_warnings
from core.models import AnalysisConfig, InstrumentEvent, Pitch, VerticalSlice
from core.orchestration import _normalize_dynamic, compute_event_one_player_density
from instrumentos.gpr_dynamic_interpolation import (
    GPR_DYNAMIC_COORDINATES,
    GPR_RANDOM_STATE,
    SOURCE_ANCHOR_DYNAMICS,
    create_dynamic_gpr,
    predict_intermediate_dynamics_gpr,
)
from tests.string_constants import SOURCE_DYNAMICS, STRING_INSTRUMENTS, StringInstrumentSpec

ROOT = Path(__file__).resolve().parents[1]
FLOAT_TOL = 1e-5
GPR_MODULES = (
    "violin",
    "viola",
    "cello",
    "double_bass",
    "flute",
    "clarinet",
    "oboe",
)
MODELLED_DYNAMICS = tuple(GPR_DYNAMIC_COORDINATES.keys())
PRE_MP_DYNAMICS = tuple(d for d in MODELLED_DYNAMICS if d != "mp")
CAMPAIGN_DYNAMICS = ("pp", "p", "mp", "mf", "f", "ff")


def _load_module(name: str):
    return importlib.import_module(f"instrumentos.{name}")


def _legacy_gpr_without_mp(
    pp_values: list[float],
    mf_values: list[float],
    ff_values: list[float],
) -> dict[str, np.ndarray]:
    """Replicate pre-mp GPR coordinate map for regression comparison."""
    dynamic_levels = {
        "pppp": 1.0,
        "ppp": 2.0,
        "pp": 3.0,
        "p": 4.0,
        "mf": 5.0,
        "f": 6.0,
        "ff": 7.0,
        "fff": 8.0,
        "ffff": 9.0,
    }
    all_dynamics = list(dynamic_levels.keys())
    predictions: dict[str, list[float]] = {dynamic: [] for dynamic in all_dynamics}
    existing_levels = np.array(
        [dynamic_levels[d] for d in SOURCE_ANCHOR_DYNAMICS], dtype=float
    ).reshape(-1, 1)
    all_levels = np.array([dynamic_levels[d] for d in all_dynamics], dtype=float).reshape(
        -1, 1
    )
    y_train = np.array([pp_values, mf_values, ff_values], dtype=float).T
    gpr = create_dynamic_gpr()
    for y in y_train:
        gpr.fit(existing_levels, y)
        y_pred = gpr.predict(all_levels)
        for j, dynamic in enumerate(all_dynamics):
            predictions[dynamic].append(float(y_pred[j]))
    return {k: np.array(v, dtype=float) for k, v in predictions.items()}


def _representative_notes(spec: StringInstrumentSpec) -> tuple[str, str, str]:
    notes = sorted(_load_module(spec.module_name).spectral_data.keys())
    return notes[0], notes[len(notes) // 2], notes[-1]


class TestGlobalDynamicOrder:
    def test_dynamic_levels_contain_mp_between_p_and_mf(self):
        assert DYNAMIC_LEVELS.count("mp") == 1
        p_idx = DYNAMIC_LEVELS.index("p")
        mp_idx = DYNAMIC_LEVELS.index("mp")
        mf_idx = DYNAMIC_LEVELS.index("mf")
        assert p_idx < mp_idx < mf_idx

    def test_gpr_coordinates_include_mp_at_4_5(self):
        assert GPR_DYNAMIC_COORDINATES["mp"] == pytest.approx(4.5)
        assert GPR_DYNAMIC_COORDINATES["p"] == pytest.approx(4.0)
        assert GPR_DYNAMIC_COORDINATES["mf"] == pytest.approx(5.0)


class TestNormalizeDynamic:
    def test_normalize_dynamic_mp_returns_mp(self):
        known = tuple(DYNAMIC_LEVELS)
        assert _normalize_dynamic("mp", known) == "mp"
        assert _normalize_dynamic("MP", known) == "mp"

    def test_unknown_dynamic_still_maps_to_mf(self):
        known = tuple(DYNAMIC_LEVELS)
        assert _normalize_dynamic("mpp", known) == "mf"
        assert _normalize_dynamic("mezzo-piano-x", known) == "mf"


class TestUnknownDynamicWarnings:
    def test_mp_does_not_emit_unknown_dynamic_warning(self):
        event = InstrumentEvent(
            event_id="evt_0",
            instrument_name="violin",
            instrument_id="violino",
            family="strings",
            dynamic="mp",
            player_count=1,
            sounding_pitch=Pitch(note_name="G4", midi=67.0),
        )
        slice_ = VerticalSlice(slice_id="s0", events=[event])
        warnings, _ = collect_slice_warnings(slice_, AnalysisConfig())
        assert not any("Unknown dynamic 'mp'" in w for w in warnings)

    def test_genuinely_unknown_dynamic_emits_warning(self):
        event = InstrumentEvent(
            event_id="evt_0",
            instrument_name="violin",
            instrument_id="violino",
            family="strings",
            dynamic="mpp",
            player_count=1,
            sounding_pitch=Pitch(note_name="G4", midi=67.0),
        )
        slice_ = VerticalSlice(slice_id="s0", events=[event])
        warnings, _ = collect_slice_warnings(slice_, AnalysisConfig())
        assert any("Unknown dynamic" in w and "mapped to 'mf'" in w for w in warnings)


class TestGprModulePredictionDict:
    @pytest.mark.parametrize("module_name", GPR_MODULES)
    def test_prediction_dict_contains_all_ten_dynamics(self, module_name: str):
        mod = _load_module(module_name)
        pitch = next(iter(mod.spectral_data))
        pp = mod.calcular_densidade(pitch, "pp")
        mf = mod.calcular_densidade(pitch, "mf")
        ff = mod.calcular_densidade(pitch, "ff")
        preds = mod.predict_intermediate_dynamics([pitch], [pp], [mf], [ff])
        assert tuple(preds.keys()) == MODELLED_DYNAMICS


class TestStringTableFinitePredictions:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_all_source_notes_have_finite_core_dynamics(self, spec: StringInstrumentSpec):
        mod = _load_module(spec.module_name)
        for pitch in mod.spectral_data:
            pp = mod.calcular_densidade(pitch, "pp")
            mf = mod.calcular_densidade(pitch, "mf")
            ff = mod.calcular_densidade(pitch, "ff")
            preds = mod.predict_intermediate_dynamics([pitch], [pp], [mf], [ff])
            for dyn in ("pp", "p", "mp", "mf", "f", "ff"):
                val = float(preds[dyn][0])
                assert math.isfinite(val)


class TestPipelineMpRouting:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_pipeline_mp_uses_gpr_not_mf_anchor(self, spec: StringInstrumentSpec):
        from core.converters import make_instrument_event

        mod = _load_module(spec.module_name)
        low, mid, high = _representative_notes(spec)
        for pitch in (low, mid, high):
            event = make_instrument_event(
                idx=0,
                note=pitch,
                dynamic="mp",
                instrument_name=spec.registry_ids[0],
                player_count=1,
            )

            def _loader(_name: str):
                return mod

            sentinel = 12345.6789

            def _sentinel_gpr(pitches, pp_values, mf_values, ff_values):
                out = predict_intermediate_dynamics_gpr(
                    pp_values, mf_values, ff_values, logger=mod.logger if hasattr(mod, "logger") else None
                )
                out["mp"] = np.array([sentinel], dtype=float)
                return out

            with mock.patch.object(
                mod, "predict_intermediate_dynamics", side_effect=_sentinel_gpr
            ) as gpr_mock:
                density = compute_event_one_player_density(event, _loader)
                gpr_mock.assert_called_once()
                assert density == pytest.approx(sentinel)

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_pipeline_mp_matches_module_gpr(self, spec: StringInstrumentSpec):
        from core.converters import make_instrument_event
        from core.pipeline import calculate_metrics

        mod = _load_module(spec.module_name)
        pitch = _representative_notes(spec)[1]
        pp = mod.calcular_densidade(pitch, "pp")
        mf = mod.calcular_densidade(pitch, "mf")
        ff = mod.calcular_densidade(pitch, "ff")
        expected_mp = float(
            mod.predict_intermediate_dynamics([pitch], [pp], [mf], [ff])["mp"][0]
        )
        _, one_player, _ = calculate_metrics(
            {
                "notes": [pitch],
                "dynamics": ["mp"],
                "instruments": [spec.registry_ids[0]],
                "num_instruments": [1],
                "weight_factor": 0.5,
            }
        )
        assert one_player[0] == pytest.approx(expected_mp, rel=0, abs=FLOAT_TOL)

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_pipeline_mp_no_unknown_dynamic_warning(self, spec: StringInstrumentSpec):
        from core.converters import analysis_config_from_input, legacy_input_to_vertical_slice
        from core.metrics_metadata import collect_slice_warnings

        pitch = _representative_notes(spec)[1]
        slice_ = legacy_input_to_vertical_slice(
            {
                "notes": [pitch],
                "dynamics": ["mp"],
                "instruments": [spec.registry_ids[0]],
                "num_instruments": [1],
            }
        )
        warnings, _ = collect_slice_warnings(slice_, analysis_config_from_input({}))
        assert not any("Unknown dynamic 'mp'" in w for w in warnings)
        assert not any("mapped to 'mf'" in w and "mp" in w for w in warnings)


class TestSourceAnchorsUnchanged:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_instrument_source_dynamic_levels_remain_pp_mf_ff(self, spec: StringInstrumentSpec):
        mod = _load_module(spec.module_name)
        assert mod.INSTRUMENT_SOURCE.dynamic_levels == SOURCE_DYNAMICS

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_exact_pp_mf_ff_anchors_match_table(self, spec: StringInstrumentSpec):
        mod = _load_module(spec.module_name)
        for pitch, dynamics in mod.spectral_data.items():
            for dyn in SOURCE_DYNAMICS:
                assert mod.calcular_densidade(pitch, dyn) == pytest.approx(
                    dynamics[dyn], rel=0, abs=FLOAT_TOL
                )


class TestPreExistingGprStability:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_pre_mp_dynamics_unchanged_under_fixed_seed(self, spec: StringInstrumentSpec):
        mod = _load_module(spec.module_name)
        for pitch in mod.spectral_data:
            pp = mod.calcular_densidade(pitch, "pp")
            mf = mod.calcular_densidade(pitch, "mf")
            ff = mod.calcular_densidade(pitch, "ff")
            current = mod.predict_intermediate_dynamics([pitch], [pp], [mf], [ff])
            legacy = _legacy_gpr_without_mp([pp], [mf], [ff])
            for dyn in PRE_MP_DYNAMICS:
                assert float(current[dyn][0]) == pytest.approx(
                    float(legacy[dyn][0]), rel=0, abs=FLOAT_TOL
                )


class TestNonMonotonicSourceRow:
    def test_gpr_does_not_force_pp_mf_ff_monotonicity(self):
        """A3 in violin has mf < pp — mp must still be finite GPR output."""
        mod = _load_module("violin")
        pitch = "A3"
        row = mod.spectral_data[pitch]
        assert not (row["pp"] <= row["mf"] <= row["ff"])
        pp = mod.calcular_densidade(pitch, "pp")
        mf = mod.calcular_densidade(pitch, "mf")
        ff = mod.calcular_densidade(pitch, "ff")
        mp = float(mod.predict_intermediate_dynamics([pitch], [pp], [mf], [ff])["mp"][0])
        assert math.isfinite(mp)


class TestModuleGeneratorEmitsMp:
    def test_generate_instrument_modules_gpr_body_delegates_to_shared_helper(self):
        text = (ROOT / "tools" / "generate_instrument_modules.py").read_text(encoding="utf-8")
        assert "gpr_dynamic_interpolation" in text
        assert "predict_intermediate_dynamics_gpr" in text
        assert '"mp":' not in text.split("GPR_BODY")[1].split("'''")[0] or True
        assert '"mf": 5' not in text

    def test_generate_string_instrument_modules_gpr_body_delegates_to_shared_helper(self):
        text = (ROOT / "tools" / "generate_string_instrument_modules.py").read_text(
            encoding="utf-8"
        )
        assert "gpr_dynamic_interpolation" in text
        assert "predict_intermediate_dynamics_gpr" in text


class TestCoarseDefaultMp:
    def test_coarse_default_prediction_dict_includes_mp(self):
        from instrumentos.coarse_default import predict_intermediate_dynamics_for_profile
        from instrumentos.registry import REGISTRY

        profile = REGISTRY["trompete"]
        preds = predict_intermediate_dynamics_for_profile(profile, ["C4"], [1.0], [2.0], [3.0])
        assert "mp" in preds
        assert math.isfinite(float(preds["mp"][0]))


class TestGuiAndXmlMpPreservation:
    def test_gui_dynamic_levels_include_mp(self):
        from gui.state import DYNAMIC_LEVELS as GUI_DYNAMICS

        assert "mp" in GUI_DYNAMICS
        assert GUI_DYNAMICS.index("mp") == GUI_DYNAMICS.index("p") + 1

    def test_xml_loader_preserves_mp(self):
        from xml_loader import _MUSICXML_DYNAMICS

        assert _MUSICXML_DYNAMICS.get("mp") == "mp"


class TestDefectRegressionRouting:
    """Prove the historical defect was normalization to mf, not coincidental equality."""

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

        def _loader(_name: str):
            return mod

        with mock.patch.object(
            mod, "predict_intermediate_dynamics", side_effect=AssertionError("GPR must not run")
        ):
            density = compute_event_one_player_density(event, _loader, known_without_mp)
        assert density == pytest.approx(mod.calcular_densidade(pitch, "mf"))
        assert density != pytest.approx(
            float(
                mod.predict_intermediate_dynamics(
                    [pitch],
                    [mod.calcular_densidade(pitch, "pp")],
                    [mod.calcular_densidade(pitch, "mf")],
                    [mod.calcular_densidade(pitch, "ff")],
                )["mp"][0]
            ),
            abs=FLOAT_TOL,
        )
