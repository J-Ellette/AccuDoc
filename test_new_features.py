#!/usr/bin/env python3
"""Test script for new documentation generation features."""

import sys
import os
from pathlib import Path
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator
from accudoc.templates import TemplateManager
from accudoc.markdown_flavors import MarkdownFlavorManager


def test_templates():
    """Test template system."""
    print("=" * 60)
    print("Test 1: Template System")
    print("=" * 60)
    
    try:
        manager = TemplateManager()
        
        # List templates
        templates = manager.list_templates()
        print(f"✓ Found {len(templates)} built-in templates:")
        for tpl in templates:
            print(f"  - {tpl['id']}: {tpl['name']} - {tpl['description']}")
        
        # Test each template
        scanner = RepositoryScanner(str(Path(__file__).parent))
        repo_info = scanner.scan()
        
        for tpl in templates:
            if tpl['type'] == 'builtin':
                generator = DocumentGenerator(repo_info, template=tpl['id'])
                doc = generator.generate_all()
                if doc and len(doc) > 100:
                    print(f"✓ Template '{tpl['id']}' generated {len(doc)} characters")
                else:
                    print(f"✗ Template '{tpl['id']}' failed")
                    return False
        
        print("\n✓ Test PASSED: All templates working")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_markdown_flavors():
    """Test markdown flavor support."""
    print("\n" + "=" * 60)
    print("Test 2: Markdown Flavors")
    print("=" * 60)
    
    try:
        # Get test content
        test_content = """# Test Document

## Overview
This is a test document with **bold** and *italic* text.

## Code Example
```
def hello():
    print("Hello, World!")
```

## Task List
- [ ] Task 1
- [x] Task 2

## Table
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
"""
        
        flavors = MarkdownFlavorManager.get_supported_flavors()
        print(f"✓ Found {len(flavors)} flavors: {', '.join(flavors)}")
        
        for flavor in ['github', 'gitlab', 'commonmark']:
            result = MarkdownFlavorManager.convert(test_content, flavor)
            if result and len(result) > 0:
                print(f"✓ Flavor '{flavor}' converted successfully ({len(result)} chars)")
            else:
                print(f"✗ Flavor '{flavor}' failed")
                return False
        
        print("\n✓ Test PASSED: All markdown flavors working")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_themes():
    """Test HTML themes."""
    print("\n" + "=" * 60)
    print("Test 3: HTML Themes")
    print("=" * 60)
    
    try:
        scanner = RepositoryScanner(str(Path(__file__).parent))
        repo_info = scanner.scan()
        generator = DocumentGenerator(repo_info)
        
        themes = ['default', 'dark', 'minimal', 'corporate']
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for theme in themes:
                output_path = Path(tmpdir) / f"test_{theme}.html"
                result = generator.generate_and_export(
                    str(output_path),
                    format='html',
                    theme=theme
                )
                
                if output_path.exists():
                    size = output_path.stat().st_size
                    print(f"✓ Theme '{theme}' generated ({size} bytes)")
                else:
                    print(f"✗ Theme '{theme}' failed")
                    return False
        
        print("\n✓ Test PASSED: All themes working")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_template():
    """Test custom template creation and loading."""
    print("\n" + "=" * 60)
    print("Test 4: Custom Templates")
    print("=" * 60)
    
    try:
        manager = TemplateManager()
        
        # Create a custom template
        sections = [
            ('header', '_generate_header', 0),
            ('overview', '_generate_overview', 10),
            ('features', '_generate_features', 20),
            ('license', '_generate_license_section', 30),
        ]
        
        custom = manager.create_custom_template(
            'my_custom',
            'My Custom Template',
            'A custom template for testing',
            sections
        )
        
        print(f"✓ Created custom template: {custom.name}")
        print(f"  Sections: {len(custom.get_sections())}")
        
        # Test with generator
        scanner = RepositoryScanner(str(Path(__file__).parent))
        repo_info = scanner.scan()
        generator = DocumentGenerator(repo_info, template='my_custom')
        doc = generator.generate_all()
        
        if doc and len(doc) > 100:
            print(f"✓ Custom template generated {len(doc)} characters")
        else:
            print(f"✗ Custom template failed to generate content")
            return False
        
        # Test saving and loading
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "custom_template.json"
            manager.save_custom_template(custom, 'my_custom', str(template_path))
            
            if template_path.exists():
                print(f"✓ Saved custom template to {template_path}")
                
                # Load it back
                new_manager = TemplateManager()
                loaded_id = new_manager.load_custom_template(str(template_path))
                print(f"✓ Loaded custom template: {loaded_id}")
                
                loaded_template = new_manager.get_template(loaded_id)
                if loaded_template.name == custom.name:
                    print(f"✓ Loaded template matches original")
                else:
                    print(f"✗ Loaded template doesn't match")
                    return False
            else:
                print(f"✗ Failed to save custom template")
                return False
        
        print("\n✓ Test PASSED: Custom templates working")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_features():
    """Test combining templates, flavors, and themes."""
    print("\n" + "=" * 60)
    print("Test 5: Combined Features")
    print("=" * 60)
    
    try:
        scanner = RepositoryScanner(str(Path(__file__).parent))
        repo_info = scanner.scan()
        
        test_cases = [
            ('minimal', 'markdown', 'github', None),
            ('detailed', 'html', None, 'dark'),
            ('api', 'html', None, 'corporate'),
            ('readme', 'markdown', 'gitlab', None),
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for template, format, flavor, theme in test_cases:
                generator = DocumentGenerator(repo_info, template=template)
                
                ext = 'md' if format == 'markdown' else 'html'
                output_path = Path(tmpdir) / f"test_{template}.{ext}"
                
                kwargs = {'format': format}
                if flavor:
                    kwargs['markdown_flavor'] = flavor
                if theme:
                    kwargs['theme'] = theme
                
                result = generator.generate_and_export(str(output_path), **kwargs)
                
                if output_path.exists():
                    size = output_path.stat().st_size
                    desc = f"{template} + {format}"
                    if flavor:
                        desc += f" ({flavor})"
                    if theme:
                        desc += f" [{theme}]"
                    print(f"✓ {desc}: {size} bytes")
                else:
                    print(f"✗ Failed: {template} + {format}")
                    return False
        
        print("\n✓ Test PASSED: Combined features working")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Documentation Generation Features Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_templates,
        test_markdown_flavors,
        test_themes,
        test_custom_template,
        test_combined_features,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"\nPassed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
