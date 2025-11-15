"""
Test suite for Phase 2 AccuDoc features:
- Multi-Repository Support
- Test Coverage Analysis
- Readability Metrics
- Database Schema Extraction
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from accudoc.multi_repo import MultiRepositoryManager
from accudoc.test_coverage import TestCoverageAnalyzer as CoverageAnalyzer
from accudoc.readability import ReadabilityAnalyzer
from accudoc.db_schema import DatabaseSchemaExtractor


class TestMultiRepository(unittest.TestCase):
    """Test multi-repository support."""
    
    def setUp(self):
        """Set up test repositories."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create two simple test repositories
        for i in range(2):
            repo_dir = Path(self.test_dir) / f'repo{i+1}'
            repo_dir.mkdir()
            (repo_dir / f'file{i+1}.py').write_text(f'# Repo {i+1}')
            (repo_dir / 'README.md').write_text(f'# Repository {i+1}')
    
    def tearDown(self):
        """Clean up test repositories."""
        shutil.rmtree(self.test_dir)
    
    def test_scan_repositories(self):
        """Test scanning multiple repositories."""
        manager = MultiRepositoryManager(max_workers=2)
        
        repositories = [
            {'path': str(Path(self.test_dir) / 'repo1'), 'name': 'Repo1', 'group': 'Test'},
            {'path': str(Path(self.test_dir) / 'repo2'), 'name': 'Repo2', 'group': 'Test'}
        ]
        
        results = manager.scan_repositories(repositories)
        
        self.assertEqual(results['summary']['total'], 2)
        self.assertIn('Repo1', results['repositories'])
        self.assertIn('Repo2', results['repositories'])
    
    def test_generate_unified_documentation(self):
        """Test unified documentation generation."""
        manager = MultiRepositoryManager()
        
        # Mock scan results
        scan_results = {
            'summary': {'total': 2, 'successful': 2, 'failed': 0},
            'repositories': {
                'Repo1': {
                    'status': 'success',
                    'config': {'path': 'repo1', 'group': 'Test'},
                    'scan': {'name': 'Repo1', 'languages': {'Python': 1}, 'files': ['file1.py'], 'dependencies': {}}
                },
                'Repo2': {
                    'status': 'success',
                    'config': {'path': 'repo2', 'group': 'Test'},
                    'scan': {'name': 'Repo2', 'languages': {'Python': 1}, 'files': ['file2.py'], 'dependencies': {}}
                }
            }
        }
        
        doc = manager.generate_unified_documentation(scan_results)
        
        self.assertIn('Multi-Repository Documentation', doc)
        self.assertIn('Repo1', doc)
        self.assertIn('Repo2', doc)
    
    def test_generate_comparison_matrix(self):
        """Test comparison matrix generation."""
        manager = MultiRepositoryManager()
        
        scan_results = {
            'repositories': {
                'Repo1': {
                    'status': 'success',
                    'scan': {'languages': {'Python': 1}, 'dependencies': {'pip': ['requests']}}
                }
            }
        }
        
        matrix = manager.generate_comparison_matrix(scan_results)
        
        self.assertIn('Comparison Matrix', matrix)
        self.assertIn('Python', matrix)


class TestCoverageAnalysis(unittest.TestCase):
    """Test test coverage analysis."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_detect_coverage_files(self):
        """Test coverage file detection."""
        # Create fake coverage file
        (self.repo_path / 'coverage.xml').write_text('<coverage></coverage>')
        
        analyzer = CoverageAnalyzer(str(self.repo_path))
        files = analyzer.detect_coverage_files()
        
        self.assertIn('python', files)
        self.assertTrue(len(files['python']) > 0)
    
    def test_parse_python_coverage_xml(self):
        """Test Python coverage XML parsing."""
        coverage_xml = '''<?xml version="1.0" ?>
<coverage version="5.5" timestamp="1234567890" lines-covered="80" lines-valid="100" line-rate="0.8" branch-rate="0.75">
    <packages>
        <package name="mypackage" line-rate="0.8">
            <classes>
                <class name="module.py" filename="mypackage/module.py" line-rate="0.8">
                </class>
            </classes>
        </package>
    </packages>
</coverage>'''
        
        xml_file = self.repo_path / 'coverage.xml'
        xml_file.write_text(coverage_xml)
        
        analyzer = CoverageAnalyzer(str(self.repo_path))
        coverage = analyzer.parse_python_coverage_xml(xml_file)
        
        self.assertIsNotNone(coverage)
        self.assertEqual(coverage['tool'], 'python-coverage')
        self.assertEqual(coverage['overall']['line_rate'], 80.0)
    
    def test_generate_coverage_report(self):
        """Test coverage report generation."""
        analyzer = CoverageAnalyzer(str(self.repo_path))
        
        coverage_data = {
            'status': 'success',
            'coverage_data': [{
                'tool': 'python-coverage',
                'overall': {
                    'line_rate': 85.5,
                    'branch_rate': 75.0,
                    'lines_covered': 855,
                    'lines_valid': 1000
                },
                'files': []
            }]
        }
        
        report = analyzer.generate_coverage_report(coverage_data)
        
        self.assertIn('Test Coverage Report', report)
        self.assertIn('85.5', report)


class TestReadabilityAnalyzer(unittest.TestCase):
    """Test readability analysis."""
    
    def setUp(self):
        """Set up analyzer."""
        self.analyzer = ReadabilityAnalyzer()
    
    def test_count_syllables(self):
        """Test syllable counting."""
        self.assertEqual(self.analyzer._count_syllables('hello'), 2)
        self.assertEqual(self.analyzer._count_syllables('documentation'), 5)
        self.assertEqual(self.analyzer._count_syllables('the'), 1)
    
    def test_analyze_text(self):
        """Test text analysis."""
        text = """
        This is a simple test document. It contains multiple sentences.
        The purpose is to test readability analysis. We want to ensure
        the analyzer can calculate various metrics correctly.
        """
        
        result = self.analyzer.analyze_text(text)
        
        self.assertIn('statistics', result)
        self.assertIn('scores', result)
        self.assertGreater(result['statistics']['sentences'], 0)
        self.assertGreater(result['statistics']['words'], 0)
        self.assertIn('flesch_reading_ease', result['scores'])
    
    def test_analyze_file(self):
        """Test file analysis."""
        test_dir = tempfile.mkdtemp()
        try:
            test_file = Path(test_dir) / 'test.md'
            test_file.write_text('# Test\n\nThis is a test document with some content.')
            
            result = self.analyzer.analyze_file(test_file)
            
            self.assertIn('file', result)
            self.assertIn('statistics', result)
        finally:
            shutil.rmtree(test_dir)
    
    def test_interpret_score(self):
        """Test score interpretation."""
        interpretation = self.analyzer.interpret_score('flesch_reading_ease', 85)
        self.assertIn('Easy', interpretation)
        
        interpretation = self.analyzer.interpret_score('flesch_kincaid_grade', 8)
        self.assertIn('Middle School', interpretation)
    
    def test_generate_report(self):
        """Test report generation."""
        results = [{
            'file': 'test.md',
            'statistics': {
                'sentences': 5,
                'words': 50,
                'syllables': 75,
                'complex_words': 10,
                'characters': 250,
                'avg_words_per_sentence': 10,
                'avg_syllables_per_word': 1.5,
                'avg_chars_per_word': 5
            },
            'scores': {
                'flesch_reading_ease': 75.0,
                'flesch_kincaid_grade': 7.5,
                'gunning_fog': 8.0,
                'coleman_liau': 8.5,
                'ari': 7.0
            }
        }]
        
        report = self.analyzer.generate_report(results)
        
        self.assertIn('Readability Report', report)
        self.assertIn('75.0', report)


class TestDatabaseSchemaExtractor(unittest.TestCase):
    """Test database schema extraction."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_find_schema_files(self):
        """Test schema file detection."""
        # Create fake schema files
        migrations_dir = self.repo_path / 'migrations'
        migrations_dir.mkdir()
        (migrations_dir / '001_initial.sql').write_text('CREATE TABLE users (id INT);')
        
        extractor = DatabaseSchemaExtractor(str(self.repo_path))
        files = extractor.find_schema_files()
        
        self.assertIn('sql_migrations', files)
    
    def test_parse_sql_create_table(self):
        """Test SQL CREATE TABLE parsing."""
        sql = '''
        CREATE TABLE users (
            id INT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        
        extractor = DatabaseSchemaExtractor(str(self.repo_path))
        tables = extractor.parse_sql_create_table(sql)
        
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]['name'], 'users')
        self.assertGreater(len(tables[0]['columns']), 0)
    
    def test_parse_django_models(self):
        """Test Django model parsing."""
        models_content = '''
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
'''
        
        models_file = self.repo_path / 'models.py'
        models_file.write_text(models_content)
        
        extractor = DatabaseSchemaExtractor(str(self.repo_path))
        models = extractor.parse_django_models(models_file)
        
        self.assertGreater(len(models), 0)
        if models:
            self.assertIn('name', models[0])
            self.assertIn('fields', models[0])
    
    def test_generate_schema_documentation(self):
        """Test schema documentation generation."""
        extractor = DatabaseSchemaExtractor(str(self.repo_path))
        
        schema = {
            'status': 'success',
            'tables': [{
                'name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'INT', 'primary_key': True, 'not_null': True, 'unique': False, 'has_default': False},
                    {'name': 'username', 'type': 'VARCHAR(100)', 'primary_key': False, 'not_null': True, 'unique': True, 'has_default': False}
                ],
                'constraints': []
            }],
            'models': [],
            'source_files': ['schema.sql']
        }
        
        doc = extractor.generate_schema_documentation(schema)
        
        self.assertIn('Database Schema', doc)
        self.assertIn('users', doc)


def run_tests():
    """Run all Phase 2 tests."""
    print("=" * 60)
    print("AccuDoc Phase 2 Features Test Suite")
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
