#!/usr/bin/env python3
"""Tests for open source documentation generators."""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
from accudoc.opensource_docs import OpenSourceDocsGenerator


class TestOpenSourceDocsGenerator(unittest.TestCase):
    """Test OpenSourceDocsGenerator class."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Sample repo info for Python project
        self.python_repo_info = {
            'name': 'TestProject',
            'description': 'A test project',
            'languages': ['Python'],
            'files': ['requirements.txt', 'setup.py', 'test_sample.py', 'README.md'],
            'dependencies': {'pytest': '6.0.0'}
        }
        
        # Sample repo info for JavaScript project
        self.js_repo_info = {
            'name': 'JSProject',
            'description': 'A JavaScript project',
            'languages': ['JavaScript', 'TypeScript'],
            'files': ['package.json', 'test.js', 'README.md'],
            'dependencies': {'jest': '27.0.0'}
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test generator initialization."""
        generator = OpenSourceDocsGenerator(self.python_repo_info)
        self.assertEqual(generator.repo_name, 'TestProject')
        self.assertEqual(generator.description, 'A test project')
    
    def test_generate_contributing_guide(self):
        """Test CONTRIBUTING.md generation."""
        generator = OpenSourceDocsGenerator(self.python_repo_info)
        content = generator.generate_contributing_guide()
        
        # Check key sections are present
        self.assertIn('# Contributing to TestProject', content)
        self.assertIn('## Table of Contents', content)
        self.assertIn('## Code of Conduct', content)
        self.assertIn('## Getting Started', content)
        self.assertIn('## Development Setup', content)
        self.assertIn('## Coding Guidelines', content)
        self.assertIn('## Pull Request Process', content)
        self.assertIn('## Reporting Bugs', content)
        self.assertIn('## Suggesting Features', content)
        
        # Check Python-specific content
        self.assertIn('Python', content)
        self.assertIn('pip install', content)
        self.assertIn('pytest', content)
        self.assertIn('PEP 8', content)
    
    def test_generate_contributing_guide_javascript(self):
        """Test CONTRIBUTING.md generation for JavaScript project."""
        generator = OpenSourceDocsGenerator(self.js_repo_info)
        content = generator.generate_contributing_guide()
        
        # Check JavaScript-specific content
        self.assertIn('Node.js', content)
        self.assertIn('npm', content)
        self.assertIn('npm test', content)
        self.assertIn('ESLint', content)
    
    def test_generate_bug_template(self):
        """Test bug report template generation."""
        generator = OpenSourceDocsGenerator(self.python_repo_info)
        content = generator.generate_issue_template_bug()
        
        # Check key sections
        self.assertIn('name: Bug Report', content)
        self.assertIn('## Bug Description', content)
        self.assertIn('## Steps to Reproduce', content)
        self.assertIn('## Expected Behavior', content)
        self.assertIn('## Actual Behavior', content)
        self.assertIn('## Environment', content)
        self.assertIn('Python Version', content)
    
    def test_generate_feature_template(self):
        """Test feature request template generation."""
        generator = OpenSourceDocsGenerator(self.python_repo_info)
        content = generator.generate_issue_template_feature()
        
        # Check key sections
        self.assertIn('name: Feature Request', content)
        self.assertIn('## Feature Description', content)
        self.assertIn('## Problem Statement', content)
        self.assertIn('## Proposed Solution', content)
        self.assertIn('## Alternative Solutions', content)
        self.assertIn('## Use Cases', content)
        self.assertIn('## Priority', content)
    
    def test_generate_code_of_conduct(self):
        """Test CODE_OF_CONDUCT.md generation."""
        generator = OpenSourceDocsGenerator(self.python_repo_info)
        content = generator.generate_code_of_conduct()
        
        # Check key sections
        self.assertIn('# Code of Conduct', content)
        self.assertIn('## Our Pledge', content)
        self.assertIn('## Our Standards', content)
        self.assertIn('## Enforcement Responsibilities', content)
        self.assertIn('## Scope', content)
        self.assertIn('## Enforcement', content)
        self.assertIn('## Enforcement Guidelines', content)
        self.assertIn('Contributor Covenant', content)
    
    def test_detect_package_manager_python(self):
        """Test package manager detection for Python."""
        generator = OpenSourceDocsGenerator(self.python_repo_info)
        pm = generator._detect_package_manager()
        self.assertEqual(pm, 'pip')
    
    def test_detect_package_manager_javascript(self):
        """Test package manager detection for JavaScript."""
        generator = OpenSourceDocsGenerator(self.js_repo_info)
        pm = generator._detect_package_manager()
        self.assertEqual(pm, 'npm')
    
    def test_detect_package_manager_java(self):
        """Test package manager detection for Java with Maven."""
        repo_info = {
            'name': 'JavaProject',
            'languages': ['Java'],
            'files': ['pom.xml', 'src/Main.java']
        }
        generator = OpenSourceDocsGenerator(repo_info)
        pm = generator._detect_package_manager()
        self.assertEqual(pm, 'maven')
    
    def test_detect_package_manager_go(self):
        """Test package manager detection for Go."""
        repo_info = {
            'name': 'GoProject',
            'languages': ['Go'],
            'files': ['go.mod', 'main.go']
        }
        generator = OpenSourceDocsGenerator(repo_info)
        pm = generator._detect_package_manager()
        self.assertEqual(pm, 'go')
    
    def test_generate_all_templates(self):
        """Test generating all templates at once."""
        generator = OpenSourceDocsGenerator(self.python_repo_info)
        templates = generator.generate_all_templates(self.test_dir)
        
        # Check all templates are generated
        self.assertEqual(len(templates), 4)
        
        # Check file paths
        contributing_path = os.path.join(self.test_dir, 'CONTRIBUTING.md')
        self.assertIn(contributing_path, templates)
        
        conduct_path = os.path.join(self.test_dir, 'CODE_OF_CONDUCT.md')
        self.assertIn(conduct_path, templates)
        
        # Check content exists
        for path, content in templates.items():
            self.assertTrue(len(content) > 0)
    
    def test_write_all_templates(self):
        """Test writing all templates to files."""
        generator = OpenSourceDocsGenerator(self.python_repo_info)
        created_files = generator.write_all_templates(self.test_dir)
        
        # Check all files were created
        self.assertEqual(len(created_files), 4)
        
        # Verify files exist
        for file_path in created_files:
            self.assertTrue(os.path.exists(file_path))
            
            # Verify content is not empty
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertTrue(len(content) > 0)
        
        # Check specific files
        contributing_path = os.path.join(self.test_dir, 'CONTRIBUTING.md')
        self.assertTrue(os.path.exists(contributing_path))
        
        conduct_path = os.path.join(self.test_dir, 'CODE_OF_CONDUCT.md')
        self.assertTrue(os.path.exists(conduct_path))
        
        bug_template_path = os.path.join(self.test_dir, '.github', 'ISSUE_TEMPLATE', 'bug_report.md')
        self.assertTrue(os.path.exists(bug_template_path))
        
        feature_template_path = os.path.join(self.test_dir, '.github', 'ISSUE_TEMPLATE', 'feature_request.md')
        self.assertTrue(os.path.exists(feature_template_path))


if __name__ == '__main__':
    unittest.main()
