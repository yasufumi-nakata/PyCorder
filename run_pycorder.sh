#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[error] Python interpreter not found (python3/python)." >&2
  exit 1
fi

if [[ ! -x ".venv/bin/python" ]] || ! .venv/bin/python -V >/dev/null 2>&1; then
  echo "[setup] Creating virtual environment at .venv"
  "$PYTHON_BIN" -m venv --clear .venv
fi

if ! .venv/bin/python - <<'PY' >/dev/null 2>&1
import importlib
for name in ("numpy", "scipy", "lxml", "PySide6", "pyqtgraph"):
    importlib.import_module(name)
PY
then
  echo "[setup] Installing dependencies from requirements.txt"
  .venv/bin/pip install --upgrade pip setuptools wheel
  .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/python main.py "$@"
