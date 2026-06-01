#!/usr/bin/env python
"""
Build a standalone Windows executable for Textural Density.
Uses PyInstaller with the same options as documented in README.
Run from project root: python build_exe.py
Output: dist/densidade-vertical.exe
"""
import subprocess
import sys


def main():
    try:
        import PyInstaller.__main__ as pyi
    except ImportError:
        print("PyInstaller is not installed. Install it with: pip install pyinstaller")
        sys.exit(1)

    # Same options as README: one-file, windowed (no console)
    run_py = "run.py"
    args = [
        run_py,
        "--name=densidade-vertical",
        "--windowed",
        "--onefile",
    ]
    print("Running: pyinstaller " + " ".join(args))
    pyi.run(args)


if __name__ == "__main__":
    main()
