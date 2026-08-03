# instrumentos/bass_drum.py
"""
Bass drum instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM)
proxy values from **NonTunPerc** MC Analysis exports
(``replication/percussion_nontunperc/Analysis/density_profiles_mc.csv``).

Phase = strike: the transient IS the instrument's density for membranophones; sustained-texture CDM still uses the strike composite as the proxy.

- **ff:** MC p50 ``composite_index`` for phase ``strike``
  (p05=0.935656, p50=22.888331, p95=444.199125; seed=20260803)
- **pp/mf:** ``generate_profile(stroke='bass_drum_beater', dynamic=…)``
  strike indices, scaled so ff matches MC p50 exactly
- **mf→ff jump:** ff/mf ≈ 1.776 (physical cascade / ff plate bypass
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
    citation=('theoretical model output (NonTunPerc v0.3.5, MC median), anchored in Rossing 2000 / Fletcher & Rossing 1998 / Sivian et al. 1931; validated against Iowa EMS recordings for mallet-excited plates and mf tam-tams; NOT validated for striking-position-specific strokes. Specimen bassdrum_82cm phase=strike MC p50 composite_index=22.888331 (p05=0.935656, p95=444.199125; seed=20260803).'),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles_mc.csv"
    ),
    extraction_method=("density_profiles_mc.csv strike p50 band weights → composite_index (ff); generate_profile(stroke='bass_drum_beater', dynamic=pp|mf|ff) strike indices scaled so ff=MC p50; flat chromatic CDM proxy; piecewise log-linear CDM interpolation (internal_default; guarantees monotone pp…ff on cascade jumps). Cross-family ratio caveat: NonTunPerc calibration bridge reports NO CALIBRATION ACHIEVED; CDM comparisons between these four instruments and empirically derived pitched-instrument tables are rank-order indicative only, not ratio-valid."),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(28, 48),
    uncertainty="high",
    version="2026-08-03+nontunperc-0.3.5+mc20260803",
    source_technique="struck_membrane",
    table_supported_techniques=("struck_membrane",),
    unpitched=True,
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("bass_drum")

# MC composite_index CI for the chosen phase (scale reference; seed=20260803).
SPECTRAL_PHASE_CI = {
    "phase": "strike",
    "p05": 0.935656,
    "p50": 22.888331,
    "p95": 444.199125,
    "mc_seed": 20260803,
    "nontunperc_commit": "4a110dbbaab3af831c0987e99a4b7019b008bbd6",
    "nontunperc_version": "0.3.5",
}

# Parallel CI dict (same for every note; flat unpitched table).
spectral_data_ci = {
    "p05": 0.935656,
    "p50": 22.888331,
    "p95": 444.199125,
}

# Flat CDM proxy. Range is notation-lookup convention only; no acoustic meaning
# (see unpitched flag).
spectral_data = {
    'E1': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'F1': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'F#1': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'G1': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'G#1': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'A1': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'A#1': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'B1': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'C2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'C#2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'D2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'D#2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'E2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'F2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'F#2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'G2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'G#2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'A2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'A#2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'B2': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
    'C3': {'pp': 7.613906, 'mf': 12.889258, 'ff': 22.888331},
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
