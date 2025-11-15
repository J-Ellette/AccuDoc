"""
Test suite for Call Graph Generator feature.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from accudoc.call_graph import CallGraphGenerator


class TestCallGraphGenerator(unittest.TestCase):
    """Test call graph generation functionality."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_simple_function_calls(self):
        """Test extracting simple function calls."""
        py_file = self.repo_path / 'simple.py'
        py_file.write_text('''
def func_a():
    return 1

def func_b():
    return func_a() + 2

def func_c():
    return func_b() + func_a()
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        analysis = generator.analyze_python_file(py_file)
        
        self.assertEqual(len(analysis['functions']), 3)
        self.assertIn('func_a', analysis['functions'])
        self.assertIn('func_b', analysis['functions'])
        self.assertIn('func_c', analysis['functions'])
        
        # Check calls
        self.assertIn('func_a', analysis['calls']['func_b'])
        self.assertIn('func_a', analysis['calls']['func_c'])
        self.assertIn('func_b', analysis['calls']['func_c'])
    
    def test_class_methods(self):
        """Test extracting class methods."""
        py_file = self.repo_path / 'classes.py'
        py_file.write_text('''
class MyClass:
    def __init__(self):
        self.value = 0
    
    def method_a(self):
        return self.value
    
    def method_b(self):
        return self.method_a() + 1
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        analysis = generator.analyze_python_file(py_file)
        
        self.assertEqual(len(analysis['classes']), 1)
        self.assertIn('MyClass', analysis['classes'])
        self.assertEqual(len(analysis['classes']['MyClass']['methods']), 3)
    
    def test_nested_calls(self):
        """Test nested function calls."""
        py_file = self.repo_path / 'nested.py'
        py_file.write_text('''
def level_1():
    return 1

def level_2():
    return level_1()

def level_3():
    return level_2()
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        analysis = generator.analyze_python_file(py_file)
        
        self.assertIn('level_1', analysis['calls']['level_2'])
        self.assertIn('level_2', analysis['calls']['level_3'])
    
    def test_build_call_graph(self):
        """Test building complete call graph from multiple files."""
        # Create multiple files
        (self.repo_path / 'file1.py').write_text('''
def func_a():
    return 1

def func_b():
    return func_a()
''')
        
        (self.repo_path / 'file2.py').write_text('''
def func_c():
    return 2

def func_d():
    return func_c()
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        
        # Analyze both files
        analysis1 = generator.analyze_python_file(self.repo_path / 'file1.py')
        analysis2 = generator.analyze_python_file(self.repo_path / 'file2.py')
        
        # Build call graph
        call_graph = generator.build_call_graph([analysis1, analysis2])
        
        self.assertEqual(call_graph['summary']['total_functions'], 4)
        self.assertGreater(call_graph['summary']['total_call_relationships'], 0)
    
    def test_find_callers(self):
        """Test finding callers of a function."""
        py_file = self.repo_path / 'callers.py'
        py_file.write_text('''
def target():
    return 1

def caller_a():
    return target()

def caller_b():
    return target() + 1
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        analysis = generator.analyze_python_file(py_file)
        call_graph = generator.build_call_graph([analysis])
        
        callers = generator.find_callers('target', call_graph)
        
        # Should find both caller_a and caller_b
        self.assertGreaterEqual(len(callers), 1)
    
    def test_find_callees(self):
        """Test finding functions called by a function."""
        py_file = self.repo_path / 'callees.py'
        py_file.write_text('''
def helper_a():
    return 1

def helper_b():
    return 2

def main_function():
    return helper_a() + helper_b()
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        analysis = generator.analyze_python_file(py_file)
        call_graph = generator.build_call_graph([analysis])
        
        callees = generator.find_callees('main_function', call_graph)
        
        # Should find helper_a and helper_b
        self.assertGreaterEqual(len(callees), 1)
    
    def test_repository_analysis(self):
        """Test analyzing entire repository."""
        # Create multiple files
        (self.repo_path / 'module1.py').write_text('''
def func1():
    return 1
''')
        
        (self.repo_path / 'module2.py').write_text('''
def func2():
    return 2
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        call_graph = generator.analyze_repository(['.py'])
        
        self.assertGreaterEqual(call_graph['summary']['total_functions'], 2)
        self.assertIn('functions', call_graph)
        self.assertIn('call_graph', call_graph)
    
    def test_generate_mermaid_diagram(self):
        """Test Mermaid diagram generation."""
        py_file = self.repo_path / 'diagram.py'
        py_file.write_text('''
def func_a():
    return 1

def func_b():
    return func_a()

def func_c():
    return func_b()
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        analysis = generator.analyze_python_file(py_file)
        call_graph = generator.build_call_graph([analysis])
        
        diagram = generator.generate_mermaid_diagram(call_graph)
        
        self.assertIn('```mermaid', diagram)
        self.assertIn('graph TD', diagram)
        self.assertIn('```', diagram)
    
    def test_generate_report(self):
        """Test report generation."""
        py_file = self.repo_path / 'report.py'
        py_file.write_text('''
def helper():
    return 1

def main():
    return helper() + helper()
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        analysis = generator.analyze_python_file(py_file)
        call_graph = generator.build_call_graph([analysis])
        
        report = generator.generate_report(call_graph)
        
        self.assertIn('Call Graph Analysis Report', report)
        self.assertIn('Summary', report)
        self.assertIn('Recommendations', report)
        self.assertIsInstance(report, str)
    
    def test_method_calls(self):
        """Test extracting method calls."""
        py_file = self.repo_path / 'methods.py'
        py_file.write_text('''
class Calculator:
    def add(self, x, y):
        return x + y
    
    def multiply(self, x, y):
        return x * y
    
    def calculate(self, x, y):
        sum_result = self.add(x, y)
        prod_result = self.multiply(x, y)
        return sum_result + prod_result
''')
        
        generator = CallGraphGenerator(str(self.repo_path))
        analysis = generator.analyze_python_file(py_file)
        
        # Check that method calls are tracked
        self.assertIn('Calculator.calculate', analysis['calls'])


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Call Graph Generator Test Suite")
    print("=" * 60)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCallGraphGenerator)
    
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
