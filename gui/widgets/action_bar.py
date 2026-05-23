"""Bottom action bar (load, calculate, clear, report)."""

from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Mapping


class ActionBar:
    def __init__(self, root: tk.Misc, callbacks: Mapping[str, Callable[..., Any]]) -> None:
        frame = tk.Frame(root)
        frame.pack(side=tk.BOTTOM, pady=10)

        tk.Button(frame, text="Load XML", command=callbacks.get("load_xml")).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        tk.Button(frame, text="Load MIDI", command=callbacks.get("load_midi")).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        tk.Button(frame, text="Calculate", command=callbacks["calculate"]).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        tk.Button(frame, text="Clear", command=callbacks["clear"]).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        tk.Button(
            frame, text="Generate Scientific Report", command=callbacks["generate_report"]
        ).pack(side=tk.LEFT, padx=5, pady=5)

        self.frame = frame
