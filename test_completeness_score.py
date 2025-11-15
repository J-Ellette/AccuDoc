"""
Test suite for Documentation Completeness Score feature.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from accudoc.completeness_score import CompletenessScorer


class TestCompletenessScorer(unittest.TestCase):
    """Test documentation completeness scoring."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_empty_repository(self):
        """Test scoring an empty repository."""
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        self.assertIn('overall_score', results)
        self.assertIn('grade', results)
        self.assertIn('scores', results)
        self.assertIn('gaps', results)
        
        # Empty repo should have low score
        self.assertLess(results['overall_score'], 50)
    
    def test_readme_detection(self):
        """Test README file detection and scoring."""
        # Create a comprehensive README
        readme = self.repo_path / 'README.md'
        readme.write_text('''
# Test Project

A great test project with all the features.

## Installation

```bash
pip install test-project
```

## Usage

Here's how to use it.

## Features

- Feature 1
- Feature 2

## Contributing

Please contribute!

## License

MIT License
''')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        readme_score = results['scores']['readme']
        self.assertTrue(readme_score['found'])
        self.assertGreater(readme_score['score'], 80)
        self.assertEqual(readme_score['quality'], 'excellent')
    
    def test_license_detection(self):
        """Test LICENSE file detection."""
        # Create LICENSE file
        (self.repo_path / 'LICENSE').write_text('MIT License')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        license_score = results['scores']['license']
        self.assertTrue(license_score['found'])
        self.assertEqual(license_score['score'], 100)
    
    def test_contributing_detection(self):
        """Test CONTRIBUTING file detection."""
        # Create CONTRIBUTING file
        (self.repo_path / 'CONTRIBUTING.md').write_text('# Contributing Guide')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        contrib_score = results['scores']['contributing']
        self.assertTrue(contrib_score['found'])
        self.assertEqual(contrib_score['score'], 100)
    
    def test_code_documentation(self):
        """Test code documentation scoring."""
        # Create well-documented Python file
        py_file = self.repo_path / 'test.py'
        py_file.write_text('''
"""Module docstring."""

class MyClass:
    """Class docstring."""
    
    def method(self):
        """Method docstring."""
        pass

def my_function():
    """Function docstring."""
    return 1
''')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        code_score = results['scores']['code_documentation']
        self.assertGreater(code_score['score'], 90)
        self.assertEqual(code_score['documented_modules'], 1)
        self.assertEqual(code_score['documented_classes'], 1)
        self.assertEqual(code_score['documented_functions'], 2)
    
    def test_undocumented_code(self):
        """Test detection of undocumented code."""
        # Create poorly documented Python file
        py_file = self.repo_path / 'test.py'
        py_file.write_text('''
def function1():
    return 1

def function2():
    return 2

class MyClass:
    def method(self):
        pass
''')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        code_score = results['scores']['code_documentation']
        self.assertEqual(code_score['score'], 0)
        self.assertGreater(code_score['total_functions'], 0)
        self.assertEqual(code_score['documented_functions'], 0)
    
    def test_comments_analysis(self):
        """Test inline comments analysis."""
        # Create file with comments
        py_file = self.repo_path / 'test.py'
        py_file.write_text('''
"""Module docstring."""

def my_function():
    # This is a comment
    x = 1  # Another comment
    # More comments
    return x
''')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        comments_score = results['scores']['comments']
        self.assertGreater(comments_score['comment_lines'], 0)
        self.assertGreater(comments_score['comment_ratio'], 0)
    
    def test_changelog_detection(self):
        """Test CHANGELOG file detection."""
        (self.repo_path / 'CHANGELOG.md').write_text('# Changelog')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        changelog_score = results['scores']['changelog']
        self.assertTrue(changelog_score['found'])
        self.assertEqual(changelog_score['score'], 100)
    
    def test_examples_detection(self):
        """Test examples/demos detection."""
        # Create example files
        (self.repo_path / 'example.py').write_text('# Example code')
        (self.repo_path / 'demo.py').write_text('# Demo code')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        examples_score = results['scores']['examples']
        self.assertTrue(examples_score['found'])
        self.assertGreaterEqual(examples_score['count'], 2)
        self.assertGreater(examples_score['score'], 0)
    
    def test_grade_calculation(self):
        """Test grade letter calculation."""
        scorer = CompletenessScorer(str(self.repo_path))
        
        self.assertEqual(scorer._calculate_grade(95), 'A')
        self.assertEqual(scorer._calculate_grade(85), 'B')
        self.assertEqual(scorer._calculate_grade(75), 'C')
        self.assertEqual(scorer._calculate_grade(65), 'D')
        self.assertEqual(scorer._calculate_grade(50), 'F')
    
    def test_gaps_identification(self):
        """Test identification of documentation gaps."""
        # Create minimal repository
        (self.repo_path / 'README.md').write_text('# Test')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        gaps = results['gaps']
        self.assertGreater(len(gaps), 0)
        
        # Check gap structure
        for gap in gaps:
            self.assertIn('category', gap)
            self.assertIn('severity', gap)
            self.assertIn('message', gap)
            self.assertIn('recommendation', gap)
    
    def test_complete_repository(self):
        """Test a well-documented repository."""
        # Create comprehensive documentation
        (self.repo_path / 'README.md').write_text('''
# Test Project

Description of the project.

## Installation

Install instructions here.

## Usage

Usage instructions here.

## Features

List of features.

## Contributing

Contribution guidelines.

## License

MIT License
''')
        (self.repo_path / 'LICENSE').write_text('MIT License')
        (self.repo_path / 'CONTRIBUTING.md').write_text('# Contributing')
        (self.repo_path / 'CHANGELOG.md').write_text('# Changelog')
        (self.repo_path / 'example.py').write_text('# Example')
        
        # Create documented code
        (self.repo_path / 'main.py').write_text('''
"""Main module."""

class App:
    """Application class."""
    
    def run(self):
        """Run the application."""
        pass

def main():
    """Main entry point."""
    pass
''')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        # Should have high score
        self.assertGreater(results['overall_score'], 70)
        self.assertIn(results['grade'], ['A', 'B', 'C'])
    
    def test_generate_report(self):
        """Test report generation."""
        (self.repo_path / 'README.md').write_text('# Test')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        report = scorer.generate_report(results)
        
        self.assertIn('Documentation Completeness Report', report)
        self.assertIn('Overall Score', report)
        self.assertIn('Category Scores', report)
        self.assertIn('Next Steps', report)
        self.assertIsInstance(report, str)
    
    def test_summary_metrics(self):
        """Test summary metrics calculation."""
        (self.repo_path / 'README.md').write_text('# Test')
        (self.repo_path / 'LICENSE').write_text('MIT')
        
        scorer = CompletenessScorer(str(self.repo_path))
        results = scorer.analyze_repository()
        
        summary = results['summary']
        self.assertIn('total_files_analyzed', summary)
        self.assertIn('missing_critical', summary)
        self.assertIn('missing_important', summary)
        self.assertIn('missing_optional', summary)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Completeness Scorer Test Suite")
    print("=" * 60)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCompletenessScorer)
    
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
