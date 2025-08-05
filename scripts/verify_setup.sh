#!/bin/bash

# Virtual Environment Verification Script
# This script verifies that the virtual environment is properly set up

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="venv"
REQUIRED_PYTHON_VERSION="3.8"

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo
    echo -e "${BLUE}=== $1 ===${NC}"
    echo
}

# Function to compare version numbers
version_compare() {
    local version1=$1
    local version2=$2
    if [[ "$(printf '%s\n' "$version1" "$version2" | sort -V | head -n1)" == "$version2" ]]; then
        return 0  # version1 >= version2
    else
        return 1  # version1 < version2
    fi
}

# Main verification function
verify_setup() {
    local errors=0

    print_header "Seismic Classifier Environment Verification"

    # Check if virtual environment exists
    if [[ -d "$VENV_NAME" ]]; then
        print_success "Virtual environment directory exists"
    else
        print_error "Virtual environment directory not found"
        print_info "Run 'make setup' or 'bash scripts/setup_venv.sh' to create it"
        ((errors++))
    fi

    # Check if virtual environment is activated
    if [[ -n "$VIRTUAL_ENV" ]]; then
        if [[ "$VIRTUAL_ENV" == *"$VENV_NAME" ]]; then
            print_success "Virtual environment is activated: $(basename $VIRTUAL_ENV)"
        else
            print_warning "Different virtual environment is active: $(basename $VIRTUAL_ENV)"
            print_info "Expected: $VENV_NAME"
        fi
    else
        print_warning "Virtual environment is not activated"
        print_info "Run 'source venv/bin/activate' to activate it"
    fi

    # Check Python version
    if command -v python >/dev/null 2>&1; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if version_compare "$PYTHON_VERSION" "$REQUIRED_PYTHON_VERSION"; then
            print_success "Python version: $PYTHON_VERSION (>= $REQUIRED_PYTHON_VERSION required)"
        else
            print_error "Python version: $PYTHON_VERSION (< $REQUIRED_PYTHON_VERSION required)"
            ((errors++))
        fi
    else
        print_error "Python not found in PATH"
        ((errors++))
    fi

    # Check Python executable location
    if [[ -n "$VIRTUAL_ENV" ]]; then
        PYTHON_PATH=$(which python)
        if [[ "$PYTHON_PATH" == "$VIRTUAL_ENV"* ]]; then
            print_success "Python executable is from virtual environment"
        else
            print_warning "Python executable is NOT from virtual environment"
            print_info "Expected: $VIRTUAL_ENV/bin/python"
            print_info "Actual: $PYTHON_PATH"
        fi
    fi

    # Check pip
    if command -v pip >/dev/null 2>&1; then
        PIP_VERSION=$(pip --version | cut -d' ' -f2)
        print_success "Pip version: $PIP_VERSION"

        # Check pip location
        if [[ -n "$VIRTUAL_ENV" ]]; then
            PIP_PATH=$(which pip)
            if [[ "$PIP_PATH" == "$VIRTUAL_ENV"* ]]; then
                print_success "Pip is from virtual environment"
            else
                print_warning "Pip is NOT from virtual environment"
                print_info "Expected: $VIRTUAL_ENV/bin/pip"
                print_info "Actual: $PIP_PATH"
            fi
        fi
    else
        print_error "Pip not found in PATH"
        ((errors++))
    fi

    # Check core dependencies
    print_header "Core Dependencies Check"

    local core_packages=("numpy" "pandas" "scipy" "obspy" "scikit-learn" "matplotlib")
    local missing_packages=()

    for package in "${core_packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            local version=$(python -c "import $package; print($package.__version__)" 2>/dev/null || echo "unknown")
            print_success "$package ($version)"
        else
            print_error "$package - NOT INSTALLED"
            missing_packages+=("$package")
            ((errors++))
        fi
    done

    # Check development dependencies
    print_header "Development Dependencies Check"

    local dev_packages=("pytest" "black" "flake8" "mypy")

    for package in "${dev_packages[@]}"; do
        if command -v $package >/dev/null 2>&1; then
            local version=$($package --version 2>/dev/null | head -n1 || echo "unknown")
            print_success "$package ($version)"
        else
            print_warning "$package - NOT INSTALLED (development dependency)"
        fi
    done

    # Check project structure
    print_header "Project Structure Check"

    local required_dirs=("src" "tests" "scripts" "docs" "data" "config")
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            print_success "Directory: $dir"
        else
            print_warning "Directory missing: $dir"
        fi
    done

    local required_files=("requirements.txt" "requirements-dev.txt" "setup.py" "pyproject.toml" "Makefile" ".gitignore")
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_success "File: $file"
        else
            print_warning "File missing: $file"
        fi
    done

    # Check environment variables
    print_header "Environment Check"

    if [[ -f ".env" ]]; then
        print_success ".env file exists"
    else
        if [[ -f ".env.example" ]]; then
            print_warning ".env file not found (but .env.example exists)"
            print_info "Run 'cp .env.example .env' to create it"
        else
            print_warning "No .env or .env.example file found"
        fi
    fi

    # Check PYTHONPATH
    if [[ -n "$PYTHONPATH" ]]; then
        if [[ "$PYTHONPATH" == *"src"* ]]; then
            print_success "PYTHONPATH includes src directory"
        else
            print_warning "PYTHONPATH does not include src directory"
            print_info "Current PYTHONPATH: $PYTHONPATH"
        fi
    else
        print_warning "PYTHONPATH not set"
        print_info "This may cause import issues"
    fi

    # Summary
    print_header "Verification Summary"

    if [[ $errors -eq 0 ]]; then
        print_success "All critical checks passed! Environment is ready for development."

        echo
        print_info "Next steps:"
        echo "  • Run tests: make test"
        echo "  • Format code: make format"
        echo "  • Download data: make download-data"
        echo "  • Train model: make train-model"
        echo "  • Start dashboard: make dashboard"

    else
        print_error "$errors critical errors found. Please fix them before proceeding."

        if [[ ${#missing_packages[@]} -gt 0 ]]; then
            echo
            print_info "To install missing packages:"
            echo "  source venv/bin/activate"
            echo "  pip install ${missing_packages[*]}"
        fi

        echo
        print_info "To fix most issues, try:"
        echo "  make setup"
        echo "  source venv/bin/activate"
    fi

    return $errors
}

# Run verification
verify_setup
exit_code=$?

echo
if [[ $exit_code -eq 0 ]]; then
    print_success "Environment verification completed successfully!"
else
    print_error "Environment verification failed with $exit_code errors."
fi

exit $exit_code
