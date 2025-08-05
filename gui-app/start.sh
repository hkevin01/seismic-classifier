#!/bin/bash

# Quick start script for the Seismic Dashboard
echo "🌍 Starting Seismic Event Monitoring Dashboard..."

# Navigate to the GUI app directory
cd "$(dirname "$0")/gui-app" || exit 1

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Dependencies not found. Installing..."
    npm install
fi

# Start the development server
echo "🚀 Starting development server..."
echo "🌐 Dashboard will be available at: http://localhost:3000"
echo ""
npm run dev
