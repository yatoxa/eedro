VENV_HOME = ./.venv
PYTHON_VENV = $(VENV_HOME)/bin/python

ifeq ($(wildcard $(PYTHON_VENV)),)
  $(info --- venv not found, to initialize it, run make venv or make venv-dev ---)
endif

PYTHON ?= python3.12

default: help

.PHONY: help ## Display this help message
help:
	@awk '/^\.PHONY: [a-zA-Z0-9_.-]+ ## / { target=$$2; desc=substr($$0, index($$0, "## ") + 3); printf "\033[1;32m%s\033[0m: %s\n", target, desc }' $(MAKEFILE_LIST) | sort

.PHONY: venv-init ## Create a fresh virtual environment
venv-init:
	$(PYTHON) -m venv --copies --clear --upgrade-deps $(VENV_HOME)

.PHONY: venv-update ## Install or update runtime dependencies in venv
venv-update:
	$(PYTHON_VENV) -m pip install -U pip
	$(PYTHON_VENV) -m pip install -U -e ./

.PHONY: venv-update-dev ## Install or update runtime and dev dependencies in venv
venv-update-dev: venv-update
	$(PYTHON_VENV) -m pip install -U -e ./[dev]

.PHONY: venv ## Recreate venv and install runtime dependencies
venv: venv-init venv-update

.PHONY: venv-dev ## Recreate venv and install runtime and dev dependencies
venv-dev: venv-init venv-update-dev

.PHONY: pretty ## Run code formatters (isort + black)
pretty:
	$(PYTHON_VENV) -m isort .
	$(PYTHON_VENV) -m black .

.PHONY: lint ## Run static checks (flake8 + black --check)
lint:
	$(PYTHON_VENV) -m flake8 .
	$(PYTHON_VENV) -m black . --check

.PHONY: pretty-lint ## Format code and then run lint checks
pretty-lint: pretty lint

.PHONY: package ## Build source and wheel distributions
package:
	rm -rf build dist wheels *.egg-info
	$(PYTHON_VENV) -m pip wheel --no-deps . -w wheels/

.PHONY: docker-clean ## Stop containers and remove local images
docker-clean:
	docker compose down --rmi local

.PHONY: docker-build ## Build docker images without cache
docker-build:
	docker compose build --no-cache

.PHONY: docker-up ## Start services in detached mode
docker-up:
	docker compose up -d

.PHONY: docker-rebuild ## Rebuild docker environment from scratch
docker-rebuild: docker-clean docker-build docker-up

.PHONY: docker-logs ## Show docker compose logs for selected services
docker-logs:
	docker compose logs $(filter-out $@,$(MAKECMDGOALS)) || true

.PHONY: tests-py310 ## Run test container for Python 3.10
tests-py310:
	docker compose up tests-py310

.PHONY: tests-py311 ## Run test container for Python 3.11
tests-py311:
	docker compose up tests-py311

.PHONY: tests-py312 ## Run test container for Python 3.12
tests-py312:
	docker compose up tests-py312

.PHONY: tests-py313 ## Run test container for Python 3.13
tests-py313:
	docker compose up tests-py313

.PHONY: tests-py314 ## Run test container for Python 3.14
tests-py314:
	docker compose up tests-py314

.PHONY: tests-sorted ## Run tests in containers sequentially from 3.10 to 3.14
tests-sorted: tests-py310 tests-py311 tests-py312 tests-py313 tests-py314

.PHONY: tests ## Run tests asynchronously across all configured test containers.
tests:
	docker compose up tests-py310 tests-py311 tests-py312 tests-py313 tests-py314

%:
	@:
