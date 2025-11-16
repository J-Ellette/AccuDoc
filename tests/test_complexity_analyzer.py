"""
Test suite for Complexity Analyzer feature.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from accudoc.complexity_analyzer import ComplexityAnalyzer


class TestComplexityAnalyzer(unittest.TestCase):
    """Test complexity analysis functionality."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_simple_function_complexity(self):
        """Test complexity of a simple function."""
        # Create a simple Python file
        py_file = self.repo_path / 'simple.py'
        py_file.write_text('''
def simple_function(x):
    """A simple function."""
    return x + 1
''')
        
        analyzer = ComplexityAnalyzer(str(self.repo_path))
        analysis = analyzer.analyze_python_file(py_file)
        
        self.assertEqual(analysis['total_functions'], 1)
        self.assertEqual(analysis['functions'][0]['name'], 'simple_function')
        self.assertEqual(analysis['functions'][0]['complexity'], 1)
        self.assertTrue(analysis['functions'][0]['has_docstring'])
    
    def test_complex_function_complexity(self):
        """Test complexity of a complex function."""
        # Create a complex Python file
        py_file = self.repo_path / 'complex.py'
        py_file.write_text('''
def complex_function(x, y):
    """A complex function."""
    result = 0
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                result += i
            else:
                result -= i
        
        while y > 0:
            result += y
            y -= 1
    elif x < 0:
        result = -x
    else:
        result = 0
    
    return result
''')
        
        analyzer = ComplexityAnalyzer(str(self.repo_path))
        analysis = analyzer.analyze_python_file(py_file)
        
        self.assertEqual(analysis['total_functions'], 1)
        self.assertEqual(analysis['functions'][0]['name'], 'complex_function')
        # This function has: 1 base + 3 if/elif/else + 1 for + 1 while = 6+
        self.assertGreater(analysis['functions'][0]['complexity'], 5)
        self.assertTrue(analysis['functions'][0]['has_docstring'])
    
    def test_undocumented_function(self):
        """Test detection of undocumented functions."""
        # Create a file with undocumented complex function
        py_file = self.repo_path / 'undocumented.py'
        py_file.write_text('''
def undocumented_complex_function(x):
    if x > 10:
        if x > 20:
            return x * 2
        else:
            return x + 10
    else:
        return x
''')
        
        analyzer = ComplexityAnalyzer(str(self.repo_path))
        analysis = analyzer.analyze_python_file(py_file)
        
        self.assertEqual(analysis['total_functions'], 1)
        self.assertFalse(analysis['functions'][0]['has_docstring'])
        # Should be marked as undocumented if complexity > 5
        if analysis['functions'][0]['complexity'] > 5:
            self.assertEqual(len(analysis['undocumented_functions']), 1)
    
    def test_class_analysis(self):
        """Test analysis of classes."""
        # Create a file with a class
        py_file = self.repo_path / 'classes.py'
        py_file.write_text('''
class MyClass:
    """A test class."""
    
    def __init__(self):
        """Constructor."""
        pass
    
    def method1(self):
        """Method 1."""
        return 1
    
    def method2(self):
        """Method 2."""
        return 2
''')
        
        analyzer = ComplexityAnalyzer(str(self.repo_path))
        analysis = analyzer.analyze_python_file(py_file)
        
        self.assertEqual(analysis['total_classes'], 1)
        self.assertEqual(analysis['classes'][0]['name'], 'MyClass')
        self.assertTrue(analysis['classes'][0]['has_docstring'])
        self.assertEqual(analysis['classes'][0]['methods'], 3)  # __init__, method1, method2
    
    def test_javascript_file_analysis(self):
        """Test basic JavaScript file analysis."""
        # Create a JavaScript file
        js_file = self.repo_path / 'test.js'
        js_file.write_text('''
function myFunction() {
    if (x > 0) {
        for (let i = 0; i < 10; i++) {
            console.log(i);
        }
    }
}

const arrowFunc = () => {
    return 42;
};

class MyClass {
    constructor() {
        this.value = 0;
    }
}
''')
        
        analyzer = ComplexityAnalyzer(str(self.repo_path))
        analysis = analyzer.analyze_javascript_file(js_file)
        
        self.assertGreater(analysis['functions'], 0)
        self.assertEqual(analysis['classes'], 1)
        self.assertIn('control_flow_count', analysis)
    
    def test_repository_analysis(self):
        """Test analyzing multiple files in repository."""
        # Create multiple Python files
        (self.repo_path / 'file1.py').write_text('''
def func1():
    """Function 1."""
    return 1
''')
        
        (self.repo_path / 'file2.py').write_text('''
def func2(x):
    """Function 2."""
    if x > 0:
        return x
    return 0

class TestClass:
    """A test class."""
    pass
''')
        
        analyzer = ComplexityAnalyzer(str(self.repo_path))
        analysis = analyzer.analyze_repository(['.py'])
        
        self.assertEqual(analysis['summary']['total_files'], 2)
        self.assertGreaterEqual(analysis['summary']['total_functions'], 2)
        self.assertGreaterEqual(analysis['summary']['total_classes'], 1)
        self.assertIsInstance(analysis['python_files'], list)
    
    def test_generate_report(self):
        """Test report generation."""
        # Create a test file
        (self.repo_path / 'test.py').write_text('''
def complex_func(x, y, z):
    result = 0
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                result += i
            else:
                result -= i
    
    if y > 0:
        while y > 0:
            result += y
            y -= 1
    
    if z > 0:
        result *= z
    
    return result
''')
        
        analyzer = ComplexityAnalyzer(str(self.repo_path))
        analysis = analyzer.analyze_repository(['.py'])
        report = analyzer.generate_report(analysis)
        
        self.assertIn('Code Complexity Analysis Report', report)
        self.assertIn('Summary', report)
        self.assertIn('Recommendations', report)
        self.assertIsInstance(report, str)
    
    def test_high_complexity_detection(self):
        """Test detection of high complexity functions."""
        # Create a very complex function
        py_file = self.repo_path / 'high_complexity.py'
        py_file.write_text('''
def very_complex_function(a, b, c, d, e, f, g, h):
    """A very complex function for testing."""
    result = 0
    
    # Multiple if statements (not elif)
    if a > 0:
        result += a
    
    if b > 0:
        result += b
    
    if c > 0:
        result += c
    
    if d > 0:
        result += d
    
    if e > 0:
        result += e
    
    if f > 0:
        result += f
    
    if g > 0:
        result += g
    
    if h > 0:
        result += h
    
    # Add loops and more complexity
    for i in range(10):
        if i % 2 == 0:
            result += i
        else:
            result -= i
    
    while result > 100:
        result -= 10
    
    return result
''')
        
        analyzer = ComplexityAnalyzer(str(self.repo_path))
        analysis = analyzer.analyze_repository(['.py'])
        
        # Should detect at least one high complexity function
        self.assertGreater(len(analysis['summary']['high_complexity_functions']), 0)
        
        # Verify the function is marked as complex
        high_complex = analysis['summary']['high_complexity_functions'][0]
        self.assertEqual(high_complex['function'], 'very_complex_function')
        self.assertGreater(high_complex['complexity'], 10)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Complexity Analyzer Test Suite")
    print("=" * 60)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestComplexityAnalyzer)
    
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
