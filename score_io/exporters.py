"""
JSON export for analysis results.

Core module: no Tkinter. GUI file dialogs live in ``gui.file_io``.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from error_handler import FileOperationError
from utils.serialize_utils import serialize_for_json

logger = logging.getLogger("score_io.exporters")


def write_results_json(resultados: dict[str, Any], path: str) -> str:
    """
    Write analysis results to a JSON file.

    Args:
        resultados: Results dictionary from ``calculate_metrics``.
        path: Destination file path.

    Returns:
        The path written.

    Raises:
        FileOperationError: If the file cannot be written.
    """
    try:
        converted = serialize_for_json(resultados)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(converted, handle, ensure_ascii=False, indent=4)
        logger.info("Results saved to: %s", path)
        return path
    except OSError as exc:
        raise FileOperationError(
            str(exc),
            filename=path,
            operation="write",
        ) from exc


def save_results(
    resultados: dict[str, Any],
    nome_arquivo: Optional[str] = None,
    *,
    prompt_if_missing: bool = False,
) -> Optional[str]:
    """
    Save results to JSON.

    Args:
        resultados: Results dictionary.
        nome_arquivo: Target path. If ``None`` and ``prompt_if_missing`` is
            False, returns ``None`` without writing.
        prompt_if_missing: When ``nome_arquivo`` is ``None``, open a GUI save
            dialog (requires ``gui.file_io``).

    Returns:
        Path written, or ``None`` if cancelled or on write failure (legacy
        behaviour for callers expecting ``None`` instead of exceptions).
    """
    if nome_arquivo is None:
        if not prompt_if_missing:
            return None
        from gui.file_io import prompt_save_results_path

        nome_arquivo = prompt_save_results_path()
        if not nome_arquivo:
            return None

    try:
        return write_results_json(resultados, nome_arquivo)
    except FileOperationError as exc:
        logger.error("Error saving results: %s", exc)
        if prompt_if_missing:
            from gui.file_io import show_save_error

            show_save_error(str(exc))
        return None
