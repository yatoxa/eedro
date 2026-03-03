#!/usr/bin/env bash
set -e

APP_DIR="/app"
SRC_DIR="${APP_DIR}/src"
TESTS_DIR="${SRC_DIR}/tests"
VENV_HOME="${APP_DIR}/venv"
COVERAGE_VENV="${VENV_HOME}/bin/coverage"

PYTHONPATH=${SRC_DIR}:$PYTHONPATH ${COVERAGE_VENV} run --rcfile="${SRC_DIR}/pyproject.toml" -m pytest ${TESTS_DIR} "$@"
PYTHONPATH=${SRC_DIR}:$PYTHONPATH ${COVERAGE_VENV} report --rcfile="${SRC_DIR}/pyproject.toml" "$@"
