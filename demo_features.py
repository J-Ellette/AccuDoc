#!/usr/bin/env python3
"""
Demonstration script for AccuDoc Documentation Generation Features.

This script showcases all the newly implemented features:
- API Documentation extraction
- Code Examples extraction
- TODO/FIXME comment extraction
- Code Statistics
- Architecture diagrams
- Dependency graphs
- Multiple output formats
- Security badges
"""

from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator
from accudoc.exporters import DocumentExporter
from pathlib import Path
import sys


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70 + "\n")


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "-" * 70)
    print(title)
    print("-" * 70)


def main():
    """Run the demonstration."""
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print_header("AccuDoc Documentation Generation Features Demo")
    
    print(f"Repository: {repo_path}")
    print()
    
    # Scan repository
    print("📊 Scanning repository...")
    scanner = RepositoryScanner(repo_path)
    repo_info = scanner.scan()
    print("✓ Scan complete!\n")
    
    # Feature 1: API Documentation
    print_section("Feature 1: API Documentation Extraction")
    api_docs = repo_info.get('api_docs', {})
    classes = api_docs.get('classes', [])
    functions = api_docs.get('functions', [])
    methods = api_docs.get('methods', [])
    
    print(f"Extracted API documentation:")
    print(f"  • Classes: {len(classes)}")
    print(f"  • Functions: {len(functions)}")
    print(f"  • Methods: {len(methods)}")
    
    if classes:
        print(f"\nSample Classes:")
        for cls in classes[:3]:
            print(f"  - {cls['name']} ({cls['file']}:{cls['line']})")
            if cls.get('docstring'):
                print(f"    {cls['docstring'][:60]}...")
    
    # Feature 2: Code Examples
    print_section("Feature 2: Code Examples Extraction")
    examples = repo_info.get('code_examples', [])
    print(f"Found {len(examples)} code examples")
    
    if examples:
        print(f"\nSample Examples:")
        for example in examples[:3]:
            print(f"  - {example['name']} ({example['file']})")
    
    # Feature 3: TODO/FIXME Comments
    print_section("Feature 3: TODO/FIXME Comment Extraction")
    todos = repo_info.get('todos', [])
    print(f"Found {len(todos)} TODO items")
    
    if todos:
        # Group by type
        from collections import Counter
        todo_types = Counter(todo['type'] for todo in todos)
        print(f"\nBreakdown by type:")
        for todo_type, count in todo_types.items():
            print(f"  • {todo_type}: {count}")
        
        print(f"\nSample TODOs:")
        for todo in todos[:3]:
            print(f"  - {todo['type']} in {todo['file']}:{todo['line']}")
            print(f"    {todo['message'][:60]}...")
    
    # Feature 4: Code Statistics
    print_section("Feature 4: Code Statistics")
    stats = repo_info.get('code_stats', {})
    
    if stats:
        print(f"Overall Statistics:")
        print(f"  • Total Lines: {stats.get('total_lines', 0):,}")
        print(f"  • Code Lines: {stats.get('code_lines', 0):,}")
        print(f"  • Comment Lines: {stats.get('comment_lines', 0):,}")
        print(f"  • Blank Lines: {stats.get('blank_lines', 0):,}")
        print(f"  • Files Analyzed: {stats.get('file_count', 0)}")
        
        total = stats.get('total_lines', 0)
        if total > 0:
            code_pct = (stats.get('code_lines', 0) / total) * 100
            comment_pct = (stats.get('comment_lines', 0) / total) * 100
            print(f"\nCode Distribution:")
            print(f"  • Code: {code_pct:.1f}%")
            print(f"  • Comments: {comment_pct:.1f}%")
        
        by_lang = stats.get('by_language', {})
        if by_lang:
            print(f"\nBy Language:")
            for lang, lang_stats in sorted(by_lang.items()):
                print(f"  • {lang}: {lang_stats['total_lines']:,} lines in {lang_stats['files']} files")
    
    # Feature 5: Architecture Diagrams
    print_section("Feature 5: Architecture Diagrams")
    architecture = repo_info.get('architecture', {})
    
    if architecture:
        dirs = architecture.get('directories', [])
        print(f"Project structure identified:")
        print(f"  • Main directories: {len(dirs)}")
        print(f"  • Mermaid diagram: {'✓' if architecture.get('mermaid') else '✗'}")
        print(f"  • Text diagram: {'✓' if architecture.get('text') else '✗'}")
        
        if dirs:
            print(f"\nTop-level directories:")
            for dir_name in sorted(dirs)[:5]:
                print(f"  - {dir_name}/")
    
    # Feature 6: Dependency Graphs
    print_section("Feature 6: Dependency Graphs")
    dep_graph = repo_info.get('dependency_graph', {})
    
    if dep_graph:
        summary = dep_graph.get('summary', {})
        print(f"Dependency analysis:")
        print(f"  • Dependency types: {len(summary)}")
        print(f"  • Mermaid diagram: {'✓' if dep_graph.get('mermaid') else '✗'}")
        
        if summary:
            print(f"\nDependencies by type:")
            for dep_type, deps in summary.items():
                print(f"  • {dep_type}: {len(deps)} packages")
    
    # Feature 7: Badges
    print_section("Feature 7: Security & Status Badges")
    badges = repo_info.get('badges', [])
    
    print(f"Generated {len(badges)} badges:")
    for badge in badges:
        print(f"  • {badge['label']}: {badge['message']} ({badge['color']})")
    
    # Feature 8: Multiple Output Formats
    print_section("Feature 8: Multiple Output Formats")
    
    print("Generating documentation in multiple formats...")
    generator = DocumentGenerator(repo_info)
    
    output_dir = Path('/tmp/accudoc_output')
    output_dir.mkdir(exist_ok=True)
    
    formats = [
        ('markdown', 'md', {}),
        ('html', 'html', {'theme': 'default'}),
        ('html', 'dark.html', {'theme': 'dark'}),
        ('text', 'txt', {}),
    ]
    
    for format_type, ext, kwargs in formats:
        output_path = output_dir / f'documentation.{ext}'
        generator.generate_and_export(str(output_path), format=format_type, **kwargs)
        size = output_path.stat().st_size
        theme = f" ({kwargs.get('theme', 'default')})" if 'theme' in kwargs else ""
        print(f"  ✓ {format_type.upper()}{theme}: {output_path} ({size:,} bytes)")
    
    # Summary
    print_header("Summary")
    
    print("All Documentation Generation Features Successfully Demonstrated!")
    print()
    print("Features Implemented:")
    print("  ✓ API Documentation extraction")
    print("  ✓ Code Examples extraction")
    print("  ✓ TODO/FIXME comment extraction")
    print("  ✓ Code Statistics (LOC, by language)")
    print("  ✓ Architecture diagrams (Mermaid)")
    print("  ✓ Dependency graphs (Mermaid)")
    print("  ✓ Security & status badges")
    print("  ✓ Multiple output formats (Markdown, HTML, Text)")
    print()
    print(f"Generated documentation available in: {output_dir}")
    print()
    
    # Show a preview
    print("Preview of generated documentation:")
    print("-" * 70)
    doc = generator.generate_all()
    preview_lines = doc.split('\n')[:30]
    for line in preview_lines:
        print(line)
    print("...")
    print("-" * 70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
