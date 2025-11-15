#!/usr/bin/env python3
"""
Demo script for Multi-Repository Documentation Consistency Dashboard.

This script demonstrates how to use the multi-repo dashboard to analyze
documentation quality across multiple repositories.
"""

import sys
import json
from pathlib import Path
from accudoc.multi_repo_dashboard import MultiRepoDashboard, DashboardConfig
from accudoc.scanner import RepositoryScanner


def create_sample_repos():
    """Create sample repository data for demonstration."""
    
    # Sample repo 1: Well-documented project
    repo1 = {
        'name': 'AccuDoc',
        'path': '/projects/accudoc',
        'files_count': 150,
        'languages': {'Python': 120, 'JavaScript': 30},
        'statistics': {
            'total_lines': 15000,
            'code_lines': 10500,
            'comment_lines': 3000,
            'blank_lines': 1500
        },
        'dependencies': {
            'pip': [
                {'name': 'flask', 'version': '2.0.0'},
                {'name': 'requests', 'version': '2.28.0'},
                {'name': 'pytest', 'version': '7.0.0'}
            ]
        },
        'documentation': [
            'README.md', 'CONTRIBUTING.md', 'LICENSE', 
            'CHANGELOG.md', 'CODE_OF_CONDUCT.md'
        ],
        'api_docs': [
            {'name': 'Scanner API'}, 
            {'name': 'Generator API'}, 
            {'name': 'Dashboard API'}
        ],
        'code_examples': [
            {'file': 'examples/basic.py'},
            {'file': 'examples/advanced.py'},
            {'file': 'examples/api_usage.py'}
        ],
        'todos': [
            {'file': 'scanner.py', 'line': 42, 'type': 'TODO', 'comment': 'Add caching'}
        ],
        'license': 'GPL-3.0'
    }
    
    # Sample repo 2: Moderately documented project
    repo2 = {
        'name': 'WebApp',
        'path': '/projects/webapp',
        'files_count': 100,
        'languages': {'JavaScript': 70, 'TypeScript': 30},
        'statistics': {
            'total_lines': 10000,
            'code_lines': 7500,
            'comment_lines': 1500,
            'blank_lines': 1000
        },
        'dependencies': {
            'npm': [
                {'name': 'react', 'version': '18.0.0'},
                {'name': 'express', 'version': '4.18.0'}
            ]
        },
        'documentation': ['README.md', 'LICENSE'],
        'api_docs': [{'name': 'REST API'}],
        'code_examples': [{'file': 'examples/app.js'}],
        'todos': [
            {'file': 'app.js', 'line': 10, 'type': 'TODO', 'comment': 'Error handling'},
            {'file': 'server.js', 'line': 20, 'type': 'FIXME', 'comment': 'Security issue'},
            {'file': 'routes.js', 'line': 30, 'type': 'TODO', 'comment': 'Optimization'}
        ],
        'license': 'MIT'
    }
    
    # Sample repo 3: Poorly documented project
    repo3 = {
        'name': 'DataProcessor',
        'path': '/projects/dataprocessor',
        'files_count': 50,
        'languages': {'Python': 45, 'Shell': 5},
        'statistics': {
            'total_lines': 5000,
            'code_lines': 4200,
            'comment_lines': 300,
            'blank_lines': 500
        },
        'dependencies': {
            'pip': [
                {'name': 'pandas', 'version': '1.5.0'}
            ]
        },
        'documentation': ['README.md'],
        'api_docs': [],
        'code_examples': [],
        'todos': [
            {'file': 'processor.py', 'line': 5, 'type': 'TODO', 'comment': 'Add tests'},
            {'file': 'processor.py', 'line': 15, 'type': 'TODO', 'comment': 'Add docs'},
            {'file': 'processor.py', 'line': 25, 'type': 'FIXME', 'comment': 'Memory leak'},
            {'file': 'processor.py', 'line': 35, 'type': 'TODO', 'comment': 'Refactor'},
            {'file': 'utils.py', 'line': 10, 'type': 'TODO', 'comment': 'Validate input'}
        ],
        'license': None
    }
    
    return [repo1, repo2, repo3]


def demo_basic_usage():
    """Demonstrate basic dashboard usage."""
    print("\n" + "=" * 80)
    print("DEMO 1: Basic Multi-Repository Dashboard Usage")
    print("=" * 80)
    
    # Create dashboard
    dashboard = MultiRepoDashboard()
    
    # Get sample repositories
    repos = create_sample_repos()
    
    # Add repositories
    print("\nAdding repositories to dashboard...")
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. Adding {repo['name']}...")
        dashboard.add_repository(repo)
    
    print(f"\n✓ Added {len(dashboard.repositories)} repositories")
    
    # Analyze consistency
    print("\nAnalyzing consistency across repositories...")
    gaps = dashboard.analyze_consistency()
    print(f"✓ Found {len(gaps)} consistency gaps")
    
    # Generate analytics
    print("\nGenerating organization-wide analytics...")
    analytics = dashboard.generate_analytics()
    print(f"✓ Analytics generated")
    
    # Display summary
    summary = analytics['summary']
    print("\n" + "-" * 80)
    print("SUMMARY STATISTICS")
    print("-" * 80)
    print(f"Documentation Coverage: {summary['documentation_coverage']['average']:.1f}%")
    print(f"  Range: {summary['documentation_coverage']['min']:.1f}% - {summary['documentation_coverage']['max']:.1f}%")
    print(f"Completeness Score: {summary['completeness_score']['average']:.1f}%")
    print(f"  Range: {summary['completeness_score']['min']:.1f}% - {summary['completeness_score']['max']:.1f}%")
    print(f"Style Compliance: {summary['style_compliance']['average']:.1f}%")
    
    # Show top consistency gaps
    if gaps:
        print("\n" + "-" * 80)
        print("TOP CONSISTENCY GAPS")
        print("-" * 80)
        critical_gaps = [g for g in gaps if g.severity == 'critical']
        high_gaps = [g for g in gaps if g.severity == 'high']
        
        for severity, gap_list in [('CRITICAL', critical_gaps), ('HIGH', high_gaps)]:
            if gap_list:
                print(f"\n{severity} Severity:")
                for gap in gap_list[:3]:  # Show top 3
                    print(f"  • {gap.description}")
                    print(f"    Affected: {', '.join(gap.affected_repos)}")
    
    return dashboard


def demo_style_guides():
    """Demonstrate different style guide configurations."""
    print("\n" + "=" * 80)
    print("DEMO 2: Different Style Guide Configurations")
    print("=" * 80)
    
    repos = create_sample_repos()
    
    style_guides = ['google', 'microsoft', 'plain']
    
    for style_guide in style_guides:
        print(f"\n--- {style_guide.upper()} Style Guide ---")
        
        config = DashboardConfig(style_guide=style_guide)
        dashboard = MultiRepoDashboard(config)
        
        # Add first repo only for quick demo
        dashboard.add_repository(repos[0])
        
        repo = dashboard.repositories[0]
        print(f"Style Guide: {repo.style_compliance['style_guide']}")
        print(f"Compliance: {repo.style_compliance['compliance_percentage']:.1f}%")


def demo_custom_thresholds():
    """Demonstrate custom threshold configuration."""
    print("\n" + "=" * 80)
    print("DEMO 3: Custom Threshold Configuration")
    print("=" * 80)
    
    # Create dashboard with custom thresholds
    config = DashboardConfig(
        min_doc_coverage=80.0,  # Higher threshold
        min_completeness_score=70.0,  # Higher threshold
        style_guide="microsoft"
    )
    
    dashboard = MultiRepoDashboard(config)
    
    # Add repositories
    repos = create_sample_repos()
    for repo in repos:
        dashboard.add_repository(repo)
    
    # Generate analytics
    analytics = dashboard.generate_analytics()
    summary = analytics['summary']
    
    print(f"\nConfiguration:")
    print(f"  Minimum Coverage Threshold: {config.min_doc_coverage}%")
    print(f"  Minimum Completeness Threshold: {config.min_completeness_score}%")
    print(f"  Style Guide: {config.style_guide}")
    
    print(f"\nRepositories Below Thresholds:")
    print(f"  Coverage: {summary['documentation_coverage']['below_threshold']}")
    print(f"  Completeness: {summary['completeness_score']['below_threshold']}")


def demo_report_formats():
    """Demonstrate different report formats."""
    print("\n" + "=" * 80)
    print("DEMO 4: Report Format Examples")
    print("=" * 80)
    
    dashboard = MultiRepoDashboard()
    repos = create_sample_repos()
    
    # Add only first two repos for cleaner output
    dashboard.add_repository(repos[0])
    dashboard.add_repository(repos[1])
    
    dashboard.analyze_consistency()
    dashboard.generate_analytics()
    
    # Text format (partial)
    print("\n--- TEXT FORMAT (excerpt) ---")
    text_report = dashboard.generate_report('text')
    lines = text_report.split('\n')[:30]  # First 30 lines
    print('\n'.join(lines))
    print("... (truncated)")
    
    # Markdown format (partial)
    print("\n--- MARKDOWN FORMAT (excerpt) ---")
    md_report = dashboard.generate_report('markdown')
    md_lines = md_report.split('\n')[:25]  # First 25 lines
    print('\n'.join(md_lines))
    print("... (truncated)")
    
    # JSON export info
    print("\n--- JSON FORMAT ---")
    json_data = dashboard.export_to_json()
    data = json.loads(json_data)
    print(f"JSON export contains {len(data.keys())} top-level keys:")
    for key in data.keys():
        print(f"  • {key}")


def demo_rankings():
    """Demonstrate repository rankings."""
    print("\n" + "=" * 80)
    print("DEMO 5: Repository Rankings")
    print("=" * 80)
    
    dashboard = MultiRepoDashboard()
    repos = create_sample_repos()
    
    for repo in repos:
        dashboard.add_repository(repo)
    
    analytics = dashboard.generate_analytics()
    rankings = analytics['rankings']
    
    print("\n--- Overall Ranking ---")
    for entry in rankings['overall']:
        print(f"  {entry['rank']}. {entry['name']}: {entry['score']:.1f}")
    
    print("\n--- By Documentation Coverage ---")
    for entry in rankings['by_coverage']:
        print(f"  {entry['rank']}. {entry['name']}: {entry['score']:.1f}%")
    
    print("\n--- By Completeness ---")
    for entry in rankings['by_completeness']:
        print(f"  {entry['rank']}. {entry['name']}: {entry['score']:.1f}%")


def demo_recommendations():
    """Demonstrate recommendation generation."""
    print("\n" + "=" * 80)
    print("DEMO 6: Organization-Wide Recommendations")
    print("=" * 80)
    
    dashboard = MultiRepoDashboard()
    repos = create_sample_repos()
    
    for repo in repos:
        dashboard.add_repository(repo)
    
    analytics = dashboard.generate_analytics()
    recommendations = analytics['recommendations']
    
    print(f"\nGenerated {len(recommendations)} recommendations:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}\n")


def demo_export():
    """Demonstrate exporting dashboard data."""
    print("\n" + "=" * 80)
    print("DEMO 7: Exporting Dashboard Data")
    print("=" * 80)
    
    dashboard = MultiRepoDashboard()
    repos = create_sample_repos()
    
    for repo in repos:
        dashboard.add_repository(repo)
    
    dashboard.analyze_consistency()
    dashboard.generate_analytics()
    
    # Export to JSON
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # JSON export
        json_path = os.path.join(tmpdir, 'dashboard.json')
        dashboard.export_to_json(json_path)
        size = os.path.getsize(json_path)
        print(f"\n✓ Exported to JSON: {json_path}")
        print(f"  File size: {size:,} bytes")
        
        # Text report
        text_path = os.path.join(tmpdir, 'dashboard.txt')
        report = dashboard.generate_report('text')
        with open(text_path, 'w') as f:
            f.write(report)
        size = os.path.getsize(text_path)
        print(f"\n✓ Exported to text: {text_path}")
        print(f"  File size: {size:,} bytes")
        
        # Markdown report
        md_path = os.path.join(tmpdir, 'dashboard.md')
        report = dashboard.generate_report('markdown')
        with open(md_path, 'w') as f:
            f.write(report)
        size = os.path.getsize(md_path)
        print(f"\n✓ Exported to markdown: {md_path}")
        print(f"  File size: {size:,} bytes")
        
        # HTML report
        html_path = os.path.join(tmpdir, 'dashboard.html')
        report = dashboard.generate_report('html')
        with open(html_path, 'w') as f:
            f.write(report)
        size = os.path.getsize(html_path)
        print(f"\n✓ Exported to HTML: {html_path}")
        print(f"  File size: {size:,} bytes")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("MULTI-REPOSITORY DOCUMENTATION CONSISTENCY DASHBOARD")
    print("Feature Demonstration")
    print("=" * 80)
    
    try:
        # Run demos
        demo_basic_usage()
        demo_style_guides()
        demo_custom_thresholds()
        demo_report_formats()
        demo_rankings()
        demo_recommendations()
        demo_export()
        
        print("\n" + "=" * 80)
        print("All demos completed successfully!")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("  ✓ Multi-repository analysis")
        print("  ✓ Documentation coverage tracking")
        print("  ✓ Completeness scoring")
        print("  ✓ Style guide compliance checking")
        print("  ✓ Consistency gap detection")
        print("  ✓ Organization-wide analytics")
        print("  ✓ Repository rankings")
        print("  ✓ Recommendation generation")
        print("  ✓ Multiple export formats (text, markdown, HTML, JSON)")
        print("  ✓ Configurable thresholds and style guides")
        print("\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during demo: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
