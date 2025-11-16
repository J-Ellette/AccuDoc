# AccuDoc GitHub Action

Automatically generate comprehensive documentation for your repository using AccuDoc in your GitHub Actions workflows.

## Features

- 🚀 **Zero Configuration** - Works out of the box with sensible defaults
- 📊 **Health & Quality Checks** - Built-in project health and documentation quality analysis
- 🎯 **Coverage Gates** - Fail builds if documentation coverage is below threshold
- 💬 **PR Comments** - Automatic PR comments with documentation metrics
- 🎨 **Multiple Formats** - Generate Markdown, HTML, PDF, or static sites
- 📝 **6 Templates** - Choose from default, minimal, detailed, API, README, or student templates

## Quick Start

Add this to your workflow (`.github/workflows/docs.yml`):

```yaml
name: Documentation

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: J-Ellette/AccuDoc@v1
        with:
          output-file: 'docs/DOCUMENTATION.md'
```

## Usage Examples

### Basic Documentation Generation

```yaml
- uses: J-Ellette/AccuDoc@v1
  with:
    repository-path: '.'
    output-file: 'docs/README.md'
    template: 'default'
    format: 'markdown'
```

### With Health Check

```yaml
- uses: J-Ellette/AccuDoc@v1
  with:
    output-file: 'docs/README.md'
    health-check: true
    coverage-threshold: 70
```

### With Quality Analysis

```yaml
- uses: J-Ellette/AccuDoc@v1
  with:
    output-file: 'docs/API.md'
    template: 'api'
    quality-check: true
    fail-on-warnings: true
```

### Generate HTML with Dark Theme

```yaml
- uses: J-Ellette/AccuDoc@v1
  with:
    output-file: 'docs/index.html'
    format: 'html'
    theme: 'dark'
```

### Full CI Pipeline with PR Comments

```yaml
name: Documentation Pipeline

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  docs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Generate Documentation
        id: accudoc
        uses: J-Ellette/AccuDoc@v1
        with:
          output-file: 'docs/DOCUMENTATION.md'
          template: 'detailed'
          health-check: true
          quality-check: true
          coverage-threshold: 60
          pr-comment: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `repository-path` | Path to repository to scan | No | `.` |
| `output-file` | Output documentation file | No | `docs/DOCUMENTATION.md` |
| `template` | Template (default, minimal, detailed, api, readme, student) | No | `default` |
| `format` | Format (markdown, html, txt, pdf, site) | No | `markdown` |
| `theme` | HTML theme (default, dark, minimal, corporate) | No | `default` |
| `markdown-flavor` | Markdown flavor (github, gitlab, commonmark) | No | `github` |
| `no-cache` | Disable caching | No | `false` |
| `health-check` | Run health analysis | No | `false` |
| `quality-check` | Run quality analysis | No | `false` |
| `coverage-threshold` | Min coverage % (fails if below) | No | `0` |
| `fail-on-warnings` | Fail on doc warnings | No | `false` |
| `pr-comment` | Post PR comment with results | No | `false` |

## Outputs

| Output | Description |
|--------|-------------|
| `documentation-file` | Path to generated documentation |
| `health-score` | Project health score (0-100) |
| `coverage-score` | Documentation coverage percentage |
| `quality-score` | Documentation quality score (0-100) |

## Advanced Usage

### Framework-Specific Templates

**React/Vue/Angular Projects:**
```yaml
- uses: J-Ellette/AccuDoc@v1
  with:
    template: 'default'
    format: 'html'
    theme: 'minimal'
```

**Python Libraries:**
```yaml
- uses: J-Ellette/AccuDoc@v1
  with:
    template: 'api'
    format: 'markdown'
    quality-check: true
```

**CLI Tools:**
```yaml
- uses: J-Ellette/AccuDoc@v1
  with:
    template: 'detailed'
    markdown-flavor: 'github'
```

### Documentation Coverage Gates

Fail the build if coverage is too low:

```yaml
- uses: J-Ellette/AccuDoc@v1
  with:
    health-check: true
    coverage-threshold: 75
    fail-on-warnings: true
```

### Multi-Format Documentation

Generate multiple formats in one workflow:

```yaml
- name: Generate Markdown
  uses: J-Ellette/AccuDoc@v1
  with:
    output-file: 'docs/README.md'
    format: 'markdown'

- name: Generate HTML Site
  uses: J-Ellette/AccuDoc@v1
  with:
    output-file: 'docs/index.html'
    format: 'html'
    theme: 'corporate'

- name: Generate PDF
  uses: J-Ellette/AccuDoc@v1
  with:
    output-file: 'docs/documentation.pdf'
    format: 'pdf'
```

### Using Outputs

```yaml
- name: Generate Docs
  id: docs
  uses: J-Ellette/AccuDoc@v1
  with:
    health-check: true
    quality-check: true

- name: Check Results
  run: |
    echo "Documentation: ${{ steps.docs.outputs.documentation-file }}"
    echo "Health Score: ${{ steps.docs.outputs.health-score }}"
    echo "Coverage: ${{ steps.docs.outputs.coverage-score }}%"
    echo "Quality: ${{ steps.docs.outputs.quality-score }}"
```

## Troubleshooting

**Action fails with "command not found":**
- Ensure Python 3.7+ is available (use `actions/setup-python@v4`)

**Coverage threshold fails unexpectedly:**
- Run with `health-check: true` locally to see actual coverage
- Check that your repository has README, contributing guidelines, etc.

**PR comments not appearing:**
- Ensure `GITHUB_TOKEN` is provided
- Verify workflow has `pull-requests: write` permission

## Local Development

Test the action locally using [act](https://github.com/nektos/act):

```bash
act push -j docs
```

## License

MIT License - see [LICENSE](LICENSE) for details

## Support

- 📖 [Full Documentation](https://github.com/J-Ellette/AccuDoc)
- 🐛 [Report Issues](https://github.com/J-Ellette/AccuDoc/issues)
- 💡 [Request Features](https://github.com/J-Ellette/AccuDoc/issues/new)
