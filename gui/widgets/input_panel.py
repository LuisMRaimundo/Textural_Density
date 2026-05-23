"""Note entry grid, weight slider, and GUI-only options."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from gui.state import (
    CENTS_VALUES,
    DYNAMIC_LEVELS,
    INSTRUMENTS,
    NOTAS_BASE,
    NUM_NOTE_ROWS,
    OCTAVE_LIST,
)
from gui.types import GuiAnalysisInput

logger = logging.getLogger("gui.input_panel")


class InputPanel:
    """Collects symbolic slice input; does not run analysis."""

    def __init__(self, parent: tk.Misc, on_row_toggle: Callable[[int], None]) -> None:
        self._on_row_toggle = on_row_toggle
        self.var_save_results = tk.BooleanVar(value=False)
        self.var_show_graphs = tk.BooleanVar(value=True)
        self.weight_factor_slider: tk.Scale | None = None

        self.note_vars: list[tk.StringVar] = []
        self.octave_vars: list[tk.StringVar] = []
        self.cents_vars: list[tk.StringVar] = []
        self.dynamic_vars: list[tk.StringVar] = []
        self.instrument_vars: list[tk.StringVar] = []
        self.num_instruments_vars: list[tk.StringVar] = []
        self.state_vars: list[tk.IntVar] = []
        self.note_menus: list[ttk.Combobox] = []
        self.octave_menus: list[ttk.Combobox] = []
        self.cents_menus: list[ttk.Combobox] = []
        self.dynamic_menus: list[ttk.Combobox] = []
        self.instrument_menus: list[ttk.Combobox] = []
        self.num_instruments_menus: list[ttk.Combobox] = []

        self.input_frame = tk.Frame(parent)
        self._build_weight_slider(parent)
        self._build_note_grid()
        self._build_options(parent)

    def _build_weight_slider(self, parent: tk.Misc) -> None:
        slider_frame = tk.Frame(parent)
        slider_frame.pack(pady=(10, 5), fill="x", padx=20)

        tk.Label(
            slider_frame,
            text="Adjust balance between components:",
            font=("Arial", 10, "bold"),
        ).pack(pady=(5, 3))

        balance_frame = tk.Frame(slider_frame)
        balance_frame.pack(fill="x")
        tk.Label(balance_frame, text="100% Interval Density", anchor="w", fg="blue").pack(
            side=tk.LEFT
        )
        tk.Label(balance_frame, text="100% Instrument Density", anchor="e", fg="red").pack(
            side=tk.RIGHT
        )

        self.weight_factor_slider = tk.Scale(
            slider_frame,
            from_=0,
            to=1,
            orient="horizontal",
            resolution=0.01,
            length=400,
            showvalue=True,
            tickinterval=0.25,
            label="Weight factor",
        )
        self.weight_factor_slider.set(0.5)
        self.weight_factor_slider.pack(pady=(0, 10))

        help_text = (
            "Move the slider left to increase interval density importance, or\n"
            "right to increase the importance of density from the instrument."
        )
        tk.Label(slider_frame, text=help_text, font=("Arial", 8, "italic")).pack(pady=(0, 5))

    def _build_note_grid(self) -> None:
        headers = ("Enable", "Note", "Octave", "Cents", "Dynamic", "Instrument", "Qty")
        for col, label in enumerate(headers):
            tk.Label(self.input_frame, text=label).grid(row=0, column=col, padx=5, pady=5)

        for i in range(NUM_NOTE_ROWS):
            row = i + 1
            state_var = tk.IntVar(value=0)
            self.state_vars.append(state_var)
            tk.Checkbutton(
                self.input_frame,
                variable=state_var,
                command=lambda idx=i: self._on_row_toggle(idx),
            ).grid(row=row, column=0, padx=5, pady=2)

            note_var = tk.StringVar()
            self.note_vars.append(note_var)
            note_menu = ttk.Combobox(
                self.input_frame, textvariable=note_var, values=NOTAS_BASE, width=5, state="disabled"
            )
            note_menu.grid(row=row, column=1, padx=5, pady=2)
            self.note_menus.append(note_menu)

            octave_var = tk.StringVar(value="4")
            self.octave_vars.append(octave_var)
            octave_menu = ttk.Combobox(
                self.input_frame,
                textvariable=octave_var,
                values=OCTAVE_LIST,
                width=5,
                state="disabled",
            )
            octave_menu.grid(row=row, column=2, padx=5, pady=2)
            self.octave_menus.append(octave_menu)

            cents_var = tk.StringVar(value="0")
            self.cents_vars.append(cents_var)
            cents_menu = ttk.Combobox(
                self.input_frame,
                textvariable=cents_var,
                values=CENTS_VALUES,
                width=5,
                state="disabled",
            )
            cents_menu.grid(row=row, column=3, padx=5, pady=2)
            self.cents_menus.append(cents_menu)

            dynamic_var = tk.StringVar(value="mf")
            self.dynamic_vars.append(dynamic_var)
            dynamic_menu = ttk.Combobox(
                self.input_frame,
                textvariable=dynamic_var,
                values=DYNAMIC_LEVELS,
                width=5,
                state="disabled",
            )
            dynamic_menu.grid(row=row, column=4, padx=5, pady=2)
            self.dynamic_menus.append(dynamic_menu)

            instrument_var = tk.StringVar(value="Flauta")
            self.instrument_vars.append(instrument_var)
            instrument_menu = ttk.Combobox(
                self.input_frame,
                textvariable=instrument_var,
                values=INSTRUMENTS,
                width=10,
                state="disabled",
            )
            instrument_menu.grid(row=row, column=5, padx=5, pady=2)
            self.instrument_menus.append(instrument_menu)

            num_var = tk.StringVar(value="1")
            self.num_instruments_vars.append(num_var)
            num_menu = ttk.Combobox(
                self.input_frame,
                textvariable=num_var,
                values=[str(j) for j in range(1, 21)],
                width=5,
                state="disabled",
            )
            num_menu.grid(row=row, column=6, padx=5, pady=2)
            self.num_instruments_menus.append(num_menu)

    def _build_options(self, parent: tk.Misc) -> None:
        options_frame = tk.Frame(parent)
        options_frame.pack(pady=5)
        tk.Checkbutton(
            options_frame, text="Save results to file", variable=self.var_save_results
        ).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(
            options_frame, text="Show detailed graphs", variable=self.var_show_graphs
        ).pack(side=tk.LEFT, padx=5)

    def toggle_row(self, index: int) -> None:
        state = "normal" if self.state_vars[index].get() == 1 else "disabled"
        self.note_menus[index].config(state=state)
        self.octave_menus[index].config(state=state)
        self.cents_menus[index].config(state=state)
        self.dynamic_menus[index].config(state=state)
        self.instrument_menus[index].config(state=state)
        self.num_instruments_menus[index].config(state=state)

    def clear(self) -> None:
        for var in self.note_vars:
            var.set("")
        for var in self.octave_vars:
            var.set("4")
        for var in self.cents_vars:
            var.set("0")
        for var in self.dynamic_vars:
            var.set("mf")
        for var in self.instrument_vars:
            var.set("Flauta")
        for var in self.num_instruments_vars:
            var.set("1")
        for var in self.state_vars:
            var.set(0)
        if self.weight_factor_slider is not None:
            self.weight_factor_slider.set(0.5)

    def collect_raw_input(self) -> GuiAnalysisInput:
        """Return GUI-collected dict (includes save_results / show_graphs)."""
        active_indices = [i for i in range(len(self.state_vars)) if self.state_vars[i].get() == 1]
        complete_notes: list[str] = []
        for i in active_indices:
            note_part = self.note_vars[i].get()
            octave_part = self.octave_vars[i].get()
            cents_part = self.cents_vars[i].get()
            if note_part and octave_part:
                if cents_part and cents_part != "0":
                    complete_notes.append(f"{note_part}{octave_part}{cents_part}c")
                else:
                    complete_notes.append(f"{note_part}{octave_part}")
            else:
                logger.warning(
                    "Incomplete note row: note=%s octave=%s", note_part, octave_part
                )
                if note_part and not octave_part:
                    complete_notes.append(f"{note_part}4")
                elif octave_part and not note_part:
                    complete_notes.append(f"C{octave_part}")
                else:
                    complete_notes.append("C4")

        raw: dict[str, Any] = {
            "notes": complete_notes,
            "dynamics": [self.dynamic_vars[i].get() for i in active_indices],
            "instruments": [self.instrument_vars[i].get() for i in active_indices],
            "num_instruments": [
                int(self.num_instruments_vars[i].get()) for i in active_indices
            ],
            "weight_factor": self.weight_factor_slider.get() if self.weight_factor_slider else 0.5,
            "save_results": self.var_save_results.get(),
            "show_graphs": self.var_show_graphs.get(),
        }
        return raw  # type: ignore[return-value]

    def load_from_data(self, data: dict[str, Any]) -> None:
        from core.input_validation import strip_removed_gui_preference_keys
        from xml_loader import note_string_to_gui_parts

        data, stripped = strip_removed_gui_preference_keys(dict(data))
        if stripped:
            logger.warning(
                "Ignored removed legacy options in loaded data: %s",
                ", ".join(sorted(stripped)),
            )
        self.clear()
        notes = data.get("notes", [])
        dynamics = list(data.get("dynamics", []))
        instruments = list(data.get("instruments", []))
        num_instruments = list(data.get("num_instruments", []))
        n = min(len(notes), NUM_NOTE_ROWS)
        if len(dynamics) < n:
            dynamics.extend(["mf"] * (n - len(dynamics)))
        if len(instruments) < n:
            instruments.extend(["Flauta"] * (n - len(instruments)))
        if len(num_instruments) < n:
            num_instruments.extend([1] * (n - len(num_instruments)))
        for i in range(n):
            self.state_vars[i].set(1)
            note_base, octave_str, cents_str = note_string_to_gui_parts(notes[i])
            self.note_vars[i].set(note_base)
            self.octave_vars[i].set(octave_str)
            self.cents_vars[i].set(cents_str)
            self.dynamic_vars[i].set(dynamics[i])
            self.instrument_vars[i].set(instruments[i])
            num_val = num_instruments[i]
            self.num_instruments_vars[i].set(str(max(1, min(20, int(num_val)))))
            self.toggle_row(i)
        if self.weight_factor_slider is not None:
            self.weight_factor_slider.set(
                max(0.0, min(1.0, float(data.get("weight_factor", 0.5))))
            )
        if "save_results" in data:
            self.var_save_results.set(bool(data["save_results"]))
        if "show_graphs" in data:
            self.var_show_graphs.set(bool(data["show_graphs"]))
