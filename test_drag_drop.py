#!/usr/bin/env python3
"""Test drag and drop functionality."""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestDragDrop(unittest.TestCase):
    """Test drag and drop functionality."""
    
    def setUp(self):
        """Setup test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_repo_path = os.path.join(self.test_dir, "test_repo")
        os.makedirs(self.test_repo_path)
        
        # Create some test files
        with open(os.path.join(self.test_repo_path, "README.md"), "w") as f:
            f.write("# Test Repository\n")
    
    def tearDown(self):
        """Cleanup test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_drag_drop_methods_exist(self):
        """Test that drag and drop methods exist in GUI."""
        from accudoc.gui import AccuDocGUI
        
        # Check that the methods are defined
        self.assertTrue(hasattr(AccuDocGUI, '_setup_drag_and_drop'))
        self.assertTrue(hasattr(AccuDocGUI, '_on_drop'))
        self.assertTrue(hasattr(AccuDocGUI, '_on_drag_enter'))
        self.assertTrue(hasattr(AccuDocGUI, '_on_drag_leave'))
        self.assertTrue(hasattr(AccuDocGUI, '_reset_drag_feedback'))
    
    @patch('tkinter.Tk')
    @patch('accudoc.gui.RepositoryScanner')
    def test_on_drop_valid_path(self, mock_scanner, mock_tk):
        """Test dropping a valid path."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        # Create GUI instance with mocked root
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            mock_home.return_value = Path(self.test_dir)
            gui = AccuDocGUI(mock_root)
            gui.repo_url = Mock()
            gui.repo_url.set = Mock()
            gui._log = Mock()
            gui._update_status = Mock()
            gui._reset_drag_feedback = Mock()
            
            # Create mock event with valid path
            event = Mock()
            event.data = self.test_repo_path
            
            # Call _on_drop
            result = gui._on_drop(event)
            
            # Verify the path was set
            gui.repo_url.set.assert_called_once()
            call_args = gui.repo_url.set.call_args[0][0]
            self.assertEqual(os.path.abspath(self.test_repo_path), call_args)
            
            # Verify logging
            gui._log.assert_called()
            
            # Verify status update
            gui._update_status.assert_called()
            
            # Verify feedback reset
            gui._reset_drag_feedback.assert_called()
            
            # Verify return value
            self.assertEqual(result, 'copy')
    
    @patch('tkinter.Tk')
    @patch('accudoc.gui.messagebox')
    def test_on_drop_invalid_path(self, mock_messagebox, mock_tk):
        """Test dropping an invalid path."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        # Create GUI instance with mocked root
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            mock_home.return_value = Path(self.test_dir)
            gui = AccuDocGUI(mock_root)
            gui.repo_url = Mock()
            gui._log = Mock()
            gui._reset_drag_feedback = Mock()
            
            # Create mock event with invalid path
            event = Mock()
            event.data = "/nonexistent/path/to/repo"
            
            # Call _on_drop
            result = gui._on_drop(event)
            
            # Verify warning was shown
            mock_messagebox.showwarning.assert_called_once()
            
            # Verify feedback reset
            gui._reset_drag_feedback.assert_called()
            
            # Verify return value
            self.assertEqual(result, 'none')
    
    @patch('tkinter.Tk')
    def test_on_drop_with_curly_braces(self, mock_tk):
        """Test dropping a path with curly braces (Windows format)."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        # Create GUI instance with mocked root
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            mock_home.return_value = Path(self.test_dir)
            gui = AccuDocGUI(mock_root)
            gui.repo_url = Mock()
            gui.repo_url.set = Mock()
            gui._log = Mock()
            gui._update_status = Mock()
            gui._reset_drag_feedback = Mock()
            
            # Create mock event with path in curly braces
            event = Mock()
            event.data = f"{{{self.test_repo_path}}}"
            
            # Call _on_drop
            result = gui._on_drop(event)
            
            # Verify the path was cleaned and set
            gui.repo_url.set.assert_called_once()
            call_args = gui.repo_url.set.call_args[0][0]
            self.assertEqual(os.path.abspath(self.test_repo_path), call_args)
            
            # Verify return value
            self.assertEqual(result, 'copy')
    
    @patch('tkinter.Tk')
    def test_on_drop_with_multiple_paths(self, mock_tk):
        """Test dropping multiple paths (takes first one)."""
        from accudoc.gui import AccuDocGUI
        
        # Create second test repo
        test_repo_path2 = os.path.join(self.test_dir, "test_repo2")
        os.makedirs(test_repo_path2)
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        # Create GUI instance with mocked root
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            mock_home.return_value = Path(self.test_dir)
            gui = AccuDocGUI(mock_root)
            gui.repo_url = Mock()
            gui.repo_url.set = Mock()
            gui._log = Mock()
            gui._update_status = Mock()
            gui._reset_drag_feedback = Mock()
            
            # Create mock event with multiple paths
            event = Mock()
            event.data = f"{self.test_repo_path}\n{test_repo_path2}"
            
            # Call _on_drop
            result = gui._on_drop(event)
            
            # Verify only the first path was set
            gui.repo_url.set.assert_called_once()
            call_args = gui.repo_url.set.call_args[0][0]
            self.assertEqual(os.path.abspath(self.test_repo_path), call_args)
            
            # Verify return value
            self.assertEqual(result, 'copy')
    
    @patch('tkinter.Tk')
    def test_setup_drag_and_drop_without_tkinterdnd(self, mock_tk):
        """Test that setup gracefully handles missing tkinterdnd2."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root (not TkinterDnD)
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        # Create GUI instance with mocked root
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home, \
             patch('builtins.__import__', side_effect=ImportError):
            mock_home.return_value = Path(self.test_dir)
            gui = AccuDocGUI(mock_root)
            gui._log = Mock()
            
            # Call setup - should not raise error
            gui._setup_drag_and_drop()
            
            # Verify it logged the info about missing library
            gui._log.assert_called()


if __name__ == '__main__':
    unittest.main()
