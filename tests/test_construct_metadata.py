"""Tests for construct-level metadata hooks."""

from __future__ import annotations

from core.construct_metadata import CONSTRUCT_MAP, build_construct_records
from core.defaults import apply_research_defaults
from data_processor import calculate_metrics


def test_all_seven_constructs_present():
    data = apply_research_defaults(
        {
            "notes": ["C4", "E4", "G4"],
            "dynamics": ["mf", "f", "ff"],
            "instruments": ["flauta", "clarinete", "oboe"],
            "num_instruments": [1, 2, 1],
        }
    )
    resultados, _, _ = calculate_metrics(data)
    records = resultados.get("construct_records", {})
    expected_ids = set(CONSTRUCT_MAP.values())
    assert expected_ids <= set(records.keys())


def test_construct_record_required_fields():
    data = apply_research_defaults(
        {
            "notes": ["C4", "E4", "G4"],
            "dynamics": ["mf"] * 3,
            "instruments": ["flauta"] * 3,
            "num_instruments": [1] * 3,
        }
    )
    resultados, _, _ = calculate_metrics(data)
    for construct_id, record in resultados["construct_records"].items():
        assert record["construct_id"] == construct_id
        assert "value" in record
        assert "source_type" in record
        assert "verification_status" in record
        assert "included_in_composite" in record
        assert "component_weight" in record
        assert "assumptions" in record
        assert "warnings" in record


def test_interval_compactness_not_in_orchestration_mass():
    data = apply_research_defaults(
        {
            "notes": ["C4", "E4", "G4"],
            "dynamics": ["pp", "ff", "ff"],
            "instruments": ["flauta"] * 3,
            "num_instruments": [1, 3, 1],
        }
    )
    r1, _, _ = calculate_metrics(data)
    r2, _, _ = calculate_metrics(
        apply_research_defaults(
            {
                **data,
                "dynamics": ["mf", "mf", "mf"],
                "num_instruments": [1, 1, 1],
            }
        )
    )
    ic1 = r1["construct_records"]["interval_compactness"]["value"]
    ic2 = r2["construct_records"]["interval_compactness"]["value"]
    assert ic1 == ic2
    om1 = r1["construct_records"]["orchestration_mass"]["value"]
    om2 = r2["construct_records"]["orchestration_mass"]["value"]
    assert om1 != om2


def test_composite_has_documented_weights():
    data = apply_research_defaults(
        {
            "notes": ["C4", "E4"],
            "dynamics": ["mf", "mf"],
            "instruments": ["flauta", "flauta"],
            "num_instruments": [1, 1],
        }
    )
    resultados, _, _ = calculate_metrics(data)
    composite = resultados["construct_records"]["composite_symbolic_density"]
    assert "documented_sensitivity_weights" in composite
    assert composite["included_in_composite"] is True


def test_build_construct_records_from_subindices():
    data = apply_research_defaults(
        {
            "notes": ["C4", "G4"],
            "dynamics": ["mf", "mf"],
            "instruments": ["flauta", "flauta"],
            "num_instruments": [1, 1],
        }
    )
    resultados, _, _ = calculate_metrics(data)
    rebuilt = build_construct_records(resultados["density_subindices"])
    assert set(rebuilt.keys()) == set(resultados["construct_records"].keys())
