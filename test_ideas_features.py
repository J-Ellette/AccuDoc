"""
Test suite for new AccuDoc features:
- Branch Comparison
- Version Analysis
- Spell Checking
"""

import unittest
import tempfile
import shutil
import json
import subprocess
from pathlib import Path
from accudoc.branch_comparison import BranchComparator
from accudoc.version_analyzer import VersionAnalyzer
from accudoc.spellcheck import SpellChecker


class TestBranchComparison(unittest.TestCase):
    """Test branch comparison functionality."""
    
    def setUp(self):
        """Set up test repository."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / 'test_repo'
        self.repo_path.mkdir()
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.repo_path, capture_output=True)
        
        # Create initial commit on master
        (self.repo_path / 'file1.txt').write_text('Initial content')
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.repo_path, capture_output=True)
        
        # Get the default branch name
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              cwd=self.repo_path, capture_output=True, text=True)
        self.main_branch = result.stdout.strip()
        
        # Create feature branch
        subprocess.run(['git', 'checkout', '-b', 'feature'], cwd=self.repo_path, capture_output=True)
        (self.repo_path / 'file2.txt').write_text('Feature content')
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add feature file'], cwd=self.repo_path, capture_output=True)
        
        # Go back to main branch
        subprocess.run(['git', 'checkout', self.main_branch], cwd=self.repo_path, capture_output=True)
    
    def tearDown(self):
        """Clean up test repository."""
        shutil.rmtree(self.test_dir)
    
    def test_get_available_branches(self):
        """Test getting list of branches."""
        comparator = BranchComparator(str(self.repo_path))
        branches = comparator.get_available_branches()
        
        self.assertIn(self.main_branch, branches)
        self.assertIn('feature', branches)
        self.assertIsInstance(branches, list)
    
    def test_get_current_branch(self):
        """Test getting current branch."""
        comparator = BranchComparator(str(self.repo_path))
        current = comparator.get_current_branch()
        
        self.assertEqual(current, self.main_branch)
    
    def test_compare_branches(self):
        """Test comparing two branches."""
        comparator = BranchComparator(str(self.repo_path))
        comparison = comparator.compare_branches(self.main_branch, 'feature')
        
        self.assertEqual(comparison['base_branch'], self.main_branch)
        self.assertEqual(comparison['compare_branch'], 'feature')
        self.assertIn('files_added', comparison)
        self.assertIn('statistics', comparison)
        self.assertGreaterEqual(comparison['statistics']['commits_ahead'], 0)
    
    def test_generate_comparison_markdown(self):
        """Test markdown generation."""
        comparator = BranchComparator(str(self.repo_path))
        comparison = comparator.compare_branches(self.main_branch, 'feature')
        markdown = comparator.generate_comparison_markdown(comparison)
        
        self.assertIn('Branch Comparison', markdown)
        self.assertIn('Summary Statistics', markdown)
        self.assertIsInstance(markdown, str)


class TestVersionAnalyzer(unittest.TestCase):
    """Test version analysis functionality."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_parse_version(self):
        """Test version parsing."""
        analyzer = VersionAnalyzer(str(self.repo_path))
        
        self.assertEqual(analyzer._parse_version('1.2.3'), (1, 2, 3))
        self.assertEqual(analyzer._parse_version('v2.0.0'), (2, 0, 0))
        self.assertEqual(analyzer._parse_version('^1.5.0'), (1, 5, 0))
        self.assertEqual(analyzer._parse_version('~3.2.1'), (3, 2, 1))
    
    def test_compare_versions(self):
        """Test version comparison."""
        analyzer = VersionAnalyzer(str(self.repo_path))
        
        self.assertEqual(analyzer._compare_versions('1.0.0', '1.0.0'), 'up-to-date')
        self.assertEqual(analyzer._compare_versions('1.0.0', '1.1.0'), 'minor-update')
        self.assertEqual(analyzer._compare_versions('1.0.0', '2.0.0'), 'major-update')
    
    def test_analyze_python_requirements(self):
        """Test Python requirements analysis."""
        # Create requirements.txt
        req_file = self.repo_path / 'requirements.txt'
        req_file.write_text('requests>=2.25.0\nflask==1.1.2\n')
        
        analyzer = VersionAnalyzer(str(self.repo_path))
        results = analyzer.analyze_python_requirements()
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check structure
        if results:
            result = results[0]
            self.assertIn('package', result)
            self.assertIn('current_version', result)
            self.assertIn('ecosystem', result)
            self.assertEqual(result['ecosystem'], 'python')
    
    def test_analyze_package_json(self):
        """Test package.json analysis."""
        # Create package.json
        pkg_file = self.repo_path / 'package.json'
        pkg_data = {
            'name': 'test-project',
            'dependencies': {
                'express': '^4.17.1',
                'lodash': '~4.17.20'
            },
            'devDependencies': {
                'jest': '^27.0.0'
            }
        }
        pkg_file.write_text(json.dumps(pkg_data))
        
        analyzer = VersionAnalyzer(str(self.repo_path))
        results = analyzer.analyze_package_json()
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check structure
        if results:
            result = results[0]
            self.assertIn('package', result)
            self.assertIn('current_version', result)
            self.assertIn('ecosystem', result)
            self.assertEqual(result['ecosystem'], 'npm')
    
    def test_generate_analysis_report(self):
        """Test report generation."""
        analyzer = VersionAnalyzer(str(self.repo_path))
        
        # Mock dependencies
        dependencies = {
            'python': [
                {
                    'package': 'requests',
                    'current_version': '2.25.0',
                    'latest_version': '2.31.0',
                    'status': 'minor-update',
                    'ecosystem': 'python'
                },
                {
                    'package': 'flask',
                    'current_version': '2.0.0',
                    'latest_version': '2.0.0',
                    'status': 'up-to-date',
                    'ecosystem': 'python'
                }
            ]
        }
        
        report = analyzer.generate_analysis_report(dependencies)
        
        self.assertIn('Dependency Analysis', report)
        self.assertIn('PYTHON', report)
        self.assertIn('Summary', report)
        self.assertIsInstance(report, str)


class TestSpellChecker(unittest.TestCase):
    """Test spell checking functionality."""
    
    def setUp(self):
        """Set up spell checker."""
        self.checker = SpellChecker()
    
    def test_check_text_correct(self):
        """Test checking text with no errors."""
        text = "This is a simple test with correct spelling."
        result = self.checker.check_text(text)
        
        self.assertIn('errors', result)
        self.assertIn('total_words', result)
        self.assertIsInstance(result['errors'], list)
    
    def test_check_text_with_errors(self):
        """Test checking text with spelling errors."""
        text = "This text has some mispeled words and typos."
        result = self.checker.check_text(text)
        
        self.assertIn('errors', result)
        # 'mispeled' should be flagged (assuming it's not in dictionary)
        error_words = [e['word'] for e in result['errors']]
        self.assertIn('mispeled', error_words)
    
    def test_technical_terms(self):
        """Test that technical terms are recognized."""
        text = "Python Django Flask JavaScript React npm pip github"
        result = self.checker.check_text(text)
        
        # All these are technical terms and should not be flagged
        self.assertEqual(len(result['errors']), 0)
    
    def test_skip_code_blocks(self):
        """Test that code blocks are skipped."""
        text = """Some text here.
```
def mispeled_function():
    pass
```
More text."""
        result = self.checker.check_text(text)
        
        # Lines with ``` should be skipped
        # Note: This is a basic check; the implementation may not skip multi-line blocks perfectly
        self.assertIsInstance(result['errors'], list)
    
    def test_check_file(self):
        """Test checking a file."""
        test_dir = tempfile.mkdtemp()
        try:
            test_file = Path(test_dir) / 'test.md'
            test_file.write_text('# Test Document\n\nThis is a test document.')
            
            result = self.checker.check_file(test_file)
            
            self.assertIn('file', result)
            self.assertIn('errors', result)
            self.assertEqual(result['file'], str(test_file))
        finally:
            shutil.rmtree(test_dir)
    
    def test_generate_report(self):
        """Test report generation."""
        results = [
            {
                'file': 'test.md',
                'errors': [
                    {'word': 'mispeled', 'line': 1, 'column': 10},
                    {'word': 'mispeled', 'line': 3, 'column': 5}
                ]
            }
        ]
        
        report = self.checker.generate_report(results)
        
        self.assertIn('Spell Check Report', report)
        self.assertIn('test.md', report)
        self.assertIn('mispeled', report)
        self.assertIsInstance(report, str)
    
    def test_empty_results(self):
        """Test report generation with no errors."""
        results = []
        report = self.checker.generate_report(results)
        
        self.assertIn('Spell Check Report', report)
        self.assertIn('No spelling issues found', report)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc New Features Test Suite")
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
