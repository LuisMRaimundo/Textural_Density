# instrumentos/flute.py
"""
Flute instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM) values
from **external acoustic sources** (IOWA + ORCH sustain collections,
midpoint summary at pp/mf/ff). Intermediate dynamics are interpolated via GPR.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Median/midpoint summary of flute sustained-note Combined Density Metrics across IOWA and ORCH sound collections (pp, mf, ff)."
    ),
    source_url_or_identifier='D:\\MADEIRAS\\Flute_Zenodo_collections_media.xlsx',
    extraction_method=(
        "Combined Density Metric midpoint of IOWA/ORCH collections (CDM midpoint pass-through; no rescaling); GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(60, 96),
    uncertainty="medium",
    version="2026-06-21",
)

import logging

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C, Matern
from utils.notes import normalize_note_string

logger = logging.getLogger("flute")

# CDM medians: (IOWA + ORCH) / 2 per note at pp, mf, ff (sustains (ordinario)).
spectral_data = {
    'B3': {'pp': 8.870556, 'mf': 21.702451, 'ff': 27.071378},
    'C4': {'pp': 12.595456, 'mf': 25.954758, 'ff': 23.565058},
    'C#4': {'pp': 16.2371, 'mf': 20.53693, 'ff': 22.585794},
    'D4': {'pp': 14.194358, 'mf': 20.443077, 'ff': 22.151797},
    'D#4': {'pp': 11.967182, 'mf': 18.562162, 'ff': 21.541591},
    'E4': {'pp': 12.884926, 'mf': 16.406844, 'ff': 20.480775},
    'F4': {'pp': 14.538575, 'mf': 17.893561, 'ff': 19.840718},
    'F#4': {'pp': 14.543666, 'mf': 16.698347, 'ff': 19.598124},
    'G4': {'pp': 14.202359, 'mf': 15.730203, 'ff': 18.278442},
    'G#4': {'pp': 10.649169, 'mf': 16.933738, 'ff': 18.905842},
    'A4': {'pp': 11.717742, 'mf': 15.243497, 'ff': 15.209946},
    'A#4': {'pp': 9.083315, 'mf': 12.341037, 'ff': 13.037959},
    'B4': {'pp': 9.338328, 'mf': 12.724432, 'ff': 13.422615},
    'C5': {'pp': 7.663464, 'mf': 10.697638, 'ff': 11.209225},
    'C#5': {'pp': 7.478947, 'mf': 9.209881, 'ff': 10.276392},
    'D5': {'pp': 6.137254, 'mf': 8.842451, 'ff': 7.579961},
    'D#5': {'pp': 6.452396, 'mf': 7.920537, 'ff': 7.152035},
    'E5': {'pp': 6.600471, 'mf': 7.32222, 'ff': 8.799689},
    'F5': {'pp': 5.778505, 'mf': 7.726141, 'ff': 10.973453},
    'F#5': {'pp': 5.578118, 'mf': 8.340836, 'ff': 11.218165},
    'G5': {'pp': 6.518259, 'mf': 11.460072, 'ff': 9.517152},
    'G#5': {'pp': 5.369871, 'mf': 8.791971, 'ff': 9.053353},
    'A5': {'pp': 4.236837, 'mf': 7.387741, 'ff': 6.76985},
    'A#5': {'pp': 4.061298, 'mf': 5.682645, 'ff': 5.959571},
    'B5': {'pp': 2.873151, 'mf': 5.817257, 'ff': 6.034786},
    'C6': {'pp': 5.55885, 'mf': 5.561422, 'ff': 5.264909},
    'C#6': {'pp': 4.416359, 'mf': 4.527877, 'ff': 5.362071},
    'D6': {'pp': 3.806011, 'mf': 4.991786, 'ff': 5.14761},
    'D#6': {'pp': 4.022333, 'mf': 4.969788, 'ff': 6.315089},
    'E6': {'pp': 3.405152, 'mf': 4.755261, 'ff': 3.777119},
    'F6': {'pp': 3.317954, 'mf': 2.998054, 'ff': 3.299648},
    'F#6': {'pp': 2.536521, 'mf': 3.369646, 'ff': 3.502984},
    'G6': {'pp': 2.475006, 'mf': 5.579857, 'ff': 2.826034},
    'G#6': {'pp': 3.117187, 'mf': 2.734429, 'ff': 3.499909},
    'A6': {'pp': 1.910496, 'mf': 3.683686, 'ff': 3.345836},
    'A#6': {'pp': 3.335501, 'mf': 4.487484, 'ff': 4.483456},
    'B6': {'pp': 2.346114, 'mf': 3.556628, 'ff': 3.116059},
    'C7': {'pp': 2.998543, 'mf': 3.157057, 'ff': 4.28703},
    'C#7': {'pp': 3.81881, 'mf': 3.230978, 'ff': 4.075824},
    'D7': {'pp': 3.849684, 'mf': 3.192335, 'ff': 3.873665},
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

def predict_intermediate_dynamics(pitches, pp_values, mf_values, ff_values):
    """Predict intermediate dynamics using Gaussian Process Regression."""
    dynamic_levels = {
        "pppp": 1, "ppp": 2, "pp": 3, "p": 4, "mf": 5,
        "f": 6, "ff": 7, "fff": 8, "ffff": 9,
    }
    all_dynamics = list(dynamic_levels.keys())
    predictions = {dynamic: [] for dynamic in all_dynamics}

    existing_levels = np.array([dynamic_levels[d] for d in ["pp", "mf", "ff"]]).reshape(-1, 1)
    all_levels = np.array([dynamic_levels[d] for d in all_dynamics]).reshape(-1, 1)

    try:
        y_train = np.array([pp_values, mf_values, ff_values]).T
        if y_train.size == 0 or np.isnan(y_train).any():
            logger.warning("Insufficient or invalid training data for GPR")
            return {d: np.zeros_like(pp_values) for d in all_dynamics}

        matern_kernel = C(1.0) * Matern(length_scale=1.0, nu=1.5)
        gpr = GaussianProcessRegressor(kernel=matern_kernel, n_restarts_optimizer=10, alpha=1e-1)

        for i, y in enumerate(y_train):
            gpr.fit(existing_levels, y)
            y_pred = gpr.predict(all_levels)
            for j, dynamic in enumerate(all_dynamics):
                predictions[dynamic].append(y_pred[j])

        return {k: np.array(v) for k, v in predictions.items()}
    except Exception as e:
        logger.error(f"Error predicting intermediate dynamics: {e}")
        return {d: np.zeros_like(pp_values) for d in all_dynamics}
