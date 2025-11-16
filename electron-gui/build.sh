#!/bin/bash
# Build script for all platforms

echo "Building AccuDoc Electron GUI for all platforms..."
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/
rm -rf build/

# Install dependencies
echo "Installing dependencies..."
npm install

# Build for all platforms
echo ""
echo "Building for all platforms..."
npm run build

echo ""
echo "Build complete! Check the dist/ directory for outputs."
echo ""
echo "Built packages:"
ls -lh dist/
