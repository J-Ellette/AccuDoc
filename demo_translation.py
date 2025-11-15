#!/usr/bin/env python3
"""
Demo script for documentation translation feature.
Shows how to generate documentation in multiple languages.
"""

from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator
from accudoc.doc_translator import DocumentTranslator
import os


def demo_translation():
    """Demonstrate documentation translation feature."""
    print("=" * 70)
    print("AccuDoc - Documentation Translation Demo")
    print("=" * 70)
    print()
    
    # Scan current repository
    print("Step 1: Scanning repository...")
    scanner = RepositoryScanner('.')
    repo_info = scanner.scan()
    print(f"✓ Scanned: {repo_info['name']}")
    print()
    
    # Generate documentation in English (default)
    print("Step 2: Generating documentation in English (default)...")
    generator = DocumentGenerator(repo_info, template='minimal')
    
    # Create output directory
    os.makedirs('translation_demo', exist_ok=True)
    
    # Generate English version
    output_en = generator.generate_and_export(
        'translation_demo/README_en.md',
        format='markdown',
        language='en'
    )
    print(f"✓ English documentation: {output_en}")
    print()
    
    # Generate Spanish version
    print("Step 3: Generating documentation in Spanish...")
    output_es = generator.generate_and_export(
        'translation_demo/README_es.md',
        format='markdown',
        language='es'
    )
    print(f"✓ Spanish documentation: {output_es}")
    print()
    
    # Generate French version
    print("Step 4: Generating documentation in French...")
    output_fr = generator.generate_and_export(
        'translation_demo/README_fr.md',
        format='markdown',
        language='fr'
    )
    print(f"✓ French documentation: {output_fr}")
    print()
    
    # Generate German version
    print("Step 5: Generating documentation in German...")
    output_de = generator.generate_and_export(
        'translation_demo/README_de.md',
        format='markdown',
        language='de'
    )
    print(f"✓ German documentation: {output_de}")
    print()
    
    # Generate Chinese version
    print("Step 6: Generating documentation in Chinese...")
    output_zh = generator.generate_and_export(
        'translation_demo/README_zh.md',
        format='markdown',
        language='zh'
    )
    print(f"✓ Chinese documentation: {output_zh}")
    print()
    
    # Generate Japanese version
    print("Step 7: Generating documentation in Japanese...")
    output_ja = generator.generate_and_export(
        'translation_demo/README_ja.md',
        format='markdown',
        language='ja'
    )
    print(f"✓ Japanese documentation: {output_ja}")
    print()
    
    # Generate Arabic version
    print("Step 8: Generating documentation in Arabic...")
    output_ar = generator.generate_and_export(
        'translation_demo/README_ar.md',
        format='markdown',
        language='ar'
    )
    print(f"✓ Arabic documentation: {output_ar}")
    print()
    
    # Show supported languages
    print("=" * 70)
    print("Supported Languages")
    print("=" * 70)
    languages = DocumentTranslator.get_supported_languages()
    for code, name in languages.items():
        print(f"  {code}: {name}")
    print()
    
    # Show sample translations
    print("=" * 70)
    print("Sample Translation Preview")
    print("=" * 70)
    print()
    
    # Read and show first few lines of Spanish version
    with open('translation_demo/README_es.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()[:15]
        print("Spanish (README_es.md) - First 15 lines:")
        print("-" * 70)
        for line in lines:
            print(line.rstrip())
    print()
    
    # Read and show first few lines of Chinese version
    with open('translation_demo/README_zh.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()[:15]
        print("Chinese (README_zh.md) - First 15 lines:")
        print("-" * 70)
        for line in lines:
            print(line.rstrip())
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Documentation has been generated in 7 languages:")
    print("  - English (en)")
    print("  - Spanish (es)")
    print("  - French (fr)")
    print("  - German (de)")
    print("  - Chinese (zh)")
    print("  - Japanese (ja)")
    print("  - Arabic (ar)")
    print()
    print("All files are in the 'translation_demo' directory.")
    print()
    print("Usage examples:")
    print("  CLI: python accudoc_cli.py export . -o docs.md -l es")
    print("  CLI: python accudoc_cli.py generate scan.json -o README.md -l fr")
    print()


if __name__ == '__main__':
    demo_translation()
