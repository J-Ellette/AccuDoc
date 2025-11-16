"""
Test suite for data export feature.
"""

import unittest
import json
import csv
import tempfile
import os
from pathlib import Path
from accudoc.data_export import DataExporter, export_data


class TestDataExporter(unittest.TestCase):
    """Test cases for DataExporter."""
    
    def setUp(self):
        """Set up test repository info."""
        self.repo_info = {
            'name': 'TestProject',
            'path': '/test/path',
            'files_count': 50,
            'languages': {
                'Python': 30,
                'JavaScript': 15,
                'HTML': 5,
            },
            'dependencies': {
                'pip': [
                    {'name': 'flask', 'version': '2.0.0'},
                    {'name': 'requests', 'version': '2.28.0'},
                ],
                'npm': [
                    {'name': 'react', 'version': '18.0.0'},
                ]
            },
            'todos': [
                {'file': 'app.py', 'line': 42, 'type': 'TODO', 'comment': 'Implement feature'},
                {'file': 'utils.py', 'line': 15, 'type': 'FIXME', 'comment': 'Fix bug'},
            ],
            'statistics': {
                'total_lines': 5000,
                'code_lines': 3500,
                'comment_lines': 800,
                'blank_lines': 700,
                'by_language': {
                    'Python': {'lines': 3000},
                    'JavaScript': {'lines': 1500},
                    'HTML': {'lines': 500},
                }
            },
            'license': 'MIT'
        }
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test exporter initialization."""
        exporter = DataExporter(self.repo_info)
        self.assertEqual(exporter.repo_info, self.repo_info)
    
    def test_export_files_csv(self):
        """Test exporting files statistics to CSV."""
        exporter = DataExporter(self.repo_info)
        created_files = exporter.export_to_csv(self.temp_dir, report_type='files')
        
        self.assertEqual(len(created_files), 1)
        self.assertTrue(os.path.exists(created_files[0]))
        
        # Read and verify CSV content
        with open(created_files[0], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)  # 3 languages
            self.assertIn('Language', rows[0])
            self.assertIn('File Count', rows[0])
    
    def test_export_dependencies_csv(self):
        """Test exporting dependencies to CSV."""
        exporter = DataExporter(self.repo_info)
        created_files = exporter.export_to_csv(self.temp_dir, report_type='dependencies')
        
        self.assertEqual(len(created_files), 1)
        self.assertTrue(os.path.exists(created_files[0]))
        
        # Read and verify CSV content
        with open(created_files[0], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)  # 2 pip + 1 npm
            self.assertIn('Package Manager', rows[0])
            self.assertIn('Dependency', rows[0])
            self.assertIn('Version', rows[0])
    
    def test_export_todos_csv(self):
        """Test exporting TODOs to CSV."""
        exporter = DataExporter(self.repo_info)
        created_files = exporter.export_to_csv(self.temp_dir, report_type='todos')
        
        self.assertEqual(len(created_files), 1)
        self.assertTrue(os.path.exists(created_files[0]))
        
        # Read and verify CSV content
        with open(created_files[0], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)  # 2 todos
            self.assertIn('File', rows[0])
            self.assertIn('Type', rows[0])
            self.assertIn('Comment', rows[0])
    
    def test_export_metrics_csv(self):
        """Test exporting code metrics to CSV."""
        exporter = DataExporter(self.repo_info)
        created_files = exporter.export_to_csv(self.temp_dir, report_type='metrics')
        
        self.assertEqual(len(created_files), 1)
        self.assertTrue(os.path.exists(created_files[0]))
        
        # Read and verify CSV content
        with open(created_files[0], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertGreater(len(rows), 5)  # At least 5 basic metrics
            self.assertIn('Metric', rows[0])
            self.assertIn('Value', rows[0])
    
    def test_export_languages_csv(self):
        """Test exporting language breakdown to CSV."""
        exporter = DataExporter(self.repo_info)
        created_files = exporter.export_to_csv(self.temp_dir, report_type='languages')
        
        self.assertEqual(len(created_files), 1)
        self.assertTrue(os.path.exists(created_files[0]))
        
        # Read and verify CSV content
        with open(created_files[0], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)  # 3 languages
            self.assertIn('Language', rows[0])
            self.assertIn('Percentage', rows[0])
            self.assertIn('Lines of Code', rows[0])
    
    def test_export_all_csv(self):
        """Test exporting all reports to CSV."""
        exporter = DataExporter(self.repo_info)
        created_files = exporter.export_to_csv(self.temp_dir, report_type='all')
        
        # Should create multiple files
        self.assertGreater(len(created_files), 3)
        
        # Verify all files exist
        for file_path in created_files:
            self.assertTrue(os.path.exists(file_path))
    
    def test_export_summary_csv(self):
        """Test exporting summary CSV."""
        exporter = DataExporter(self.repo_info)
        output_file = os.path.join(self.temp_dir, 'summary.csv')
        result = exporter.export_summary_csv(output_file)
        
        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))
        
        # Read and verify content
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertGreater(len(rows), 5)
            self.assertIn('Category', rows[0])
            self.assertIn('Metric', rows[0])
            self.assertIn('Value', rows[0])
    
    def test_export_to_json(self):
        """Test exporting to JSON."""
        exporter = DataExporter(self.repo_info)
        output_file = os.path.join(self.temp_dir, 'export.json')
        result = exporter.export_to_json(output_file)
        
        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))
        
        # Read and verify JSON content
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['name'], 'TestProject')
            self.assertEqual(data['files_count'], 50)
    
    def test_export_data_function_csv(self):
        """Test export_data function with CSV format."""
        created_files = export_data(self.repo_info, self.temp_dir, format='csv', report_type='all')
        
        self.assertGreater(len(created_files), 0)
        for file_path in created_files:
            self.assertTrue(os.path.exists(file_path))
    
    def test_export_data_function_json(self):
        """Test export_data function with JSON format."""
        output_file = os.path.join(self.temp_dir, 'data.json')
        created_files = export_data(self.repo_info, output_file, format='json')
        
        self.assertEqual(len(created_files), 1)
        self.assertTrue(os.path.exists(created_files[0]))
    
    def test_export_data_function_summary(self):
        """Test export_data function with summary format."""
        output_file = os.path.join(self.temp_dir, 'summary.csv')
        created_files = export_data(self.repo_info, output_file, format='summary')
        
        self.assertEqual(len(created_files), 1)
        self.assertTrue(os.path.exists(created_files[0]))
    
    def test_empty_dependencies(self):
        """Test handling of empty dependencies."""
        repo_info = {'name': 'Test', 'dependencies': {}, 'languages': {'Python': 1}}
        exporter = DataExporter(repo_info)
        created_files = exporter.export_to_csv(self.temp_dir, report_type='dependencies')
        
        # Should not create file if no dependencies
        self.assertEqual(len(created_files), 0)
    
    def test_empty_todos(self):
        """Test handling of empty TODOs."""
        repo_info = {'name': 'Test', 'todos': [], 'languages': {'Python': 1}}
        exporter = DataExporter(repo_info)
        created_files = exporter.export_to_csv(self.temp_dir, report_type='todos')
        
        # Should not create file if no TODOs
        self.assertEqual(len(created_files), 0)


def run_tests():
    """Run all tests and print results."""
    print("=" * 60)
    print("Testing Data Export Feature")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataExporter)
    
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
