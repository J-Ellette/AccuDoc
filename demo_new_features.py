#!/usr/bin/env python3
"""Demo script showcasing new documentation generation features."""

import sys
import os
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator
from accudoc.templates import TemplateManager


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_templates():
    """Demonstrate template system."""
    print_header("Demo 1: Template System")
    
    manager = TemplateManager()
    templates = manager.list_templates()
    
    print("Available Built-in Templates:\n")
    for i, tpl in enumerate(templates, 1):
        print(f"{i}. {tpl['name']}")
        print(f"   ID: {tpl['id']}")
        print(f"   Description: {tpl['description']}")
        print()
    
    # Demonstrate each template
    print("Generating documentation with different templates...")
    print()
    
    scanner = RepositoryScanner(str(Path(__file__).parent))
    repo_info = scanner.scan()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for tpl in templates[:3]:  # Demo first 3 templates
            if tpl['type'] == 'builtin':
                generator = DocumentGenerator(repo_info, template=tpl['id'])
                output_path = Path(tmpdir) / f"{tpl['id']}_example.md"
                generator.generate_and_export(str(output_path))
                
                # Show first few lines
                with open(output_path, 'r') as f:
                    lines = f.readlines()[:5]
                    print(f"Template '{tpl['name']}' preview:")
                    for line in lines:
                        print(f"  {line.rstrip()}")
                    print(f"  ... ({len(open(output_path).readlines())} total lines)")
                    print()


def demo_markdown_flavors():
    """Demonstrate markdown flavor support."""
    print_header("Demo 2: Markdown Flavors")
    
    from accudoc.markdown_flavors import MarkdownFlavorManager
    
    # Sample content
    sample = """# Sample Documentation

## Overview
This demonstrates **markdown flavors**.

## Features
- [ ] Feature 1
- [x] Feature 2 (completed)

## Code
```python
def hello():
    print("Hello!")
```
"""
    
    flavors = ['github', 'gitlab', 'commonmark']
    
    print("Converting sample markdown to different flavors:\n")
    
    for flavor in flavors:
        print(f"Flavor: {flavor.upper()}")
        print("-" * 50)
        result = MarkdownFlavorManager.convert(sample, flavor)
        # Show first few lines of converted output
        lines = result.split('\n')[:10]
        for line in lines:
            if line.strip():
                print(f"  {line}")
        print()


def demo_themes():
    """Demonstrate HTML themes."""
    print_header("Demo 3: HTML Themes")
    
    scanner = RepositoryScanner(str(Path(__file__).parent))
    repo_info = scanner.scan()
    generator = DocumentGenerator(repo_info, template='minimal')
    
    themes = {
        'default': 'Clean, professional light theme',
        'dark': 'Modern dark theme for reduced eye strain',
        'minimal': 'Ultra-clean, distraction-free theme',
        'corporate': 'Professional gradient theme for business'
    }
    
    print("Available HTML Themes:\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for theme, description in themes.items():
            output_path = Path(tmpdir) / f"demo_{theme}.html"
            generator.generate_and_export(
                str(output_path),
                format='html',
                theme=theme,
                title=f"AccuDoc Demo - {theme.title()} Theme"
            )
            
            size = output_path.stat().st_size
            print(f"✓ {theme.title()} Theme")
            print(f"  Description: {description}")
            print(f"  Generated: {size:,} bytes")
            print(f"  Location: {output_path.name}")
            print()


def demo_custom_template():
    """Demonstrate custom template creation."""
    print_header("Demo 4: Custom Template Creation")
    
    print("Creating a custom 'Quick Start' template...\n")
    
    manager = TemplateManager()
    
    # Create a custom quick-start template
    sections = [
        ('header', '_generate_header', 0),
        ('overview', '_generate_overview', 10),
        ('installation', '_generate_installation', 20),
        ('usage', '_generate_usage', 30),
        ('examples', '_generate_code_examples', 40),
    ]
    
    custom = manager.create_custom_template(
        'quickstart',
        'Quick Start Guide',
        'Minimal template for getting started quickly',
        sections
    )
    
    print(f"✓ Created template: {custom.name}")
    print(f"  Description: {custom.description}")
    print(f"  Sections: {len(custom.get_sections())}")
    print("\n  Included sections:")
    for section in custom.get_sections():
        print(f"    - {section['name']}")
    
    # Use the custom template
    print("\nGenerating documentation with custom template...")
    scanner = RepositoryScanner(str(Path(__file__).parent))
    repo_info = scanner.scan()
    
    generator = DocumentGenerator(repo_info, template='quickstart')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "quickstart.md"
        generator.generate_and_export(str(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            print(f"\n✓ Generated {len(content)} characters of documentation")
            print(f"  Preview (first 200 chars):")
            print(f"  {content[:200]}...")


def demo_combined():
    """Demonstrate combining multiple features."""
    print_header("Demo 5: Combining Features")
    
    print("Generating documentation with combined features:\n")
    
    scanner = RepositoryScanner(str(Path(__file__).parent))
    repo_info = scanner.scan()
    
    examples = [
        {
            'desc': 'GitHub README (minimal template, GitHub flavor)',
            'template': 'minimal',
            'format': 'markdown',
            'flavor': 'github',
            'filename': 'README_github.md'
        },
        {
            'desc': 'GitLab README (readme template, GitLab flavor)',
            'template': 'readme',
            'format': 'markdown',
            'flavor': 'gitlab',
            'filename': 'README_gitlab.md'
        },
        {
            'desc': 'API Docs HTML (api template, dark theme)',
            'template': 'api',
            'format': 'html',
            'theme': 'dark',
            'filename': 'api_docs.html'
        },
        {
            'desc': 'Corporate Docs (detailed template, corporate theme)',
            'template': 'detailed',
            'format': 'html',
            'theme': 'corporate',
            'filename': 'corporate_docs.html'
        },
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for example in examples:
            generator = DocumentGenerator(repo_info, template=example['template'])
            output_path = Path(tmpdir) / example['filename']
            
            kwargs = {
                'format': example['format']
            }
            if 'flavor' in example:
                kwargs['markdown_flavor'] = example['flavor']
            if 'theme' in example:
                kwargs['theme'] = example['theme']
            
            generator.generate_and_export(str(output_path), **kwargs)
            
            size = output_path.stat().st_size
            print(f"✓ {example['desc']}")
            print(f"  File: {example['filename']}")
            print(f"  Size: {size:,} bytes")
            print()


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  AccuDoc - Documentation Generation Features Demo")
    print("=" * 70)
    print("\nThis demo showcases the new features added to AccuDoc:")
    print("  1. Custom Templates System")
    print("  2. Markdown Flavor Support")
    print("  3. Enhanced HTML Themes")
    print("  4. Custom Template Creation")
    print("  5. Combining Multiple Features")
    
    try:
        demo_templates()
        demo_markdown_flavors()
        demo_themes()
        demo_custom_template()
        demo_combined()
        
        print_header("Demo Complete!")
        print("All features demonstrated successfully!")
        print("\nFor more information, see:")
        print("  - COMPLETE_DOCUMENTATION_FEATURES.md")
        print("  - ideas.md (Documentation Generation Features section)")
        print()
        
    except Exception as e:
        print(f"\n✗ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
