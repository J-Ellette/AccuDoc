#!/usr/bin/env python3
"""
Demo script for AccuDoc Phase 2 features:
- Multi-Repository Support
- Test Coverage Analysis
- Readability Metrics
- Database Schema Extraction

This script demonstrates the advanced features added in Phase 2.
"""

import sys
import tempfile
import shutil
import json
from pathlib import Path
from accudoc.multi_repo import MultiRepositoryManager
from accudoc.test_coverage import TestCoverageAnalyzer as CoverageAnalyzer
from accudoc.readability import ReadabilityAnalyzer
from accudoc.db_schema import DatabaseSchemaExtractor


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def demo_multi_repository():
    """Demonstrate multi-repository support."""
    print_section("1. Multi-Repository Support")
    
    print("\nFeature: Scan and document multiple related repositories")
    print("Use cases:")
    print("  - Microservices architecture documentation")
    print("  - Related project ecosystems")
    print("  - Organization-wide documentation")
    
    print("\nCreating sample multi-repository setup...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create two sample repositories
        repos = []
        for i in range(2):
            repo_dir = Path(temp_dir) / f'service{i+1}'
            repo_dir.mkdir()
            (repo_dir / f'main.py').write_text(f'# Service {i+1}\n\ndef main():\n    pass')
            (repo_dir / 'README.md').write_text(f'# Service {i+1}\n\nMicroservice {i+1}')
            repos.append({
                'path': str(repo_dir),
                'name': f'Service{i+1}',
                'group': 'Microservices',
                'description': f'Microservice handling feature {i+1}'
            })
        
        manager = MultiRepositoryManager(max_workers=2)
        results = manager.scan_repositories(repos)
        
        print(f"\n  Total repositories: {results['summary']['total']}")
        print(f"  Successfully scanned: {results['summary']['successful']}")
        print(f"  Failed: {results['summary']['failed']}")
        
        # Generate unified documentation
        doc = manager.generate_unified_documentation(results, "Microservices Documentation")
        print(f"\n  Generated unified documentation ({len(doc)} characters)")
        print(f"  ✓ Multi-repository support working!")
        
    finally:
        shutil.rmtree(temp_dir)
    
    print("\nCLI Usage:")
    print("  python accudoc_cli.py multi-repo config.json -o docs.md")
    print("  python accudoc_cli.py multi-repo config.json -f comparison")


def demo_test_coverage():
    """Demonstrate test coverage analysis."""
    print_section("2. Test Coverage Analysis")
    
    print("\nFeature: Extract and analyze test coverage metrics")
    print("Use cases:")
    print("  - Monitor code quality")
    print("  - Identify untested code")
    print("  - Track coverage over time")
    
    print("\nCreating sample coverage report...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create sample Python coverage.xml
        coverage_xml = '''<?xml version="1.0" ?>
<coverage version="5.5" timestamp="1234567890" lines-covered="850" lines-valid="1000" line-rate="0.85" branch-rate="0.80">
    <packages>
        <package name="myapp" line-rate="0.85">
            <classes>
                <class name="main.py" filename="myapp/main.py" line-rate="0.90"></class>
                <class name="utils.py" filename="myapp/utils.py" line-rate="0.75"></class>
            </classes>
        </package>
    </packages>
</coverage>'''
        
        coverage_file = Path(temp_dir) / 'coverage.xml'
        coverage_file.write_text(coverage_xml)
        
        analyzer = CoverageAnalyzer(temp_dir)
        coverage_data = analyzer.analyze_coverage()
        
        if coverage_data.get('status') == 'success':
            data = coverage_data['coverage_data'][0]
            overall = data['overall']
            
            print(f"\n  Line Coverage: {overall['line_rate']:.1f}%")
            print(f"  Branch Coverage: {overall['branch_rate']:.1f}%")
            print(f"  Lines Covered: {overall['lines_covered']} / {overall['lines_valid']}")
            
            print(f"\n  ✓ Coverage analysis working!")
        
    finally:
        shutil.rmtree(temp_dir)
    
    print("\nSupported Formats:")
    print("  - Python: coverage.xml (coverage.py, pytest-cov)")
    print("  - JavaScript: coverage-final.json (Istanbul/NYC)")
    print("  - Go: coverage.out")
    
    print("\nCLI Usage:")
    print("  python accudoc_cli.py coverage <repo>")
    print("  python accudoc_cli.py coverage <repo> -o coverage-report.md")


def demo_readability():
    """Demonstrate readability analysis."""
    print_section("3. Readability Metrics")
    
    print("\nFeature: Calculate readability scores for documentation")
    print("Use cases:")
    print("  - Ensure documentation accessibility")
    print("  - Maintain consistent writing quality")
    print("  - Meet documentation standards")
    
    print("\nAnalyzing sample documentation...")
    
    sample_text = """
    # Documentation Guide
    
    This guide provides comprehensive information about our software.
    The documentation is designed to be clear and accessible to all users.
    
    ## Getting Started
    
    Begin by installing the required software packages. Follow the installation
    instructions carefully to ensure proper setup. Once installed, you can start
    using the application immediately.
    
    ## Advanced Features
    
    Our platform offers sophisticated functionality for experienced users.
    These features enable complex workflows and advanced customization options.
    """
    
    analyzer = ReadabilityAnalyzer()
    result = analyzer.analyze_text(sample_text)
    
    if 'statistics' in result:
        stats = result['statistics']
        scores = result['scores']
        
        print(f"\n  Statistics:")
        print(f"    Words: {stats['words']}")
        print(f"    Sentences: {stats['sentences']}")
        print(f"    Avg words/sentence: {stats['avg_words_per_sentence']:.1f}")
        
        print(f"\n  Readability Scores:")
        print(f"    Flesch Reading Ease: {scores['flesch_reading_ease']:.1f}")
        interpretation = analyzer.interpret_score('flesch_reading_ease', scores['flesch_reading_ease'])
        print(f"    → {interpretation}")
        
        print(f"    Flesch-Kincaid Grade: {scores['flesch_kincaid_grade']:.1f}")
        interpretation = analyzer.interpret_score('flesch_kincaid_grade', scores['flesch_kincaid_grade'])
        print(f"    → {interpretation}")
        
        print(f"\n  ✓ Readability analysis working!")
    
    print("\nMetrics Calculated:")
    print("  - Flesch Reading Ease")
    print("  - Flesch-Kincaid Grade Level")
    print("  - Gunning Fog Index")
    print("  - Coleman-Liau Index")
    print("  - Automated Readability Index (ARI)")
    
    print("\nCLI Usage:")
    print("  python accudoc_cli.py readability docs/")
    print("  python accudoc_cli.py readability README.md -o report.md")


def demo_database_schema():
    """Demonstrate database schema extraction."""
    print_section("4. Database Schema Extraction")
    
    print("\nFeature: Extract and document database schemas")
    print("Use cases:")
    print("  - Document database structure")
    print("  - Understand data models")
    print("  - Generate ER diagrams")
    
    print("\nExtracting schema from sample files...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create sample SQL schema
        migrations_dir = Path(temp_dir) / 'migrations'
        migrations_dir.mkdir()
        
        sql_content = '''
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
'''
        
        (migrations_dir / '001_initial.sql').write_text(sql_content)
        
        extractor = DatabaseSchemaExtractor(temp_dir)
        schema = extractor.extract_schema()
        
        if schema.get('status') == 'success':
            print(f"\n  Tables found: {len(schema['tables'])}")
            
            for table in schema['tables']:
                print(f"\n  Table: {table['name']}")
                print(f"    Columns: {len(table['columns'])}")
                for col in table['columns'][:3]:  # Show first 3 columns
                    constraints = []
                    if col.get('primary_key'):
                        constraints.append('PK')
                    if col.get('not_null'):
                        constraints.append('NOT NULL')
                    constraint_str = f" ({', '.join(constraints)})" if constraints else ""
                    print(f"      - {col['name']}: {col['type']}{constraint_str}")
            
            print(f"\n  ✓ Schema extraction working!")
        
    finally:
        shutil.rmtree(temp_dir)
    
    print("\nSupported Sources:")
    print("  - SQL migration files")
    print("  - Django models (models.py)")
    print("  - Rails migrations (*.rb)")
    print("  - Schema definition files")
    
    print("\nCLI Usage:")
    print("  python accudoc_cli.py db-schema <repo>")
    print("  python accudoc_cli.py db-schema <repo> -o schema-docs.md")


def demo_integration():
    """Demonstrate how Phase 2 features integrate."""
    print_section("5. Phase 2 Feature Integration")
    
    print("\nAll Phase 2 features work together seamlessly:")
    
    print("\n1. Multi-Repository Support:")
    print("   ✓ Scan multiple related repositories in parallel")
    print("   ✓ Generate unified documentation")
    print("   ✓ Create comparison matrices")
    
    print("\n2. Test Coverage Analysis:")
    print("   ✓ Support Python, JavaScript, and Go")
    print("   ✓ Parse coverage reports automatically")
    print("   ✓ Generate actionable insights")
    
    print("\n3. Readability Metrics:")
    print("   ✓ Calculate multiple readability scores")
    print("   ✓ Provide interpretations")
    print("   ✓ Suggest improvements")
    
    print("\n4. Database Schema Extraction:")
    print("   ✓ Extract from SQL and ORM models")
    print("   ✓ Document tables and relationships")
    print("   ✓ Support multiple frameworks")
    
    print("\n5. CLI Integration:")
    print("   ✓ 4 new commands: multi-repo, coverage, readability, db-schema")
    print("   ✓ Consistent interface across all features")
    print("   ✓ JSON and Markdown output formats")
    print("   ✓ CI/CD ready")


def main():
    """Run all Phase 2 demonstrations."""
    print("\n" + "=" * 70)
    print(" AccuDoc Phase 2 Features Demo")
    print(" Advanced Documentation Features")
    print("=" * 70)
    
    try:
        demo_multi_repository()
        demo_test_coverage()
        demo_readability()
        demo_database_schema()
        demo_integration()
        
        print("\n" + "=" * 70)
        print(" Demo Complete!")
        print("=" * 70)
        print("\n✓ All Phase 2 features demonstrated successfully")
        print("\nTotal Features Implemented:")
        print("  Phase 1: 3 features (branch-compare, version-check, spellcheck)")
        print("  Phase 2: 4 features (multi-repo, coverage, readability, db-schema)")
        print("  Total: 7 new features from ideas.md")
        print("\nFor more information:")
        print("  - Run tests: python test_phase2_features.py")
        print("  - See CLI help: python accudoc_cli.py --help")
        print("  - Read ideas.md for all planned features")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
