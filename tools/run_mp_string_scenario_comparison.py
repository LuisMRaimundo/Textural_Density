#!/usr/bin/env python3
"""Before/after comparison for string scenarios using ``mp`` dynamic handling."""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.metrics_metadata import collect_slice_warnings  # noqa: E402
from core.converters import legacy_input_to_vertical_slice, analysis_config_from_input  # noqa: E402
from core.pipeline import calculate_metrics  # noqa: E402
from tests.string_constants import STRING_INSTRUMENTS  # noqa: E402

REPORTS = ROOT / "reports"
CAMPAIGN_DYNAMICS = ("pp", "p", "mp", "mf", "f", "ff")


def _load_mod(module_name: str):
    return __import__(f"instrumentos.{module_name}", fromlist=["spectral_data"])


def _middle_note(module_name: str) -> str:
    notes = sorted(_load_mod(module_name).spectral_data.keys())
    return notes[len(notes) // 2]


def _old_mp_density(module_name: str, note: str) -> float:
    mod = _load_mod(module_name)
    return float(mod.calcular_densidade(note, "mf"))


def _new_mp_density(module_name: str, note: str) -> float:
    mod = _load_mod(module_name)
    pp = mod.calcular_densidade(note, "pp")
    mf = mod.calcular_densidade(note, "mf")
    ff = mod.calcular_densidade(note, "ff")
    return float(mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])["mp"][0])


def _pipeline_run(
    instruments: list[str], notes: list[str], dynamics: list[str], quantities: list[int]
) -> tuple[dict[str, float], list[str]]:
    resultados, one_player, _ = calculate_metrics(
        {
            "notes": notes,
            "dynamics": dynamics,
            "instruments": instruments,
            "num_instruments": quantities,
            "weight_factor": 0.5,
        }
    )
    slice_ = legacy_input_to_vertical_slice(
        {
            "notes": notes,
            "dynamics": dynamics,
            "instruments": instruments,
            "num_instruments": quantities,
        }
    )
    config = analysis_config_from_input({})
    warnings, _ = collect_slice_warnings(slice_, config)
    dyn = dynamics[0]
    # For homogeneous dynamic slices, per-event densities are aligned with events.
    if len(set(dynamics)) == 1:
        return {dyn: float(one_player[0])}, warnings
    values = {d: float(one_player[i]) for i, d in enumerate(dynamics)}
    return values, warnings


def _scenario_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for spec in STRING_INSTRUMENTS:
        mod = _load_mod(spec.module_name)
        notes_sorted = sorted(mod.spectral_data.keys())
        for band, note in (
            ("low", notes_sorted[0]),
            ("middle", notes_sorted[len(notes_sorted) // 2]),
            ("high", notes_sorted[-1]),
        ):
            specs.append(
                {
                    "scenario_id": f"{spec.module_name}_solo_{band}",
                    "instruments": [spec.registry_ids[0]],
                    "quantities": [1],
                    "register": band,
                    "notes": [note],
                    "module_name": spec.module_name,
                }
            )
    quartet_notes = [_middle_note(s.module_name) for s in STRING_INSTRUMENTS]
    specs.append(
        {
            "scenario_id": "string_quartet_middle",
            "instruments": [s.registry_ids[0] for s in STRING_INSTRUMENTS],
            "quantities": [1, 1, 1, 1],
            "register": "middle",
            "notes": quartet_notes,
            "module_name": None,
        }
    )
    specs.append(
        {
            "scenario_id": "violin_section_qty3",
            "instruments": ["violino"],
            "quantities": [3],
            "register": "middle",
            "notes": ["G4"],
            "module_name": "violin",
        }
    )
    specs.append(
        {
            "scenario_id": "cello_low_register_mass",
            "instruments": ["violoncelo"],
            "quantities": [4],
            "register": "low",
            "notes": [sorted(_load_mod("cello").spectral_data.keys())[0]],
            "module_name": "cello",
        }
    )
    return specs


def main() -> int:
    specs = _scenario_specs()
    rows: list[dict[str, Any]] = []
    for spec in specs:
        module_name = spec.get("module_name") or "violin"
        note_for_mp = spec["notes"][0]
        old_mp = _old_mp_density(module_name, note_for_mp)
        new_mp = _new_mp_density(module_name, note_for_mp)
        n = len(spec["notes"])
        values: dict[str, float] = {}
        all_warnings: list[str] = []
        for dyn in CAMPAIGN_DYNAMICS:
            dyn_vals, warns = _pipeline_run(
                spec["instruments"],
                spec["notes"],
                [dyn] * n,
                spec["quantities"],
            )
            values[dyn] = dyn_vals[dyn]
            all_warnings.extend(warns)
        mp_warnings = [w for w in all_warnings if "mp" in w.lower() and "mapped to 'mf'" in w]
        mod = _load_mod(module_name)
        mf_anchor = float(mod.calcular_densidade(note_for_mp, "mf"))
        rows.append(
            {
                "scenario_id": spec["scenario_id"],
                "notes": spec["notes"],
                "instruments": spec["instruments"],
                "quantities": spec["quantities"],
                "register": spec["register"],
                "p_value": values.get("p"),
                "old_mp_value": old_mp,
                "new_mp_value": new_mp,
                "mf_value": values.get("mf"),
                "f_value": values.get("f"),
                "pp_value": values.get("pp"),
                "ff_value": values.get("ff"),
                "pipeline_mp_value": values.get("mp"),
                "old_warning": (
                    "Unknown dynamic 'mp' at event evt_0; mapped to 'mf' for instrument density."
                ),
                "new_warning": "; ".join(mp_warnings),
                "diff_from_mf_anchor": new_mp - mf_anchor,
                "method": "GPR coordinate 4.5",
                "provenance": "modelled_gpr",
            }
        )

    mp_warnings_after = sum(1 for r in rows if r["new_warning"])
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario_count": len(specs),
        "row_count": len(rows),
        "mp_warnings_before": len(specs),
        "mp_warnings_after": mp_warnings_after,
    }
    payload = {"summary": summary, "rows": rows}

    REPORTS.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS / "mp_string_scenario_comparison.json"
    csv_path = REPORTS / "mp_string_scenario_comparison.csv"
    md_path = REPORTS / "mp_string_scenario_comparison.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_lines = [
        "# mp string scenario comparison",
        "",
        f"- Scenarios: {summary['scenario_count']}",
        f"- mp warnings before (historical): {summary['mp_warnings_before']}",
        f"- mp warnings after: {summary['mp_warnings_after']}",
        "",
    ]
    for r in rows:
        md_lines.append(
            f"- {r['scenario_id']}: old_mp={r['old_mp_value']:.4f}, "
            f"new_mp={r['new_mp_value']:.4f}, pipeline_mp={r['pipeline_mp_value']:.4f}, "
            f"mf={r['mf_value']:.4f}"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote {json_path}, {csv_path}, {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
