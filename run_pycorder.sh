#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Prefer an actual UTF-8 locale for Qt (not just a UTF-8-looking env var).
needs_utf8_locale=0
if command -v locale >/dev/null 2>&1; then
  current_charmap="$(locale charmap 2>/dev/null || true)"
  case "$current_charmap" in
    *UTF-8*|*utf8*) needs_utf8_locale=0 ;;
    *) needs_utf8_locale=1 ;;
  esac
else
  needs_utf8_locale=1
fi

if [[ "$needs_utf8_locale" -eq 1 ]]; then
  UTF8_LOCALE=""
  if command -v locale >/dev/null 2>&1; then
    if locale -a 2>/dev/null | grep -qi '^en_US\.UTF-8$'; then
      UTF8_LOCALE="en_US.UTF-8"
    elif locale -a 2>/dev/null | grep -qi '^C\.UTF-8$'; then
      UTF8_LOCALE="C.UTF-8"
    fi
  fi
  UTF8_LOCALE="${UTF8_LOCALE:-en_US.UTF-8}"
  export LANG="$UTF8_LOCALE"
  export LC_ALL="$UTF8_LOCALE"
  export LC_CTYPE="$UTF8_LOCALE"
fi

# Reduce verbose Qt warnings that are not actionable for end users.
export QT_LOGGING_RULES="${QT_LOGGING_RULES:-qt.qpa.fonts=false}"

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
