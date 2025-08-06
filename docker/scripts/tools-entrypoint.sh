#!/bin/bash
set -e

echo "🛠️ Starting Development Tools Environment..."

# Change to workspace directory
cd /workspace

# Set up pre-commit hooks if they exist
if [ -f ".pre-commit-config.yaml" ]; then
    echo "⚙️ Installing pre-commit hooks..."
    pre-commit install
fi

# Check for common configuration files and offer setup
echo "🔍 Checking project setup..."

if [ ! -f ".gitignore" ]; then
    echo "⚠️ No .gitignore found. Consider creating one."
fi

if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ] && [ ! -f "package.json" ]; then
    echo "⚠️ No package configuration found."
fi

echo "✅ Development tools environment ready!"
echo "🔧 Available tools:"
echo "  - Python $(python --version 2>&1)"
echo "  - Node.js $(node --version)"
echo "  - Go $(go version)"
echo "  - Docker $(docker --version)"
echo "  - Git $(git --version)"

echo "🚀 Available commands:"
echo "  Code Quality:"
echo "    - black --check ."
echo "    - flake8 ."
echo "    - mypy ."
echo "    - eslint ."
echo "    - prettier --check ."
echo "    - golangci-lint run"
echo "  Security:"
echo "    - bandit -r ."
echo "    - safety check"
echo "    - snyk test"
echo "    - trivy fs ."
echo "  Testing:"
echo "    - pytest"
echo "    - npm test"
echo "    - go test ./..."

exec "$@"
