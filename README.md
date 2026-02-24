# PyCorder
Modified PyCorder Code for EIT Experiments

Compatibility updates (2025):
- Python 3.x compatible (print, queue, configparser, perf_counter)
- macOS (Apple Silicon/Intel) and Windows 11: runs in GUI with fallback simulation when ActiChamp DLL is absent
- File I/O uses Python standard API (no libc dependency)
- Legacy PyQt4/PyQwt imports are shimmed to PySide6/pyqtgraph (`PyQt4/` directory)

Requirements:
- Python 3.9+
- numpy, scipy, lxml
- PySide6, pyqtgraph

Quick start:
- Windows with hardware: install vendor DLLs in the working directory (`ActiChamp_x64.dll`/`ActiChamp_x86.dll`)
- macOS/No hardware: app starts in simulation mode automatically
- First run on macOS/Linux (or when `.venv` is broken): `bash ./run_pycorder.sh`
- First run on Windows PowerShell: `.\run_pycorder.ps1`
- First run on Windows CMD: `run_pycorder.bat`
- Manual run after setup:
  - macOS/Linux:
    - `source .venv/bin/activate`
    - `python main.py`
  - Windows:
    - `.venv\Scripts\activate`
    - `python main.py`
- Automated smoke test (headless, no window popup):
  - `bash ./run_pycorder.sh --smoketest`
- Automated GUI measurement check with dummy data (headless/offscreen, validates 1000 Hz by default):
  - `QT_QPA_PLATFORM=offscreen .venv/bin/python tools/gui_dummy_measurement_check.py`
- Automated end-to-end check (measurement + file creation in one run):
  - `QT_QPA_PLATFORM=offscreen .venv/bin/python tools/gui_dummy_recording_check.py --sample-rate-hz 1000 --duration-ms 2600`

GUI startup (recommended):
- macOS/Linux:
  1. `bash ./run_pycorder.sh`
  2. Wait until the PyCorder main window opens.
- Windows PowerShell:
  1. `.\run_pycorder.ps1`
  2. Wait until the PyCorder main window opens.
- Windows CMD:
  1. `run_pycorder.bat`
  2. Wait until the PyCorder main window opens.

Dummy data measurement (no hardware):
1. Start GUI with one of the commands above.
2. In the amplifier online pane, click `Default` (start acquisition).
3. Confirm waveform updates in the display pane.
4. Click again to stop acquisition.

Validate 1000 Hz dummy acquisition (automated):
1. Run:
   - `QT_QPA_PLATFORM=offscreen .venv/bin/python tools/gui_dummy_measurement_check.py --sample-rate-hz 1000 --duration-ms 2600`
2. Confirm the output contains:
   - `gui_measurement_ok=True`
   - `configured_rate=1000.0`
   - `reported_rate=1000.0`

You can test other rates similarly, for example:
- `QT_QPA_PLATFORM=offscreen .venv/bin/python tools/gui_dummy_measurement_check.py --sample-rate-hz 2000 --duration-ms 2600`

Validate one-shot measurement + recording file creation:
1. Run:
   - `QT_QPA_PLATFORM=offscreen .venv/bin/python tools/gui_dummy_recording_check.py --sample-rate-hz 1000 --duration-ms 2600`
2. Confirm the output contains:
   - `gui_recording_ok=True`
   - `configured_rate=1000.0`
   - `reported_rate=1000.0`
3. Output files are created under:
   - `outputs/dummy_recordings/` (`.eeg`, `.vhdr`, `.vmrk`)

If GUI does not start:
1. Run `bash ./run_pycorder.sh --smoketest` to verify dependency/runtime startup.
2. If another instance is still running, stop it:
   - `pkill -f "python.*main.py"`
3. Run `QT_QPA_PLATFORM=offscreen .venv/bin/python tools/gui_dummy_measurement_check.py --sample-rate-hz 1000` to verify dummy acquisition path.

Notes:
- On macOS, PyCorder uses a stable simple scope (`DISP_ScopeSimple`) by default to avoid Qt/Qwt shim startup crashes while still showing live dummy/hardware waveforms.
- If the selected scope widget cannot be initialized on your Qt runtime, PyCorder falls back to a minimal pane (`DISP_ScopeLite`) so acquisition can still run.
- If TCP port `51244` is already in use, the RDA server module is skipped and the GUI still starts.

Current additions:

DC Offset pane shows the DC voltage on each electrode
