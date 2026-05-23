"""
Pytest configuration and shared fixtures for test suite.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# Test data fixtures
@pytest.fixture
def sample_notes():
    """Sample musical notes for testing."""
    return ["C4", "E4", "G4", "C5"]


@pytest.fixture
def sample_notes_with_cents():
    """Sample notes with microtonal adjustments."""
    return ["C4", "C#4+50c", "E4", "G4"]


@pytest.fixture
def sample_dynamics():
    """Sample dynamics for testing."""
    return ["mf", "f", "ff", "mf"]


@pytest.fixture
def sample_instruments():
    """Sample instruments for testing."""
    return ["flauta", "clarinete", "flauta", "clarinete"]


@pytest.fixture
def sample_num_instruments():
    """Sample number of instruments."""
    return [1, 2, 1, 1]


@pytest.fixture
def sample_input_data(sample_notes, sample_dynamics, sample_instruments, sample_num_instruments):
    """Complete input data dictionary for testing."""
    return {
        "notes": sample_notes,
        "dynamics": sample_dynamics,
        "instruments": sample_instruments,
        "num_instruments": sample_num_instruments,
        "weight_factor": 0.5,
        "save_results": False,
        "show_graphs": False,
    }


@pytest.fixture
def sample_pitches():
    """Sample MIDI pitches for testing."""
    return [60.0, 64.0, 67.0, 72.0]  # C4, E4, G4, C5


@pytest.fixture
def sample_densities():
    """Sample density values for testing."""
    return np.array([1.0, 1.5, 1.2, 1.8])


@pytest.fixture
def tolerance():
    """Numerical tolerance for floating point comparisons."""
    return 1e-6


@pytest.fixture
def tolerance_large():
    """Larger tolerance for less precise calculations."""
    return 1e-3
