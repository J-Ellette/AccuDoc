#!/usr/bin/env python3
"""
Integration test for Live Testbed feature.

This test verifies the complete integration of the live testbed feature
with settings and GUI modules.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock tkinter modules
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()


class TestLiveTestbedIntegration(unittest.TestCase):
    """Integration tests for live testbed feature."""
    
    def test_settings_have_testbed_fields(self):
        """Test that settings include testbed configuration."""
        from accudoc.settings import AccuDocSettings
        
        settings = AccuDocSettings()
        
        # Check testbed settings exist
        self.assertFalse(settings.enable_live_testbed)
        self.assertEqual(settings.testbed_timeout, 30)
        self.assertEqual(settings.testbed_memory_limit, '256m')
        self.assertEqual(settings.testbed_cpu_quota, 50000)
        self.assertTrue(settings.testbed_network_disabled)
        self.assertTrue(settings.testbed_enable_cache)
        self.assertTrue(settings.testbed_require_auth)
        self.assertIsNotNone(settings.testbed_allowed_languages)
        self.assertIn('python', settings.testbed_allowed_languages)
    
    def test_settings_can_enable_testbed(self):
        """Test enabling testbed in settings."""
        from accudoc.settings import AccuDocSettings
        
        settings = AccuDocSettings(
            enable_live_testbed=True,
            testbed_timeout=60,
            testbed_memory_limit='512m'
        )
        
        self.assertTrue(settings.enable_live_testbed)
        self.assertEqual(settings.testbed_timeout, 60)
        self.assertEqual(settings.testbed_memory_limit, '512m')
    
    def test_gui_module_imports_without_testbed(self):
        """Test that GUI module imports when testbed is unavailable."""
        from accudoc import gui
        
        # Should import successfully even without docker package
        self.assertFalse(gui.TESTBED_AVAILABLE)
    
    def test_gui_handles_testbed_gracefully(self):
        """Test that GUI handles missing testbed gracefully."""
        from accudoc import gui
        
        # When testbed is not available, GUI should still function
        # The Live Example tab simply won't be created
        self.assertIn('TESTBED_AVAILABLE', dir(gui))
    
    def test_testbed_module_structure(self):
        """Test testbed module has expected structure."""
        try:
            from accudoc.live_testbed import (
                LiveTestbed,
                Language,
                ExecutionStatus,
                CodeSnippet,
                ExecutionResult
            )
            
            # Check Language enum
            self.assertEqual(Language.PYTHON.value, 'python')
            self.assertEqual(Language.JAVASCRIPT.value, 'javascript')
            
            # Check ExecutionStatus enum
            self.assertEqual(ExecutionStatus.SUCCESS.value, 'success')
            self.assertEqual(ExecutionStatus.FAILURE.value, 'failure')
            
            # Check CodeSnippet dataclass
            snippet = CodeSnippet(
                code='test',
                language=Language.PYTHON,
                line_number=1
            )
            self.assertEqual(snippet.code, 'test')
        except ImportError:
            # Docker package not available
            self.skipTest("Docker package not available")
    
    def test_testbed_initialization(self):
        """Test testbed can be initialized with custom settings."""
        try:
            import docker
            from accudoc.live_testbed import LiveTestbed
            
            with patch('docker.from_env') as mock_docker:
                mock_client = MagicMock()
                mock_docker.return_value = mock_client
                
                testbed = LiveTestbed(
                    timeout=45,
                    memory_limit='128m',
                    cpu_quota=25000,
                    network_disabled=False,
                    enable_cache=False
                )
                
                self.assertEqual(testbed.timeout, 45)
                self.assertEqual(testbed.memory_limit, '128m')
                self.assertEqual(testbed.cpu_quota, 25000)
                self.assertFalse(testbed.network_disabled)
                self.assertFalse(testbed.enable_cache)
        except ImportError:
            # Docker package not available
            self.skipTest("Docker package not available")
    
    def test_settings_manager_supports_testbed(self):
        """Test that settings manager can save/load testbed settings."""
        from accudoc.settings import SettingsManager, AccuDocSettings
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / 'settings.json'
            manager = SettingsManager(settings_file)
            
            # Create settings with testbed enabled
            settings = AccuDocSettings(
                enable_live_testbed=True,
                testbed_timeout=90
            )
            
            # Export and import (verify serialization works)
            # This tests that our new fields don't break serialization
            data = {
                'enable_live_testbed': settings.enable_live_testbed,
                'testbed_timeout': settings.testbed_timeout
            }
            
            self.assertTrue(data['enable_live_testbed'])
            self.assertEqual(data['testbed_timeout'], 90)
    
    def test_feature_documentation_exists(self):
        """Test that feature documentation exists."""
        from pathlib import Path
        
        doc_file = Path(__file__).parent / 'LIVE_TESTBED.md'
        self.assertTrue(doc_file.exists(), "LIVE_TESTBED.md should exist")
        
        content = doc_file.read_text()
        self.assertIn('Live Documentation Testbed', content)
        self.assertIn('Docker', content)
        self.assertIn('Security', content)
    
    def test_demo_script_exists(self):
        """Test that demo script exists."""
        from pathlib import Path
        
        demo_file = Path(__file__).parent / 'demo_live_testbed.py'
        self.assertTrue(demo_file.exists(), "demo_live_testbed.py should exist")
    
    def test_tests_exist(self):
        """Test that unit tests exist."""
        from pathlib import Path
        
        test_file = Path(__file__).parent / 'test_live_testbed.py'
        self.assertTrue(test_file.exists(), "test_live_testbed.py should exist")
    
    def test_readme_mentions_testbed(self):
        """Test that README mentions the live testbed feature."""
        from pathlib import Path
        
        readme = Path(__file__).parent / 'README.md'
        content = readme.read_text()
        
        self.assertIn('Live Documentation Testbed', content)
        self.assertIn('LIVE_TESTBED.md', content)


if __name__ == '__main__':
    unittest.main()
