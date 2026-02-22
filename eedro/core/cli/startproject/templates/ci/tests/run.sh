#!/usr/bin/env bash
set -e

APP_DIR="/app"
VENV_HOME="${APP_DIR}/venv"
COVERAGE_VENV="${VENV_HOME}/bin/coverage"

PYTHONPATH="${APP_DIR}/src":$PYTHONPATH ${COVERAGE_VENV} run --omit="${APP_DIR}/src/tests/*" -m pytest "${APP_DIR}/src/tests" "$@"
PYTHONPATH="${APP_DIR}/src":$PYTHONPATH ${COVERAGE_VENV} report --omit="${APP_DIR}/src/tests/*" -m "$@"
