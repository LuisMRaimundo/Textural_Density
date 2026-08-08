"""
Enforce monotone CDM ladders on pitched table-backed modules (offline).

For each pitch row with pp/mf/ff anchors:
1. Clamp anchors to non-decreasing soft→loud (pp ≤ mf ≤ ff)
2. Rebuild the full 10-level ladder with the former unpitched
   ``internal_default`` piecewise log-linear CDM + adaptive tails
   (``tools/legacy_gpr_dynamic_interpolation.py``, ``log_cdm_space=True``)

Does not modify unpitched percussion (already monotone DYNAMIC_CDM).
Does not touch core/composite.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from config import DYNAMIC_LEVELS  # noqa: E402
from instrumentos.registry import list_profiles  # noqa: E402
from legacy_gpr_dynamic_interpolation import (  # noqa: E402
    GPR_DYNAMIC_COORDINATES,
    predict_intermediate_dynamics_gpr,
)

FULL_DYNAMICS = tuple(DYNAMIC_LEVELS)


def _isotonic_anchors(pp: float, mf: float, ff: float) -> tuple[float, float, float]:
    """Clamp measured anchors to soft→loud non-decreasing order."""
    pp_i = float(pp)
    mf_i = max(pp_i, float(mf))
    ff_i = max(mf_i, float(ff))
    return pp_i, mf_i, ff_i


def monotone_ladder_from_anchors(pp: float, mf: float, ff: float) -> dict[str, float]:
    pp_i, mf_i, ff_i = _isotonic_anchors(pp, mf, ff)
    preds = predict_intermediate_dynamics_gpr(
        [pp_i],
        [mf_i],
        [ff_i],
        log_cdm_space=True,
    )
    return {d: round(float(preds[d][0]), 7) for d in GPR_DYNAMIC_COORDINATES}


def _format_spectral_data(spectral: dict[str, dict[str, float]]) -> str:
    lines = ["spectral_data = {"]
    for note, row in spectral.items():
        parts = ", ".join(f"'{d}': {row[d]}" for d in FULL_DYNAMICS if d in row)
        lines.append(f"    {note!r}: {{{parts}}},")
    lines.append("}")
    return "\n".join(lines)


def _replace_balanced_assignment(text: str, name: str, replacement: str) -> str:
    """Replace ``name = {...}`` with brace-balanced matching."""
    needle = f"{name} = {{"
    start = text.find(needle)
    if start < 0:
        raise ValueError(f"Assignment {name!r} not found")
    i = start + len(needle) - 1
    depth = 0
    in_str = False
    quote = ""
    escape = False
    while i < len(text):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
        else:
            if ch in ("'", '"'):
                in_str = True
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    return text[:start] + replacement + text[end:]
        i += 1
    raise ValueError(f"Unbalanced braces for {name}")


def _ensure_dynamic_levels(text: str) -> str:
    levels = "(" + ", ".join(repr(d) for d in FULL_DYNAMICS) + ")"
    pattern = r"dynamic_levels=\([^)]*\)"
    if not re.search(pattern, text):
        return text
    return re.sub(pattern, f"dynamic_levels={levels}", text, count=1)


def pitched_module_names() -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for profile in list_profiles():
        if not profile.module_name or profile.unpitched:
            continue
        if profile.module_name in seen:
            continue
        seen.add(profile.module_name)
        names.append(profile.module_name)
    return names


def rewrite_module(module_name: str) -> tuple[int, int]:
    mod = importlib.import_module(f"instrumentos.{module_name}")
    old = getattr(mod, "spectral_data", None)
    if not isinstance(old, dict) or not old:
        raise ValueError(f"{module_name}: no spectral_data")

    new: dict[str, dict[str, float]] = {}
    changed_rows = 0
    for note, row in old.items():
        if not all(k in row for k in ("pp", "mf", "ff")):
            new[note] = dict(row)
            continue
        ladder = monotone_ladder_from_anchors(
            float(row["pp"]), float(row["mf"]), float(row["ff"])
        )
        if any(abs(float(row.get(d, -1)) - ladder[d]) > 1e-9 for d in FULL_DYNAMICS):
            changed_rows += 1
        new[note] = ladder

    path = ROOT / "instrumentos" / f"{module_name}.py"
    text = path.read_text(encoding="utf-8")
    text = _replace_balanced_assignment(text, "spectral_data", _format_spectral_data(new))
    text = _ensure_dynamic_levels(text)
    marker = "monotone log-CDM ladder enforcement"
    if marker not in text:
        note = (
            f"{marker} (2026-08-03): pp/mf/ff anchors isotonic-clamped then "
            "full DYNAMIC_LEVELS rebuilt via offline internal_default "
            "log-linear + adaptive tails; "
        )
        text2, n = re.subn(
            r"(extraction_method=\(\s*\n?\s*\")",
            rf"\1{note}",
            text,
            count=1,
        )
        if n:
            text = text2
    path.write_text(text, encoding="utf-8")
    return len(new), changed_rows


def main() -> int:
    total_changed = 0
    for name in pitched_module_names():
        n_rows, n_changed = rewrite_module(name)
        total_changed += n_changed
        print(f"{name}: {n_rows} rows, {n_changed} rewritten")
    print(f"Done. Rows rewritten: {total_changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
