.PHONY: help venv setup install install-dev test test-cov lint format type-check security clean build docs serve-docs

# Configuration
VENV_NAME = venv
PYTHON = $(VENV_NAME)/bin/python
PIP = $(VENV_NAME)/bin/pip
ACTIVATE = source $(VENV_NAME)/bin/activate

# Make scripts executable on first run
$(shell chmod +x scripts/*.sh 2>/dev/null || true)

# Default target
help:
	@echo "Available commands:"
	@echo "  venv          Create and setup virtual environment"
	@echo "  setup         Complete project setup (venv + install + hooks)"
	@echo "  verify        Verify environment setup"
	@echo "  install       Install package and dependencies"
	@echo "  install-dev   Install package with development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run code linting"
	@echo "  format        Format code with black"
	@echo "  type-check    Run type checking with mypy"
	@echo "  security      Run security checks"
	@echo "  clean         Clean build artifacts"
	@echo "  clean-venv    Remove virtual environment"
	@echo "  build         Build package"
	@echo "  docs          Build documentation"
	@echo "  serve-docs    Serve documentation locally"
	@echo "  all           Run full test suite (format, lint, type-check, test)"

# Virtual environment setup
venv:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV_NAME); \
		echo "Virtual environment created at $(VENV_NAME)"; \
	else \
		echo "Virtual environment already exists at $(VENV_NAME)"; \
	fi
	@echo "To activate: source $(VENV_NAME)/bin/activate"

# Complete setup
setup: venv
	@echo "Setting up development environment..."
	$(ACTIVATE) && $(PIP) install --upgrade pip setuptools wheel
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	$(ACTIVATE) && $(PIP) install -r requirements-dev.txt
	$(ACTIVATE) && $(PIP) install -e .
	@if [ -f ".pre-commit-config.yaml" ]; then \
		$(ACTIVATE) && pre-commit install; \
	fi
	@echo "Setup complete! Activate with: source $(VENV_NAME)/bin/activate"
	@echo "Run 'make verify' to check the setup"

# Verify setup
verify: venv
	@echo "Verifying environment setup..."
	$(ACTIVATE) && bash scripts/verify_setup.sh

# Installation targets (ensure venv exists)
install: venv
	$(ACTIVATE) && $(PIP) install -e .

install-dev: venv
	$(ACTIVATE) && $(PIP) install -e ".[dev,docs,jupyter]"
	$(ACTIVATE) && pre-commit install

# Testing targets
test: venv
	$(ACTIVATE) && pytest tests/ -v

test-cov: venv
	$(ACTIVATE) && pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Code quality targets
lint: venv
	$(ACTIVATE) && flake8 src/ tests/ scripts/

format: venv
	$(ACTIVATE) && black src/ tests/ scripts/

format-check: venv
	$(ACTIVATE) && black --check src/ tests/ scripts/

type-check: venv
	$(ACTIVATE) && mypy src/

security: venv
	$(ACTIVATE) && bandit -r src/
	$(ACTIVATE) && safety check

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

clean-venv:
	rm -rf $(VENV_NAME)
	@echo "Virtual environment removed"

# Build targets
build: venv clean
	$(ACTIVATE) && python -m build

# Documentation targets
docs: venv
	$(ACTIVATE) && cd docs && make html

serve-docs: venv
	$(ACTIVATE) && cd docs/_build/html && python -m http.server 8000

# Combined targets
all: venv format lint type-check test

# Development workflow
dev-setup: setup
	@echo "Development environment setup complete!"
	@echo "You can now run 'make all' to run the full test suite."

# Data and model targets
download-data: venv
	$(ACTIVATE) && python scripts/data_download.py

train-model: venv
	$(ACTIVATE) && python scripts/train_model.py

# Dashboard target
dashboard: venv
	$(ACTIVATE) && python dashboard/app.py

# Real-time classification
classify: venv
	$(ACTIVATE) && python scripts/real_time_classifier.py
