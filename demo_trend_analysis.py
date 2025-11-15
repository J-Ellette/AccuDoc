#!/usr/bin/env python3
"""
Demo script for trend analysis feature.
Shows how to analyze repository trends over time.
"""

from accudoc.trend_analysis import TrendAnalyzer
import os


def demo_trend_analysis():
    """Demonstrate trend analysis feature."""
    print("=" * 70)
    print("AccuDoc - Trend Analysis Demo")
    print("=" * 70)
    print()
    
    # Analyze current repository
    print("Step 1: Analyzing repository trends...")
    analyzer = TrendAnalyzer('.')
    
    # Analyze over last month with 5 data points
    print("Period: Last month")
    print("Data points: 5")
    print()
    
    trends = analyzer.analyze(period='month', intervals=5)
    print("✓ Analysis complete")
    print()
    
    # Display text report
    print("Step 2: Generating trend report")
    print()
    report = analyzer.generate_report()
    print(report)
    
    # Show JSON export preview
    print()
    print("=" * 70)
    print("JSON Export Preview")
    print("=" * 70)
    print()
    
    data = analyzer.export_to_json()
    summary = data['summary']
    
    print("Summary Statistics:")
    print(f"  Period: {summary['period']}")
    print(f"  Total Commits: {summary['total_commits']}")
    print(f"  Total Files: {summary['total_files']}")
    print(f"  Total Contributors: {summary['total_contributors']}")
    print(f"  Lines Added: {summary['total_lines_added']:,}")
    print(f"  Lines Deleted: {summary['total_lines_deleted']:,}")
    print()
    
    if 'top_languages' in summary:
        print("Top Languages:")
        for lang, count in summary['top_languages'].items():
            print(f"  {lang}: {count} files")
    print()
    
    # Show growth rates
    print("Growth Rates:")
    growth = data['growth_rates']
    for metric, rate in growth.items():
        print(f"  {metric.replace('_', ' ').title()}: {rate:+.1f}%")
    print()
    
    # Save outputs
    print("=" * 70)
    print("Saving Outputs")
    print("=" * 70)
    print()
    
    # Save text report
    text_file = '/tmp/trend_report.txt'
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ Text report saved to: {text_file}")
    
    # Save JSON export
    import json
    json_file = '/tmp/trend_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✓ JSON data saved to: {json_file}")
    
    # Save CSV export
    csv_dir = '/tmp/trend_export'
    csv_files = analyzer.export_to_csv(csv_dir)
    print(f"✓ CSV data exported to: {csv_dir}")
    print(f"  Created {len(csv_files)} files")
    print()
    
    # Show CLI examples
    print("=" * 70)
    print("CLI Usage Examples")
    print("=" * 70)
    print()
    print("# Analyze trends over last month (default: text output)")
    print("python accudoc_cli.py trends /path/to/repo -p month")
    print()
    print("# Analyze with custom intervals")
    print("python accudoc_cli.py trends /path/to/repo -p quarter -i 12")
    print()
    print("# Save report to file")
    print("python accudoc_cli.py trends /path/to/repo -o trends.txt")
    print()
    print("# Export as JSON")
    print("python accudoc_cli.py trends /path/to/repo -o trends.json -f json")
    print()
    print("# Export to CSV")
    print("python accudoc_cli.py trends /path/to/repo -o ./trends_data -f csv")
    print()
    print("# Analyze all history")
    print("python accudoc_cli.py trends /path/to/repo -p all -i 20")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Trend Analysis Features:")
    print()
    print("• Tracks repository growth over time using git history")
    print("• Collects metrics at multiple time points:")
    print("  - Commit count")
    print("  - File count")
    print("  - Contributor count")
    print("  - Lines added/deleted")
    print("  - Language distribution")
    print()
    print("• Calculates growth rates between first and last data points")
    print("• Supports multiple time periods:")
    print("  - week: Last 7 days")
    print("  - month: Last 30 days")
    print("  - quarter: Last 90 days")
    print("  - year: Last 365 days")
    print("  - all: Entire repository history")
    print()
    print("• Customizable number of data points (intervals)")
    print("• Multiple output formats: text report, JSON, CSV")
    print()


if __name__ == '__main__':
    demo_trend_analysis()
