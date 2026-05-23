"""
Expert annotation schema (Phase 8 validation scaffolding).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ExpertAnnotation:
    example_id: str
    score_source: str
    slice_time: Optional[float]
    rater_id: str
    rating_dimension: str
    rating_value: float
    rating_scale: str
    comments: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExpertAnnotation:
        return cls(
            example_id=str(data["example_id"]),
            score_source=str(data.get("score_source", "")),
            slice_time=float(data["slice_time"]) if data.get("slice_time") is not None else None,
            rater_id=str(data.get("rater_id", "anonymous")),
            rating_dimension=str(data["rating_dimension"]),
            rating_value=float(data["rating_value"]),
            rating_scale=str(data.get("rating_scale", "unknown")),
            comments=str(data.get("comments", "")),
        )


REQUIRED_FIELDS = {
    "example_id",
    "rating_dimension",
    "rating_value",
}


def load_expert_annotations(path: str | Path) -> list[ExpertAnnotation]:
    """Load expert annotations from a JSON list file."""
    filepath = Path(path)
    if not filepath.exists():
        return []
    with open(filepath, encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, list):
        raise ValueError("Expert annotations file must contain a JSON list")
    annotations: list[ExpertAnnotation] = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Annotation at index {idx} is not an object")
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(f"Annotation at index {idx} missing fields: {sorted(missing)}")
        annotations.append(ExpertAnnotation.from_dict(item))
    return annotations
