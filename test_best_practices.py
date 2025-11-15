"""
Test suite for Best Practices Checker feature.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from accudoc.best_practices import BestPracticesChecker


class TestBestPracticesChecker(unittest.TestCase):
    """Test best practices checking functionality."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_missing_module_docstring(self):
        """Test detection of missing module docstring."""
        py_file = self.repo_path / 'no_docstring.py'
        py_file.write_text('''
def some_function():
    return 1
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        violation_types = [v['type'] for v in result['violations']]
        self.assertIn('missing_module_docstring', violation_types)
    
    def test_missing_function_docstring(self):
        """Test detection of missing function docstring."""
        py_file = self.repo_path / 'func_no_docstring.py'
        py_file.write_text('''
"""Module docstring."""

def public_function():
    return 1
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        violation_types = [v['type'] for v in result['violations']]
        self.assertIn('missing_function_docstring', violation_types)
    
    def test_too_many_parameters(self):
        """Test detection of functions with too many parameters."""
        py_file = self.repo_path / 'many_params.py'
        py_file.write_text('''
"""Module docstring."""

def function_with_many_params(a, b, c, d, e, f, g):
    """Function with many parameters."""
    return a + b + c + d + e + f + g
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        violation_types = [v['type'] for v in result['violations']]
        self.assertIn('too_many_parameters', violation_types)
    
    def test_mutable_default_argument(self):
        """Test detection of mutable default arguments."""
        py_file = self.repo_path / 'mutable_default.py'
        py_file.write_text('''
"""Module docstring."""

def function_with_mutable_default(items=[]):
    """Function with mutable default."""
    items.append(1)
    return items
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        violation_types = [v['type'] for v in result['violations']]
        self.assertIn('mutable_default_argument', violation_types)
        
        # Check severity
        for v in result['violations']:
            if v['type'] == 'mutable_default_argument':
                self.assertEqual(v['severity'], 'high')
    
    def test_bare_except(self):
        """Test detection of bare except clauses."""
        py_file = self.repo_path / 'bare_except.py'
        py_file.write_text('''
"""Module docstring."""

def risky_function():
    """Function with bare except."""
    try:
        x = 1 / 0
    except:
        pass
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        violation_types = [v['type'] for v in result['violations']]
        self.assertIn('bare_except', violation_types)
        
        # Check severity
        for v in result['violations']:
            if v['type'] == 'bare_except':
                self.assertEqual(v['severity'], 'high')
    
    def test_broad_exception(self):
        """Test detection of broad exception catching."""
        py_file = self.repo_path / 'broad_except.py'
        py_file.write_text('''
"""Module docstring."""

def broad_catch():
    """Function with broad exception."""
    try:
        x = 1 / 0
    except Exception:
        pass
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        violation_types = [v['type'] for v in result['violations']]
        self.assertIn('broad_exception', violation_types)
    
    def test_missing_class_docstring(self):
        """Test detection of missing class docstring."""
        py_file = self.repo_path / 'class_no_docstring.py'
        py_file.write_text('''
"""Module docstring."""

class MyClass:
    def __init__(self):
        """Constructor."""
        pass
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        violation_types = [v['type'] for v in result['violations']]
        self.assertIn('missing_class_docstring', violation_types)
    
    def test_line_too_long(self):
        """Test detection of lines that are too long."""
        py_file = self.repo_path / 'long_line.py'
        long_line = 'x = ' + '"a" + ' * 50 + '"b"'  # Create a very long line
        py_file.write_text(f'''
"""Module docstring."""

{long_line}
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        violation_types = [v['type'] for v in result['violations']]
        self.assertIn('line_too_long', violation_types)
    
    def test_clean_code(self):
        """Test that clean code has no violations (or minimal)."""
        py_file = self.repo_path / 'clean.py'
        py_file.write_text('''
"""A clean module following best practices."""

def add(x, y):
    """Add two numbers."""
    return x + y

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        self.result = 0
    
    def multiply(self, x, y):
        """Multiply two numbers."""
        return x * y
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        # Should have very few violations
        self.assertLessEqual(result['total_violations'], 2)
    
    def test_repository_check(self):
        """Test checking multiple files in repository."""
        # Create multiple files
        (self.repo_path / 'file1.py').write_text('''
"""Module 1."""

def func1():
    """Function 1."""
    return 1
''')
        
        (self.repo_path / 'file2.py').write_text('''
def func2():
    return 2
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        results = checker.check_repository(['.py'])
        
        self.assertEqual(results['summary']['total_files'], 2)
        self.assertGreater(results['summary']['total_violations'], 0)
        self.assertIn('severity_counts', results['summary'])
    
    def test_severity_counts(self):
        """Test severity counting."""
        py_file = self.repo_path / 'violations.py'
        py_file.write_text('''
def func(items=[]):
    try:
        x = 1 / 0
    except:
        pass
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        self.assertIn('severity_counts', result)
        # Should have some high severity (bare except, mutable default)
        self.assertGreater(result['severity_counts']['high'], 0)
    
    def test_generate_report(self):
        """Test report generation."""
        # Create files with violations
        (self.repo_path / 'violations.py').write_text('''
def func(items=[]):
    try:
        x = 1 / 0
    except:
        pass
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        results = checker.check_repository(['.py'])
        report = checker.generate_report(results)
        
        self.assertIn('Best Practices Check Report', report)
        self.assertIn('Summary', report)
        self.assertIn('Recommendations', report)
        self.assertIsInstance(report, str)
    
    def test_private_methods_skip_docstring_check(self):
        """Test that private methods are not required to have docstrings."""
        py_file = self.repo_path / 'private_methods.py'
        py_file.write_text('''
"""Module docstring."""

class MyClass:
    """Class docstring."""
    
    def _private_method(self):
        return 1
    
    def __double_private(self):
        return 2
''')
        
        checker = BestPracticesChecker(str(self.repo_path))
        result = checker.check_python_file(py_file)
        
        # Should not complain about missing docstrings for private methods
        violation_types = [v['type'] for v in result['violations']]
        # Filter to only function docstring violations
        func_docstring_violations = [v for v in result['violations'] 
                                     if v['type'] == 'missing_function_docstring']
        # Should be empty or not complain about _private_method
        self.assertEqual(len(func_docstring_violations), 0)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Best Practices Checker Test Suite")
    print("=" * 60)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBestPracticesChecker)
    
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
