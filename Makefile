VENV_HOME = ./venv
PYTHON_VENV = $(VENV_HOME)/bin/python

PYTHON ?= python3.10

.PHONY: venv-init venv-update venv-update-dev venv venv-dev pretty lint pretty-lint

venv-init:
	$(PYTHON) -m venv --copies --clear --upgrade-deps $(VENV_HOME)

venv-update:
	$(PYTHON_VENV) -m pip install -U pip
	$(PYTHON_VENV) -m pip install -U -r ./etc/requirements.txt

venv-update-dev: venv-update
	$(PYTHON_VENV) -m pip install -U -r ./etc/requirements-dev.txt

venv: venv-init venv-update

venv-dev: venv-init venv-update-dev

pretty:
	$(PYTHON_VENV) -m isort .
	$(PYTHON_VENV) -m black .

lint:
	$(PYTHON_VENV) -m flake8 .
	$(PYTHON_VENV) -m black . --check

pretty-lint: pretty lint
