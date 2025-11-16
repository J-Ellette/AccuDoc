# Clean Installation Script for Windows
# Run this if you had previous installation issues

Write-Host "🧹 Cleaning previous installation..." -ForegroundColor Yellow

# Remove old files
if (Test-Path "node_modules") {
    Write-Host "  Removing node_modules..." -ForegroundColor Gray
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
}

if (Test-Path "package-lock.json") {
    Write-Host "  Removing package-lock.json..." -ForegroundColor Gray
    Remove-Item package-lock.json -ErrorAction SilentlyContinue
}

Write-Host "  Cleaning npm cache..." -ForegroundColor Gray
npm cache clean --force 2>$null

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Green
Write-Host "  This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Installation successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the application, run:" -ForegroundColor Cyan
    Write-Host "  npm start" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Installation failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Make sure Node.js 18+ is installed: node --version" -ForegroundColor Gray
    Write-Host "2. Make sure npm is up to date: npm --version" -ForegroundColor Gray
    Write-Host "3. See TROUBLESHOOTING.md for more help" -ForegroundColor Gray
    Write-Host ""
}
