"""
Example: Using AccuDoc as a Python Library

This example demonstrates how to use AccuDoc programmatically in your Python code.
"""

# Basic Usage
# ===========

from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator

# Scan a repository
scanner = RepositoryScanner('/path/to/repository')
repo_info = scanner.scan()

# Generate documentation
generator = DocumentGenerator(repo_info, template='default')
doc_path = generator.generate_and_export('README.md')

print(f"Documentation generated at: {doc_path}")


# Advanced Usage with Options
# ============================

from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator

# Scan with progress callback
def progress_callback(message):
    print(f"Progress: {message}")

scanner = RepositoryScanner('/path/to/repo', progress_callback=progress_callback)
repo_info = scanner.scan()

# Generate with custom options
generator = DocumentGenerator(repo_info, template='api')
doc_path = generator.generate_and_export(
    'docs.html',
    format='html',
    theme='dark',
    markdown_flavor='github',
    language='en'
)


# Using Templates Gallery
# ========================

from accudoc.template_gallery import TemplateGallery

gallery = TemplateGallery()

# List all templates
templates = gallery.list_all()
for template in templates:
    print(f"{template.name}: {template.description}")

# Search for templates
api_templates = gallery.search(tags=['api'])

# Get template details
template_info = gallery.get_template('detailed')
print(gallery.format_template_detail('detailed'))


# Documentation Versioning
# =========================

from accudoc.doc_versioning import DocumentationVersionControl, VersionStatus

# Initialize version control
vc = DocumentationVersionControl('/path/to/repo')

# Save a version
version = vc.save_version(
    content=doc_content,
    file_path='README.md',
    message='Initial documentation',
    tags=['v1.0', 'release']
)

# List versions
versions = vc.list_versions()
for v in versions:
    print(f"{v.version_id}: {v.message}")

# Compare versions
diff = vc.diff_versions('v1_20240101_120000', 'v2_20240115_120000')
print(vc.format_diff_report(diff))

# Rollback to previous version
vc.rollback('v1_20240101_120000', 'README.md')


# Scheduled Scans
# ===============

from accudoc.scheduler import ScanScheduler, ScheduleType

# Create scheduler
scheduler = ScanScheduler()

# Add a daily scan
scan_id = scheduler.add_schedule(
    repo_path='/path/to/repo',
    schedule_type=ScheduleType.DAILY,
    output_path='docs.md'
)

# Register custom callback
def scan_callback(repo_path, options):
    print(f"Scanning {repo_path}")
    scanner = RepositoryScanner(repo_path)
    repo_info = scanner.scan()
    generator = DocumentGenerator(repo_info)
    generator.generate_and_export('auto_docs.md')

scheduler.register_callback(scan_id, scan_callback)

# Start scheduler
scheduler.start()

# ... scheduler runs in background ...

# Stop scheduler when done
scheduler.stop()


# Email Reporting
# ===============

from accudoc.email_reporter import EmailReporter, create_email_config

# Create email configuration
config = create_email_config(
    provider='gmail',
    username='your.email@gmail.com',
    password='your_app_password'
)

# Create reporter
reporter = EmailReporter(config)

# Send documentation report
success = reporter.send_documentation_report(
    to_emails=['recipient@example.com'],
    repo_name='MyProject',
    doc_file='README.md',
    scan_summary={
        'total_files': 150,
        'languages': ['Python', 'JavaScript'],
        'dependencies': 25
    }
)


# Async Operations
# ================

import asyncio
from accudoc.async_scanner import AsyncScanner

async def scan_async():
    async with AsyncScanner() as scanner:
        # Async scan
        repo_info = await scanner.scan_repository('/path/to/repo')
        
        # Async generate
        doc_path = await scanner.generate_documentation(
            repo_info,
            'docs.md'
        )
        
        return doc_path

# Run async
doc_path = asyncio.run(scan_async())


# Interactive Tutorial
# ====================

from accudoc.interactive_tutorial import TutorialSystem

tutorial_system = TutorialSystem()

# List tutorials
tutorials = tutorial_system.list_tutorials()
for tutorial in tutorials:
    print(f"{tutorial.title}: {tutorial.description}")

# Start a tutorial
tutorial_system.start_tutorial('getting_started')

# Get current step
step = tutorial_system.get_current_step('getting_started')
print(tutorial_system.format_tutorial_step('getting_started'))

# Complete step
tutorial_system.complete_step('getting_started', 0)


# Documentation Search
# ====================

from accudoc.doc_search import DocumentationSearch

search = DocumentationSearch()

# Search documentation
results = search.search('installation', context_lines=3)

# Format and display results
print(search.format_results(results))

# Search within a section
results = search.search_section('Usage', 'CLI')

# Get help on a topic
help_text = search.get_topic_help('Installation')
print(help_text)


# Keyboard Shortcuts (for GUI)
# =============================

from accudoc.keyboard_shortcuts import ShortcutManager, ShortcutAction

shortcut_manager = ShortcutManager()

# Register callbacks
def scan_action():
    print("Scanning repository...")

shortcut_manager.register_callback(ShortcutAction.SCAN_REPO, scan_action)

# Get shortcuts help
print(shortcut_manager.get_shortcuts_help())

# In Tkinter GUI:
# shortcut_manager.bind_all_to_widget(root_window)


# Custom Analyzers (Plugin System)
# =================================

from accudoc.plugins import AnalyzerPlugin, PluginManager
from pathlib import Path

class CustomMarkdownAnalyzer(AnalyzerPlugin):
    @property
    def name(self):
        return "Custom Markdown Analyzer"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "Analyzes custom markdown features"
    
    def analyze(self, file_path: Path, content: str):
        # Custom analysis logic
        return {
            'headers': content.count('#'),
            'links': content.count('['),
            'code_blocks': content.count('```')
        }
    
    def supports_file(self, file_path: Path):
        return file_path.suffix == '.md'

# Register plugin
plugin_manager = PluginManager()
plugin_manager.register_analyzer(CustomMarkdownAnalyzer())


# Complete Example: Library Integration
# ======================================

from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator
from accudoc.doc_versioning import DocumentationVersionControl
from accudoc.email_reporter import EmailReporter, create_email_config

def generate_and_distribute(repo_path, recipients):
    """
    Complete workflow: scan, generate, version, and email.
    """
    # 1. Scan repository
    print("Scanning repository...")
    scanner = RepositoryScanner(repo_path)
    repo_info = scanner.scan()
    
    # 2. Generate documentation
    print("Generating documentation...")
    generator = DocumentGenerator(repo_info, template='detailed')
    doc_path = generator.generate_and_export('docs.md')
    
    # 3. Save version
    print("Saving version...")
    vc = DocumentationVersionControl(repo_path)
    with open(doc_path, 'r') as f:
        content = f.read()
    version = vc.save_version(
        content=content,
        file_path=doc_path,
        message='Automated documentation update',
        tags=['automated']
    )
    
    # 4. Email report
    print("Sending email...")
    config = create_email_config(
        provider='gmail',
        username='your.email@gmail.com',
        password='your_app_password'
    )
    reporter = EmailReporter(config)
    reporter.send_documentation_report(
        to_emails=recipients,
        repo_name=repo_info.get('name', 'Unknown'),
        doc_file=doc_path,
        scan_summary={
            'total_files': repo_info.get('total_files', 0),
            'languages': list(repo_info.get('languages', {}).keys())
        }
    )
    
    print(f"Complete! Version: {version.version_id}")

# Use it
generate_and_distribute(
    repo_path='/path/to/my-project',
    recipients=['team@example.com']
)
