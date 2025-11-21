#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-${ROOT_DIR}/.venv}"
PYTHON_BIN="${PYTHON:-python3}"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[dev_env] Creating virtual environment at ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip >/dev/null
python -m pip install -r "${ROOT_DIR}/requirements.txt"

export PYTHONPATH="${ROOT_DIR}:${PYTHONPATH:-}"

# Provide a sane default for Qt plugin discovery when running inside the venv
PYSIDE_PLUGIN_ROOT="$(python -c 'import PySide6, os; print(os.path.join(os.path.dirname(PySide6.__file__), \"Qt\", \"plugins\"))' 2>/dev/null || true)"
if [[ -n "${PYSIDE_PLUGIN_ROOT}" ]]; then
  export QT_QPA_PLATFORM_PLUGIN_PATH="${QT_QPA_PLATFORM_PLUGIN_PATH:-${PYSIDE_PLUGIN_ROOT}}"
fi

exec "${PYTHON_BIN}" "${ROOT_DIR}/main.py" "$@"

