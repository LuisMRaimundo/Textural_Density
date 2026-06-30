"""
Main Tkinter view: composes input/results/report panels and action bar.

Presentation only — analysis runs via AnalysisController in Main or tests.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Mapping

from core.request import AnalysisRequest
from core.version import PRODUCT_DISPLAY_NAME
from gui.analysis_adapter import build_analysis_request
from gui.types import GuiAnalysisInput
from gui.widgets.action_bar import ActionBar
from gui.widgets.input_panel import InputPanel
from gui.widgets.report_panel import ReportPanel
from gui.widgets.results_panel import ResultsPanel


class DensityCalculatorGUI:
    """Integrated density calculator view (controller + panel composition)."""

    def __init__(self, root: tk.Misc, callbacks: Mapping[str, Callable[..., Any]]) -> None:
        self.root = root
        self.root.title(PRODUCT_DISPLAY_NAME)
        self.callbacks = callbacks

        ActionBar(root, callbacks)

        self._main_content = tk.Frame(root)
        self._main_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(self._main_content)
        scroll_y = tk.Scrollbar(self._main_content, orient="vertical", command=canvas.yview)
        scroll_host = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scroll_host, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_host.bind(
            "<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self.input_panel = InputPanel(scroll_host, on_row_toggle=self.toggle_state)
        self.input_panel.input_frame.pack(fill="both", expand=True)

        self.results_panel = ResultsPanel(
            self._main_content,
            on_run_validation=lambda: self.callbacks["execute_validation"](),
        )
        self.report_panel = ReportPanel(root)

        # Backward-compatible attribute aliases used by legacy callers/tests
        self._bind_legacy_attributes()

    def _bind_legacy_attributes(self) -> None:
        ip = self.input_panel
        rp = self.results_panel
        self.weight_factor_slider = ip.weight_factor_slider
        self.note_vars = ip.note_vars
        self.octave_vars = ip.octave_vars
        self.cents_vars = ip.cents_vars
        self.dynamic_vars = ip.dynamic_vars
        self.instrument_vars = ip.instrument_vars
        self.num_instruments_vars = ip.num_instruments_vars
        self.state_vars = ip.state_vars
        self.note_menus = ip.note_menus
        self.octave_menus = ip.octave_menus
        self.cents_menus = ip.cents_menus
        self.dynamic_menus = ip.dynamic_menus
        self.instrument_menus = ip.instrument_menus
        self.num_instruments_menus = ip.num_instruments_menus
        self.var_save_results = ip.var_save_results
        self.var_show_graphs = ip.var_show_graphs
        self.input_frame = ip.input_frame
        self.result_text = rp.result_text
        self.tree = rp.tree
        self.validation_text = rp.validation_text
        self.embedded_graphs_frame = rp.embedded_graphs_frame
        self.notebook = rp.notebook

    def get_input_data(self) -> GuiAnalysisInput:
        """Collect GUI input including save_results / show_graphs flags."""
        return self.input_panel.collect_raw_input()

    def get_analysis_request(self) -> AnalysisRequest:
        """Typed analytical boundary (GUI-only keys stripped)."""
        return build_analysis_request(dict(self.get_input_data()))

    def get_input_notes(self) -> list[str]:
        return list(self.get_input_data().get("notes", []))

    def show_error(self, message: str) -> None:
        messagebox.showerror("Error", message)

    def toggle_state(self, index: int) -> None:
        self.input_panel.toggle_row(index)

    def clear_inputs(self) -> None:
        self.input_panel.clear()
        self.results_panel.clear_all_outputs()

    def load_from_xml_data(self, data: dict[str, Any]) -> None:
        self.input_panel.load_from_data(data)

    def show_results(self, result_text: str) -> None:
        self.results_panel.show_results(result_text)

    def show_validation_results(self, validation_text: str) -> None:
        self.results_panel.show_validation_results(validation_text)

    def update_metrics_tree(self, results: dict[str, Any]) -> None:
        self.results_panel.update_metrics_tree(results)

    def create_embedded_graphs(self, pitches: list[float], densities: list[float]) -> None:
        self.results_panel.create_embedded_graphs(pitches, densities)

    def show_report_config_dialog(self, on_generate: Callable[[dict[str, Any]], None]) -> None:
        self.report_panel.show_report_config_dialog(on_generate)
