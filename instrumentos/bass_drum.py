# instrumentos/bass_drum.py
"""
Bass drum instrument density module.

Pitch-independent Combined Density Metric (CDM) proxy from **NonTunPerc**
MC Analysis exports
(``replication/percussion_nontunperc/Analysis/density_profiles_mc.csv``).

Phase = strike: the transient IS the instrument's density for membranophones; sustained-texture CDM still uses the strike composite as the proxy.

- **ff:** MC p50 ``composite_index`` for phase ``strike``
  (p05=0.935656, p50=22.888331, p95=444.199125; seed=20260803)
- **pp/mf:** ``generate_profile(stroke='bass_drum_beater', dynamic=…)``
  strike indices, scaled so ff matches MC p50 exactly
- **mf→ff jump:** ff/mf ≈ 1.776 (physical cascade / ff plate bypass
  retained; interior/tail levels committed from the former offline
  piecewise log-linear CDM + adaptive-tail ladder — no runtime fill-in)
- **NonTunPerc:** v0.3.5 commit ``4a110dbbaab3af831c0987e99a4b7019b008bbd6``

Unpitched: GUI/MusicXML/MIDI do not associate sounding pitch. ``nota`` is
ignored; density is dynamics-only. ``spectral_data`` keeps a single canonical
placeholder key (``D2``) for lookup-compat only.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="model_derived",
    citation=('theoretical model output (NonTunPerc v0.3.5, MC median), anchored in Rossing 2000 / Fletcher & Rossing 1998 / Sivian et al. 1931; validated against Iowa EMS recordings for mallet-excited plates and mf tam-tams; NOT validated for striking-position-specific strokes. Specimen bassdrum_82cm phase=strike MC p50 composite_index=22.888331 (p05=0.935656, p95=444.199125; seed=20260803).'),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles_mc.csv"
    ),
    extraction_method=("density_profiles_mc.csv strike p50 band weights → composite_index (ff); generate_profile(stroke='bass_drum_beater', dynamic=pp|mf|ff) strike indices scaled so ff=MC p50; pitch-independent DYNAMIC_CDM; committed 10-level ladder via offline piecewise log-linear CDM + adaptive tails (former internal_default; not runtime GPR). Cross-family ratio caveat: NonTunPerc calibration bridge reports NO CALIBRATION ACHIEVED; CDM comparisons between these four instruments and empirically derived pitched-instrument tables are rank-order indicative only, not ratio-valid."),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(28, 48),
    uncertainty="high",
    version="2026-08-03+nontunperc-0.3.5+mc20260803+committed-ladder",
    source_technique="struck_membrane",
    table_supported_techniques=("struck_membrane",),
    unpitched=True,
)

import logging

from instrumentos.pitch_interpolation import MissingCommittedDynamicError

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

spectral_data_ci = {
    "p05": 0.935656,
    "p50": 22.888331,
    "p95": 444.199125,
}

# Pitch-independent committed 10-dynamic CDM ladder (pp/mf/ff = NonTunPerc
# anchors; other levels = former internal_default log-linear + adaptive tails).
DYNAMIC_CDM = {'pppp': 6.675018, 'ppp': 6.974356, 'pp': 7.613906, 'p': 9.906442, 'mp': 11.299854, 'mf': 12.889258, 'f': 17.17596, 'ff': 22.888331, 'fff': 26.421695, 'ffff': 28.387945}

# Single canonical placeholder for MIDI-space table shape (lookup convention only).
LOOKUP_NOTE = 'D2'
spectral_data = {LOOKUP_NOTE: DYNAMIC_CDM}


def calcular_densidade(nota, dinamica):
    """Unpitched density: dynamics only; ``nota`` is ignored."""
    dyn = (dinamica or "mf").strip().lower()
    if dyn not in DYNAMIC_CDM:
        raise MissingCommittedDynamicError(
            f"Dynamic {dyn!r} not committed in bass_drum DYNAMIC_CDM "
            f"(have {sorted(DYNAMIC_CDM)})."
        )
    return float(DYNAMIC_CDM[dyn])
