# instrumentos/tamtam.py
"""
Tam-tam instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM)
proxy values from **NonTunPerc** MC Analysis exports
(``replication/percussion_nontunperc/Analysis/density_profiles_mc.csv``).

Phase = shimmer of the tam-tam template (post-bloom sustained regime). The CDM proxy feeds sustained-texture analysis; the strike window under-represents plates and, combined with the excitation filter, artificially collapses pp/mf.

- **ff:** MC p50 ``composite_index`` for phase ``shimmer``
  (p05=2.634758, p50=12.324004, p95=75.077651; seed=20260803)
- **pp/mf:** ``generate_profile(stroke='yarn_mallet', dynamic=…)``
  shimmer indices, scaled so ff matches MC p50 exactly
- **mf→ff jump:** ff/mf ≈ 3.008 (physical cascade / ff plate bypass
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
    citation=('theoretical model output (NonTunPerc v0.3.5, MC median), anchored in Rossing 2000 / Fletcher & Rossing 1998 / Sivian et al. 1931; validated against Iowa EMS recordings for mallet-excited plates and mf tam-tams; NOT validated for striking-position-specific strokes. Specimen tamtam_80cm_bronze phase=shimmer MC p50 composite_index=12.324004 (p05=2.634758, p95=75.077651; seed=20260803).'),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles_mc.csv"
    ),
    extraction_method=("density_profiles_mc.csv shimmer p50 band weights → composite_index (ff); generate_profile(stroke='yarn_mallet', dynamic=pp|mf|ff) shimmer indices scaled so ff=MC p50; flat chromatic CDM proxy; piecewise log-linear CDM interpolation (internal_default; guarantees monotone pp…ff on cascade jumps). Cross-family ratio caveat: NonTunPerc calibration bridge reports NO CALIBRATION ACHIEVED; CDM comparisons between these four instruments and empirically derived pitched-instrument tables are rank-order indicative only, not ratio-valid."),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(24, 48),
    uncertainty="high",
    version="2026-08-03+nontunperc-0.3.5+mc20260803",
    source_technique="struck_plate",
    table_supported_techniques=("struck_plate",),
    unpitched=True,
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("tamtam")

# MC composite_index CI for the chosen phase (scale reference; seed=20260803).
SPECTRAL_PHASE_CI = {
    "phase": "shimmer",
    "p05": 2.634758,
    "p50": 12.324004,
    "p95": 75.077651,
    "mc_seed": 20260803,
    "nontunperc_commit": "4a110dbbaab3af831c0987e99a4b7019b008bbd6",
    "nontunperc_version": "0.3.5",
}

# Parallel CI dict (same for every note; flat unpitched table).
spectral_data_ci = {
    "p05": 2.634758,
    "p50": 12.324004,
    "p95": 75.077651,
}

# Flat CDM proxy. Range is notation-lookup convention only; no acoustic meaning
# (see unpitched flag).
spectral_data = {
    'C1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'C#1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'D1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'D#1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'E1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'F1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'F#1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'G1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'G#1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'A1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'A#1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'B1': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'C2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'C#2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'D2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'D#2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'E2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'F2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'F#2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'G2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'G#2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'A2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'A#2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'B2': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
    'C3': {'pp': 3.049788, 'mf': 4.096546, 'ff': 12.324004},
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
