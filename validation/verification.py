"""
Verification runner — synthetic and property checks (Phase 8).
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from validation.synthetic_cases import all_synthetic_cases, base_input


@dataclass
class CheckResult:
    check_id: str
    passed: bool
    message: str


@dataclass
class VerificationResult:
    synthetic_cases_run: int
    checks: list[CheckResult] = field(default_factory=list)
    external_validation_available: bool = False

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failed_checks(self) -> list[CheckResult]:
        return [c for c in self.checks if not c.passed]


def _calculate(input_data: dict[str, Any]) -> dict[str, Any]:
    from data_processor import calculate_metrics

    resultados, _, _ = calculate_metrics(input_data)
    return resultados


def _finite_density(resultados: dict[str, Any]) -> bool:
    for val in resultados.get("density", {}).values():
        if not np.isfinite(float(val)):
            return False
    return True


def run_verification_suite() -> VerificationResult:
    """Run synthetic verification and property checks."""
    checks: list[CheckResult] = []
    cases = all_synthetic_cases()

    for case in cases:
        try:
            resultados = _calculate(case.input_data)
            ok = _finite_density(resultados)
            checks.append(
                CheckResult(
                    f"synthetic.{case.case_id}.finite",
                    ok,
                    f"{case.description}: density outputs finite"
                    if ok
                    else f"{case.description}: non-finite density",
                )
            )
        except Exception as exc:
            checks.append(
                CheckResult(
                    f"synthetic.{case.case_id}.finite",
                    False,
                    f"{case.description}: {exc}",
                )
            )

    # --- Property checks (qualitative verification) ---
    chromatic = _calculate(base_input(["C4", "C#4", "D4", "D#4", "E4"]))["density"]["interval"]
    wide = _calculate(
        base_input(["C3", "G3", "D4", "A4", "E5"], instruments=["violoncelo"] * 5)
    )["density"]["interval"]
    checks.append(
        CheckResult(
            "property.chromatic_gt_wide_interval",
            float(chromatic) > float(wide),
            f"chromatic={chromatic:.4f}, wide={wide:.4f}",
        )
    )

    low_players = base_input(["C4", "E4"], num_instruments=[1, 1])
    high_players = base_input(["C4", "E4"], num_instruments=[4, 4])
    mass_low = _calculate(low_players)["density_subindices"]["orchestral_mass"]["raw"]
    mass_high = _calculate(high_players)["density_subindices"]["orchestral_mass"]["raw"]
    interval_low = _calculate(low_players)["density"]["interval"]
    interval_high = _calculate(high_players)["density"]["interval"]
    checks.append(
        CheckResult(
            "property.player_mass_increases",
            float(mass_high) > float(mass_low),
            f"mass low={mass_low}, high={mass_high}",
        )
    )
    checks.append(
        CheckResult(
            "property.interval_unchanged_by_players",
            float(interval_low) == float(interval_high),
            f"interval low={interval_low}, high={interval_high}",
        )
    )

    narrow = _calculate(base_input(["C4", "E4", "G4"]))
    wide_span = _calculate(
        base_input(["C3", "E4", "G5"], instruments=["violoncelo"] * 3)
    )
    pitch_n = narrow["density"]["pitch_structure"]
    pitch_w = wide_span["density"]["pitch_structure"]
    checks.append(
        CheckResult(
            "property.pitch_structure_decreases_with_span",
            float(pitch_w) < float(pitch_n),
            f"pitch_structure narrow={pitch_n:.4f}, wide={pitch_w:.4f}",
        )
    )

    unison = _calculate(base_input(["C4", "C4", "C4", "C4"]))
    differentiated = _calculate(base_input(["C4", "C#4", "D4", "E4"]))
    checks.append(
        CheckResult(
            "property.unison_not_highest_composite",
            float(differentiated["density"]["total"]) > float(unison["density"]["total"]),
            (
                f"unison total={unison['density']['total']:.4f}, "
                f"differentiated={differentiated['density']['total']:.4f}"
            ),
        )
    )
    checks.append(
        CheckResult(
            "property.unison_zero_pitch_structure",
            float(unison["density"]["pitch_structure"]) == 0.0,
            f"unison pitch_structure={unison['density']['pitch_structure']}",
        )
    )

    quiet = _calculate(base_input(["C4", "E4", "G4"], dynamics=["pp", "pp", "pp"]))
    loud = _calculate(base_input(["C4", "E4", "G4"], dynamics=["ff", "ff", "ff"]))
    mass_q = quiet["density"]["sonic_mass"]
    mass_l = loud["density"]["sonic_mass"]
    count_q = quiet["density_subindices"]["event_count"]["raw"]["event_count"]
    count_l = loud["density_subindices"]["event_count"]["raw"]["event_count"]
    checks.append(
        CheckResult(
            "property.dynamics_affect_mass",
            float(mass_l) > float(mass_q) and count_q == count_l,
            f"mass quiet={mass_q}, loud={mass_l}",
        )
    )

    flauta_only = _calculate(
        base_input(["C4", "E4"], instruments=["flauta", "flauta"])
    )
    mixed = _calculate(
        base_input(["C4", "E4"], instruments=["flauta", "trompete"])
    )
    checks.append(
        CheckResult(
            "property.family_change_affects_timbre_not_interval",
            float(mixed["density"]["interval"]) == float(flauta_only["density"]["interval"])
            and float(mixed["density"]["instrument"]) != float(flauta_only["density"]["instrument"]),
            "interval unchanged; instrument density changed",
        )
    )

    base = _calculate(base_input(["C4", "E4", "G4"]))
    checks.append(
        CheckResult(
            "property.no_combination_tone_subindex",
            "combination_tone_candidates" not in base.get("density_subindices", {}),
            "combination-tone subindex absent (feature removed)",
        )
    )

    from error_handler import InputError

    combo_rejected = False
    try:
        _calculate(base_input(["C4", "E4", "G4"], calculate_combination_tones=True))
    except InputError:
        combo_rejected = True
    checks.append(
        CheckResult(
            "property.combo_keys_rejected",
            combo_rejected,
            "calculate_combination_tones raises InputError",
        )
    )

    unknown = deepcopy(base_input(["C4", "E4"]))
    unknown["instruments"] = ["flauta", "unknown_xyz_instrument"]
    warnings = _calculate(unknown).get("metric_metadata", {}).get("warnings", [])
    checks.append(
        CheckResult(
            "property.unknown_instrument_warns",
            any("unknown" in w.lower() or "registry" in w.lower() for w in warnings),
            f"warnings={warnings[:2]}",
        )
    )

    from spectral_analysis import calculate_chroma_vector

    chroma = calculate_chroma_vector([60, 64, 67], [1.0, 1.0, 1.0])
    checks.append(
        CheckResult(
            "property.chroma_sums_to_one",
            abs(float(np.sum(chroma)) - 1.0) < 1e-6,
            f"chroma sum={float(np.sum(chroma))}",
        )
    )

    from densidade_intervalar import calculate_interval_density

    d1 = calculate_interval_density(["C4", "D4"], lamb=0.05, use_optimization=False)
    d2 = calculate_interval_density(["C4", "G4"], lamb=0.05, use_optimization=False)
    checks.append(
        CheckResult(
            "property.interval_decays_with_distance",
            float(d1) > float(d2),
            f"C4-D4={d1:.4f}, C4-G4={d2:.4f}",
        )
    )

    return VerificationResult(
        synthetic_cases_run=len(cases),
        checks=checks,
        external_validation_available=False,
    )
