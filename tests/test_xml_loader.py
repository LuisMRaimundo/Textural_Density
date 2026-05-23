"""
Unit tests for xml_loader (Phase 4.1).

Tests note_string_to_gui_parts and parse_xml with a small fixture.
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from xml_loader import note_string_to_gui_parts, parse_xml


class TestNoteStringToGuiParts:
    """Test conversion of note string to GUI (base, octave, cents)."""

    def test_simple_note(self):
        base, octave, cents = note_string_to_gui_parts("C4")
        assert base in ("C", "C♯")  # may be Unicode sharp
        assert octave == "4"
        assert cents == "0" or cents == "+0"

    def test_sharp_note(self):
        base, octave, cents = note_string_to_gui_parts("C#4")
        assert "C" in base and "4" in octave

    def test_with_cents(self):
        base, octave, cents = note_string_to_gui_parts("C#4+25c")
        assert octave == "4"
        assert "25" in cents

    def test_empty_defaults(self):
        base, octave, cents = note_string_to_gui_parts("")
        assert base == "C" and octave == "4" and cents == "0"


class TestParseXml:
    """Test XML parsing (custom densidade_analysis format)."""

    def test_parse_custom_densidade_xml(self):
        # Use example file from project for reliable parsing (same format as GUI)
        example_path = Path(__file__).parent.parent / "exemplo_densidade.xml"
        if not example_path.exists():
            pytest.skip("exemplo_densidade.xml not found")
        data = parse_xml(str(example_path))
        assert "notes" in data
        assert len(data["notes"]) >= 1
        assert data["notes"][0] == "C4"
        assert len(data["dynamics"]) == len(data["notes"])
        assert len(data["instruments"]) == len(data["notes"])
        assert len(data["num_instruments"]) == len(data["notes"])
        assert all(1 <= n <= 20 for n in data["num_instruments"])
        assert "weight_factor" in data

    def test_parse_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_xml("/nonexistent/path/file.xml")

    def test_parse_minimal_xml_fixture(self):
        """Parse minimal in-memory XML to ensure structure is read (notes may be defaulted)."""
        xml_content = '<?xml version="1.0"?><densidade_analysis><voices>'
        xml_content += "<voice><note>C4</note><dynamics>mf</dynamics><instrument>Flauta</instrument><num_instruments>1</num_instruments></voice>"
        xml_content += "</voices></densidade_analysis>"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            path = f.name
        try:
            data = parse_xml(path)
            assert data["notes"] == ["C4"]
            assert data["dynamics"] == ["mf"]
            assert data["num_instruments"] == [1]
        finally:
            Path(path).unlink(missing_ok=True)
