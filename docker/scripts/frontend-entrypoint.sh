#!/bin/bash
set -e

echo "🎨 Starting Frontend Development Environment..."

# Change to app directory
cd /app

# Install project dependencies if they exist
if [ -f "package.json" ]; then
    echo "📦 Installing dependencies..."

    # Detect package manager and install
    if [ -f "yarn.lock" ]; then
        echo "Using Yarn..."
        yarn install
    elif [ -f "pnpm-lock.yaml" ]; then
        echo "Using PNPM..."
        pnpm install
    else
        echo "Using NPM..."
        npm install
    fi
fi

# Set up development environment
echo "✅ Frontend development environment ready!"
echo "🔧 Available tools:"
echo "  - Node.js $(node --version)"
echo "  - NPM $(npm --version)"
echo "  - Yarn $(yarn --version 2>/dev/null || echo 'not installed')"
echo "  - PNPM $(pnpm --version 2>/dev/null || echo 'not installed')"
echo "  - TypeScript $(tsc --version 2>/dev/null || echo 'not installed globally')"

echo "🌐 Common development commands:"
echo "  - npm run dev / yarn dev / pnpm dev"
echo "  - npm run build / yarn build / pnpm build"
echo "  - npm test / yarn test / pnpm test"

exec "$@"
