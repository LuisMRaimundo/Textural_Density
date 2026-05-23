# densidade_intervalar.py - versão com parâmetros ajustáveis
import re
import math
import numpy as np
import matplotlib.pyplot as plt
import logging
import json
import os
from scipy.optimize import minimize
from typing import Optional
from config import USE_LOG_COMPRESSION


# Configurar logging
logger = logging.getLogger('densidade_intervalar')

# Importar funções do módulo centralizado (como estava no seu código original)
from microtonal import (
    nota_para_posicao, escala_microtonal,
    note_to_midi, QUARTO_TOM_ACIMA, QUARTO_TOM_ABAIXO,
    ESCALA_MICROTONAL
)

from utils.notes import dyad_notes_from_semitone_interval




# ------------------------------------------------------------------------------
# PARÂMETROS GLOBAIS
# ------------------------------------------------------------------------------
TAMANHO_OITAVA_MICROTONAL = 24

# Path to calibrated parameters config file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config', 'density_params.json')

# Reference values for empirical dyad consonance ratings
# Baseados em dados de Hutchinson & Knopoff, Malmberg, Kameoka & Kuriyagawa
CONSONANCE_RATINGS = {
    0: 1.0,    # unisono
    2: -0.582, # M2/m7
    3: 0.594,  # m3/M6
    4: 0.386,  # M3/m6
    5: 1.240,  # P4/P5
    6: -0.453, # TT
}

# Default lambda when no calibration is available
DEFAULT_LAMBDA = 0.05

# Note list for internal use
llista_notas = list(escala_microtonal.keys())

# Lista simplificada com apenas notas cromáticas padrão (12 por oitava)
lista_notas_cromaticas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# ------------------------------------------------------------------------------
# Gerenciamento de parâmetros calibrados
# ------------------------------------------------------------------------------

def load_calibrated_parameters():
    """
    Load calibrated parameters from a JSON file.
    Returns the lambda value based on experimental data.
    """
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                params = json.load(f)
                logger.info(f"Parameters loaded: {params}")
                return params.get('lambda', DEFAULT_LAMBDA)
        else:
            logger.warning(f"Config file not found: {CONFIG_PATH}")
            return DEFAULT_LAMBDA
    except Exception as e:
        logger.error(f"Error loading parameters: {e}")
        return DEFAULT_LAMBDA

def save_calibrated_parameters(params):
    """
    Save calibrated parameters to a JSON file.
    """
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(params, f, indent=4)
            logger.info(f"Parameters saved: {params}")
        return True
    except Exception as e:
        logger.error(f"Error saving parameters: {e}")
        return False

# ------------------------------------------------------------------------------
# Calibração de parâmetros com base em dados experimentais
# ------------------------------------------------------------------------------

def calibrate_lambda(experimental_data=None):
    """
    Calibrate lambda using experimental data.
    If no data is provided, uses reference values from the literature.

    experimental_data: dict of the form {interval: consonance_value}

    Returns the optimized lambda value.
    """
    if experimental_data is None:
        experimental_data = CONSONANCE_RATINGS

    logger.info(f"Starting calibration with data: {experimental_data}")
    
    # Lambda search range (0.01 to 1.0)
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

    result = minimize(
        objective,
        [DEFAULT_LAMBDA],
        bounds=bounds,
        method='L-BFGS-B'
    )
    lambda_optimized = result.x[0]
    logger.info(f"Calibration complete. Optimized lambda: {lambda_optimized}")
    save_calibrated_parameters({'lambda': lambda_optimized})
    return lambda_optimized

# ------------------------------------------------------------------------------
# DEBUG: Função para imprimir informações detalhadas sobre cálculo de intervalo
# ------------------------------------------------------------------------------

def debug_intervalo(nota1, nota2, delta):
    """
    Função de debug para imprimir informações detalhadas sobre o cálculo
    do intervalo entre duas notas.
    """
    # [código original mantido]
    # Converter para MIDI para diagnóstico
    try:
        midi1 = note_to_midi(nota1)
        midi2 = note_to_midi(nota2)
        midi_delta = abs(midi1 - midi2)
        
        # Tentar converter para posições microtonais para diagnóstico
        try:
            # Converter símbolos Unicode para notação +/- antes de chamar nota_para_posicao
            nota1_processada = nota1
            nota2_processada = nota2
            
            if QUARTO_TOM_ACIMA in nota1:
                nota1_processada = nota1.replace(QUARTO_TOM_ACIMA, '+')
            elif QUARTO_TOM_ABAIXO in nota1:
                nota1_processada = nota1.replace(QUARTO_TOM_ABAIXO, '-')
                
            if QUARTO_TOM_ACIMA in nota2:
                nota2_processada = nota2.replace(QUARTO_TOM_ACIMA, '+')
            elif QUARTO_TOM_ABAIXO in nota2:
                nota2_processada = nota2.replace(QUARTO_TOM_ABAIXO, '-')
                
            pos1 = nota_para_posicao(nota1_processada)
            pos2 = nota_para_posicao(nota2_processada)
            pos_delta = abs(pos1 - pos2)
            
            logger.debug(f"DEBUG INTERVALO: {nota1} <-> {nota2}")
            logger.debug(f"  MIDI: {midi1:.2f} <-> {midi2:.2f} = {midi_delta:.2f}")
            logger.debug(f"  POS: {pos1:.2f} <-> {pos2:.2f} = {pos_delta:.2f}")
            logger.debug(f"  DELTA FINAL: {delta:.2f}")
            
        except ValueError as e:
            logger.error(f"Erro no debug de intervalo: {e}")
            
    except Exception as e:
        logger.error(f"Erro no debug de intervalo: {e}")

# ------------------------------------------------------------------------------
# 2) TRADUZIR INTERVALO (EM PASSOS) -> STRING
# ------------------------------------------------------------------------------
def translate_to_traditional_interval(microtonal_steps):
    """
    Given a number of microtonal steps (0..), returns an interval name
    (e.g. 'm3', 'P5'), accounting for octaves above 24 microtones.
    """
    interval_names = {
        0: 'unison', 1: 'unison+', 2: 'm2', 3: 'm2+', 4: 'M2', 5: 'M2+',
        6: 'm3', 7: 'm3+', 8: 'M3', 9: 'M3+', 10: 'P4', 11: 'P4+', 12: 'aug4',
        13: 'aug4+', 14: 'P5', 15: 'P5+', 16: 'm6', 17: 'm6+', 18: 'M6',
        19: 'M6+', 20: 'm7', 21: 'm7+', 22: 'M7', 23: 'M7+', 24: 'octave'
    }
    octaves = microtonal_steps // 24
    remainder = microtonal_steps % 24
    name = interval_names.get(remainder, f"?({remainder})")
    if octaves > 0:
        name += f" + {octaves} octave(s)"
    return name

# ------------------------------------------------------------------------------
# 3) FUNÇÃO MONOTÔNICA DECRESCENTE (EXPO) COM UNÍSSONO=0
# ------------------------------------------------------------------------------

def modified_exponential_decay(delta, lamb=None):
    """
    Modified exponential decay for interval density.

    Unison (delta=0) returns maximum value (1.0). Reflects acoustic reality
    where unisons create maximum density.

    Args:
        delta (float): Interval distance in microtones
        lamb (float, optional): Decay parameter. If None, uses calibrated value.

    Returns:
        float: Density contribution (1.0 for unison, decaying with distance)
    """
    if lamb is None:
        lamb = load_calibrated_parameters()
    if delta == 0:
        return 1.0
    return math.exp(-lamb * delta)

# ------------------------------------------------------------------------------
# 4) CALCULAR DENSIDADE INTERVALAR (SOMA PAR-A-PAR)
# ------------------------------------------------------------------------------
def get_intervals(notas):
    """
    Generate list of intervals in the form ["m2 (interval 2)", "M3 (interval 8)", ...]
    for each pair (i < j).
    """
    posicoes = [nota_para_posicao(n) for n in notas]
    intervalos_str = []
    for i in range(len(posicoes)):
        for j in range(i+1, len(posicoes)):
            delta = abs(posicoes[i] - posicoes[j])
            nome_trad = translate_to_traditional_interval(delta)
            intervalos_str.append(f"{nome_trad} (interval {delta})")
    return intervalos_str


def interval_string_to_number(intervalo_string):
    """
    Extract the number (int) from text "X (interval N)" -> N.
    E.g. 'm3 (interval 6)' -> 6.
    """
    match = re.search(r'\(intervalo (\d+)\)|\(interval (\d+)\)', intervalo_string)
    if match:
        return int(match.group(1) or match.group(2))
    return None


def calculate_interval_density(notas, lamb=None, use_optimization=True):
    """
    Pairwise sum of modified_exponential_decay: density = S_{i<j} e^(-lamb*delta).

    Symbolic pitch-distance model only (no perceptual weighting).
    """
    if lamb is None:
        lamb = load_calibrated_parameters()
        
    # Use MIDI values for more precision, especially with cents
    pitches = [note_to_midi(nota) for nota in notas if nota]
    
    if len(pitches) < 2:
        return 0.0
    
    # Logging para debug
    logger.debug(f"Notas: {notas}")
    logger.debug(f"Pitches MIDI: {pitches}")
    logger.debug(f"Usando lambda: {lamb}")
    logger.debug(f"Otimização vetorizada: {use_optimization}")
    
    if use_optimization and len(pitches) > 10:
        try:
            from utils.optimization import optimized_interval_density
            import numpy as np
            
            pitches_array = np.array(pitches, dtype=float)
            
            # Converter para escala microtonal (fator 2)
            def decay_func(d: np.ndarray) -> np.ndarray:
                # d já está em semitons, converter para escala microtonal
                delta = d * 2
                return modified_exponential_decay(delta, lamb)
            
            # Calcular usando versão vetorizada
            from utils.optimization import vectorized_density_calculation
            densidade_total = vectorized_density_calculation(pitches_array, decay_func)
            
            logger.debug(f"Densidade total (otimizada): {densidade_total:.6f}")
            return densidade_total
            
        except ImportError:
            logger.warning("Optimisation module not available, using default version")
        except Exception as e:
            logger.warning(f"Erro na versão otimizada: {e}, usando versão padrão")
    
    # Pairwise loop fallback when vectorised path is unavailable
    densidade_total = 0.0
    n = len(pitches)
    
    for i in range(n):
        for j in range(i+1, n):
            delta_semitons = abs(pitches[i] - pitches[j])
            
            # Log cada intervalo para debug
            logger.debug(f"Intervalo entre {notas[i]} e {notas[j]}: {delta_semitons:.2f} semitons")
            
            # Se o intervalo for muito pequeno (menos de 0.01 semitom), 
            # pode ser erro de precisão numérica, então verificamos explicitamente
            if delta_semitons < 0.01:
                # Verificar se as notas são realmente as mesmas ou se têm diferenças microtonais
                if notas[i] != notas[j]:
                    # Forçar um valor mínimo para garantir que o intervalo seja contabilizado
                    logger.debug(f"Intervalo muito pequeno entre notas diferentes: {notas[i]} e {notas[j]}")
                    delta_semitons = max(delta_semitons, 0.25)  # Forçar pelo menos um quarto de tom
            
            # Converter para a escala microtonal
            delta = delta_semitons * 2  # Fator 2 para manter a proporção com a escala original
            
            # Calcular a densidade deste intervalo
            densidade_base = modified_exponential_decay(delta, lamb)
            densidade_intervalo = densidade_base
            densidade_total += densidade_intervalo
            
            # Log para debug
            logger.debug(f"  delta = {delta:.2f}, densidade = {densidade_intervalo:.6f}")
            
            # Debug detalhado
            debug_intervalo(notas[i], notas[j], delta)
    
    logger.debug(f"Densidade total: {densidade_total:.6f}")
    return densidade_total


def calculate_interval_density_normalized(notas, lamb=None):
    """
    Symbolic interval density with mean pairwise normalization and optional log compression.

    Returns normalized reported value used in weighted density and metadata.
    """
    raw = calculate_interval_density(notas, lamb=lamb)
    n = len([x for x in notas if x])
    if n > 1:
        dens_scalar = float(2.0 * raw / (n * (n - 1)))
    else:
        dens_scalar = 0.0
    if USE_LOG_COMPRESSION:
        dens_scalar = float(np.log10(1.0 + dens_scalar))
    return dens_scalar

# ------------------------------------------------------------------------------
# Funções adicionais de análise e visualização
# ------------------------------------------------------------------------------

def analyze_consonance_vs_lambda(intervalos_teste=None, range_lambda=(0.01, 1.0, 0.05)):
    """
    Analyze how different lambda values affect computed consonance.

    intervalos_teste: list of (name, [notes]) to test
    range_lambda: (min, max, step) for lambda values

    Returns a DataFrame and plots a figure.
    """
    if intervalos_teste is None:
        intervalos_teste = [
            ("Unison", ["C4", "C4"]),
            ("Minor 2nd", ["C4", "Db4"]),
            ("Major 2nd", ["C4", "D4"]),
            ("Minor 3rd", ["C4", "Eb4"]),
            ("Major 3rd", ["C4", "E4"]),
            ("Perfect 4th", ["C4", "F4"]),
            ("Tritone", ["C4", "F#4"]),
            ("Perfect 5th", ["C4", "G4"]),
            ("Minor 6th", ["C4", "Ab4"]),
            ("Major 6th", ["C4", "A4"]),
            ("Minor 7th", ["C4", "Bb4"]),
            ("Major 7th", ["C4", "B4"]),
            ("Octave", ["C4", "C5"]),
        ]
    
    # Criar lista de valores lambda para testar
    lambda_min, lambda_max, lambda_step = range_lambda
    lambdas = np.arange(lambda_min, lambda_max + lambda_step/2, lambda_step)
    
    # Armazenar resultados
    resultados = []
    
    # Calcular densidade para cada intervalo e cada lambda
    for nome, notas in intervalos_teste:
        for lamb in lambdas:
            densidade = calculate_interval_density(notas, lamb=lamb)
            resultados.append({
                "Interval": nome,
                "Lambda": lamb,
                "Densidade": densidade
            })
    
    # Converter para DataFrame
    import pandas as pd
    df = pd.DataFrame(resultados)
    
    # Plotar resultados
    plt.figure(figsize=(12, 8))
    for nome in set(df["Interval"]):
        subset = df[df["Interval"] == nome]
        plt.plot(subset["Lambda"], subset["Densidade"], label=nome)
    plt.title("Interval Density vs. Lambda for Different Intervals")
    plt.xlabel("Lambda")
    plt.ylabel("Interval Density")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    return df

def test_calibrated_model():
    """
    Test the model with calibrated lambda on different intervals and compare
    with experimental consonance ratings.
    """
    lambda_calibrado = load_calibrated_parameters()
    
    # Criar um DataFrame com intervalos e seus valores de densidade calculados
    resultados = []
    
    # Testar nos intervalos de referência
    for intervalo, valor_exp in CONSONANCE_RATINGS.items():
        notas = list(dyad_notes_from_semitone_interval("C4", int(intervalo)))
        
        # Calcular densidade com lambda calibrado
        densidade = calculate_interval_density(notas, lamb=lambda_calibrado)
        max_valor = max(CONSONANCE_RATINGS.values())
        densidade_norm = 2 * (densidade / max_valor) - 1
        resultados.append({
            "Interval": translate_to_traditional_interval(intervalo * 2),
            "Experimental": valor_exp,
            "Density": densidade,
            "Normalized": densidade_norm,
            "Error": abs(densidade_norm - valor_exp)
        })
    import pandas as pd
    df = pd.DataFrame(resultados)
    plt.figure(figsize=(12, 6))
    intervalos = df["Interval"].tolist()
    plt.subplot(1, 2, 1)
    plt.bar(intervalos, df["Experimental"], alpha=0.7, label="Experimental")
    plt.bar(intervalos, df["Normalized"], alpha=0.7, label="Model")
    plt.title(f"Comparison: Lambda={lambda_calibrado:.4f}")
    plt.xlabel("Interval")
    plt.ylabel("Normalized Consonance")
    plt.xticks(rotation=45)
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.bar(intervalos, df["Error"])
    plt.title("Absolute Error")
    plt.xlabel("Interval")
    plt.ylabel("Error")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return df

# ------------------------------------------------------------------------------
# Funções para validação experimental
# ------------------------------------------------------------------------------

def collect_experimental_data():
    """
    Interface for collecting experimental consonance ratings.
    Returns a dict {interval: consonance_value}.
    """
    dados = {}
    intervalos = [
        (0, "Unison (C4-C4)"),
        (2, "Minor 2nd (C4-Db4)"),
        (4, "Major 2nd (C4-D4)"),
        (6, "Minor 3rd (C4-Eb4)"),
        (8, "Major 3rd (C4-E4)"),
        (10, "Perfect 4th (C4-F4)"),
        (12, "Tritone (C4-Gb4)"),
        (14, "Perfect 5th (C4-G4)")
    ]
    print("Experimental consonance rating")
    print("Rate each interval from -1 to 1 (-1=dissonant, 0=neutral, 1=consonant)")
    for intervalo, descricao in intervalos:
        while True:
            try:
                valor = float(input(f"{descricao}: "))
                if -1 <= valor <= 1:
                    dados[intervalo] = valor
                    break
                print("Value must be between -1 and 1.")
            except ValueError:
                print("Enter a valid number.")
    return dados

# ------------------------------------------------------------------------------
# Funções de demonstração
# ------------------------------------------------------------------------------

def demonstrate_calibration():
    """
    Demonstrate the calibration process with data collection and visualization.
    """
    print("Calibrating with reference data...")
    calibrate_lambda()
    test_calibrated_model()
    print("\nRun custom calibration with your own data? (y/n)")
    opcao = input()
    if opcao.lower() in ('s', 'sim', 'y', 'yes'):
        dados = collect_experimental_data()
        calibrate_lambda(dados)
        test_calibrated_model()
    analyze_consonance_vs_lambda()


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
__all__ = [
    "calculate_interval_density",
    "calculate_interval_density_normalized",
    "calibrate_lambda",
    "load_calibrated_parameters",
    "save_calibrated_parameters",
    "visualize_decay_function",
    "test_calibrated_model",
    "analyze_consonance_vs_lambda",
    "get_current_lambda",
]


def visualize_decay_function(lamb=None, max_delta=48, filename=None):
    """
    Professional visualization of the exponential decay function.
    Plots e^(-lamb*delta) for delta 0..max_delta (default 0..48 microtones).

    Args:
        lamb (float, optional): Lambda parameter. If None, uses calibrated value
        max_delta (int): Maximum delta for the plot
        filename: Path to save the figure (optional)

    Returns:
        Tuple (fig, ax)
    """
    from utils.plotting_style import (
        create_professional_figure,
        enhance_axes,
        finalize_figure,
        SCIENTIFIC_COLORS,
        PUBLICATION_DPI,
    )
    if lamb is None:
        lamb = load_calibrated_parameters()
    steps = np.linspace(0, max_delta, 200)
    valores = [modified_exponential_decay(s, lamb) for s in steps]

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
    ax.fill_between(steps, 0, valores, color=SCIENTIFIC_COLORS['primary'], alpha=0.2, zorder=2)
    enhance_axes(
        ax,
        title=rf'Decay function ($\lambda = {lamb:.4f}$)',
        xlabel=r'Interval distance $\delta$ (semitones)',
        ylabel=r'Density weight $w(\delta)$',
        grid=True
    )
    ax.legend(loc='upper right', framealpha=0.95)
    finalize_figure(fig)
    if filename:
        fig.savefig(filename, dpi=PUBLICATION_DPI, bbox_inches='tight', facecolor='white')
    else:
        plt.show()
    
    return fig, ax


def get_current_lambda():
    """Return the current calibrated lambda value."""
    return load_calibrated_parameters()

