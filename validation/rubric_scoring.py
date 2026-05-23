"""
Score-only upgrade rubric scoring utilities.

Totals human-provided dimension scores only — does not infer validation status.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_DIMENSION_IDS = frozenset(
    {
        "score_only_scope",
        "formal_construct_axioms",
        "construct_separation",
        "benchmark_replication",
        "core_native_architecture",
        "orchestration_metadata_honesty",
        "testing_regression",
        "reporting_transparency",
    }
)

DEFAULT_RUBRIC_PATH = Path(__file__).resolve().parents[1] / "docs" / "score_only_upgrade_rubric.json"


@dataclass
class RubricScoreResult:
    total: float
    max_total: int
    interpretation: str
    dimension_scores: dict[str, float]
    dimension_weights: dict[str, int]
    rubric_version: str
    project_version: str | None
    date: str | None
    notes: dict[str, str]


def load_rubric(path: str | Path | None = None) -> dict[str, Any]:
    rubric_path = Path(path) if path else DEFAULT_RUBRIC_PATH
    with open(rubric_path, encoding="utf-8") as f:
        rubric = json.load(f)
    validate_rubric_structure(rubric)
    return rubric


def validate_rubric_structure(rubric: dict[str, Any]) -> None:
    if rubric.get("total_points") != 100:
        raise ValueError(f"total_points must be 100, got {rubric.get('total_points')}")
    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise ValueError("rubric must contain a non-empty dimensions list")
    weight_sum = 0
    seen_ids: set[str] = set()
    for dim in dimensions:
        dim_id = dim.get("id")
        weight = dim.get("weight")
        if not dim_id or not isinstance(weight, int):
            raise ValueError(f"invalid dimension entry: {dim}")
        if dim_id in seen_ids:
            raise ValueError(f"duplicate dimension id: {dim_id}")
        seen_ids.add(dim_id)
        weight_sum += weight
    if weight_sum != 100:
        raise ValueError(f"dimension weights must sum to 100, got {weight_sum}")
    missing = REQUIRED_DIMENSION_IDS - seen_ids
    if missing:
        raise ValueError(f"missing required dimension ids: {sorted(missing)}")


def _weights_map(rubric: dict[str, Any]) -> dict[str, int]:
    return {str(d["id"]): int(d["weight"]) for d in rubric["dimensions"]}


def validate_submission(rubric: dict[str, Any], submission: dict[str, Any]) -> dict[str, float]:
    """Validate and normalize scores; raise ValueError on invalid input."""
    if submission.get("rubric_version") and submission["rubric_version"] != rubric.get("rubric_version"):
        raise ValueError(
            f"rubric_version mismatch: submission={submission['rubric_version']} "
            f"rubric={rubric.get('rubric_version')}"
        )
    scores_raw = submission.get("scores")
    if not isinstance(scores_raw, dict):
        raise ValueError("submission must contain a scores object")
    weights = _weights_map(rubric)
    unknown = set(scores_raw) - set(weights)
    if unknown:
        raise ValueError(f"unknown dimension ids: {sorted(unknown)}")
    missing = set(weights) - set(scores_raw)
    if missing:
        raise ValueError(f"missing dimension scores: {sorted(missing)}")
    normalized: dict[str, float] = {}
    for dim_id, max_pts in weights.items():
        val = scores_raw[dim_id]
        if not isinstance(val, (int, float)):
            raise ValueError(f"score for {dim_id} must be numeric")
        fval = float(val)
        if fval < 0 or fval > max_pts:
            raise ValueError(f"score for {dim_id} must be in [0, {max_pts}], got {fval}")
        normalized[dim_id] = fval
    return normalized


def interpret_total(total: float, rubric: dict[str, Any]) -> str:
    bands = rubric.get("interpretation_bands", [])
    for band in bands:
        if band["min"] <= total <= band["max"]:
            return str(band["label"])
    return "Unknown band"


def score_submission(
    submission: dict[str, Any],
    *,
    rubric: dict[str, Any] | None = None,
    rubric_path: str | Path | None = None,
) -> RubricScoreResult:
    rubric_data = rubric if rubric is not None else load_rubric(rubric_path)
    dimension_scores = validate_submission(rubric_data, submission)
    weights = _weights_map(rubric_data)
    total = sum(dimension_scores.values())
    return RubricScoreResult(
        total=total,
        max_total=int(rubric_data["total_points"]),
        interpretation=interpret_total(total, rubric_data),
        dimension_scores=dimension_scores,
        dimension_weights=weights,
        rubric_version=str(rubric_data.get("rubric_version", "")),
        project_version=submission.get("project_version"),
        date=submission.get("date"),
        notes={k: str(v) for k, v in (submission.get("notes") or {}).items()},
    )


def format_markdown_summary(result: RubricScoreResult) -> str:
    lines = [
        "# Score-Only Upgrade Rubric Summary",
        "",
        f"- **Total:** {result.total:.0f} / {result.max_total}",
        f"- **Interpretation:** {result.interpretation}",
        f"- **Rubric version:** {result.rubric_version}",
    ]
    if result.project_version:
        lines.append(f"- **Project version:** {result.project_version}")
    if result.date:
        lines.append(f"- **Date:** {result.date}")
    lines.extend(["", "## Dimension scores", ""])
    for dim_id in sorted(result.dimension_scores):
        score = result.dimension_scores[dim_id]
        weight = result.dimension_weights[dim_id]
        note = result.notes.get(dim_id, "")
        line = f"- `{dim_id}`: {score:.0f} / {weight}"
        if note:
            line += f" — {note}"
        lines.append(line)
    lines.extend(
        [
            "",
            "_Human-assigned scores only. This summary does not infer validation status from repository state._",
        ]
    )
    return "\n".join(lines) + "\n"


def load_submission(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
