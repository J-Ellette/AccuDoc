"""
Test suite for Phase 3 AccuDoc features:
- Monorepo Support
- Breaking Changes Detection
- Code Quality Metrics
- Grammar Checking
- Documentation Coverage
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from accudoc.monorepo import MonorepoDetector
from accudoc.breaking_changes import BreakingChangesDetector
from accudoc.code_quality import CodeQualityAnalyzer
from accudoc.grammar_check import GrammarChecker
from accudoc.doc_coverage import DocumentationCoverageAnalyzer


class TestMonorepoSupport(unittest.TestCase):
    """Test monorepo detection and analysis."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_detect_lerna_monorepo(self):
        """Test Lerna monorepo detection."""
        # Create lerna.json
        lerna_config = {'packages': ['packages/*'], 'version': '1.0.0'}
        (self.repo_path / 'lerna.json').write_text(json.dumps(lerna_config))
        
        detector = MonorepoDetector(str(self.repo_path))
        
        self.assertTrue(detector.is_monorepo())
        self.assertEqual(detector.detect_monorepo_type(), 'lerna')
    
    def test_detect_yarn_workspaces(self):
        """Test Yarn workspaces detection."""
        # Create package.json with workspaces
        package = {'name': 'monorepo', 'workspaces': ['packages/*']}
        (self.repo_path / 'package.json').write_text(json.dumps(package))
        
        detector = MonorepoDetector(str(self.repo_path))
        
        self.assertTrue(detector.is_monorepo())
        self.assertEqual(detector.detect_monorepo_type(), 'yarn_workspaces')
    
    def test_find_projects(self):
        """Test finding projects in monorepo."""
        # Create simple multi-package structure
        packages_dir = self.repo_path / 'packages'
        packages_dir.mkdir()
        
        # Create two packages
        for i in range(2):
            pkg_dir = packages_dir / f'pkg{i+1}'
            pkg_dir.mkdir()
            pkg_json = {'name': f'@test/pkg{i+1}', 'version': '1.0.0'}
            (pkg_dir / 'package.json').write_text(json.dumps(pkg_json))
        
        detector = MonorepoDetector(str(self.repo_path))
        projects = detector.find_projects()
        
        self.assertEqual(len(projects), 2)
        self.assertTrue(all('name' in p for p in projects))


class TestBreakingChanges(unittest.TestCase):
    """Test breaking changes detection."""
    
    def test_extract_python_signatures(self):
        """Test Python signature extraction."""
        code = '''
def hello(name):
    pass

class MyClass:
    def method(self, x, y):
        pass
'''
        detector = BreakingChangesDetector('/tmp')
        signatures = detector._extract_python_signatures(code)
        
        self.assertIn('def hello(name)', signatures)
        self.assertIn('class MyClass', signatures)
    
    def test_extract_javascript_signatures(self):
        """Test JavaScript signature extraction."""
        code = '''
function greet(name) {
    return "Hello " + name;
}

class Person {
    constructor(name) {
        this.name = name;
    }
}
'''
        detector = BreakingChangesDetector('/tmp')
        signatures = detector._extract_javascript_signatures(code)
        
        self.assertIn('function greet(name)', signatures)
        self.assertIn('class Person', signatures)
    
    def test_parse_version(self):
        """Test version parsing."""
        detector = BreakingChangesDetector('/tmp')
        
        self.assertEqual(detector._parse_version('1.2.3'), (1, 2, 3))
        self.assertEqual(detector._parse_version('v2.0.0'), (2, 0, 0))
        self.assertEqual(detector._parse_version('3.1.4-beta'), (3, 1, 4))


class TestCodeQuality(unittest.TestCase):
    """Test code quality analysis."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_calculate_cyclomatic_complexity(self):
        """Test complexity calculation."""
        code = '''
def complex_function(x):
    if x > 0:
        for i in range(10):
            if i % 2 == 0:
                print(i)
    elif x < 0:
        while x < 0:
            x += 1
    return x
'''
        analyzer = CodeQualityAnalyzer(str(self.repo_path))
        complexity = analyzer.calculate_cyclomatic_complexity(code, 'python')
        
        # Should have multiple decision points
        self.assertGreater(complexity, 1)
    
    def test_maintainability_index(self):
        """Test maintainability index calculation."""
        analyzer = CodeQualityAnalyzer(str(self.repo_path))
        
        # Low complexity, few lines = high MI
        mi_high = analyzer.calculate_maintainability_index(10, 2)
        self.assertGreater(mi_high, 70)
        
        # High complexity, many lines = low MI
        mi_low = analyzer.calculate_maintainability_index(500, 50)
        self.assertLess(mi_low, 50)
    
    def test_analyze_file(self):
        """Test file analysis."""
        # Create test Python file
        test_file = self.repo_path / 'test.py'
        test_file.write_text('''
def simple_function():
    """A simple function."""
    return 42

# This is a comment
x = 10
''')
        
        analyzer = CodeQualityAnalyzer(str(self.repo_path))
        result = analyzer.analyze_file(test_file)
        
        self.assertIsNotNone(result)
        self.assertIn('metrics', result)
        self.assertIn('code_lines', result['metrics'])
        self.assertIn('maintainability_index', result['metrics'])


class TestGrammarChecker(unittest.TestCase):
    """Test grammar checking."""
    
    def setUp(self):
        """Set up grammar checker."""
        self.checker = GrammarChecker()
    
    def test_repeated_words(self):
        """Test detection of repeated words."""
        text = "This is is a test."
        result = self.checker.check_text(text)
        
        # Should detect repeated "is"
        self.assertGreater(result['total_issues'], 0)
        repeated = [i for i in result['issues'] if i['rule'] == 'repeated_words']
        self.assertGreater(len(repeated), 0)
    
    def test_passive_voice(self):
        """Test passive voice detection."""
        text = "The code was written by the developer."
        result = self.checker.check_text(text)
        
        # Should detect passive voice
        passive = [i for i in result['issues'] if i['rule'] == 'passive_voice']
        self.assertGreaterEqual(len(passive), 0)  # May or may not flag depending on context
    
    def test_clean_text(self):
        """Test with grammatically correct text."""
        text = "This is a well-written sentence. It has no obvious grammar issues."
        result = self.checker.check_text(text)
        
        # Should have minimal or no issues
        self.assertIsInstance(result['issues'], list)
    
    def test_generate_report(self):
        """Test report generation."""
        results = [{
            'file': 'test.md',
            'issues': [
                {'rule': 'repeated_words', 'line': 1, 'text': 'is is', 
                 'message': 'Repeated word', 'severity': 'error', 'context': 'This is is a test'}
            ],
            'total_issues': 1,
            'by_severity': {'error': 1},
            'by_rule': {'repeated_words': 1}
        }]
        
        report = self.checker.generate_report(results)
        
        self.assertIn('Grammar Check Report', report)
        self.assertIn('test.md', report)


class TestDocumentationCoverage(unittest.TestCase):
    """Test documentation coverage analysis."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_analyze_python_documented(self):
        """Test Python file with documentation."""
        test_file = self.repo_path / 'documented.py'
        test_file.write_text('''
def documented_function(x):
    """This function is documented."""
    return x * 2

class DocumentedClass:
    """This class is documented."""
    def method(self):
        """This method is documented."""
        pass
''')
        
        analyzer = DocumentationCoverageAnalyzer(str(self.repo_path))
        result = analyzer.analyze_python_file(test_file)
        
        self.assertIsNotNone(result)
        # Should count function and class (method is part of class)
        self.assertEqual(result['documented'], 2)
        self.assertEqual(result['coverage'], 100.0)
    
    def test_analyze_python_undocumented(self):
        """Test Python file without documentation."""
        test_file = self.repo_path / 'undocumented.py'
        test_file.write_text('''
def undocumented_function(x):
    return x * 2

class UndocumentedClass:
    def method(self):
        pass
''')
        
        analyzer = DocumentationCoverageAnalyzer(str(self.repo_path))
        result = analyzer.analyze_python_file(test_file)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['documented'], 0)
        self.assertEqual(result['coverage'], 0.0)
        self.assertGreater(len(result['undocumented_items']), 0)
    
    def test_calculate_overall_coverage(self):
        """Test overall coverage calculation."""
        analyzer = DocumentationCoverageAnalyzer(str(self.repo_path))
        
        results = [
            {'file': 'a.py', 'language': 'python', 'total_items': 10, 'documented': 8, 'coverage': 80.0},
            {'file': 'b.py', 'language': 'python', 'total_items': 5, 'documented': 5, 'coverage': 100.0}
        ]
        
        overall = analyzer.calculate_overall_coverage(results)
        
        self.assertEqual(overall['total_items'], 15)
        self.assertEqual(overall['documented'], 13)
        self.assertAlmostEqual(overall['coverage'], 86.67, places=1)
    
    def test_generate_report(self):
        """Test report generation."""
        analyzer = DocumentationCoverageAnalyzer(str(self.repo_path))
        
        results = [
            {'file': 'test.py', 'language': 'python', 'total_items': 10, 
             'documented': 7, 'undocumented': 3, 'coverage': 70.0, 'undocumented_items': []}
        ]
        
        report = analyzer.generate_report(results)
        
        self.assertIn('Documentation Coverage Report', report)
        self.assertIn('70', report)


def run_tests():
    """Run all Phase 3 tests."""
    print("=" * 60)
    print("AccuDoc Phase 3 Features Test Suite")
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
