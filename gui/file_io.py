"""
GUI file I/O helpers (Tkinter). Not imported by the analytical core.
"""

from __future__ import annotations

import os
from tkinter import filedialog, messagebox


def prompt_save_results_path(initialdir: str | None = None) -> str | None:
    """Ask the user for a JSON save path. Returns ``None`` if cancelled."""
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Save analysis results",
        initialdir=initialdir or os.getcwd(),
    )
    return path or None


def show_save_error(message: str) -> None:
    messagebox.showerror("Error", f"Error saving results: {message}")
