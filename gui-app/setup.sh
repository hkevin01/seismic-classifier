#!/bin/bash

# Seismic Dashboard Setup Script
echo "🌍 Setting up Seismic Event Monitoring Dashboard..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Navigate to the GUI app directory
cd "$(dirname "$0")/gui-app" || exit 1

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the application
echo "🔨 Building the application..."
npm run build

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   cd gui-app"
echo "   npm run dev"
echo ""
echo "🌐 The dashboard will be available at: http://localhost:3000"
echo ""
echo "📋 Features included:"
echo "   ✅ Real-time seismic waveform visualization"
echo "   ✅ Interactive event dashboard with filters"
echo "   ✅ Magnitude distribution charts"
echo "   ✅ File upload simulation for seismic data"
echo "   ✅ Settings panel with theme switching"
echo "   ✅ Notification system for alerts"
echo "   ✅ Modal dialogs for detailed views"
echo "   ✅ Responsive design with smooth animations"
