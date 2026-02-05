.PHONY: setup test lint build shell

setup:
	@echo "Installing dependencies with uv..."
	uv pip install -e ".[dev]"

test:
	@echo "Running tests with uv..."
	uv run pytest tests/ -v

lint:
	@echo "Linting with uv..."
	uv run ruff check .
	uv run black --check .

build:
	docker build -t chimera-env .

shell:
	uv run bash
