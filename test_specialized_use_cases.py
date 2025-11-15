"""
Test suite for Specialized Use Cases features:
- Academic Papers
- Tutorial Generation
- Compliance Reports
- Audit Documentation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from accudoc.academic_paper import AcademicPaperGenerator
from accudoc.tutorial_generator import TutorialGenerator
from accudoc.compliance_audit import ComplianceReportGenerator, AuditDocumentationGenerator


class TestAcademicPaperGenerator(unittest.TestCase):
    """Test academic paper generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.generator = AcademicPaperGenerator(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_generate_abstract(self):
        """Test abstract generation."""
        project_info = {
            'name': 'Test Project',
            'description': 'A test software system',
            'languages': ['Python', 'JavaScript']
        }
        
        abstract = self.generator.generate_abstract(project_info)
        
        self.assertIn('Test Project', abstract)
        self.assertIn('Python', abstract)
    
    def test_generate_introduction(self):
        """Test introduction generation."""
        project_info = {'name': 'Test System'}
        
        intro = self.generator.generate_introduction(project_info)
        
        self.assertIn('Test System', intro)
        self.assertIn('Section II', intro)
        self.assertIn('contributions', intro)
    
    def test_generate_architecture_section(self):
        """Test architecture section generation."""
        arch_info = {
            'components': [
                {'name': 'Component A', 'description': 'Handles A'},
                {'name': 'Component B', 'description': 'Handles B'}
            ],
            'patterns': ['MVC', 'Singleton']
        }
        
        section = self.generator.generate_architecture_section(arch_info)
        
        self.assertIn('Component A', section)
        self.assertIn('MVC', section)
    
    def test_generate_paper(self):
        """Test complete paper generation."""
        project_data = {
            'name': 'Research Project',
            'description': 'Novel system',
            'architecture': {'components': []},
            'implementation': {'languages': [{'name': 'Python', 'percentage': 100}]},
            'evaluation': {}
        }
        
        paper_config = {
            'authors': ['John Doe', 'Jane Smith'],
            'affiliation': 'University'
        }
        
        paper = self.generator.generate_paper(project_data, paper_config)
        
        self.assertIn('RESEARCH PROJECT', paper)
        self.assertIn('John Doe', paper)
        self.assertIn('University', paper)
        self.assertIn('Abstract', paper)
        self.assertIn('REFERENCES', paper)
    
    def test_generate_latex_paper(self):
        """Test LaTeX paper generation."""
        project_data = {'name': 'Test Project'}
        paper_config = {'authors': ['Author One']}
        
        latex = self.generator.generate_latex_paper(project_data, paper_config)
        
        self.assertIn('\\documentclass', latex)
        self.assertIn('\\title', latex)
        self.assertIn('\\begin{document}', latex)
        self.assertIn('\\end{document}', latex)


class TestTutorialGenerator(unittest.TestCase):
    """Test tutorial generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.generator = TutorialGenerator(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_extract_code_examples(self):
        """Test code example extraction."""
        test_file = Path(self.test_dir) / 'test.py'
        test_file.write_text('''
def hello_world():
    print("Hello, World!")
    return True

def calculate(x, y):
    return x + y
''')
        
        examples = self.generator.extract_code_examples(test_file, max_examples=5)
        
        self.assertGreater(len(examples), 0)
        self.assertEqual(examples[0]['type'], 'function')
    
    def test_categorize_by_complexity(self):
        """Test complexity categorization."""
        examples = [
            {'name': 'simple', 'code': 'def simple():\n    return 1'},
            {'name': 'complex', 'code': 'class Complex:\n    def __init__(self):\n        pass\n    async def process(self):\n        try:\n            pass\n        except:\n            pass'}
        ]
        
        categorized = self.generator.categorize_by_complexity(examples)
        
        self.assertIn('beginner', categorized)
        self.assertIn('intermediate', categorized)
        self.assertIn('advanced', categorized)
    
    def test_generate_tutorial_step(self):
        """Test tutorial step generation."""
        example = {
            'name': 'add_numbers',
            'code': 'def add_numbers(a, b):\n    return a + b',
            'type': 'function'
        }
        
        step = self.generator.generate_tutorial_step(example, 1)
        
        self.assertIn('Step 1', step)
        self.assertIn('add_numbers', step)
        self.assertIn('Code:', step)
        self.assertIn('Explanation:', step)
    
    def test_generate_tutorial(self):
        """Test complete tutorial generation."""
        examples = [
            {'name': 'func1', 'code': 'def func1(): pass', 'type': 'function'},
            {'name': 'func2', 'code': 'def func2(): pass', 'type': 'function'}
        ]
        
        tutorial = self.generator.generate_tutorial('Test Tutorial', examples, 'beginner')
        
        self.assertIn('Test Tutorial', tutorial)
        self.assertIn('Beginner', tutorial)
        self.assertIn('Prerequisites', tutorial)
        self.assertIn('Learning Objectives', tutorial)
    
    def test_generate_learning_path(self):
        """Test learning path generation."""
        all_examples = {
            'beginner': [{'name': 'basic1', 'code': 'def basic(): pass'}],
            'intermediate': [{'name': 'inter1', 'code': 'def inter(): pass'}],
            'advanced': [{'name': 'adv1', 'code': 'class Adv: pass'}]
        }
        
        path = self.generator.generate_learning_path('Test Project', all_examples)
        
        self.assertIn('Learning Path', path)
        self.assertIn('Level 1: Beginner', path)
        self.assertIn('Level 2: Intermediate', path)
        self.assertIn('Level 3: Advanced', path)
    
    def test_create_quick_start_guide(self):
        """Test quick start guide generation."""
        project_info = {
            'name': 'Test Project',
            'repo_url': 'https://github.com/test/project',
            'languages': ['Python']
        }
        
        guide = self.generator.create_quick_start_guide(project_info)
        
        self.assertIn('Quick Start Guide', guide)
        self.assertIn('Installation', guide)
        self.assertIn('Basic Usage', guide)


class TestComplianceReportGenerator(unittest.TestCase):
    """Test compliance report generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.generator = ComplianceReportGenerator(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_generate_soc2_report(self):
        """Test SOC 2 report generation."""
        project_data = {'name': 'Test System'}
        
        report = self.generator.generate_soc2_report(project_data)
        
        self.assertIn('SOC 2 Compliance Report', report)
        self.assertIn('Security', report)
        self.assertIn('Availability', report)
        self.assertIn('Trust Service Criteria', report)
    
    def test_generate_iso27001_documentation(self):
        """Test ISO 27001 documentation generation."""
        project_data = {
            'name': 'Test System',
            'organization': 'Test Org'
        }
        
        doc = self.generator.generate_iso27001_documentation(project_data)
        
        self.assertIn('ISO 27001', doc)
        self.assertIn('Risk Assessment', doc)
        self.assertIn('Risk Treatment', doc)
    
    def test_generate_gdpr_compliance_report(self):
        """Test GDPR compliance report generation."""
        project_data = {'name': 'Test System'}
        
        report = self.generator.generate_gdpr_compliance_report(project_data)
        
        self.assertIn('GDPR Compliance', report)
        self.assertIn('Article 5', report)
        self.assertIn('Data Subject Rights', report)
        self.assertIn('Data Protection by Design', report)


class TestAuditDocumentationGenerator(unittest.TestCase):
    """Test audit documentation generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.generator = AuditDocumentationGenerator(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_generate_change_log(self):
        """Test change log generation."""
        changes = [
            {
                'date': '2025-01-01',
                'id': 'CHG-001',
                'type': 'Feature',
                'description': 'New feature',
                'author': 'Dev',
                'status': 'Complete'
            }
        ]
        
        log = self.generator.generate_change_log(changes)
        
        self.assertIn('Change Log', log)
        self.assertIn('CHG-001', log)
        self.assertIn('New feature', log)
    
    def test_generate_security_audit_report(self):
        """Test security audit report generation."""
        audit_data = {
            'auditor': 'Security Team',
            'high_findings': [
                {'title': 'Critical Issue', 'risk': 'High', 'recommendation': 'Fix now'}
            ],
            'medium_findings': []
        }
        
        report = self.generator.generate_security_audit_report(audit_data)
        
        self.assertIn('Security Audit Report', report)
        self.assertIn('Executive Summary', report)
        self.assertIn('Critical Issue', report)
    
    def test_generate_access_control_report(self):
        """Test access control report generation."""
        access_data = {
            'users': [
                {'name': 'User1', 'role': 'Admin', 'last_access': '2025-01-01', 
                 'level': 'Full', 'status': 'Active'},
                {'name': 'User2', 'role': 'User', 'last_access': '2025-01-02',
                 'level': 'Standard', 'status': 'Active'}
            ]
        }
        
        report = self.generator.generate_access_control_report(access_data)
        
        self.assertIn('Access Control Audit Report', report)
        self.assertIn('User1', report)
        self.assertIn('Admin', report)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc Specialized Use Cases Test Suite")
    print("Testing: Academic Papers, Tutorials, Compliance, Audit")
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
