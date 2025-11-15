"""
Test suite for new AccuDoc features:
- Version History (tags support)
- Webhook Support
- PR Documentation
- Jenkins Integration
- Auto-Deploy
"""

import unittest
import tempfile
import shutil
import json
import subprocess
from pathlib import Path
from accudoc.branch_comparison import BranchComparator
from accudoc.webhooks import WebhookHandler, GitHubWebhook, GitLabWebhook
from accudoc.pr_docs import PRDocGenerator
from accudoc.jenkins_integration import JenkinsIntegration, generate_jenkinsfile
from accudoc.auto_deploy import DeploymentManager


class TestVersionHistory(unittest.TestCase):
    """Test version history and tag support."""
    
    def setUp(self):
        """Set up test repository with tags."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / 'test_repo'
        self.repo_path.mkdir()
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.repo_path, capture_output=True)
        
        # Create initial commit
        (self.repo_path / 'file1.txt').write_text('Initial content')
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.repo_path, capture_output=True)
        
        # Create v1.0.0 tag
        subprocess.run(['git', 'tag', '-a', 'v1.0.0', '-m', 'Version 1.0.0'], cwd=self.repo_path, capture_output=True)
        
        # Make another commit
        (self.repo_path / 'file2.txt').write_text('New feature')
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add new feature'], cwd=self.repo_path, capture_output=True)
        
        # Create v1.1.0 tag
        subprocess.run(['git', 'tag', '-a', 'v1.1.0', '-m', 'Version 1.1.0'], cwd=self.repo_path, capture_output=True)
    
    def tearDown(self):
        """Clean up test repository."""
        shutil.rmtree(self.test_dir)
    
    def test_get_available_tags(self):
        """Test getting list of tags."""
        comparator = BranchComparator(str(self.repo_path))
        tags = comparator.get_available_tags()
        
        self.assertIsInstance(tags, list)
        self.assertGreater(len(tags), 0)
        
        tag_names = [t['name'] for t in tags]
        self.assertIn('v1.0.0', tag_names)
        self.assertIn('v1.1.0', tag_names)
    
    def test_compare_tags(self):
        """Test comparing two tags."""
        comparator = BranchComparator(str(self.repo_path))
        comparison = comparator.compare_tags('v1.0.0', 'v1.1.0')
        
        self.assertEqual(comparison['base_branch'], 'v1.0.0')
        self.assertEqual(comparison['compare_branch'], 'v1.1.0')
        self.assertIn('files_added', comparison)
        self.assertIn('statistics', comparison)
    
    def test_generate_version_history(self):
        """Test generating version history documentation."""
        comparator = BranchComparator(str(self.repo_path))
        history = comparator.generate_version_history()
        
        self.assertIn('Version History', history)
        self.assertIn('v1.0.0', history)
        self.assertIn('v1.1.0', history)
        self.assertIsInstance(history, str)


class TestWebhookHandler(unittest.TestCase):
    """Test webhook handling functionality."""
    
    def setUp(self):
        """Set up webhook handler."""
        self.handler = WebhookHandler(secret='test-secret')
    
    def test_register_handler(self):
        """Test registering event handlers."""
        def test_handler(payload):
            return {'processed': True}
        
        self.handler.register_handler('push', test_handler)
        self.assertIn('push', self.handler.handlers)
    
    def test_verify_signature(self):
        """Test signature verification."""
        payload = b'test payload'
        
        import hmac
        import hashlib
        signature = hmac.new(
            'test-secret'.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        result = self.handler.verify_signature(payload, signature, 'sha256')
        self.assertTrue(result)
    
    def test_process_event(self):
        """Test processing webhook events."""
        def test_handler(payload):
            return {'data': payload}
        
        self.handler.register_handler('test_event', test_handler)
        
        result = self.handler.process_event('test_event', {'key': 'value'})
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['event_type'], 'test_event')
    
    def test_process_unknown_event(self):
        """Test processing unknown event type."""
        result = self.handler.process_event('unknown', {})
        
        self.assertEqual(result['status'], 'ignored')


class TestGitHubWebhook(unittest.TestCase):
    """Test GitHub webhook handling."""
    
    def setUp(self):
        """Set up GitHub webhook handler."""
        self.webhook = GitHubWebhook(secret='github-secret')
    
    def test_parse_push_event(self):
        """Test parsing GitHub push events."""
        headers = {'X-GitHub-Event': 'push'}
        payload = {
            'repository': {'full_name': 'user/repo'},
            'ref': 'refs/heads/main',
            'sender': {'login': 'testuser'},
            'commits': [{'message': 'Test commit'}],
            'head_commit': {'id': 'abc123'}
        }
        
        event_type, event_data = self.webhook.parse_github_event(headers, payload)
        
        self.assertEqual(event_type, 'push')
        self.assertEqual(event_data['repository'], 'user/repo')
        self.assertEqual(event_data['branch'], 'main')
    
    def test_parse_pull_request_event(self):
        """Test parsing GitHub pull request events."""
        headers = {'X-GitHub-Event': 'pull_request'}
        payload = {
            'repository': {'full_name': 'user/repo'},
            'action': 'opened',
            'pull_request': {
                'number': 42,
                'title': 'Test PR',
                'base': {'ref': 'main'},
                'head': {'ref': 'feature'}
            },
            'sender': {'login': 'testuser'}
        }
        
        event_type, event_data = self.webhook.parse_github_event(headers, payload)
        
        self.assertEqual(event_type, 'pull_request')
        self.assertEqual(event_data['action'], 'opened')
        self.assertEqual(event_data['number'], 42)


class TestGitLabWebhook(unittest.TestCase):
    """Test GitLab webhook handling."""
    
    def setUp(self):
        """Set up GitLab webhook handler."""
        self.webhook = GitLabWebhook(secret='gitlab-token')
    
    def test_verify_gitlab_token(self):
        """Test GitLab token verification."""
        result = self.webhook.verify_gitlab_token('gitlab-token')
        self.assertTrue(result)
        
        result = self.webhook.verify_gitlab_token('wrong-token')
        self.assertFalse(result)
    
    def test_parse_push_event(self):
        """Test parsing GitLab push events."""
        headers = {'X-Gitlab-Event': 'Push Hook'}
        payload = {
            'project': {'path_with_namespace': 'user/repo'},
            'ref': 'refs/heads/main',
            'user_name': 'testuser',
            'commits': [{'message': 'Test commit'}]
        }
        
        event_type, event_data = self.webhook.parse_gitlab_event(headers, payload)
        
        self.assertEqual(event_type, 'push')
        self.assertEqual(event_data['project'], 'user/repo')
        self.assertEqual(event_data['branch'], 'main')


class TestPRDocGenerator(unittest.TestCase):
    """Test PR documentation generation."""
    
    def setUp(self):
        """Set up test repository."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / 'test_repo'
        self.repo_path.mkdir()
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.repo_path, capture_output=True)
        
        # Create main branch with initial commit
        (self.repo_path / 'file1.py').write_text('# Initial code')
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.repo_path, capture_output=True)
        
        # Get default branch name
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              cwd=self.repo_path, capture_output=True, text=True)
        self.main_branch = result.stdout.strip()
        
        # Create feature branch
        subprocess.run(['git', 'checkout', '-b', 'feature'], cwd=self.repo_path, capture_output=True)
        (self.repo_path / 'file2.py').write_text('# New feature')
        (self.repo_path / 'test_feature.py').write_text('# Test code')
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add new feature'], cwd=self.repo_path, capture_output=True)
        
        subprocess.run(['git', 'checkout', self.main_branch], cwd=self.repo_path, capture_output=True)
    
    def tearDown(self):
        """Clean up test repository."""
        shutil.rmtree(self.test_dir)
    
    def test_analyze_pr_changes(self):
        """Test analyzing PR changes."""
        generator = PRDocGenerator(str(self.repo_path))
        analysis = generator.analyze_pr_changes(self.main_branch, 'feature')
        
        self.assertEqual(analysis['base_branch'], self.main_branch)
        self.assertEqual(analysis['head_branch'], 'feature')
        self.assertIn('files_changed', analysis)
        self.assertIn('statistics', analysis)
        self.assertIn('changes_by_type', analysis)
    
    def test_generate_pr_documentation(self):
        """Test generating PR documentation."""
        generator = PRDocGenerator(str(self.repo_path))
        analysis = generator.analyze_pr_changes(self.main_branch, 'feature')
        
        pr_metadata = {
            'title': 'Add new feature',
            'number': 42,
            'author': 'testuser'
        }
        
        docs = generator.generate_pr_documentation(analysis, pr_metadata)
        
        self.assertIn('Pull Request', docs)
        self.assertIn('Add new feature', docs)
        self.assertIn('Review Checklist', docs)
        self.assertIsInstance(docs, str)
    
    def test_generate_pr_review_template(self):
        """Test generating PR review template."""
        generator = PRDocGenerator(str(self.repo_path))
        template = generator.generate_pr_review_template()
        
        self.assertIn('Pull Request Review', template)
        self.assertIn('Checklist', template)
        self.assertIsInstance(template, str)


class TestJenkinsIntegration(unittest.TestCase):
    """Test Jenkins integration."""
    
    def test_generate_jenkinsfile(self):
        """Test Jenkinsfile generation."""
        jenkinsfile = generate_jenkinsfile(
            repo_url='https://github.com/user/repo',
            output_path='docs/README.md'
        )
        
        self.assertIn('pipeline', jenkinsfile)
        self.assertIn('stages', jenkinsfile)
        self.assertIn('Generate Documentation', jenkinsfile)
        self.assertIsInstance(jenkinsfile, str)
    
    def test_jenkins_integration_class(self):
        """Test JenkinsIntegration class."""
        integration = JenkinsIntegration()
        
        config = {
            'repo_url': 'https://github.com/user/repo',
            'output_path': 'docs/README.md',
            'multibranch': True,
            'pipeline_script': True
        }
        
        files = integration.generate_configuration(config)
        
        self.assertIn('Jenkinsfile', files)
        self.assertIn('Jenkinsfile.multibranch', files)
        self.assertIn('pipeline-script.groovy', files)


class TestAutoDeployment(unittest.TestCase):
    """Test auto-deployment functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / 'test_repo'
        self.repo_path.mkdir()
        
        # Create docs directory
        self.docs_dir = self.repo_path / 'docs'
        self.docs_dir.mkdir()
        (self.docs_dir / 'index.html').write_text('<html><body>Test</body></html>')
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_generate_netlify_toml(self):
        """Test Netlify configuration generation."""
        manager = DeploymentManager(str(self.repo_path))
        result = manager.generate_netlify_toml('docs')
        
        self.assertTrue(result)
        netlify_file = self.repo_path / 'netlify.toml'
        self.assertTrue(netlify_file.exists())
        
        content = netlify_file.read_text()
        self.assertIn('[build]', content)
        self.assertIn('publish = "docs"', content)
    
    def test_generate_github_actions_deploy(self):
        """Test GitHub Actions workflow generation."""
        manager = DeploymentManager(str(self.repo_path))
        result = manager.generate_github_actions_deploy('docs')
        
        self.assertTrue(result)
        workflow_file = self.repo_path / '.github' / 'workflows' / 'deploy-docs.yml'
        self.assertTrue(workflow_file.exists())
        
        content = workflow_file.read_text()
        self.assertIn('Deploy Documentation', content)
        self.assertIn('Generate Documentation', content)
    
    def test_deploy_to_gitlab_pages(self):
        """Test GitLab Pages configuration."""
        manager = DeploymentManager(str(self.repo_path))
        result = manager.deploy_to_gitlab_pages('public')
        
        self.assertTrue(result)
        ci_file = self.repo_path / '.gitlab-ci.yml'
        self.assertTrue(ci_file.exists())
        
        content = ci_file.read_text()
        self.assertIn('pages:', content)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc New Features Test Suite")
    print("Testing: Version History, Webhooks, PR Docs, Jenkins, Auto-Deploy")
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
