#!/usr/bin/env python3
"""
Demo script for Best Practices Checker feature.

This script demonstrates how to use the best practices checker to identify
coding standards violations and get recommendations for improvement.
"""

import tempfile
import shutil
from pathlib import Path
from accudoc.best_practices import BestPracticesChecker


def create_sample_repository():
    """Create a sample repository with various code quality issues."""
    test_dir = tempfile.mkdtemp()
    repo_path = Path(test_dir)
    
    # Create a file with good practices
    (repo_path / 'good_code.py').write_text('''
"""A well-written module following best practices."""

import logging

logger = logging.getLogger(__name__)


def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
        
    Returns:
        float: The average value
        
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    return sum(numbers) / len(numbers)


class DataProcessor:
    """Process and transform data with various operations."""
    
    def __init__(self, data=None):
        """
        Initialize the data processor.
        
        Args:
            data: Optional initial data
        """
        self.data = data if data is not None else []
    
    def process(self, transformer):
        """
        Apply a transformation to the data.
        
        Args:
            transformer: Function to apply to each item
            
        Returns:
            list: Transformed data
        """
        try:
            return [transformer(item) for item in self.data]
        except TypeError as e:
            logger.error(f"Error processing data: {e}")
            raise
''')
    
    # Create a file with bad practices
    (repo_path / 'bad_code.py').write_text('''
def process_user_data(username, email, age, address, phone, preferences, settings, metadata):
    try:
        result = []
        for item in [username, email, age, address, phone, preferences, settings, metadata]:
            if item:
                result.append(str(item))
        return ','.join(result)
    except:
        return None

def dangerous_function(items=[]):
    items.append(1)
    return items

class HugeClass:
    def method1(self): return 1
    def method2(self): return 2
    def method3(self): return 3
    def method4(self): return 4
    def method5(self): return 5
    def method6(self): return 6
    def method7(self): return 7
    def method8(self): return 8
    def method9(self): return 9
    def method10(self): return 10
    def method11(self): return 11
    def method12(self): return 12
    def method13(self): return 13
    def method14(self): return 14
    def method15(self): return 15
    def method16(self): return 16
    def method17(self): return 17
    def method18(self): return 18
    def method19(self): return 19
    def method20(self): return 20
    def method21(self): return 21
    def method22(self): return 22

def calculate_score(a, b, c):
    magic_value = 42
    multiplier = 3.14159
    threshold = 87
    bonus = 123
    penalty = 456
    
    if a > threshold:
        score = a * multiplier + bonus
    else:
        score = a * multiplier - penalty
    
    return score + magic_value
''')
    
    # Create a file with mixed quality
    (repo_path / 'mixed_code.py').write_text('''
"""This module has mixed code quality."""

def good_function():
    """A well-documented simple function."""
    return True

def bad_function(x, y, z, a, b, c, d):
    result = 0
    try:
        for i in range(100):
            if i > 50:
                result += i * 2
            else:
                result += i
        
        if x > 10:
            result *= x
        
        if y > 20:
            result *= y
        
        if z > 30:
            result *= z
    except Exception:
        pass
    
    return result
''')
    
    return repo_path


def demo_best_practices_check():
    """Run a demonstration of best practices checking."""
    print("=" * 70)
    print("AccuDoc Best Practices Checker Demo")
    print("=" * 70)
    print()
    
    # Create sample repository
    print("Creating sample repository with various code quality issues...")
    repo_path = create_sample_repository()
    
    try:
        # Check the repository
        print(f"Checking repository at: {repo_path}")
        print()
        
        checker = BestPracticesChecker(str(repo_path))
        results = checker.check_repository(['.py'])
        
        # Show summary
        print("Check Summary:")
        print("-" * 70)
        summary = results['summary']
        print(f"Total Files Checked: {summary['total_files']}")
        print(f"Files with Violations: {summary['files_with_violations']}")
        print(f"Total Violations: {summary['total_violations']}")
        print(f"  High Severity: {summary['severity_counts']['high']}")
        print(f"  Medium Severity: {summary['severity_counts']['medium']}")
        print(f"  Low Severity: {summary['severity_counts']['low']}")
        print()
        
        # Show violation types
        if summary['violation_types']:
            print("Violation Types:")
            print("-" * 70)
            sorted_types = sorted(summary['violation_types'].items(), 
                                 key=lambda x: x[1], reverse=True)
            for vtype, count in sorted_types:
                print(f"  {vtype.replace('_', ' ').title()}: {count}")
            print()
        
        # Show file-by-file results
        print("File Analysis:")
        print("-" * 70)
        for file_result in results['files']:
            print(f"\nFile: {file_result['file']}")
            print(f"  Total Violations: {file_result.get('total_violations', 0)}")
            
            if file_result.get('total_violations', 0) > 0:
                sc = file_result.get('severity_counts', {})
                print(f"  High: {sc.get('high', 0)}, "
                      f"Medium: {sc.get('medium', 0)}, "
                      f"Low: {sc.get('low', 0)}")
                
                # Show first few violations
                violations = file_result.get('violations', [])[:3]
                for v in violations:
                    print(f"    Line {v['line']}: [{v['severity'].upper()}] {v['message']}")
                
                if len(file_result.get('violations', [])) > 3:
                    print(f"    ... and {len(file_result['violations']) - 3} more")
        
        print()
        
        # Generate and display full report
        print("Generating Full Report:")
        print("=" * 70)
        report = checker.generate_report(results)
        print(report)
        
    finally:
        # Cleanup
        print()
        print(f"Cleaning up temporary directory: {repo_path}")
        shutil.rmtree(repo_path)
    
    print()
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == '__main__':
    demo_best_practices_check()
