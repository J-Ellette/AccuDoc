#!/usr/bin/env python3
"""
Demo script for Complexity Analyzer feature.

This script demonstrates how to use the complexity analyzer to identify
complex code that needs better documentation.
"""

import tempfile
import shutil
from pathlib import Path
from accudoc.complexity_analyzer import ComplexityAnalyzer


def create_sample_repository():
    """Create a sample repository with various complexity levels."""
    test_dir = tempfile.mkdtemp()
    repo_path = Path(test_dir)
    
    # Create a simple module
    (repo_path / 'simple_module.py').write_text('''
"""A simple module with low complexity."""

def add(x, y):
    """Add two numbers."""
    return x + y

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

class Calculator:
    """A simple calculator."""
    
    def __init__(self):
        """Initialize calculator."""
        self.result = 0
    
    def calculate(self, operation, x, y):
        """Perform a calculation."""
        if operation == 'add':
            return x + y
        elif operation == 'subtract':
            return x - y
        elif operation == 'multiply':
            return x * y
        elif operation == 'divide':
            return x / y if y != 0 else 0
        else:
            return 0
''')
    
    # Create a complex module with undocumented functions
    (repo_path / 'complex_module.py').write_text('''
"""A complex module with high complexity functions."""

def process_data(data, options):
    # Complex function without documentation
    result = []
    
    if not data:
        return result
    
    for item in data:
        if item['type'] == 'A':
            if item['value'] > 100:
                result.append(item['value'] * 2)
            else:
                result.append(item['value'] + 10)
        elif item['type'] == 'B':
            if item['value'] < 50:
                result.append(item['value'] / 2)
            else:
                result.append(item['value'] - 20)
        elif item['type'] == 'C':
            if options.get('special'):
                result.append(item['value'] ** 2)
            else:
                result.append(item['value'])
    
    if options.get('sort'):
        result.sort()
    
    if options.get('reverse'):
        result.reverse()
    
    return result

def validate_input(user_input, rules):
    """Validate user input against rules."""
    errors = []
    
    if 'required' in rules and not user_input:
        errors.append("Input is required")
    
    if 'min_length' in rules and len(user_input) < rules['min_length']:
        errors.append(f"Minimum length is {rules['min_length']}")
    
    if 'max_length' in rules and len(user_input) > rules['max_length']:
        errors.append(f"Maximum length is {rules['max_length']}")
    
    if 'pattern' in rules:
        import re
        if not re.match(rules['pattern'], user_input):
            errors.append("Input does not match required pattern")
    
    if 'custom_validator' in rules:
        validator = rules['custom_validator']
        if not validator(user_input):
            errors.append("Custom validation failed")
    
    return errors

class DataProcessor:
    """Process data with various transformations."""
    
    def transform(self, data, transformations):
        result = data
        
        for transform in transformations:
            if transform['type'] == 'filter':
                result = [x for x in result if transform['condition'](x)]
            elif transform['type'] == 'map':
                result = [transform['function'](x) for x in result]
            elif transform['type'] == 'reduce':
                import functools
                result = functools.reduce(transform['function'], result)
            elif transform['type'] == 'sort':
                result = sorted(result, key=transform.get('key'))
        
        return result
''')
    
    # Create a JavaScript file
    (repo_path / 'complex_script.js').write_text('''
// Complex JavaScript with many control flows

function processUserData(userData, config) {
    let result = {};
    
    if (userData.name) {
        if (userData.name.length > 0) {
            result.name = userData.name.trim();
        }
    }
    
    if (userData.email) {
        if (userData.email.includes('@')) {
            result.email = userData.email.toLowerCase();
        }
    }
    
    if (config.validateAge) {
        if (userData.age) {
            if (userData.age >= 18) {
                result.age = userData.age;
            }
        }
    }
    
    for (let key in userData.preferences) {
        if (userData.preferences[key]) {
            result[key] = userData.preferences[key];
        }
    }
    
    return result;
}

class UserManager {
    constructor() {
        this.users = [];
    }
    
    addUser(user) {
        this.users.push(user);
    }
}
''')
    
    return repo_path


def demo_complexity_analysis():
    """Run a demonstration of complexity analysis."""
    print("=" * 70)
    print("AccuDoc Complexity Analyzer Demo")
    print("=" * 70)
    print()
    
    # Create sample repository
    print("Creating sample repository...")
    repo_path = create_sample_repository()
    
    try:
        # Analyze the repository
        print(f"Analyzing repository at: {repo_path}")
        print()
        
        analyzer = ComplexityAnalyzer(str(repo_path))
        analysis = analyzer.analyze_repository(['.py', '.js'])
        
        # Show summary
        print("Analysis Summary:")
        print("-" * 70)
        summary = analysis['summary']
        print(f"Total Files Analyzed: {summary['total_files']}")
        print(f"Total Functions: {summary['total_functions']}")
        print(f"Total Classes: {summary['total_classes']}")
        print(f"High Complexity Functions (>10): {len(summary['high_complexity_functions'])}")
        print(f"Undocumented Complex Functions: {len(summary['undocumented_complex_functions'])}")
        print()
        
        # Show high complexity functions
        if summary['high_complexity_functions']:
            print("High Complexity Functions:")
            print("-" * 70)
            for func in summary['high_complexity_functions']:
                print(f"  • {func['file']}:{func['line']}")
                print(f"    Function: {func['function']}")
                print(f"    Complexity: {func['complexity']}")
                print()
        
        # Show undocumented complex functions
        if summary['undocumented_complex_functions']:
            print("Undocumented Complex Functions (Need Documentation!):")
            print("-" * 70)
            for func in summary['undocumented_complex_functions']:
                print(f"  • {func['file']}:{func['line']}")
                print(f"    Function: {func['function']}")
                print(f"    Complexity: {func['complexity']}")
                print()
        
        # Show Python file details
        if analysis['python_files']:
            print("Python Files Analysis:")
            print("-" * 70)
            for file_analysis in analysis['python_files']:
                if 'error' in file_analysis:
                    continue
                
                print(f"File: {file_analysis['file']}")
                print(f"  Functions: {file_analysis['total_functions']}")
                print(f"  Classes: {file_analysis['total_classes']}")
                print(f"  Complex Functions: {len(file_analysis.get('complex_functions', []))}")
                print(f"  Undocumented Complex: {len(file_analysis.get('undocumented_functions', []))}")
                print()
        
        # Generate and display report
        print("Generating Full Report:")
        print("=" * 70)
        report = analyzer.generate_report(analysis)
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
    demo_complexity_analysis()
