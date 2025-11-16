@echo off
REM Build script for Windows

echo Building AccuDoc Electron GUI...
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Install dependencies
echo Installing dependencies...
call npm install

REM Build for Windows
echo.
echo Building for Windows...
call npm run build:win

echo.
echo Build complete! Check the dist\ directory for outputs.
echo.
dir dist
pause
