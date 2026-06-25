"""Shared constants for string-instrument musicological test batteries."""

from __future__ import annotations

from dataclasses import dataclass

SOURCE_DYNAMICS = ("pp", "mf", "ff")


@dataclass(frozen=True)
class StringInstrumentSpec:
    module_name: str
    registry_ids: tuple[str, ...]
    documented_row_count: int
    documented_first_pitch: str
    documented_last_pitch: str
    open_strings: tuple[str, ...]
    workbook_path: str


STRING_INSTRUMENTS: tuple[StringInstrumentSpec, ...] = (
    StringInstrumentSpec(
        module_name="violin",
        registry_ids=("violino", "violin"),
        documented_row_count=49,
        documented_first_pitch="G3",
        documented_last_pitch="G7",
        open_strings=("G3", "D4", "A4", "E5"),
        workbook_path=r"D:\CORDAS\VIOLIN_Zenodo_collections_media.xlsx",
    ),
    StringInstrumentSpec(
        module_name="viola",
        registry_ids=("viola",),
        documented_row_count=49,
        documented_first_pitch="C2",
        documented_last_pitch="C6",
        open_strings=("C3", "G3", "D4", "A4"),
        workbook_path=r"D:\CORDAS\ViOLA_Zenodo_collections_media.xlsx",
    ),
    StringInstrumentSpec(
        module_name="cello",
        registry_ids=("violoncelo", "cello", "violoncello"),
        documented_row_count=49,
        documented_first_pitch="C2",
        documented_last_pitch="C6",
        open_strings=("C2", "G2", "D3", "A3"),
        workbook_path=r"D:\CORDAS\CELLO_Zenodo_collections_media.xlsx",
    ),
    StringInstrumentSpec(
        module_name="double_bass",
        registry_ids=("contrabaixo", "double_bass", "contrabass"),
        documented_row_count=45,
        documented_first_pitch="E1",
        documented_last_pitch="C5",
        open_strings=("E1", "A1", "D2", "G2"),
        workbook_path=r"D:\CORDAS\DOUBLEBASS_Zenodo_collections_media.xlsx",
    ),
)

STRING_MODULE_NAMES = tuple(s.module_name for s in STRING_INSTRUMENTS)
