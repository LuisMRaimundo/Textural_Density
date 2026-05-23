# calibration.py
"""
Module for calibrating the lambda parameter in interval density analysis.
Centralizes calibration, visualization and access to calibrated parameters.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import logging

from utils.notes import dyad_notes_from_semitone_interval

logger = logging.getLogger('calibration')
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config', 'density_params.json')
DEFAULT_LAMBDA = 0.05

CONSONANCE_RATINGS = {
    0: 1.0,    # unison
    2: -0.582, # M2/m7
    3: 0.594,  # m3/M6
    4: 0.386,  # M3/m6
    5: 1.240,  # P4/P5
    6: -0.453, # TT
}


def load_calibrated_parameters(config_path=None):
    """
    Load calibrated parameters from a JSON file. Returns lambda.
    When config_path is None, uses densidade_intervalar (same file as calculation).
    """
    if config_path is None:
        from densidade_intervalar import load_calibrated_parameters as _load
        return _load()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                params = json.load(f)
                logger.info(f"Parameters loaded: {params}")
                return params.get('lambda', DEFAULT_LAMBDA)
        logger.warning(f"Config file not found: {config_path}")
        return DEFAULT_LAMBDA
    except Exception as e:
        logger.error(f"Error loading parameters: {e}")
        return DEFAULT_LAMBDA


def save_calibrated_parameters(params, config_path=None):
    """
    Save calibrated parameters to a JSON file.
    When config_path is None, delegates to densidade_intervalar.
    """
    if config_path is None:
        from densidade_intervalar import save_calibrated_parameters as _save
        return _save(params)
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(params, f, indent=4)
            logger.info(f"Parameters saved: {params}")
        return True
    except Exception as e:
        logger.error(f"Error saving parameters: {e}")
        return False


def _modified_exponential_decay(delta, lamb=None):
    """If delta=0 return 0; else e^(-lamb*delta). Uses calibrated lambda if lamb is None."""
    if lamb is None:
        lamb = load_calibrated_parameters()
    if delta == 0:
        return 0.0
    return np.exp(-lamb * delta)


def calculate_interval_density(notas, lamb=None):
    """
    Compute interval density for a set of notes. Simplified implementation.
    When lamb is None uses calibrated value. Delegates to densidade_intervalar for full logic if needed.
    """
    from utils.notes import note_to_midi
    if lamb is None:
        lamb = load_calibrated_parameters()
    if len(notas) < 2:
        return 0.0
    pitches = [note_to_midi(nota) for nota in notas if nota]
    densidade_total = 0.0
    for i in range(len(pitches)):
        for j in range(i+1, len(pitches)):
            delta_semitons = abs(pitches[i] - pitches[j])
            delta = delta_semitons * 2
            densidade_parcial = _modified_exponential_decay(delta, lamb)
            densidade_total += densidade_parcial
    return densidade_total


def calibrate_lambda(experimental_data=None):
    """
    Calibrate lambda using experimental data. If None, uses CONSONANCE_RATINGS.
    Returns optimized lambda.
    """
    if experimental_data is None:
        experimental_data = CONSONANCE_RATINGS
    logger.info(f"Starting calibration with data: {experimental_data}")
    bounds = [(0.01, 1.0)]

    def objective(lambda_val):
        lambda_val = lambda_val[0]
        error_sum = 0
        for interval, exp_val in experimental_data.items():
            notes = list(dyad_notes_from_semitone_interval("C4", int(interval)))
            density = calculate_interval_density(notes, lamb=lambda_val)
            density_norm = 2 * (density / max(experimental_data.values())) - 1
            error_sum += (density_norm - exp_val) ** 2
        logger.debug(f"Lambda: {lambda_val}, Error: {error_sum}")
        return error_sum

    result = minimize(objective, [DEFAULT_LAMBDA], bounds=bounds, method='L-BFGS-B')
    lambda_optimized = result.x[0]
    logger.info(f"Calibration complete. Optimized lambda: {lambda_optimized}")
    save_calibrated_parameters({'lambda': lambda_optimized})
    return lambda_optimized

def visualize_decay_function(lamb=None, max_delta=48, filename=None):
    """
    Professional visualization of the exponential decay function.
    Plots e^(-lamb*delta) for delta 0..max_delta. Returns (fig, ax).
    """
    from utils.plotting_style import (
        create_professional_figure,
        enhance_axes,
        SCIENTIFIC_COLORS
    )
    from densidade_intervalar import modified_exponential_decay

    if lamb is None:
        lamb = load_calibrated_parameters()
    steps = np.linspace(0, max_delta, 200)
    valores = [modified_exponential_decay(s, lamb) for s in steps]
    
    from utils.plotting_style import finalize_figure, PUBLICATION_DPI
    fig, ax = create_professional_figure(nrows=1, ncols=1, figsize=(8, 5))

    ax.plot(
        steps,
        valores,
        color=SCIENTIFIC_COLORS['primary'],
        linewidth=2.5,
        alpha=0.9,
        label=rf'$e^{{-{lamb:.4f}\,\delta}}$',
        zorder=3
    )
    
    # Adicionar área sombreada sob a curva
    ax.fill_between(
        steps,
        0,
        valores,
        color=SCIENTIFIC_COLORS['primary'],
        alpha=0.2,
        zorder=2
    )
    
    # Adicionar linha de referência em y=0
    ax.axhline(y=0, color=SCIENTIFIC_COLORS['neutral'], linestyle='-', linewidth=1.0, alpha=0.5, zorder=1)
    
    ax.annotate(
        'Unison (δ=0)',
        xy=(0, 0),
        xytext=(max_delta * 0.15, max(valores) * 0.1),
        fontsize=10,
        color=SCIENTIFIC_COLORS['dark'],
        bbox=dict(
            boxstyle='round,pad=0.5',
            facecolor='white',
            edgecolor=SCIENTIFIC_COLORS['primary'],
            alpha=0.9,
            linewidth=1.5
        ),
        arrowprops=dict(
            arrowstyle='->',
            color=SCIENTIFIC_COLORS['primary'],
            lw=1.5,
            alpha=0.7
        )
    )
    
    enhance_axes(
        ax,
        title=rf'Exponential decay function ($\lambda = {lamb:.4f}$)',
        xlabel=r'Interval distance $\delta$ (semitones)',
        ylabel=r'Density weight $w(\delta)$',
        grid=True
    )
    
    # Adicionar legenda
    ax.legend(
        loc='upper right',
        framealpha=0.95,
        fontsize=10,
        edgecolor=SCIENTIFIC_COLORS['neutral']
    )
    
    info_text = f"Unison (δ=0) = 0\nMax as δ→0⁺"
    ax.text(
        0.98, 0.02,
        info_text,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment='bottom',
        horizontalalignment='right',
        bbox=dict(
            boxstyle='round,pad=0.5',
            facecolor='white',
            edgecolor=SCIENTIFIC_COLORS['neutral'],
            alpha=0.9
        )
    )
    
    finalize_figure(fig)
    if filename:
        fig.savefig(filename, dpi=PUBLICATION_DPI, bbox_inches='tight', facecolor='white')
    else:
        plt.show()
    return fig, ax

def test_calibrated_model():
    """
    Test the model with calibrated lambda. Delegates to densidade_intervalar.test_calibrated_model.
    Returns matplotlib Figure.
    """
    from densidade_intervalar import test_calibrated_model as _test
    return _test()

def analyze_consonance_vs_lambda(intervalos_teste=None, range_lambda=(0.01, 1.0, 0.05)):
    """
    Analyze how different lambda values affect computed consonance.
    Delegates to densidade_intervalar. Returns DataFrame.
    """
    from densidade_intervalar import analyze_consonance_vs_lambda as _analyze
    return _analyze(intervalos_teste, range_lambda)


def get_current_lambda():
    """Return the current calibrated lambda value."""
    return load_calibrated_parameters()


def run_calibration(experimental_data=None):
    """
    Run lambda calibration from experimental data. Shows visualizations and returns optimized lambda.
    """
    lambda_atual = load_calibrated_parameters()
    print(f"Current lambda: {lambda_atual}")
    lambda_otimizado = calibrate_lambda(experimental_data)
    print(f"Optimized lambda: {lambda_otimizado}")
    test_calibrated_model()
    visualize_decay_function(lambda_otimizado)
    return lambda_otimizado


if __name__ == "__main__":
    run_calibration()
