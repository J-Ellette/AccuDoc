#!/usr/bin/env python3
"""
Demo script for Call Graph Generator feature.

This script demonstrates how to generate call graphs showing function
relationships and dependencies in code.
"""

import tempfile
import shutil
from pathlib import Path
from accudoc.call_graph import CallGraphGenerator


def create_sample_repository():
    """Create a sample repository with various function relationships."""
    test_dir = tempfile.mkdtemp()
    repo_path = Path(test_dir)
    
    # Create a utilities module
    (repo_path / 'utils.py').write_text('''
"""Utility functions module."""

def validate_input(value):
    """Validate input value."""
    if value is None:
        raise ValueError("Value cannot be None")
    return True

def format_output(data):
    """Format data for output."""
    return str(data)

def log_message(message):
    """Log a message."""
    print(f"[LOG] {message}")
''')
    
    # Create a data processing module
    (repo_path / 'processor.py').write_text('''
"""Data processing module."""

def read_data(source):
    """Read data from source."""
    return [1, 2, 3, 4, 5]

def transform_data(data):
    """Transform data."""
    return [x * 2 for x in data]

def filter_data(data, threshold):
    """Filter data by threshold."""
    return [x for x in data if x > threshold]

def process_pipeline(source, threshold):
    """Full processing pipeline."""
    raw_data = read_data(source)
    transformed = transform_data(raw_data)
    filtered = filter_data(transformed, threshold)
    return filtered
''')
    
    # Create a main application module
    (repo_path / 'main.py').write_text('''
"""Main application module."""

import utils
import processor

def initialize_app():
    """Initialize the application."""
    utils.log_message("Initializing application")
    return True

def run_analysis(source):
    """Run data analysis."""
    utils.log_message("Starting analysis")
    
    # Validate input
    if not utils.validate_input(source):
        return None
    
    # Process data
    result = processor.process_pipeline(source, threshold=5)
    
    # Format output
    formatted = utils.format_output(result)
    
    utils.log_message("Analysis complete")
    return formatted

def main():
    """Main entry point."""
    if initialize_app():
        result = run_analysis("data.txt")
        print(result)
''')
    
    # Create a class-based module
    (repo_path / 'calculator.py').write_text('''
"""Calculator module with class-based design."""

class Calculator:
    """Basic calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        self.result = 0
    
    def add(self, x, y):
        """Add two numbers."""
        return x + y
    
    def subtract(self, x, y):
        """Subtract two numbers."""
        return x - y
    
    def multiply(self, x, y):
        """Multiply two numbers."""
        return x * y
    
    def divide(self, x, y):
        """Divide two numbers."""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y
    
    def calculate(self, operation, x, y):
        """Perform calculation based on operation."""
        if operation == 'add':
            return self.add(x, y)
        elif operation == 'subtract':
            return self.subtract(x, y)
        elif operation == 'multiply':
            return self.multiply(x, y)
        elif operation == 'divide':
            return self.divide(x, y)
        else:
            raise ValueError(f"Unknown operation: {operation}")

class ScientificCalculator(Calculator):
    """Extended calculator with scientific functions."""
    
    def power(self, x, y):
        """Raise x to the power of y."""
        return x ** y
    
    def sqrt(self, x):
        """Calculate square root."""
        return x ** 0.5
    
    def calculate(self, operation, x, y=None):
        """Extended calculation support."""
        if operation == 'power':
            return self.power(x, y)
        elif operation == 'sqrt':
            return self.sqrt(x)
        else:
            return super().calculate(operation, x, y)
''')
    
    return repo_path


def demo_call_graph_generation():
    """Run a demonstration of call graph generation."""
    print("=" * 70)
    print("AccuDoc Call Graph Generator Demo")
    print("=" * 70)
    print()
    
    # Create sample repository
    print("Creating sample repository with function relationships...")
    repo_path = create_sample_repository()
    
    try:
        # Generate call graph
        print(f"Analyzing repository at: {repo_path}")
        print()
        
        generator = CallGraphGenerator(str(repo_path))
        call_graph = generator.analyze_repository(['.py'])
        
        # Show summary
        print("Call Graph Summary:")
        print("-" * 70)
        summary = call_graph['summary']
        print(f"Total Functions: {summary['total_functions']}")
        print(f"Total Classes: {summary['total_classes']}")
        print(f"Total Call Relationships: {summary['total_call_relationships']}")
        print()
        
        # Show some function details
        print("Sample Functions:")
        print("-" * 70)
        for func_name, func_info in list(call_graph['functions'].items())[:5]:
            simple_name = func_name.split('::')[-1]
            print(f"  {simple_name}")
            print(f"    File: {func_info['file']}")
            print(f"    Line: {func_info['line']}")
            print(f"    Parameters: {', '.join(func_info.get('parameters', []))}")
            
            # Show what this function calls
            callees = generator.find_callees(simple_name, call_graph)
            if callees:
                print(f"    Calls: {len(callees)} function(s)")
            
            # Show what calls this function
            callers = generator.find_callers(simple_name, call_graph)
            if callers:
                print(f"    Called by: {len(callers)} function(s)")
            print()
        
        # Show most called functions
        graph = call_graph['call_graph']
        from collections import defaultdict
        callee_counts = defaultdict(int)
        for callees in graph.values():
            for callee in callees:
                callee_counts[callee] += 1
        
        if callee_counts:
            print("Most Called Functions:")
            print("-" * 70)
            sorted_callees = sorted(callee_counts.items(), key=lambda x: x[1], reverse=True)
            for callee, count in sorted_callees[:5]:
                simple_name = callee.split('::')[-1]
                print(f"  {simple_name}: called {count} time(s)")
            print()
        
        # Show functions with most dependencies
        caller_counts = {caller: len(callees) for caller, callees in graph.items()}
        if caller_counts:
            print("Functions with Most Dependencies:")
            print("-" * 70)
            sorted_callers = sorted(caller_counts.items(), key=lambda x: x[1], reverse=True)
            for caller, count in sorted_callers[:5]:
                if count > 0:
                    simple_name = caller.split('::')[-1]
                    print(f"  {simple_name}: calls {count} function(s)")
            print()
        
        # Generate and display full report
        print("Generating Full Report:")
        print("=" * 70)
        report = generator.generate_report(call_graph)
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
    demo_call_graph_generation()
