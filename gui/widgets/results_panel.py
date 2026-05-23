"""Results notebook: text output, metrics tree, graphs, validation tab."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from utils.notes import midi_to_note_name


class ResultsPanel:
    def __init__(
        self,
        parent: tk.Misc,
        on_run_validation: Callable[[], None],
    ) -> None:
        self.result_text: tk.Text | None = None
        self.validation_text: tk.Text | None = None
        self.tree: ttk.Treeview | None = None
        self.embedded_graphs_frame: tk.Frame | None = None
        self.notebook: ttk.Notebook | None = None
        self._build_notebook(parent, on_run_validation)

    def _build_notebook(
        self, parent: tk.Misc, on_run_validation: Callable[[], None]
    ) -> None:
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True, pady=10)

        text_frame = tk.Frame(notebook)
        notebook.add(text_frame, text="Numerical Results")
        self.result_text = tk.Text(text_frame, height=15, width=60)
        self.result_text.pack(pady=10, padx=10, fill="both", expand=True)
        text_scrollbar = tk.Scrollbar(text_frame, command=self.result_text.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=text_scrollbar.set)

        self.embedded_graphs_frame = tk.Frame(notebook)
        notebook.add(self.embedded_graphs_frame, text="Quick Graphs")

        metrics_frame = tk.Frame(notebook)
        notebook.add(metrics_frame, text="Advanced Metrics")
        self.tree = ttk.Treeview(metrics_frame)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree["columns"] = ("valor",)
        self.tree.column("#0", width=250, minwidth=250)
        self.tree.column("valor", width=150, minwidth=150)
        self.tree.heading("#0", text="Metric")
        self.tree.heading("valor", text="Value")

        validation_frame = tk.Frame(notebook)
        notebook.add(validation_frame, text="Statistical Validation")
        tk.Label(
            validation_frame,
            text=(
                "This section validates the reliability of computed metrics "
                "using statistical methods."
            ),
        ).pack(pady=10)
        tk.Button(
            validation_frame,
            text="Run Statistical Validation",
            command=on_run_validation,
        ).pack(pady=5)
        self.validation_text = tk.Text(validation_frame, height=15, width=60)
        self.validation_text.pack(pady=10, padx=10, fill="both", expand=True)

        self.notebook = notebook

    def clear_graphs(self) -> None:
        if self.embedded_graphs_frame is not None:
            for widget in self.embedded_graphs_frame.winfo_children():
                widget.destroy()

    def clear_metrics_tree(self) -> None:
        if self.tree is not None:
            for item in self.tree.get_children():
                self.tree.delete(item)

    def clear_all_outputs(self) -> None:
        self.clear_metrics_tree()
        self.clear_graphs()

    def show_results(self, result_text: str) -> None:
        if self.result_text is None:
            return
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)

    def show_validation_results(self, validation_text: str) -> None:
        if self.validation_text is None:
            return
        self.validation_text.delete(1.0, tk.END)
        self.validation_text.insert(tk.END, validation_text)

    def update_metrics_tree(self, results: dict[str, Any]) -> None:
        if self.tree is None:
            return
        self.clear_metrics_tree()

        pitch_id = self.tree.insert("", "end", text="Pitch structure", open=True)
        orch_id = self.tree.insert("", "end", text="Orchestral mass", open=True)
        agg = results.get("pitch_aggregation") or {}
        dens = results["density"]
        if agg:
            self.tree.insert(pitch_id, "end", text="Event count", values=(str(agg.get("event_count", "")),))
            self.tree.insert(
                pitch_id,
                "end",
                text="Player count (Qty sum)",
                values=(str(agg.get("player_count", agg.get("total_player_count", ""))),),
            )
            self.tree.insert(
                pitch_id,
                "end",
                text="Distinct pitch count",
                values=(str(agg.get("distinct_pitch_count", "")),),
            )
            self.tree.insert(
                pitch_id,
                "end",
                text="Pitch polyphony",
                values=(str(agg.get("pitch_polyphony", agg.get("distinct_pitch_count", ""))),),
            )
            self.tree.insert(
                pitch_id,
                "end",
                text="Event doubling count",
                values=(str(agg.get("event_doubling_count", agg.get("doubling_count", ""))),),
            )
            self.tree.insert(
                pitch_id,
                "end",
                text="Player doubling count",
                values=(str(agg.get("player_doubling_count", "")),),
            )
        for key, label in (
            ("interval", "Interval compactness (distinct)"),
            ("pitch_structure", "Pitch-structure density"),
            ("total", "Composite vertical density"),
        ):
            val = dens.get(key) if key != "pitch_structure" else dens.get("pitch_structure", dens.get("refined"))
            if isinstance(val, (int, float)) and np.isfinite(val):
                self.tree.insert(pitch_id, "end", text=label, values=(f"{max(0.0, float(val)):.4f}",))
        for key, label in (
            ("sonic_mass", "Sonic / orchestral mass (linear Qty)"),
            ("instrument", "Instrument density (pressure-equiv RSS)"),
            ("weighted_orchestral", "Weighted orchestral component"),
            ("weighted_pitch", "Weighted pitch component"),
        ):
            val = dens.get(key)
            if val is None and key == "weighted_orchestral":
                val = dens.get("weighted")
            if isinstance(val, (int, float)) and np.isfinite(val):
                self.tree.insert(orch_id, "end", text=label, values=(f"{max(0.0, float(val)):.4f}",))

        moments_id = self.tree.insert("", "end", text="Spectral Moments", open=True)
        additional_id = self.tree.insert("", "end", text="Additional Metrics", open=True)
        texture_id = self.tree.insert("", "end", text="Texture", open=True)
        timbre_id = self.tree.insert("", "end", text="Timbre", open=True)
        orchestration_id = self.tree.insert("", "end", text="Orchestration", open=True)

        for k, v in results["spectral_moments"].items():
            if k == "centroid":
                self.tree.insert(
                    moments_id,
                    "end",
                    text="Centroid",
                    values=(f"{v['frequency']:.2f} Hz ({v['note']})",),
                )
            elif k == "spread":
                self.tree.insert(
                    moments_id,
                    "end",
                    text="Spread",
                    values=(f"±{v['deviation']:.2f} Hz",),
                )
            elif isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):
                display = max(0.0, float(v))
                self.tree.insert(
                    moments_id,
                    "end",
                    text=k.replace("spectral_", "").capitalize(),
                    values=(f"{display:.4f}",),
                )

        for k, v in results["additional_metrics"].items():
            if k != "chroma_vector" and isinstance(v, (int, float)):
                if not np.isnan(v) and not np.isinf(v):
                    self.tree.insert(
                        additional_id, "end", text=k.capitalize(), values=(f"{v:.4f}",)
                    )

        for k, v in results["texture"].items():
            if isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):
                self.tree.insert(texture_id, "end", text=k.capitalize(), values=(f"{v:.4f}",))

        for k, v in results["timbre"].items():
            if k != "family_contributions" and isinstance(v, (int, float)):
                if not np.isnan(v) and not np.isinf(v):
                    self.tree.insert(timbre_id, "end", text=k.capitalize(), values=(f"{v:.4f}",))

        for k, v in results["orchestration"].items():
            if k != "register_distribution" and isinstance(v, (int, float)):
                if not np.isnan(v) and not np.isinf(v):
                    self.tree.insert(
                        orchestration_id, "end", text=k.capitalize(), values=(f"{v:.4f}",)
                    )

    def create_embedded_graphs(self, pitches: list[float], densities: list[float]) -> None:
        if self.embedded_graphs_frame is None:
            return
        self.clear_graphs()

        note_names = [midi_to_note_name(p) for p in pitches]
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(range(len(pitches)), densities, color="royalblue", alpha=0.8)
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.1,
                f"{height:.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
        ax.set_title("Densidade Espectral por Nota", fontsize=11)
        ax.set_xlabel("Notas", fontsize=10)
        ax.set_ylabel("Densidade", fontsize=10)
        ax.set_xticks(range(len(pitches)))
        ax.set_xticklabels(note_names, rotation=45, ha="right")
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.embedded_graphs_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self.embedded_graphs_frame)
        toolbar.update()
