#!/bin/bash

# Make scripts executable
# This script ensures all shell scripts have the correct permissions

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

print_header "Making scripts executable..."

# Find all shell scripts and make them executable
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Make scripts executable
find "$SCRIPT_DIR" -name "*.sh" -type f -exec chmod +x {} \;

print_status "Made shell scripts executable:"
find "$SCRIPT_DIR" -name "*.sh" -type f -exec basename {} \; | sort

# Make Makefile executable (if needed)
if [[ -f "$PROJECT_ROOT/Makefile" ]]; then
    chmod +x "$PROJECT_ROOT/Makefile" 2>/dev/null || true
fi

print_header "Script permissions updated successfully!"
