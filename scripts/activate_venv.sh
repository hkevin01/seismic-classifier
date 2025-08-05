#!/bin/bash

# Activation script for Seismic Classifier virtual environment
# Usage: source scripts/activate_venv.sh

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

VENV_NAME="venv"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/$VENV_NAME"

# Check if virtual environment exists
if [[ ! -d "$VENV_PATH" ]]; then
    echo -e "${RED}[ERROR]${NC} Virtual environment not found at $VENV_PATH"
    echo -e "${YELLOW}[INFO]${NC} Run 'make setup' or 'bash scripts/setup_venv.sh' to create it"
    return 1
fi

# Check if already in a virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    # Check if it's the same virtual environment
    if [[ "$VIRTUAL_ENV" == "$VENV_PATH" ]]; then
        echo -e "${GREEN}[INFO]${NC} Already in the correct virtual environment: $VIRTUAL_ENV"
        return 0
    else
        echo -e "${YELLOW}[WARNING]${NC} Already in a different virtual environment: $VIRTUAL_ENV"
        echo -e "${YELLOW}[WARNING]${NC} Deactivating current environment..."
        deactivate
    fi
fi

# Activate virtual environment
echo -e "${GREEN}[INFO]${NC} Activating virtual environment: $VENV_PATH"
source "$VENV_PATH/bin/activate"

# Verify activation
if [[ "$VIRTUAL_ENV" == "$VENV_PATH" ]]; then
    echo -e "${GREEN}[SUCCESS]${NC} Virtual environment activated successfully"
    echo -e "${GREEN}[INFO]${NC} Python: $(which python)"
    echo -e "${GREEN}[INFO]${NC} Pip: $(which pip)"
    echo -e "${GREEN}[INFO]${NC} Python version: $(python --version)"

    # Set PYTHONPATH to include src directory
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
    echo -e "${GREEN}[INFO]${NC} PYTHONPATH updated to include src directory"

    # Change to project root if not already there
    if [[ "$PWD" != "$PROJECT_ROOT" ]]; then
        cd "$PROJECT_ROOT"
        echo -e "${GREEN}[INFO]${NC} Changed directory to project root: $PROJECT_ROOT"
    fi

    return 0
else
    echo -e "${RED}[ERROR]${NC} Failed to activate virtual environment"
    return 1
fi
