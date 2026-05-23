"""
Instrument registry metadata audit — epistemic honesty for profile provenance.
"""

from __future__ import annotations

from typing import Any

from instrumentos.registry import REGISTRY, list_profiles, profile_for_event, resolve_profile

# Map registry statuses to audit vocabulary (no registry formula changes).
_STATUS_AUDIT_MAP = {
    "coarse_default": "symbolic_default",
    "symbolic_default": "symbolic_default",
    "literature_derived": "literature_informed",
    "literature_informed": "literature_informed",
    "empirical_source": "empirical_profile",
    "empirical_profile": "empirical_profile",
}


def audit_profile_status(raw_status: str) -> str:
    return _STATUS_AUDIT_MAP.get(raw_status, "unknown_needs_review")


def audit_instrument_profile(profile: Any) -> dict[str, Any]:
    status = audit_profile_status(profile.profile_status)
    uncertainty = profile.uncertainty if profile.uncertainty else "unknown"
    empirical_claim = status == "empirical_profile"
    has_source = bool(profile.source_notes and profile.source_notes.strip())
    if empirical_claim and not has_source:
        status = "unknown_needs_review"

    return {
        "instrument_id": profile.instrument_id,
        "display_name": profile.display_name,
        "family": profile.family,
        "profile_status": status,
        "registry_profile_status": profile.profile_status,
        "uncertainty": uncertainty,
        "source_notes": profile.source_notes,
        "limitations": list(profile.missing_data_warnings),
        "has_range_metadata": profile.sounding_range != (0.0, 0.0),
        "has_register_metadata": bool(profile.register_bands),
        "has_dynamic_weight_metadata": bool(profile.default_dynamic_response_curve),
        "has_technique_metadata": bool(profile.supported_techniques),
        "warnings": list(profile.missing_data_warnings),
        "claims_empirical_without_notes": empirical_claim and not has_source,
    }


def build_instrument_metadata_audit() -> dict[str, Any]:
    profiles = [audit_instrument_profile(p) for p in list_profiles()]
    unknown_fallback = audit_instrument_profile(profile_for_event("__nonexistent_test_instrument__"))
    needs_review = [
        p["instrument_id"]
        for p in profiles
        if p["profile_status"] in ("unknown_needs_review", "symbolic_default")
        and p["uncertainty"] in ("high", "unknown")
    ]
    return {
        "audit_version": "1.0.0",
        "instrument_count": len(profiles),
        "profiles": profiles,
        "unknown_instrument_fallback": unknown_fallback,
        "instruments_needing_review": sorted(set(needs_review)),
        "disclaimer": (
            "Instrument registry audit. GPR-backed modules use externally sourced acoustic "
            "amplitude metadata (sparse tables, not runtime audio). Coarse profiles lack "
            "such tables. profile_status=empirical_profile requires documented source_notes."
        ),
    }


def resolve_audit_for_name(name: str) -> dict[str, Any] | None:
    profile = resolve_profile(name)
    if profile is None:
        return None
    return audit_instrument_profile(profile)
