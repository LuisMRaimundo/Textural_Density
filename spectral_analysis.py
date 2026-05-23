"""spectral_analysis.py

Módulo autónomo com utilitários para análise espectral – centroid, spread,
skewness, kurtosis, flatness, roll‑off e vetor de chroma.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple
import logging
from scipy.stats import gaussian_kde
from microtonal import frequency_to_note_name as _microtonal_hz_to_note
from microtonal import midi_to_hz

LOGGER = logging.getLogger(__name__)

################################################################################
# 1. UTILITÁRIOS BÁSICOS                                                       #
################################################################################


def _hz_to_centroid_note(freq: float) -> str:
    """
    Label for centroid note from Hz.

    Keeps English ``Invalid`` for empty/invalid spectra (API stability); delegates
    valid frequencies to ``microtonal.frequency_to_note_name``.
    """
    if not np.isfinite(freq) or freq <= 0:
        return "Invalid"
    label = _microtonal_hz_to_note(freq)
    if label in ("Inválida", "") or label is None:
        return "Invalid"
    return label

################################################################################
# 2. KERNEL DENSITY ESTIMATION ROBUSTO                                        #
################################################################################

def robust_gaussian_kde(data: np.ndarray,
                        weights: np.ndarray | None = None,
                        bw_method: str | float | None = None):
    """Versão à prova de *LinAlgError* quando a matriz de covariância é singular."""
    try:
        return gaussian_kde(data, weights=weights, bw_method=bw_method)
    except np.linalg.LinAlgError:
        LOGGER.warning("Singular covariance detected – adding jitter…")
        noise = np.random.normal(0, 1e-6, size=data.shape)
        return gaussian_kde(data + noise, weights=weights, bw_method=bw_method)

################################################################################
# 3. MOMENTOS ESPECTRAIS                                                      #
################################################################################

def _safe_array(a):
    """Convert input to numpy array, replacing NaN with 0."""
    return np.nan_to_num(np.asarray(a, dtype=float))


def calculate_spectral_moments(
    pitches: List[float] | np.ndarray,
    amplitudes: List[float] | np.ndarray
) -> Dict[str, Dict[str, float] | float]:
    """Centroid, spread and skewness (spectral moments).

    * ``pitches``  – MIDI heights (floats for microtones)
    * ``amplitudes`` – weights (density, RMS, etc.)
    """
    pitches = np.asarray(pitches, dtype=float)
    amps = np.asarray(amplitudes, dtype=float)
    # Mask out non-finite values to avoid RuntimeWarnings (overflow/invalid)
    finite = np.isfinite(pitches) & np.isfinite(amps)
    pitches = np.where(finite, pitches, 0.0)
    amps = np.where(finite, amps, 0.0)
    total = amps.sum()
    if total <= 0 or len(pitches) == 0:
        return {
            "centroid": {"frequency": 0.0, "note": "Invalid"},
            "spread": {"deviation": 0.0},
            "spectral_skewness": 0.0,
        }

    centroid_midi = (pitches * amps).sum() / total
    spread_midi = np.sqrt(np.maximum(0, ((pitches - centroid_midi) ** 2 * amps).sum() / total))
    if spread_midi > 0:
        skew_num = ((pitches - centroid_midi) ** 3 * amps).sum() / total
        skewness = skew_num / (spread_midi ** 3)
    else:
        skewness = 0.0

    centroid_freq = midi_to_hz(centroid_midi)
    spread_freq = midi_to_hz(centroid_midi + spread_midi) - centroid_freq if spread_midi > 0 else 0.0

    return {
        "centroid": {"frequency": centroid_freq, "note": _hz_to_centroid_note(centroid_freq)},
        "spread": {"deviation": spread_freq},
        "spectral_skewness": skewness,
    }


def calculate_extended_spectral_moments(
    pitches: List[float] | np.ndarray,
    amplitudes: List[float] | np.ndarray
) -> Dict[str, float | Dict[str, float]]:
    """
    Calcula momentos espectrais estendidos incluindo kurtosis, flatness, roll-off e entropia.
    
    Esta função estende calculate_spectral_moments() com métricas adicionais:
    - Kurtosis: Mede a "cauda" da distribuição espectral
    - Flatness: Razão entre média geométrica e aritmética (mede uniformidade)
    - Roll-off: Frequência abaixo da qual 85% da energia está concentrada
    - Entropia: Mede a "desordem" ou uniformidade do espectro
    
    Args:
        pitches: Array de valores MIDI das notas (aceita floats para microtons).
        amplitudes: Array de amplitudes correspondentes (densidade, RMS, etc.).
            Deve ter o mesmo comprimento que pitches.
    
    Returns:
        Dicionário com todas as métricas espectrais:
            - Centróide: Frequência e nota do centróide
            - Dispersão: Desvio padrão espectral
            - Assimetria: Skewness espectral
            - spectral_kurtosis: Curtose espectral
            - spectral_flatness: Planura espectral (0-1)
            - spectral_rolloff: Frequência de roll-off (Hz)
            - spectral_entropy: Entropia espectral (bits)
    
    Example:
        >>> pitches = [60.0, 64.0, 67.0, 72.0]
        >>> amplitudes = [1.0, 1.5, 1.2, 1.8]
        >>> result = calculate_extended_spectral_moments(pitches, amplitudes)
        >>> print(result['spectral_entropy'])
        1.85...
    """
    # Obter resultados básicos
    base = calculate_spectral_moments(pitches, amplitudes)
    
    # Preparar arrays
    pitches = _safe_array(pitches)
    amps = _safe_array(amplitudes)
    
    # Verificar por entrada vazia ou inválida
    total = amps.sum()
    if total <= 0 or len(pitches) == 0 or len(amps) == 0:
        # Adicionar métricas estendidas como zeros
        base.update({
            "spectral_kurtosis": 0.0,
            "spectral_flatness": 0.0,
            "spectral_rolloff": 0.0,
            "spectral_entropy": 0.0,
        })
        return base

    # Recuperar centróide já calculado (MIDI)
    centroid_midi = (pitches * amps).sum() / total
    
    # Calcular dispersão (spread)
    spread_midi = np.sqrt(np.maximum(0, ((pitches - centroid_midi) ** 2 * amps).sum() / total))
    
    # Calcular curtose (kurtosis)
    if spread_midi > 0:
        kurt_num = ((pitches - centroid_midi) ** 4 * amps).sum() / total
        kurtosis = kurt_num / (spread_midi ** 4) - 3
    else:
        kurtosis = 0.0

    # Calcular planura espectral (flatness) - razão entre média geométrica e média aritmética
    nz_amps = amps[amps > 1e-10]  # Usar apenas amplitudes não-zero
    if len(nz_amps) > 0:
        # Média geométrica / média aritmética
        flatness = np.exp(np.log(nz_amps).mean()) / nz_amps.mean()
    else:
        flatness = 0.0

    # Calcular roll-off (85%)
    if len(pitches) > 0:
        cumsum = np.cumsum(amps)
        threshold = 0.85 * cumsum[-1]
        idx = np.searchsorted(cumsum, threshold)
        rolloff_midi = pitches[min(idx, len(pitches)-1)]
        rolloff_freq = midi_to_hz(rolloff_midi)
    else:
        rolloff_freq = 0.0

    # Calcular entropia espectral
    # Normalizar amplitudes para formar uma distribuição de probabilidade
    prob = amps / total
    
    # Filtrar probabilidades muito pequenas que causariam problemas no log
    valid_mask = prob > 1e-10
    if np.any(valid_mask):
        valid_probs = prob[valid_mask]
        if len(valid_probs) <= 1:
            entropy = 0.0
        else:
            entropy = float(-np.sum(valid_probs * np.log2(valid_probs)))
    else:
        entropy = 0.0
    entropy = max(0.0, float(entropy))

    # Adicionar métricas estendidas ao dicionário de resultados
    base.update({
        "spectral_kurtosis": kurtosis,
        "spectral_flatness": flatness,
        "spectral_rolloff": rolloff_freq,
        "spectral_entropy": entropy,
    })
    return base

################################################################################
# 4. VETOR DE CHROMA                                                          #
################################################################################

def calculate_chroma_vector(
    pitches: List[float] | np.ndarray,
    amplitudes: List[float] | np.ndarray | None = None
) -> List[float]:
    """
    Calcula o vetor de chroma (distribuição de energia por classe de altura).
    
    O vetor de chroma representa a distribuição de energia espectral entre
    as 12 classes de altura (C, C#, D, D#, E, F, F#, G, G#, A, A#, B),
    independentemente da oitava. É útil para análise harmônica e reconhecimento
    de acordes.
    
    Args:
        pitches: Array de valores MIDI das notas (aceita floats para microtons).
        amplitudes: Array opcional de amplitudes correspondentes.
            Se None, todas as notas têm amplitude igual (1.0).
            Deve ter o mesmo comprimento que pitches se fornecido.
    
    Returns:
        Lista de 12 valores float representando a energia normalizada em cada
        classe de altura (C, C#, D, ..., B). Valores somam 1.0 se houver energia.
    
    Example:
        >>> pitches = [60.0, 64.0, 67.0]  # C4, E4, G4
        >>> amplitudes = [1.0, 1.5, 1.2]
        >>> chroma = calculate_chroma_vector(pitches, amplitudes)
        >>> print(chroma[0])  # C chroma
        0.27...
        >>> print(chroma[4])  # E chroma
        0.40...
    """
    pitches = _safe_array(pitches)
    amps = _safe_array(amplitudes) if amplitudes is not None else np.ones_like(pitches)
    
    # Inicializar vetor de chroma
    chroma = np.zeros(12)
    
    # Acumular energia em cada classe de alturas
    for p, a in zip(pitches, amps):
        if not np.isnan(p) and not np.isinf(p):
            chroma[int(round(p)) % 12] += a
    
    # Normalizar se houver valores não-zero
    total = chroma.sum()
    if total > 0:
        chroma /= total
        
    return chroma.tolist()

################################################################################
# 5. RAZÃO HARMÔNICA                                                          #
################################################################################

def calculate_harmonic_ratio(
    pitches: List[float] | np.ndarray,
    amplitudes: List[float] | np.ndarray | None = None,
    fundamental: float | None = None
) -> float:
    """
    Calcula a razão harmônica: proporção de energia em harmônicos vs. fundamental.
    
    A razão harmônica mede quanto do espectro consiste em harmônicos (múltiplos
    inteiros da frequência fundamental) versus componentes não-harmônicos.
    Valores próximos de 1.0 indicam espectro altamente harmônico, enquanto
    valores próximos de 0.0 indicam espectro inarmônico.
    
    Args:
        pitches: Array de valores MIDI das notas (aceita floats para microtons).
        amplitudes: Array opcional de amplitudes correspondentes.
            Se None, todas as notas têm amplitude igual (1.0).
        fundamental: Frequência fundamental em Hz (opcional).
            Se None, tenta detectar automaticamente a partir dos pitches.
    
    Returns:
        Razão harmônica (0.0 a 1.0):
            - 1.0: Espectro completamente harmônico
            - 0.0: Espectro completamente inarmônico
            - Valores intermediários: Mistura de harmônicos e não-harmônicos
    
    Example:
        >>> pitches = [60.0, 72.0, 84.0]  # C4, C5, C6 (harmônicos)
        >>> amplitudes = [1.0, 0.8, 0.6]
        >>> ratio = calculate_harmonic_ratio(pitches, amplitudes)
        >>> print(ratio)  # Should be close to 1.0
        0.95...
    """
    # Verificar entrada vazia
    if not pitches:
        return 0.0

    # Preparar arrays
    pitches = _safe_array(pitches)
    amps = np.ones_like(pitches) if amplitudes is None else _safe_array(amplitudes)
    
    # Remover valores NaN ou Inf
    valid_mask = ~(np.isnan(pitches) | np.isinf(pitches))
    pitches = pitches[valid_mask]
    amps = amps[valid_mask]
    
    # Verificar se ainda temos dados válidos
    if len(pitches) == 0:
        return 0.0

    # Determinar fundamental se não fornecida
    if fundamental is None:
        fundamental = pitches.min()

    # Calcular distâncias (em semitons) à fundamental
    intervals = pitches - fundamental
    
    # Identificar harmônicos (intervalos próximos a múltiplos de 12 semitons)
    harmonic_mask = np.isclose(intervals % 12, 0, atol=0.25)

    # Calcular razão de energia
    harm_energy = amps[harmonic_mask].sum()
    total_energy = amps.sum()
    
    return float(harm_energy / total_energy) if total_energy > 0 else 0.0

################################################################################
# API pública                                                                  #
################################################################################
__all__ = [
    "calculate_spectral_moments",
    "calculate_extended_spectral_moments",
    "calculate_chroma_vector",
    "robust_gaussian_kde",
    "calculate_harmonic_ratio",
]