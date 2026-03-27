PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup run worker test lint format clean bootstrap

bootstrap:
	bash scripts/bootstrap.sh

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

run:
	$(PYTHON) -m uvicorn controldiff.api.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	$(PYTHON) -m controldiff.workers.main

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests scripts

format:
	$(PYTHON) -m ruff format src tests scripts

clean:
	rm -rf .venv .pytest_cache .ruff_cache artifacts data/processed
