# eedro

`eedro` is a Python CLI tool for bootstrapping new service projects from templates.
It also ships reusable infrastructure helpers for settings loading, logging, command execution patterns, and runtime utilities.

## Features

- `eedro startproject` command to generate a ready-to-run project skeleton.
- Built-in templates for:
  - Python package structure
  - CLI entrypoint
  - Docker and docker-compose setup
  - CI test containers
  - baseline test suite
- Reusable helpers in `eedro.contrib`:
  - settings loading from YAML + environment
  - logging setup and log level control
  - base classes for sync/async CLI commands
  - buffered writer, decorators, and async rate limiter

## Requirements

- Python `>=3.10`
- Docker and Docker Compose for matrix test runs via `make`

## Installation

```bash
pip install .
```

For development:

```bash
pip install -e ".[dev,test]"
```

## Quick Start

Inspect `startproject` options:

```bash
eedro startproject --help
```

Example output:

```text
Usage: eedro startproject [OPTIONS]

Options:
  -i, --ignore                           Use files that exist in the new project path.
  -f, --force                            Overwrite files existing in the new project path.
  --python [3.10|3.11|3.12|3.13|3.14]    Python version of the new project. [required]
  -r, --root TEXT                        The name of the new project's root namespace.
  -c, --context-class TEXT               Python (or dotted) path to the context class.
  -t, --templates DIRECTORY              Path to the templates directory.
  -p, --path DIRECTORY                   Path to the new project.  [required]
  -n, --name TEXT                        Name of the new project.  [required]
  --help                                 Show this message and exit.
```

Generate a new project:

```bash
eedro startproject \
  --name sample-app \
  --path /tmp/sample-app \
  --python 3.12 \
  --root sample_root
```

This creates a project with Python package code, configs, CI/Docker setup, and starter tests.

## CLI Usage

Show global help:

```bash
eedro --help
```

Example output:

```text
Usage: eedro [OPTIONS] COMMAND [ARGS]...

Options:
  -w, --work-dir DIRECTORY                           Set current working directory.
  --log-level [debug|info|warning|error|critical]    Set logging level.  [default: INFO]
  -q, --quiet                                        Disable logging to console.
  --version                                          Show the version and exit.
  --help                                             Show this message and exit.

Commands:
  startproject
```

## Project Structure

- `eedro/core/cli/` - CLI composition and commands.
- `eedro/core/cli/startproject/` - project generator and templates.
- `eedro/contrib/` - reusable runtime helpers.
- `ci/` - containerized test environment.
- `tests/` - unit and smoke tests.

## Development

Run tests for Python 3.12 in Docker:

```bash
make tests-py312
```

Run all configured Python versions:

```bash
make tests
```

Format and lint:

```bash
make pretty
make lint
```

or

```bash
make pretty-lint
```

## Roadmap

Planned improvements are tracked in `PLAN.md`.
