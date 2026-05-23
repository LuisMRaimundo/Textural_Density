"""
Score annotation schema validation (score-only symbolic validation line).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_RATING_DIMENSIONS = frozenset(
    {
        "overall_symbolic_vertical_density",
        "event_density",
        "interval_compactness",
        "registral_density",
        "orchestration_mass",
        "timbral_orchestration_complexity",
    }
)

REQUIRED_FIELDS = frozenset(
    {
        "corpus_id",
        "piece_id",
        "slice_id",
        "score_source",
        "input_file",
        "rater_id",
        "rating_dimension",
        "rating_value",
        "rating_scale_min",
        "rating_scale_max",
        "annotation_protocol_version",
    }
)


@dataclass
class ScoreAnnotation:
    corpus_id: str
    piece_id: str
    slice_id: str
    score_source: str
    input_file: str
    rater_id: str
    rating_dimension: str
    rating_value: float
    rating_scale_min: float
    rating_scale_max: float
    annotation_protocol_version: str
    composer: str = ""
    work_title: str = ""
    movement_or_section: str = ""
    measure: str | int | None = None
    beat: str | float | None = None
    rater_expertise: str = ""
    comments: str = ""
    date: str = ""
    fixture_label: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScoreAnnotation:
        missing = REQUIRED_FIELDS - set(data)
        if missing:
            raise ValueError(f"Missing required annotation fields: {sorted(missing)}")
        dim = str(data["rating_dimension"])
        if dim not in REQUIRED_RATING_DIMENSIONS:
            raise ValueError(f"Unknown rating_dimension: {dim}")
        lo = float(data["rating_scale_min"])
        hi = float(data["rating_scale_max"])
        val = float(data["rating_value"])
        if val < lo or val > hi:
            raise ValueError(f"rating_value {val} outside scale [{lo}, {hi}]")
        return cls(
            corpus_id=str(data["corpus_id"]),
            piece_id=str(data["piece_id"]),
            slice_id=str(data["slice_id"]),
            score_source=str(data["score_source"]),
            input_file=str(data["input_file"]),
            rater_id=str(data["rater_id"]),
            rating_dimension=dim,
            rating_value=val,
            rating_scale_min=lo,
            rating_scale_max=hi,
            annotation_protocol_version=str(data["annotation_protocol_version"]),
            composer=str(data.get("composer", "")),
            work_title=str(data.get("work_title", "")),
            movement_or_section=str(data.get("movement_or_section", "")),
            measure=data.get("measure"),
            beat=data.get("beat"),
            rater_expertise=str(data.get("rater_expertise", "")),
            comments=str(data.get("comments", "")),
            date=str(data.get("date", "")),
            fixture_label=str(data.get("fixture_label", "")),
        )

    @property
    def is_fixture(self) -> bool:
        return bool(self.fixture_label) or self.score_source == "synthetic_fixture"


def load_score_annotations(path: str | Path) -> list[ScoreAnnotation]:
    filepath = Path(path)
    if not filepath.exists():
        return []
    with open(filepath, encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, list):
        raise ValueError("Score annotations file must contain a JSON list")
    return [ScoreAnnotation.from_dict(item) for item in payload]


def validate_annotation_file(path: str | Path) -> tuple[list[ScoreAnnotation], list[str]]:
    """Load and validate; return (annotations, errors)."""
    errors: list[str] = []
    try:
        annotations = load_score_annotations(path)
        return annotations, errors
    except (ValueError, json.JSONDecodeError, TypeError) as exc:
        errors.append(str(exc))
        return [], errors
