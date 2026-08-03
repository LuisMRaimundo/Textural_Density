"""Fail loudly when a scenario names an instrument absent from the registry."""

from __future__ import annotations

from instrumentos.registry import list_profiles, resolve_profile


def known_display_names() -> list[str]:
    return sorted({p.display_name for p in list_profiles()})


def require_instruments(names: list[str] | tuple[str, ...]) -> None:
    missing = [n for n in names if resolve_profile(n) is None]
    if missing:
        valid = ", ".join(known_display_names())
        raise SystemExit(
            f"Stress battery: unknown instrument(s) {missing!r}. "
            f"Valid registry display names: {valid}"
        )
