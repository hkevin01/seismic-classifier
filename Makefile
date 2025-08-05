.PHONY: help install install-dev test test-cov lint format type-check security clean build docs serve-docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install       Install package and dependencies"
	@echo "  install-dev   Install package with development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run code linting"
	@echo "  format        Format code with black"
	@echo "  type-check    Run type checking with mypy"
	@echo "  security      Run security checks"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  docs          Build documentation"
	@echo "  serve-docs    Serve documentation locally"
	@echo "  all           Run full test suite (format, lint, type-check, test)"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs,jupyter]"
	pre-commit install

# Testing targets
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Code quality targets
lint:
	flake8 src/ tests/ scripts/

format:
	black src/ tests/ scripts/

format-check:
	black --check src/ tests/ scripts/

type-check:
	mypy src/

security:
	bandit -r src/
	safety check

# Clean targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Build targets
build: clean
	python -m build

# Documentation targets
docs:
	cd docs && make html

serve-docs:
	cd docs/_build/html && python -m http.server 8000

# Combined targets
all: format lint type-check test

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "You can now run 'make all' to run the full test suite."

# Data and model targets
download-data:
	python scripts/data_download.py

train-model:
	python scripts/train_model.py

# Dashboard target
dashboard:
	python dashboard/app.py

# Real-time classification
classify:
	python scripts/real_time_classifier.py
