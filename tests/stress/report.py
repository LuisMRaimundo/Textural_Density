"""Markdown report writer for the stress battery."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import MAX_DENS_GLOBAL
from core import get_package_version
from tests.stress.engine import AssertionResult, SliceResult, _get, by_id, git_hash
from tests.stress.scenarios import WEIGHT

FAMILY_TITLES = {
    "A": "A. Pitched-only baselines",
    "B": "B. Percussion-only",
    "C": "C. Mixed aggregates",
    "D": "D. Degenerate and adversarial",
    "E": "E. Invariance and consistency properties",
}

FAMILY_INTERP = {
    "A": (
        "Family A isolates instrument CDM, unison Qty (mass without pitch growth), "
        "chordal cardinality, and registral span at fixed pitch-class cardinality. "
        "Together these establish the pitched baseline against which mixed and "
        "percussion-only regimes are compared."
    ),
    "B": (
        "Family B verifies unpitched-only routing: pitch metrics stay at zero, "
        "spectral blocks report n/a, and the blend collapses to the weighted "
        "orchestral term (DV = 0) while composite follows the unified log path. "
        "The tam-tam dynamics ladder records the mf→ff cascade discontinuity."
    ),
    "C": (
        "Family C is analytically central: percussion additions to a pitched core, "
        "the mass-vs-component-count compression probe (C2), a fixed-player "
        "unpitched-share sweep, permutation invariance, and a realistic tutti "
        "comparison with/without the percussion battery."
    ),
    "D": (
        "Family D stresses empty input, minimum nonzero unpitched, extreme Qty, "
        "microtonal cardinality, cross-instrument unison, dynamic extremes, and "
        "musically unreal percussion Qty — confirming graceful failure or "
        "numerical sanity rather than musical plausibility."
    ),
    "E": (
        "Family E encodes standing contracts as assertions: random-addition "
        "monotonicity, pitch-metric invariance when unpitched events are removed, "
        "Qty scaling (pitch fixed, mass linear), printed-header formula self-check, "
        "and whole-battery determinism via CSV hash."
    ),
}

SCOPE_NOTES = [
    (
        "(i) Mass-vs-component-count semantics of percussion aggregation: "
        "composite may treat a loud unpitched addition as comparable in mass terms "
        "to adding another pitched voice; C2 documents the size of this seam rather "
        "than adjudicating which semantics is 'correct'."
    ),
    (
        "(ii) Cross-family ratio validity pending calibration: absolute ratios of "
        "composites across pitched-only, unpitched-only, and mixed regimes are "
        "reported for inspection but are not treated as calibrated perceptual "
        "equivalences."
    ),
    (
        "(iii) Per-player means may legitimately move opposite to totals: "
        "`average_texture_density` is a Qty-weighted mean CDM and may fall when "
        "low-CDM instruments are added or rise under Qty expansion toward "
        "high-CDM instruments; monotone quantities are Sonic Mass, RSS, and Composite."
    ),
]


def _table_rows(family_results: list[SliceResult]) -> list[str]:
    lines = [
        "| Slice id | Summary | DI (interval) | RSS | Mass | Composite | Events | Players | Distinct |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in family_results:
        if r.spec.get("expect_error"):
            lines.append(
                f"| `{r.spec['id']}` | {r.spec['summary']} | — | — | — | — | "
                f"error | — | — |"
            )
            continue
        if not r.ok or not r.resultados:
            lines.append(
                f"| `{r.spec['id']}` | {r.spec['summary']} | FAIL | — | — | — | "
                f"— | — | — |"
            )
            continue
        di = float(_get(r, "density", "interval", default=0))
        rss = float(_get(r, "density", "instrument", default=0))
        mass = float(_get(r, "density", "sonic_mass", default=0))
        tot = float(_get(r, "density", "total", default=0))
        ev = int(_get(r, "pitch_aggregation", "event_count", default=0))
        pl = int(_get(r, "pitch_aggregation", "player_count", default=0))
        dist = int(_get(r, "pitch_aggregation", "distinct_pitch_count", default=0))
        lines.append(
            f"| `{r.spec['id']}` | {r.spec['summary']} | {di:.4f} | {rss:.4f} | "
            f"{mass:.4f} | {tot:.4f} | {ev} | {pl} | {dist} |"
        )
    return lines


def write_report(
    *,
    results: list[SliceResult],
    asserts: list[AssertionResult],
    figure_paths: dict[str, Path],
    seed: int,
    e1_trials: int,
    csv_path: Path,
    report_path: Path,
    determinism_ok: bool | None,
    elapsed_s: float,
) -> None:
    n_pass = sum(1 for a in asserts if a.passed)
    n_fail = sum(1 for a in asserts if not a.passed)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    lines.append("# Stress Test Report — Textural Density")
    lines.append("")
    lines.append("## Header")
    lines.append("")
    lines.append(f"- **Tool version:** {get_package_version()}")
    lines.append(f"- **Git hash:** `{git_hash()}`")
    lines.append(f"- **weight_factor (w):** {WEIGHT}")
    lines.append(f"- **REF (`MAX_DENS_GLOBAL`):** {MAX_DENS_GLOBAL:g}")
    lines.append(f"- **Date:** {date}")
    lines.append(f"- **Battery seed:** {seed}")
    lines.append(f"- **E1 trials:** {e1_trials}")
    lines.append(f"- **Slices run:** {len(results)}")
    lines.append(f"- **Assertions:** {n_pass} passed / {n_fail} failed / {len(asserts)} total")
    lines.append(f"- **Wall time:** {elapsed_s:.1f}s")
    lines.append(f"- **CSV:** `{csv_path.name}`")
    if determinism_ok is not None:
        lines.append(
            f"- **E5 determinism (repeat CSV hash):** "
            f"{'PASS' if determinism_ok else 'FAIL'}"
        )
    lines.append("")

    idx = by_id(results)
    for fam in ("A", "B", "C", "D", "E"):
        lines.append(f"## {FAMILY_TITLES[fam]}")
        lines.append("")
        fam_slices = [r for r in results if r.spec["family"] == fam]
        if fam_slices:
            lines.extend(_table_rows(fam_slices))
            lines.append("")
        fam_asserts = [a for a in asserts if a.family == fam]
        if fam_asserts:
            lines.append("| Assertion | Result | Detail |")
            lines.append("|---|---|---|")
            for a in fam_asserts:
                # Collapse per-slice E4 / run noise into summary for E4
                mark = "PASS" if a.passed else "FAIL"
                lines.append(f"| `{a.name}` | **{mark}** | {a.detail} |")
            lines.append("")
        lines.append(FAMILY_INTERP[fam])
        lines.append("")

        # Prominent C2 paragraph
        if fam == "C" and "C2_quartet_plus_tamtam_ffff" in idx:
            r_tt = idx["C2_quartet_plus_tamtam_ffff"]
            r_q5 = idx.get("C2_quintet_fifth_string")
            if r_tt.ok and r_q5 and r_q5.ok:
                t_tt = float(_get(r_tt, "density", "total"))
                t_q5 = float(_get(r_q5, "density", "total"))
                lines.append("### C2 — Compression probe (prominent)")
                lines.append("")
                lines.append(
                    f"Quartet + Tam-tam ffff composite = **{t_tt:.6f}**; "
                    f"quintet (fifth string instead) composite = **{t_q5:.6f}**; "
                    f"difference (tam-tam − quintet) = **{t_tt - t_q5:.6f}**."
                )
                lines.append("")
                lines.append(
                    "Under **mass semantics** these two aggregates may be near-equal "
                    "(or the percussion side even larger) because a loud unpitched "
                    "stroke contributes substantial CDM/mass. Under **component-count "
                    "semantics** the tam-tam side is 'fatter' by one non-pitched event "
                    "without adding pitch structure. The battery documents the size of "
                    "this seam rather than judging which reading is correct."
                )
                lines.append("")

        if fam == "A" and "A2" in figure_paths:
            lines.append(f"![A2 doubling curve]({figure_paths['A2'].as_posix()})")
            lines.append("")
        if fam == "B" and "B3" in figure_paths:
            lines.append(f"![B3 dynamics ladder]({figure_paths['B3'].as_posix()})")
            lines.append("")
        if fam == "C" and "C3" in figure_paths:
            lines.append(f"![C3 percussion fraction sweep]({figure_paths['C3'].as_posix()})")
            lines.append("")
        if fam == "C" and "C5" in figure_paths:
            lines.append(f"![C5 tutti comparison]({figure_paths['C5'].as_posix()})")
            lines.append("")

    # Collapse E4 rows in findings only — keep full table above but maybe too long.
    # Actually E4 per-slice makes a huge table. Let me rewrite report to summarize E4.

    lines.append("## FINDINGS")
    lines.append("")
    findings = [a for a in asserts if not a.passed]
    caveats = [
        a
        for a in asserts
        if a.passed
        and a.name
        in {
            "C2_compression_probe_documented",
            "B3_mf_to_ff_jump_recorded",
            "D7_absurd_qty_finite",
        }
    ]
    if not findings:
        lines.append(f"No findings: all {len(asserts)} assertions passed.")
        lines.append("")
    else:
        lines.append("| Severity | Slice / assertion | Expected vs observed |")
        lines.append("|---|---|---|")
        for a in findings:
            lines.append(
                f"| **{a.severity}** | `{a.slice_id or a.name}` / `{a.name}` | {a.detail} |"
            )
        lines.append("")

    if caveats:
        lines.append("### Documented caveats (not failures)")
        lines.append("")
        for a in caveats:
            lines.append(f"- `{a.name}`: {a.detail}")
        lines.append("")

    lines.append("## SCOPE NOTES")
    lines.append("")
    lines.append(
        "The battery deliberately does **not** adjudicate the following standing "
        "caveats (restated for methods-chapter readers):"
    )
    lines.append("")
    for note in SCOPE_NOTES:
        lines.append(f"- {note}")
    lines.append("")

    lines.append("## Reproduction")
    lines.append("")
    lines.append("```bash")
    lines.append("python run_stress_battery.py")
    lines.append("```")
    lines.append("")
    lines.append(
        "Optional: `python run_stress_battery.py --e1-trials 50 --seed 42` "
        "(adjusts E1 trial count / RNG seed). "
        "Regenerates `STRESS_TEST_REPORT.md`, `stress_results.csv`, and `stress_figures/`."
    )
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def summarize_e4(asserts: list[AssertionResult]) -> list[AssertionResult]:
    """Collapse per-slice E4 assertions into one summary row for the report table."""
    e4 = [a for a in asserts if a.name.startswith("E4_header_")]
    others = [a for a in asserts if not a.name.startswith("E4_header_")]
    if not e4:
        return asserts
    n_fail = sum(1 for a in e4 if not a.passed)
    others.append(
        AssertionResult(
            "E",
            "E4_header_formula_self_check_all_slices",
            n_fail == 0,
            f"slices={len(e4)} failures={n_fail}",
        )
    )
    return others
