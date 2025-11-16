"""
Test suite for custom reports feature.
"""

import unittest
import tempfile
import os
import shutil
import json
from accudoc.custom_reports import (
    ReportTemplate, CustomReportGenerator, create_sample_template
)


class TestReportTemplate(unittest.TestCase):
    """Test cases for ReportTemplate."""
    
    def test_initialization(self):
        """Test template initialization."""
        template_data = {
            'name': 'Test Template',
            'description': 'A test template',
            'format': 'markdown',
            'sections': [
                {'title': 'Section 1', 'data': ['name']}
            ]
        }
        
        template = ReportTemplate(template_data)
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.format, 'markdown')
        self.assertEqual(len(template.sections), 1)
    
    def test_validation_success(self):
        """Test successful validation."""
        template_data = {
            'name': 'Valid Template',
            'sections': [
                {'title': 'Section 1', 'content': 'Test content'}
            ]
        }
        
        template = ReportTemplate(template_data)
        errors = template.validate()
        self.assertEqual(len(errors), 0)
    
    def test_validation_no_name(self):
        """Test validation fails without name."""
        template_data = {
            'sections': [
                {'title': 'Section 1', 'content': 'Test'}
            ]
        }
        
        template = ReportTemplate(template_data)
        errors = template.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('name' in err for err in errors))
    
    def test_validation_no_sections(self):
        """Test validation fails without sections."""
        template_data = {
            'name': 'Test',
            'sections': []
        }
        
        template = ReportTemplate(template_data)
        errors = template.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('section' in err for err in errors))
    
    def test_validation_section_no_title(self):
        """Test validation fails for section without title."""
        template_data = {
            'name': 'Test',
            'sections': [
                {'content': 'Test content'}
            ]
        }
        
        template = ReportTemplate(template_data)
        errors = template.validate()
        self.assertGreater(len(errors), 0)


class TestCustomReportGenerator(unittest.TestCase):
    """Test cases for CustomReportGenerator."""
    
    def setUp(self):
        """Set up test repository data."""
        self.repo_info = {
            'name': 'TestProject',
            'path': '/test/project',
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
                    {'name': 'flask', 'version': '2.0.0'}
                ]
            },
            'documentation': ['README.md', 'CONTRIBUTING.md'],
            'api_docs': [{'name': 'api1'}],
            'code_examples': [{'file': 'example.py'}],
            'todos': [
                {'file': 'app.py', 'line': 1, 'type': 'TODO', 'comment': 'Test'}
            ],
            'license': 'MIT'
        }
    
    def test_initialization(self):
        """Test generator initialization."""
        generator = CustomReportGenerator(self.repo_info)
        self.assertEqual(generator.repo_info, self.repo_info)
    
    def test_list_builtin_templates(self):
        """Test listing built-in templates."""
        generator = CustomReportGenerator(self.repo_info)
        templates = generator.list_builtin_templates()
        
        self.assertGreater(len(templates), 0)
        self.assertIn('name', templates[0])
        self.assertIn('title', templates[0])
        self.assertIn('description', templates[0])
    
    def test_get_builtin_template(self):
        """Test getting built-in template."""
        generator = CustomReportGenerator(self.repo_info)
        template = generator.get_builtin_template('minimal')
        
        self.assertIsInstance(template, ReportTemplate)
        self.assertEqual(template.name, 'Minimal Report')
    
    def test_get_unknown_builtin_template(self):
        """Test getting unknown built-in template."""
        generator = CustomReportGenerator(self.repo_info)
        
        with self.assertRaises(ValueError):
            generator.get_builtin_template('nonexistent')
    
    def test_prepare_context(self):
        """Test context preparation."""
        generator = CustomReportGenerator(self.repo_info)
        context = generator._prepare_context()
        
        self.assertIn('name', context)
        self.assertIn('languages_list', context)
        self.assertIn('dependencies_count', context)
        self.assertIn('generated_date', context)
    
    def test_get_nested_value(self):
        """Test getting nested values."""
        generator = CustomReportGenerator(self.repo_info)
        
        value = generator._get_nested_value(self.repo_info, 'name')
        self.assertEqual(value, 'TestProject')
        
        value = generator._get_nested_value(self.repo_info, 'statistics.total_lines')
        self.assertEqual(value, 10000)
        
        value = generator._get_nested_value(self.repo_info, 'nonexistent.path')
        self.assertIsNone(value)
    
    def test_replace_variables(self):
        """Test variable replacement."""
        generator = CustomReportGenerator(self.repo_info)
        context = {'name': 'TestProject', 'files_count': 100}
        
        text = "Project: {name}, Files: {files_count}"
        result = generator._replace_variables(text, context)
        
        self.assertEqual(result, "Project: TestProject, Files: 100")
    
    def test_format_field_simple(self):
        """Test formatting simple field."""
        generator = CustomReportGenerator(self.repo_info)
        
        result = generator._format_field('name', 'TestProject')
        self.assertIn('Name', result)
        self.assertIn('TestProject', result)
    
    def test_format_field_dict(self):
        """Test formatting dictionary field."""
        generator = CustomReportGenerator(self.repo_info)
        
        value = {'Python': 70, 'JavaScript': 30}
        result = generator._format_field('languages', value)
        
        self.assertIn('Languages', result)
        self.assertIn('Python', result)
        self.assertIn('70', result)
    
    def test_format_field_list(self):
        """Test formatting list field."""
        generator = CustomReportGenerator(self.repo_info)
        
        value = ['item1', 'item2', 'item3']
        result = generator._format_field('items', value)
        
        self.assertIn('Items', result)
        self.assertIn('item1', result)
    
    def test_generate_minimal_template(self):
        """Test generating minimal template."""
        generator = CustomReportGenerator(self.repo_info)
        template = generator.get_builtin_template('minimal')
        
        report = generator.generate(template)
        
        self.assertIn('Minimal Report', report)
        self.assertIn('Project Overview', report)
        self.assertIn('TestProject', report)
    
    def test_generate_detailed_template(self):
        """Test generating detailed template."""
        generator = CustomReportGenerator(self.repo_info)
        template = generator.get_builtin_template('detailed')
        
        report = generator.generate(template)
        
        self.assertIn('Detailed Report', report)
        self.assertIn('Project Information', report)
        self.assertIn('Code Statistics', report)
    
    def test_generate_executive_template(self):
        """Test generating executive template."""
        generator = CustomReportGenerator(self.repo_info)
        template = generator.get_builtin_template('executive')
        
        report = generator.generate(template)
        
        self.assertIn('Executive Summary', report)
        self.assertIn('TestProject', report)
    
    def test_generate_technical_template(self):
        """Test generating technical template."""
        generator = CustomReportGenerator(self.repo_info)
        template = generator.get_builtin_template('technical')
        
        report = generator.generate(template)
        
        self.assertIn('Technical Deep Dive', report)
        self.assertIn('Architecture', report)
    
    def test_generate_custom_template(self):
        """Test generating custom template."""
        generator = CustomReportGenerator(self.repo_info)
        
        template_data = {
            'name': 'Custom Test Report',
            'format': 'markdown',
            'sections': [
                {
                    'title': 'Custom Section',
                    'content': 'Project: {name}'
                }
            ]
        }
        
        template = ReportTemplate(template_data)
        report = generator.generate(template)
        
        self.assertIn('Custom Test Report', report)
        self.assertIn('Custom Section', report)
        self.assertIn('TestProject', report)
    
    def test_generate_with_data_section(self):
        """Test generating with data section."""
        generator = CustomReportGenerator(self.repo_info)
        
        template_data = {
            'name': 'Data Test',
            'format': 'markdown',
            'sections': [
                {
                    'title': 'Stats',
                    'data': ['files_count', 'languages']
                }
            ]
        }
        
        template = ReportTemplate(template_data)
        report = generator.generate(template)
        
        self.assertIn('Stats', report)
        self.assertIn('100', report)
    
    def test_load_template_from_file(self):
        """Test loading template from JSON file."""
        generator = CustomReportGenerator(self.repo_info)
        
        temp_dir = tempfile.mkdtemp()
        try:
            template_file = os.path.join(temp_dir, 'template.json')
            template_data = {
                'name': 'File Template',
                'sections': [
                    {'title': 'Section', 'content': 'Test'}
                ]
            }
            
            with open(template_file, 'w') as f:
                json.dump(template_data, f)
            
            template = generator.load_template(template_file)
            self.assertEqual(template.name, 'File Template')
        finally:
            shutil.rmtree(temp_dir)
    
    def test_save_template(self):
        """Test saving template to file."""
        generator = CustomReportGenerator(self.repo_info)
        
        template_data = {
            'name': 'Save Test',
            'sections': [{'title': 'Test', 'content': 'Content'}]
        }
        
        template = ReportTemplate(template_data)
        
        temp_dir = tempfile.mkdtemp()
        try:
            output_file = os.path.join(temp_dir, 'saved_template.json')
            generator.save_template(template, output_file)
            
            self.assertTrue(os.path.exists(output_file))
            
            with open(output_file, 'r') as f:
                loaded_data = json.load(f)
            
            self.assertEqual(loaded_data['name'], 'Save Test')
        finally:
            shutil.rmtree(temp_dir)
    
    def test_format_markdown(self):
        """Test markdown formatting."""
        generator = CustomReportGenerator(self.repo_info)
        sections = ['## Section 1\nContent 1', '## Section 2\nContent 2']
        
        result = generator._format_markdown('Test Report', sections)
        
        self.assertIn('# Test Report', result)
        self.assertIn('Section 1', result)
        self.assertIn('Section 2', result)
    
    def test_format_html(self):
        """Test HTML formatting."""
        generator = CustomReportGenerator(self.repo_info)
        sections = ['## Section 1\n**Bold text**']
        
        result = generator._format_html('Test Report', sections)
        
        self.assertIn('<html>', result)
        self.assertIn('<title>Test Report</title>', result)
        self.assertIn('Section 1', result)
    
    def test_format_text(self):
        """Test text formatting."""
        generator = CustomReportGenerator(self.repo_info)
        sections = ['## Section 1\n**Bold**']
        
        result = generator._format_text('Test Report', sections)
        
        self.assertIn('TEST REPORT', result)
        self.assertIn('Section 1', result)
        # Should remove markdown
        self.assertNotIn('##', result)
        self.assertNotIn('**', result)


class TestCreateSampleTemplate(unittest.TestCase):
    """Test cases for create_sample_template function."""
    
    def test_create_basic_sample(self):
        """Test creating basic sample template."""
        sample = create_sample_template('basic')
        
        self.assertIn('name', sample)
        self.assertIn('sections', sample)
        self.assertGreater(len(sample['sections']), 0)
    
    def test_create_comprehensive_sample(self):
        """Test creating comprehensive sample template."""
        sample = create_sample_template('comprehensive')
        
        self.assertEqual(sample['name'], 'Comprehensive Report')
        self.assertGreater(len(sample['sections']), 1)


def run_tests():
    """Run all tests and print results."""
    print("=" * 60)
    print("Testing Custom Reports Feature")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestReportTemplate))
    suite.addTests(loader.loadTestsFromTestCase(TestCustomReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestCreateSampleTemplate))
    
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
