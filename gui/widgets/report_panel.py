"""Scientific report configuration dialog."""

from __future__ import annotations

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
from typing import Any, Callable


class ReportPanel:
    def __init__(self, root: tk.Misc) -> None:
        self.root = root

    def show_report_config_dialog(self, on_generate: Callable[[dict[str, Any]], None]) -> None:
        directory = filedialog.askdirectory(
            title="Select directory to save reports",
            initialdir=os.getcwd(),
        )
        if not directory:
            return

        config_window = tk.Toplevel(self.root)
        config_window.title("Report Settings")
        config_window.geometry("500x500")

        config_frame = tk.Frame(config_window, padx=10, pady=10)
        config_frame.pack(fill="both", expand=True)

        tk.Label(config_frame, text="Report title:").grid(row=0, column=0, sticky="w", pady=5)
        title_var = tk.StringVar(value="Advanced Spectral Analysis of Musical Composition")
        tk.Entry(config_frame, textvariable=title_var, width=50).grid(row=0, column=1, pady=5)

        tk.Label(config_frame, text="Authors:").grid(row=1, column=0, sticky="w", pady=5)
        authors_var = tk.StringVar(value="")
        tk.Entry(config_frame, textvariable=authors_var, width=50).grid(row=1, column=1, pady=5)

        tk.Label(config_frame, text="Institution:").grid(row=2, column=0, sticky="w", pady=5)
        institution_var = tk.StringVar(value="")
        tk.Entry(config_frame, textvariable=institution_var, width=50).grid(row=2, column=1, pady=5)

        tk.Label(config_frame, text="Summary:").grid(row=3, column=0, sticky="w", pady=5)
        summary_text = tk.Text(config_frame, width=48, height=5)
        summary_text.grid(row=3, column=1, pady=5)
        summary_text.insert(
            "1.0",
            "This report presents a detailed analysis of spectral, textural and timbral "
            "properties of a set of musical notes using advanced quantitative methods.",
        )

        tk.Label(config_frame, text="Conclusions:").grid(row=4, column=0, sticky="w", pady=5)
        conclusions_text = tk.Text(config_frame, width=48, height=5)
        conclusions_text.grid(row=4, column=1, pady=5)
        conclusions_text.insert(
            "1.0",
            "The analyses demonstrate the effectiveness of spectral and textural metrics "
            "for objective characterisation of musical material. Results can be applied "
            "in musical analysis, composition and sound synthesis contexts.",
        )

        tk.Label(config_frame, text="Report formats:").grid(row=5, column=0, sticky="w", pady=5)
        pdf_var = tk.BooleanVar(value=True)
        tk.Checkbutton(config_frame, text="PDF report", variable=pdf_var).grid(
            row=5, column=1, sticky="w"
        )
        paper_var = tk.BooleanVar(value=True)
        tk.Checkbutton(config_frame, text="Scientific paper", variable=paper_var).grid(
            row=6, column=1, sticky="w"
        )
        figures_var = tk.BooleanVar(value=True)
        tk.Checkbutton(config_frame, text="Publication figures", variable=figures_var).grid(
            row=7, column=1, sticky="w"
        )
        tables_var = tk.BooleanVar(value=True)
        tk.Checkbutton(config_frame, text="Data tables", variable=tables_var).grid(
            row=8, column=1, sticky="w"
        )

        status_label = tk.Label(config_frame, text="", font=("Arial", 10, "italic"))
        status_label.grid(row=10, column=0, columnspan=2, pady=5)

        def execute_generation() -> None:
            config = {
                "title": title_var.get(),
                "authors": authors_var.get(),
                "institution": institution_var.get(),
                "abstract": summary_text.get("1.0", "end-1c"),
                "conclusions": conclusions_text.get("1.0", "end-1c"),
                "date": datetime.now().strftime("%d de %B de %Y"),
                "formats": {
                    "pdf": pdf_var.get(),
                    "paper": paper_var.get(),
                    "figures": figures_var.get(),
                    "tables": tables_var.get(),
                },
                "output_directory": directory,
            }
            status_label.config(text="Generating reports. Please wait...")
            config_window.update()
            on_generate(config)
            config_window.destroy()

        buttons_frame = tk.Frame(config_frame)
        buttons_frame.grid(row=9, column=0, columnspan=2, pady=10)
        tk.Button(buttons_frame, text="Generate Reports", command=execute_generation).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(buttons_frame, text="Cancelar", command=config_window.destroy).pack(
            side=tk.LEFT, padx=5
        )

        config_window.update_idletasks()
        width = config_window.winfo_width()
        height = config_window.winfo_height()
        x = (config_window.winfo_screenwidth() // 2) - (width // 2)
        y = (config_window.winfo_screenheight() // 2) - (height // 2)
        config_window.geometry(f"{width}x{height}+{x}+{y}")

        config_window.transient(self.root)
        config_window.grab_set()
        self.root.wait_window(config_window)
