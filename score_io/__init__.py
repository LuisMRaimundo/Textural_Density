"""Score/symbolic I/O utilities (GUI-independent). Avoids shadowing stdlib ``io``."""

from score_io.exporters import save_results, write_results_json

__all__ = ["write_results_json", "save_results"]
