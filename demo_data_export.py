#!/usr/bin/env python3
"""
Demo script for data export feature.
Shows how to export repository analysis data to CSV and JSON formats.
"""

from accudoc.scanner import RepositoryScanner
from accudoc.data_export import DataExporter
import os
import shutil


def demo_data_export():
    """Demonstrate data export feature."""
    print("=" * 70)
    print("AccuDoc - Data Export Demo")
    print("=" * 70)
    print()
    
    # Scan current repository
    print("Step 1: Scanning repository...")
    scanner = RepositoryScanner('.')
    repo_info = scanner.scan()
    print(f"✓ Scanned: {repo_info.get('name', 'AccuDoc')}")
    print(f"  - Files: {repo_info.get('files_count', 0)}")
    print(f"  - Languages: {len(repo_info.get('languages', {}))}")
    print(f"  - Dependencies: {sum(len(v) if isinstance(v, list) else 0 for v in repo_info.get('dependencies', {}).values())}")
    print()
    
    # Create exporter
    exporter = DataExporter(repo_info)
    
    # Create output directory
    output_dir = 'data_export_demo'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Export all CSV reports
    print("Step 2: Exporting all CSV reports...")
    csv_files = exporter.export_to_csv(output_dir, report_type='all')
    print(f"✓ Created {len(csv_files)} CSV files:")
    for file_path in csv_files:
        print(f"  • {file_path}")
    print()
    
    # Export summary CSV
    print("Step 3: Exporting summary CSV...")
    summary_file = os.path.join(output_dir, 'summary.csv')
    exporter.export_summary_csv(summary_file)
    print(f"✓ Created summary: {summary_file}")
    print()
    
    # Export to JSON
    print("Step 4: Exporting to JSON...")
    json_file = os.path.join(output_dir, 'repo_data.json')
    exporter.export_to_json(json_file)
    print(f"✓ Created JSON: {json_file}")
    print()
    
    # Show sample data from summary
    print("=" * 70)
    print("Sample Data - Summary CSV")
    print("=" * 70)
    print()
    
    import csv
    with open(summary_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        print(f"{'Category':<20} {'Metric':<30} {'Value':<20}")
        print("-" * 70)
        for row in list(reader)[:10]:
            print(f"{row['Category']:<20} {row['Metric']:<30} {row['Value']:<20}")
    print()
    
    # Show sample data from languages
    print("=" * 70)
    print("Sample Data - Languages CSV")
    print("=" * 70)
    print()
    
    langs_file = os.path.join(output_dir, 'languages.csv')
    if os.path.exists(langs_file):
        with open(langs_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            print(f"{'Language':<15} {'Files':<10} {'Percentage':<15} {'Lines':<10}")
            print("-" * 70)
            for row in reader:
                print(f"{row['Language']:<15} {row['File Count']:<10} {row['Percentage']:<15} {row['Lines of Code']:<10}")
    print()
    
    # Show export types
    print("=" * 70)
    print("Available Export Types")
    print("=" * 70)
    print()
    print("CSV Reports:")
    print("  - all         : All available reports")
    print("  - files       : File statistics by language")
    print("  - dependencies: List of dependencies with versions")
    print("  - todos       : TODO/FIXME comments")
    print("  - metrics     : Code metrics (lines, comments, etc.)")
    print("  - languages   : Language breakdown with percentages")
    print()
    print("Other Formats:")
    print("  - summary     : Single CSV with key metrics")
    print("  - json        : Complete repository data in JSON format")
    print()
    
    # Show CLI examples
    print("=" * 70)
    print("CLI Usage Examples")
    print("=" * 70)
    print()
    print("# Export all CSV reports")
    print("python accudoc_cli.py data-export /path/to/repo -o ./exports -f csv -r all")
    print()
    print("# Export only dependencies")
    print("python accudoc_cli.py data-export /path/to/repo -o ./exports -f csv -r dependencies")
    print()
    print("# Export summary CSV")
    print("python accudoc_cli.py data-export /path/to/repo -o summary.csv -f summary")
    print()
    print("# Export to JSON")
    print("python accudoc_cli.py data-export /path/to/repo -o data.json -f json")
    print()
    print("# Use existing scan results")
    print("python accudoc_cli.py data-export scan.json -o ./exports -f csv")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print(f"All exported files are in the '{output_dir}' directory.")
    print()


if __name__ == '__main__':
    demo_data_export()
