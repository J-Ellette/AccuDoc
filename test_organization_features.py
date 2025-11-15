"""
Tests for organization-wide features: glossary, onboarding, sharing, and license management.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json

from accudoc.glossary import GlossaryManager, GlossaryTerm
from accudoc.onboarding_generator import OnboardingGenerator, OnboardingStep
from accudoc.document_sharing import DocumentSharingManager
from accudoc.license_management import LicenseManagementToolkit


class TestGlossaryManager(unittest.TestCase):
    """Test glossary management."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_glossary.db'
        self.manager = GlossaryManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.manager.close()
        shutil.rmtree(self.temp_dir)
    
    def test_add_term(self):
        """Test adding a glossary term."""
        term = self.manager.add_term(
            term='API',
            definition='Application Programming Interface',
            preferred_usage='Use REST API for...',
            aliases=['api', 'interface'],
            deprecated_terms=['web service']
        )
        
        self.assertIsInstance(term, GlossaryTerm)
        self.assertEqual(term.term, 'API')
        self.assertEqual(len(term.aliases), 2)
    
    def test_get_terms(self):
        """Test retrieving glossary terms."""
        self.manager.add_term('API', 'Application Programming Interface', 'Use REST API')
        self.manager.add_term('SDK', 'Software Development Kit', 'Use the SDK')
        
        terms = self.manager.get_terms()
        self.assertEqual(len(terms), 2)
    
    def test_scan_content(self):
        """Test scanning content for violations."""
        self.manager.add_term(
            term='API',
            definition='Application Programming Interface',
            preferred_usage='Use REST API',
            deprecated_terms=['web service']
        )
        
        content = """
        This is a documentation about our web service.
        The web service provides access to data.
        """
        
        violations = self.manager.scan_content(content)
        self.assertGreater(len(violations), 0)
        self.assertTrue(any('web service' in v.term for v in violations))
    
    def test_generate_report(self):
        """Test generating violation report."""
        violations = []
        report = self.manager.generate_report(violations, '/test/repo')
        
        self.assertIn('Glossary & Style Compliance Report', report)
        self.assertIn('Total Violations', report)


class TestOnboardingGenerator(unittest.TestCase):
    """Test onboarding generation."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_onboarding.db'
        self.generator = OnboardingGenerator(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.generator.close()
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_repository(self):
        """Test analyzing repository for onboarding steps."""
        repo_info = {
            'name': 'test-repo',
            'url': 'https://github.com/test/repo',
            'languages': {'Python': 80, 'JavaScript': 20},
            'dependencies': {
                'requirements.txt': ['flask', 'pytest'],
                'package.json': ['express', 'jest']
            },
            'documentation': {
                'README.md': {},
                'CONTRIBUTING.md': {}
            }
        }
        
        steps = self.generator.analyze_repository(repo_info)
        
        self.assertGreater(len(steps), 0)
        self.assertTrue(any('Clone' in s.title for s in steps))
        self.assertTrue(any('Python' in s.title for s in steps))
    
    def test_create_checklist(self):
        """Test creating an onboarding checklist."""
        repo_info = {
            'name': 'test-repo',
            'languages': {'Python': 100}
        }
        
        checklist = self.generator.create_checklist(
            repository_path='/test/repo',
            repo_info=repo_info
        )
        
        self.assertIsNotNone(checklist.checklist_id)
        self.assertIsNotNone(checklist.steps)
        self.assertGreater(len(checklist.steps), 0)
    
    def test_generate_markdown_guide(self):
        """Test generating markdown guide."""
        repo_info = {
            'name': 'test-repo',
            'languages': {'Python': 100}
        }
        
        checklist = self.generator.create_checklist('/test/repo', repo_info)
        markdown = self.generator.generate_markdown_guide(checklist)
        
        self.assertIn('# ', markdown)
        self.assertIn('Onboarding Guide', markdown)
    
    def test_assign_and_update_progress(self):
        """Test assigning checklist and updating progress."""
        repo_info = {'name': 'test-repo', 'languages': {'Python': 100}}
        checklist = self.generator.create_checklist('/test/repo', repo_info)
        
        progress = self.generator.assign_checklist(checklist.checklist_id, 'user123')
        
        self.assertEqual(progress.user_id, 'user123')
        self.assertEqual(progress.progress_percentage, 0.0)
        
        # Complete a step
        if checklist.steps:
            updated = self.generator.update_progress(
                progress.progress_id,
                checklist.steps[0].step_id
            )
            self.assertGreater(updated.progress_percentage, 0.0)


class TestDocumentSharing(unittest.TestCase):
    """Test document sharing."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_sharing.db'
        self.manager = DocumentSharingManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.manager.close()
        shutil.rmtree(self.temp_dir)
    
    def test_share_document_section(self):
        """Test sharing a document section."""
        shared = self.manager.share_document_section(
            document_path='/docs/api.md',
            content='# API Documentation\n\nThis is the API docs.',
            shared_by='user123',
            section_title='API Reference',
            watermark=True
        )
        
        self.assertIsNotNone(shared.share_id)
        self.assertIsNotNone(shared.access_token)
        self.assertIn('shared by user123', shared.content)
    
    def test_get_shared_document(self):
        """Test accessing a shared document."""
        shared = self.manager.share_document_section(
            document_path='/docs/api.md',
            content='# API Documentation',
            shared_by='user123'
        )
        
        retrieved = self.manager.get_shared_document(shared.access_token)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.share_id, shared.share_id)
    
    def test_expired_share(self):
        """Test accessing an expired share."""
        shared = self.manager.share_document_section(
            document_path='/docs/api.md',
            content='# API Documentation',
            shared_by='user123',
            expires_in_days=-1  # Already expired
        )
        
        retrieved = self.manager.get_shared_document(shared.access_token)
        
        # Should return None for expired share
        self.assertIsNone(retrieved)
    
    def test_download_limit(self):
        """Test download limit enforcement."""
        shared = self.manager.share_document_section(
            document_path='/docs/api.md',
            content='# API Documentation',
            shared_by='user123',
            download_limit=2
        )
        
        # First download
        self.assertTrue(self.manager.record_download(shared.share_id))
        
        # Second download
        self.assertTrue(self.manager.record_download(shared.share_id))
        
        # Third download should fail
        self.assertFalse(self.manager.record_download(shared.share_id))
    
    def test_revoke_share(self):
        """Test revoking a share."""
        shared = self.manager.share_document_section(
            document_path='/docs/api.md',
            content='# API Documentation',
            shared_by='user123'
        )
        
        success = self.manager.revoke_share(shared.share_id, 'user123')
        self.assertTrue(success)
        
        # Should not be accessible after revocation
        retrieved = self.manager.get_shared_document(shared.access_token)
        self.assertIsNone(retrieved)


class TestLicenseManagement(unittest.TestCase):
    """Test license management."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_license.db'
        self.manager = LicenseManagementToolkit(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.manager.close()
        shutil.rmtree(self.temp_dir)
    
    def test_create_copyright_header(self):
        """Test creating a copyright header."""
        header = self.manager.create_copyright_header(
            organization='Test Corp',
            year='2024',
            license_type='MIT'
        )
        
        self.assertIsNotNone(header.header_id)
        self.assertIn('Test Corp', header.header_text)
        self.assertIn('2024', header.header_text)
        self.assertIn('MIT', header.header_text)
    
    def test_add_attribution(self):
        """Test adding an attribution."""
        attribution = self.manager.add_attribution(
            component_name='Flask',
            author='Pallets',
            license='BSD-3-Clause',
            source_url='https://flask.palletsprojects.com'
        )
        
        self.assertIsNotNone(attribution.attribution_id)
        self.assertEqual(attribution.component_name, 'Flask')
    
    def test_generate_attribution_file(self):
        """Test generating attribution file."""
        self.manager.add_attribution(
            component_name='Flask',
            author='Pallets',
            license='BSD-3-Clause'
        )
        
        self.manager.add_attribution(
            component_name='pytest',
            author='pytest-dev',
            license='MIT'
        )
        
        content = self.manager.generate_attribution_file()
        
        self.assertIn('Third-Party Attributions', content)
        self.assertIn('Flask', content)
        self.assertIn('pytest', content)
    
    def test_scan_for_headers(self):
        """Test scanning for copyright headers."""
        # Create test repository
        test_repo = Path(self.temp_dir) / 'test_repo'
        test_repo.mkdir()
        
        # Create file with header
        file_with_header = test_repo / 'with_header.py'
        file_with_header.write_text('''# Copyright (c) 2024 Test Corp
# Licensed under MIT

def hello():
    pass
''')
        
        # Create file without header
        file_without_header = test_repo / 'without_header.py'
        file_without_header.write_text('''def world():
    pass
''')
        
        results = self.manager.scan_for_headers(str(test_repo))
        
        self.assertEqual(results['total_files'], 2)
        self.assertEqual(results['files_with_headers'], 1)
        self.assertEqual(len(results['missing_headers']), 1)


if __name__ == '__main__':
    unittest.main()
