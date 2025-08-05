#!/bin/bash

# Virtual Environment Setup Script for Seismic Classifier
# This script creates and activates a virtual environment and installs dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="venv"
PYTHON_MIN_VERSION="3.8"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    local version=$($python_cmd --version 2>&1 | cut -d' ' -f2)
    local major=$(echo $version | cut -d'.' -f1)
    local minor=$(echo $version | cut -d'.' -f2)
    
    if [[ $major -eq 3 && $minor -ge 8 ]]; then
        return 0
    else
        return 1
    fi
}

# Function to find suitable Python executable
find_python() {
    for python_cmd in python3.11 python3.10 python3.9 python3.8 python3 python; do
        if command -v $python_cmd >/dev/null 2>&1; then
            if check_python_version $python_cmd; then
                echo $python_cmd
                return 0
            fi
        fi
    done
    return 1
}

# Main setup function
setup_environment() {
    print_header "Setting up Python virtual environment for Seismic Classifier"
    
    # Check if virtual environment already exists
    if [[ -d "$VENV_NAME" ]]; then
        print_warning "Virtual environment '$VENV_NAME' already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf "$VENV_NAME"
        else
            print_status "Using existing virtual environment"
            source "$VENV_NAME/bin/activate"
            print_status "Virtual environment activated: $VIRTUAL_ENV"
            return 0
        fi
    fi
    
    # Find suitable Python interpreter
    print_status "Finding suitable Python interpreter..."
    if ! PYTHON_CMD=$(find_python); then
        print_error "No suitable Python interpreter found (requires Python $PYTHON_MIN_VERSION+)"
        print_error "Please install Python $PYTHON_MIN_VERSION or later"
        exit 1
    fi
    
    print_status "Using Python: $PYTHON_CMD ($($PYTHON_CMD --version))"
    
    # Create virtual environment
    print_status "Creating virtual environment '$VENV_NAME'..."
    $PYTHON_CMD -m venv "$VENV_NAME"
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Install dependencies
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing core dependencies from requirements.txt..."
        pip install -r requirements.txt
    fi
    
    if [[ -f "requirements-dev.txt" ]]; then
        print_status "Installing development dependencies from requirements-dev.txt..."
        pip install -r requirements-dev.txt
    fi
    
    # Install package in development mode
    print_status "Installing package in development mode..."
    pip install -e .
    
    # Install pre-commit hooks if available
    if [[ -f ".pre-commit-config.yaml" ]]; then
        print_status "Installing pre-commit hooks..."
        pre-commit install
    fi
    
    print_header "Virtual environment setup complete!"
    print_status "Virtual environment: $VIRTUAL_ENV"
    print_status "Python version: $(python --version)"
    print_status "Pip version: $(pip --version)"
    
    echo
    print_header "To activate the virtual environment in the future, run:"
    echo -e "${BLUE}source $VENV_NAME/bin/activate${NC}"
    echo
    print_header "To deactivate the virtual environment, run:"
    echo -e "${BLUE}deactivate${NC}"
    echo
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -f, --force    Force recreation of virtual environment"
    echo
    echo "This script will:"
    echo "  1. Create a Python virtual environment"
    echo "  2. Install all dependencies"
    echo "  3. Install the package in development mode"
    echo "  4. Set up pre-commit hooks"
}

# Parse command line arguments
FORCE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Force recreation if requested
if [[ "$FORCE" == true && -d "$VENV_NAME" ]]; then
    print_status "Force flag set, removing existing virtual environment..."
    rm -rf "$VENV_NAME"
fi

# Run setup
setup_environment
