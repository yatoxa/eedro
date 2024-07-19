#!/usr/bin/env bash
set -e

APP_DIR="/app"
VENV_HOME="${APP_DIR}/venv"
PYTHON_VENV="${VENV_HOME}/bin/python"

PYTHONPATH="${APP_DIR}/src":$PYTHONPATH ${PYTHON_VENV} -m pytest "${APP_DIR}/src/tests" "$@"
