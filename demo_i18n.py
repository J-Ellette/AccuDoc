#!/usr/bin/env python3
"""
Demo script for AccuDoc Internationalization features.

This demonstrates the multi-language support in AccuDoc, including:
- UI translation in 7 languages
- Automatic locale detection
- RTL language support
- Language preferences persistence
"""

from accudoc.i18n import I18n, get_i18n


def demo_basic_translation():
    """Demonstrate basic translation functionality."""
    print("=" * 70)
    print("DEMO: Basic Translation")
    print("=" * 70)
    
    # Show all supported languages
    i18n = I18n('en')
    print("\nSupported Languages:")
    for code, name in i18n.get_supported_languages().items():
        print(f"  {code}: {name}")
    
    print("\n")


def demo_language_switching():
    """Demonstrate switching between languages."""
    print("=" * 70)
    print("DEMO: Language Switching")
    print("=" * 70)
    
    languages = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'ar']
    
    for lang in languages:
        i18n = I18n(lang)
        lang_name = i18n.get_supported_languages()[lang]
        
        print(f"\n{lang_name} ({lang}):")
        print(f"  App Title: {i18n.get('app_title')}")
        print(f"  Scan Button: {i18n.get('scan')}")
        print(f"  Ready Status: {i18n.get('ready')}")
        print(f"  Settings: {i18n.get('settings')}")


def demo_auto_detection():
    """Demonstrate automatic locale detection."""
    print("\n" + "=" * 70)
    print("DEMO: Automatic Locale Detection")
    print("=" * 70)
    
    i18n = I18n()  # No language specified - auto-detect
    detected_lang = i18n.get_language()
    lang_name = i18n.get_supported_languages()[detected_lang]
    
    print(f"\nDetected system language: {lang_name} ({detected_lang})")
    print(f"Sample translation: {i18n.get('app_title')}")


def demo_rtl_support():
    """Demonstrate RTL language detection."""
    print("\n" + "=" * 70)
    print("DEMO: RTL (Right-to-Left) Language Support")
    print("=" * 70)
    
    languages = ['en', 'ar', 'he']
    
    for lang in languages:
        try:
            i18n = I18n(lang)
            lang_name = i18n.get_supported_languages().get(lang, lang)
            is_rtl = i18n.is_rtl()
            
            print(f"\n{lang_name} ({lang}):")
            print(f"  RTL: {'Yes' if is_rtl else 'No'}")
            print(f"  Sample: {i18n.get('scan')}")
        except Exception as e:
            print(f"  (Language not fully supported: {e})")


def demo_formatting():
    """Demonstrate formatted translations."""
    print("\n" + "=" * 70)
    print("DEMO: Formatted Translations")
    print("=" * 70)
    
    languages = ['en', 'es', 'fr', 'de']
    error_msg = "File not found"
    
    for lang in languages:
        i18n = I18n(lang)
        lang_name = i18n.get_supported_languages()[lang]
        
        formatted = i18n.get('error_occurred', error=error_msg)
        print(f"\n{lang_name}: {formatted}")


def demo_common_ui_strings():
    """Demonstrate common UI strings in different languages."""
    print("\n" + "=" * 70)
    print("DEMO: Common UI Strings")
    print("=" * 70)
    
    ui_elements = [
        ('file', 'File Menu'),
        ('edit', 'Edit Menu'),
        ('view', 'View Menu'),
        ('help', 'Help Menu'),
        ('ok', 'OK Button'),
        ('cancel', 'Cancel Button'),
        ('save', 'Save Button'),
    ]
    
    languages = ['en', 'es', 'fr', 'de', 'zh', 'ja']
    
    print("\n" + " " * 15 + "  ".join(f"{I18n(l).get_supported_languages()[l][:8]:>8}" for l in languages))
    print("-" * 70)
    
    for key, description in ui_elements:
        translations = [I18n(lang).get(key) for lang in languages]
        print(f"{description:15} " + "  ".join(f"{t:>8}" for t in translations))


def demo_template_names():
    """Demonstrate template name translations."""
    print("\n" + "=" * 70)
    print("DEMO: Template Names")
    print("=" * 70)
    
    templates = [
        'template_default',
        'template_minimal',
        'template_detailed',
        'template_api',
        'template_readme',
        'template_student',
    ]
    
    languages = ['en', 'es', 'fr']
    
    for lang in languages:
        i18n = I18n(lang)
        lang_name = i18n.get_supported_languages()[lang]
        
        print(f"\n{lang_name}:")
        for template_key in templates:
            print(f"  {template_key.split('_')[1].title()}: {i18n.get(template_key)}")


def demo_complete_ui_scenario():
    """Demonstrate a complete UI interaction scenario."""
    print("\n" + "=" * 70)
    print("DEMO: Complete UI Scenario")
    print("=" * 70)
    
    print("\nSimulating user workflow in Spanish:")
    i18n = I18n('es')
    
    print(f"\n1. Window Title: {i18n.get('app_title')}")
    print(f"2. Status: {i18n.get('ready')}")
    print(f"3. Input Label: {i18n.get('repository')}")
    print(f"4. Action Button: {i18n.get('scan')}")
    print(f"5. Browse Button: {i18n.get('browse')}")
    print(f"6. Status Update: {i18n.get('scanning_repository')}")
    print(f"7. Success Message: {i18n.get('scan_complete')}")
    print(f"8. Save Action: {i18n.get('save')}")
    
    print("\nSimulating the same workflow in Japanese:")
    i18n = I18n('ja')
    
    print(f"\n1. Window Title: {i18n.get('app_title')}")
    print(f"2. Status: {i18n.get('ready')}")
    print(f"3. Input Label: {i18n.get('repository')}")
    print(f"4. Action Button: {i18n.get('scan')}")
    print(f"5. Browse Button: {i18n.get('browse')}")
    print(f"6. Status Update: {i18n.get('scanning_repository')}")
    print(f"7. Success Message: {i18n.get('scan_complete')}")
    print(f"8. Save Action: {i18n.get('save')}")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "AccuDoc Internationalization Demo" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    
    demo_basic_translation()
    demo_language_switching()
    demo_auto_detection()
    demo_rtl_support()
    demo_formatting()
    demo_common_ui_strings()
    demo_template_names()
    demo_complete_ui_scenario()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ 7 language translations (EN, ES, FR, DE, ZH, JA, AR)")
    print("  ✓ Automatic locale detection")
    print("  ✓ RTL language support detection")
    print("  ✓ Dynamic language switching")
    print("  ✓ Formatted string translations")
    print("  ✓ Complete UI coverage")
    print("\nTo use in the GUI:")
    print("  1. Run: python main.py")
    print("  2. Click 'Settings' button")
    print("  3. Select your preferred language")
    print("  4. Restart the application")
    print("\n")


if __name__ == '__main__':
    main()
