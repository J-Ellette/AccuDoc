# AccuDoc Electron GUI

A modern, cross-platform desktop application for AccuDoc - the Automated Repository Documentation Generator. Built with Electron, this GUI provides full access to all AccuDoc features with an intuitive interface.

## Features

- 🖥️ **Modern Desktop Interface** - Native look and feel on Windows, macOS, and Linux
- 🔍 **Repository Scanning** - Visual interface for scanning local and remote repositories
- 📝 **Documentation Generation** - Easy-to-use controls for generating docs in multiple formats
- 📊 **Code Analysis** - Visual presentation of complexity, best practices, and call graphs
- ❤️ **Health Dashboard** - Interactive health metrics and scoring
- 💾 **Data Export** - Export analysis data to CSV/JSON formats
- 📄 **Open Source Docs** - Generate CONTRIBUTING.md, CODE_OF_CONDUCT.md, and issue templates
- ⌨️ **Integrated Terminal** - Full CLI access within the application
- ⚙️ **Settings Management** - Configure preferences and behavior
- 🎨 **Beautiful UI** - Clean, modern interface with intuitive navigation

## Screenshots

### Main Dashboard
![Home View](docs/screenshots/home.png)

### Code Analysis
![Analysis View](docs/screenshots/analysis.png)

### Health Dashboard
![Health View](docs/screenshots/health.png)

## Installation

### Prerequisites

- **Node.js** 18+ and npm (no build tools required!)
- **Python** 3.8+ (for AccuDoc backend)
- Git (for repository cloning)

### Quick Start

1. **Clone the repository:**
   ```bash
   cd AccuDoc
   cd electron-gui
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Install Python dependencies:**
   ```bash
   cd ..
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   npm start
   ```

## Building

### Build for All Platforms

```bash
npm run build
```

### Platform-Specific Builds

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

Built applications will be in the `dist/` directory.

## Development

### Project Structure

```
electron-gui/
├── src/
│   ├── main/
│   │   └── main.js          # Main process (Electron)
│   └── renderer/
│       ├── index.html       # Main UI
│       ├── styles.css       # Styling
│       └── renderer.js      # Renderer process logic
├── assets/
│   ├── icon.png             # App icon
│   ├── icon.ico             # Windows icon
│   └── icon.icns            # macOS icon
├── package.json             # Dependencies and build config
└── README.md                # This file
```

### Key Technologies

- **Electron 28** - Cross-platform desktop framework
- **Node.js** - JavaScript runtime
- **@xterm/xterm** - Modern terminal emulator (no native build required)
- **marked** - Markdown parser
- **highlight.js** - Syntax highlighting

### Python Bridge

The application communicates with AccuDoc's Python backend through a bridge that:
- Executes CLI commands via child processes
- Streams real-time output to the UI
- Handles errors and exit codes
- Supports all AccuDoc CLI features

## Usage

### Scanning a Repository

1. Click **Scan Repository** from the home screen or sidebar
2. Enter a repository path or click **Browse**
3. Configure options (cache, JSON output)
4. Click **Start Scan**
5. View results in the output panel

### Generating Documentation

1. Navigate to **Generate Docs**
2. Select repository and output paths
3. Choose template, format, language, and theme
4. Click **Generate Documentation**
5. Documentation will be created at the specified location

### Code Analysis

1. Go to **Code Analysis**
2. Enter repository path
3. Click analysis type:
   - **Complexity Analysis** - Identify complex code
   - **Best Practices** - Check coding standards
   - **Call Graph** - Visualize function relationships
   - **Completeness Score** - Rate documentation quality

### Health Dashboard

1. Select **Health Dashboard**
2. Enter repository path
3. Click **Check Health**
4. View metrics:
   - Overall Health Score
   - Documentation Coverage
   - Code Quality
   - Dependency Health

### Using the Terminal

1. Open **Terminal** from the sidebar or press `Ctrl+T`
2. Type AccuDoc CLI commands directly
3. Available commands:
   ```bash
   scan <path>           # Scan repository
   generate <path>       # Generate docs
   export <path>         # Export data
   health <path>         # Check health
   clear                 # Clear terminal
   help                  # Show help
   ```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Window |
| `Ctrl+O` | Open Repository |
| `Ctrl+R` | Scan Repository |
| `Ctrl+G` | Generate Documentation |
| `Ctrl+T` | Show Terminal |
| `Ctrl+,` | Settings |
| `Ctrl+Q` | Quit |
| `F11` | Toggle Fullscreen |
| `Ctrl+0` | Reset Zoom |
| `Ctrl++` | Zoom In |
| `Ctrl+-` | Zoom Out |

## Configuration

Settings are stored in localStorage and include:

- **Theme** - Light/Dark/Auto
- **Cache** - Enable/disable caching
- **Parallel Processing** - Multi-threaded scanning
- **Python Path** - Custom Python interpreter

## Packaging

### Windows

Creates `.exe` installer and portable executable:
```bash
npm run build:win
```

Output: `dist/AccuDoc Setup.exe` and `dist/AccuDoc.exe`

### macOS

Creates `.dmg` disk image:
```bash
npm run build:mac
```

Output: `dist/AccuDoc.dmg`

Requires macOS to build. For code signing, add developer credentials to `package.json`.

### Linux

Creates AppImage and .deb package:
```bash
npm run build:linux
```

Output: `dist/AccuDoc.AppImage` and `dist/accudoc_*.deb`

## Distribution

Built applications include:
- The Electron app
- Node.js runtime
- AccuDoc Python backend
- All dependencies

Users don't need to install Python or Node.js separately.

## Troubleshooting

### Python Not Found

If the app can't find Python:
1. Open Settings
2. Enter the full path to your Python executable
3. Save settings

### Permission Errors

On Linux/macOS, you may need to make the AppImage executable:
```bash
chmod +x AccuDoc.AppImage
```

### Port Already in Use

If you see port errors, close other Electron apps or change the port in `main.js`.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- 📧 Email: support@accudoc.dev
- 🐛 Issues: [GitHub Issues](https://github.com/J-Ellette/AccuDoc/issues)
- 📖 Docs: [Documentation](https://github.com/J-Ellette/AccuDoc)

## Acknowledgments

- Built with [Electron](https://www.electronjs.org/)
- Terminal powered by [xterm.js](https://xtermjs.org/)
- Icons from various open-source projects

---

**Made with ❤️ by the AccuDoc Team**
