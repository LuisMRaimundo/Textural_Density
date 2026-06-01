"""
Tests for score-only upgrade rubric JSON and scoring helper (v2.0.0).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from validation.rubric_scoring import (
    REQUIRED_DIMENSION_IDS,
    format_markdown_summary,
    interpret_total,
    load_rubric,
    score_submission,
    validate_rubric_structure,
    validate_submission,
)

ROOT = Path(__file__).resolve().parents[1]
RUBRIC_PATH = ROOT / "docs" / "score_only_upgrade_rubric.json"
RUBRIC_MD_PATH = ROOT / "docs" / "score_only_upgrade_rubric.md"
EXAMPLE_PATH = ROOT / "docs" / "examples" / "score_only_rubric_scores_example.json"

FORBIDDEN_MANDATORY_PHRASES = [
    "required expert annotations",
    "required listening tests",
    "required psychoacoustic validation",
    "90+ requires external ratings",
]

OPTIONAL_SECTION_HEADER = "## Optional empirical extensions"


@pytest.fixture
def rubric():
    return load_rubric(RUBRIC_PATH)


class TestRubricJson:
    def test_rubric_loads_v2(self, rubric):
        assert rubric["rubric_version"] == "2.0.0"
        assert rubric["research_line"] == "score_only_systematic_symbolic_analysis"

    def test_weights_sum_to_100(self, rubric):
        total = sum(d["weight"] for d in rubric["dimensions"])
        assert total == 100
        assert rubric["total_points"] == 100

    def test_all_required_dimension_ids_exist(self, rubric):
        ids = {d["id"] for d in rubric["dimensions"]}
        assert REQUIRED_DIMENSION_IDS <= ids

    def test_external_score_validation_dimension_absent(self, rubric):
        ids = {d["id"] for d in rubric["dimensions"]}
        assert "external_score_validation" not in ids

    def test_formal_construct_axioms_dimension_present(self, rubric):
        ids = {d["id"] for d in rubric["dimensions"]}
        assert "formal_construct_axioms" in ids
        axioms = next(d for d in rubric["dimensions"] if d["id"] == "formal_construct_axioms")
        assert axioms["weight"] == 15

    def test_no_dimension_requires_expert_ratings(self, rubric):
        blob = json.dumps(rubric).lower()
        for dim in rubric["dimensions"]:
            dim_blob = json.dumps(dim).lower()
            assert "expert annotation" not in dim_blob or "optional" in blob
            assert "inter-rater" not in dim_blob
            assert "listening test" not in dim_blob
        assert "external_score_validation" not in blob

    def test_no_dimension_requires_psychoacoustic_tests(self, rubric):
        for dim in rubric["dimensions"]:
            dim_blob = json.dumps(dim).lower()
            assert "psychoacoustic test" not in dim_blob
            assert "listening test" not in dim_blob


class TestRubricMandatoryLanguage:
    def test_rubric_md_no_forbidden_mandatory_phrases_outside_optional_section(self):
        text = RUBRIC_MD_PATH.read_text(encoding="utf-8")
        if OPTIONAL_SECTION_HEADER in text:
            mandatory_part = text.split(OPTIONAL_SECTION_HEADER)[0]
        else:
            mandatory_part = text
        lowered = mandatory_part.lower()
        for phrase in FORBIDDEN_MANDATORY_PHRASES:
            assert phrase not in lowered, f"Forbidden mandatory phrase found: {phrase}"

    def test_rubric_json_optional_extensions_marked(self, rubric):
        assert "optional_empirical_extensions" in rubric
        assert "expert_score_annotations" in rubric["optional_empirical_extensions"]


class TestRubricScoring:
    def test_compute_total_for_fixture(self, rubric):
        submission = {
            "rubric_version": "2.0.0",
            "scores": {dim: 5 for dim in REQUIRED_DIMENSION_IDS},
        }
        result = score_submission(submission, rubric=rubric)
        assert result.total == pytest.approx(40.0)
        assert result.interpretation == "Prototype / incomplete formalization"

    def test_interpretation_band_75_84(self, rubric):
        assert interpret_total(80, rubric) == (
            "Strong systematic score-analysis software with good tests and documentation; "
            "remaining gaps in corpus, architecture, or construct formalization"
        )

    def test_interpretation_band_90_plus(self, rubric):
        assert interpret_total(92, rubric) == (
            "Publication-grade systematic score-analysis method with auditable core pipeline, "
            "stable benchmark corpus, frozen outputs, and fully documented constructs"
        )
        assert "expert" not in interpret_total(92, rubric).lower()
        assert "listening" not in interpret_total(92, rubric).lower()

    def test_rejects_score_above_weight(self, rubric):
        submission = {
            "scores": {
                "score_only_scope": 11,
                "formal_construct_axioms": 0,
                "construct_separation": 0,
                "benchmark_replication": 0,
                "core_native_architecture": 0,
                "orchestration_metadata_honesty": 0,
                "testing_regression": 0,
                "reporting_transparency": 0,
            }
        }
        with pytest.raises(ValueError, match="score_only_scope"):
            validate_submission(rubric, submission)

    def test_rejects_old_external_score_validation_dimension(self, rubric):
        submission = {
            "scores": {
                "score_only_scope": 5,
                "construct_separation": 5,
                "external_score_validation": 5,
                "benchmark_replication": 5,
                "core_native_architecture": 5,
                "orchestration_metadata_honesty": 5,
                "testing_regression": 5,
                "reporting_transparency": 5,
            }
        }
        with pytest.raises(ValueError, match="unknown dimension|missing dimension"):
            validate_submission(rubric, submission)

    def test_markdown_summary_includes_disclaimer(self, rubric):
        submission = {"scores": {dim: 1 for dim in REQUIRED_DIMENSION_IDS}}
        result = score_submission(submission, rubric=rubric)
        md = format_markdown_summary(result)
        assert "does not infer validation status" in md.lower()


class TestExampleScoresFile:
    def test_example_is_labelled_illustrative(self):
        with open(EXAMPLE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        disclaimer = str(data.get("_disclaimer", "")).lower()
        assert "illustrative" in disclaimer
        assert "not an official" in disclaimer

    def test_example_uses_rubric_v2(self):
        with open(EXAMPLE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        assert data["rubric_version"] == "2.0.0"
        assert "external_score_validation" not in data.get("scores", {})

    def test_example_does_not_penalize_missing_expert_ratings(self, rubric):
        with open(EXAMPLE_PATH, encoding="utf-8") as f:
            submission = json.load(f)
        result = score_submission(submission, rubric=rubric)
        notes_blob = json.dumps(result.notes).lower()
        assert "expert" not in notes_blob or "optional" in notes_blob or "axiom" in notes_blob
        assert "external_score_validation" not in submission.get("scores", {})

    def test_example_scores_compute(self, rubric):
        with open(EXAMPLE_PATH, encoding="utf-8") as f:
            submission = json.load(f)
        result = score_submission(submission, rubric=rubric)
        expected = float(sum(submission["scores"].values()))
        assert result.total == pytest.approx(expected)


class TestRubricStructureValidation:
    def test_invalid_weight_sum_raises(self):
        bad = {
            "total_points": 100,
            "dimensions": [
                {"id": "score_only_scope", "weight": 10},
                {"id": "formal_construct_axioms", "weight": 10},
            ],
        }
        with pytest.raises(ValueError, match="sum to 100"):
            validate_rubric_structure(bad)
