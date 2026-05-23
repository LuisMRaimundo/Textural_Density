"""
Professional scientific plotting style configuration.

Publication-ready defaults: clean theme (ggplot or seaborn whitegrid),
sophisticated palette (viridis/magma), LaTeX math in labels, no top/right spines,
subtle grid, DPI 300, tight_layout, minimal chart junk.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from typing import Optional, Dict, Tuple

# ============================================================================
# THEME AND STYLE
# ============================================================================

def _apply_theme():
    """Apply clean theme: seaborn whitegrid (matplotlib built-in) or ggplot."""
    for style_name in ('seaborn-v0_8-whitegrid', 'seaborn-whitegrid', 'ggplot'):
        try:
            plt.style.use(style_name)
            break
        except (OSError, KeyError):
            continue


def _get_cmap(name: str):
    """Get colormap (compatible with matplotlib 3.4+)."""
    try:
        return mpl.colormaps.get_cmap(name)
    except AttributeError:
        return mpl.cm.get_cmap(name)


def _get_palette_colors(name: str = 'viridis', n: int = 10) -> list:
    """Return list of hex colors from a matplotlib colormap (viridis or magma)."""
    cmap = _get_cmap(name)
    colors = [mpl.colors.to_hex(cmap(x)) for x in np.linspace(0.15, 0.85, n)]
    return colors


# Sophisticated palettes (viridis primary; magma alternative)
VIRIDIS_PALETTE = _get_palette_colors('viridis', 10)
MAGMA_PALETTE = _get_palette_colors('magma', 10)

# Legacy names for backward compatibility
SCIENTIFIC_COLORS = {
    'primary': VIRIDIS_PALETTE[2],    # blue-green
    'secondary': VIRIDIS_PALETTE[5],  # yellow-green
    'accent': VIRIDIS_PALETTE[7],     # yellow
    'success': VIRIDIS_PALETTE[3],
    'warning': MAGMA_PALETTE[2],
    'neutral': '#9e9e9e',
    'dark': '#212529',
    'light': '#fafafa',
}
SCIENTIFIC_PALETTE = VIRIDIS_PALETTE
SEQUENTIAL_PALETTE = _get_palette_colors('viridis', 256)[::256//7][:7]
DIVERGING_PALETTE = list(reversed(_get_palette_colors('magma', 5))) + list(_get_palette_colors('viridis', 5))

# Grid: subtle gray
GRID_COLOR = '#d0d0d0'
GRID_ALPHA = 0.6
GRID_LINESTYLE = '-'
GRID_LINEWIDTH = 0.5

# DPI: use display for on-screen/GUI (fits monitor), publication for saved files
DISPLAY_DPI = 96   # on-screen and embedded figures
PUBLICATION_DPI = 300  # savefig() for print/export

# ============================================================================
# TYPOGRAPHY
# ============================================================================

def configure_typography(font_family: str = 'sans-serif', font_size: float = 10):
    """
    Configure typography. Use mathtext for LaTeX-like math in labels (e.g. r'$\\lambda$').
    """
    plt.rcParams.update({
        'font.family': font_family,
        'font.size': font_size,
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Liberation Sans', 'Helvetica', 'sans-serif'],
        'font.serif': ['DejaVu Serif', 'Times New Roman', 'Liberation Serif', 'Times', 'serif'],
        'axes.titlesize': font_size + 2,
        'axes.labelsize': font_size,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'legend.fontsize': font_size - 1,
        'figure.titlesize': font_size + 4,
        # LaTeX-style math in labels (mathtext, no external LaTeX required)
        'mathtext.fontset': 'dejavusans',
        'mathtext.default': 'regular',
    })


# ============================================================================
# STYLE CONFIGURATION
# ============================================================================

def apply_scientific_style(figsize: Tuple[float, float] = (10, 6), dpi: int = DISPLAY_DPI):
    """
    Apply publication-ready style: theme, palette, typography, grid, save defaults.
    """
    _apply_theme()
    configure_typography()

    # Color cycle from viridis for lines/patches
    plt.rcParams['axes.prop_cycle'] = mpl.cycler(color=VIRIDIS_PALETTE)

    style_params = {
        'figure.figsize': figsize,
        'figure.dpi': dpi,
        'figure.facecolor': 'white',
        'figure.edgecolor': 'white',
        'axes.facecolor': 'white',
        'axes.edgecolor': '#616161',
        'axes.linewidth': 1.0,
        'axes.grid': False,  # we enable grid per-axes with subtle style in enhance_axes
        'axes.axisbelow': True,
        'axes.labelcolor': '#212529',
        'xtick.color': '#424242',
        'ytick.color': '#424242',
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 4.0,
        'ytick.major.size': 4.0,
        'xtick.minor.size': 2.0,
        'ytick.minor.size': 2.0,
        'legend.frameon': True,
        'legend.framealpha': 0.95,
        'legend.facecolor': 'white',
        'legend.edgecolor': '#e0e0e0',
        'legend.fancybox': False,
        'legend.shadow': False,
        'lines.linewidth': 2.0,
        'lines.markersize': 6.0,
        'patch.edgecolor': 'white',
        'patch.linewidth': 0.5,
        'savefig.dpi': PUBLICATION_DPI,  # high-res when saving to file
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
        'savefig.facecolor': 'white',
        'savefig.edgecolor': 'white',
    }
    for key, value in style_params.items():
        try:
            plt.rcParams[key] = value
        except KeyError:
            pass
    return style_params


def create_professional_figure(
    nrows: int = 1,
    ncols: int = 1,
    figsize: Optional[Tuple[float, float]] = None,
    dpi: int = None,
    constrained_layout: bool = True
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create a figure with publication-ready styling. Call finalize_figure(fig) before save.
    Uses DISPLAY_DPI by default so on-screen figures fit the monitor; pass dpi=PUBLICATION_DPI
    only when creating figures solely for high-res export. When saving to file, use
    fig.savefig(..., dpi=PUBLICATION_DPI) to get 300 DPI output.
    """
    if dpi is None:
        dpi = DISPLAY_DPI
    apply_scientific_style(figsize=figsize or (10, 6), dpi=dpi)
    if figsize is None:
        width = 6 * ncols
        height = 4.5 * nrows
        figsize = (width, height)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=figsize,
        dpi=dpi,
        constrained_layout=constrained_layout
    )
    if nrows == 1 and ncols == 1:
        axes = np.array([axes])
    elif nrows == 1 or ncols == 1:
        axes = axes.flatten()
    return fig, axes


def finalize_figure(fig: plt.Figure, pad: float = 1.08) -> None:
    """
    Call before save: tight_layout for clean margins, no overlapping elements.
    """
    try:
        fig.tight_layout(pad=pad)
    except Exception:
        pass


# ============================================================================
# COLOR UTILITIES
# ============================================================================

def get_color(index: int, palette: Optional[list] = None) -> str:
    if palette is None:
        palette = SCIENTIFIC_PALETTE
    return palette[index % len(palette)]


def create_colormap(name: str = 'viridis', n_colors: int = 256):
    cmap = _get_cmap('magma' if name == 'magma' else 'viridis')
    try:
        return cmap.resampled(n_colors)
    except AttributeError:
        return mpl.cm.get_cmap(cmap.name, lut=n_colors)


# ============================================================================
# ANNOTATION HELPERS
# ============================================================================

def add_value_labels(ax: plt.Axes, bars, fmt: str = '{:.2f}', offset: float = 0.02):
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    offset_pixels = y_range * offset
    if hasattr(bars, '__iter__') and not isinstance(bars, str):
        for bar in bars:
            height = bar.get_height()
            if not np.isnan(height) and not np.isinf(height):
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height + offset_pixels,
                    fmt.format(height),
                    ha='center', va='bottom',
                    fontsize=plt.rcParams['font.size'] - 1,
                    fontweight='bold',
                    color=SCIENTIFIC_COLORS['dark']
                )


def add_annotation(ax: plt.Axes, text: str, xy: Tuple[float, float],
                   xytext: Optional[Tuple[float, float]] = None,
                   arrowprops: Optional[Dict] = None, **kwargs):
    default_arrowprops = {
        'arrowstyle': '->', 'color': SCIENTIFIC_COLORS['primary'], 'lw': 1.5, 'alpha': 0.7
    }
    if arrowprops:
        default_arrowprops.update(arrowprops)
    default_kwargs = {
        'fontsize': plt.rcParams['font.size'],
        'color': SCIENTIFIC_COLORS['dark'],
        'bbox': dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=SCIENTIFIC_COLORS['primary'], alpha=0.9, linewidth=1.0)
    }
    default_kwargs.update(kwargs)
    ax.annotate(text, xy=xy, xytext=xytext or xy,
                arrowprops=default_arrowprops if xytext else None, **default_kwargs)


# ============================================================================
# AXES ENHANCEMENT (minimalist: no chart junk, precise ticks)
# ============================================================================

def enhance_axes(ax: plt.Axes, title: Optional[str] = None, xlabel: Optional[str] = None,
                 ylabel: Optional[str] = None, grid: bool = True):
    """
    Publication axes: no top/right spines, subtle gray grid, clear labels.
    Labels support LaTeX via mathtext (e.g. r'$\\lambda$', r'$f_c$ (Hz)').
    """
    if title:
        ax.set_title(title, fontsize=plt.rcParams['axes.titlesize'], fontweight='bold',
                     color=SCIENTIFIC_COLORS['dark'], pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=plt.rcParams['axes.labelsize'],
                      color=SCIENTIFIC_COLORS['dark'], fontweight='normal')
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=plt.rcParams['axes.labelsize'],
                      color=SCIENTIFIC_COLORS['dark'], fontweight='normal')

    # Subtle gray grid
    if grid:
        ax.grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE, linewidth=GRID_LINEWIDTH, color=GRID_COLOR)
        ax.set_axisbelow(True)

    # Remove top and right spines (minimalist)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.spines['bottom'].set_color(GRID_COLOR)


def format_axes_ticks(ax: plt.Axes, x_format: Optional[str] = None, y_format: Optional[str] = None):
    if x_format:
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: x_format.format(x)))
    if y_format:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, p: y_format.format(y)))


# ============================================================================
# INITIALIZATION
# ============================================================================

try:
    apply_scientific_style()
except Exception as e:
    import warnings
    warnings.warn(f"Could not apply all style parameters: {e}")
