"""Module and table contracts for GPR string instruments."""

from __future__ import annotations

import importlib
import inspect
import logging
import math
import re
from pathlib import Path

import pytest

from instrumentos import get_instrument_module, get_instrument_profile
from instrumentos.provenance import InstrumentSource
from instrumentos.spectral_lookup import lookup_spectral_density_detailed
from microtonal import note_to_midi_strict
from tests.string_constants import SOURCE_DYNAMICS, STRING_INSTRUMENTS, StringInstrumentSpec

FLOAT_TOL = 1e-5
_WINDOWS_ABS_PATH = re.compile(r"^[A-Za-z]:[\\/]")


def _is_machine_local_source_path(identifier: str) -> bool:
    if not identifier or identifier.startswith("docs/"):
        return False
    if _WINDOWS_ABS_PATH.match(identifier):
        return True
    return Path(identifier).is_absolute() and not identifier.startswith("docs/")


def _load_module(spec: StringInstrumentSpec):
    return importlib.import_module(f"instrumentos.{spec.module_name}")


@pytest.mark.musicological
class TestStringModuleImportContract:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_module_surface(self, spec: StringInstrumentSpec):
        mod = _load_module(spec)
        assert hasattr(mod, "spectral_data") and mod.spectral_data
        assert hasattr(mod, "INSTRUMENT_SOURCE")
        assert callable(mod.calcular_densidade)
        assert callable(mod.predict_intermediate_dynamics)
        assert getattr(mod, "IS_COARSE_DEFAULT", False) is False

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_instrument_source_metadata(self, spec: StringInstrumentSpec):
        src: InstrumentSource = _load_module(spec).INSTRUMENT_SOURCE
        assert src.source_type == "external_acoustic_metadata"
        assert src.citation
        assert src.extraction_method
        assert src.dynamic_levels == SOURCE_DYNAMICS
        assert src.uncertainty in {"low", "medium", "high"}
        assert src.version
        assert src.pitch_range[0] < src.pitch_range[1]


@pytest.mark.musicological
class TestStringTableShape:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_documented_row_count_and_pitch_span(self, spec: StringInstrumentSpec):
        table = _load_module(spec).spectral_data
        notes = sorted(table.keys(), key=lambda n: note_to_midi_strict(n))
        assert len(notes) == spec.documented_row_count
        assert notes[0] == spec.documented_first_pitch
        assert notes[-1] == spec.documented_last_pitch

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_every_pitch_has_source_dynamics(self, spec: StringInstrumentSpec):
        table = _load_module(spec).spectral_data
        for pitch, dynamics in table.items():
            note_to_midi_strict(pitch)
            for dyn in SOURCE_DYNAMICS:
                assert dyn in dynamics
                val = dynamics[dyn]
                assert isinstance(val, (int, float))
                assert math.isfinite(val)
                assert val > 0.0

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_no_conflicting_midi_rows(self, spec: StringInstrumentSpec):
        table = _load_module(spec).spectral_data
        seen: dict[float, str] = {}
        for pitch in table:
            midi = float(note_to_midi_strict(pitch))
            if midi in seen and seen[midi] != pitch:
                pytest.fail(f"Duplicate MIDI {midi}: {seen[midi]!r} vs {pitch!r}")
            seen[midi] = pitch


@pytest.mark.musicological
class TestStringExactAnchorLookup:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_all_table_cells_match_calcular_densidade(self, spec: StringInstrumentSpec):
        mod = _load_module(spec)
        logger = logging.getLogger(f"test.string.anchor.{spec.module_name}")
        for pitch, dynamics in mod.spectral_data.items():
            for dyn, expected in dynamics.items():
                actual = mod.calcular_densidade(pitch, dyn)
                assert actual == pytest.approx(expected, abs=FLOAT_TOL)
                detail = lookup_spectral_density_detailed(
                    mod.spectral_data, pitch, dyn, logger=logger
                )
                assert detail.provenance in ("exact", "normalized_exact")
                assert detail.value == pytest.approx(expected, abs=FLOAT_TOL)


@pytest.mark.musicological
class TestStringRegistryResolution:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_aliases_resolve_to_dedicated_module(self, spec: StringInstrumentSpec):
        for alias in spec.registry_ids:
            profile = get_instrument_profile(alias)
            assert profile.module_name == spec.module_name
            assert profile.profile_status == "literature_derived"
            mod = get_instrument_module(alias)
            assert mod.calcular_densidade is _load_module(spec).calcular_densidade

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_open_string_pitches_lookup(self, spec: StringInstrumentSpec):
        mod = get_instrument_module(spec.registry_ids[0])
        for pitch in spec.open_strings:
            assert pitch in mod.spectral_data
            assert math.isfinite(mod.calcular_densidade(pitch, "mf"))


@pytest.mark.musicological
class TestStringTechniqueHonesty:
    """Registry lists extended techniques; committed tables represent arco sustains."""

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_calcular_densidade_has_no_technique_parameter(self, spec: StringInstrumentSpec):
        sig = inspect.signature(_load_module(spec).calcular_densidade)
        assert list(sig.parameters) == ["nota", "dinamica"]

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_registry_lists_arco_among_supported_techniques(self, spec: StringInstrumentSpec):
        profile = get_instrument_profile(spec.registry_ids[0])
        assert "arco" in profile.supported_techniques


@pytest.mark.musicological
class TestStringProvenancePortability:
    KNOWN_LOCAL_PATH_MODULES = frozenset({"viola"})

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_source_identifier_portability(self, spec: StringInstrumentSpec):
        src = _load_module(spec).INSTRUMENT_SOURCE
        identifier = src.source_url_or_identifier or ""
        is_local_path = _is_machine_local_source_path(identifier)
        if spec.module_name in self.KNOWN_LOCAL_PATH_MODULES:
            assert is_local_path, "viola expected to document known local workbook path"
            return
        assert not is_local_path, f"{spec.module_name} should not use machine-local path"
        assert identifier.startswith("docs/")
