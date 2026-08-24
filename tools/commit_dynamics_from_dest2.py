#!/usr/bin/env python3
"""Commit 10-dynamic ladders from D:\\CORDAS_2 / MADEIRAS_2 / METAIS_2 *_dynamics.xlsx."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.generate_full_dynamics_modules_from_xlsx import (  # noqa: E402
    load_results_table,
    render_module,
    InstrumentSpec,
)

VERSION = "2026-08-24"


@dataclass(frozen=True)
class DestSpec:
    spec: InstrumentSpec
    xlsx: Path


SPECS = (
    DestSpec(
        InstrumentSpec("violin", "Violin", "Violin_dynamics.xlsx", "violin", "arco_sustain", "arco"),
        Path(r"D:\CORDAS_2\Violin_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("viola", "Viola", "Viola_dynamics.xlsx", "viola", "arco_sustain", "arco"),
        Path(r"D:\CORDAS_2\Viola_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("cello", "Cello", "Cello_dynamics.xlsx", "cello", "arco_sustain", "arco"),
        Path(r"D:\CORDAS_2\Cello_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec(
            "double_bass",
            "Double bass",
            "DoubleBass_dynamics.xlsx",
            "double-bass-double_bass",
            "arco_sustain",
            "arco",
        ),
        Path(r"D:\CORDAS_2\DoubleBass_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("flute", "Flute", "Flute_dynamics.xlsx", "flute", "ordinary_sustain", "ordinary sustain"),
        Path(r"D:\MADEIRAS_2\Flute_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("clarinet", "Clarinet", "Clarinet_dynamics.xlsx", "clarinet", "ordinary_sustain", "ordinary sustain"),
        Path(r"D:\MADEIRAS_2\Clarinet_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("oboe", "Oboe", "Oboe_dynamics.xlsx", "oboe", "ordinary_sustain", "ordinary sustain"),
        Path(r"D:\MADEIRAS_2\Oboe_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("bassoon", "Bassoon", "Bassoon_dynamics.xlsx", "bassoon", "ordinary_sustain", "ordinary sustain"),
        Path(r"D:\MADEIRAS_2\Bassoon_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("horn", "Horn", "Horn_dynamics.xlsx", "horn", "ordinary_sustain", "ordinary sustain"),
        Path(r"D:\METAIS_2\Horn_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("trumpet", "Trumpet", "Trumpet_dynamics.xlsx", "trumpet", "ordinary_sustain", "ordinary sustain"),
        Path(r"D:\METAIS_2\Trumpet_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("trombone", "Trombone", "Trombone_dynamics.xlsx", "trombone", "ordinary_sustain", "ordinary sustain"),
        Path(r"D:\METAIS_2\Trombone_dynamics.xlsx"),
    ),
    DestSpec(
        InstrumentSpec("tuba", "Tuba", "Tuba_dynamics.xlsx", "tuba", "ordinary_sustain", "ordinary sustain"),
        Path(r"D:\METAIS_2\Tuba_dynamics.xlsx"),
    ),
)


def main() -> int:
    for item in SPECS:
        if not item.xlsx.is_file():
            raise SystemExit(f"Missing dynamics workbook: {item.xlsx}")
        table = load_results_table(item.xlsx, "Results")
        text = render_module(item.spec, table, source_path=item.xlsx, sheet="Results")
        text = text.replace('version="2026-08-03"', f'version="{VERSION}"')
        out = ROOT / "instrumentos" / f"{item.spec.module}.py"
        out.write_text(text, encoding="utf-8")
        print(f"Wrote {out.name} ({len(table)} pitches from {item.xlsx})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
