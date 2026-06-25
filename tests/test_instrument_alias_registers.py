"""Alias resolution must map to the same canonical register profile."""

from __future__ import annotations

import pytest

from instrumentos.registry import REGISTRY, resolve_profile
from tests.instrument_register_audit import build_instrument_register_audit


@pytest.fixture(scope="module")
def alias_rows():
    return build_instrument_register_audit()["alias_resolution"]


def test_every_alias_resolves_to_canonical_id(alias_rows):
    for row in alias_rows:
        assert row["resolved_id"] == row["canonical_id"], (
            f"alias {row['alias']!r} resolved to {row['resolved_id']!r}, "
            f"expected {row['canonical_id']!r}"
        )


@pytest.mark.parametrize("instrument_id", sorted(REGISTRY.keys()))
def test_all_aliases_share_sounding_range(instrument_id):
    profile = REGISTRY[instrument_id]
    candidates = (profile.instrument_id, profile.display_name, *profile.aliases)
    for alias in candidates:
        resolved = resolve_profile(alias)
        assert resolved is profile
        assert resolved.sounding_range == profile.sounding_range
        assert resolved.comfortable_range == profile.comfortable_range


@pytest.mark.parametrize(
    "alias,expected_id",
    [
        ("violin", "violino"),
        ("Flute", "flauta"),
        ("bass_clarinet", "clarinete_baixo"),
        ("glockenspiel", "metalofone"),
        ("Contrabassoon", "contrafagote"),
        ("cor anglais", "cor_anglais"),
        ("double_bass", "contrabaixo"),
    ],
)
def test_documented_alias_resolution(alias, expected_id):
    profile = resolve_profile(alias)
    assert profile is not None
    assert profile.instrument_id == expected_id
