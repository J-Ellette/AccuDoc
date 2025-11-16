# AccuDoc for VS Code

Automated Repository Documentation Generator extension for Visual Studio Code.

## Features

- **Scan Repository**: Analyze your codebase directly from VS Code
- **Generate Documentation**: Create comprehensive markdown/HTML documentation
- **Smart Search**: Fuzzy search across source files and documentation
- **Quality Analysis**: Get documentation quality scores and improvement suggestions
- **Documentation Explorer**: Tree view for quick access to AccuDoc features
- **Quality Metrics**: Real-time quality scoring in the sidebar

## Requirements

- Python 3.7 or higher
- AccuDoc Python package installed (`pip install accudoc`)
- OR access to `accudoc_cli.py` script

## Installation

1. Install the extension from VS Code Marketplace
2. Install AccuDoc Python package:
   ```bash
   pip install accudoc
   ```
3. Open a project folder in VS Code
4. Access AccuDoc from:
   - Command Palette: `Ctrl+Shift+P` → "AccuDoc"
   - Activity Bar: AccuDoc icon
   - Status Bar: Click "AccuDoc" button

## Usage

### Scan Repository
- Command: `AccuDoc: Scan Repository`
- Analyzes your codebase and extracts documentation metadata

### Generate Documentation
- Command: `AccuDoc: Generate Documentation`
- Creates README with API docs, code stats, architecture diagrams
- Choose format: Markdown, HTML, or Text

### Smart Search
- Command: `AccuDoc: Smart Search`
- Search across all source files and documentation
- Jump directly to matched lines

### Quality Analysis
- Command: `AccuDoc: Analyze Quality`
- Get quality scores for your documentation
- Receive improvement suggestions

## Extension Settings

This extension contributes the following settings:

* `accudoc.pythonPath`: Path to Python executable (default: `python`)
* `accudoc.cliPath`: Path to accudoc_cli.py script (optional)
* `accudoc.autoScan`: Automatically scan repository on startup
* `accudoc.outputFormat`: Default output format (markdown/html/text)
* `accudoc.theme`: Theme for HTML output (default/dark)

## Commands

- `accudoc.scan` - Scan Repository
- `accudoc.generate` - Generate Documentation
- `accudoc.export` - Export Documentation
- `accudoc.search` - Smart Search
- `accudoc.quality` - Analyze Quality
- `accudoc.openSettings` - Open Settings

## Known Issues

None at this time. Please report issues on GitHub.

## Release Notes

### 1.0.0

Initial release:
- Repository scanning
- Documentation generation
- Smart search
- Quality analysis
- Tree view explorer
- Quality metrics sidebar

## Contributing

Contributions welcome! Visit [AccuDoc on GitHub](https://github.com/J-Ellette/AccuDoc)

## License

MIT License - see LICENSE file for details
