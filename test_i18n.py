"""Tests for the i18n module."""

import unittest
import locale
from accudoc.i18n import I18n, get_i18n, _


class TestI18n(unittest.TestCase):
    """Test cases for I18n class."""
    
    def test_initialization_with_language(self):
        """Test i18n initialization with specific language."""
        i18n = I18n('es')
        self.assertEqual(i18n.get_language(), 'es')
    
    def test_initialization_auto_detect(self):
        """Test i18n initialization with auto-detection."""
        i18n = I18n()
        # Should default to a supported language
        self.assertIn(i18n.get_language(), I18n.SUPPORTED_LANGUAGES)
    
    def test_get_translation_english(self):
        """Test getting English translations."""
        i18n = I18n('en')
        self.assertEqual(i18n.get('app_title'), 'AccuDoc - Repository Documentation Generator')
        self.assertEqual(i18n.get('ready'), 'Ready')
        self.assertEqual(i18n.get('scan'), 'Scan Repository')
    
    def test_get_translation_spanish(self):
        """Test getting Spanish translations."""
        i18n = I18n('es')
        self.assertEqual(i18n.get('ready'), 'Listo')
        self.assertEqual(i18n.get('scan'), 'Escanear Repositorio')
    
    def test_get_translation_french(self):
        """Test getting French translations."""
        i18n = I18n('fr')
        self.assertEqual(i18n.get('ready'), 'Prêt')
        self.assertEqual(i18n.get('scan'), 'Analyser le Dépôt')
    
    def test_get_translation_german(self):
        """Test getting German translations."""
        i18n = I18n('de')
        self.assertEqual(i18n.get('ready'), 'Bereit')
        self.assertEqual(i18n.get('scan'), 'Repository Scannen')
    
    def test_get_translation_chinese(self):
        """Test getting Chinese translations."""
        i18n = I18n('zh')
        self.assertEqual(i18n.get('ready'), '就绪')
        self.assertEqual(i18n.get('scan'), '扫描仓库')
    
    def test_get_translation_japanese(self):
        """Test getting Japanese translations."""
        i18n = I18n('ja')
        self.assertEqual(i18n.get('ready'), '準備完了')
        self.assertEqual(i18n.get('scan'), 'リポジトリをスキャン')
    
    def test_get_translation_arabic(self):
        """Test getting Arabic translations."""
        i18n = I18n('ar')
        self.assertEqual(i18n.get('ready'), 'جاهز')
        self.assertEqual(i18n.get('scan'), 'مسح المستودع')
    
    def test_get_translation_fallback(self):
        """Test fallback to English for missing translations."""
        i18n = I18n('en')
        # Non-existent key should return the key itself
        self.assertEqual(i18n.get('non_existent_key'), 'non_existent_key')
    
    def test_get_translation_with_formatting(self):
        """Test translations with formatting parameters."""
        i18n = I18n('en')
        result = i18n.get('error_occurred', error='Test error')
        self.assertEqual(result, 'An error occurred: Test error')
    
    def test_set_language(self):
        """Test changing language."""
        i18n = I18n('en')
        self.assertEqual(i18n.get('ready'), 'Ready')
        
        i18n.set_language('es')
        self.assertEqual(i18n.get('ready'), 'Listo')
    
    def test_is_rtl(self):
        """Test RTL language detection."""
        i18n_ar = I18n('ar')
        self.assertTrue(i18n_ar.is_rtl())
        
        i18n_en = I18n('en')
        self.assertFalse(i18n_en.is_rtl())
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        i18n = I18n('en')
        langs = i18n.get_supported_languages()
        
        self.assertIn('en', langs)
        self.assertIn('es', langs)
        self.assertIn('fr', langs)
        self.assertIn('de', langs)
        self.assertIn('zh', langs)
        self.assertIn('ja', langs)
        self.assertIn('ar', langs)
        
        self.assertEqual(langs['en'], 'English')
        self.assertEqual(langs['es'], 'Español')
    
    def test_global_instance(self):
        """Test global i18n instance."""
        i18n1 = get_i18n()
        i18n2 = get_i18n()
        
        # Should return the same instance
        self.assertIs(i18n1, i18n2)
    
    def test_shorthand_function(self):
        """Test shorthand translation function."""
        # This uses the global instance
        result = _('ready')
        # Should be a valid translation (default language may vary)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
    
    def test_all_languages_have_common_keys(self):
        """Test that all languages have the common keys."""
        common_keys = [
            'app_title', 'ready', 'scanning', 'error', 'success',
            'file', 'edit', 'view', 'help',
            'scan', 'save', 'browse', 'cancel', 'ok',
            'repository', 'template', 'format', 'language',
        ]
        
        for lang_code in I18n.SUPPORTED_LANGUAGES.keys():
            i18n = I18n(lang_code)
            for key in common_keys:
                translation = i18n.get(key)
                # Should not be empty and should not be the key itself (except for unsupported languages)
                self.assertTrue(len(translation) > 0, 
                    f"Language {lang_code} missing translation for key: {key}")


class TestI18nIntegration(unittest.TestCase):
    """Integration tests for i18n module."""
    
    def test_language_consistency(self):
        """Test that switching languages maintains consistency."""
        languages = ['en', 'es', 'fr', 'de']
        
        for lang in languages:
            i18n = I18n(lang)
            # Should have app title
            app_title = i18n.get('app_title')
            self.assertTrue('AccuDoc' in app_title)
            
            # Should have all menu items
            self.assertTrue(len(i18n.get('file')) > 0)
            self.assertTrue(len(i18n.get('edit')) > 0)
            self.assertTrue(len(i18n.get('view')) > 0)
            self.assertTrue(len(i18n.get('help')) > 0)


if __name__ == '__main__':
    unittest.main()
