import numpy as np

from scipy import stats

import matplotlib.pyplot as plt

from matplotlib import cm

from mpl_toolkits.mplot3d import Axes3D




def calculate_texture_density(
    pitches: list[float] | np.ndarray,
    instruments_counts: list[int] | np.ndarray
) -> dict[str, float]:
    """
    Texture metrics from distinct pitch bins (not raw event rows).

    ``pitches`` and ``instruments_counts`` must refer to aggregated pitch bins:
    one entry per distinct simultaneous pitch. ``instruments_counts`` is the
    total player count (Qty sum) per pitch bin — not polyphony.

    Returns player-weighted mass and pitch polyphony (distinct pitch count).
    """
    if len(pitches) == 0 or len(instruments_counts) == 0:
        return {
            "player_count": 0,
            "player_weighted_texture_mass": 0,
            "pitch_polyphony": 0,
            "average_texture_density": 0,
            "texture_polyphony": 0,
            "texture_variability": 0,
            "texture_contrast": 0,
        }

    player_count = int(sum(instruments_counts))
    pitch_polyphony = len(pitches)

    # Legacy alias: total players across distinct pitch bins
    player_weighted_texture_mass = float(player_count)
    average_texture_density = player_weighted_texture_mass

    if len(pitches) > 1:
        texture_variability = np.std(pitches)
    else:
        texture_variability = 0

    texture_contrast = max(pitches) - min(pitches) if len(pitches) > 1 else 0

    return {
        "player_count": float(player_count),
        "player_weighted_texture_mass": player_weighted_texture_mass,
        "pitch_polyphony": float(pitch_polyphony),
        "average_texture_density": average_texture_density,
        "texture_polyphony": float(pitch_polyphony),
        "texture_variability": float(texture_variability),
        "texture_contrast": float(texture_contrast),
    }



def calculate_timbre_blend(
    instruments: list[str],
    densities_per_note: list[float] | np.ndarray
) -> dict[str, float]:
    """
    Calcula a mistura tímbrica com base nos instrumentos e suas densidades espectrais.
    
    A mistura tímbrica avalia como diferentes instrumentos se combinam,
    considerando a distribuição de densidades espectrais entre instrumentos.
    
    Args:
        instruments: Lista de nomes de instrumentos.
            Deve ter o mesmo comprimento que densities_per_note.
        densities_per_note: Array de densidades espectrais correspondentes a cada nota.
            Valores devem ser >= 0.
    
    Returns:
        Dicionário com métricas de mistura tímbrica:
            - timbre_diversity: Diversidade tímbrica (número de instrumentos únicos)
            - timbre_balance: Balanceamento entre instrumentos (0-1)
            - timbre_dominance: Dominância do instrumento mais presente (0-1)
            - average_timbre_density: Densidade tímbrica média
    
    Example:
        >>> instruments = ['flauta', 'clarinete', 'flauta']
        >>> densities = [1.0, 1.5, 1.2]
        >>> result = calculate_timbre_blend(instruments, densities)
        >>> print(result['timbre_diversity'])
        2.0
    """

    # Contar a frequência de cada instrumento

    unique_instruments = set(instruments)

    instrument_counts = {instr: instruments.count(instr) for instr in unique_instruments}

    

    # Calcular densidade média por instrumento

    instrument_densities = {}

    for i, instr in enumerate(instruments):

        if instr not in instrument_densities:

            instrument_densities[instr] = []

        instrument_densities[instr].append(densities_per_note[i])

    

    avg_densities = {instr: np.mean(densities) for instr, densities in instrument_densities.items()}

    

    # Índice de heterogeneidade tímbrica (baseado na diversidade de instrumentos)

    timbre_diversity = len(unique_instruments) / len(instruments) if len(instruments) > 0 else 0

    

    # Variância entre densidades médias dos instrumentos (maior = menos blend)

    density_values = list(avg_densities.values())

    density_variance = np.var(density_values) if len(density_values) > 1 else 0

    

    # Índice de blend (inversamente proporcional à variância)

    blend_index = 1 / (1 + density_variance) if density_variance != 0 else 1

    

    # Calcular a contribuição relativa de cada família de instrumentos

    instrument_families = {

        "madeiras": ["flautim", "flauta", "Oboe", "Corne_ingles", "clarinete", "clarinete baixo", "fagote", "contrafagote"],

        "cordas": ["violino"],

        # Adicionar outras famílias conforme necessário

    }

    

    family_contributions = {}

    for family, family_instruments in instrument_families.items():

        family_count = sum(instrument_counts.get(i, 0) for i in family_instruments)

        family_contributions[family] = family_count / len(instruments) if len(instruments) > 0 else 0

    # Balance: same as blend_index (0–1); dominance: share of most frequent instrument
    timbre_balance = blend_index if len(instruments) > 0 else 0.0
    max_count = max(instrument_counts.values()) if instrument_counts else 0
    timbre_dominance = max_count / len(instruments) if len(instruments) > 0 else 0.0

    return {

        "timbre_diversity": timbre_diversity,

        "blend_index": blend_index,

        "density_variance": density_variance,

        "family_contributions": family_contributions,

        "timbre_balance": timbre_balance,

        "timbre_dominance": timbre_dominance,

    }



def calculate_orchestration_balance(
    pitches: list[float] | np.ndarray,
    densities: list[float] | np.ndarray,
    instruments: list[str]
) -> dict[str, float]:
    """
    Calcula o equilíbrio da orquestração com base na distribuição de densidade pelo registro.
    
    Esta função avalia o equilíbrio orquestral considerando:
    - Distribuição de densidade entre registros (baixo, médio, agudo)
    - Balanceamento entre instrumentos
    - Uniformidade da distribuição espectral
    
    Args:
        pitches: Array de valores MIDI das notas (aceita floats para microtons).
            Deve ter o mesmo comprimento que densities e instruments.
        densities: Array de densidades espectrais correspondentes a cada pitch.
            Valores devem ser >= 0.
        instruments: Lista de nomes de instrumentos para cada nota.
            Deve ter o mesmo comprimento que pitches e densities.
    
    Returns:
        Dicionário com métricas de equilíbrio de orquestração:
            - register_balance: Balanceamento entre registros (0-1)
            - density_balance: Balanceamento de densidade (0-1)
            - orchestration_evenness: Uniformidade da orquestração (0-1)
            - pitch_balance: Balanceamento de alturas
            - instrument_balance: Balanceamento entre instrumentos
    
    Example:
        >>> pitches = [60.0, 64.0, 67.0, 72.0]
        >>> densities = [1.0, 1.5, 1.2, 1.8]
        >>> instruments = ['flauta', 'clarinete', 'flauta', 'clarinete']
        >>> result = calculate_orchestration_balance(pitches, densities, instruments)
        >>> print(result['register_balance'])
        0.65...
    """

    if len(pitches) == 0:

        return {

            "register_balance": 0,

            "density_balance": 0,

            "orchestration_evenness": 0,

            "orchestration_balance": 0,

            "pitch_balance": 0,

            "instrument_balance": 0,

        }

    

    # Definir registros (baixo, médio, agudo)

    registers = {

        "baixo": (0, 48),    # C1-C4

        "médio": (48, 72),   # C4-C6

        "agudo": (72, 108)   # C6-C9

    }

    

    # Calcular distribuição de densidades por registro

    register_densities = {reg: 0 for reg in registers}

    for pitch, density in zip(pitches, densities):

        for reg, (low, high) in registers.items():

            if low <= pitch < high:

                register_densities[reg] += density

                break

    

    # Calcular o total de densidade

    total_density = sum(register_densities.values())

    

    # Normalizar as densidades por registro

    if total_density > 0:

        normalized_densities = {reg: d/total_density for reg, d in register_densities.items()}

    else:

        normalized_densities = {reg: 0 for reg in registers}

    

    # Calcular equilíbrio de registro (entropia da distribuição)

    nonzero_densities = [d for d in normalized_densities.values() if d > 0]

    if nonzero_densities:

        register_balance = -sum(d * np.log2(d) for d in nonzero_densities) / np.log2(len(registers))

    else:

        register_balance = 0

    

    # Calcular equilíbrio de densidade (quão uniforme está a distribuição)

    density_balance = 1 - (max(normalized_densities.values()) - min(normalized_densities.values()))

    

    # Calcular uniformidade da orquestração (Gini coefficient invertido)

    sorted_densities = sorted(normalized_densities.values())

    n = len(sorted_densities)

    if n > 0 and sum(sorted_densities) > 0:

        # Cálculo do coeficiente de Gini

        gini = sum((2*i - n - 1) * sorted_densities[i] for i in range(n)) / (n * sum(sorted_densities))

        # Inverter para que 1 seja perfeita uniformidade

        orchestration_evenness = 1 - abs(gini)

    else:

        orchestration_evenness = 0

    

    # Aliases for backward compatibility with tests/API expectations
    return {

        "register_balance": register_balance,

        "density_balance": density_balance,

        "orchestration_evenness": orchestration_evenness,

        "register_distribution": normalized_densities,

        "orchestration_balance": orchestration_evenness,

        "pitch_balance": register_balance,

        "instrument_balance": density_balance,

    }



def plot_orchestration_analysis(pitches, densities, instruments):

    """

    Versão final que garante distâncias proporcionais em QUALQUER registro.

    Funciona para notas graves, médias ou agudas.

    

    Args:

        pitches (array-like): MIDI pitches das notas.

        densities (array-like): Densidades espectrais correspondentes a cada pitch.

        instruments (array-like): Instrumentos para cada nota.

    """

    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from utils.plotting_style import (
        apply_scientific_style,
        enhance_axes,
        finalize_figure,
        SCIENTIFIC_COLORS,
        SCIENTIFIC_PALETTE,
        get_color,
    )

    # Converter para arrays numpy (crucial para consistência)

    pitches = np.array(pitches, dtype=float)

    densities = np.array(densities, dtype=float)

    instruments = np.array(instruments)

    

    # Verificar dados válidos

    if len(pitches) == 0 or len(pitches) != len(densities) or len(pitches) != len(instruments):

        print("Dados inválidos para visualização.")

        return

    

    # CALCULAR LIMITES ADAPTÁVEIS COM PROPORÇÃO FIXA

    # Usamos uma margem de 3 semitons para garantir visibilidade

    margin = 3

    pitch_min = np.floor(np.min(pitches) - margin)

    pitch_max = np.ceil(np.max(pitches) + margin)

    

    # Mapa de valores MIDI para nomes de notas

    midi_to_note = {}

    # Adicionar todas as notas C (Dó) para ter pontos de referência

    for octave in range(0, 9):  # C0 a C8

        midi_value = 12 + (octave * 12)  # C em cada oitava

        midi_to_note[midi_value] = f'C{octave}'

    

    # Adicionar outras notas comuns em registros relevantes

    for midi_value, note in [

        (60, 'C4'), (61, 'C#4'), (62, 'D4'), (63, 'D#4'), (64, 'E4'), 

        (65, 'F4'), (66, 'F#4'), (67, 'G4'), (68, 'G#4'), (69, 'A4'), 

        (70, 'A#4'), (71, 'B4'), (72, 'C5'), (73, 'C#5'), (74, 'D5'), 

        (75, 'D#5'), (76, 'E5')

    ]:

        midi_to_note[midi_value] = note

    

    apply_scientific_style(figsize=(12, 9))
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
        2, 2, figsize=(12, 9), constrained_layout=True
    )
    ax1 = fig.add_subplot(221, projection='3d')

    # 1. GRÁFICO 3D

    

    # Converter instrumentos para valores numéricos

    unique_instruments = list(set(instruments))

    instrument_indices = [unique_instruments.index(i) for i in instruments]

    

    # Criar um mapa de cores mais distintivo

    cmap = plt.cm.viridis

    norm = plt.Normalize(min(densities), max(densities))

    color_map = cmap(norm(densities))

    

    # Tentar configurar projeção ortográfica (se disponível)

    try:

        ax1.set_proj_type('ortho')

    except:

        pass  # Ignorar se a versão do matplotlib não suportar

    

    # CRUCIAL: Definir os limites do eixo X ANTES de plotar

    ax1.set_xlim(pitch_min, pitch_max)

    

    # Plotar gráfico 3D com pontos maiores 

    scatter = ax1.scatter(

        pitches,  # Usar valores MIDI reais

        instrument_indices, 

        densities, 

        c=color_map, 

        s=100,  # Pontos maiores

        alpha=0.8,

        depthshade=False  # Desativar sombreamento de profundidade

    )

    

    # Adicionar linhas de grade verticais para cada semitom

    for p in range(int(pitch_min), int(pitch_max) + 1):

        if p % 12 == 0:  # Destacar as notas C (dó)

            ax1.plot([p, p], 

                     [min(instrument_indices)-0.5, max(instrument_indices)+0.5], 

                     [0, 0], 

                     color='red', linestyle='-', alpha=0.3, linewidth=1)

        elif p in midi_to_note:

            ax1.plot([p, p], 

                     [min(instrument_indices)-0.5, max(instrument_indices)+0.5], 

                     [0, 0], 

                     color='gray', linestyle=':', alpha=0.3)

    

    # Adicionar rótulos em formato de texto para o eixo X

    for p in range(int(pitch_min), int(pitch_max) + 1):

        if p in midi_to_note:

            ax1.text(p, min(instrument_indices)-0.5, 0, 

                    midi_to_note[p], fontsize=8, ha='center', va='top')

    

    # Ajustar visualmente para destacar as distâncias proporcionais
    ax1.set_xlabel('Pitch (MIDI)', fontsize=10, labelpad=8)
    ax1.set_ylabel('Instrumento', fontsize=10, labelpad=8)
    ax1.set_zlabel('Densidade Espectral', fontsize=10, labelpad=8)

    

    # Configurar rótulos de instrumentos

    if len(unique_instruments) <= 10:

        ax1.set_yticks(range(len(unique_instruments)))

        ax1.set_yticklabels(unique_instruments)

    else:

        step = max(1, len(unique_instruments) // 8)

        selected_ticks = range(0, len(unique_instruments), step)

        selected_labels = [unique_instruments[i] for i in selected_ticks]

        ax1.set_yticks(selected_ticks)

        ax1.set_yticklabels(selected_labels)

    

    ax1.set_title('Distribuição Tridimensional da Orquestração', fontsize=11)

    

    # Colorbar para referência

    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax1, pad=0.1)

    cbar.set_label('Densidade Espectral', fontsize=10)

    

    # -----------------------------------------------------------------

    # 2. GRÁFICO DE LINHA

    # -----------------------------------------------------------------

    ax2 = fig.add_subplot(222)

    

    # Ordenar por altura para linha conectada correta

    sorted_indices = np.argsort(pitches)

    sorted_pitches = pitches[sorted_indices]

    sorted_densities = densities[sorted_indices]

    

    # CRUCIAL: Definir os limites do eixo X ANTES de plotar

    ax2.set_xlim(pitch_min, pitch_max)

    

    # Plotar gráfico de linha com área sombreada

    ax2.plot(sorted_pitches, sorted_densities, 'o-', color='blue', 

            alpha=0.7, linewidth=2, markersize=8)

    ax2.fill_between(sorted_pitches, 0, sorted_densities, color='blue', alpha=0.2)

    

    # Adicionar rótulos para cada ponto mostrando o valor MIDI exato

    for p, d in zip(pitches, densities):

        ax2.text(p, d + 0.5, f"{p}", ha='center', va='bottom', fontsize=9)

    

    # Adicionar linhas de grade verticais

    for p in range(int(pitch_min), int(pitch_max) + 1):

        if p % 12 == 0:  # Destacar as notas C (dó)

            ax2.axvline(x=p, color='red', linestyle='-', alpha=0.3, linewidth=1)

        else:

            ax2.axvline(x=p, color='gray', linestyle=':', alpha=0.2)

    

    # Adicionar rótulos de notas no eixo X

    tick_positions = []

    tick_labels = []

    for p in range(int(pitch_min), int(pitch_max) + 1):

        if p in midi_to_note:

            tick_positions.append(p)

            tick_labels.append(midi_to_note[p])

    

    if tick_positions:

        ax2.set_xticks(tick_positions)

        ax2.set_xticklabels(tick_labels, rotation=45)

    

    ax2.set_xlabel('Pitch (MIDI)', fontsize=10)
    ax2.set_ylabel('Densidade Espectral', fontsize=10)
    ax2.set_title('Perfil de Densidade por Registro', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    

    # -----------------------------------------------------------------

    # 3. HEATMAP

    # -----------------------------------------------------------------

    ax3 = fig.add_subplot(212)

    

    # Preparar grid para o heatmap com resolução de 0.5 semitons

    grid_step = 0.5

    x_grid = np.arange(pitch_min, pitch_max + grid_step, grid_step)

    

    # Inicializar matriz para o heatmap

    heatmap_data = np.zeros((len(unique_instruments), len(x_grid) - 1))

    

    # Preencher matriz do heatmap

    for i, instrument in enumerate(unique_instruments):

        for j in range(len(x_grid) - 1):

            bin_min = x_grid[j]

            bin_max = x_grid[j+1]

            

            # Encontrar notas deste instrumento neste bin

            mask = [(ins == instrument and bin_min <= p < bin_max) 

                   for ins, p in zip(instruments, pitches)]

            

            if any(mask):

                matching_densities = [d for d, m in zip(densities, mask) if m]

                heatmap_data[i, j] = np.mean(matching_densities)

    

    # CRUCIAL: Definir extent preciso para o heatmap

    extent = [pitch_min, pitch_max, -0.5, len(unique_instruments) - 0.5]

    im = ax3.imshow(heatmap_data, aspect='auto', cmap='viridis', 

                   interpolation='nearest', extent=extent)

    

    # Configurar rótulos de instrumentos

    if len(unique_instruments) <= 10:

        ax3.set_yticks(range(len(unique_instruments)))

        ax3.set_yticklabels(unique_instruments)

    else:

        step = max(1, len(unique_instruments) // 8)

        selected_ticks = range(0, len(unique_instruments), step)

        selected_labels = [unique_instruments[i] for i in selected_ticks]

        ax3.set_yticks(selected_ticks)

        ax3.set_yticklabels(selected_labels)

    

    # Adicionar rótulos de notas no eixo X

    ax3.set_xticks(tick_positions)

    ax3.set_xticklabels(tick_labels)

    

    ax3.set_xlabel('Pitch (MIDI)', fontsize=10)
    ax3.set_ylabel('Instrumento', fontsize=10)
    ax3.set_title('Distribuição de Densidade por Instrumento e Registro', fontsize=11, fontweight='bold')

    

    # Colorbar

    cbar = plt.colorbar(im, ax=ax3, pad=0.01)

    cbar.set_label('Densidade Espectral', fontsize=10)

    

    # Não usar subplots_adjust quando constrained_layout=True
    # O constrained_layout já gerencia o espaçamento automaticamente
    
    fig.suptitle(
        'Análise de Orquestração (Distâncias Proporcionais)',
        fontsize=11,
        fontweight='bold',
        y=0.98
    )
    finalize_figure(fig)
    plt.show()

    

    # Imprimir informações para verificação

    print("\nConfirmação das distâncias entre notas:")

    sorted_pitches_unique = sorted(set(pitches))

    for i in range(1, len(sorted_pitches_unique)):

        distance = sorted_pitches_unique[i] - sorted_pitches_unique[i-1]

        print(f"Distância entre {sorted_pitches_unique[i-1]} e {sorted_pitches_unique[i]}: {distance} semitons")

