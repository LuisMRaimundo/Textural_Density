# plot_metr_espectrais.py

import matplotlib.pyplot as plt
import numpy as np
from spectral_analysis import (
    calculate_spectral_moments,
    calculate_extended_spectral_moments,
    calculate_chroma_vector,
    robust_gaussian_kde,
)
from microtonal import midi_to_note_name, note_to_midi, frequency_to_note_name
from utils.serialize_utils import safe_show_figure
from utils.plotting_style import (
    create_professional_figure,
    enhance_axes,
    finalize_figure,
    add_value_labels,
    SCIENTIFIC_COLORS,
    SCIENTIFIC_PALETTE,
    get_color,
    PUBLICATION_DPI,
)


def plot_metricas_espectrais_completo(metrics, title="Spectral Metrics", filename=None):
    """
    Full plot of all spectral metrics (professional style).

    Args:
        metrics: Dict of spectral metrics
        title: Plot title
        filename: Optional path to save the figure

    Returns:
        Tuple (fig, ax) of matplotlib figure and axes
    """
    fig, axes = create_professional_figure(nrows=1, ncols=1, figsize=(10, 6))
    ax = axes[0] if isinstance(axes, np.ndarray) else axes
    
    # Extrair todos os valores com verificação de segurança
    metrics_values = {
        'centroid': {
            'valor': metrics.get('centroid', 0),
            'formato': '{:.2f} Hz',
            'cor': SCIENTIFIC_COLORS['primary'],
            'unidade': 'Hz'
        },
        'spread': {
            'valor': metrics.get('spread', 0),
            'formato': '{:.2f} Hz',
            'cor': SCIENTIFIC_COLORS['secondary'],
            'unidade': 'Hz'
        },
        'Skewness': {
            'valor': metrics.get('skewness', 0),
            'formato': '{:.4f}',
            'cor': SCIENTIFIC_COLORS['accent'],
            'unidade': ''
        },
        'Kurtosis': {
            'valor': metrics.get('kurtosis', 0),
            'formato': '{:.4f}',
            'cor': SCIENTIFIC_COLORS['success'],
            'unidade': ''
        },
        'Flatness': {
            'valor': metrics.get('flatness', 0),
            'formato': '{:.4f}',
            'cor': SCIENTIFIC_COLORS['warning'],
            'unidade': ''
        },
        'Entropy': {
            'valor': metrics.get('entropy', 0),
            'formato': '{:.4f}',
            'cor': get_color(5),
            'unidade': 'bits'
        }
    }
    
    # Sanitizar valores para evitar erros de plotagem
    for key in metrics_values:
        valor = metrics_values[key]['valor']
        if np.isnan(valor) or np.isinf(valor):
            metrics_values[key]['valor'] = 0
    
    # Extrair dados para o gráfico
    labels = list(metrics_values.keys())
    valores = [metrics_values[k]['valor'] for k in labels]
    cores = [metrics_values[k]['cor'] for k in labels]

    # Escalas de referência por métrica: cada barra = (valor / ref) * 5, limitado a [-5, 5].
    # Assim a altura visual é sempre proporcional ao valor real (sem misturar Hz com adimensionais).
    REFS = {
        'centroid': None,       # not plotted as bar
        'spread': 100.0,        # Hz reference for scale
        'Skewness': 2.0,
        'Kurtosis': 2.0,
        'Flatness': 1.0,
        'Entropia': 1.0,        # 0–1 bits
    }
    valores_normalizados = []
    for label, v in zip(labels, valores):
        if np.isnan(v) or np.isinf(v):
            v = 0
        ref = REFS.get(label)
        if label == 'centroid' or ref is None:
            valores_normalizados.append(0)
        else:
            s = (v / ref) * 5.0 if ref > 0 else 0
            valores_normalizados.append(max(-5.0, min(5.0, s)))
    
    # Criar gráfico de barras profissional
    bars = ax.bar(
        labels,
        valores_normalizados,
        color=cores,
        width=0.7,
        edgecolor='white',
        linewidth=1.5,
        alpha=0.9,
        zorder=3
    )
    
    # Adicionar rótulos e anotações profissionais
    for i, (label, bar, valor_original, valor_norm) in enumerate(zip(labels, bars, valores, valores_normalizados)):
        formato = metrics_values[label]['formato']
        cor = cores[i]
        
        if label == 'centroid':
            # Mostrar nota e frequência para centróide
            nota = metrics.get('centroid_note', frequency_to_note_name(valor_original))
            ax.text(
                i, 0.5,
                f"{nota}\n{formato.format(valor_original)}",
                ha='center',
                va='center',
                fontsize=11,
                fontweight='bold',
                color='white',
                bbox=dict(
                    facecolor=cor,
                    boxstyle='round,pad=0.5',
                    alpha=0.95,
                    edgecolor='white',
                    linewidth=1.5
                ),
                zorder=4
            )
        else:
            # Mostrar valor formatado acima da barra
            altura = bar.get_height()
            offset = max(valores_normalizados) * 0.05
            y_pos = altura + offset if altura >= 0 else altura - offset
            
            valor_texto = formato.format(valor_original)
            unidade = metrics_values[label]['unidade']
            # Evitar duplicar unidade (ex.: "26.04 Hz" + "Hz" -> "26.04 Hz Hz")
            if unidade and unidade not in valor_texto:
                texto_completo = f"{valor_texto}\n{unidade}"
            else:
                texto_completo = valor_texto
            
            ax.text(
                i, y_pos,
                texto_completo,
                ha='center',
                va='bottom' if altura >= 0 else 'top',
                fontsize=10,
                fontweight='bold',
                color=SCIENTIFIC_COLORS['dark'],
                bbox=dict(
                    facecolor='white',
                    edgecolor=cor,
                    boxstyle='round,pad=0.3',
                    alpha=0.95,
                    linewidth=1.5
                ),
                zorder=4
            )
    
    enhance_axes(
        ax,
        title=title,
        xlabel=r'Metric',
        ylabel=r'Normalized value (ref. scale)',
        grid=True
    )
    
    # Rotacionar labels do eixo X se necessário
    ax.tick_params(axis='x', rotation=0)
    
    # Ajustar limites do eixo Y
    y_max = max(valores_normalizados) * 1.15 if valores_normalizados else 1.0
    y_min = min(0, min(valores_normalizados) * 1.15) if valores_normalizados else -0.5
    ax.set_ylim(y_min, y_max)
    
    # Adicionar linha de referência no zero
    ax.axhline(y=0, color=SCIENTIFIC_COLORS['neutral'], linestyle='-', linewidth=1.0, alpha=0.5, zorder=1)
    
    finalize_figure(fig)
    if filename:
        fig.savefig(filename, dpi=PUBLICATION_DPI, bbox_inches='tight', facecolor='white', edgecolor='none')
    
    return fig, ax


def extract_and_plot_metrics(notas, instrumentos, numeros_instrumentos, densidades_instrumento, note_to_midi_func=None):
    """
    Versão atualizada que passa a nota do centróide explicitamente
    """
    try:
        # Converter notas para MIDI
        if note_to_midi_func is None:
            note_to_midi_func = note_to_midi
        
        pitches = [note_to_midi_func(nota) for nota in notas]
        amplitudes = densidades_instrumento
        
        # 1. Calcular os momentos espectrais básicos
        spectral_results = calculate_spectral_moments(pitches, amplitudes)
        
        # 2. Calcular métricas estendidas explicitamente
        extended_metrics = calculate_extended_spectral_moments(pitches, amplitudes)
        
        # 3. Combinar os resultados
        centroid_freq = spectral_results.get("centroid", {}).get("frequency", 0)
        centroid_note = spectral_results.get("centroid", {}).get("note", "N/A")
        spread_hz = spectral_results.get("spread", {}).get("deviation", 0)
        
        # Obter métricas adicionais (mesma lógica anterior)
        skewness = spectral_results.get("spectral_skewness", 
                   extended_metrics.get("skewness", 
                   extended_metrics.get("spectral_skewness", 0)))
                   
        kurtosis = spectral_results.get("kurtosis", 
                  spectral_results.get("spectral_kurtosis", 
                  extended_metrics.get("kurtosis", 
                  extended_metrics.get("spectral_kurtosis", 0))))
                  
        flatness = spectral_results.get("flatness", 
                  spectral_results.get("spectral_flatness", 
                  extended_metrics.get("flatness", 
                  extended_metrics.get("spectral_flatness", 0))))
                  
        entropy = spectral_results.get("entropy", 
                 spectral_results.get("spectral_entropy", 
                 extended_metrics.get("entropy", 
                 extended_metrics.get("spectral_entropy", 0))))
        
        # Imprimir todas as métricas disponíveis
        print(f"Centroid: {centroid_freq:.2f} Hz, Note: {centroid_note}")
        print(f"Spread: ±{spread_hz:.2f} Hz")
        print(f"Skewness: {skewness:.4f}")
        print(f"Kurtosis: {kurtosis:.4f}")
        print(f"Flatness: {flatness:.4f}")
        print(f"Entropy: {entropy:.4f}")
        
        # Construir dicionário completo
        metrics = {
            'centroid': centroid_freq,
            'centroid_note': centroid_note,  # Passar a nota explicitamente
            'spread': spread_hz,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'flatness': flatness,
            'entropy': entropy
        }
        
        # Fechar figuras existentes
        plt.close('all')
        
        # Gerar o gráfico
        fig, ax = plot_metricas_espectrais_completo(metrics, title="Spectral Metrics")
        
        # Mostrar o gráfico
        safe_show_figure(fig)
        
        return metrics
    
    except Exception as e:
        print(f"Error processing spectral metrics: {e}")
        import traceback
        traceback.print_exc()
        return {}


def plot_chroma_vector(chroma_vector, title="Chroma Vector", filename=None):
    """
    Professional chroma vector visualization.

    Args:
        chroma_vector: List of 12 values for pitch classes
        title: Plot title
        filename: Optional path to save

    Returns:
        Tuple (fig, ax)
    """
    fig, ax = create_professional_figure(nrows=1, ncols=1, figsize=(8, 5))
    
    # Nomes das classes de altura
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Criar gráfico de barras circular (polar) ou linear
    bars = ax.bar(
        note_names,
        chroma_vector,
        color=[get_color(i) for i in range(12)],
        width=0.8,
        edgecolor='white',
        linewidth=1.5,
        alpha=0.85,
        zorder=3
    )
    
    # Adicionar valores nas barras
    for i, (bar, val) in enumerate(zip(bars, chroma_vector)):
        if val > 0.01:  # Só mostrar se significativo
            ax.text(
                i, val + max(chroma_vector) * 0.02,
                f'{val:.3f}',
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold',
                color=SCIENTIFIC_COLORS['dark']
            )
    
    enhance_axes(
        ax,
        title=title,
        xlabel=r'Pitch class',
        ylabel=r'Normalized energy',
        grid=True
    )
    
    ax.set_ylim(0, max(chroma_vector) * 1.15 if chroma_vector else 1.0)
    
    finalize_figure(fig)
    if filename:
        fig.savefig(filename, dpi=PUBLICATION_DPI, bbox_inches='tight', facecolor='white')

    return fig, ax


def plot_spectral_distribution(pitches, amplitudes, title="Spectral Distribution", filename=None):
    """
    Professional spectral distribution visualization.

    Args:
        pitches: Array of MIDI values
        amplitudes: Array of corresponding amplitudes
        title: Plot title
        filename: Optional path to save

    Returns:
        Tuple (fig, ax)
    """
    fig, ax = create_professional_figure(nrows=1, ncols=1, figsize=(10, 5))
    
    # Converter MIDI para frequência
    from microtonal import midi_to_hz
    frequencies = [midi_to_hz(p) for p in pitches]
    
    # Criar gráfico de barras ou linha
    bars = ax.bar(
        frequencies,
        amplitudes,
        width=(max(frequencies) - min(frequencies)) / len(frequencies) * 0.8 if len(frequencies) > 1 else 100,
        color=SCIENTIFIC_COLORS['primary'],
        edgecolor='white',
        linewidth=1.0,
        alpha=0.7,
        zorder=3
    )
    
    # Adicionar linha suave usando KDE se houver dados suficientes
    if len(pitches) > 3:
        try:
            kde = robust_gaussian_kde(np.array(pitches), weights=np.array(amplitudes))
            x_smooth = np.linspace(min(pitches), max(pitches), 200)
            y_smooth = kde(x_smooth)
            # Normalizar para escala de amplitudes
            y_smooth = y_smooth / y_smooth.max() * max(amplitudes) if y_smooth.max() > 0 else y_smooth
            freq_smooth = [midi_to_hz(p) for p in x_smooth]
            ax.plot(freq_smooth, y_smooth, color=SCIENTIFIC_COLORS['secondary'], linewidth=2.5, 
                   alpha=0.8, label='Smoothed distribution', zorder=4)
            ax.legend(loc='upper right', framealpha=0.95)
        except:
            pass  # Se KDE falhar, continuar sem linha suave
    
    enhance_axes(
        ax,
        title=title,
        xlabel=r'Frequência $f$ (Hz)',
        ylabel=r'Amplitude',
        grid=True
    )
    
    # Formatar eixo X para frequências
    ax.set_xscale('log')  # Escala logarítmica para frequências
    
    finalize_figure(fig)
    if filename:
        fig.savefig(filename, dpi=PUBLICATION_DPI, bbox_inches='tight', facecolor='white')

    return fig, ax


# Adicione este código ao final do arquivo para calcular explicitamente as métricas estendidas
def calculate_all_spectral_metrics(pitches, amplitudes):
    """
    Função que calcula TODAS as métricas espectrais possíveis.
    Useful to call directly when needed.
    """
    # Calcular métricas básicas
    basic_metrics = calculate_spectral_moments(pitches, amplitudes)
    
    # Calcular métricas estendidas
    extended_metrics = calculate_extended_spectral_moments(pitches, amplitudes)
    
    # Combinar os resultados
    all_metrics = {**basic_metrics}
    
    # Extrair métricas estendidas e adicionar ao dicionário
    if isinstance(extended_metrics, dict):
        for key, value in extended_metrics.items():
            all_metrics[key] = value
    
    return all_metrics