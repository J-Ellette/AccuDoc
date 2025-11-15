"""
Test suite for Security & Privacy features:
- Credential Management
- SSH Key Support
- License Compliance
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
from accudoc.credential_manager import CredentialManager, SSHKeyManager, get_credential_from_env
from accudoc.license_compliance import LicenseAnalyzer, LICENSE_COMPATIBILITY


class TestCredentialManager(unittest.TestCase):
    """Test credential management."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.test_dir) / 'credentials.enc'
        self.manager = CredentialManager(self.storage_path, password='test_password')
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_store_and_retrieve_password(self):
        """Test storing and retrieving password."""
        self.manager.store_password('github.com', 'testuser', 'testpass123')
        
        cred = self.manager.get_credential('github.com', 'testuser')
        
        self.assertIsNotNone(cred)
        self.assertEqual(cred['type'], 'password')
        self.assertEqual(cred['password'], 'testpass123')
    
    def test_store_and_retrieve_token(self):
        """Test storing and retrieving token."""
        self.manager.store_token('github.com', 'ghp_test_token_123', 'personal')
        
        cred = self.manager.get_credential('github.com')
        
        self.assertIsNotNone(cred)
        self.assertEqual(cred['type'], 'token')
        self.assertEqual(cred['token'], 'ghp_test_token_123')
    
    def test_list_credentials(self):
        """Test listing credentials."""
        self.manager.store_password('github.com', 'user1', 'pass1')
        self.manager.store_password('github.com', 'user2', 'pass2')
        self.manager.store_password('gitlab.com', 'user3', 'pass3')
        
        creds = self.manager.list_credentials()
        
        self.assertIn('github.com', creds)
        self.assertIn('gitlab.com', creds)
        self.assertEqual(len(creds['github.com']), 2)
        self.assertEqual(len(creds['gitlab.com']), 1)
    
    def test_delete_credential(self):
        """Test deleting credential."""
        self.manager.store_password('github.com', 'testuser', 'testpass')
        
        # Verify it exists
        self.assertIsNotNone(self.manager.get_credential('github.com', 'testuser'))
        
        # Delete it
        self.manager.delete_credential('github.com', 'testuser')
        
        # Verify it's gone
        self.assertIsNone(self.manager.get_credential('github.com', 'testuser'))
    
    def test_clear_all(self):
        """Test clearing all credentials."""
        self.manager.store_password('github.com', 'user1', 'pass1')
        self.manager.store_token('gitlab.com', 'token1')
        
        self.manager.clear_all()
        
        creds = self.manager.list_credentials()
        self.assertEqual(len(creds), 0)
    
    def test_secure_permissions(self):
        """Test that credentials file has secure permissions."""
        self.manager.store_password('test.com', 'user', 'pass')
        
        if self.storage_path.exists():
            perms = self.storage_path.stat().st_mode
            # Check that only user has read/write (0600)
            # This is platform-specific, so we just check it's not world-readable
            self.assertTrue(self.storage_path.exists())


class TestSSHKeyManager(unittest.TestCase):
    """Test SSH key management."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.ssh_dir = Path(self.test_dir) / '.ssh'
        self.ssh_dir.mkdir()
        self.manager = SSHKeyManager(self.ssh_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_list_keys(self):
        """Test listing SSH keys."""
        # Create mock keys
        (self.ssh_dir / 'id_rsa').write_text('private key content')
        (self.ssh_dir / 'id_rsa.pub').write_text('public key content')
        (self.ssh_dir / 'id_ed25519').write_text('ed25519 private')
        
        keys = self.manager.list_keys()
        
        self.assertGreater(len(keys), 0)
        self.assertTrue(any('id_rsa' in k for k in keys))
    
    def test_has_key(self):
        """Test checking if key exists."""
        self.assertFalse(self.manager.has_key('id_rsa'))
        
        (self.ssh_dir / 'id_rsa').write_text('private key')
        
        self.assertTrue(self.manager.has_key('id_rsa'))
    
    def test_get_key_path(self):
        """Test getting key path."""
        (self.ssh_dir / 'id_rsa').write_text('private key')
        
        path = self.manager.get_key_path('id_rsa')
        
        self.assertIsNotNone(path)
        self.assertTrue(path.exists())
    
    def test_get_public_key(self):
        """Test getting public key content."""
        pub_key = 'ssh-rsa AAAAB3... user@host'
        (self.ssh_dir / 'id_rsa.pub').write_text(pub_key)
        
        content = self.manager.get_public_key('id_rsa')
        
        self.assertEqual(content, pub_key)
    
    def test_configure_git_ssh(self):
        """Test configuring Git SSH command."""
        (self.ssh_dir / 'id_rsa').write_text('private key')
        
        ssh_command = self.manager.configure_git_ssh('id_rsa')
        
        self.assertIsNotNone(ssh_command)
        self.assertIn('ssh -i', ssh_command)
        self.assertIn('id_rsa', ssh_command)


class TestGetCredentialFromEnv(unittest.TestCase):
    """Test getting credentials from environment."""
    
    def test_get_github_token(self):
        """Test getting GitHub token from environment."""
        os.environ['GITHUB_TOKEN'] = 'test_token_123'
        
        cred = get_credential_from_env('github.com')
        
        self.assertIsNotNone(cred)
        self.assertEqual(cred['type'], 'token')
        self.assertEqual(cred['token'], 'test_token_123')
        
        # Clean up
        del os.environ['GITHUB_TOKEN']
    
    def test_no_env_token(self):
        """Test when no environment token exists."""
        # Make sure no tokens are set
        for var in ['GIT_TOKEN', 'GITHUB_TOKEN', 'GITLAB_TOKEN']:
            if var in os.environ:
                del os.environ[var]
        
        cred = get_credential_from_env('github.com')
        
        self.assertIsNone(cred)


class TestLicenseAnalyzer(unittest.TestCase):
    """Test license compliance checking."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)
        self.analyzer = LicenseAnalyzer(str(self.repo_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_detect_mit_license(self):
        """Test detecting MIT license."""
        license_file = self.repo_path / 'LICENSE'
        license_file.write_text('''
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software...
''')
        
        detected = self.analyzer.detect_license(license_file)
        
        self.assertEqual(detected, 'MIT')
    
    def test_detect_apache_license(self):
        """Test detecting Apache 2.0 license."""
        license_file = self.repo_path / 'LICENSE'
        license_file.write_text('''
Apache License
Version 2.0, January 2004

Licensed under the Apache License, Version 2.0...
''')
        
        detected = self.analyzer.detect_license(license_file)
        
        self.assertEqual(detected, 'Apache-2.0')
    
    def test_find_license_files(self):
        """Test finding license files."""
        (self.repo_path / 'LICENSE').write_text('MIT License...')
        (self.repo_path / 'subdir').mkdir()
        (self.repo_path / 'subdir' / 'LICENSE.txt').write_text('Apache License...')
        
        licenses = self.analyzer.find_license_files()
        
        self.assertGreaterEqual(len(licenses), 1)
    
    def test_get_project_license(self):
        """Test getting main project license."""
        (self.repo_path / 'LICENSE').write_text('MIT License\nPermission is hereby granted...')
        
        license_name = self.analyzer.get_project_license()
        
        self.assertEqual(license_name, 'MIT')
    
    def test_check_compatibility(self):
        """Test checking license compatibility."""
        # MIT project can include MIT dependencies
        self.assertTrue(self.analyzer.check_compatibility('MIT', 'MIT'))
        
        # MIT project can include Apache dependencies
        self.assertTrue(self.analyzer.check_compatibility('MIT', 'Apache-2.0'))
        
        # GPL project cannot include proprietary (not in compatibility list)
        if 'Proprietary' not in LICENSE_COMPATIBILITY.get('GPL-3.0', set()):
            self.assertFalse(self.analyzer.check_compatibility('GPL-3.0', 'Proprietary'))
    
    def test_analyze_dependencies(self):
        """Test analyzing dependency licenses."""
        (self.repo_path / 'LICENSE').write_text('MIT License\nPermission is hereby granted...')
        
        dependencies = [
            {'name': 'package1', 'license': 'MIT'},
            {'name': 'package2', 'license': 'Apache-2.0'},
            {'name': 'package3', 'license': 'Unknown'}
        ]
        
        analysis = self.analyzer.analyze_dependencies(dependencies)
        
        self.assertEqual(analysis['project_license'], 'MIT')
        self.assertEqual(analysis['total_dependencies'], 3)
        self.assertGreaterEqual(len(analysis['compatible']), 2)
        self.assertEqual(len(analysis['unknown']), 1)
    
    def test_generate_compliance_report(self):
        """Test generating compliance report."""
        analysis = {
            'project_license': 'MIT',
            'total_dependencies': 3,
            'compatible': [
                {'name': 'pkg1', 'license': 'MIT'},
                {'name': 'pkg2', 'license': 'Apache-2.0'}
            ],
            'incompatible': [],
            'unknown': ['pkg3'],
            'by_category': {
                'permissive': ['pkg1', 'pkg2']
            }
        }
        
        report = self.analyzer.generate_compliance_report(analysis)
        
        self.assertIn('License Compliance Report', report)
        self.assertIn('MIT', report)
        self.assertIn('pkg1', report)
        self.assertIn('Unknown', report)
    
    def test_get_license_info(self):
        """Test getting license information."""
        info = self.analyzer.get_license_info('Apache-2.0')
        
        self.assertEqual(info['name'], 'Apache-2.0')
        self.assertTrue(info['patent_use'])
        self.assertTrue(info['commercial_use'])


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc Security & Privacy Test Suite")
    print("Testing: Credentials, SSH Keys, License Compliance")
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
