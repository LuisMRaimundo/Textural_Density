# instrumentos/oboe.py
"""
Oboe instrument density module.

Delegates to the flute module, which uses **externally sourced acoustic
metadata** (``flute.spectral_data``), scaled by ``OBOE_SCALE``. Oboe-specific
measured tables are not yet committed; provenance is documented in
``instrumentos/registry.py`` (``profile_status=literature_derived``).
"""

import logging

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="literature_derived",
    citation=(
        "Scaled proxy over flute external acoustic table; "
        "see docs/instrument_acoustic_sources.md#oboe"
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#oboe",
    extraction_method="flute acoustic table × OBOE_SCALE (1.05); no oboe-specific corpus committed",
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(58, 88),
    uncertainty="medium",
    version="2026-05-21",
)

from . import flute

logger = logging.getLogger("oboe")

# Oboe typically has slightly higher spectral centroid than flute in mid range; scale density
OBOE_SCALE = 1.05


def calcular_densidade(nota: str, dinamica: str) -> float:
    """Density for oboe; delegates to flute model with scaling."""
    d = flute.calcular_densidade(nota, dinamica)
    return float(d) * OBOE_SCALE


def predict_intermediate_dynamics(pitches, pp_values, mf_values, ff_values):
    """Intermediate dynamics; delegates to flute and scales results."""
    out = flute.predict_intermediate_dynamics(pitches, pp_values, mf_values, ff_values)
    return {k: v * OBOE_SCALE for k, v in out.items()}
