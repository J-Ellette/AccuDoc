# Installation Troubleshooting

## Common Installation Issues

### Issue: node-pty Build Errors (Windows)

If you see compilation errors related to `node-pty` or `conpty.cc`, this is a known issue with older terminal packages on Windows.

**Solution:** We've updated the packages to use modern alternatives that don't require native compilation.

**Steps:**
1. Delete the `node_modules` folder if it exists
2. Delete `package-lock.json` if it exists
3. Run `npm install` again

```powershell
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install
```

### Issue: Module Not Found Errors

If you see errors about missing modules like `xterm` or `xterm-addon-fit`:

**Solution:** The packages have been renamed to `@xterm/xterm` and `@xterm/addon-fit`. Simply reinstall:

```bash
npm install
```

### Issue: Permission Errors (Windows)

If you see `EPERM` errors:

**Solution:** Run PowerShell or Command Prompt as Administrator, or:

1. Close all open files in the project
2. Close VS Code or other editors
3. Try the installation again

### Issue: Python Not Found

If you see "Python not found" during installation:

**Solution:** The new version doesn't require Python for installation, only for running AccuDoc features. You can install Node packages without Python.

### Issue: Visual Studio Build Tools

If you still see build tool errors:

**Solution:** The updated packages don't require Visual Studio Build Tools. If you have old dependencies, clean and reinstall:

```powershell
npm cache clean --force
Remove-Item -Recurse -Force node_modules
npm install
```

## Fresh Installation

If all else fails, do a completely fresh installation:

```powershell
# Navigate to electron-gui directory
cd electron-gui

# Clean everything
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm cache clean --force

# Reinstall
npm install

# Run
npm start
```

## Alternative: Run Without Terminal

If terminal features continue to cause issues, you can still use all other features. The terminal is optional - all functionality is available through the UI panels.

## Verified Working Configuration

- Node.js: 18.x, 20.x, 22.x
- npm: 9.x, 10.x
- Windows: 10, 11
- macOS: 12+, 13+, 14+
- Linux: Ubuntu 20.04+, Fedora 36+

## Still Having Issues?

1. Check Node.js version: `node --version` (should be 18+)
2. Check npm version: `npm --version` (should be 9+)
3. Make sure you're in the `electron-gui` directory
4. Try the fresh installation steps above
5. If problems persist, the terminal feature can be disabled - all other features work independently

## Success Indicators

A successful installation will:
- Complete without errors
- Create a `node_modules` folder
- Create a `package-lock.json` file
- Show "added X packages" message

Then you can run:
```bash
npm start
```

The app should open without errors!
