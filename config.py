# config.py
# Centralized configuration for the application.
# Mathematical models, formulas, and tutorial: docs/MATHEMATICAL_MANUAL.md

import os
from typing import Any, Dict, List, Tuple

# -------------------------------------------------------------------
# Normalização e compressão da densidade total (Phase 3.1)
# MAX_DENS_GLOBAL: divisor to normalise total density; calibrate with corpus.
# USE_LOG_COMPRESSION: apply log10(1 + x) to total density to smooth extremes.
# -------------------------------------------------------------------
MAX_DENS_GLOBAL = 20.0
USE_LOG_COMPRESSION = True

# Register bands for registral-density subindex (MIDI inclusive lower, exclusive upper).
# Configurable modelling assumption — not a universal acoustic truth.
DEFAULT_REGISTER_BANDS: dict[str, tuple[int, int]] = {
    "very_low": (0, 36),
    "low": (36, 48),
    "mid": (48, 72),
    "high": (72, 84),
    "very_high": (84, 128),
}

# Composite total-density component weights (documented, fixed in Phase 5).
COMPOSITE_HARMONIC_DAMPING = 0.15


# ===================================================================
# CONFIGURAÇÕES GERAIS
# ===================================================================

# Default directory for saving output files
DEFAULT_OUTPUT_DIRECTORY = os.path.join(os.path.expanduser("~"), "Densidade_Espectral_Output")

# Log level and format
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ===================================================================
# MUSICAL CONFIGURATION
# ===================================================================

# Notation and intervals
TAMANHO_OITAVA_MICROTONAL = 24
NOTAS_CROMATICAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Mapeamento de "nota base" -> posição (1..24)
ESCALA_MICROTONAL = {
    "C": 1,
    "C#-": 2,
    "C#": 3,
    "C#+": 4,
    "D": 5,
    "D#-": 6,
    "D#": 7,
    "D#+": 8,
    "E": 9,
    "E#-": 10,
    "F": 11,
    "F#-": 12,
    "F#": 13,
    "F#+": 14,
    "G": 15,
    "G#-": 16,
    "G#": 17,
    "G#+": 18,
    "A": 19,
    "A#-": 20,
    "A#": 21,
    "A#+": 22,
    "B": 23,
    "B#-": 24,
    "Cb+": 24,
    "Db+": 2,
    "Db": 3,
    "Db-": 4,
    "Eb+": 6,
    "Eb": 7,
    "Eb-": 8,
    "Fb+": 10,
    "Gb+": 12,
    "Gb": 13,
    "Gb-": 14,
    "Ab+": 16,
    "Ab": 17,
    "Ab-": 18,
    "Bb+": 20,
    "Bb": 21,
    "Bb-": 22,
}

# Note equivalences (flat vs sharp)
EQUIVALENCIAS_NOTAS = {
    "Cb": "B",
    "Db": "C#",
    "Eb": "D#",
    "Fb": "E",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
    "C-": "B#",
    "D-": "C#+",
    "E-": "D#+",
    "F-": "E#+",
    "G-": "F#+",
    "A-": "G#+",
    "B-": "A#+",
    "C+": "B-",
    "D+": "C#-",
    "E+": "D#-",
    "F+": "E-",
    "G+": "F#-",
    "A+": "G#-",
    "B+": "A#-",
}

# Note to MIDI value mapping
NOTA_PARA_MIDI_BASE = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "C#-": 0.5,
    "C#+": 1.5,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "D#-": 2.5,
    "D#+": 3.5,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "F#-": 5.5,
    "F#+": 6.5,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "G#-": 7.5,
    "G#+": 8.5,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "A#-": 9.5,
    "A#+": 10.5,
    "B": 11,
    "C-": 11.5,
    "B#": 12,
    "B#-": 11.5,
}

# ===================================================================
# GUI CONFIGURATION
# ===================================================================

# UI sizes and styles
UI_FONT_FAMILY = "Arial"
UI_DEFAULT_FONT_SIZE = 10
UI_TITLE_FONT_SIZE = 12
UI_PADDING = 10
UI_MARGIN = 5

# Cores
UI_COLORS = {
    "primary": "#4472C4",
    "secondary": "#5B9BD5",
    "background": "#F2F2F2",
    "text": "#333333",
    "warning": "#FFC000",
    "error": "#C00000",
    "success": "#70AD47",
}

# Dropdown menu options
DYNAMIC_LEVELS = ["pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff"]
INSTRUMENT_LIST = [
    "flautim",
    "flauta",
    "Oboe",
    "Corne_ingles",
    "clarinete",
    "clarinete baixo",
    "fagote",
    "contrafagote",
    "violino",
]
OCTAVE_LIST = [str(i) for i in range(10)]
QUANTITY_LIST = [str(i) for i in range(1, 21)]

# ===================================================================
# ANALYSIS AND PROCESSING CONFIGURATION
# ===================================================================

# Spectral analysis parameters
DEFAULT_LAMBDA = 0.05  # Lambda for exponential decay function
MIDI_BASE_FREQUENCY = 440.0  # Reference frequency A4
MIDI_BASE_NOTE = 69  # MIDI value for A4

# Default weight factor for analysis
DEFAULT_WEIGHT_FACTOR = 0.5

# Statistical validation settings
MIN_SAMPLES_FOR_VALIDATION = 5
HIGH_CORRELATION_THRESHOLD = 0.7

# ===================================================================
# REPORT CONFIGURATION
# ===================================================================

# Formatos de saída suportados
REPORT_FORMATS = {
    "pdf": "PDF Report",
    "txt": "Text Report",
    "json": "JSON Data",
    "csv": "CSV Data",
}

# Figure settings for reports
FIGURE_DPI = 300
DEFAULT_FIGURE_FORMAT = "png"
FIGURE_SIZES = {
    "small": (6, 4),
    "medium": (8, 6),
    "large": (12, 8),
}

# ===================================================================
# MESSAGES AND TEXT
# ===================================================================

# Common error messages
ERROR_MESSAGES = {
    "invalid_note": "Invalid musical note",
    "calculation_error": "Error during metric calculation",
    "missing_inputs": "Fill in all required fields",
    "file_save_error": "Error saving file",
    "insufficient_samples": "Insufficient samples for statistical validation",
    "module_not_found": "Module not found",
}

# Informative messages
INFO_MESSAGES = {
    "calculation_success": "Calculations completed successfully",
    "report_saved": "Report saved successfully",
    "validation_success": "Statistical validation completed",
}
