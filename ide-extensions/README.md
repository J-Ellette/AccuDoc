# AccuDoc IDE Extensions

Official IDE extensions for AccuDoc - Automated Repository Documentation Generator.

## Available Extensions

### [VS Code Extension](./vscode-accudoc/)
Extension for Visual Studio Code with complete AccuDoc integration.

**Features:**
- Repository scanning
- Documentation generation
- Smart search
- Quality analysis
- Tree view explorer
- Quality metrics sidebar

**Installation:**
```bash
cd vscode-accudoc
npm install
npm run compile
# Package: npm run package
```

**Publish:**
```bash
vsce publish
```

---

### [JetBrains Plugin](./jetbrains-accudoc/)
Plugin for IntelliJ IDEA, PyCharm, WebStorm, and all JetBrains IDEs.

**Features:**
- Repository scanning
- Documentation generation
- Smart search
- Quality analysis
- Tool window
- Context menu integration

**Build:**
```bash
cd jetbrains-accudoc
./gradlew buildPlugin
```

**Output:** `build/distributions/accudoc-jetbrains-1.0.0.jar`

---

## Common Features

Both extensions provide:

1. **Repository Scanning**
   - Analyze codebase metadata
   - Extract API documentation
   - Generate statistics

2. **Documentation Generation**
   - Multiple output formats (Markdown, HTML, Text)
   - Customizable themes
   - Automatic README generation

3. **Smart Search**
   - Fuzzy/exact search
   - Cross-file search
   - Jump-to-line results

4. **Quality Analysis**
   - Documentation quality scores
   - Improvement suggestions
   - Readability metrics

## Requirements

Both extensions require:
- Python 3.7+
- AccuDoc Python package:
  ```bash
  pip install accudoc
  ```

Or direct CLI access to `accudoc_cli.py`

## Development

### VS Code Extension
```bash
cd vscode-accudoc
npm install
npm run compile
code .
# Press F5 to launch Extension Development Host
```

### JetBrains Plugin
```bash
cd jetbrains-accudoc
./gradlew runIde
```

## Publishing

### VS Code
1. Create account on [Visual Studio Marketplace](https://marketplace.visualstudio.com/)
2. Generate Personal Access Token
3. Login: `vsce login <publisher>`
4. Publish: `vsce publish`

### JetBrains
1. Create account on [JetBrains Marketplace](https://plugins.jetbrains.com/)
2. Build plugin: `./gradlew buildPlugin`
3. Upload `.jar` from `build/distributions/`

## Support

- [Main Documentation](../README.md)
- [Report Issues](https://github.com/J-Ellette/AccuDoc/issues)
- [Contributing Guide](../CONTRIBUTING.md)

## License

MIT License - see [LICENSE](../LICENSE) for details
