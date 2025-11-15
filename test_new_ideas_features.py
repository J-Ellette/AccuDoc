"""
Tests for new features from ideas.md implementation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json


class TestDocumentationVersioning(unittest.TestCase):
    """Test documentation versioning features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / "test_repo"
        self.repo_path.mkdir()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_save_version(self):
        """Test saving documentation version."""
        from accudoc.doc_versioning import DocumentationVersionControl
        
        vc = DocumentationVersionControl(str(self.repo_path))
        
        # Save a version
        version = vc.save_version(
            content="# Test Documentation\n\nThis is a test.",
            file_path="README.md",
            message="Initial version"
        )
        
        self.assertIsNotNone(version)
        self.assertEqual(version.message, "Initial version")
        self.assertEqual(len(vc.versions), 1)
    
    def test_version_diff(self):
        """Test version diffing."""
        from accudoc.doc_versioning import DocumentationVersionControl
        
        vc = DocumentationVersionControl(str(self.repo_path))
        
        # Save two versions
        v1 = vc.save_version(
            content="# Version 1\n\nFirst version.",
            file_path="README.md",
            message="Version 1"
        )
        
        v2 = vc.save_version(
            content="# Version 2\n\nSecond version.",
            file_path="README.md",
            message="Version 2"
        )
        
        # Get diff
        diff = vc.diff_versions(v1.version_id, v2.version_id)
        
        self.assertIsNotNone(diff)
        self.assertEqual(diff.old_version, v1.version_id)
        self.assertEqual(diff.new_version, v2.version_id)
        self.assertGreater(len(diff.changes), 0)
    
    def test_rollback(self):
        """Test rollback to previous version."""
        from accudoc.doc_versioning import DocumentationVersionControl
        
        vc = DocumentationVersionControl(str(self.repo_path))
        
        # Save versions
        v1 = vc.save_version(
            content="Original content",
            file_path="README.md",
            message="Original"
        )
        
        v2 = vc.save_version(
            content="Modified content",
            file_path="README.md",
            message="Modified"
        )
        
        # Rollback
        output_path = str(self.repo_path / "rollback.md")
        success = vc.rollback(v1.version_id, output_path)
        
        self.assertTrue(success)
        self.assertTrue(Path(output_path).exists())
        
        # Verify content
        with open(output_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Original content")


class TestScheduler(unittest.TestCase):
    """Test scheduled scan features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_add_schedule(self):
        """Test adding a scheduled scan."""
        from accudoc.scheduler import ScanScheduler, ScheduleType
        
        scheduler = ScanScheduler(self.test_dir)
        
        scan_id = scheduler.add_schedule(
            repo_path="/test/repo",
            schedule_type=ScheduleType.DAILY
        )
        
        self.assertIsNotNone(scan_id)
        self.assertEqual(len(scheduler.schedules), 1)
    
    def test_list_schedules(self):
        """Test listing schedules."""
        from accudoc.scheduler import ScanScheduler, ScheduleType
        
        scheduler = ScanScheduler(self.test_dir)
        
        scheduler.add_schedule("/repo1", ScheduleType.DAILY)
        scheduler.add_schedule("/repo2", ScheduleType.WEEKLY)
        
        schedules = scheduler.list_schedules()
        self.assertEqual(len(schedules), 2)
    
    def test_enable_disable_schedule(self):
        """Test enabling/disabling schedules."""
        from accudoc.scheduler import ScanScheduler, ScheduleType
        
        scheduler = ScanScheduler(self.test_dir)
        
        scan_id = scheduler.add_schedule("/repo", ScheduleType.DAILY)
        
        # Disable
        scheduler.disable_schedule(scan_id)
        schedule = scheduler.schedules[scan_id]
        self.assertFalse(schedule.enabled)
        
        # Enable
        scheduler.enable_schedule(scan_id)
        schedule = scheduler.schedules[scan_id]
        self.assertTrue(schedule.enabled)


class TestEmailReporter(unittest.TestCase):
    """Test email reporting features."""
    
    def test_email_config_creation(self):
        """Test email configuration creation."""
        from accudoc.email_reporter import create_email_config
        
        config = create_email_config(
            provider='gmail',
            username='test@gmail.com',
            password='password'
        )
        
        self.assertEqual(config.smtp_host, 'smtp.gmail.com')
        self.assertEqual(config.smtp_port, 587)
        self.assertTrue(config.use_tls)
    
    def test_email_config_save_load(self):
        """Test saving and loading email config."""
        from accudoc.email_reporter import EmailConfig
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name
        
        try:
            # Create and save
            config = EmailConfig(
                smtp_host='smtp.test.com',
                smtp_port=587,
                username='test@test.com',
                password='pass',
                use_tls=True
            )
            config.save_to_file(config_file)
            
            # Load
            loaded = EmailConfig.load_from_file(config_file)
            
            self.assertEqual(loaded.smtp_host, 'smtp.test.com')
            self.assertEqual(loaded.username, 'test@test.com')
        finally:
            Path(config_file).unlink()


class TestTemplateGallery(unittest.TestCase):
    """Test template gallery features."""
    
    def test_list_templates(self):
        """Test listing templates."""
        from accudoc.template_gallery import TemplateGallery
        
        gallery = TemplateGallery()
        templates = gallery.list_all()
        
        self.assertGreater(len(templates), 0)
        self.assertIn('default', [t.id for t in templates])
    
    def test_search_templates(self):
        """Test searching templates."""
        from accudoc.template_gallery import TemplateGallery
        
        gallery = TemplateGallery()
        
        # Search by tag
        results = gallery.search(tags=['api'])
        self.assertGreater(len(results), 0)
        
        # Search by query
        results = gallery.search(query='minimal')
        self.assertGreater(len(results), 0)
    
    def test_get_template(self):
        """Test getting specific template."""
        from accudoc.template_gallery import TemplateGallery
        
        gallery = TemplateGallery()
        template = gallery.get_template('default')
        
        self.assertIsNotNone(template)
        self.assertEqual(template.id, 'default')


class TestInteractiveTutorial(unittest.TestCase):
    """Test interactive tutorial features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_list_tutorials(self):
        """Test listing tutorials."""
        from accudoc.interactive_tutorial import TutorialSystem
        
        system = TutorialSystem(self.test_dir)
        tutorials = system.list_tutorials()
        
        self.assertGreater(len(tutorials), 0)
    
    def test_start_tutorial(self):
        """Test starting a tutorial."""
        from accudoc.interactive_tutorial import TutorialSystem, TutorialStatus
        
        system = TutorialSystem(self.test_dir)
        success = system.start_tutorial('getting_started')
        
        self.assertTrue(success)
        
        tutorial = system.get_tutorial('getting_started')
        self.assertEqual(tutorial.status, TutorialStatus.IN_PROGRESS.value)
    
    def test_complete_step(self):
        """Test completing tutorial steps."""
        from accudoc.interactive_tutorial import TutorialSystem
        
        system = TutorialSystem(self.test_dir)
        system.start_tutorial('getting_started')
        
        # Complete first step
        success = system.complete_step('getting_started', 0)
        self.assertTrue(success)
        
        tutorial = system.get_tutorial('getting_started')
        self.assertTrue(tutorial.steps[0].completed)


class TestKeyboardShortcuts(unittest.TestCase):
    """Test keyboard shortcuts features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_get_shortcut(self):
        """Test getting shortcuts."""
        from accudoc.keyboard_shortcuts import ShortcutManager, ShortcutAction
        
        manager = ShortcutManager(self.test_dir)
        shortcut = manager.get_shortcut(ShortcutAction.SCAN_REPO)
        
        self.assertIsNotNone(shortcut)
        self.assertEqual(shortcut.key, "<Control-r>")
    
    def test_set_shortcut(self):
        """Test setting custom shortcuts."""
        from accudoc.keyboard_shortcuts import ShortcutManager, ShortcutAction
        
        manager = ShortcutManager(self.test_dir)
        manager.set_shortcut(ShortcutAction.SCAN_REPO, "<Control-Shift-r>")
        
        shortcut = manager.get_shortcut(ShortcutAction.SCAN_REPO)
        self.assertEqual(shortcut.key, "<Control-Shift-r>")


class TestDocumentationSearch(unittest.TestCase):
    """Test documentation search features."""
    
    def test_search_documentation(self):
        """Test searching documentation."""
        from accudoc.doc_search import DocumentationSearch
        
        # Create a test documentation directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test markdown file
            test_md = Path(temp_dir) / "README.md"
            test_md.write_text("# Installation\n\nRun pip install accudoc\n")
            
            search = DocumentationSearch(temp_dir)
            results = search.search("installation")
            
            # Should find at least one result
            self.assertGreater(len(results), 0)
    
    def test_list_topics(self):
        """Test listing documentation topics."""
        from accudoc.doc_search import DocumentationSearch
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_md = Path(temp_dir) / "README.md"
            test_md.write_text("# Installation\n\n# Usage\n\n# Configuration\n")
            
            search = DocumentationSearch(temp_dir)
            topics = search.list_topics()
            
            self.assertIn("Installation", topics)
            self.assertIn("Usage", topics)


class TestAsyncScanner(unittest.TestCase):
    """Test async scanning features."""
    
    def test_async_scanner_creation(self):
        """Test creating async scanner."""
        from accudoc.async_scanner import AsyncScanner
        
        scanner = AsyncScanner(max_workers=2)
        self.assertEqual(scanner.max_workers, 2)
        scanner.shutdown()
    
    def test_async_event_manager(self):
        """Test async event manager."""
        from accudoc.async_scanner import AsyncEventManager
        
        manager = AsyncEventManager()
        
        # Subscribe to event
        called = []
        def callback():
            called.append(True)
        
        manager.subscribe('test_event', callback)
        
        # Event should have listener
        self.assertIn('test_event', manager.listeners)
        self.assertEqual(len(manager.listeners['test_event']), 1)


if __name__ == '__main__':
    unittest.main()
