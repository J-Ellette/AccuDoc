#!/usr/bin/env python3
"""Tests for student project template."""

import unittest
import tempfile
import shutil
from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator
from accudoc.templates import TemplateManager


class TestStudentTemplate(unittest.TestCase):
    """Test student project template."""
    
    def setUp(self):
        """Setup test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Sample repo info
        self.repo_info = {
            'name': 'StudentProject',
            'description': 'A student project',
            'languages': {'Python': 100},
            'frameworks': ['Flask'],
            'files': ['main.py', 'test_main.py', 'README.md'],
            'dependencies': {}
        }
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_student_template_exists(self):
        """Test that student template is registered."""
        manager = TemplateManager()
        templates = manager.list_templates()
        
        template_ids = [t['id'] for t in templates]
        self.assertIn('student', template_ids)
    
    def test_student_template_info(self):
        """Test student template metadata."""
        manager = TemplateManager()
        template = manager.get_template('student')
        
        self.assertEqual(template.name, 'Student Project')
        self.assertIn('student', template.description.lower())
        self.assertIn('academic', template.description.lower())
    
    def test_generate_with_student_template(self):
        """Test generating documentation with student template."""
        generator = DocumentGenerator(self.repo_info, template='student')
        doc = generator.generate_all()
        
        # Check student-specific sections are present
        self.assertIn('Student Information', doc)
        self.assertIn('Learning Objectives', doc)
        self.assertIn('Assignment Requirements', doc)
        self.assertIn('Deliverables', doc)
        self.assertIn('Resources and References', doc)
        self.assertIn('Acknowledgments', doc)
    
    def test_student_info_section(self):
        """Test student information section."""
        generator = DocumentGenerator(self.repo_info, template='student')
        content = generator._generate_student_info()
        
        self.assertIn('Student Information', content)
        self.assertIn('Project Title', content)
        self.assertIn('Student Name', content)
        self.assertIn('Student ID', content)
        self.assertIn('Course', content)
        self.assertIn('Instructor', content)
    
    def test_learning_objectives_section(self):
        """Test learning objectives section."""
        generator = DocumentGenerator(self.repo_info, template='student')
        content = generator._generate_learning_objectives()
        
        self.assertIn('Learning Objectives', content)
        self.assertIn('Python', content)  # Should mention the language
        self.assertIn('Flask', content)   # Should mention the framework
        self.assertIn('best practices', content)
    
    def test_assignment_requirements_section(self):
        """Test assignment requirements section."""
        generator = DocumentGenerator(self.repo_info, template='student')
        content = generator._generate_assignment_requirements()
        
        self.assertIn('Assignment Requirements', content)
        self.assertIn('Functional Requirements', content)
        self.assertIn('Technical Requirements', content)
        self.assertIn('Documentation Requirements', content)
        # Check for checkboxes
        self.assertIn('[ ]', content)
    
    def test_testing_section_with_tests(self):
        """Test testing section when tests are present."""
        generator = DocumentGenerator(self.repo_info, template='student')
        content = generator._generate_testing_section()
        
        self.assertIn('Testing', content)
        self.assertIn('Running Tests', content)
        self.assertIn('pytest', content)  # Python test framework
    
    def test_testing_section_without_tests(self):
        """Test testing section when no tests are present."""
        repo_info = self.repo_info.copy()
        repo_info['files'] = ['main.py', 'README.md']  # No test files
        
        generator = DocumentGenerator(repo_info, template='student')
        content = generator._generate_testing_section()
        
        self.assertIn('Testing', content)
        self.assertIn('Test Plan', content)
        self.assertIn('Manual Testing', content)
    
    def test_deliverables_section(self):
        """Test deliverables section."""
        generator = DocumentGenerator(self.repo_info, template='student')
        content = generator._generate_deliverables()
        
        self.assertIn('Deliverables', content)
        self.assertIn('Code Deliverables', content)
        self.assertIn('Documentation Deliverables', content)
        self.assertIn('[ ]', content)  # Checkboxes
    
    def test_resources_section(self):
        """Test resources and references section."""
        generator = DocumentGenerator(self.repo_info, template='student')
        content = generator._generate_resources()
        
        self.assertIn('Resources and References', content)
        self.assertIn('Documentation', content)
        self.assertIn('Libraries and Tools', content)
        self.assertIn('Learning Resources', content)
    
    def test_acknowledgments_section(self):
        """Test acknowledgments section."""
        generator = DocumentGenerator(self.repo_info, template='student')
        content = generator._generate_acknowledgments()
        
        self.assertIn('Acknowledgments', content)
        self.assertIn('Instructor', content)
        self.assertIn('Teaching Assistants', content)
        self.assertIn('Classmates', content)
    
    def test_student_template_sections_order(self):
        """Test that sections are in the correct order."""
        generator = DocumentGenerator(self.repo_info, template='student')
        doc = generator.generate_all()
        
        # Check order of key sections
        student_info_pos = doc.find('Student Information')
        learning_obj_pos = doc.find('Learning Objectives')
        requirements_pos = doc.find('Assignment Requirements')
        deliverables_pos = doc.find('Deliverables')
        
        self.assertGreater(learning_obj_pos, student_info_pos)
        self.assertGreater(requirements_pos, learning_obj_pos)
        self.assertGreater(deliverables_pos, requirements_pos)


if __name__ == '__main__':
    unittest.main()
