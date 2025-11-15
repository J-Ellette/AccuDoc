#!/usr/bin/env python3
"""Test live preview functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile


class TestLivePreview(unittest.TestCase):
    """Test live preview functionality."""
    
    def test_basic_markdown_to_html(self):
        """Test basic markdown to HTML conversion."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        # Create GUI instance with mocked root
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            
            temp_dir = tempfile.mkdtemp()
            mock_home.return_value = Path(temp_dir)
            gui = AccuDocGUI(mock_root)
            
            # Test basic markdown conversion
            markdown = "# Header\n\nThis is **bold** and *italic*.\n\n```python\nprint('hello')\n```"
            html = gui._basic_markdown_to_html(markdown)
            
            # Check that basic conversions happened
            self.assertIn('<h1>Header</h1>', html)
            self.assertIn('<strong>bold</strong>', html)
            self.assertIn('<em>italic</em>', html)
            self.assertIn('<code>print(&#x27;hello&#x27;)</code>', html.replace('<pre>', '').replace('</pre>', '') or '<code>' in html)
    
    def test_simplify_markdown(self):
        """Test markdown simplification for text preview."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        # Create GUI instance with mocked root
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            
            temp_dir = tempfile.mkdtemp()
            mock_home.return_value = Path(temp_dir)
            gui = AccuDocGUI(mock_root)
            
            # Test markdown simplification
            markdown = "# Header\n\nThis is **bold** text.\n\n- Item 1\n- Item 2"
            simplified = gui._simplify_markdown(markdown)
            
            # Check that markdown syntax is removed
            self.assertNotIn('#', simplified)
            self.assertNotIn('**', simplified)
            self.assertIn('Header', simplified)
            self.assertIn('bold', simplified)
            self.assertIn('•', simplified)  # List marker converted
    
    def test_markdown_to_html_with_library(self):
        """Test markdown to HTML with markdown library if available."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        # Create GUI instance with mocked root
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            
            temp_dir = tempfile.mkdtemp()
            mock_home.return_value = Path(temp_dir)
            gui = AccuDocGUI(mock_root)
            
            # Test full markdown to HTML
            markdown = "# Test\n\nParagraph text."
            html = gui._markdown_to_html(markdown)
            
            # Should contain HTML structure
            self.assertIn('<!DOCTYPE html>', html)
            self.assertIn('<body>', html)
            self.assertIn('<style>', html)
            self.assertIn('Test', html)
    
    def test_update_preview_method_exists(self):
        """Test that update preview method exists."""
        from accudoc.gui import AccuDocGUI
        
        # Check that the method is defined
        self.assertTrue(hasattr(AccuDocGUI, '_update_preview'))
        self.assertTrue(hasattr(AccuDocGUI, '_markdown_to_html'))
        self.assertTrue(hasattr(AccuDocGUI, '_basic_markdown_to_html'))
        self.assertTrue(hasattr(AccuDocGUI, '_simplify_markdown'))
    
    def test_create_preview_tab_method_exists(self):
        """Test that create preview tab method exists."""
        from accudoc.gui import AccuDocGUI
        
        # Check that the method is defined
        self.assertTrue(hasattr(AccuDocGUI, '_create_preview_tab'))
    
    def test_basic_html_conversion_headers(self):
        """Test that headers are converted correctly."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            
            temp_dir = tempfile.mkdtemp()
            mock_home.return_value = Path(temp_dir)
            gui = AccuDocGUI(mock_root)
            
            # Test different header levels
            markdown = "# H1\n## H2\n### H3"
            html = gui._basic_markdown_to_html(markdown)
            
            self.assertIn('<h1>H1</h1>', html)
            self.assertIn('<h2>H2</h2>', html)
            self.assertIn('<h3>H3</h3>', html)
    
    def test_basic_html_conversion_code(self):
        """Test that code blocks are converted correctly."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            
            temp_dir = tempfile.mkdtemp()
            mock_home.return_value = Path(temp_dir)
            gui = AccuDocGUI(mock_root)
            
            # Test inline code
            markdown = "This is `inline code` here."
            html = gui._basic_markdown_to_html(markdown)
            self.assertIn('<code>inline code</code>', html)
            
            # Test code block
            markdown = "```\ncode block\n```"
            html = gui._basic_markdown_to_html(markdown)
            self.assertIn('<pre>', html)
            self.assertIn('<code>', html)
    
    def test_basic_html_conversion_lists(self):
        """Test that lists are converted correctly."""
        from accudoc.gui import AccuDocGUI
        
        # Create mock root
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        
        with patch('accudoc.gui.tk.StringVar'), \
             patch('accudoc.gui.Path.home') as mock_home:
            
            temp_dir = tempfile.mkdtemp()
            mock_home.return_value = Path(temp_dir)
            gui = AccuDocGUI(mock_root)
            
            # Test unordered list
            markdown = "- Item 1\n- Item 2\n- Item 3"
            html = gui._basic_markdown_to_html(markdown)
            
            self.assertIn('<ul>', html)
            self.assertIn('<li>Item 1</li>', html)
            self.assertIn('<li>Item 2</li>', html)
            self.assertIn('</ul>', html)


if __name__ == '__main__':
    unittest.main()
