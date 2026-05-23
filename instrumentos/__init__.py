# instrumentos/__init__.py
"""
Orchestral instrument modules and registry.

Dedicated scripts (``flauta``, ``clarinete``, ``oboe``) embed sparse amplitude
tables from **external acoustic sources**, loaded at import time and queried
during score analysis — the pipeline does not analyse audio waveforms.
"""

import importlib
import logging
import os
from types import ModuleType
from typing import Union

from instrumentos.registry import (
    InstrumentProfile,
    list_instrument_ids,
    list_profiles,
    resolve_profile,
)

logger = logging.getLogger("instrumentos")

_available_instruments: dict[str, Union[ModuleType, object]] = {}

_instruments_dir = os.path.dirname(__file__)
for filename in os.listdir(_instruments_dir):
    if filename.endswith(".py") and filename not in (
        "__init__.py",
        "registry.py",
        "coarse_default.py",
        "metadata_audit.py",
        "provenance.py",
    ):
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f".{module_name}", package=__name__)
            _available_instruments[module_name] = module
            logger.info("Instrument module loaded: %s", module_name)
        except ImportError as exc:
            logger.warning("Could not import module %s: %s", module_name, exc)


def _coarse_cache_key(instrument_id: str) -> str:
    return f"__coarse__:{instrument_id}"


def get_instrument_profile(instrument_name: str) -> InstrumentProfile:
    from instrumentos.registry import profile_for_event

    return profile_for_event(instrument_name)


def get_instrument_module(instrument_name: str):
    """
    Return the module for the given instrument.

    Resolution order:
    1. Registry alias → dedicated module if ``module_name`` is set and importable
    2. Registry → coarse-default module bound to profile
    3. Direct module import by raw name (legacy)
    """
    profile = resolve_profile(instrument_name)
    if profile is not None:
        if profile.module_name and profile.module_name in _available_instruments:
            return _available_instruments[profile.module_name]
        cache_key = _coarse_cache_key(profile.instrument_id)
        if cache_key not in _available_instruments:
            from instrumentos.coarse_default import build_coarse_module

            _available_instruments[cache_key] = build_coarse_module(profile)
        return _available_instruments[cache_key]

    raw = instrument_name.strip().lower()
    if raw in _available_instruments:
        return _available_instruments[raw]
    try:
        module = importlib.import_module(f".{raw}", package=__name__)
        _available_instruments[raw] = module
        return module
    except ImportError as exc:
        from instrumentos.registry import profile_for_event
        from instrumentos.coarse_default import build_coarse_module

        fallback = profile_for_event(instrument_name)
        cache_key = _coarse_cache_key(fallback.instrument_id)
        if cache_key not in _available_instruments:
            _available_instruments[cache_key] = build_coarse_module(fallback)
        logger.warning(
            "Instrument '%s' not registered; using unknown coarse proxy.",
            instrument_name,
        )
        return _available_instruments[cache_key]


# Registered + dedicated module names (legacy list)
available_instruments = sorted(
    set(list(_available_instruments.keys()) + list_instrument_ids())
)


__all__ = [
    "available_instruments",
    "get_instrument_module",
    "get_instrument_profile",
    "list_instrument_ids",
    "list_profiles",
    "resolve_profile",
]
