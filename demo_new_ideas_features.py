"""
Demo of new features from ideas.md implementation.

This script demonstrates all the newly implemented features.
"""

import asyncio
from pathlib import Path


def demo_template_gallery():
    """Demonstrate template gallery feature."""
    print("=" * 70)
    print("DEMO: Template Gallery")
    print("=" * 70)
    
    from accudoc.template_gallery import TemplateGallery
    
    gallery = TemplateGallery()
    
    # List all templates
    print("\n📚 Available Templates:")
    print(gallery.format_template_list())
    
    # Search for API templates
    print("\n🔍 Searching for API templates...")
    api_templates = gallery.search(tags=['api'])
    for template in api_templates:
        print(f"  - {template.name}: {template.description}")
    
    # Get detailed info
    print("\n📋 Detailed Template Info:")
    print(gallery.format_template_detail('detailed'))
    
    print("\n✅ Template Gallery Demo Complete!\n")


def demo_documentation_versioning():
    """Demonstrate documentation versioning."""
    print("=" * 70)
    print("DEMO: Documentation Versioning")
    print("=" * 70)
    
    from accudoc.doc_versioning import DocumentationVersionControl, VersionStatus
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        vc = DocumentationVersionControl(temp_dir)
        
        # Save first version
        print("\n📝 Saving version 1...")
        v1 = vc.save_version(
            content="# My Project\n\nVersion 1 documentation.",
            file_path="README.md",
            message="Initial documentation",
            tags=['v1.0']
        )
        print(f"  Version created: {v1.version_id}")
        
        # Save second version
        print("\n📝 Saving version 2...")
        v2 = vc.save_version(
            content="# My Project\n\nVersion 2 documentation with improvements.",
            file_path="README.md",
            message="Updated documentation",
            tags=['v2.0']
        )
        print(f"  Version created: {v2.version_id}")
        
        # Show diff
        print("\n📊 Comparing versions...")
        diff = vc.diff_versions(v1.version_id, v2.version_id)
        print(vc.format_diff_report(diff))
        
        # List versions
        print("\n📜 Version History:")
        for version in vc.get_history():
            print(f"  {version.version_id}: {version.message} (tags: {', '.join(version.tags)})")
        
        print("\n✅ Documentation Versioning Demo Complete!\n")


def demo_scheduler():
    """Demonstrate scheduled scans."""
    print("=" * 70)
    print("DEMO: Scheduled Scans")
    print("=" * 70)
    
    from accudoc.scheduler import ScanScheduler, ScheduleType
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        scheduler = ScanScheduler(temp_dir)
        
        # Add schedules
        print("\n⏰ Adding scheduled scans...")
        
        daily_id = scheduler.add_schedule(
            repo_path="/path/to/repo1",
            schedule_type=ScheduleType.DAILY,
            output_path="daily_docs.md"
        )
        print(f"  Daily scan scheduled: {daily_id}")
        
        weekly_id = scheduler.add_schedule(
            repo_path="/path/to/repo2",
            schedule_type=ScheduleType.WEEKLY,
            output_path="weekly_docs.md"
        )
        print(f"  Weekly scan scheduled: {weekly_id}")
        
        # List schedules
        print("\n📋 Active Schedules:")
        schedules = scheduler.list_schedules()
        for schedule in schedules:
            print(f"  - {schedule.id}")
            print(f"    Repository: {schedule.repo_path}")
            print(f"    Schedule: {schedule.schedule_type}")
            print(f"    Next run: {schedule.next_run}")
            print(f"    Enabled: {schedule.enabled}")
        
        # Get status
        print("\n📊 Scheduler Status:")
        status = scheduler.get_status()
        print(f"  Running: {status['running']}")
        print(f"  Total schedules: {status['total_schedules']}")
        print(f"  Enabled schedules: {status['enabled_schedules']}")
        
        print("\n✅ Scheduled Scans Demo Complete!\n")


def demo_email_reporter():
    """Demonstrate email reporting."""
    print("=" * 70)
    print("DEMO: Email Reporting")
    print("=" * 70)
    
    from accudoc.email_reporter import create_email_config, EmailReporter
    
    # Note: This is a demo - won't actually send email without valid credentials
    print("\n📧 Creating email configuration...")
    
    try:
        config = create_email_config(
            provider='gmail',
            username='demo@example.com',
            password='demo_password'
        )
        
        print(f"  SMTP Host: {config.smtp_host}")
        print(f"  SMTP Port: {config.smtp_port}")
        print(f"  Use TLS: {config.use_tls}")
        
        reporter = EmailReporter(config)
        
        print("\n📨 Email reporter ready!")
        print("  To send reports, use:")
        print("    reporter.send_documentation_report(...)")
        
    except Exception as e:
        print(f"  Demo only - not sending actual emails: {e}")
    
    print("\n✅ Email Reporting Demo Complete!\n")


def demo_interactive_tutorial():
    """Demonstrate interactive tutorials."""
    print("=" * 70)
    print("DEMO: Interactive Tutorials")
    print("=" * 70)
    
    from accudoc.interactive_tutorial import TutorialSystem
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        system = TutorialSystem(temp_dir)
        
        # List tutorials
        print("\n📚 Available Tutorials:")
        print(system.format_tutorial_list())
        
        # Start a tutorial
        print("\n🎓 Starting 'Getting Started' tutorial...")
        system.start_tutorial('getting_started')
        
        # Show current step
        print("\n📖 Current Step:")
        print(system.format_tutorial_step('getting_started'))
        
        # Complete a step
        print("\n✓ Completing step 1...")
        system.complete_step('getting_started', 0)
        
        tutorial = system.get_tutorial('getting_started')
        print(f"  Progress: {tutorial.get_progress():.0f}%")
        
        print("\n✅ Interactive Tutorial Demo Complete!\n")


def demo_keyboard_shortcuts():
    """Demonstrate keyboard shortcuts."""
    print("=" * 70)
    print("DEMO: Keyboard Shortcuts")
    print("=" * 70)
    
    from accudoc.keyboard_shortcuts import ShortcutManager, ShortcutAction
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = ShortcutManager(temp_dir)
        
        # Show all shortcuts
        print("\n⌨️  Keyboard Shortcuts:")
        print(manager.get_shortcuts_help())
        
        # Register a callback
        def scan_callback():
            print("Scanning repository...")
        
        manager.register_callback(ShortcutAction.SCAN_REPO, scan_callback)
        print("\n✓ Callback registered for Ctrl+R (Scan Repository)")
        
        print("\n✅ Keyboard Shortcuts Demo Complete!\n")


def demo_documentation_search():
    """Demonstrate documentation search."""
    print("=" * 70)
    print("DEMO: Documentation Search")
    print("=" * 70)
    
    from accudoc.doc_search import DocumentationSearch
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample documentation
        readme = Path(temp_dir) / "README.md"
        readme.write_text("""
# AccuDoc

## Installation

Install using pip:
```
pip install accudoc
```

## Usage

Run AccuDoc:
```
python accudoc_cli.py scan /path/to/repo
```

## Features

- Automatic documentation generation
- Multiple output formats
- Template support
""")
        
        search = DocumentationSearch(temp_dir)
        
        # Search for a term
        print("\n🔍 Searching for 'installation'...")
        results = search.search("installation", context_lines=2)
        print(search.format_results(results[:3]))  # Show top 3
        
        # List topics
        print("\n📋 Documentation Topics:")
        topics = search.list_topics()
        for topic in topics:
            print(f"  - {topic}")
        
        # Get help on a topic
        print("\n💡 Help on 'Installation':")
        help_text = search.get_topic_help("Installation")
        if help_text:
            print(help_text[:200] + "...")  # Show preview
        
        print("\n✅ Documentation Search Demo Complete!\n")


async def demo_async_operations():
    """Demonstrate async operations."""
    print("=" * 70)
    print("DEMO: Async Operations")
    print("=" * 70)
    
    from accudoc.async_scanner import AsyncScanner, AsyncEventManager
    
    # Event manager
    print("\n⚡ Event-Driven Architecture:")
    manager = AsyncEventManager()
    
    async def on_scan_start():
        print("  Event: Scan started")
    
    async def on_scan_complete():
        print("  Event: Scan completed")
    
    manager.subscribe('scan_start', on_scan_start)
    manager.subscribe('scan_complete', on_scan_complete)
    
    print("  Subscribers registered for scan events")
    
    # Emit events
    await manager.emit('scan_start')
    await asyncio.sleep(0.1)  # Simulate work
    await manager.emit('scan_complete')
    
    print("\n✅ Async Operations Demo Complete!\n")


def demo_library_usage():
    """Demonstrate using AccuDoc as a library."""
    print("=" * 70)
    print("DEMO: Python Library Usage")
    print("=" * 70)
    
    print("\n📚 AccuDoc can be used as a Python library!")
    print("\nExample code:")
    print("""
from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator

# Scan repository
scanner = RepositoryScanner('/path/to/repo')
repo_info = scanner.scan()

# Generate documentation
generator = DocumentGenerator(repo_info, template='default')
doc_path = generator.generate_and_export('README.md')
""")
    
    print("\n📖 See examples/library_usage.py for complete examples")
    print("\n✅ Library Usage Demo Complete!\n")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("AccuDoc New Features Demo")
    print("Showcasing features from ideas.md implementation")
    print("=" * 70 + "\n")
    
    # Run demos
    demo_template_gallery()
    demo_documentation_versioning()
    demo_scheduler()
    demo_email_reporter()
    demo_interactive_tutorial()
    demo_keyboard_shortcuts()
    demo_documentation_search()
    asyncio.run(demo_async_operations())
    demo_library_usage()
    
    print("=" * 70)
    print("All Demos Complete!")
    print("=" * 70)
    print("\nNew Features Implemented:")
    print("  ✅ Python Library Support")
    print("  ✅ Custom Analyzers (via Plugin System)")
    print("  ✅ Templates Gallery")
    print("  ✅ Keyboard Shortcuts")
    print("  ✅ Scheduled Scans")
    print("  ✅ Email Reports")
    print("  ✅ Interactive Tutorial")
    print("  ✅ Documentation Search")
    print("  ✅ Modular Design")
    print("  ✅ Async Operations")
    print("  ✅ Event System")
    print("  ✅ Type Hints & Dataclasses")
    print("  ✅ Documentation Versioning")
    print("\nFor installation instructions, see setup.py")
    print("For library usage examples, see examples/library_usage.py")
    print()


if __name__ == '__main__':
    main()
