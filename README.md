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

Current additions:

DC Offset pane shows the DC voltage on each electrode
