.PHONY: help install test lint format check clean build

help:
	@echo "Available targets:"
	@echo "  install  - Install dependencies with poetry"
	@echo "  test     - Run tests with pytest"
	@echo "  lint     - Run ruff linter"
	@echo "  format   - Format code with ruff"
	@echo "  check    - Run all checks (lint, deptry, test)"
	@echo "  clean    - Remove build artifacts"
	@echo "  build    - Build package"

install:
	poetry install

test:
	python -m pytest

lint:
	ruff check .

format:
	ruff check --fix .
	ruff format .

deptry:
	@command -v deptry >/dev/null 2>&1 && deptry . || echo "deptry not installed (requires Python >=3.10), skipping"

check: lint deptry test

clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	poetry build
