"""
Phase 1: core/GUI separation tests.

Analytical modules must not import Tkinter at module load time.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest


CORE_MODULES = [
    "data_processor",
    "densidade_intervalar",
    "spectral_analysis",
    "microtonal",
    "timbre_texture_analysis",
    "score_io.exporters",
    "core.pipeline",
    "utils.notes",
    "utils.optimization",
    "utils.serialize_utils",
]


def _module_imports_tkinter(module_name: str) -> bool:
    mod = importlib.import_module(module_name)
    path = Path(mod.__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] == "tkinter" for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] == "tkinter":
                return True
    return False


class TestCoreImportsWithoutTkinter:
    @pytest.mark.parametrize("module_name", CORE_MODULES)
    def test_module_has_no_tkinter_import(self, module_name):
        assert not _module_imports_tkinter(module_name), (
            f"{module_name} must not import tkinter at module level"
        )


class TestCoreAPI:
    def test_core_calculate_metrics_import(self):
        from core import calculate_metrics, calcular_metricas

        assert calculate_metrics is calcular_metricas

    def test_core_runs_without_gui_import(self):
        from core.pipeline import calculate_metrics

        resultados, densidades, pitches = calculate_metrics(
            {
                "notes": ["C4", "E4", "G4"],
                "dynamics": ["mf", "mf", "mf"],
                "instruments": ["flauta", "flauta", "flauta"],
                "num_instruments": [1, 1, 1],
                "weight_factor": 0.5,
            }
        )
        assert "density" in resultados
        assert len(pitches) == 3
        assert len(densidades) == 3

    def test_pipeline_does_not_import_data_processor(self):
        import ast
        from pathlib import Path

        path = Path(__file__).resolve().parents[1] / "core" / "pipeline.py"
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] != "data_processor"
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] != "data_processor"

    def test_data_processor_shims_core_pipeline(self):
        import data_processor
        from core.pipeline import calculate_metrics as core_calculate_metrics

        assert data_processor.calculate_metrics is core_calculate_metrics
        assert data_processor.calcular_metricas is core_calculate_metrics

    def test_gui_adapter_does_not_import_data_processor(self):
        import ast
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        gui_py_files = sorted((root / "gui").rglob("*.py"))
        rel_paths = [str(p.relative_to(root)).replace("\\", "/") for p in gui_py_files]
        for rel in rel_paths:
            tree = ast.parse(root.joinpath(rel).read_text(encoding="utf-8-sig"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert alias.name.split(".")[0] != "data_processor", rel
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert node.module.split(".")[0] != "data_processor", rel

    def test_gui_controller_has_no_tkinter(self):
        assert not _module_imports_tkinter("gui.controllers.analysis_controller")

    def test_gui_state_has_no_tkinter(self):
        assert not _module_imports_tkinter("gui.state")

    def test_density_calculator_gui_composes_panels(self):
        from gui.app import DensityCalculatorGUI
        from gui.widgets import InputPanel, ResultsPanel

        assert DensityCalculatorGUI is not None
        assert InputPanel is not None
        assert ResultsPanel is not None

    def test_gui_types_exported(self):
        from gui import AnalysisResult, GuiAnalysisInput, SymbolicSliceInput, calculate_from_gui

        assert callable(calculate_from_gui)
        assert SymbolicSliceInput.__required_keys__ == frozenset(
            {"notes", "dynamics", "instruments", "num_instruments"}
        )
        assert GuiAnalysisInput is not None
        assert AnalysisResult is not None


class TestScoreIOExport:
    def test_write_results_json_roundtrip(self, tmp_path):
        from score_io.exporters import write_results_json

        payload = {"density": {"total": 1.0}, "input_data": {"notes": ["C4"]}}
        path = tmp_path / "out.json"
        written = write_results_json(payload, str(path))
        assert written == str(path)
        assert path.read_text(encoding="utf-8").strip().startswith("{")

    def test_write_results_json_raises_on_bad_path(self):
        from error_handler import FileOperationError
        from score_io.exporters import write_results_json

        with pytest.raises(FileOperationError):
            write_results_json({"a": 1}, "/invalid/path/no/file.json")
