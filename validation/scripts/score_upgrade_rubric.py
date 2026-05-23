#!/usr/bin/env python3
"""
Compute total score and interpretation band from human-assigned rubric dimension scores.

Does not infer validation status or auto-score the repository.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.rubric_scoring import (
    format_markdown_summary,
    load_rubric,
    load_submission,
    score_submission,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score Densidade Vertical upgrades using the score-only rubric."
    )
    parser.add_argument(
        "scores_file",
        help="JSON file with rubric_version and scores object",
    )
    parser.add_argument(
        "--rubric",
        default=str(ROOT / "docs" / "score_only_upgrade_rubric.json"),
        help="Path to rubric JSON (default: docs/score_only_upgrade_rubric.json)",
    )
    parser.add_argument(
        "--markdown",
        help="Optional path to write Markdown summary",
    )
    args = parser.parse_args()

    rubric = load_rubric(args.rubric)
    submission = load_submission(args.scores_file)
    result = score_submission(submission, rubric=rubric)

    print(f"Total: {result.total:.0f} / {result.max_total}")
    print(f"Interpretation: {result.interpretation}")
    print(f"Rubric version: {result.rubric_version}")
    for dim_id in sorted(result.dimension_scores):
        w = result.dimension_weights[dim_id]
        s = result.dimension_scores[dim_id]
        print(f"  {dim_id}: {s:.0f}/{w}")

    if args.markdown:
        out = Path(args.markdown)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(format_markdown_summary(result), encoding="utf-8")
        print(f"Wrote {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
