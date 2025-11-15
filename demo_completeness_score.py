#!/usr/bin/env python3
"""
Demo script for Documentation Completeness Score feature.

This script demonstrates how to calculate a completeness score for
repository documentation and identify gaps.
"""

import tempfile
import shutil
from pathlib import Path
from accudoc.completeness_score import CompletenessScorer


def create_sample_repositories():
    """Create sample repositories with different documentation levels."""
    repos = {}
    
    # Repository 1: Poorly documented
    print("Creating poorly documented repository...")
    poor_dir = tempfile.mkdtemp()
    poor_path = Path(poor_dir)
    
    (poor_path / 'main.py').write_text('''
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add(self, item):
        self.data.append(item)
''')
    
    (poor_path / 'utils.py').write_text('''
def helper1(x):
    return x + 1

def helper2(y):
    return y * 2
''')
    
    repos['poor'] = poor_path
    
    # Repository 2: Well documented
    print("Creating well-documented repository...")
    good_dir = tempfile.mkdtemp()
    good_path = Path(good_dir)
    
    (good_path / 'README.md').write_text('''
# Awesome Project

A comprehensive example of well-documented code.

## Installation

```bash
pip install awesome-project
```

## Usage

```python
from awesome import Project
project = Project()
project.run()
```

## Features

- Feature 1: Does amazing things
- Feature 2: Does more amazing things
- Feature 3: Documentation everywhere!

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## License

MIT License - see LICENSE file for details.
''')
    
    (good_path / 'LICENSE').write_text('MIT License\n\nCopyright (c) 2024\n\nPermission is hereby granted...')
    
    (good_path / 'CONTRIBUTING.md').write_text('''
# Contributing to Awesome Project

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
''')
    
    (good_path / 'CHANGELOG.md').write_text('''
# Changelog

## [1.0.0] - 2024-01-01
### Added
- Initial release
- Basic features
''')
    
    (good_path / 'main.py').write_text('''
"""Main module for the awesome project."""

class Project:
    """Main project class that does awesome things."""
    
    def __init__(self):
        """Initialize the project."""
        self.data = []
    
    def run(self):
        """Run the main project logic."""
        print("Running awesome project!")
    
    def process(self, data):
        """
        Process input data.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
        """
        return [x * 2 for x in data if x > 0]

def main():
    """Main entry point for the application."""
    project = Project()
    project.run()

if __name__ == '__main__':
    main()
''')
    
    (good_path / 'example.py').write_text('''
"""Example usage of the awesome project."""

from main import Project

def demo():
    """Demonstrate basic usage."""
    project = Project()
    result = project.process([1, 2, 3])
    print(f"Result: {result}")

if __name__ == '__main__':
    demo()
''')
    
    (good_path / 'demo.py').write_text('''
"""Demo script for the awesome project."""

from main import Project

def run_demo():
    """Run a complete demo."""
    print("Starting demo...")
    project = Project()
    project.run()
    print("Demo complete!")

if __name__ == '__main__':
    run_demo()
''')
    
    repos['good'] = good_path
    
    return repos


def analyze_repository(name, path):
    """Analyze a repository and print results."""
    print("=" * 70)
    print(f"Analyzing: {name}")
    print("=" * 70)
    print()
    
    scorer = CompletenessScorer(str(path))
    results = scorer.analyze_repository()
    
    # Show quick stats
    print(f"Overall Score: {results['overall_score']}/100")
    print(f"Grade: {results['grade']}")
    print()
    
    # Show category breakdown
    print("Category Scores:")
    print("-" * 70)
    for category, data in results['scores'].items():
        score = data.get('score', 0)
        status = '✅' if score >= 70 else ('⚠️' if score >= 50 else '❌')
        category_name = category.replace('_', ' ').title()
        print(f"  {status} {category_name:30s} {score:6.1f}%")
    print()
    
    # Show critical gaps
    critical_gaps = [g for g in results['gaps'] if g['severity'] == 'critical']
    if critical_gaps:
        print("Critical Gaps:")
        print("-" * 70)
        for gap in critical_gaps:
            print(f"  ❌ {gap['category']}: {gap['message']}")
        print()
    
    # Show summary
    summary = results['summary']
    print("Summary:")
    print("-" * 70)
    print(f"  Total Files: {summary['total_files_analyzed']}")
    print(f"  Critical Gaps: {summary['missing_critical']}")
    print(f"  Important Gaps: {summary['missing_important']}")
    print(f"  Optional Gaps: {summary['missing_optional']}")
    print()
    
    return results


def demo_completeness_scoring():
    """Run a demonstration of completeness scoring."""
    print("=" * 70)
    print("AccuDoc Documentation Completeness Scorer Demo")
    print("=" * 70)
    print()
    
    # Create sample repositories
    print("Creating sample repositories...")
    repos = create_sample_repositories()
    print()
    
    try:
        # Analyze poorly documented repo
        poor_results = analyze_repository("Poorly Documented Repository", repos['poor'])
        
        # Analyze well documented repo
        good_results = analyze_repository("Well-Documented Repository", repos['good'])
        
        # Generate comparison
        print("=" * 70)
        print("Comparison")
        print("=" * 70)
        print()
        print(f"Poor Documentation:  {poor_results['overall_score']:6.1f}% (Grade: {poor_results['grade']})")
        print(f"Good Documentation:  {good_results['overall_score']:6.1f}% (Grade: {good_results['grade']})")
        print()
        improvement = good_results['overall_score'] - poor_results['overall_score']
        print(f"Improvement: +{improvement:.1f} percentage points")
        print()
        
        # Show full report for the good repo
        print("=" * 70)
        print("Full Report for Well-Documented Repository")
        print("=" * 70)
        print()
        
        scorer = CompletenessScorer(str(repos['good']))
        report = scorer.generate_report(good_results)
        print(report)
        
    finally:
        # Cleanup
        print()
        print("Cleaning up temporary directories...")
        for path in repos.values():
            shutil.rmtree(path)
    
    print()
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("- Well-documented projects score significantly higher")
    print("- README, LICENSE, and code docstrings are critical")
    print("- Examples and CONTRIBUTING files add polish")
    print("- Regular documentation reviews maintain quality")


if __name__ == '__main__':
    demo_completeness_scoring()
