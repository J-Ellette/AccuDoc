#!/usr/bin/env python3
"""
Demo script for health dashboard feature.
Shows how to generate and view project health metrics.
"""

from accudoc.scanner import RepositoryScanner
from accudoc.health_dashboard import HealthDashboard
import os


def demo_health_dashboard():
    """Demonstrate health dashboard feature."""
    print("=" * 70)
    print("AccuDoc - Project Health Dashboard Demo")
    print("=" * 70)
    print()
    
    # Scan current repository
    print("Step 1: Scanning repository...")
    scanner = RepositoryScanner('.')
    repo_info = scanner.scan()
    print(f"✓ Scanned: {repo_info.get('name', 'AccuDoc')}")
    print()
    
    # Create dashboard
    print("Step 2: Generating health dashboard...")
    dashboard = HealthDashboard(repo_info)
    print("✓ Dashboard created")
    print()
    
    # Display text dashboard
    print("Step 3: Displaying health dashboard")
    print()
    text_output = dashboard.generate_text_dashboard()
    print(text_output)
    
    # Show JSON export
    print()
    print("=" * 70)
    print("JSON Export Preview")
    print("=" * 70)
    print()
    
    data = dashboard.export_to_dict()
    summary = data['summary']
    
    print("Overall Health Metrics:")
    print(f"  Overall Score: {summary['overall_score']}/100 ({summary['overall_grade']})")
    print(f"  Status: {summary['overall_status']}")
    print()
    print("Component Scores:")
    print(f"  Documentation Coverage: {summary['documentation']}/100")
    print(f"  Code Quality: {summary['code_quality']}/100")
    print(f"  Dependency Health: {summary['dependencies']}/100")
    print(f"  Maintainability: {summary['maintainability']}/100")
    print(f"  License Compliance: {summary['license']}/100")
    print()
    
    # Save outputs
    print("=" * 70)
    print("Saving Outputs")
    print("=" * 70)
    print()
    
    # Save text dashboard
    text_file = '/tmp/health_dashboard.txt'
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text_output)
    print(f"✓ Text dashboard saved to: {text_file}")
    
    # Save JSON export
    import json
    json_file = '/tmp/health_dashboard.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✓ JSON data saved to: {json_file}")
    print()
    
    # Show CLI examples
    print("=" * 70)
    print("CLI Usage Examples")
    print("=" * 70)
    print()
    print("# Display health dashboard in terminal")
    print("python accudoc_cli.py health /path/to/repo")
    print()
    print("# Save health dashboard to file")
    print("python accudoc_cli.py health /path/to/repo -o dashboard.txt")
    print()
    print("# Export as JSON")
    print("python accudoc_cli.py health /path/to/repo -o dashboard.json -f json")
    print()
    print("# Use existing scan results")
    print("python accudoc_cli.py health scan.json")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Health Metrics Explained:")
    print()
    print("• Documentation Coverage: Measures presence of README, API docs,")
    print("  code examples, and other documentation files")
    print()
    print("• Code Quality: Evaluates TODO/FIXME items, code complexity,")
    print("  best practices violations, and test coverage")
    print()
    print("• Dependency Health: Assesses number of dependencies and checks")
    print("  for outdated or vulnerable packages")
    print()
    print("• Maintainability Index: Considers comment ratio, configuration")
    print("  files, and repository size")
    print()
    print("• License Compliance: Checks for license file and potential")
    print("  compliance issues")
    print()
    print("• Overall Health: Weighted average of all metrics")
    print("  (Doc 25%, Quality 30%, Deps 20%, Maint 15%, License 10%)")
    print()


if __name__ == '__main__':
    demo_health_dashboard()
