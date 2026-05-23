# Legacy helpers — not part of the canonical analytical pipeline.

import logging

import numpy as np

from error_handler import InputError
from microtonal import converter_para_sustenido, extract_cents, note_to_midi

logger = logging.getLogger("data_processor")


def save_results(resultados, nome_arquivo=None):
    from score_io.exporters import save_results as _save_results

    return _save_results(
        resultados,
        nome_arquivo,
        prompt_if_missing=(nome_arquivo is None),
    )


def calcular_densidade_intervalar_com_cents(notas, lamb=0.05):
    from densidade_intervalar import modified_exponential_decay

    if not notas or len(notas) < 2:
        return 0.0

    valid_pitches = []
    valid_notas = []
    for nota in notas:
        if not nota:
            continue
        try:
            midi_value = note_to_midi(nota)
            if midi_value is not None and midi_value != 60.0:
                valid_pitches.append(midi_value)
                valid_notas.append(nota)
            elif nota.upper().startswith("C4"):
                valid_pitches.append(midi_value)
                valid_notas.append(nota)
        except Exception as e:
            logger.error(f"Error converting note to MIDI: {e}")

    if len(valid_pitches) < 2:
        return 0.0

    if len(valid_pitches) > 10:
        try:
            from utils.optimization import vectorized_density_calculation

            pitches_array = np.array(valid_pitches, dtype=float)

            def decay_func(d: np.ndarray) -> np.ndarray:
                return modified_exponential_decay(d * 2, lamb)

            return vectorized_density_calculation(pitches_array, decay_func)
        except (ImportError, Exception):
            pass

    densidade_total = 0.0
    n = len(valid_pitches)
    for i in range(n):
        for j in range(i + 1, n):
            delta_semitons = abs(valid_pitches[i] - valid_pitches[j])
            if delta_semitons < 0.01 and valid_notas[i] != valid_notas[j]:
                delta_semitons = 0.25
            delta = delta_semitons * 2
            densidade_total += modified_exponential_decay(delta, lamb)
    return densidade_total


def calcular_densidade_fundida(
    DI, DV, alpha=0.5, DI_max=100, DV_max=10, DI_mean=50, DI_std=25, DV_mean=5, DV_std=2.5
):
    DI_minmax = DI / DI_max
    DV_minmax = DV / DV_max
    DI_zscore = (DI - DI_mean) / DI_std if DI_std > 0 else 0
    DV_zscore = (DV - DV_mean) / DV_std if DV_std > 0 else 0
    DI_fundida = alpha * DI_minmax + (1 - alpha) * DI_zscore
    DV_fundida = alpha * DV_minmax + (1 - alpha) * DV_zscore
    return 10 * (DI_fundida + DV_fundida) / 2


def _validate_and_extract_input(input_data: dict):
    notas = input_data.get("notes", [])
    dinamicas = input_data.get("dynamics", [])
    instrumentos = input_data.get("instruments", [])
    numeros_instr = input_data.get("num_instruments", [])
    weight_factor = input_data.get("weight_factor", 0.5)
    if not (notas and dinamicas and instrumentos and numeros_instr):
        raise InputError("Notes, dynamics, instruments and quantities are required.")
    if not (len(notas) == len(dinamicas) == len(instrumentos) == len(numeros_instr)):
        raise InputError("Input lists must have the same length.")
    return notas, dinamicas, instrumentos, numeros_instr, weight_factor


def _normalize_notes_to_sustenido(notas: list) -> list:
    return [
        (
            f"{converter_para_sustenido(base)}{('+' if cents > 0 else '')}{cents}c"
            if cents
            else converter_para_sustenido(base)
        )
        for base, cents in (extract_cents(n) for n in notas)
    ]


def generate_validation_text(resultados_validacao, num_historico):
    from validation.gui_validation import generate_validation_text as _fmt

    return _fmt(resultados_validacao, num_historico)
