#!/bin/bash
set -e

echo "🚀 Starting Backend Development Environment..."

# Install project dependencies if they exist
if [ -f "/workspace/pyproject.toml" ]; then
    echo "📦 Installing Python dependencies with Poetry..."
    cd /workspace && poetry install
fi

if [ -f "/workspace/requirements.txt" ]; then
    echo "📦 Installing Python dependencies with pip..."
    cd /workspace && pip install -r requirements.txt
fi

if [ -f "/workspace/package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd /workspace && npm install
fi

# Set up development database if needed
if [ "$DB_AUTO_MIGRATE" = "true" ]; then
    echo "🗄️ Setting up development database..."
    # Add database migration commands here
fi

# Start development services
echo "✅ Backend development environment ready!"
echo "🔧 Available tools:"
echo "  - Python $(python --version 2>&1)"
echo "  - Node.js $(node --version)"
echo "  - Poetry $(poetry --version 2>/dev/null || echo 'not installed')"
echo "  - Jupyter $(jupyter --version 2>/dev/null | head -1 || echo 'not installed')"

exec "$@"
