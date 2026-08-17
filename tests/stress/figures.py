"""Matplotlib figures for the stress battery report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tests.stress.engine import SliceResult, _get, by_id


def write_figures(results: list[SliceResult], out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = by_id(results)
    paths: dict[str, Path] = {}

    # A2 doubling curve
    qs = [1, 2, 4, 8, 16]
    a2 = [idx.get(f"A2_violin_C4_qty{q}") for q in qs]
    if all(r and r.ok for r in a2):
        totals = [float(_get(r, "density", "total")) for r in a2]  # type: ignore[arg-type]
        masses = [float(_get(r, "density", "sonic_mass")) for r in a2]  # type: ignore[arg-type]
        fig, ax1 = plt.subplots(figsize=(6.5, 3.8))
        ax1.plot(qs, totals, "o-", color="#1f4e79", label="Composite")
        ax1.set_xlabel("Qty (violin C4 unison)")
        ax1.set_ylabel("Composite", color="#1f4e79")
        ax2 = ax1.twinx()
        ax2.plot(qs, masses, "s--", color="#c45911", label="Sonic mass")
        ax2.set_ylabel("Sonic mass", color="#c45911")
        ax1.set_title("A2 — Unison Qty stacking (mass↑, pitch metrics invariant)")
        fig.tight_layout()
        p = out_dir / "A2_doubling_curve.png"
        fig.savefig(p, dpi=140)
        plt.close(fig)
        paths["A2"] = p

    # B3 dynamics ladder
    dyns = ["pp", "mf", "ff", "ffff"]
    b3 = [idx.get(f"B3_tamtam_{d}") for d in dyns]
    if all(r and r.ok for r in b3):
        totals = [float(_get(r, "density", "total")) for r in b3]  # type: ignore[arg-type]
        fig, ax = plt.subplots(figsize=(6.0, 3.6))
        ax.plot(dyns, totals, "o-", color="#548235")
        ax.set_xlabel("Dynamic")
        ax.set_ylabel("Composite")
        ax.set_title("B3 — Tam-tam dynamics ladder (cascade discontinuity at mf→ff)")
        if len(totals) >= 3:
            ax.annotate(
                f"Δ={totals[2]-totals[1]:.4f}",
                xy=(2, totals[2]),
                xytext=(1.2, (totals[1] + totals[2]) / 2),
                arrowprops=dict(arrowstyle="->", color="#843c0c"),
                fontsize=9,
            )
        fig.tight_layout()
        p = out_dir / "B3_dynamics_ladder.png"
        fig.savefig(p, dpi=140)
        plt.close(fig)
        paths["B3"] = p

    # C3 percussion fraction sweep
    shares = list(range(0, 5))
    c3 = [idx.get(f"C3_perc_share_{n}_of_8") for n in shares]
    if all(r and r.ok for r in c3):
        totals = [float(_get(r, "density", "total")) for r in c3]  # type: ignore[arg-type]
        rss = [float(_get(r, "density", "instrument")) for r in c3]  # type: ignore[arg-type]
        fig, ax1 = plt.subplots(figsize=(6.5, 3.8))
        x = [n / 8 for n in shares]
        ax1.plot(x, totals, "o-", color="#1f4e79", label="Composite")
        ax1.set_xlabel("Unpitched event share (of 8 players)")
        ax1.set_ylabel("Composite", color="#1f4e79")
        ax2 = ax1.twinx()
        ax2.plot(x, rss, "s--", color="#c45911", label="RSS (instrument)")
        ax2.set_ylabel("Instrument density (RSS)", color="#c45911")
        ax1.set_title("C3 — Percussion fraction sweep (fixed 8-player total)")
        fig.tight_layout()
        p = out_dir / "C3_perc_fraction_sweep.png"
        fig.savefig(p, dpi=140)
        plt.close(fig)
        paths["C3"] = p

    # C5 tutti comparison
    r0, r1 = idx.get("C5_tutti_no_perc"), idx.get("C5_tutti_with_perc")
    if r0 and r0.ok and r1 and r1.ok:
        vals = [
            float(_get(r0, "density", "total")),
            float(_get(r1, "density", "total")),
        ]
        fig, ax = plt.subplots(figsize=(5.5, 3.6))
        ax.bar(
            ["Pitched tutti", "Tutti + percussion"],
            vals,
            color=["#5b9bd5", "#ed7d31"],
        )
        ax.set_ylabel("Composite")
        ax.set_title("C5 — Realistic tutti with / without percussion battery")
        for i, v in enumerate(vals):
            ax.text(i, v, f"{v:.4f}", ha="center", va="bottom", fontsize=9)
        fig.tight_layout()
        p = out_dir / "C5_tutti_comparison.png"
        fig.savefig(p, dpi=140)
        plt.close(fig)
        paths["C5"] = p

    return paths
