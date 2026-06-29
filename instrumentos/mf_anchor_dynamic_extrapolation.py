"""Extrapolate pp/ff GPR anchors from a single measured mf anchor row."""

from __future__ import annotations

from typing import Mapping


def build_spectral_data_from_mf_anchor(
    mf_measured: Mapping[str, float],
    *,
    reference_module_name: str = "violin",
) -> dict[str, dict[str, float]]:
    """
    Build a pp/mf/ff table when only mf is measured.

    pp and ff are derived per note using the reference module's pp/mf and ff/mf
    ratios (default: violin arco). mf values are copied exactly from
    ``mf_measured``.
    """
    import importlib

    reference = importlib.import_module(f"instrumentos.{reference_module_name}")
    reference_table = reference.spectral_data

    spectral: dict[str, dict[str, float]] = {}
    fallback_pp_ratio = _median_ratio(reference_table, "pp", "mf")
    fallback_ff_ratio = _median_ratio(reference_table, "ff", "mf")

    for note, mf_value in mf_measured.items():
        mf = round(float(mf_value), 6)
        ref = reference_table.get(note)
        if ref and ref.get("mf"):
            pp_ratio = float(ref["pp"]) / float(ref["mf"])
            ff_ratio = float(ref["ff"]) / float(ref["mf"])
        else:
            pp_ratio = fallback_pp_ratio
            ff_ratio = fallback_ff_ratio
        spectral[note] = {
            "pp": round(mf * pp_ratio, 6),
            "mf": mf,
            "ff": round(mf * ff_ratio, 6),
        }
    return spectral


def _median_ratio(
    reference_table: Mapping[str, Mapping[str, float]],
    numerator_key: str,
    denominator_key: str,
) -> float:
    ratios: list[float] = []
    for row in reference_table.values():
        denominator = float(row[denominator_key])
        if denominator:
            ratios.append(float(row[numerator_key]) / denominator)
    if not ratios:
        return 1.0
    ratios.sort()
    mid = len(ratios) // 2
    if len(ratios) % 2:
        return ratios[mid]
    return (ratios[mid - 1] + ratios[mid]) / 2.0
