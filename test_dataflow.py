"""
Test suite for Data Flow Analysis feature.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from accudoc.dataflow import DataFlowAnalyzer


class TestDataFlowAnalyzer(unittest.TestCase):
    """Test data flow analysis functionality."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_simple_function_analysis(self):
        """Test analyzing a simple function."""
        # Create a simple Python file
        test_file = self.repo_path / 'simple.py'
        test_file.write_text('''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    result = a + b
    return result
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        self.assertEqual(len(result['functions']), 1)
        func = result['functions'][0]
        
        self.assertEqual(func['name'], 'calculate_sum')
        self.assertEqual(len(func['parameters']), 2)
        self.assertEqual(func['parameters'][0]['name'], 'a')
        self.assertEqual(func['parameters'][1]['name'], 'b')
        
        # Check assignments
        self.assertGreater(len(func['assignments']), 0)
        self.assertEqual(func['assignments'][0]['variable'], 'result')
        
        # Check returns
        self.assertEqual(len(func['returns']), 1)
        self.assertEqual(func['returns'][0]['value'], 'result')
        
        # Check variables
        self.assertIn('a', func['variables_read'])
        self.assertIn('b', func['variables_read'])
        self.assertIn('result', func['variables_written'])
    
    def test_complex_function_analysis(self):
        """Test analyzing a function with multiple operations."""
        test_file = self.repo_path / 'complex.py'
        test_file.write_text('''
def process_data(items, threshold):
    """Process data items."""
    filtered = [x for x in items if x > threshold]
    total = sum(filtered)
    average = total / len(filtered) if filtered else 0
    result = {
        'total': total,
        'average': average,
        'count': len(filtered)
    }
    return result
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        self.assertEqual(len(result['functions']), 1)
        func = result['functions'][0]
        
        # Check parameters
        self.assertEqual(len(func['parameters']), 2)
        param_names = [p['name'] for p in func['parameters']]
        self.assertIn('items', param_names)
        self.assertIn('threshold', param_names)
        
        # Check assignments
        self.assertGreater(len(func['assignments']), 0)
        var_names = [a['variable'] for a in func['assignments']]
        self.assertIn('filtered', var_names)
        self.assertIn('total', var_names)
        self.assertIn('average', var_names)
        self.assertIn('result', var_names)
    
    def test_class_analysis(self):
        """Test analyzing a class with methods."""
        test_file = self.repo_path / 'class_example.py'
        test_file.write_text('''
class Calculator:
    """Simple calculator class."""
    
    def __init__(self, initial_value=0):
        self.value = initial_value
        self.history = []
    
    def add(self, amount):
        """Add to current value."""
        self.value += amount
        self.history.append(('add', amount))
        return self.value
    
    def subtract(self, amount):
        """Subtract from current value."""
        self.value -= amount
        self.history.append(('subtract', amount))
        return self.value
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        self.assertEqual(len(result['classes']), 1)
        cls = result['classes'][0]
        
        self.assertEqual(cls['name'], 'Calculator')
        self.assertIn('value', cls['attributes'])
        self.assertIn('history', cls['attributes'])
        
        # Check methods
        self.assertEqual(len(cls['methods']), 3)
        method_names = [m['name'] for m in cls['methods']]
        self.assertIn('__init__', method_names)
        self.assertIn('add', method_names)
        self.assertIn('subtract', method_names)
    
    def test_augmented_assignment(self):
        """Test tracking augmented assignments (+=, -=, etc.)."""
        test_file = self.repo_path / 'augmented.py'
        test_file.write_text('''
def increment(value, step):
    """Increment value by step."""
    value += step
    return value
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        func = result['functions'][0]
        
        # Should track both read and write for augmented assignment
        self.assertIn('value', func['variables_read'])
        self.assertIn('value', func['variables_written'])
        
        # Should have assignment record
        self.assertGreater(len(func['assignments']), 0)
    
    def test_multiple_returns(self):
        """Test function with multiple return statements."""
        test_file = self.repo_path / 'multiple_returns.py'
        test_file.write_text('''
def check_value(x):
    """Check if value is valid."""
    if x < 0:
        return False
    elif x > 100:
        return False
    else:
        return True
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        func = result['functions'][0]
        
        # Should track all return statements
        self.assertEqual(len(func['returns']), 3)
        return_values = [r['value'] for r in func['returns']]
        self.assertIn('False', return_values)
        self.assertIn('True', return_values)
    
    def test_repository_analysis(self):
        """Test analyzing entire repository."""
        # Create multiple Python files
        file1 = self.repo_path / 'module1.py'
        file1.write_text('''
def func1(x):
    y = x * 2
    return y
''')
        
        file2 = self.repo_path / 'module2.py'
        file2.write_text('''
def func2(a, b):
    c = a + b
    return c

class MyClass:
    def method1(self):
        pass
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_repository()
        
        # Check summary
        self.assertEqual(result['summary']['total_files'], 2)
        # func1, func2, and MyClass.method1 = 3 functions total
        self.assertEqual(result['summary']['total_functions'], 3)
        self.assertEqual(result['summary']['total_classes'], 1)
        self.assertGreater(result['summary']['total_assignments'], 0)
    
    def test_mermaid_diagram_generation(self):
        """Test generating Mermaid diagrams."""
        test_file = self.repo_path / 'diagram_test.py'
        test_file.write_text('''
def process(input_data):
    cleaned = input_data.strip()
    result = cleaned.upper()
    return result
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        func = result['functions'][0]
        diagram = analyzer.generate_mermaid_diagram(func)
        
        # Should contain Mermaid syntax
        self.assertIn('```mermaid', diagram)
        self.assertIn('graph TD', diagram)
        self.assertIn('START', diagram)
        
        # Should reference function name
        self.assertIn('process', diagram)
        
        # Should show parameter
        self.assertIn('input_data', diagram)
        
        # Should show assignments
        self.assertIn('cleaned', diagram)
        self.assertIn('result', diagram)
    
    def test_report_generation(self):
        """Test generating markdown report."""
        test_file = self.repo_path / 'report_test.py'
        test_file.write_text('''
def example_function(param1, param2):
    """Example function for report."""
    temp = param1 + param2
    result = temp * 2
    return result
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        file_result = analyzer.analyze_file(test_file)
        repo_result = analyzer.analyze_repository()
        
        # Test file report
        report = analyzer.generate_report(file_result)
        
        self.assertIn('Data Flow Analysis Report', report)
        self.assertIn('example_function', report)
        self.assertIn('Parameters', report)
        self.assertIn('param1', report)
        self.assertIn('Variable Assignments', report)
        
        # Test repository report
        repo_report = analyzer.generate_report(repo_result)
        
        self.assertIn('Summary', repo_report)
        self.assertIn('Total Files Analyzed', repo_report)
        self.assertIn('Total Functions', repo_report)
    
    def test_complex_expressions(self):
        """Test tracking complex expressions."""
        test_file = self.repo_path / 'complex_expr.py'
        test_file.write_text('''
def calculate(x, y, z):
    """Complex calculations."""
    result1 = x * y + z
    result2 = (x + y) / z if z != 0 else 0
    data = [1, 2, 3, 4, 5]
    mapped = list(map(lambda i: i * 2, data))
    return result1, result2, mapped
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        func = result['functions'][0]
        
        # Should track all assignments
        self.assertGreater(len(func['assignments']), 3)
        
        # Should handle return tuple
        self.assertEqual(len(func['returns']), 1)
    
    def test_error_handling(self):
        """Test handling invalid Python files."""
        test_file = self.repo_path / 'invalid.py'
        test_file.write_text('this is not valid python code {{{')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        # Should return error information
        self.assertIn('error', result)
        self.assertEqual(len(result['functions']), 0)
    
    def test_empty_function(self):
        """Test analyzing empty function."""
        test_file = self.repo_path / 'empty.py'
        test_file.write_text('''
def empty_function():
    """Empty function."""
    pass
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        func = result['functions'][0]
        
        self.assertEqual(func['name'], 'empty_function')
        self.assertEqual(len(func['parameters']), 0)
        self.assertEqual(len(func['assignments']), 0)
        self.assertEqual(len(func['returns']), 0)
    
    def test_nested_function_calls(self):
        """Test tracking nested function calls."""
        test_file = self.repo_path / 'nested.py'
        test_file.write_text('''
def process_string(text):
    """Process a string with multiple operations."""
    result = text.strip().lower().replace(' ', '_')
    return result
''')
        
        analyzer = DataFlowAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        func = result['functions'][0]
        
        # Should track the assignment
        self.assertGreater(len(func['assignments']), 0)
        self.assertEqual(func['assignments'][0]['variable'], 'result')


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Data Flow Analysis Test Suite")
    print("=" * 60)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
