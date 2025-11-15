#!/usr/bin/env python3
"""
Demo script for comparison reports feature.
Shows how to compare multiple repositories.
"""

from accudoc.comparison_reports import RepositoryComparison
from accudoc.scanner import RepositoryScanner
import os
import json
import tempfile


def demo_comparison_reports():
    """Demonstrate comparison reports feature."""
    print("=" * 70)
    print("AccuDoc - Comparison Reports Demo")
    print("=" * 70)
    print()
    
    # Create comparison
    print("Step 1: Creating comparison of current repository with itself")
    print("(In real use, you would scan different repositories)")
    print()
    
    comparison = RepositoryComparison()
    
    # Scan current repository
    print("Scanning repository...")
    scanner = RepositoryScanner('.')
    repo_info = scanner.scan()
    
    # Add it twice with different names for demo purposes
    comparison.add_repository(repo_info, name='AccuDoc (Current)')
    
    # Create a modified version for comparison
    repo_info_modified = repo_info.copy()
    repo_info_modified['files_count'] = int(repo_info.get('files_count', 0) * 0.8)
    if 'statistics' in repo_info_modified:
        stats = repo_info_modified['statistics'].copy()
        stats['total_lines'] = int(stats.get('total_lines', 0) * 0.7)
        repo_info_modified['statistics'] = stats
    
    comparison.add_repository(repo_info_modified, name='AccuDoc (Modified)')
    
    print("✓ Added 2 repositories for comparison")
    print()
    
    # Perform comparison
    print("Step 2: Performing comparison...")
    comparison.compare()
    print("✓ Comparison complete")
    print()
    
    # Display text report
    print("Step 3: Generating comparison report")
    print()
    report = comparison.generate_report()
    print(report)
    
    # Show JSON export preview
    print()
    print("=" * 70)
    print("JSON Export Preview")
    print("=" * 70)
    print()
    
    data = comparison.export_to_json()
    
    print("Comparison Summary:")
    print(f"  Repositories Compared: {data['repository_count']}")
    print(f"  Repository Names: {', '.join(data['repository_names'])}")
    print()
    
    if 'summary' in data:
        summary = data['summary']
        if 'best_performers' in summary:
            print("Best Performers:")
            for category, name in summary['best_performers'].items():
                print(f"  • {category.replace('_', ' ').title()}: {name}")
    print()
    
    # Save outputs
    print("=" * 70)
    print("Saving Outputs")
    print("=" * 70)
    print()
    
    # Save text report
    text_file = '/tmp/comparison_report.txt'
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ Text report saved to: {text_file}")
    
    # Save JSON export
    json_file = '/tmp/comparison_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✓ JSON data saved to: {json_file}")
    
    # Save CSV export
    csv_dir = '/tmp/comparison_export'
    csv_files = comparison.export_to_csv(csv_dir)
    print(f"✓ CSV data exported to: {csv_dir}")
    print(f"  Created {len(csv_files)} files")
    print()
    
    # Show CLI examples
    print("=" * 70)
    print("CLI Usage Examples")
    print("=" * 70)
    print()
    print("# Compare two repositories (scan on the fly)")
    print("python accudoc_cli.py compare /path/to/repo1 /path/to/repo2")
    print()
    print("# Compare using existing scan files")
    print("python accudoc_cli.py compare scan1.json scan2.json scan3.json")
    print()
    print("# Save comparison to file")
    print("python accudoc_cli.py compare repo1 repo2 -o comparison.txt")
    print()
    print("# Export as JSON")
    print("python accudoc_cli.py compare repo1 repo2 -o comparison.json -f json")
    print()
    print("# Export to CSV")
    print("python accudoc_cli.py compare repo1 repo2 -o ./compare_data -f csv")
    print()
    print("# Use custom names")
    print("python accudoc_cli.py compare repo1 repo2 -n ProjectA ProjectB")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Comparison Reports Features:")
    print()
    print("• Compare multiple repositories side-by-side")
    print("• Metrics compared:")
    print("  - File counts and language distribution")
    print("  - Code statistics (lines, comments, ratios)")
    print("  - Dependencies and package managers")
    print("  - Documentation coverage")
    print("  - TODO/FIXME items")
    print("  - Health scores (if available)")
    print()
    print("• Automatic rankings:")
    print("  - By file count")
    print("  - By code lines")
    print("  - By documentation coverage")
    print("  - By health score")
    print()
    print("• Summary of best/worst performers")
    print("• Multiple output formats: text report, JSON, CSV")
    print("• Works with live repository scans or existing JSON files")
    print()


if __name__ == '__main__':
    demo_comparison_reports()
