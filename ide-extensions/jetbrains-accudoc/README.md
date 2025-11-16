# AccuDoc for JetBrains IDEs

Automated Repository Documentation Generator plugin for IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs.

## Features

- **Repository Scanning**: Analyze your codebase directly from your IDE
- **Documentation Generation**: Create comprehensive markdown/HTML documentation
- **Smart Search**: Fuzzy search across source files and documentation
- **Quality Analysis**: Get documentation quality scores and improvement suggestions
- **Tool Window**: Dedicated AccuDoc panel with all features
- **Context Menu Integration**: Right-click access in project explorer

## Supported IDEs

- IntelliJ IDEA (Community & Ultimate)
- PyCharm (Community & Professional)
- WebStorm
- PhpStorm
- RubyMine
- GoLand
- CLion
- Rider
- Android Studio
- All other JetBrains IDEs based on IntelliJ Platform 2021.1+

## Requirements

- JetBrains IDE (2021.1 or later)
- Python 3.7 or higher
- AccuDoc Python package installed (`pip install accudoc`)
- OR access to `accudoc_cli.py` script

## Installation

### From JetBrains Marketplace
1. Open IDE Settings → Plugins
2. Search for "AccuDoc"
3. Click Install
4. Restart IDE

### Manual Installation
1. Download `.jar` file from [Releases](https://github.com/J-Ellette/AccuDoc/releases)
2. Open IDE Settings → Plugins
3. Click gear icon → Install Plugin from Disk
4. Select downloaded `.jar` file
5. Restart IDE

### Python Package
```bash
pip install accudoc
```

## Usage

### Access AccuDoc

- **Menu**: Tools → AccuDoc
- **Tool Window**: View → Tool Windows → AccuDoc (or click AccuDoc tab on right side)
- **Context Menu**: Right-click in Project view → AccuDoc
- **Find Action**: Ctrl+Shift+A (Cmd+Shift+A on Mac) → "AccuDoc"

### Scan Repository
1. Open Tools → AccuDoc → Scan Repository
2. Or right-click project root → AccuDoc → Scan Repository
3. View results in AccuDoc tool window

### Generate Documentation
1. Tools → AccuDoc → Generate Documentation
2. Select output format (Markdown/HTML/Text)
3. Choose output location
4. Documentation is generated and opened automatically

### Smart Search
1. Tools → AccuDoc → Smart Search
2. Enter search query
3. View results in Find panel
4. Double-click to jump to file/line

### Quality Analysis
1. Tools → AccuDoc → Analyze Quality
2. View quality scores in tool window
3. Get improvement suggestions

## Configuration

Open Settings → Tools → AccuDoc:

- **Python Path**: Path to Python executable (default: `python`)
- **CLI Path**: Path to accudoc_cli.py script (optional, uses installed package if empty)
- **Auto Scan**: Automatically scan on project open
- **Output Format**: Default format for generated documentation
- **Theme**: Theme for HTML output (default/dark)

## Building from Source

```bash
cd ide-extensions/jetbrains-accudoc
./gradlew buildPlugin
```

Output: `build/distributions/accudoc-jetbrains-1.0.0.jar`

## Development

### Prerequisites
- JDK 11 or higher
- Gradle 7.0+

### Build
```bash
./gradlew build
```

### Run IDE with Plugin
```bash
./gradlew runIde
```

### Test
```bash
./gradlew test
```

## Project Structure

```
jetbrains-accudoc/
├── src/main/
│   ├── java/com/accudoc/jetbrains/
│   │   ├── actions/              # Action implementations
│   │   ├── toolwindow/           # Tool window UI
│   │   ├── AccuDocSettings.java  # Settings panel
│   │   └── AccuDocService.java   # Core service
│   └── resources/
│       ├── META-INF/plugin.xml   # Plugin descriptor
│       └── icons/                # Plugin icons
├── build.gradle                  # Gradle build file
└── gradle.properties            # Plugin properties
```

## Troubleshooting

### Python not found
- Set Python path in Settings → Tools → AccuDoc → Python Path
- Ensure Python is in system PATH

### AccuDoc package not found
- Install: `pip install accudoc`
- Or set CLI Path in settings to point to accudoc_cli.py

### Plugin not loading
- Check IDE version compatibility (2021.1+)
- View logs: Help → Show Log in Explorer/Finder

## Known Issues

None at this time. Please report issues on [GitHub](https://github.com/J-Ellette/AccuDoc/issues).

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## License

MIT License - see [LICENSE](../../LICENSE) for details

## Links

- [AccuDoc on GitHub](https://github.com/J-Ellette/AccuDoc)
- [Documentation](https://github.com/J-Ellette/AccuDoc#readme)
- [Report Issues](https://github.com/J-Ellette/AccuDoc/issues)
