.PHONY: setup test lint build shell

setup:
	pip install -e .[dev]

test:
	pytest tests/ -v

lint:
	# Add ruff or flake8 later
	echo "Linting..."

build:
	docker build -t chimera-env .

shell:
	docker run -it -v $(PWD):/app chimera-env /bin/bash
