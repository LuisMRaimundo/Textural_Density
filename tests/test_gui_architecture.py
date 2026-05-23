"""
GUI architecture boundary tests.

Ensures the GUI layer routes analysis exclusively through:
  GUI input → adapter → AnalysisRequest → core.pipeline.calculate_metrics
"""

from __future__ import annotations

import ast
import math
from pathlib import Path

import pytest

from adapters.gui_adapter import build_analysis_request, calculate_from_gui_request
from gui.controllers.analysis_controller import AnalysisController

ROOT = Path(__file__).resolve().parents[1]
GUI_ROOT = ROOT / "gui"
ADAPTER_PATH = ROOT / "adapters" / "gui_adapter.py"
MAIN_PATH = ROOT / "Main.py"

_REMOVED_KEYS = (
    "calculate_combination_tones",
    "combination_tones",
    "use_psychoacoustic",
    "use_stevens",
)


def _iter_python_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.rglob("*.py") if p.is_file())


def _file_imports_module(path: Path, module_prefix: str) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == module_prefix or alias.name.startswith(f"{module_prefix}."):
                    hits.append(alias.name)
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == module_prefix or node.module.startswith(f"{module_prefix}."):
                hits.append(node.module)
    return hits


def _file_references_name(path: Path, name: str) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == name:
                    return True
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == name:
                    return True
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == name:
                return True
            if isinstance(func, ast.Attribute) and func.attr == name:
                return True
    return False


class TestGuiNoLegacyImports:
    @pytest.mark.parametrize("path", _iter_python_files(GUI_ROOT), ids=lambda p: p.relative_to(ROOT).as_posix())
    def test_gui_modules_do_not_import_data_processor(self, path: Path):
        assert _file_imports_module(path, "data_processor") == []

    def test_main_does_not_import_data_processor(self):
        assert _file_imports_module(MAIN_PATH, "data_processor") == []


class TestCalculateMetricsBoundary:
    def test_only_adapter_imports_calculate_metrics_for_gui_path(self):
        gui_hits = [
            p.relative_to(ROOT).as_posix()
            for p in _iter_python_files(GUI_ROOT)
            if _file_imports_module(p, "core") and _file_references_name(p, "calculate_metrics")
        ]
        assert gui_hits == []

    def test_adapter_is_single_calculate_metrics_gateway(self):
        assert _file_imports_module(ADAPTER_PATH, "core")
        tree = ast.parse(ADAPTER_PATH.read_text(encoding="utf-8-sig"))
        calculate_imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == "core"
            and any(a.name == "calculate_metrics" for a in node.names)
        ]
        assert len(calculate_imports) == 1

    def test_controller_delegates_to_adapter_not_core_pipeline(self):
        controller = GUI_ROOT / "controllers" / "analysis_controller.py"
        assert not _file_references_name(controller, "calculate_metrics")
        assert _file_imports_module(controller, "adapters")

    def test_main_uses_analysis_controller_only(self):
        text = MAIN_PATH.read_text(encoding="utf-8-sig")
        assert "AnalysisController.analyze" in text
        assert "calculate_metrics" not in text
        assert "data_processor" not in text


class TestAnalysisRequestValidation:
    def test_build_request_uses_from_mapping(self):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["Flauta"],
            "num_instruments": [3],
        }
        request = build_analysis_request(raw)
        assert request.num_instruments == (3,)

    @pytest.mark.parametrize("key", _REMOVED_KEYS)
    def test_removed_keys_stripped_before_core(self, key: str):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
            key: True,
        }
        request = build_analysis_request(raw)
        pipeline = request.to_pipeline_dict()
        assert key not in pipeline
        resultados, _, _ = calculate_from_gui_request(raw)
        assert "density" in resultados

    def test_unknown_keys_stripped_before_from_mapping(self):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
            "bogus_key": 1,
        }
        request = build_analysis_request(raw)
        pipeline = request.to_pipeline_dict()
        assert "bogus_key" not in pipeline
        assert set(pipeline.keys()) <= {
            "notes",
            "dynamics",
            "instruments",
            "num_instruments",
            "weight_factor",
            "onsets",
            "offsets",
            "durations",
            "part_ids",
        }

    def test_invalid_qty_rejected(self):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [0],
        }
        with pytest.raises(ValueError, match="quantity must be >= 1"):
            build_analysis_request(raw)


class TestGuiQtySemanticsMatchCore:
    def _gui_raw(self, notes: list[str], qty: list[int]) -> dict:
        return {
            "notes": notes,
            "dynamics": ["mf"] * len(notes),
            "instruments": ["Flauta"] * len(notes),
            "num_instruments": qty,
            "weight_factor": 0.5,
        }

    def test_qty_ten_player_count_and_mass(self):
        resultados, _, _ = calculate_from_gui_request(self._gui_raw(["C4"], [10]))
        agg = resultados["pitch_aggregation"]
        assert agg["player_count"] == 10
        assert agg["pitch_polyphony"] == 1
        assert agg["distinct_pitch_count"] == 1

    def test_row_splitting_equivalence_via_gui_adapter(self):
        one_row, _, _ = calculate_from_gui_request(self._gui_raw(["C4"], [4]))
        four_rows, _, _ = calculate_from_gui_request(
            self._gui_raw(["C4", "C4", "C4", "C4"], [1, 1, 1, 1])
        )
        assert one_row["density"]["sonic_mass"] == pytest.approx(
            four_rows["density"]["sonic_mass"], rel=1e-6
        )
        assert one_row["density"]["instrument"] == pytest.approx(
            four_rows["density"]["instrument"], rel=1e-6
        )

    def test_no_qty_three_halves_via_gui_path(self):
        one, _, _ = calculate_from_gui_request(self._gui_raw(["C4"], [1]))
        ten, _, _ = calculate_from_gui_request(self._gui_raw(["C4"], [10]))
        b_mass = float(one["density"]["sonic_mass"])
        t_mass = float(ten["density"]["sonic_mass"])
        b_inst = float(one["density"]["instrument"])
        t_inst = float(ten["density"]["instrument"])
        if b_mass > 0 and b_inst > 0:
            assert t_mass / b_mass == pytest.approx(10.0, rel=0.02)
            assert t_inst / b_inst == pytest.approx(math.sqrt(10), rel=0.02)
            assert t_mass / b_mass != pytest.approx(math.pow(10, 1.5), rel=0.05)

    def test_controller_matches_adapter(self):
        raw = self._gui_raw(["C4", "E4"], [2, 1])
        r_adapter, d_adapter, p_adapter = calculate_from_gui_request(raw)
        r_ctrl, d_ctrl, p_ctrl = AnalysisController.analyze(raw)
        assert r_ctrl["density"]["sonic_mass"] == pytest.approx(
            r_adapter["density"]["sonic_mass"]
        )
        assert d_ctrl == pytest.approx(d_adapter)
        assert p_ctrl == pytest.approx(p_adapter)


class TestResultFormattingPath:
    def test_controller_format_uses_core_formatting(self):
        raw = {
            "notes": ["C4"],
            "dynamics": ["mf"],
            "instruments": ["flauta"],
            "num_instruments": [1],
        }
        resultados, _, _ = AnalysisController.analyze(raw)
        text = AnalysisController.format_results(resultados)
        assert "Player Count" in text or "player_count" in resultados.get("pitch_aggregation", {})
        assert "Pitch Polyphony" in text or "pitch_polyphony" in str(
            resultados.get("pitch_aggregation", {})
        )
