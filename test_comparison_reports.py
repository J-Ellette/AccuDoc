"""
Test suite for comparison reports feature.
"""

import unittest
import tempfile
import os
import shutil
import json
from accudoc.comparison_reports import RepositoryComparison


class TestRepositoryComparison(unittest.TestCase):
    """Test cases for RepositoryComparison."""
    
    def setUp(self):
        """Set up test repository data."""
        self.repo1 = {
            'name': 'Project A',
            'path': '/test/projecta',
            'files_count': 100,
            'languages': {'Python': 70, 'JavaScript': 30},
            'statistics': {
                'total_lines': 10000,
                'code_lines': 7000,
                'comment_lines': 2000,
                'blank_lines': 1000
            },
            'dependencies': {
                'pip': [
                    {'name': 'flask', 'version': '2.0.0'},
                    {'name': 'requests', 'version': '2.28.0'}
                ]
            },
            'documentation': ['README.md', 'CONTRIBUTING.md'],
            'api_docs': [{'name': 'api1'}],
            'code_examples': [{'file': 'example1.py'}],
            'todos': [
                {'file': 'app.py', 'line': 1, 'type': 'TODO', 'comment': 'Test'},
                {'file': 'app.py', 'line': 2, 'type': 'FIXME', 'comment': 'Test'}
            ],
            'license': 'MIT'
        }
        
        self.repo2 = {
            'name': 'Project B',
            'path': '/test/projectb',
            'files_count': 150,
            'languages': {'Java': 100, 'Python': 50},
            'statistics': {
                'total_lines': 15000,
                'code_lines': 12000,
                'comment_lines': 2000,
                'blank_lines': 1000
            },
            'dependencies': {
                'maven': [
                    {'name': 'junit', 'version': '4.12'}
                ]
            },
            'documentation': ['README.md'],
            'api_docs': [],
            'code_examples': [],
            'todos': [],
            'license': 'Apache 2.0'
        }
        
        self.repo3 = {
            'name': 'Project C',
            'path': '/test/projectc',
            'files_count': 50,
            'languages': {'Go': 50},
            'statistics': {
                'total_lines': 5000,
                'code_lines': 4000,
                'comment_lines': 500,
                'blank_lines': 500
            },
            'dependencies': {},
            'documentation': ['README.md', 'LICENSE', 'CONTRIBUTING.md'],
            'api_docs': [{'name': 'api1'}, {'name': 'api2'}],
            'code_examples': [{'file': 'ex1.go'}],
            'todos': [{'file': 'main.go', 'line': 1, 'type': 'TODO'}],
            'license': 'BSD'
        }
    
    def test_initialization(self):
        """Test comparison initialization."""
        comparison = RepositoryComparison()
        self.assertEqual(len(comparison.repositories), 0)
    
    def test_add_repository(self):
        """Test adding repositories."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        
        self.assertEqual(len(comparison.repositories), 1)
        self.assertEqual(comparison.repositories[0]['name'], 'Project A')
    
    def test_add_repository_custom_name(self):
        """Test adding repository with custom name."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1, name='Custom Name')
        
        self.assertEqual(comparison.repositories[0]['name'], 'Custom Name')
    
    def test_load_from_json(self):
        """Test loading repository from JSON."""
        temp_dir = tempfile.mkdtemp()
        try:
            json_file = os.path.join(temp_dir, 'repo.json')
            with open(json_file, 'w') as f:
                json.dump(self.repo1, f)
            
            comparison = RepositoryComparison()
            comparison.load_from_json(json_file)
            
            self.assertEqual(len(comparison.repositories), 1)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_compare_minimum_repos(self):
        """Test comparison requires at least 2 repos."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        
        with self.assertRaises(ValueError):
            comparison.compare()
    
    def test_compare_basic(self):
        """Test basic comparison."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        
        result = comparison.compare()
        
        self.assertEqual(result['repository_count'], 2)
        self.assertIn('metrics', result)
        self.assertIn('rankings', result)
        self.assertIn('summary', result)
    
    def test_compare_files(self):
        """Test file comparison."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        
        result = comparison.compare()
        files_data = result['metrics']['files']
        
        self.assertEqual(files_data['Project A']['count'], 100)
        self.assertEqual(files_data['Project B']['count'], 150)
        self.assertEqual(files_data['_max'], 150)
        self.assertEqual(files_data['_min'], 100)
    
    def test_compare_languages(self):
        """Test language comparison."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        
        result = comparison.compare()
        lang_data = result['metrics']['languages']
        
        self.assertIn('Python', lang_data['_all_languages'])
        self.assertIn('Java', lang_data['_all_languages'])
        self.assertIn('JavaScript', lang_data['_all_languages'])
    
    def test_compare_code_stats(self):
        """Test code statistics comparison."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        
        result = comparison.compare()
        stats_data = result['metrics']['code_stats']
        
        self.assertEqual(stats_data['Project A']['total_lines'], 10000)
        self.assertEqual(stats_data['Project B']['total_lines'], 15000)
        self.assertEqual(stats_data['Project A']['comment_ratio'], 20.0)
    
    def test_compare_dependencies(self):
        """Test dependency comparison."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        
        result = comparison.compare()
        deps_data = result['metrics']['dependencies']
        
        self.assertEqual(deps_data['Project A']['total'], 2)
        self.assertEqual(deps_data['Project B']['total'], 1)
    
    def test_compare_documentation(self):
        """Test documentation comparison."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo3)
        
        result = comparison.compare()
        doc_data = result['metrics']['documentation']
        
        self.assertEqual(doc_data['Project A']['doc_files'], 2)
        self.assertEqual(doc_data['Project C']['doc_files'], 3)
    
    def test_compare_todos(self):
        """Test TODO comparison."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        
        result = comparison.compare()
        todo_data = result['metrics']['todos']
        
        self.assertEqual(todo_data['Project A']['count'], 2)
        self.assertEqual(todo_data['Project B']['count'], 0)
    
    def test_compare_licenses(self):
        """Test license comparison."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        
        result = comparison.compare()
        license_data = result['metrics']['license']
        
        self.assertEqual(license_data['Project A'], 'MIT')
        self.assertEqual(license_data['Project B'], 'Apache 2.0')
    
    def test_rankings(self):
        """Test rankings calculation."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        comparison.add_repository(self.repo3)
        
        result = comparison.compare()
        rankings = result['rankings']
        
        self.assertIn('by_files', rankings)
        self.assertIn('by_code_lines', rankings)
        self.assertIn('by_documentation', rankings)
        
        # Project B has most files
        self.assertEqual(rankings['by_files'][0], 'Project B')
        
        # Project C has most documentation
        self.assertEqual(rankings['by_documentation'][0], 'Project C')
    
    def test_summary(self):
        """Test summary generation."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        
        result = comparison.compare()
        summary = result['summary']
        
        self.assertEqual(summary['total_repositories'], 2)
        self.assertIn('best_performers', summary)
        self.assertIn('worst_performers', summary)
    
    def test_generate_report(self):
        """Test report generation."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        comparison.compare()
        
        report = comparison.generate_report()
        
        self.assertIn('REPOSITORY COMPARISON REPORT', report)
        self.assertIn('Project A', report)
        self.assertIn('Project B', report)
        self.assertIn('FILE STATISTICS', report)
        self.assertIn('CODE STATISTICS', report)
    
    def test_export_to_json(self):
        """Test JSON export."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        comparison.compare()
        
        data = comparison.export_to_json()
        
        self.assertIsInstance(data, dict)
        self.assertIn('repository_count', data)
        self.assertIn('metrics', data)
    
    def test_export_to_csv(self):
        """Test CSV export."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        comparison.compare()
        
        temp_dir = tempfile.mkdtemp()
        try:
            files = comparison.export_to_csv(temp_dir)
            
            self.assertGreater(len(files), 0)
            
            # Verify files exist
            for file_path in files:
                self.assertTrue(os.path.exists(file_path))
        finally:
            shutil.rmtree(temp_dir)
    
    def test_three_way_comparison(self):
        """Test comparing three repositories."""
        comparison = RepositoryComparison()
        comparison.add_repository(self.repo1)
        comparison.add_repository(self.repo2)
        comparison.add_repository(self.repo3)
        
        result = comparison.compare()
        
        self.assertEqual(result['repository_count'], 3)
        self.assertEqual(len(result['repository_names']), 3)


def run_tests():
    """Run all tests and print results."""
    print("=" * 60)
    print("Testing Comparison Reports Feature")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRepositoryComparison)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
