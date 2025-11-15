# AccuDoc CLI Documentation

Complete guide to using the AccuDoc Command-Line Interface for automation and CI/CD integration.

## Overview

The AccuDoc CLI provides a powerful command-line interface for automated documentation generation. It's designed for:

- **CI/CD Integration**: Automate documentation in your build pipelines
- **Batch Processing**: Process multiple repositories at once
- **Scripting**: Include in shell scripts and automation workflows
- **Headless Environments**: Run without GUI on servers

## Installation

No additional installation needed! The CLI is included with AccuDoc:

```bash
git clone https://github.com/jamesellette/AccuDoc.git
cd AccuDoc
python accudoc_cli.py --help
```

## Quick Start

```bash
# Generate documentation for a repository in one command
python accudoc_cli.py export /path/to/repo -o docs.md

# With custom options
python accudoc_cli.py export https://github.com/user/repo \
  -o docs.html \
  --format html \
  --theme dark \
  --template detailed
```

## Commands

### `export` - Quick Documentation Generation

Scans and generates documentation in one step.

```bash
python accudoc_cli.py export <repository> -o <output-file> [options]
```

**Arguments:**
- `repository` - Repository URL or local path

**Options:**
- `-o, --output` - Output file path (required)
- `-t, --template` - Template: default, minimal, detailed, api, readme (default: default)
- `-f, --format` - Output format: markdown, html, txt (default: markdown)
- `--theme` - HTML theme: default, dark, minimal, corporate (default: default)
- `--markdown-flavor` - Markdown flavor: github, gitlab, commonmark (default: github)
- `--no-cache` - Disable caching for this scan

**Examples:**

```bash
# Basic usage
python accudoc_cli.py export /path/to/repo -o README.md

# HTML with dark theme
python accudoc_cli.py export https://github.com/user/repo \
  -o docs.html --format html --theme dark

# Minimal template with GitLab flavor
python accudoc_cli.py export /local/repo \
  -o docs.md --template minimal --markdown-flavor gitlab

# API documentation
python accudoc_cli.py export /path/to/repo \
  -o api-docs.md --template api

# Disable caching
python accudoc_cli.py export /path/to/repo -o docs.md --no-cache
```

### `scan` - Repository Scanning

Scans a repository and saves the results to a JSON file.

```bash
python accudoc_cli.py scan <repository> [options]
```

**Options:**
- `-o, --output` - Save results to JSON file
- `--json` - Output JSON to stdout
- `--no-cache` - Disable caching

**Examples:**

```bash
# Save scan results to file
python accudoc_cli.py scan /path/to/repo -o scan.json

# Output JSON to stdout (useful for piping)
python accudoc_cli.py scan /path/to/repo --json

# Scan without caching
python accudoc_cli.py scan /path/to/repo -o scan.json --no-cache
```

### `generate` - Documentation Generation

Generates documentation from a previously saved scan.

```bash
python accudoc_cli.py generate <scan-file> -o <output-file> [options]
```

**Arguments:**
- `scan_file` - JSON file with scan results

**Options:**
- `-o, --output` - Output file path (required)
- `-t, --template` - Template (default: default)
- `-f, --format` - Output format (default: markdown)
- `--theme` - HTML theme (default: default)
- `--markdown-flavor` - Markdown flavor (default: github)

**Examples:**

```bash
# Generate markdown from scan
python accudoc_cli.py generate scan.json -o docs.md

# Generate HTML with custom theme
python accudoc_cli.py generate scan.json \
  -o docs.html --format html --theme corporate

# Use detailed template
python accudoc_cli.py generate scan.json \
  -o docs.md --template detailed
```

### `batch` - Batch Processing

Process multiple repositories from a configuration file.

```bash
python accudoc_cli.py batch <batch-file>
```

**Arguments:**
- `batch_file` - JSON configuration file

**Batch Configuration Format:**

```json
{
  "repositories": [
    {
      "url": "https://github.com/user/repo1",
      "output": "docs/repo1.md",
      "template": "default",
      "format": "markdown",
      "markdown_flavor": "github"
    },
    {
      "path": "/local/repo",
      "output": "docs/local.html",
      "template": "detailed",
      "format": "html",
      "theme": "dark"
    }
  ]
}
```

**Example:**

```bash
# Process all repositories in configuration
python accudoc_cli.py batch repos.json

# With verbose output
python accudoc_cli.py -vv batch repos.json
```

### `cache` - Cache Management

Manage AccuDoc's smart caching system.

```bash
python accudoc_cli.py cache <action> <repository>
```

**Actions:**
- `stats` - Show cache statistics
- `clear` - Clear cache for repository

**Examples:**

```bash
# View cache statistics
python accudoc_cli.py cache stats /path/to/repo

# Clear cache
python accudoc_cli.py cache clear /path/to/repo
```

### `info` - System Information

Display information about AccuDoc's capabilities.

```bash
python accudoc_cli.py info
```

Shows available templates, formats, themes, and markdown flavors.

## Global Options

Available for all commands:

- `-v, --verbose` - Increase verbosity (can be used multiple times: -v, -vv, -vvv)
- `-q, --quiet` - Suppress output messages

**Examples:**

```bash
# Verbose output
python accudoc_cli.py -v export /path/to/repo -o docs.md

# Very verbose (debug level)
python accudoc_cli.py -vv scan /path/to/repo -o scan.json

# Quiet mode (only errors)
python accudoc_cli.py -q export /path/to/repo -o docs.md
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Generate Documentation

on:
  push:
    branches: [ main ]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install AccuDoc
        run: |
          git clone https://github.com/jamesellette/AccuDoc.git
          cd AccuDoc
      
      - name: Generate Documentation
        run: |
          python AccuDoc/accudoc_cli.py export . -o docs/README.md
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

### GitLab CI

```yaml
generate-docs:
  stage: build
  image: python:3.9
  script:
    - git clone https://github.com/jamesellette/AccuDoc.git
    - python AccuDoc/accudoc_cli.py export . -o docs/README.md
  artifacts:
    paths:
      - docs/
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Generate Docs') {
            steps {
                sh '''
                    git clone https://github.com/jamesellette/AccuDoc.git
                    python3 AccuDoc/accudoc_cli.py export . -o docs.md
                '''
            }
        }
    }
}
```

## Docker Usage

### Build Image

```bash
docker build -t accudoc .
```

### Run Commands

```bash
# Export documentation
docker run -v $(pwd):/repos -v $(pwd)/output:/output \
  accudoc export /repos -o /output/docs.md

# Scan repository
docker run -v $(pwd):/repos -v $(pwd)/output:/output \
  accudoc scan /repos -o /output/scan.json

# Batch processing
docker run -v $(pwd):/repos -v $(pwd)/output:/output \
  accudoc batch /repos/batch.json
```

### Docker Compose

```yaml
version: '3.8'

services:
  accudoc:
    image: accudoc:latest
    volumes:
      - ./repos:/repos
      - ./output:/output
    command: export /repos/my-project -o /output/docs.md
```

## Advanced Usage

### Pipeline Processing

Separate scan and generate for efficiency:

```bash
# 1. Scan once
python accudoc_cli.py scan /path/to/repo -o scan.json

# 2. Generate multiple outputs from same scan
python accudoc_cli.py generate scan.json -o README.md
python accudoc_cli.py generate scan.json -o docs.html --format html
python accudoc_cli.py generate scan.json -o api.md --template api
```

### JSON Output for Scripting

```bash
# Get scan data as JSON
python accudoc_cli.py scan /path/to/repo --json | jq '.stats'

# Parse and use in scripts
LANG_COUNT=$(python accudoc_cli.py scan . --json | jq '.stats.total_languages')
echo "Languages detected: $LANG_COUNT"
```

### Caching Strategy

```bash
# First run creates cache (slower)
python accudoc_cli.py export /path/to/repo -o docs.md

# Subsequent runs use cache (faster)
python accudoc_cli.py export /path/to/repo -o docs.md

# Force full re-scan when needed
python accudoc_cli.py export /path/to/repo -o docs.md --no-cache

# View cache statistics
python accudoc_cli.py cache stats /path/to/repo

# Clear cache when starting fresh
python accudoc_cli.py cache clear /path/to/repo
```

## Best Practices

1. **Use Templates Wisely**
   - `minimal` - For quick README files
   - `default` - For comprehensive documentation
   - `detailed` - For in-depth technical docs
   - `api` - For API reference documentation
   - `readme` - For GitHub README style

2. **Leverage Caching**
   - Keep cache enabled for large repositories
   - Clear cache after major changes
   - Use `--no-cache` for one-time scans

3. **Batch Processing**
   - Create reusable batch configurations
   - Use different templates per repository
   - Process related projects together

4. **CI/CD Integration**
   - Use quiet mode in pipelines: `-q`
   - Enable verbose logging for debugging: `-vv`
   - Save scan results as artifacts for reuse

5. **Output Formats**
   - Markdown for GitHub/GitLab
   - HTML for documentation sites
   - Plain text for simple output

## Troubleshooting

### Common Issues

**Issue**: Scan fails on large repositories
```bash
# Solution: Use quiet mode and check logs
python accudoc_cli.py -v scan /path/to/repo -o scan.json 2>&1 | tee scan.log
```

**Issue**: Cache is stale
```bash
# Solution: Clear and rebuild
python accudoc_cli.py cache clear /path/to/repo
python accudoc_cli.py scan /path/to/repo -o scan.json
```

**Issue**: Memory issues with large repos
```bash
# Solution: Disable caching and scan with minimal template
python accudoc_cli.py export /path/to/repo \
  -o docs.md --template minimal --no-cache
```

## Examples

### Complete Workflow

```bash
#!/bin/bash
# complete-workflow.sh - Generate comprehensive documentation

REPO_PATH="/path/to/repo"
OUTPUT_DIR="./docs"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# 1. Scan repository
echo "Scanning repository..."
python accudoc_cli.py scan "$REPO_PATH" -o "$OUTPUT_DIR/scan.json"

# 2. Generate multiple formats
echo "Generating documentation..."
python accudoc_cli.py generate "$OUTPUT_DIR/scan.json" \
  -o "$OUTPUT_DIR/README.md" --template readme

python accudoc_cli.py generate "$OUTPUT_DIR/scan.json" \
  -o "$OUTPUT_DIR/api-docs.md" --template api

python accudoc_cli.py generate "$OUTPUT_DIR/scan.json" \
  -o "$OUTPUT_DIR/docs.html" --format html --theme dark

# 3. Show cache stats
echo "Cache statistics:"
python accudoc_cli.py cache stats "$REPO_PATH"

echo "Documentation generation complete!"
```

### Monitoring Script

```bash
#!/bin/bash
# monitor-repos.sh - Monitor multiple repositories

REPOS=(
  "/path/to/repo1"
  "/path/to/repo2"
  "/path/to/repo3"
)

for repo in "${REPOS[@]}"; do
  echo "Processing $repo..."
  python accudoc_cli.py export "$repo" \
    -o "docs/$(basename $repo).md" \
    --template minimal
done

echo "All repositories processed!"
```

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/jamesellette/AccuDoc
- Issues: https://github.com/jamesellette/AccuDoc/issues

---

*AccuDoc CLI - Automate your documentation workflow*
