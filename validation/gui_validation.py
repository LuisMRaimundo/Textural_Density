"""
GUI-facing validation report formatting (historical metrics correlation text).

Not part of the analytical pipeline; used by Main after statistical_validation.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def generate_validation_text(resultados_validacao, num_historico: int) -> str:
    """Format descriptive stats and correlation summary for the GUI validation tab."""
    try:
        texto = "=== DESCRIPTIVE STATISTICS ===\n"
        desc_stats = resultados_validacao["descriptive_stats"]
        texto += f"Number of samples: {num_historico}\n\n"
        for col in desc_stats.columns:
            texto += f"{col}:\n"
            texto += f"  Mean: {desc_stats[col]['mean']:.4f}\n"
            texto += f"  Std Dev: {desc_stats[col]['std']:.4f}\n"
            texto += f"  Min: {desc_stats[col]['min']:.4f}\n"
            texto += f"  Max: {desc_stats[col]['max']:.4f}\n"
            texto += (
                f"  Coef. of Variation: "
                f"{resultados_validacao['coefficient_of_variation'][col]:.4f}\n\n"
            )
        texto += "=== SIGNIFICANT CORRELATIONS ===\n"
        if resultados_validacao["high_correlations"]:
            for (m1, m2), corr in resultados_validacao["high_correlations"].items():
                texto += f"{m1} – {m2}: {corr:.4f}\n"
        else:
            texto += "No significant correlations found.\n"
        if "pca" in resultados_validacao:
            texto += "\n=== PRINCIPAL COMPONENT ANALYSIS ===\n"
            texto += (
                f"Number of components for 95% variance: "
                f"{resultados_validacao['pca']['n_components_95']}\n"
            )
        return texto
    except Exception as e:
        logger.error("Error generating validation text: %s", e)
        return f"Error generating validation text: {e}"
