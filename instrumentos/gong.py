# instrumentos/gong.py
"""
Gong instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM)
proxy values from **NonTunPerc** MC Analysis exports
(``replication/percussion_nontunperc/Analysis/density_profiles_mc.csv``).

Phase = shimmer (tam-tam-template sustained regime for plate gongs; wind-gong subtypes share the same post-bloom emphasis). The CDM proxy feeds sustained-texture analysis; the strike window under-represents plates and, combined with the excitation filter, artificially collapses pp/mf.

- **ff:** MC p50 ``composite_index`` for phase ``shimmer``
  (p05=1.639183, p50=17.148679, p95=112.884854; seed=20260803)
- **pp/mf:** ``generate_profile(stroke='yarn_mallet', dynamic=…)``
  shimmer indices, scaled so ff matches MC p50 exactly
- **mf→ff jump:** ff/mf ≈ 8.135 (physical cascade / ff plate bypass
  where applicable — retained; interior dynamics use log-CDM piecewise linear
  interpolation so ``f`` lies between mf and ff)
- **NonTunPerc:** v0.3.5 commit ``4a110dbbaab3af831c0987e99a4b7019b008bbd6``

Flat chromatic table: note key is notation-lookup convention only; no acoustic
meaning (see ``INSTRUMENT_SOURCE.unpitched`` / registry ``unpitched`` flag).
Intermediate dynamics use piecewise log-linear CDM interpolation
(``internal_default``; Matérn GPR cannot stay monotone on large mf→ff jumps).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="model_derived",
    citation=('theoretical model output (NonTunPerc v0.3.5, MC median), anchored in Rossing 2000 / Fletcher & Rossing 1998 / Sivian et al. 1931; validated against Iowa EMS recordings for mallet-excited plates and mf tam-tams; NOT validated for striking-position-specific strokes. Specimen gong_50cm_bronze phase=shimmer MC p50 composite_index=17.148679 (p05=1.639183, p95=112.884854; seed=20260803).'),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles_mc.csv"
    ),
    extraction_method=("density_profiles_mc.csv shimmer p50 band weights → composite_index (ff); generate_profile(stroke='yarn_mallet', dynamic=pp|mf|ff) shimmer indices scaled so ff=MC p50; flat chromatic CDM proxy; piecewise log-linear CDM interpolation (internal_default; guarantees monotone pp…ff on cascade jumps). Cross-family ratio caveat: NonTunPerc calibration bridge reports NO CALIBRATION ACHIEVED; CDM comparisons between these four instruments and empirically derived pitched-instrument tables are rank-order indicative only, not ratio-valid."),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(36, 60),
    uncertainty="high",
    version="2026-08-03+nontunperc-0.3.5+mc20260803",
    source_technique="struck_plate",
    table_supported_techniques=("struck_plate",),
    unpitched=True,
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("gong")

# MC composite_index CI for the chosen phase (scale reference; seed=20260803).
SPECTRAL_PHASE_CI = {
    "phase": "shimmer",
    "p05": 1.639183,
    "p50": 17.148679,
    "p95": 112.884854,
    "mc_seed": 20260803,
    "nontunperc_commit": "4a110dbbaab3af831c0987e99a4b7019b008bbd6",
    "nontunperc_version": "0.3.5",
}

# Parallel CI dict (same for every note; flat unpitched table).
spectral_data_ci = {
    "p05": 1.639183,
    "p50": 17.148679,
    "p95": 112.884854,
}

# Flat CDM proxy. Range is notation-lookup convention only; no acoustic meaning
# (see unpitched flag).
spectral_data = {
    'C2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'C#2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'D2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'D#2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'E2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'F2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'F#2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'G2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'G#2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'A2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'A#2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'B2': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'C3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'C#3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'D3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'D#3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'E3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'F3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'F#3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'G3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'G#3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'A3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'A#3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'B3': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
    'C4': {'pp': 1.537666, 'mf': 2.10794, 'ff': 17.148679},
}

def calcular_densidade(nota, dinamica):
    """Compute density from spectral CDM table (MIDI-space lookup, octave-safe)."""
    from instrumentos.spectral_lookup import lookup_spectral_density

    return lookup_spectral_density(
        spectral_data,
        nota,
        dinamica,
        logger=logger,
        preprocess=normalize_note_string,
    )
