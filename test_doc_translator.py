"""
Test suite for documentation translation feature.
"""

import unittest
from accudoc.doc_translator import DocumentTranslator


class TestDocumentTranslator(unittest.TestCase):
    """Test cases for DocumentTranslator."""
    
    def test_initialization(self):
        """Test translator initialization."""
        translator = DocumentTranslator('es')
        self.assertEqual(translator.target_language, 'es')
        
        translator_en = DocumentTranslator('en')
        self.assertEqual(translator_en.target_language, 'en')
    
    def test_supported_languages(self):
        """Test supported languages list."""
        languages = DocumentTranslator.get_supported_languages()
        self.assertIn('en', languages)
        self.assertIn('es', languages)
        self.assertIn('fr', languages)
        self.assertIn('de', languages)
        self.assertIn('zh', languages)
        self.assertIn('ja', languages)
        self.assertIn('ar', languages)
        self.assertEqual(len(languages), 7)
    
    def test_is_supported(self):
        """Test language support checking."""
        self.assertTrue(DocumentTranslator.is_supported('en'))
        self.assertTrue(DocumentTranslator.is_supported('es'))
        self.assertTrue(DocumentTranslator.is_supported('fr'))
        self.assertFalse(DocumentTranslator.is_supported('xx'))
        self.assertFalse(DocumentTranslator.is_supported('invalid'))
    
    def test_translate_english_no_change(self):
        """Test that English content is not modified."""
        content = "## Overview\n\nThis is a test.\n\n## Features\n\n- Feature 1"
        translator = DocumentTranslator('en')
        result = translator.translate(content)
        self.assertEqual(content, result)
    
    def test_translate_headers_spanish(self):
        """Test Spanish header translation."""
        content = "## Overview\n\nContent here\n\n## Features\n\n- Item 1"
        translator = DocumentTranslator('es')
        result = translator.translate(content)
        
        self.assertIn('Descripción General', result)
        self.assertIn('Características', result)
        self.assertNotIn('## Overview', result)
        self.assertNotIn('## Features', result)
    
    def test_translate_headers_french(self):
        """Test French header translation."""
        content = "## Overview\n\n## Installation\n\n## Usage"
        translator = DocumentTranslator('fr')
        result = translator.translate(content)
        
        self.assertIn('Aperçu', result)
        self.assertIn('Installation', result)
        self.assertIn('Utilisation', result)
    
    def test_translate_headers_german(self):
        """Test German header translation."""
        content = "## Overview\n\n## Features\n\n## License"
        translator = DocumentTranslator('de')
        result = translator.translate(content)
        
        self.assertIn('Übersicht', result)
        self.assertIn('Funktionen', result)
        self.assertIn('Lizenz', result)
    
    def test_translate_headers_chinese(self):
        """Test Chinese header translation."""
        content = "## Overview\n\n## Features\n\n## Installation"
        translator = DocumentTranslator('zh')
        result = translator.translate(content)
        
        self.assertIn('概述', result)
        self.assertIn('功能', result)
        self.assertIn('安装', result)
    
    def test_translate_headers_japanese(self):
        """Test Japanese header translation."""
        content = "## Overview\n\n## Features\n\n## Installation"
        translator = DocumentTranslator('ja')
        result = translator.translate(content)
        
        self.assertIn('概要', result)
        self.assertIn('機能', result)
        self.assertIn('インストール', result)
    
    def test_translate_headers_arabic(self):
        """Test Arabic header translation."""
        content = "## Overview\n\n## Features\n\n## Installation"
        translator = DocumentTranslator('ar')
        result = translator.translate(content)
        
        self.assertIn('نظرة عامة', result)
        self.assertIn('الميزات', result)
        self.assertIn('التثبيت', result)
    
    def test_translate_common_terms(self):
        """Test translation of common terms."""
        content = "**Required**: Python 3.7\n**Optional**: Docker\n**Version**: 1.0.0"
        translator = DocumentTranslator('es')
        result = translator.translate(content)
        
        self.assertIn('Requerido', result)
        self.assertIn('Opcional', result)
        self.assertIn('Versión', result)
    
    def test_translate_with_note(self):
        """Test translation with note added."""
        content = "## Overview\n\nThis is content."
        translator = DocumentTranslator('es')
        result = translator.translate_with_note(content)
        
        # Should contain translation note
        self.assertIn('Nota de Traducción', result)
        self.assertIn('traducida automáticamente', result)
        
        # Should contain translated content
        self.assertIn('Descripción General', result)
    
    def test_translate_with_note_english(self):
        """Test that English doesn't get a translation note."""
        content = "## Overview\n\nThis is content."
        translator = DocumentTranslator('en')
        result = translator.translate_with_note(content)
        
        # Should not have translation note for English
        self.assertNotIn('Translation Note', result)
        self.assertEqual(content, result)
    
    def test_translate_preserves_code_blocks(self):
        """Test that code blocks are preserved during translation."""
        content = """## Installation

```bash
pip install package
```

## Usage

Run the command."""
        
        translator = DocumentTranslator('es')
        result = translator.translate(content)
        
        # Code blocks should be preserved
        self.assertIn('```bash', result)
        self.assertIn('pip install package', result)
        self.assertIn('```', result)
        
        # Headers should be translated
        self.assertIn('Instalación', result)
        self.assertIn('Uso', result)
    
    def test_translate_multiple_header_levels(self):
        """Test translation of different header levels."""
        content = """# Main Title
## Overview
### Getting Started
#### Prerequisites
##### Step 1
###### Details"""
        
        translator = DocumentTranslator('fr')
        result = translator.translate(content)
        
        self.assertIn('Aperçu', result)
        self.assertIn('Démarrage', result)
        self.assertIn('Prérequis', result)
    
    def test_case_insensitive_header_translation(self):
        """Test that header translation works regardless of case."""
        content = "## OVERVIEW\n\n## overview\n\n## Overview"
        translator = DocumentTranslator('es')
        result = translator.translate(content)
        
        # All variations should be translated
        self.assertIn('Descripción General', result)
        # Original headers should not be present
        self.assertNotIn('OVERVIEW', result)


def run_tests():
    """Run all tests and print results."""
    print("=" * 60)
    print("Testing Documentation Translation Feature")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDocumentTranslator)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
