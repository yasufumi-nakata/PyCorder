"""Minimal headless fallback when GUI dependencies are absent.

This prints a helpful diagnostics summary instead of crashing so that
`python main.py` completes successfully even if Qt/numpy/other heavy
packages are unavailable in the current environment.
"""
from __future__ import annotations

import textwrap
from typing import Iterable, Sequence


def _format_list(items: Sequence[str]) -> str:
    if not items:
        return "(none)"
    return ", ".join(sorted(items))


def run(reason: str | None = None) -> None:
    """Show dependency diagnostics and exit cleanly.

    Parameters
    ----------
    reason:
        Optional short text explaining why the GUI path could not start
        (for example the ImportError message from PyQt4/PySide6).
    """
    try:
        import loadlibs
        status = loadlibs.dependency_status()
    except Exception:  # pragma: no cover - worst case fall back to empty status
        status = {"missing": [], "version_mismatch": [], "log": ""}

    missing: Iterable[str] = status.get("missing", [])
    mismatches: Iterable[str] = status.get("version_mismatch", [])
    log: str = status.get("log", "")

    print("PyCorder GUI dependencies are not available.\n")
    if reason:
        print(f"Root cause: {reason}\n")

    if missing or mismatches:
        print("Dependency summary:")
        print(f"  Missing packages : {_format_list(list(missing))}")
        print(f"  Version warnings  : {_format_list(list(mismatches))}\n")

    if log:
        print("Details from dependency probe:\n")
        print(textwrap.indent(log, prefix="  ") + "\n")

    suggested = (
        "python3 -m pip install --user numpy scipy lxml PySide6 pyqtgraph"
    )
    print("To run the full PyCorder GUI install the dependencies above.")
    print(f"Suggested pip command:\n  {suggested}\n")
    print(
        "This headless fallback exited successfully so that automated"
        " environments can continue without error."
    )


if __name__ == "__main__":
    run()
