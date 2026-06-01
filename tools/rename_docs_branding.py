"""One-off: rename legacy product labels to Textural Density in documentation."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = [
    ("Simultaneity Density Analyser (SDA)", "Textural Density"),
    ("Simultaneity Density Analyser", "Textural Density"),
    ("Densidade Vertical", "Textural Density"),
    ("densidade vertical", "Textural Density"),
    ("SDA Benchmark", "Textural Density Benchmark"),
    ("SDA Project", "Textural Density Project"),
]

SKIP_PARTS = {"node_modules", ".git", "__pycache__", "expected_outputs", "htmlcov", "tools"}


def iter_doc_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix in {".md", ".json", ".musicxml"}:
            files.append(path)
        elif path.name in {"requirements.txt", "pyproject.toml", "validation/report.py"}:
            files.append(path)
    return files


def transform(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    text = re.sub(r"\bSDA\b", "Textural Density", text)
    text = text.replace("Textural Density / Textural Density", "Textural Density")
    text = text.replace(
        "Textural Density (Textural Density / Textural Density)",
        "Textural Density",
    )
    return text


def main() -> int:
    changed: list[str] = []
    for path in sorted(iter_doc_files()):
        original = path.read_text(encoding="utf-8")
        updated = transform(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} files")
    for name in changed:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
