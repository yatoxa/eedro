#!/usr/bin/env bash
set -e

APP_DIR="/app"
SRC_DIR="${APP_DIR}/src"
VENV_HOME="${APP_DIR}/venv"
PYTHON_VENV="${VENV_HOME}/bin/python"

PYTHONPATH=${SRC_DIR}:$PYTHONPATH ${PYTHON_VENV} -m $%{root_namespace}.core.server.pong "$@"
