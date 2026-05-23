# plot_spectrogram.py
"""
Spectrogram-style visualization of spectral density results.

Creates spectrogram-like views of spectral density distribution across
pitches/frequencies and notes/instruments from notated symbolic input only.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple
import logging

from microtonal import midi_to_hz, midi_to_note_name
from utils.plotting_style import (
    create_professional_figure,
    enhance_axes,
    finalize_figure,
    DISPLAY_DPI,
    PUBLICATION_DPI,
)

logger = logging.getLogger(__name__)


def plot_spectrogram_density(
    pitches: List[float],
    densities: List[float],
    notes: Optional[List[str]] = None,
    instruments: Optional[List[str]] = None,
    title: str = "Spectral Density Spectrogram",
    filename: Optional[str] = None,
    figsize: Tuple[float, float] = (12, 8),
    dpi: int = None
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Creates a spectrogram-like visualization of spectral density from input pitches.

    Args:
        pitches: List of MIDI values from notated events
        densities: List of corresponding symbolic density weights
        notes: Optional list of note names (for labels)
        instruments: Optional list of instruments (for labels)
        title: Plot title
        filename: Optional path to save the figure
        figsize: Figure size (width, height)
        dpi: Figure resolution

    Returns:
        Tuple (fig, ax) of matplotlib figure and axes
    """
    dpi = dpi or DISPLAY_DPI
    try:
        if not pitches or not densities or len(pitches) != len(densities):
            logger.warning("Invalid data for spectrogram")
            return None, None

        pitches_array = np.array(pitches)
        densities_array = np.array(densities)
        densities_array = np.maximum(densities_array, 0)

        fig, axes = create_professional_figure(nrows=1, ncols=1, figsize=figsize, dpi=dpi)
        ax = axes[0] if isinstance(axes, np.ndarray) else axes

        if notes:
            num_primary = len(notes)
        else:
            num_primary = len(pitches)

        midi_min = max(0, int(np.floor(np.min(pitches_array))) - 2)
        midi_max = min(127, int(np.ceil(np.max(pitches_array))) + 2)
        midi_range = midi_max - midi_min

        freq_bins = np.linspace(midi_min, midi_max, midi_range * 4 + 1)

        if notes:
            time_axis = np.arange(len(notes))
            time_labels = [f"{n}" for n in notes]
        else:
            time_axis = np.arange(len(pitches))
            time_labels = [f"Tone {i+1}" for i in range(len(pitches))]

        spectrogram = np.zeros((len(freq_bins) - 1, len(time_axis)))

        for i, (pitch, density) in enumerate(zip(pitches_array, densities_array)):
            freq_idx = np.searchsorted(freq_bins, pitch) - 1
            freq_idx = np.clip(freq_idx, 0, len(freq_bins) - 2)
            time_idx = i if i < len(time_axis) else len(time_axis) - 1
            spectrogram[freq_idx, time_idx] += density

        from scipy import ndimage
        try:
            spectrogram = ndimage.gaussian_filter(spectrogram, sigma=(0.5, 0.3))
        except ImportError:
            logger.warning("scipy not available, skipping smoothing")

        freq_centers = midi_to_hz((freq_bins[:-1] + freq_bins[1:]) / 2)
        time_mesh, freq_mesh = np.meshgrid(time_axis, freq_centers)

        im = ax.pcolormesh(
            time_mesh,
            freq_mesh,
            spectrogram,
            shading='gouraud',
            cmap='viridis',
            vmin=0,
            vmax=np.max(spectrogram) if np.max(spectrogram) > 0 else 1
        )

        cbar = plt.colorbar(im, ax=ax, pad=0.02)
        cbar.set_label('Densidade Espectral', fontsize=10, rotation=270, labelpad=15)

        ax.set_xlabel('Nota/Instrumento', fontsize=10)
        ax.set_ylabel('Frequência (Hz)', fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')

        if notes and len(notes) <= 20:
            ax.set_xticks(time_axis)
            ax.set_xticklabels(time_labels, rotation=45, ha='right', fontsize=9)
        else:
            ax.set_xticks(time_axis[::max(1, len(time_axis)//10)])
            ax.set_xticklabels(
                [time_labels[i] for i in range(0, len(time_labels), max(1, len(time_labels)//10))],
                rotation=45, ha='right', fontsize=9,
            )

        y_ticks = ax.get_yticks()
        for freq in y_ticks:
            if freq > 0:
                midi_val = 69 + 12 * np.log2(freq / 440.0)
                note_name = midi_to_note_name(midi_val, include_cents=False)

        ax.grid(True, alpha=0.3, linestyle='--')

        if notes:
            for i, (note, pitch, density) in enumerate(
                zip(notes[:num_primary], pitches_array[:num_primary], densities_array[:num_primary])
            ):
                freq = midi_to_hz(pitch)
                if density > np.max(spectrogram) * 0.1:
                    ax.annotate(
                        note,
                        xy=(i, freq),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8,
                        color='white',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.6),
                        arrowprops=dict(arrowstyle='->', color='white', lw=0.5)
                    )

        enhance_axes(ax, grid=False)
        finalize_figure(fig)
        if filename:
            fig.savefig(filename, dpi=PUBLICATION_DPI, bbox_inches='tight', facecolor='white', edgecolor='none')
            logger.info(f"Espectrograma salvo em: {filename}")

        plt.show()
        return fig, ax

    except Exception as e:
        logger.error(f"Error creating spectrogram: {e}", exc_info=True)
        return None, None


def plot_spectrogram_3d(
    pitches: List[float],
    densities: List[float],
    notes: Optional[List[str]] = None,
    instruments: Optional[List[str]] = None,
    title: str = "Espectrograma 3D de Densidade Espectral",
    filename: Optional[str] = None,
    figsize: Tuple[float, float] = (14, 10),
    dpi: int = None
) -> Tuple[plt.Figure, plt.Axes]:
    """Create a 3D spectrogram-like visualization from input pitches only."""
    dpi = dpi or DISPLAY_DPI
    try:
        from mpl_toolkits.mplot3d import Axes3D
        if not pitches or not densities or len(pitches) != len(densities):
            logger.warning("Invalid data for 3D spectrogram")
            return None, None
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111, projection='3d')

        pitches_array = np.array(pitches)
        densities_array = np.array(densities)

        midi_min = max(0, int(np.floor(np.min(pitches_array))) - 2)
        midi_max = min(127, int(np.ceil(np.max(pitches_array))) + 2)
        freq_bins = np.linspace(midi_min, midi_max, (midi_max - midi_min) * 4 + 1)

        time_axis = np.arange(len(pitches))
        spectrogram = np.zeros((len(freq_bins) - 1, len(time_axis)))

        for i, (pitch, density) in enumerate(zip(pitches_array, densities_array)):
            freq_idx = np.searchsorted(freq_bins, pitch) - 1
            freq_idx = np.clip(freq_idx, 0, len(freq_bins) - 2)
            time_idx = i if i < len(time_axis) else len(time_axis) - 1
            spectrogram[freq_idx, time_idx] += density

        freq_centers = midi_to_hz((freq_bins[:-1] + freq_bins[1:]) / 2)
        X, Y = np.meshgrid(time_axis, freq_centers)

        surf = ax.plot_surface(
            X, Y, spectrogram,
            cmap='viridis',
            alpha=0.9,
            linewidth=0,
            antialiased=True
        )

        ax.set_xlabel('Note/Instrument', fontsize=10)
        ax.set_ylabel('Frequency (Hz)', fontsize=10)
        ax.set_zlabel('Spectral Density', fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')

        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=20, pad=0.1)

        if filename:
            fig.savefig(filename, dpi=PUBLICATION_DPI, bbox_inches='tight', facecolor='white')
            logger.info(f"3D spectrogram saved to: {filename}")

        plt.show()
        return fig, ax

    except Exception as e:
        logger.error(f"Error creating 3D spectrogram: {e}", exc_info=True)
        return None, None
