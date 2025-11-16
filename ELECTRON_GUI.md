# AccuDoc Electron GUI

## Overview

AccuDoc now includes a modern, cross-platform **Electron-based desktop application** that provides full access to all AccuDoc features through an intuitive graphical interface.

## Key Features

✨ **Modern Desktop Experience**
- Native application for Windows, macOS, and Linux
- Beautiful, intuitive user interface
- Real-time progress tracking
- Integrated terminal emulator

🎯 **Complete Feature Access**
- Repository scanning with live output
- Documentation generation in multiple formats
- Code analysis (complexity, best practices, call graphs)
- Project health dashboard with visual metrics
- Data export to CSV/JSON
- Open source documentation generation
- Settings and preferences management

⌨️ **Power User Features**
- Integrated terminal with full CLI access
- Keyboard shortcuts for common actions
- Recent repositories tracking
- Customizable settings

## Quick Start

### Prerequisites

- Node.js 18+ ([Download](https://nodejs.org))
- Python 3.8+ ([Download](https://python.org))

### Installation

```bash
# Navigate to the Electron GUI directory
cd electron-gui

# Install dependencies
npm install

# Run the application
npm start
```

### First Use

1. The application will open automatically
2. Click "Scan Repository" from the home screen
3. Browse to a code folder or enter a path
4. Click "Start Scan" to analyze the repository
5. View results in real-time!

## Documentation

The `electron-gui/` directory contains comprehensive documentation:

- **[START_HERE.md](electron-gui/START_HERE.md)** - Quick start guide for new users
- **[QUICKSTART.md](electron-gui/QUICKSTART.md)** - Quick reference
- **[GETTING_STARTED.md](electron-gui/GETTING_STARTED.md)** - Detailed setup and usage guide
- **[README.md](electron-gui/README.md)** - Complete documentation
- **[IMPLEMENTATION_SUMMARY.md](electron-gui/IMPLEMENTATION_SUMMARY.md)** - Technical overview

## Building for Distribution

Create standalone executables for all platforms:

```bash
cd electron-gui

# Build for all platforms
npm run build

# Or build for specific platforms
npm run build:win      # Windows installer
npm run build:mac      # macOS disk image
npm run build:linux    # Linux AppImage and .deb
```

Built applications will be in the `electron-gui/dist/` directory.

## Features Overview

### Home Screen
- Quick action cards for common tasks
- Recent repositories list
- One-click navigation to all features

### Repository Scanning
- Browse for local repositories
- Enter Git URLs for remote repos
- Real-time scan progress
- JSON output option
- Cache control for performance

### Documentation Generation
- Choose output format (Markdown, HTML, PDF, Text)
- Select from 6 templates
- Multi-language support (7 languages)
- Theme selection for HTML output
- Real-time generation progress

### Code Analysis
- **Complexity Analysis** - Identify complex code
- **Best Practices** - Check coding standards
- **Call Graph** - Visualize dependencies
- **Completeness Score** - Rate documentation quality

### Health Dashboard
- Overall health score
- Documentation coverage metrics
- Code quality assessment
- Dependency health
- Visual metric cards

### Data Export
- Export to CSV reports
- Export to JSON data
- Summary CSV option
- Choose output directory

### Open Source Documentation
- Generate CONTRIBUTING.md
- Generate CODE_OF_CONDUCT.md
- Create issue templates
- Customizable output

### Integrated Terminal
- Full xterm.js terminal
- Direct CLI command access
- Command history
- All AccuDoc CLI features

### Settings
- Theme selection (Light/Dark/Auto)
- Cache control
- Parallel processing toggle
- Custom Python path

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Window |
| `Ctrl+O` | Open Repository |
| `Ctrl+R` | Scan Repository |
| `Ctrl+G` | Generate Documentation |
| `Ctrl+T` | Show Terminal |
| `Ctrl+,` | Open Settings |
| `Ctrl+Q` | Quit Application |
| `F11` | Toggle Fullscreen |

## Architecture

The Electron GUI consists of:

- **Main Process** (`main.js`) - Electron app, window management, IPC
- **Renderer Process** (`renderer.js`) - UI logic, event handling
- **Python Bridge** - Executes AccuDoc CLI commands
- **User Interface** (`index.html`, `styles.css`) - Visual design

Communication flow:
```
UI → Renderer → IPC → Main Process → Python Bridge → AccuDoc CLI → Output
```

## Technology Stack

- **Electron 28** - Cross-platform desktop framework
- **Node.js** - JavaScript runtime
- **xterm.js** - Terminal emulation
- **marked** - Markdown parsing
- **highlight.js** - Syntax highlighting
- **electron-builder** - Application packaging

## Distribution

Built applications include:
- Electron framework
- Node.js runtime  
- AccuDoc Python backend
- All dependencies

**End users don't need to install Python or Node.js!**

## Comparison: GUI vs CLI vs Tkinter

| Feature | Electron GUI | Tkinter GUI | CLI |
|---------|--------------|-------------|-----|
| Cross-platform | ✅ Windows, macOS, Linux | ✅ Windows, macOS, Linux | ✅ All platforms |
| Modern UI | ✅ Yes | ⚠️ Basic | ❌ N/A |
| Terminal Integration | ✅ Built-in | ❌ No | ✅ Native |
| Real-time Output | ✅ Streaming | ⚠️ Limited | ✅ Direct |
| Standalone Distribution | ✅ Yes | ⚠️ Requires Python | ⚠️ Requires Python |
| All Features | ✅ Yes | ✅ Yes | ✅ Yes |
| Best For | Desktop users | Python developers | Automation, CI/CD |

## Troubleshooting

### App Won't Start
- Ensure Node.js 18+ is installed
- Delete `node_modules/` and run `npm install`
- Check for errors in terminal output

### Python Not Found
- Install Python 3.8+
- Open Settings and set custom Python path
- Verify Python is in system PATH

### Scan/Generation Fails
- Check repository path is correct
- Ensure you have read permissions
- View error details in output panel
- Try using the integrated terminal for debugging

## Contributing

The Electron GUI is part of the AccuDoc project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes in `electron-gui/`
4. Test thoroughly
5. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/J-Ellette/AccuDoc/issues)
- **Documentation**: See files in `electron-gui/` directory
- **CLI Reference**: See main `CLI_DOCUMENTATION.md`

## License

MIT License - Same as the main AccuDoc project

## Acknowledgments

- Built with [Electron](https://www.electronjs.org/)
- Terminal powered by [xterm.js](https://xtermjs.org/)
- Markdown rendering by [marked](https://marked.js.org/)

---

**Ready to get started?** Navigate to `electron-gui/` and run `npm start`! 🚀
