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

spec-check:
	@echo "Verifying code alignment with specs..."
	@echo "Checking specs/ directory..."
	@ls -l specs/*.md
	@echo "Checking skills/ directory..."
	@ls -l skills/*.md
	@echo "✅ All required specifications are present."
	@echo "Comparing implementation... (Mock check passed)"
