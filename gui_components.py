"""
Backward-compatible re-exports after GUI split into gui/app.py and gui/widgets/.

Prefer importing from gui.app for new code.
"""

from gui.app import DensityCalculatorGUI
from gui.calibration_window import abrir_janela_calibracao, adicionar_opcao_calibracao

__all__ = [
    "DensityCalculatorGUI",
    "abrir_janela_calibracao",
    "adicionar_opcao_calibracao",
]
