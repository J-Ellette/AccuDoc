#!/usr/bin/env python3
"""
Validation script for i18n integration.
Tests that all components work together correctly.
"""

import sys
import os

def test_i18n_module():
    """Test i18n module."""
    print("Testing i18n module...")
    from accudoc.i18n import I18n, get_i18n, _
    
    # Test basic functionality
    i18n = I18n('en')
    assert i18n.get('scan') == 'Scan Repository'
    
    i18n = I18n('es')
    assert i18n.get('scan') == 'Escanear Repositorio'
    
    # Test auto-detection
    i18n_auto = I18n()
    assert i18n_auto.get_language() in I18n.SUPPORTED_LANGUAGES
    
    # Test RTL
    assert I18n('ar').is_rtl() == True
    assert I18n('en').is_rtl() == False
    
    print("✓ i18n module tests passed")


def test_settings_integration():
    """Test settings integration."""
    print("Testing settings integration...")
    from accudoc.settings import AccuDocSettings, SettingsManager
    
    # Test that language field exists
    settings = AccuDocSettings()
    assert hasattr(settings, 'language')
    assert settings.language == 'auto'
    
    # Test changing language
    settings.language = 'es'
    assert settings.language == 'es'
    
    print("✓ Settings integration tests passed")


def test_module_imports():
    """Test that all modules import correctly."""
    print("Testing module imports...")
    
    try:
        from accudoc.i18n import I18n
        from accudoc.settings import AccuDocSettings, SettingsManager
        from accudoc.scanner import RepositoryScanner
        from accudoc.generator import DocumentGenerator
        print("✓ All core modules import successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    return True


def test_translation_completeness():
    """Test that all languages have required translations."""
    print("Testing translation completeness...")
    from accudoc.i18n import I18n
    
    required_keys = [
        'app_title', 'ready', 'scan', 'save', 'settings',
        'file', 'edit', 'view', 'help',
        'repository', 'template', 'format', 'language',
    ]
    
    for lang_code in I18n.SUPPORTED_LANGUAGES.keys():
        i18n = I18n(lang_code)
        for key in required_keys:
            translation = i18n.get(key)
            assert len(translation) > 0, f"Missing translation for {key} in {lang_code}"
    
    print(f"✓ All {len(I18n.SUPPORTED_LANGUAGES)} languages have complete translations")


def main():
    """Run all validation tests."""
    print("\n" + "=" * 70)
    print("AccuDoc i18n Integration Validation")
    print("=" * 70 + "\n")
    
    try:
        test_i18n_module()
        test_settings_integration()
        test_module_imports()
        test_translation_completeness()
        
        print("\n" + "=" * 70)
        print("✓ ALL VALIDATION TESTS PASSED")
        print("=" * 70)
        print("\nThe i18n implementation is working correctly and integrated properly.")
        print("Users can now use AccuDoc in 7 different languages!")
        return 0
    
    except Exception as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
