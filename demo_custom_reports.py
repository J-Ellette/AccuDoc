#!/usr/bin/env python3
"""
Demo script for custom reports feature.
Shows how to create and use custom report templates.
"""

from accudoc.scanner import RepositoryScanner
from accudoc.custom_reports import (
    CustomReportGenerator, ReportTemplate, create_sample_template
)
import os
import json


def demo_custom_reports():
    """Demonstrate custom reports feature."""
    print("=" * 70)
    print("AccuDoc - Custom Reports Demo")
    print("=" * 70)
    print()
    
    # Scan current repository
    print("Step 1: Scanning repository...")
    scanner = RepositoryScanner('.')
    repo_info = scanner.scan()
    print("✓ Repository scanned")
    print()
    
    # Create generator
    generator = CustomReportGenerator(repo_info)
    
    # List built-in templates
    print("Step 2: Available built-in templates")
    print("-" * 70)
    templates = generator.list_builtin_templates()
    for tmpl in templates:
        print(f"\n{tmpl['name']}: {tmpl['title']}")
        print(f"  {tmpl['description']}")
    print()
    
    # Generate minimal report
    print("=" * 70)
    print("Step 3: Generating Minimal Report")
    print("=" * 70)
    print()
    template = generator.get_builtin_template('minimal')
    report = generator.generate(template)
    print(report[:500])  # Show first 500 chars
    print("\n... (truncated)")
    print()
    
    # Generate executive summary
    print("=" * 70)
    print("Step 4: Generating Executive Summary")
    print("=" * 70)
    print()
    template = generator.get_builtin_template('executive')
    report = generator.generate(template)
    print(report[:500])
    print("\n... (truncated)")
    print()
    
    # Create custom template
    print("=" * 70)
    print("Step 5: Creating Custom Template")
    print("=" * 70)
    print()
    
    custom_template_data = {
        'name': 'Custom Demo Report',
        'description': 'A custom report for demonstration',
        'format': 'markdown',
        'sections': [
            {
                'title': 'Quick Facts',
                'content': 'Repository: {name}\nFiles: {files_count}\nLicense: {license}'
            },
            {
                'title': 'Languages Used',
                'data': ['languages']
            },
            {
                'title': 'Code Metrics',
                'data': ['statistics.total_lines', 'statistics.code_lines', 'statistics.comment_lines']
            }
        ]
    }
    
    custom_template = ReportTemplate(custom_template_data)
    
    # Validate template
    errors = custom_template.validate()
    if errors:
        print("Template validation errors:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("✓ Template validation passed")
    print()
    
    # Generate custom report
    print("Generating custom report...")
    custom_report = generator.generate(custom_template)
    print()
    print(custom_report)
    print()
    
    # Save outputs
    print("=" * 70)
    print("Step 6: Saving Outputs")
    print("=" * 70)
    print()
    
    # Save minimal report
    minimal_template = generator.get_builtin_template('minimal')
    minimal_report = generator.generate(minimal_template)
    minimal_file = '/tmp/minimal_report.md'
    with open(minimal_file, 'w', encoding='utf-8') as f:
        f.write(minimal_report)
    print(f"✓ Minimal report saved to: {minimal_file}")
    
    # Save executive summary
    exec_template = generator.get_builtin_template('executive')
    exec_report = generator.generate(exec_template)
    exec_file = '/tmp/executive_summary.md'
    with open(exec_file, 'w', encoding='utf-8') as f:
        f.write(exec_report)
    print(f"✓ Executive summary saved to: {exec_file}")
    
    # Save custom template
    template_file = '/tmp/custom_template.json'
    with open(template_file, 'w') as f:
        json.dump(custom_template_data, f, indent=2)
    print(f"✓ Custom template saved to: {template_file}")
    
    # Save custom report
    custom_file = '/tmp/custom_report.md'
    with open(custom_file, 'w', encoding='utf-8') as f:
        f.write(custom_report)
    print(f"✓ Custom report saved to: {custom_file}")
    print()
    
    # Create sample templates
    print("=" * 70)
    print("Step 7: Creating Sample Templates")
    print("=" * 70)
    print()
    
    basic_sample = create_sample_template('basic')
    basic_file = '/tmp/basic_template.json'
    with open(basic_file, 'w') as f:
        json.dump(basic_sample, f, indent=2)
    print(f"✓ Basic sample template created: {basic_file}")
    
    comprehensive_sample = create_sample_template('comprehensive')
    comp_file = '/tmp/comprehensive_template.json'
    with open(comp_file, 'w') as f:
        json.dump(comprehensive_sample, f, indent=2)
    print(f"✓ Comprehensive sample template created: {comp_file}")
    print()
    
    # Show CLI examples
    print("=" * 70)
    print("CLI Usage Examples")
    print("=" * 70)
    print()
    print("# List available built-in templates")
    print("python accudoc_cli.py custom-report /path/to/repo --list")
    print()
    print("# Generate report with built-in template")
    print("python accudoc_cli.py custom-report /path/to/repo -b minimal")
    print("python accudoc_cli.py custom-report /path/to/repo -b executive -o summary.md")
    print()
    print("# Create sample template")
    print("python accudoc_cli.py custom-report . --create-sample basic -o my_template.json")
    print()
    print("# Use custom template")
    print("python accudoc_cli.py custom-report /path/to/repo -t my_template.json -o report.md")
    print()
    print("# Generate from existing scan")
    print("python accudoc_cli.py custom-report scan.json -b detailed -o detailed_report.md")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Custom Reports Features:")
    print()
    print("• User-defined report templates using JSON")
    print("• 4 built-in templates:")
    print("  - minimal: Essential information only")
    print("  - detailed: Comprehensive analysis")
    print("  - executive: High-level summary for stakeholders")
    print("  - technical: In-depth technical details")
    print()
    print("• Template sections support:")
    print("  - Static content with variable substitution {name}, {files_count}")
    print("  - Dynamic data fields from repository info")
    print("  - Nested data access using dot notation (statistics.total_lines)")
    print()
    print("• Multiple output formats:")
    print("  - Markdown (default)")
    print("  - HTML")
    print("  - Plain text")
    print()
    print("• Template validation to ensure correctness")
    print("• Sample templates to get started quickly")
    print()


if __name__ == '__main__':
    demo_custom_reports()
