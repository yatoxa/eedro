VENV_HOME = ./venv
PYTHON_VENV = $(VENV_HOME)/bin/python

ifeq ($(wildcard $(PYTHON_VENV)),)
  $(info --- venv not found, to initialize it, run make venv or make venv-dev ---)
endif

PYTHON ?= python3.10

.PHONY: venv-init venv-update venv-update-dev venv venv-dev pretty lint pretty-lint docker-clean docker-build docker-up docker-rebuild docker-logs tests

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

docker-clean:
	docker compose down --rmi local

docker-build:
	docker compose build --no-cache

docker-up:
	docker compose up -d

docker-rebuild: docker-clean docker-build docker-up

docker-logs:
	docker compose logs $(filter-out $@,$(MAKECMDGOALS)) || true

tests:
	docker compose up tests

%:
	@:
