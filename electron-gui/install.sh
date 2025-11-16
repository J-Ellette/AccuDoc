#!/bin/bash
# Clean Installation Script for Unix/Mac
# Run this if you had previous installation issues

echo "🧹 Cleaning previous installation..."

# Remove old files
if [ -d "node_modules" ]; then
    echo "  Removing node_modules..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    echo "  Removing package-lock.json..."
    rm -f package-lock.json
fi

echo "  Cleaning npm cache..."
npm cache clean --force > /dev/null 2>&1

echo ""
echo "📦 Installing dependencies..."
echo "  This may take a few minutes..."
echo ""

npm install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "To start the application, run:"
    echo "  npm start"
    echo ""
else
    echo ""
    echo "❌ Installation failed!"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Make sure Node.js 18+ is installed: node --version"
    echo "2. Make sure npm is up to date: npm --version"
    echo "3. See TROUBLESHOOTING.md for more help"
    echo ""
fi
