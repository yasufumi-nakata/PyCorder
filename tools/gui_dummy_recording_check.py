#!/usr/bin/env python3
"""End-to-end GUI dummy run: start measurement, record, and verify output files."""

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
    try:
        charmap = subprocess.check_output(
            ["locale", "charmap"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        charmap = ""
    if "UTF-8" in charmap.upper() or "UTF8" in charmap.upper():
        return

    selected = "en_US.UTF-8"
    try:
        out = subprocess.check_output(["locale", "-a"], text=True, stderr=subprocess.DEVNULL)
        lower = {line.strip().lower(): line.strip() for line in out.splitlines() if line.strip()}
        if "en_us.utf-8" in lower:
            selected = lower["en_us.utf-8"]
        elif "c.utf-8" in lower:
            selected = lower["c.utf-8"]
    except Exception:
        pass

    os.environ["LANG"] = selected
    os.environ["LC_ALL"] = selected
    os.environ["LC_CTYPE"] = selected


def _pick_sample_rate(sample_rates, target_hz: float):
    if not sample_rates:
        raise RuntimeError("No sample rates available on amplifier object")
    return min(sample_rates, key=lambda x: abs(float(x["value"]) - float(target_hz)))


def run(duration_ms: int, sample_rate_hz: float, output_dir: Path, base_name: str) -> int:
    _ensure_utf8_locale()
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.fonts=false")

    repo_root = _repo_root()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from PyQt4 import Qt, QtCore
    from actichamp_w import CHAMP_MODE_NORMAL
    from modbase import EventType, ModuleEvent

    argv_backup = list(sys.argv)
    sys.argv = [argv_backup[0]]
    import main

    output_dir.mkdir(parents=True, exist_ok=True)
    app = Qt.QApplication([])
    try:
        win = main.MainWindow()
        win.usageConfirmed = True
        amp = win.topmodule
        storage = next(
            m for m in main.flatten(win.modules) if m.__class__.__name__ == "StorageVision"
        )

        selected_rate = _pick_sample_rate(amp.sample_rates, sample_rate_hz)
        amp.sample_rate = selected_rate
        amp.update_receivers()
        storage.default_path = str(output_dir)

        state = {
            "ok": False,
            "configured_rate": float(selected_rate["value"]),
            "reported_rate": 0.0,
            "samples": 0,
            "elapsed_s": 0.0,
            "eeg_file": "",
            "vhdr_file": "",
            "vmrk_file": "",
            "eeg_bytes": 0,
            "vhdr_bytes": 0,
            "vmrk_bytes": 0,
            "error": "",
        }
        started = {"t": 0.0}

        def start_measurement():
            try:
                amp._online_mode_changed(CHAMP_MODE_NORMAL)
                started["t"] = time.perf_counter()
                QtCore.QTimer.singleShot(200, start_saving)
            except Exception as exc:
                state["error"] = f"start_measurement: {exc}"
                finalize(exit_code=2)

        def start_saving():
            try:
                storage.process_event(
                    ModuleEvent(
                        module="E2E",
                        type=EventType.COMMAND,
                        info="StartSaving",
                        cmd_value=base_name,
                    )
                )
                if not storage.file_name or storage.data_file is None:
                    state["error"] = "StartSaving did not open recording file"
                    finalize(exit_code=2)
                    return
                QtCore.QTimer.singleShot(duration_ms, stop_all)
            except Exception as exc:
                state["error"] = f"start_saving: {exc}"
                finalize(exit_code=2)

        def stop_all():
            try:
                storage.process_event(
                    ModuleEvent(module="E2E", type=EventType.COMMAND, info="StopSaving")
                )
                if amp.isRunning():
                    amp.stop(force=True)
            except Exception as exc:
                state["error"] = f"stop_all: {exc}"
                finalize(exit_code=2)
                return
            QtCore.QTimer.singleShot(100, lambda: finalize(exit_code=0))

        def finalize(exit_code: int):
            try:
                state["samples"] = int(getattr(amp.eeg_data, "sample_counter", 0))
                state["reported_rate"] = float(getattr(amp.eeg_data, "sample_rate", 0.0) or 0.0)
                if started["t"] > 0:
                    state["elapsed_s"] = max(1e-6, time.perf_counter() - started["t"])
                eeg_file = storage.file_name or ""
                if eeg_file:
                    eeg_path = Path(eeg_file)
                    vhdr_path = eeg_path.with_suffix(".vhdr")
                    vmrk_path = eeg_path.with_suffix(".vmrk")
                    state["eeg_file"] = str(eeg_path)
                    state["vhdr_file"] = str(vhdr_path)
                    state["vmrk_file"] = str(vmrk_path)
                    if eeg_path.exists():
                        state["eeg_bytes"] = eeg_path.stat().st_size
                    if vhdr_path.exists():
                        state["vhdr_bytes"] = vhdr_path.stat().st_size
                    if vmrk_path.exists():
                        state["vmrk_bytes"] = vmrk_path.stat().st_size

                same_rate = abs(state["configured_rate"] - state["reported_rate"]) < 1e-6
                files_ok = (
                    state["eeg_bytes"] > 0 and state["vhdr_bytes"] > 0 and state["vmrk_bytes"] > 0
                )
                measured = state["samples"] > 0
                state["ok"] = exit_code == 0 and same_rate and files_ok and measured and not state["error"]
            finally:
                try:
                    win.close()
                finally:
                    app.exit(exit_code)

        QtCore.QTimer.singleShot(0, start_measurement)
        rc = app.exec_()
        print(
            "gui_recording_ok=%s rc=%d configured_rate=%.1f reported_rate=%.1f "
            "samples=%d elapsed_s=%.3f eeg_bytes=%d vhdr_bytes=%d vmrk_bytes=%d "
            "eeg_file=%s error=%s"
            % (
                state["ok"],
                rc,
                state["configured_rate"],
                state["reported_rate"],
                state["samples"],
                state["elapsed_s"],
                state["eeg_bytes"],
                state["vhdr_bytes"],
                state["vmrk_bytes"],
                state["eeg_file"] or "-",
                state["error"] or "-",
            )
        )
        return 0 if state["ok"] else 2
    finally:
        sys.argv = argv_backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-ms", type=int, default=2500)
    parser.add_argument("--sample-rate-hz", type=float, default=1000.0)
    parser.add_argument("--output-dir", type=str, default="outputs/dummy_recordings")
    parser.add_argument("--base-name", type=str, default="dummy_e2e")
    args = parser.parse_args()

    return run(
        duration_ms=max(200, int(args.duration_ms)),
        sample_rate_hz=max(1.0, float(args.sample_rate_hz)),
        output_dir=Path(args.output_dir),
        base_name=str(args.base_name).strip() or "dummy_e2e",
    )


if __name__ == "__main__":
    sys.exit(main())

