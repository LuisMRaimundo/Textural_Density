# instrumentos/violin.py
"""
Violin instrument density module.

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
        "Sparse violin CDM table from IOWA and ORCH sustain collections; midpoint summary at pp/mf/ff (Zenodo curation workbook)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin',
    extraction_method=(
        "Combined Density Metric midpoint of IOWA/ORCH collections; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(55, 103),
    uncertainty="medium",
    version="2026-06-19",
)

import logging

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C, Matern
from utils.notes import normalize_note_string

logger = logging.getLogger("violin")

# CDM medians: (IOWA + ORCH) / 2 per note at pp, mf, ff (arco / ordinario sustains).
spectral_data = {
    'G3': {'pp': 57.391507, 'mf': 61.65907, 'ff': 70.623528},
    'G#3': {'pp': 33.591535, 'mf': 36.008517, 'ff': 38.554306},
    'A3': {'pp': 30.702267, 'mf': 29.143841, 'ff': 42.287864},
    'A#3': {'pp': 28.838925, 'mf': 32.194271, 'ff': 38.719126},
    'B3': {'pp': 39.784207, 'mf': 39.101102, 'ff': 35.503268},
    'C4': {'pp': 27.340394, 'mf': 23.374901, 'ff': 27.795461},
    'C#4': {'pp': 25.052836, 'mf': 22.127835, 'ff': 25.8856},
    'D4': {'pp': 26.133791, 'mf': 34.381636, 'ff': 36.879891},
    'D#4': {'pp': 26.560277, 'mf': 32.386338, 'ff': 30.695905},
    'E4': {'pp': 31.15438, 'mf': 35.982938, 'ff': 34.793031},
    'F4': {'pp': 26.177892, 'mf': 26.256405, 'ff': 31.173848},
    'F#4': {'pp': 26.192578, 'mf': 29.118582, 'ff': 28.988298},
    'G4': {'pp': 26.244, 'mf': 28.582867, 'ff': 29.160595},
    'G#4': {'pp': 21.367527, 'mf': 20.040854, 'ff': 24.983277},
    'A4': {'pp': 27.47028, 'mf': 23.809207, 'ff': 30.79765},
    'A#4': {'pp': 22.652636, 'mf': 20.433399, 'ff': 26.037132},
    'B4': {'pp': 25.336199, 'mf': 25.26667, 'ff': 23.994139},
    'C5': {'pp': 16.400225, 'mf': 16.67357, 'ff': 16.590142},
    'C#5': {'pp': 19.387751, 'mf': 15.382446, 'ff': 17.748366},
    'D5': {'pp': 16.640459, 'mf': 18.281285, 'ff': 18.556922},
    'D#5': {'pp': 17.096813, 'mf': 16.571727, 'ff': 18.685236},
    'E5': {'pp': 21.459182, 'mf': 23.295079, 'ff': 25.541413},
    'F5': {'pp': 15.674254, 'mf': 18.070114, 'ff': 19.702604},
    'F#5': {'pp': 14.343111, 'mf': 17.293324, 'ff': 20.63479},
    'G5': {'pp': 15.895791, 'mf': 17.19385, 'ff': 17.95471},
    'G#5': {'pp': 13.179229, 'mf': 14.251474, 'ff': 13.795649},
    'A5': {'pp': 13.386584, 'mf': 14.84153, 'ff': 17.357882},
    'A#5': {'pp': 10.710713, 'mf': 12.021352, 'ff': 11.619004},
    'B5': {'pp': 13.053029, 'mf': 14.265343, 'ff': 14.197524},
    'C6': {'pp': 13.138963, 'mf': 14.68363, 'ff': 17.558458},
    'C#6': {'pp': 10.378064, 'mf': 11.798903, 'ff': 13.601809},
    'D6': {'pp': 9.584466, 'mf': 12.903616, 'ff': 15.145209},
    'D#6': {'pp': 10.632592, 'mf': 12.162554, 'ff': 15.773834},
    'E6': {'pp': 12.124289, 'mf': 13.7056, 'ff': 12.457872},
    'F6': {'pp': 8.559391, 'mf': 9.228193, 'ff': 8.730382},
    'F#6': {'pp': 8.187718, 'mf': 8.468389, 'ff': 9.191835},
    'G6': {'pp': 6.336218, 'mf': 8.310972, 'ff': 7.974047},
    'G#6': {'pp': 6.989477, 'mf': 9.869439, 'ff': 8.668368},
    'A6': {'pp': 7.428443, 'mf': 7.846089, 'ff': 9.525356},
    'A#6': {'pp': 5.321608, 'mf': 6.28718, 'ff': 6.586375},
    'B6': {'pp': 6.431797, 'mf': 6.888149, 'ff': 7.98655},
    'C7': {'pp': 5.245629, 'mf': 7.706866, 'ff': 5.790592},
    'C#7': {'pp': 5.426751, 'mf': 7.643142, 'ff': 6.961116},
    'D7': {'pp': 5.883139, 'mf': 6.513301, 'ff': 6.907783},
    'D#7': {'pp': 4.383445, 'mf': 6.275297, 'ff': 7.088029},
    'E7': {'pp': 5.041328, 'mf': 5.99111, 'ff': 4.730762},
    'F7': {'pp': 4.958746, 'mf': 6.41294, 'ff': 5.669511},
    'F#7': {'pp': 5.877028, 'mf': 6.304183, 'ff': 5.274257},
    'G7': {'pp': 4.46921, 'mf': 6.365012, 'ff': 4.816325},
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
