.PHONY: help install install-dev test lint format check clean build

help:
	@echo "Available targets:"
	@echo "  install      - Install epoxy-calc (user or system-wide with sudo)"
	@echo "  install-dev  - Install dev dependencies with poetry"
	@echo "  test         - Run tests with pytest"
	@echo "  lint         - Run ruff linter"
	@echo "  format       - Format code with ruff"
	@echo "  check        - Run all checks (lint, deptry, test)"
	@echo "  clean        - Remove build artifacts"
	@echo "  build        - Build package"

install:
	@if [ "$$(id -u)" = "0" ]; then \
		pip install .; \
	else \
		pip install --user .; \
	fi

install-dev:
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
