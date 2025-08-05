#!/bin/bash

# Seismic Dashboard - Complete Setup and Launch Script
echo "🌊 Seismic Dashboard - Complete Setup & Launch"
echo "=============================================="

# Check if we're in the right directory
if [[ ! -f "package.json" ]]; then
    echo "❌ Error: package.json not found. Please run this script from the gui-app directory."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully!"
echo ""
echo "🎯 Checking TypeScript compilation..."
npx tsc --noEmit

echo ""
echo "🚀 Starting development server..."
echo "   Dashboard will be available at: http://localhost:3000"
echo ""
echo "📊 Features included:"
echo "   ✓ Real-time seismic monitoring"
echo "   ✓ Interactive data visualization"
echo "   ✓ Event classification and analysis"
echo "   ✓ File upload and processing"
echo "   ✓ Notifications and alerts"
echo "   ✓ Modern responsive UI"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
