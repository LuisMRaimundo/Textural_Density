"""
Validation report generator (Phase 8).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from validation.schemas import load_expert_annotations
from validation.verification import VerificationResult, run_verification_suite

VALIDATION_ROOT = Path(__file__).resolve().parent
REPORTS_DIR = VALIDATION_ROOT / "reports"
EXPERT_DIR = VALIDATION_ROOT / "expert_annotations"
LISTENING_DIR = VALIDATION_ROOT / "listening_tests"
CORPUS_DIR = VALIDATION_ROOT / "corpus_examples"


def _count_json_lists(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    total = 0
    for path in directory.glob("*.json"):
        if path.name.startswith("example"):
            continue
        try:
            total += len(load_expert_annotations(path)) if directory == EXPERT_DIR else 1
        except (ValueError, OSError):
            continue
    return total


def generate_validation_report(
    *,
    verification: VerificationResult | None = None,
    output_path: str | Path | None = None,
) -> str:
    """
    Write validation report markdown and return its text.

    If no external validation corpora exist, states verified_only status explicitly.
    """
    verification = verification or run_verification_suite()
    output_path = Path(output_path or REPORTS_DIR / "validation_report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    expert_count = _count_json_lists(EXPERT_DIR)
    listening_count = len(list(LISTENING_DIR.glob("*.json"))) if LISTENING_DIR.is_dir() else 0
    corpus_count = len(list(CORPUS_DIR.glob("*"))) if CORPUS_DIR.is_dir() else 0

    failed = verification.failed_checks
    passed_count = sum(1 for c in verification.checks if c.passed)
    total_checks = len(verification.checks)

    lines = [
        "# Validation Report — Textural Density",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Status",
        "",
    ]

    if expert_count or listening_count:
        lines.append(
            "- **Empirical validation:** partial external data present (see tables below)."
        )
    else:
        lines.append(
            "- **Empirical validation:** No external validation data provided. "
            "**Current status: verified_only.**"
        )

    lines.extend(
        [
            "- **Verification:** synthetic cases and property checks (implementation correctness).",
            "- **Validation:** expert/listening/corpus comparison requires annotated data in "
            "`validation/` subfolders.",
            "",
            "## Verification summary",
            "",
            f"- Synthetic cases executed: **{verification.synthetic_cases_run}**",
            f"- Property/regression checks: **{passed_count}/{total_checks} passed**",
            "",
        ]
    )

    if failed:
        lines.append("### Failed checks")
        lines.append("")
        for check in failed:
            lines.append(f"- `{check.check_id}`: {check.message}")
        lines.append("")

    lines.extend(
        [
            "### Passed property checks (sample)",
            "",
        ]
    )
    for check in verification.checks:
        if check.passed and check.check_id.startswith("property."):
            lines.append(f"- `{check.check_id}`: {check.message}")
    lines.append("")

    lines.extend(
        [
            "## External data inventory",
            "",
            f"| Source | Files/records |",
            f"|--------|---------------|",
            f"| Expert annotations (`validation/expert_annotations/`) | {expert_count} |",
            f"| Listening tests (`validation/listening_tests/`) | {listening_count} |",
            f"| Corpus examples (`validation/corpus_examples/`) | {corpus_count} |",
            "",
            "## Known limitations",
            "",
            "- Score/information input only — no measured audio spectra or SPL.",
            "- Strictly symbolic analysis: no auditory, psychoacoustic, perceptual, or virtual-tone modelling.",
            "- Instrument profiles may be `coarse_default` with high uncertainty.",
            "- Lambda calibration validates one interval-decay component only.",
            "",
            "## Calibration residuals",
            "",
            "See `densidade_intervalar.calibrate_lambda` and `config/density_params.json`. "
            "Full model external validation pending annotated corpora.",
            "",
        ]
    )

    text = "\n".join(lines)
    output_path.write_text(text, encoding="utf-8")
    return text
