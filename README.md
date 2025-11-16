# AccuDoc

**Automated Repository Documentation Generator**

AccuDoc is a Python application that scans repositories (local or remote) and automatically generates comprehensive documentation based on what it finds.

## Features

- **🆕 Electron GUI**: Modern cross-platform desktop application with complete CLI feature parity
  - **Native Desktop Experience**: Full-featured GUI for Windows, macOS, and Linux
  - **Integrated Terminal**: Access CLI commands directly within the app
  - **Real-time Progress**: Live output streaming for all operations
  - **Beautiful Interface**: Modern design with intuitive navigation and tabbed views
  - **Complete Feature Set**: All 35+ CLI commands accessible through GUI
  - **Advanced Features**:
    - **Batch Processing**: Multi-repository analysis with worker configuration
    - **Comparison & Trends**: Repository comparison, trend analysis, branch comparison, version checking
    - **Quality Tools**: Spell check, grammar check, readability analysis, database schema validation, monorepo analysis, breaking changes detection
    - **Collaboration**: Session management, user/team management, comments system, API server control
    - **Enterprise**: Multi-repository dashboard, custom reports, hooks system, archive management, onboarding workflows, compliance checking
    - **Health Dashboard**: Project health scoring with interactive improvement tips
    - **URL Validation**: Support for both local paths and remote repository URLs
  - See `electron-gui/` directory for the Electron application
- **Tkinter GUI**: Easy-to-use graphical interface built with Tkinter
  - **🆕 Drag & Drop Support**: Simply drag and drop repository folders into the application
  - **🆕 Live Preview**: Side-by-side markdown and HTML preview for generated documentation
  - **🆕 Multi-Window Support**: Open multiple repositories in separate windows for parallel work
  - **🆕 Internationalization**: Multi-language UI support (English, Spanish, French, German, Chinese, Japanese, Arabic) with auto-detection
- **🆕 Documentation Translation**: Generate documentation in 7 languages
  - English (en) - default
  - Spanish (es) - Español
  - French (fr) - Français
  - German (de) - Deutsch
  - Chinese (zh) - 中文
  - Japanese (ja) - 日本語
  - Arabic (ar) - العربية
- **Repository Scanning**: Supports both local folders and remote Git repositories
- **Automatic Analysis**: Detects:
  - Programming languages and file types
  - Dependencies and package managers
  - Build tools and CI/CD configurations
  - Existing documentation files
  - Project structure
  - License information
- **Comprehensive Documentation**: Generates documentation including:
  - Project overview and features
  - Technology stack and frameworks
  - Architecture diagrams (Mermaid)
  - Dependency graphs
  - API documentation
  - Code examples
  - Code statistics
  - Changelog and contributors
  - Installation and usage instructions
  - Project structure
  - TODO/FIXME comments
- **Custom Templates**: Choose from 6 built-in templates or create your own
  - Default - Complete documentation
  - Minimal - Essential sections only
  - Detailed - Comprehensive technical docs
  - API Reference - Focus on API documentation
  - README Style - GitHub README format
  - **🆕 Student Project** - Academic/student project template
- **Markdown Flavors**: Export in different markdown flavors
  - GitHub Flavored Markdown (default)
  - GitLab Flavored Markdown
  - CommonMark (standard)
- **Multiple Export Formats**:
  - Markdown with flavor support
  - HTML with professional themes
  - Plain text
  - **PDF** (requires weasyprint or wkhtmltopdf)
  - **Static Website** with search functionality
- **HTML Themes**: Professional themes for HTML export
  - Default - Clean, professional light theme
  - Dark - Modern dark theme
  - Minimal - Ultra-clean, distraction-free
  - Corporate - Professional gradient theme
- **🆕 Command-Line Interface**: Comprehensive CLI for automation
  - 10 commands: scan, generate, export, site, info, cache, check-links, plugins, batch, **opensource**
  - JSON output for CI/CD integration
  - Batch processing support
- **🆕 Open Source Documentation**: Auto-generate standard open source files
  - **CONTRIBUTING.md**: Contributor guidelines with language-specific instructions
  - **CODE_OF_CONDUCT.md**: Based on Contributor Covenant 2.0
  - **Issue Templates**: Bug reports and feature requests for GitHub/GitLab
  - Fully customizable and project-aware
- **🆕 Code Analysis Suite**: Advanced code analysis features
  - **Complexity Analysis**: Identify complex code that needs documentation
  - **Best Practices Checker**: Detect coding standards violations
  - **Call Graph Generation**: Visualize function relationships and dependencies
  - **Documentation Completeness Score**: Rate documentation quality with actionable feedback
- **🆕 GitHub/GitLab/Bitbucket API Integration**: Direct repository access without cloning (50-80% faster)
- **🆕 Smart Caching**: File-level caching for 50-90% performance improvement
- **🆕 Parallel Processing**: Multi-threaded scanning (3-5x faster on large repos)
- **🆕 Plugin System**: Extensible architecture for custom analyzers and exporters
- **🆕 Static Site Generation**: Generate complete documentation websites with search
- **🆕 Link Checking**: Validate documentation links
- **🆕 Docker Support**: Containerized deployment
- **🆕 CI/CD Templates**: Ready-to-use workflows for GitHub Actions, GitLab CI, Jenkins
- **🆕 Data Export**: Export repository analysis data to CSV/JSON
  - **CSV Reports**: Files, dependencies, TODOs, metrics, language breakdown
  - **Summary CSV**: Single file with key metrics for quick overview
  - **JSON Export**: Complete repository data in JSON format
  - Export from live scan or existing scan results
- **🆕 Project Health Dashboard**: Comprehensive health metrics and scoring
  - **Overall Health Score**: Weighted score based on multiple factors
  - **Documentation Coverage**: Measures presence and quality of documentation
  - **Code Quality**: Evaluates TODOs, complexity, best practices, tests
  - **Dependency Health**: Assesses dependency count and freshness
  - **Maintainability Index**: Comment ratio, config files, repo size
  - **License Compliance**: License detection and compliance checking
  - **Recommendations**: Actionable suggestions for improvement
  - Text and JSON output formats
- **🆕 Trend Analysis**: Track repository growth over time
  - **Historical Metrics**: Commit count, file count, contributors, lines of code
  - **Growth Rates**: Calculate percentage growth across metrics
  - **Language Trends**: Track language distribution over time
  - **Time Periods**: Week, month, quarter, year, or all history
  - **Flexible Data Points**: Customizable number of intervals
  - **Multiple Formats**: Text report, JSON data, CSV export
  - Uses git history for accurate historical analysis
- **🆕 Comparison Reports**: Compare multiple repositories side-by-side
  - **Multi-Repository Analysis**: Compare 2 or more repositories
  - **Comprehensive Metrics**: Files, code stats, dependencies, documentation, health scores
  - **Automatic Rankings**: Rank repositories by various criteria
  - **Best/Worst Performers**: Identify leaders and areas needing improvement
  - **Side-by-Side Tables**: Clear comparison tables for all metrics
  - **Multiple Formats**: Text report, JSON data, CSV export
  - Works with live scans or existing JSON files
- **🆕 Multi-Repository Documentation Consistency Dashboard**: Organization-wide documentation analytics
  - **Documentation Coverage Analysis**: Track coverage across all repositories
  - **Style Guide Compliance**: Check against Google, Microsoft, or Plain Language guidelines
  - **Completeness Scoring**: Rate documentation quality with detailed breakdowns
  - **Consistency Gap Detection**: Identify discrepancies between repositories
  - **Organization-Wide Analytics**: Trends, rankings, and summary statistics
  - **Membership Integration**: Role-based access control and sharing
  - **Multiple Export Formats**: Text, Markdown, HTML, JSON reports
  - **Customizable Thresholds**: Configure minimum coverage and completeness requirements
  - **Actionable Recommendations**: Get specific improvement suggestions
- **🆕 Custom Reports**: User-defined report templates
  - **Template-Based**: JSON configuration for custom reports
  - **4 Built-in Templates**: Minimal, Detailed, Executive, Technical
  - **Variable Substitution**: Dynamic content with {variable} syntax
  - **Data Sections**: Auto-format repository data fields
  - **Nested Data Access**: Use dot notation (statistics.total_lines)
  - **Multiple Formats**: Markdown, HTML, plain text
  - **Template Validation**: Ensures template correctness
  - **Sample Templates**: Quick-start with pre-made examples
- **🆕 Real-Time Collaboration**: Multi-user documentation editing and review
  - **WebSocket Server**: Real-time synchronization for multiple users
  - **Live Document Editing**: Collaborative editing with conflict resolution
  - **Comment Threads**: Contextual comments with line-by-line discussions
  - **Review Workflows**: Request/approve/reject documentation changes
  - **User Management**: Role-based access (viewer, editor, reviewer, admin)
  - **Cursor Tracking**: See other users' cursor positions in real-time
  - **Change Notifications**: Visual indicators for edits by other users
  - **Slack/Teams Integration**: Notifications for comments and review requests
  - **Session Management**: Persistent collaboration sessions with history
  - **CLI Commands**: 
    - `start-collab-server` - Start WebSocket collaboration server
    - `collab-status` - Check server status and statistics
    - `manage-sessions` - List active sessions and edit history
    - `manage-comments` - View and resolve comment threads
    - `manage-reviews` - Track review workflows and approvals
  - **GUI Integration**: Full collaboration features in Electron interface
  - **Database Storage**: SQLite for persistent comments, reviews, and sessions
- **🆕 Advanced Quality Scoring**: Comprehensive documentation quality analysis
  - **Multi-Dimensional Scoring**: Clarity, completeness, and accuracy analysis
  - **Readability Metrics**: Flesch Reading Ease and Gunning Fog Index calculations
  - **Industry Benchmarking**: Compare against 8 project types (web framework, library, CLI tool, API service, mobile app, desktop app, data science, other)
  - **Documentation Debt Tracking**: Monitor quality trends over time
  - **Improvement Suggestions**: AI-powered recommendations for quality enhancement
  - **Historical Analysis**: Track quality metrics evolution with SQLite storage
  - **Multiple Output Formats**: Text, JSON, HTML, and Markdown reports
  - **CLI Commands**: 
    - `quality-analyze` - Run comprehensive quality analysis with benchmarking
    - `quality-history` - View quality score trends and historical data
    - `quality-benchmark` - Compare against industry standards
    - `quality-report` - Generate detailed reports with all metrics
  - **GUI Integration**: Visual quality dashboard with score circles and trend charts
  - **Percentile Ranking**: See how your documentation compares to industry standards
- **🆕 REST API**: Programmatic access via HTTP
  - **RESTful Design**: Clean JSON API for all features
  - **11 Endpoints**: Scan, generate, health, trends, compare, custom reports, data export
  - **CORS Enabled**: Ready for web applications
  - **OpenAPI Documentation**: Built-in API spec
  - **Easy Integration**: Works with curl, Python requests, any HTTP client
  - **Flask-based**: Lightweight and fast
  - **Multiple Features Exposed**:
    - Repository scanning
    - Documentation generation with translation
    - Health metrics calculation
    - Trend analysis
    - Multi-repository comparison
    - Custom report generation
    - Data export
- **🆕 Hooks System**: Event-driven extensibility
  - **Event-Driven Architecture**: Register hooks at specific execution points
  - **11 Hook Points**: Before/after scan, generate, export, file analysis, health metrics, plus custom
  - **Multiple Hook Types**: Python functions, shell commands
  - **Priority-Based Execution**: Control hook execution order
  - **Context Propagation**: Pass data between hooks
  - **Enable/Disable Support**: Turn hooks on/off dynamically
  - **Built-in Hooks**: Pre-defined hooks for common tasks
  - **Error Resilience**: Hooks failures don't stop execution
  - **CLI Management**: List, enable, disable hooks via command line

- **🆕 Immutable Documentation Archive**: Cryptographically-signed archival system
  - **Cryptographic Signatures**: HMAC-SHA256 signatures for content integrity
  - **Tamper Detection**: Automatic detection of any content modifications
  - **Multi-Format Support**: Archive Markdown, HTML, and PDF documentation
  - **Compression**: Gzip compression for 60-90% space savings
  - **Role-Based Access**: Integration with membership system for secure access
  - **Audit Trail**: Complete logging of all archive operations
  - **Tag-Based Organization**: Organize archives with tags and descriptions
  - **CLI & GUI**: Full command-line and graphical interface support
  - **Validation**: Verify archive signatures and content integrity
  - **Statistics**: Track archive usage and storage metrics
  - See [ARCHIVE_FEATURE.md](ARCHIVE_FEATURE.md) for detailed documentation

- **🆕 Live Documentation Testbed**: Interactive code execution in secure containers
  - **Secure Execution**: Run code snippets in isolated Docker containers
  - **Multi-Language Support**: Python, JavaScript, Java, Go, Ruby, Rust
  - **Trust Badges**: Visual validation indicators for executed code
  - **Access Control**: Role-based execution via membership system
  - **Resource Limits**: Memory, CPU, and timeout protection
  - **Network Isolation**: Disabled network access for security
  - **Execution Cache**: Fast repeat executions with result caching
  - **GUI Integration**: Interactive "Live Example" tab in documentation preview
  - **Configurable Settings**: Customize timeout, limits, and security options
  - See [LIVE_TESTBED.md](LIVE_TESTBED.md) for detailed documentation

- **🆕 Regulatory Compliance Mapping & Gap Analysis**: Track documentation coverage against regulatory requirements
  - **Compliance Frameworks**: SOC2, HIPAA, GDPR, ISO 27001, PCI DSS support
  - **Documentation Mapping**: Map documentation sections to specific regulatory requirements
  - **Gap Analysis**: Automatically identify missing or incomplete compliance documentation
  - **Coverage Tracking**: Monitor covered, partial, and not-covered requirements
  - **Severity Levels**: Critical, high, medium, and low gap classification
  - **Actionable Reports**: Generate compliance reports with specific recommendations
  - **Multi-Format Export**: Text, markdown, HTML, and JSON report formats
  - **Dashboard Integration**: View compliance status across multiple repositories
  - **Permission Management**: Role-based access control via membership system
  - **Database Persistence**: Store all mappings and gap analysis results
  - See [COMPLIANCE_MAPPING.md](COMPLIANCE_MAPPING.md) for detailed documentation

- **🆕 Organization-wide Glossary & Style Standardization**: Maintain terminology consistency
  - **Glossary Management**: Define preferred terms, aliases, and deprecated terms
  - **Style Rules**: Custom style rules with regex patterns
  - **Violation Detection**: Automatically scan documentation for inconsistencies
  - **Severity Levels**: Categorize violations as error, warning, or info
  - **Organization Isolation**: Support multiple organizations with separate glossaries
  - **Detailed Reporting**: Generate reports with line numbers and context
  - **CLI & REST API**: Full command-line and programmatic access
  - See [ORGANIZATION_FEATURES.md](ORGANIZATION_FEATURES.md) for detailed documentation

- **🆕 Onboarding and Training Path Generator**: Automated onboarding for new contributors
  - **Repository Analysis**: Automatically generate onboarding steps from repo structure
  - **Language-Aware**: Customize setup based on detected languages and frameworks
  - **Progress Tracking**: Track user progress through interactive checklists
  - **Multiple Formats**: Export as markdown, checklist, or JSON
  - **Time Estimates**: Provide estimated completion time for each step
  - **Assignment System**: Assign checklists to users with membership integration
  - **CLI & REST API**: Generate and manage onboarding guides
  - See [ORGANIZATION_FEATURES.md](ORGANIZATION_FEATURES.md) for detailed documentation

- **🆕 Granular Document Sharing Controls**: Secure selective documentation sharing
  - **Section-Level Sharing**: Share specific sections, not entire documents
  - **Expiring Access**: Set automatic expiration dates for shared content
  - **Watermarking**: Add watermarks to track shared documents
  - **Download Limits**: Restrict number of downloads per share
  - **Access Tracking**: Complete audit trail with IP logging
  - **Secure Tokens**: Cryptographically secure access tokens
  - **Revocation**: Instantly revoke access to shared documents
  - **CLI & REST API**: Manage shares via command-line or API
  - See [ORGANIZATION_FEATURES.md](ORGANIZATION_FEATURES.md) for detailed documentation

- **🆕 Microservice Doc API Endpoints**: Documentation as a service
  - **RESTful API**: Expose all features via clean JSON API
  - **Role-Based Access**: Integration with membership system for authorization
  - **Rate Limiting**: 60 requests per minute per client (configurable)
  - **API Authentication**: Token-based authentication for secure access
  - **Usage Auditing**: Complete audit trail of all API usage
  - **CORS Support**: Ready for web application integration
  - **OpenAPI Documentation**: Built-in API specification
  - See [ORGANIZATION_FEATURES.md](ORGANIZATION_FEATURES.md) for detailed documentation

- **🆕 License and Copyright Management Toolkit**: Bulk license and copyright management
  - **Copyright Headers**: Generate and apply copyright headers for multiple licenses
  - **Bulk Application**: Apply headers to entire repositories automatically
  - **Header Scanning**: Detect existing headers and track coverage
  - **Attribution Management**: Track third-party component attributions
  - **Attribution File Generation**: Auto-generate THIRD_PARTY_LICENSES files
  - **Compliance Checking**: Check license compliance across repositories
  - **Multiple Licenses**: Support for MIT, Apache-2.0, GPL, BSD, and more
  - **CLI & REST API**: Manage licenses via command-line or API
  - See [ORGANIZATION_FEATURES.md](ORGANIZATION_FEATURES.md) for detailed documentation

## 🆕 Latest Features (New in 2024)

AccuDoc now includes powerful new features for developers and teams:

### 🤝 Collaborative Documentation Workspace
- **Multi-User Editing**: Multiple users can edit documentation simultaneously
- **CRDT-Based Conflict Resolution**: Automatic conflict-free merging of concurrent edits
- **Real-Time Collaboration**: See changes from other users in real-time
- **Comments & Suggestions**: Discuss changes and propose improvements
- **Role-Based Access Control**: Owner, Admin, Editor, and Viewer roles
- **Team Management**: Organize users into teams for easier access control
- **Audit Trail**: Complete logging of all collaborative activities
- **REST API**: Full API support for collaborative features
- **GUI Integration**: Simple collaborative editor interface
- See [COLLABORATIVE_WORKSPACE.md](COLLABORATIVE_WORKSPACE.md) for detailed documentation

### 📦 Python Library Support
- **Install via pip**: `pip install .`
- **Use as a library**: Import and use AccuDoc programmatically in your Python code
- **Console scripts**: `accudoc` command available after installation
- **Optional dependencies**: Install only what you need (gui, api, pdf, scheduler)
- See `examples/library_usage.py` for comprehensive examples

### 📚 Documentation Versioning
- **Version History**: Track all changes to generated documentation
- **Diff Viewer**: Compare versions to see what changed
- **Tagging**: Tag important versions (v1.0, release, etc.)
- **Rollback**: Revert to any previous version
- **Export**: Save history as JSON, CSV, or Markdown

### ⏰ Scheduled Scans
- **Automatic Updates**: Scan repositories on a schedule (hourly, daily, weekly, monthly)
- **Background Processing**: Runs in background thread
- **Custom Callbacks**: Register custom handlers for scan completion
- **Persistent Config**: Schedules survive restarts

### 📧 Email Reports
- **Send Documentation**: Email generated docs to stakeholders
- **Multiple Providers**: Gmail, Outlook, Yahoo, Office365 presets
- **Rich Formatting**: HTML emails with attachments
- **Summary Reports**: Include scan statistics and metrics

### 🎨 Template Gallery
- **Browse Templates**: View all available documentation templates
- **Search & Filter**: Find templates by category, tags, or keywords
- **Preview**: See what each template includes
- **Built-in Templates**: 6 professional templates ready to use

### 🎓 Interactive Tutorials
- **Learn AccuDoc**: Step-by-step tutorials for new users
- **Track Progress**: Save completion status across sessions
- **3 Tutorials**: Getting Started (10min), Advanced Features (20min), CLI Mastery (15min)
- **Context-Aware**: Examples and tips relevant to your workflow

### ⌨️ Keyboard Shortcuts
- **Quick Actions**: Common operations with keyboard shortcuts
- **Customizable**: Change shortcuts to your preference
- **Comprehensive**: 15+ default shortcuts for all actions
- **GUI Integration**: Seamlessly integrated with Tkinter interface

### 🔍 Documentation Search
- **Search Docs**: Find information in AccuDoc's documentation
- **Context Results**: See surrounding context for each match
- **Topic Help**: Get help on specific topics
- **Relevance Scoring**: Most relevant results first

### ⚡ Async Operations
- **Non-Blocking**: Async scanning prevents UI freezing
- **Event System**: Subscribe to scan events
- **Batch Processing**: Scan multiple repos concurrently
- **Timeout Support**: Handle long-running scans gracefully

### 🏗️ Technical Improvements
- **Type Hints**: Full type coverage for better IDE support
- **Dataclasses**: Modern data modeling with dataclasses
- **Modular Design**: Independent, reusable modules
- **Event-Driven**: Extensible event system

For detailed documentation on new features, see [NEW_FEATURES_IMPLEMENTATION.md](NEW_FEATURES_IMPLEMENTATION.md)

## Installation

### Prerequisites

- Python 3.7 or higher
- Git (for cloning remote repositories)
- Tkinter (usually comes with Python)
- For Electron GUI: Node.js 18+ and npm

### Installation Methods

#### Method 1: Install as Python Package (Recommended)

```bash
# Clone repository
git clone https://github.com/jamesellette/AccuDoc.git
cd AccuDoc

# Install AccuDoc
pip install .

# Or install with all optional features
pip install .[all]

# Install specific feature sets
pip install .[gui]        # GUI support
pip install .[api]        # REST API support
pip install .[pdf]        # PDF export
pip install .[scheduler]  # Scheduled scans
```

After installation, you can use AccuDoc from anywhere:
```bash
accudoc scan /path/to/repo -o docs.md
```

Or use it as a Python library:
```python
from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator

scanner = RepositoryScanner('/path/to/repo')
repo_info = scanner.scan()

generator = DocumentGenerator(repo_info)
generator.generate_and_export('README.md')
```

#### Method 2: Run from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/jamesellette/AccuDoc.git
   cd AccuDoc
   ```

2. No additional dependencies are required! AccuDoc uses only Python standard library.

3. Run directly:
   ```bash
   python accudoc_cli.py scan /path/to/repo
   ```

### Electron GUI Installation

For the modern cross-platform desktop application:

```bash
# Navigate to the Electron GUI directory
cd electron-gui

# Install dependencies
npm install

# Run the application
npm start

# Build executables (optional)
npm run build          # All platforms
npm run build:win      # Windows only
npm run build:mac      # macOS only
npm run build:linux    # Linux only
```

See `electron-gui/README.md` for detailed instructions and `electron-gui/QUICKSTART.md` for quick setup.

## Usage

### Command-Line Interface (CLI)

AccuDoc now includes a powerful CLI for automation and CI/CD integration:

```bash
# Quick export (scan + generate in one command)
python accudoc_cli.py export https://github.com/user/repo -o docs.md

# Generate documentation in Spanish
python accudoc_cli.py export /path/to/repo -o docs_es.md --language es

# Generate documentation in French with HTML output
python accudoc_cli.py export /path/to/repo -o docs_fr.html --format html --language fr

# Scan a repository and save results
python accudoc_cli.py scan /path/to/repo -o scan.json

# Generate documentation from scan results in German
python accudoc_cli.py generate scan.json -o docs.html --format html --theme dark --language de

# Process multiple repositories in batch
python accudoc_cli.py batch batch-config.json

# Archive documentation with cryptographic signature
python accudoc_cli.py archive create /path/to/repo document.md \
    --tags "v1.0,release,public" \
    --description "Release 1.0 documentation"

# List and filter archives
python accudoc_cli.py archive list --repository /path/to/repo
python accudoc_cli.py archive list --format markdown --tags "release"

# Retrieve and validate archived documentation
python accudoc_cli.py archive retrieve arch_abc123 -o output.md
python accudoc_cli.py archive validate arch_abc123

# View archive statistics
python accudoc_cli.py archive stats --repository /path/to/repo

# View cache statistics
python accudoc_cli.py cache stats /path/to/repo

# Clear cache
python accudoc_cli.py cache clear /path/to/repo

# Check links in documentation
python accudoc_cli.py check-links docs/ --format markdown -o link-report.md

# Generate static documentation website
python accudoc_cli.py site /path/to/repo -o ./docs-site --title "My Project"

# Export to PDF (requires weasyprint or wkhtmltopdf)
python accudoc_cli.py export /path/to/repo -o docs.pdf --format pdf

# Generate open source project files (CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates)
python accudoc_cli.py opensource /path/to/repo -o ./

# Export repository data to CSV
python accudoc_cli.py data-export /path/to/repo -o ./exports -f csv -r all

# Export summary CSV with key metrics
python accudoc_cli.py data-export /path/to/repo -o summary.csv -f summary

# Export to JSON format
python accudoc_cli.py data-export /path/to/repo -o data.json -f json

# Get help and available options
python accudoc_cli.py --help
python accudoc_cli.py info
```

#### Data Export

Export repository analysis data for further processing in spreadsheet applications:

```bash
# Export all CSV reports (files, dependencies, TODOs, metrics, languages)
python accudoc_cli.py data-export /path/to/repo -o ./exports -f csv -r all

# Export specific report type
python accudoc_cli.py data-export /path/to/repo -o ./exports -f csv -r dependencies

# Export summary CSV with key metrics
python accudoc_cli.py data-export /path/to/repo -o summary.csv -f summary

# Export complete data to JSON
python accudoc_cli.py data-export /path/to/repo -o repo-data.json -f json

# Use existing scan results
python accudoc_cli.py data-export scan.json -o ./exports -f csv
```

Available CSV Reports:
- **files**: File statistics by language
- **dependencies**: List of dependencies with versions
- **todos**: TODO/FIXME comments extracted from code
- **metrics**: Code metrics (total lines, code lines, comments, blank lines)
- **languages**: Language breakdown with file counts and percentages
- **all**: Generate all of the above reports

#### Project Health Dashboard

Get comprehensive health metrics and actionable recommendations:

```bash
# Display health dashboard in terminal
python accudoc_cli.py health /path/to/repo

# Save dashboard to text file
python accudoc_cli.py health /path/to/repo -o dashboard.txt

# Export metrics as JSON
python accudoc_cli.py health /path/to/repo -o dashboard.json -f json

# Analyze from existing scan
python accudoc_cli.py health scan.json
```

Health Metrics:
- **Overall Health**: Weighted score (0-100) with letter grade (A-F)
- **Documentation Coverage**: README, API docs, examples, contributing guides (25% weight)
- **Code Quality**: TODO/FIXME items, complexity, best practices, tests (30% weight)
- **Dependency Health**: Dependency count, outdated packages, vulnerabilities (20% weight)
- **Maintainability Index**: Comment ratio, config files, repository size (15% weight)
- **License Compliance**: License detection and compatibility (10% weight)
- **Recommendations**: Prioritized suggestions for improvement

#### Advanced Quality Scoring

Comprehensive documentation quality analysis with industry benchmarking:

```bash
# Run complete quality analysis
python accudoc_cli.py quality-analyze /path/to/repo

# Analyze with specific project type and save metrics
python accudoc_cli.py quality-analyze /path/to/repo -t library --save-metrics --benchmark --suggestions

# Generate HTML quality report
python accudoc_cli.py quality-report /path/to/repo -t web-framework --include-history --include-benchmark -f html -o quality-report.html

# View quality history and trends
python accudoc_cli.py quality-history /path/to/repo --days 90 -f csv -o quality-trends.csv

# Compare against industry benchmarks
python accudoc_cli.py quality-benchmark /path/to/repo -t api-service
```

Project Types for Benchmarking:
- **web-framework**: React, Vue, Angular, etc.
- **library**: Reusable code libraries and packages
- **cli-tool**: Command-line applications and utilities
- **api-service**: REST APIs and web services
- **mobile-app**: iOS, Android, React Native apps
- **desktop-app**: Electron, native desktop applications
- **data-science**: ML/AI projects, Jupyter notebooks
- **other**: General open-source projects

Quality Metrics:
- **Clarity Score (30%)**: Flesch Reading Ease, Gunning Fog Index, sentence complexity
- **Completeness Score (40%)**: Documentation coverage, API documentation, required sections
- **Accuracy Score (30%)**: Broken links, outdated content, factual consistency
- **Documentation Debt**: Accumulated quality issues requiring attention
- **Industry Percentile**: How you rank against similar projects
- **Improvement Suggestions**: AI-powered recommendations for quality enhancement

#### Trend Analysis

Track how your repository has grown over time:

```bash
# Analyze trends over last month
python accudoc_cli.py trends /path/to/repo -p month

# Analyze with custom intervals (20 data points over all history)
python accudoc_cli.py trends /path/to/repo -p all -i 20

# Save trend report to file
python accudoc_cli.py trends /path/to/repo -o trends.txt

# Export trends as JSON
python accudoc_cli.py trends /path/to/repo -o trends.json -f json

# Export trends to CSV
python accudoc_cli.py trends /path/to/repo -o ./trend_data -f csv

# Analyze last quarter with 12 data points
python accudoc_cli.py trends /path/to/repo -p quarter -i 12
```

Time Periods:
- **week**: Last 7 days
- **month**: Last 30 days  
- **quarter**: Last 90 days
- **year**: Last 365 days
- **all**: Entire repository history

Tracked Metrics:
- Commit count growth
- File count evolution
- Contributor activity
- Lines of code added/deleted
- Language distribution changes
- Growth rates across all metrics

#### Comparison Reports

Compare multiple repositories to identify best practices and areas for improvement:

```bash
# Compare two repositories
python accudoc_cli.py compare /path/to/repo1 /path/to/repo2

# Compare using existing scan files
python accudoc_cli.py compare scan1.json scan2.json scan3.json

# Save comparison to file
python accudoc_cli.py compare repo1 repo2 -o comparison.txt

# Export as JSON
python accudoc_cli.py compare repo1 repo2 -o comparison.json -f json

# Export to CSV
python accudoc_cli.py compare repo1 repo2 repo3 -o ./compare_data -f csv

# Use custom names for clarity
python accudoc_cli.py compare repo1 repo2 -n "Project A" "Project B"
```

Comparison Metrics:
- **File Statistics**: Count, language distribution
- **Code Statistics**: Total lines, code lines, comment ratio
- **Dependencies**: Total count, by package manager
- **Documentation**: Doc files, API docs, examples
- **Health Scores**: Overall and category scores (if calculated)
- **TODO/FIXME**: Task tracking comparison
- **Rankings**: Automatic ranking by all metrics
- **Summary**: Best and worst performers identified

#### Multi-Repository Documentation Consistency Dashboard

Analyze documentation quality, style compliance, and completeness across multiple repositories for organization-wide consistency:

```bash
# Generate dashboard for multiple repositories
python accudoc_cli.py dashboard /path/to/repo1 /path/to/repo2 /path/to/repo3

# Use existing scan files
python accudoc_cli.py dashboard scan1.json scan2.json scan3.json

# Save dashboard to file
python accudoc_cli.py dashboard repo1 repo2 -o dashboard.txt

# Export as markdown
python accudoc_cli.py dashboard repo1 repo2 -o dashboard.md -f markdown

# Export as HTML
python accudoc_cli.py dashboard repo1 repo2 -o dashboard.html -f html

# Export as JSON
python accudoc_cli.py dashboard repo1 repo2 -o dashboard.json -f json

# Use custom names for repositories
python accudoc_cli.py dashboard repo1 repo2 -n "Frontend" "Backend"

# Specify style guide to check against
python accudoc_cli.py dashboard repo1 repo2 -s microsoft

# Set custom thresholds
python accudoc_cli.py dashboard repo1 repo2 --min-coverage 80 --min-completeness 70

# Skip consistency analysis
python accudoc_cli.py dashboard repo1 repo2 --no-consistency

# Enable membership authentication
python accudoc_cli.py dashboard repo1 repo2 --require-auth -u user123
```

Dashboard Features:
- **Documentation Coverage**: Track coverage across all repositories with detailed metrics
- **Completeness Scoring**: Rate documentation quality with breakdowns by category
- **Style Compliance**: Check against Google, Microsoft, or Plain Language style guides
- **Consistency Gaps**: Automatically detect inconsistencies with severity levels (critical, high, medium, low)
- **Organization Analytics**: Summary statistics, trends, and rankings
- **Repository Rankings**: Rank by coverage, completeness, compliance, and overall score
- **Actionable Recommendations**: Get specific suggestions to improve documentation quality
- **Multiple Formats**: Text, Markdown, HTML, JSON reports
- **Membership Integration**: Optional role-based access control for team collaboration

#### Compliance Mapping & Gap Analysis

Map documentation to regulatory requirements and track compliance:

```bash
# List available compliance frameworks and requirements
python accudoc_cli.py compliance frameworks
python accudoc_cli.py compliance frameworks -f soc2

# Map documentation to requirement
python accudoc_cli.py compliance map /path/to/repo SOC2-CC1.1 "README.md#Security" \
    -f soc2 \
    -n "Security section covers organizational structure" \
    -p README.md

# List compliance mappings
python accudoc_cli.py compliance list /path/to/repo
python accudoc_cli.py compliance list /path/to/repo -f soc2 --json

# Analyze compliance gaps
python accudoc_cli.py compliance analyze /path/to/repo -f soc2
python accudoc_cli.py compliance analyze /path/to/repo -f hipaa --json

# Generate compliance report
python accudoc_cli.py compliance report /path/to/repo -f soc2
python accudoc_cli.py compliance report /path/to/repo -f gdpr --format markdown -o report.md
python accudoc_cli.py compliance report /path/to/repo -f iso27001 --format html -o report.html
```

Supported Frameworks:
- **SOC2**: SOC2 Type II Trust Service Criteria
- **HIPAA**: HIPAA Security Rule requirements
- **GDPR**: EU General Data Protection Regulation
- **ISO 27001**: Information Security Management System
- **PCI DSS**: Payment Card Industry Data Security Standard

Compliance Features:
- Map documentation sections to specific regulatory requirements
- Track coverage status (covered, partial, not_covered, not_applicable)
- Automated gap analysis with severity levels (critical, high, medium, low)
- Comprehensive compliance reports with actionable recommendations
- Multiple export formats (text, markdown, HTML, JSON)
- Database persistence for all mappings and gaps
- Permission management integration
- Dashboard integration showing compliance across repositories

See [COMPLIANCE_MAPPING.md](COMPLIANCE_MAPPING.md) for detailed documentation.

#### Custom Reports

Generate custom reports using built-in or user-defined templates:

```bash
# List available built-in templates
python accudoc_cli.py custom-report /path/to/repo --list

# Generate with built-in template
python accudoc_cli.py custom-report /path/to/repo -b minimal
python accudoc_cli.py custom-report /path/to/repo -b executive -o summary.md
python accudoc_cli.py custom-report /path/to/repo -b detailed
python accudoc_cli.py custom-report /path/to/repo -b technical

# Create sample template to customize
python accudoc_cli.py custom-report . --create-sample basic -o my_template.json
python accudoc_cli.py custom-report . --create-sample comprehensive -o template.json

# Use custom template
python accudoc_cli.py custom-report /path/to/repo -t my_template.json -o report.md

# Generate from existing scan
python accudoc_cli.py custom-report scan.json -b executive -o exec_summary.md
```

Built-in Templates:
- **minimal**: Essential project information only
- **detailed**: Comprehensive project analysis
- **executive**: High-level summary for stakeholders
- **technical**: In-depth technical deep dive

Template Structure (JSON):
```json
{
  "name": "My Custom Report",
  "description": "A custom report template",
  "format": "markdown",
  "sections": [
    {
      "title": "Overview",
      "content": "Project: {name}\\nFiles: {files_count}"
    },
    {
      "title": "Statistics",
      "data": ["languages", "statistics.total_lines"]
    }
  ]
}
```

Features:
- **Variable substitution**: {name}, {files_count}, {license}
- **Dynamic data fields**: Automatically format repository data
- **Nested access**: Use dot notation (statistics.total_lines)
- **Template validation**: Ensures template is correct before generation

#### REST API

Start a REST API server to access AccuDoc features programmatically:

```bash
# Start API server on default port (5000)
python accudoc_cli.py api

# Start on custom port
python accudoc_cli.py api --port 8080

# Enable debug mode
python accudoc_cli.py api --debug

# Bind to all interfaces
python accudoc_cli.py api --host 0.0.0.0
```

**API Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /api/docs` - API documentation (OpenAPI spec)
- `POST /api/scan` - Scan repository
- `POST /api/generate` - Generate documentation
- `POST /api/export` - Scan and generate documentation
- `POST /api/health-metrics` - Get health metrics
- `POST /api/trends` - Get trend analysis
- `POST /api/compare` - Compare repositories
- `POST /api/custom-report` - Generate custom report
- `POST /api/data-export` - Export repository data

**Example API Calls (curl):**
```bash
# Scan repository
curl -X POST http://localhost:5000/api/scan \
  -H 'Content-Type: application/json' \
  -d '{"path": "/path/to/repo"}'

# Get health metrics
curl -X POST http://localhost:5000/api/health-metrics \
  -H 'Content-Type: application/json' \
  -d '{"path": "/path/to/repo"}'

# Generate custom report
curl -X POST http://localhost:5000/api/custom-report \
  -H 'Content-Type: application/json' \
  -d '{"path": "/path/to/repo", "builtin": "executive"}'
```

**Example API Calls (Python):**
```python
import requests

BASE_URL = 'http://localhost:5000'

# Scan repository
response = requests.post(
    f'{BASE_URL}/api/scan',
    json={'path': '/path/to/repo'}
)
scan_data = response.json()['data']

# Get health metrics
response = requests.post(
    f'{BASE_URL}/api/health-metrics',
    json={'scan_data': scan_data}
)
health = response.json()['data']
print(f"Overall score: {health['summary']['overall_score']}")
```

**Requirements:**
- Flask: `pip install flask flask-cors`
- API server is optional - all features work via CLI without it

#### Hooks System

The hooks system allows you to extend AccuDoc's functionality by registering custom code at specific execution points:

```bash
# List all registered hooks
python accudoc_cli.py hooks --list

# List all hook points (including empty ones)
python accudoc_cli.py hooks --list --all

# Enable a built-in hook
python accudoc_cli.py hooks --enable before_scan log_scan_start

# Disable a hook
python accudoc_cli.py hooks --disable before_scan log_scan_start
```

**Available Hook Points:**
- `BEFORE_SCAN` / `AFTER_SCAN` - Around repository scanning
- `BEFORE_FILE_ANALYSIS` / `AFTER_FILE_ANALYSIS` - Around individual file analysis
- `BEFORE_GENERATE` / `AFTER_GENERATE` - Around documentation generation
- `BEFORE_EXPORT` / `AFTER_EXPORT` - Around documentation export
- `BEFORE_HEALTH_METRICS` / `AFTER_HEALTH_METRICS` - Around health calculation
- `CUSTOM` - Custom hook points

**Programmatic Usage:**
```python
from accudoc.hooks_system import get_hooks_manager, HookPoint

# Get the hooks manager
manager = get_hooks_manager()

# Register a function hook
def my_hook(context):
    print(f"Processing: {context.get('path')}")
    context['custom_data'] = 'value'
    return context

manager.register_function(
    HookPoint.BEFORE_SCAN,
    "my_custom_hook",
    my_hook,
    priority=10
)

# Register a shell command hook
manager.register_shell(
    HookPoint.AFTER_EXPORT,
    "notify_completion",
    "echo 'Documentation generated!' | mail -s 'AccuDoc Complete' user@example.com",
    priority=90
)

# Execute hooks
context = manager.execute(HookPoint.BEFORE_SCAN, {'path': '/repo'})
```

**Hook Features:**
- **Priority-based execution**: Lower numbers run first (0-100 scale)
- **Context propagation**: Data flows between hooks
- **Error resilience**: Hook failures don't stop execution
- **Enable/disable**: Turn hooks on/off without removing them
- **Multiple types**: Python functions or shell commands

#### Open Source Documentation Generation

AccuDoc can automatically generate standard open source project documentation:

```bash
# Generate all files (CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates)
python accudoc_cli.py opensource /path/to/repo -o ./

# Generate only CONTRIBUTING.md
python accudoc_cli.py opensource /path/to/repo --contributing

# Generate only CODE_OF_CONDUCT.md
python accudoc_cli.py opensource /path/to/repo --conduct

# Generate only issue templates
python accudoc_cli.py opensource /path/to/repo --issues
```

Features:
- **CONTRIBUTING.md**: Auto-detects project language, package manager, test framework
- **CODE_OF_CONDUCT.md**: Based on Contributor Covenant 2.0
- **Issue Templates**: Bug report and feature request templates for GitHub/GitLab
- **Language-Specific**: Tailored instructions for Python, JavaScript, Java, Go, etc.

#### CLI Features

- **Multiple Commands**: `scan`, `generate`, `export`, `site`, `info`, `cache`, `check-links`, `plugins`, `batch`, **`opensource`**
- **Smart Caching**: Automatic file-level caching for faster subsequent scans
- **Parallel Processing**: Multi-threaded scanning for improved performance
- **Link Checking**: Validate links in generated documentation
- **Static Site Generation**: Create complete documentation websites with search
- **ReadTheDocs/Sphinx Integration**: Generate Sphinx projects for ReadTheDocs publishing
- **Batch Processing**: Process multiple repositories from a JSON configuration
- **Flexible Output**: Support for Markdown, HTML, TXT, PDF, Static Sites, RST, AsciiDoc, LaTeX
- **Automation Ready**: JSON output and quiet mode for CI/CD pipelines
- **Verbose Logging**: Multiple verbosity levels for debugging

### Static Site Generation

Generate a complete documentation website with navigation and search:

```bash
python accudoc_cli.py site /path/to/repo -o ./site --title "My Project Docs"
```

Features of the generated site:
- Multi-page layout (Home, API, Architecture, Contributing)
- Navigation bar
- Client-side search functionality
- Responsive design
- Theme support (default, dark)
- Statistics dashboard

### Using the GUI

Run the graphical interface:
```bash
python main.py
```

1. **Enter Repository**: Type a Git repository URL or click "Browse Local..." to select a local folder
   - **🆕 Drag & Drop**: You can also drag and drop a repository folder directly into the application window!
2. **Scan**: Click "Scan Repository" to analyze the repository
3. **View Documentation**: The generated documentation will appear in the text area
   - **🆕 Live Preview**: Switch to the "Preview" tab for a side-by-side view of markdown source and rendered HTML!
4. **Save**: Click "Save Documentation" to export the documentation to a file

**Multi-Window Support**: Open multiple AccuDoc windows to work with different repositories simultaneously:
- Use `File > New Window` or press `Ctrl+N` to open a new window
- Each window operates independently with its own state
- Perfect for comparing documentation across projects or multi-repo workflows

**Internationalization**: AccuDoc supports multiple languages with automatic locale detection:
- Supported languages: English, Spanish (Español), French (Français), German (Deutsch), Chinese (中文), Japanese (日本語), Arabic (العربية)
- Automatically detects your system language on first launch
- Change language in Settings (⚙️ Settings button or Settings menu)
- Full UI translation including menus, buttons, labels, and messages
- RTL (right-to-left) language detection for Arabic and Hebrew
- Language preference persists across sessions

To change the language:
1. Click the ⚙️ Settings button
2. Go to the "General" tab
3. Select your preferred language from the dropdown
4. Click "Apply" and restart the application

**Note**: Drag & drop functionality requires the `tkinterdnd2` package for full cross-platform support:
```bash
pip install tkinterdnd2
```

**Note**: For enhanced HTML preview in the Preview tab, install one of these optional packages:
```bash
pip install tkinterweb  # Recommended for best HTML rendering
# OR
pip install tkhtmlview  # Alternative HTML viewer
# OR
pip install markdown    # For better markdown to HTML conversion
```
If not installed, the application will work normally with text-based preview.

### Docker Usage

AccuDoc can be run in a Docker container for easy deployment:

```bash
# Build the image
docker build -t accudoc .

# Run with docker-compose
docker-compose up

# Or run directly
docker run -v ./repos:/repos -v ./output:/output accudoc export /repos/my-repo -o /output/docs.md
```

### Example Repository URLs

- `https://github.com/username/repo-name`
- `git@github.com:username/repo-name.git`
- Local path: `/path/to/local/repository`

## How It Works

1. **Repository Access**: AccuDoc clones remote repositories or accesses local folders
2. **Scanning**: Analyzes the repository structure, files, and configuration
3. **Detection**: Identifies languages, dependencies, build tools, and documentation
4. **Generation**: Creates comprehensive documentation based on findings
5. **Export**: Allows saving the documentation in multiple formats

## Project Structure

```
AccuDoc/
├── accudoc/
│   ├── __init__.py           # Package initialization
│   ├── gui.py                # GUI implementation
│   ├── scanner.py            # Repository scanning logic
│   ├── generator.py          # Documentation generation
│   ├── exporters.py          # Export to multiple formats
│   ├── templates.py          # Template system
│   └── markdown_flavors.py   # Markdown flavor support
├── main.py                   # Application entry point
├── test_accudoc.py          # Test suite
├── test_new_features.py     # Tests for new features
├── demo_new_features.py     # Demo of new features
├── requirements.txt          # Dependencies (none needed!)
├── README.md                # This file
└── LICENSE                  # License information
```

## Advanced Usage

### Using Templates

AccuDoc provides 6 built-in templates for different documentation needs:

```python
from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator

scanner = RepositoryScanner('path/to/repo')
repo_info = scanner.scan()

# Generate minimal README
generator = DocumentGenerator(repo_info, template='minimal')
generator.generate_and_export('README.md')

# Generate comprehensive API docs
generator = DocumentGenerator(repo_info, template='api')
generator.generate_and_export('api-docs.html', format='html', theme='corporate')

# Generate student project documentation
generator = DocumentGenerator(repo_info, template='student')
generator.generate_and_export('PROJECT.md')
```

**Available Templates:**
- `default` - Complete documentation with all sections
- `minimal` - Essential sections only (overview, installation, usage)
- `detailed` - Comprehensive technical documentation
- `api` - API reference focused documentation
- `readme` - GitHub README style
- **🆕 `student`** - Academic/student project template with learning objectives, requirements, deliverables

### Student Project Template

Perfect for academic projects, the student template includes:

```python
from accudoc.generator import DocumentGenerator
from accudoc.scanner import RepositoryScanner

scanner = RepositoryScanner('path/to/student/project')
repo_info = scanner.scan()

generator = DocumentGenerator(repo_info, template='student')
doc = generator.generate_and_export('PROJECT_REPORT.md')
```

**Sections included:**
- Student information (name, ID, course, instructor)
- Learning objectives (auto-detected from project)
- Assignment requirements checklist
- Testing and validation
- Deliverables checklist
- Resources and references
- Acknowledgments

The template automatically detects your project's language and framework to provide relevant setup instructions and testing guidance.

### Markdown Flavors

Export documentation optimized for different platforms:

```python
# GitHub Flavored Markdown (default)
generator.generate_and_export('README.md', markdown_flavor='github')

# GitLab Flavored Markdown with TOC
generator.generate_and_export('README.md', markdown_flavor='gitlab')

# Standard CommonMark
generator.generate_and_export('README.md', markdown_flavor='commonmark')
```

### HTML Themes

Generate beautiful HTML documentation with professional themes:

```python
# Light theme (default)
generator.generate_and_export('docs.html', format='html', theme='default')

# Dark theme
generator.generate_and_export('docs.html', format='html', theme='dark')

# Minimal theme
generator.generate_and_export('docs.html', format='html', theme='minimal')

# Corporate theme
generator.generate_and_export('docs.html', format='html', theme='corporate')
```

### Custom Templates

Create your own custom templates:

```python
from accudoc.templates import TemplateManager

manager = TemplateManager()

# Define custom sections
sections = [
    ('header', '_generate_header', 0),
    ('overview', '_generate_overview', 10),
    ('installation', '_generate_installation', 20),
]

# Create custom template
manager.create_custom_template(
    'quickstart',
    'Quick Start Guide',
    'Fast getting started documentation',
    sections
)

# Use custom template
generator = DocumentGenerator(repo_info, template='quickstart')
generator.generate_and_export('QUICKSTART.md')
```

For more details, see [COMPLETE_DOCUMENTATION_FEATURES.md](COMPLETE_DOCUMENTATION_FEATURES.md).

### Code Analysis Features

AccuDoc now includes powerful code analysis tools to help improve code quality:

#### Complexity Analysis

Identify complex code that needs better documentation or refactoring:

```python
from accudoc.complexity_analyzer import ComplexityAnalyzer

analyzer = ComplexityAnalyzer('/path/to/repo')
results = analyzer.analyze_repository(['.py', '.js'])
report = analyzer.generate_report(results)
print(report)
```

Features:
- Calculates cyclomatic complexity for functions
- Identifies high complexity functions (>10)
- Flags undocumented complex functions
- Supports Python and JavaScript/TypeScript

Run the demo: `python3 demo_complexity.py`

#### Best Practices Checker

Ensure code quality and adherence to coding standards:

```python
from accudoc.best_practices import BestPracticesChecker

checker = BestPracticesChecker('/path/to/repo')
results = checker.check_repository(['.py'])
report = checker.generate_report(results)
print(report)
```

Checks for:
- Missing docstrings (module, class, function)
- Too many function parameters (>5)
- Long functions (>50 lines)
- Mutable default arguments (high severity)
- Bare except clauses (high severity)
- Broad exception catching
- Magic numbers
- Classes with too many methods (>20)

Run the demo: `python3 demo_best_practices.py`

#### Call Graph Generation

Visualize function relationships and dependencies:

```python
from accudoc.call_graph import CallGraphGenerator

generator = CallGraphGenerator('/path/to/repo')
call_graph = generator.analyze_repository(['.py'])
report = generator.generate_report(call_graph)
print(report)
```

Features:
- Analyzes function call relationships
- Generates Mermaid diagrams for visualization
- Identifies most called functions
- Finds functions with most dependencies
- Supports caller/callee lookup

Run the demo: `python3 demo_call_graph.py`

#### Documentation Completeness Score

Measure and improve documentation quality:

```python
from accudoc.completeness_score import CompletenessScorer

scorer = CompletenessScorer('/path/to/repo')
results = scorer.analyze_repository()
print(f"Score: {results['overall_score']}/100 (Grade: {results['grade']})")
report = scorer.generate_report(results)
print(report)
```

Features:
- Comprehensive scoring across 9 categories
- Letter grades (A-F) for quick assessment
- Gap identification with severity levels
- Actionable recommendations
- Visual score bars and detailed reports

Run the demo: `python3 demo_completeness_score.py`

For complete details, see [CODE_ANALYSIS_FEATURES.md](CODE_ANALYSIS_FEATURES.md).

### Smart Caching

AccuDoc includes intelligent file-level caching to dramatically improve performance on large repositories:

```python
from accudoc.scanner import RepositoryScanner
from accudoc.cache import CacheManager

# Caching is enabled by default
scanner = RepositoryScanner('/path/to/repo')
repo_info = scanner.scan()  # Creates cache on first run

# Subsequent scans are much faster
repo_info = scanner.scan()  # Uses cache for unchanged files

# Disable caching if needed
scanner.disable_cache()
repo_info = scanner.scan()

# Manage cache programmatically
cache = CacheManager('/path/to/repo')
cache.initialize()
stats = cache.get_stats()
print(f"Cached files: {stats['cached_files']}")
cache.clear()  # Clear cache
```

Cache benefits:
- **Faster scans**: Only re-analyze changed files
- **File-level granularity**: Each file tracked independently
- **Automatic invalidation**: Changes detected via file hash
- **Minimal overhead**: Lightweight JSON-based storage

## Supported Technologies

AccuDoc can detect and document projects using:

- **Languages**: Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Ruby, PHP, Rust, and more
- **Package Managers**: pip, npm, yarn, Maven, Gradle, Cargo, Composer, Bundler, Go modules
- **Build Tools**: Make, CMake, Gradle, Maven, npm scripts, and more
- **CI/CD**: GitHub Actions, Travis CI, GitLab CI, Jenkins

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## About

AccuDoc was created to simplify the process of creating and maintaining project documentation. By automatically analyzing repositories and generating documentation, it saves time and ensures consistency.

---

*Made with ❤️ for the developer community*