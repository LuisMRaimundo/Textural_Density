#!/usr/bin/env python
"""
Launcher for Textural Density (Phase 5.1).
Sets working directory to the script folder and runs the Tkinter app.
Usage: python run.py   or   python -m run (from project root)
"""
import os
import sys
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent
    os.chdir(root_dir)
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    import tkinter as tk
    from tkinter import ttk

    from Main import DensityAnalyzerApp

    root = tk.Tk()
    root.geometry("1200x700")
    # Slightly better defaults: font and ttk theme where available
    # Use Tcl braces so "Segoe UI" is one token; otherwise Tk parses "UI" as size and raises "expected integer but got UI"
    try:
        root.option_add("*Font", "{Segoe UI} 10")
    except Exception:
        pass
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass
    app = DensityAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
