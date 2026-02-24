#!/usr/bin/env python3
"""Headless GUI measurement check using the ActiChamp dummy backend."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_utf8_locale() -> None:
    """Make sure Qt starts with a true UTF-8 locale."""
    try:
        charmap = subprocess.check_output(
            ["locale", "charmap"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        charmap = ""
    if "UTF-8" in charmap.upper() or "UTF8" in charmap.upper():
        return

    candidates: list[str] = []
    try:
        out = subprocess.check_output(["locale", "-a"], text=True, stderr=subprocess.DEVNULL)
        candidates = [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        candidates = []

    selected = "en_US.UTF-8"
    lower = {name.lower(): name for name in candidates}
    if "en_us.utf-8" in lower:
        selected = lower["en_us.utf-8"]
    elif "c.utf-8" in lower:
        selected = lower["c.utf-8"]

    os.environ["LANG"] = selected
    os.environ["LC_ALL"] = selected
    os.environ["LC_CTYPE"] = selected


def _pick_sample_rate(sample_rates, target_hz: float):
    if not sample_rates:
        raise RuntimeError("No sample rates available on amplifier object")
    return min(sample_rates, key=lambda x: abs(float(x["value"]) - float(target_hz)))


def run(duration_ms: int, sample_rate_hz: float, min_effective_ratio: float) -> int:
    _ensure_utf8_locale()
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.fonts=false")

    repo_root = _repo_root()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from PyQt4 import Qt, QtCore
    from actichamp_w import CHAMP_MODE_NORMAL

    # main.MainWindow parses sys.argv using optparse; strip our script flags.
    argv_backup = list(sys.argv)
    sys.argv = [argv_backup[0]]
    import main

    app = Qt.QApplication([])
    try:
        win = main.MainWindow()
        win.usageConfirmed = True
        amp = win.topmodule

        selected_rate = _pick_sample_rate(amp.sample_rates, sample_rate_hz)
        amp.sample_rate = selected_rate
        amp.update_receivers()
        configured_rate = float(selected_rate["value"])

        state = {
            "ok": False,
            "samples": 0,
            "running": False,
            "display_module": type(win.modules[-1]).__name__,
            "configured_rate": configured_rate,
            "reported_rate": 0.0,
            "effective_rate": 0.0,
            "min_effective_rate": configured_rate * max(0.01, float(min_effective_ratio)),
            "elapsed_s": 0.0,
        }
        started_at = {"t": 0.0}

        def start_measurement():
            amp._online_mode_changed(CHAMP_MODE_NORMAL)
            started_at["t"] = time.perf_counter()
            QtCore.QTimer.singleShot(duration_ms, check_measurement)

        def check_measurement():
            state["samples"] = int(amp.eeg_data.sample_counter)
            state["running"] = bool(amp.isRunning())
            state["reported_rate"] = float(getattr(amp.eeg_data, "sample_rate", 0.0) or 0.0)
            state["elapsed_s"] = max(1e-6, time.perf_counter() - started_at["t"])
            state["effective_rate"] = float(state["samples"]) / state["elapsed_s"]
            state["ok"] = (
                state["running"]
                and state["samples"] > 0
                and abs(state["reported_rate"] - state["configured_rate"]) < 1e-6
                and state["effective_rate"] >= state["min_effective_rate"]
            )
            amp.stop(force=True)
            win.close()
            app.exit(0 if state["ok"] else 2)

        QtCore.QTimer.singleShot(0, start_measurement)
        rc = app.exec_()
        print(
            "gui_measurement_ok=%s running=%s samples=%d configured_rate=%.1f "
            "reported_rate=%.1f effective_rate=%.1f min_effective_rate=%.1f "
            "elapsed_s=%.3f display=%s rc=%d"
            % (
                state["ok"],
                state["running"],
                state["samples"],
                state["configured_rate"],
                state["reported_rate"],
                state["effective_rate"],
                state["min_effective_rate"],
                state["elapsed_s"],
                state["display_module"],
                rc,
            )
        )
        return rc
    finally:
        sys.argv = argv_backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--duration-ms",
        type=int,
        default=2500,
        help="time to keep acquisition running before validation",
    )
    parser.add_argument(
        "--sample-rate-hz",
        type=float,
        default=1000.0,
        help="target sampling rate to validate with dummy acquisition",
    )
    parser.add_argument(
        "--min-effective-ratio",
        type=float,
        default=0.60,
        help="minimum accepted effective_rate/configured_rate ratio",
    )
    args = parser.parse_args()
    return run(
        duration_ms=max(200, args.duration_ms),
        sample_rate_hz=max(1.0, args.sample_rate_hz),
        min_effective_ratio=max(0.01, args.min_effective_ratio),
    )


if __name__ == "__main__":
    sys.exit(main())
