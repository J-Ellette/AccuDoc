# Getting Started with AccuDoc Electron GUI

This guide will help you set up and run the AccuDoc Electron GUI application.

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Node.js and npm**
   - Download from: https://nodejs.org/
   - Recommended: Node.js 18.x or later
   - Verify installation:
     ```bash
     node --version
     npm --version
     ```

2. **Python 3.8+**
   - Download from: https://python.org/
   - Make sure Python is in your PATH
   - Verify installation:
     ```bash
     python --version
     ```

3. **Git** (optional, for cloning repositories)
   - Download from: https://git-scm.com/

## Installation Steps

### 1. Navigate to the Electron GUI Directory

```bash
cd AccuDoc/electron-gui
```

### 2. Install Node.js Dependencies

```bash
npm install
```

This will install:
- Electron framework
- Terminal emulator (xterm.js)
- Markdown parser (marked)
- Syntax highlighter (highlight.js)
- Build tools (electron-builder)

### 3. Install Python Dependencies

Go back to the main AccuDoc directory and install Python dependencies:

```bash
cd ..
pip install -r requirements.txt
```

Note: AccuDoc uses mostly standard library, so this should be quick.

### 4. Run the Application

Return to the electron-gui directory and start the app:

```bash
cd electron-gui
npm start
```

The AccuDoc GUI should open in a new window!

## First-Time Usage

### 1. Scan Your First Repository

1. From the home screen, click **"Start Scan"** in the Scan Repository card
2. Click the **"Browse"** button and select a folder containing code
3. Click **"Start Scan"**
4. Watch the scan progress in real-time
5. View the results in the output panel

### 2. Generate Documentation

1. Click **"Generate Docs"** in the sidebar
2. Enter or browse to your repository path
3. Choose where to save the documentation
4. Select a template (Default is recommended for first-time users)
5. Choose an output format (Markdown, HTML, PDF, or Text)
6. Click **"Generate Documentation"**
7. Open the generated file to view your documentation!

### 3. Check Project Health

1. Navigate to **"Health Dashboard"**
2. Enter your repository path
3. Click **"Check Health"**
4. View comprehensive health metrics including:
   - Overall health score
   - Documentation coverage
   - Code quality metrics
   - Dependency health

## Tips and Tricks

### Using the Terminal

- Press `Ctrl+T` to quickly open the terminal
- Type `help` to see available commands
- Access all CLI features directly from the terminal
- Use arrow keys to navigate command history

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Repository |
| `Ctrl+R` | Start Scan |
| `Ctrl+G` | Generate Docs |
| `Ctrl+T` | Open Terminal |
| `Ctrl+,` | Open Settings |

### Settings

Customize your experience in Settings:
- Choose light or dark theme
- Enable/disable caching for faster scans
- Set custom Python path if needed
- Configure default preferences

### Recent Repositories

The home screen shows your recently scanned repositories. Click any to quickly open it again.

## Building for Distribution

### Build for Your Platform

**Windows:**
```bash
npm run build:win
```
Output: `dist/AccuDoc Setup.exe`

**macOS:**
```bash
npm run build:mac
```
Output: `dist/AccuDoc.dmg`

**Linux:**
```bash
npm run build:linux
```
Output: `dist/AccuDoc.AppImage` and `dist/accudoc_*.deb`

### Build for All Platforms

```bash
npm run build
```

Built applications include everything needed - users don't need Python or Node.js installed!

## Troubleshooting

### "Python not found" Error

**Solution:**
1. Make sure Python is installed and in your PATH
2. Open Settings (Ctrl+,)
3. Enter the full path to your Python executable
   - Windows: `C:\Python39\python.exe`
   - macOS/Linux: `/usr/bin/python3`

### Application Won't Start

**Solution:**
1. Delete `node_modules/` folder
2. Run `npm install` again
3. Try `npm start` again

### Terminal Not Working

**Solution:**
1. Make sure you're in the electron-gui directory
2. Check that all dependencies installed correctly
3. Look for errors in the DevTools console (View → Toggle DevTools)

### Scan is Slow

**Tips:**
- Enable caching in Settings for repeat scans
- Use the JSON output option for faster processing
- Close other resource-intensive applications

## Development

### Project Structure

```
electron-gui/
├── src/
│   ├── main/
│   │   └── main.js          # Electron main process
│   └── renderer/
│       ├── index.html       # UI markup
│       ├── styles.css       # Styling
│       └── renderer.js      # UI logic
├── assets/                  # Icons and images
├── package.json             # Dependencies & config
└── README.md
```

### Running in Development Mode

Development mode includes:
- Hot reload on file changes
- DevTools open by default
- Detailed error messages
- Console logging

To enable:
```bash
npm start
```

### Debugging

**Open DevTools:**
- View → Toggle Developer Tools
- Or press `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (macOS)

**View Logs:**
- Check the terminal where you ran `npm start`
- Check the DevTools console in the app window
- Look for error messages in the status bar

## Next Steps

Now that you're set up, explore these features:

1. **Code Analysis** - Analyze complexity, call graphs, and best practices
2. **Data Export** - Export analysis data to CSV or JSON
3. **Open Source Docs** - Generate CONTRIBUTING.md and CODE_OF_CONDUCT.md
4. **Multiple Formats** - Try generating HTML, PDF, and different markdown flavors
5. **Internationalization** - Generate docs in multiple languages

## Getting Help

- **Documentation:** See the main README.md
- **Issues:** Report bugs on GitHub
- **CLI Reference:** Check CLI_DOCUMENTATION.md in the main AccuDoc folder

## Contributing

Want to improve the GUI? Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Happy documenting! 🚀
