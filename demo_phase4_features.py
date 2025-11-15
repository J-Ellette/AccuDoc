#!/usr/bin/env python3
"""
Demo script for new AccuDoc features:
- Version History
- Webhook Support
- PR Documentation
- Jenkins Integration
- Auto-Deploy

This script demonstrates how to use the new features added to AccuDoc.
"""

import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.branch_comparison import BranchComparator
from accudoc.webhooks import WebhookHandler, GitHubWebhook, GitLabWebhook, create_webhook_server_example
from accudoc.pr_docs import PRDocGenerator
from accudoc.jenkins_integration import JenkinsIntegration, generate_jenkinsfile
from accudoc.auto_deploy import DeploymentManager, generate_deployment_guide


def demo_version_history():
    """Demonstrate version history feature."""
    print("=" * 60)
    print("DEMO: Version History with Git Tags")
    print("=" * 60)
    print()
    
    # Create a temporary git repository with tags
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / 'demo_repo'
    repo_path.mkdir()
    
    try:
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'demo@example.com'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Demo User'], cwd=repo_path, capture_output=True)
        
        # Create initial commit and tag
        (repo_path / 'README.md').write_text('# Demo Project\n\nInitial version')
        subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial release'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'tag', '-a', 'v1.0.0', '-m', 'Version 1.0.0 - Initial release'], cwd=repo_path, capture_output=True)
        
        # Create v1.1.0
        (repo_path / 'feature.py').write_text('# New feature')
        subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add new feature'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'tag', '-a', 'v1.1.0', '-m', 'Version 1.1.0 - Added new features'], cwd=repo_path, capture_output=True)
        
        # Create v2.0.0
        (repo_path / 'api.py').write_text('# New API')
        subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Major API update'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'tag', '-a', 'v2.0.0', '-m', 'Version 2.0.0 - Major release'], cwd=repo_path, capture_output=True)
        
        # Use BranchComparator to get tags
        comparator = BranchComparator(str(repo_path))
        
        print("1. Getting available tags:")
        tags = comparator.get_available_tags()
        for tag in tags:
            print(f"   - {tag['name']}: {tag.get('message', 'No message')}")
        print()
        
        print("2. Comparing tags (v1.0.0 vs v2.0.0):")
        comparison = comparator.compare_tags('v1.0.0', 'v2.0.0')
        print(f"   Files changed: {comparison['statistics']['files_changed']}")
        print(f"   Commits: {comparison['statistics']['commits_ahead']}")
        print()
        
        print("3. Generating version history:")
        history = comparator.generate_version_history()
        print(history[:500] + "...")
        print()
        
    finally:
        shutil.rmtree(temp_dir)
    
    print("✅ Version history demo completed!\n")


def demo_webhooks():
    """Demonstrate webhook support."""
    print("=" * 60)
    print("DEMO: Webhook Support")
    print("=" * 60)
    print()
    
    # GitHub Webhook
    print("1. GitHub Webhook Handler:")
    github_webhook = GitHubWebhook(secret='my-secret')
    
    # Register a handler
    def handle_push(payload):
        print(f"   Processing push to {payload.get('repository', 'unknown')}")
        return {'status': 'documentation updated'}
    
    github_webhook.register_handler('push', handle_push)
    
    # Simulate a push event
    headers = {'X-GitHub-Event': 'push'}
    payload = {
        'repository': {'full_name': 'user/repo'},
        'ref': 'refs/heads/main',
        'sender': {'login': 'developer'},
        'commits': [{'message': 'Update code'}]
    }
    
    event_type, event_data = github_webhook.parse_github_event(headers, payload)
    print(f"   Event type: {event_type}")
    print(f"   Repository: {event_data['repository']}")
    print(f"   Branch: {event_data['branch']}")
    print()
    
    # GitLab Webhook
    print("2. GitLab Webhook Handler:")
    gitlab_webhook = GitLabWebhook(secret='gitlab-token')
    
    headers = {'X-Gitlab-Event': 'Push Hook'}
    payload = {
        'project': {'path_with_namespace': 'group/project'},
        'ref': 'refs/heads/develop',
        'user_name': 'developer'
    }
    
    event_type, event_data = gitlab_webhook.parse_gitlab_event(headers, payload)
    print(f"   Event type: {event_type}")
    print(f"   Project: {event_data['project']}")
    print(f"   Branch: {event_data['branch']}")
    print()
    
    print("3. Webhook server example code:")
    server_code = create_webhook_server_example()
    print(f"   Generated {len(server_code)} characters of Flask server code")
    print("   (See accudoc/webhooks.py for full example)")
    print()
    
    print("✅ Webhook demo completed!\n")


def demo_pr_documentation():
    """Demonstrate PR documentation generation."""
    print("=" * 60)
    print("DEMO: Pull Request Documentation")
    print("=" * 60)
    print()
    
    # Create a temporary git repository with branches
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / 'demo_repo'
    repo_path.mkdir()
    
    try:
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'demo@example.com'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Demo User'], cwd=repo_path, capture_output=True)
        
        # Create main branch
        (repo_path / 'main.py').write_text('# Main code')
        subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path, capture_output=True)
        
        # Get default branch name
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              cwd=repo_path, capture_output=True, text=True)
        main_branch = result.stdout.strip()
        
        # Create feature branch
        subprocess.run(['git', 'checkout', '-b', 'feature/new-api'], cwd=repo_path, capture_output=True)
        (repo_path / 'api.py').write_text('# New API endpoint')
        (repo_path / 'test_api.py').write_text('# API tests')
        (repo_path / 'README.md').write_text('# Updated documentation')
        subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add new API endpoint'], cwd=repo_path, capture_output=True)
        
        subprocess.run(['git', 'checkout', main_branch], cwd=repo_path, capture_output=True)
        
        # Generate PR documentation
        generator = PRDocGenerator(str(repo_path))
        
        print("1. Analyzing PR changes:")
        analysis = generator.analyze_pr_changes(main_branch, 'feature/new-api')
        print(f"   Files changed: {analysis['statistics']['total_files']}")
        print(f"   Code files: {len(analysis['changes_by_type']['code'])}")
        print(f"   Test files: {len(analysis['changes_by_type']['tests'])}")
        print(f"   Documentation: {len(analysis['changes_by_type']['documentation'])}")
        print()
        
        print("2. Generating PR documentation:")
        pr_metadata = {
            'title': 'Add new API endpoint',
            'number': 42,
            'author': 'developer'
        }
        docs = generator.generate_pr_documentation(analysis, pr_metadata)
        print(docs[:500] + "...")
        print()
        
        print("3. Review template:")
        template = generator.generate_pr_review_template()
        print(template[:300] + "...")
        print()
        
    finally:
        shutil.rmtree(temp_dir)
    
    print("✅ PR documentation demo completed!\n")


def demo_jenkins_integration():
    """Demonstrate Jenkins integration."""
    print("=" * 60)
    print("DEMO: Jenkins Integration")
    print("=" * 60)
    print()
    
    print("1. Generating Jenkinsfile:")
    jenkinsfile = generate_jenkinsfile(
        repo_url='https://github.com/user/project',
        output_path='docs/README.md',
        accudoc_version='main'
    )
    print(f"   Generated Jenkinsfile ({len(jenkinsfile)} characters)")
    print("   First 300 characters:")
    print(jenkinsfile[:300])
    print()
    
    print("2. Jenkins Integration with all configurations:")
    integration = JenkinsIntegration()
    config = {
        'repo_url': 'https://github.com/user/project',
        'output_path': 'docs/README.md',
        'multibranch': True,
        'shared_library': True,
        'pipeline_script': True
    }
    
    files = integration.generate_configuration(config)
    print("   Generated files:")
    for filename in files.keys():
        print(f"     - {filename}")
    print()
    
    print("3. Saving configurations to temporary directory:")
    temp_dir = tempfile.mkdtemp()
    try:
        integration.save_configurations(temp_dir, config)
        saved_files = list(Path(temp_dir).rglob('*'))
        print(f"   Saved {len([f for f in saved_files if f.is_file()])} files")
    finally:
        shutil.rmtree(temp_dir)
    print()
    
    print("✅ Jenkins integration demo completed!\n")


def demo_auto_deploy():
    """Demonstrate auto-deployment features."""
    print("=" * 60)
    print("DEMO: Auto-Deployment")
    print("=" * 60)
    print()
    
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / 'demo_repo'
    repo_path.mkdir()
    docs_dir = repo_path / 'docs'
    docs_dir.mkdir()
    (docs_dir / 'index.html').write_text('<html><body>Documentation</body></html>')
    
    try:
        manager = DeploymentManager(str(repo_path))
        
        print("1. Generating Netlify configuration:")
        result = manager.generate_netlify_toml('docs')
        print(f"   Created: {result}")
        if (repo_path / 'netlify.toml').exists():
            content = (repo_path / 'netlify.toml').read_text()
            print(f"   Content preview: {content[:200]}...")
        print()
        
        print("2. Generating GitHub Actions workflow:")
        result = manager.generate_github_actions_deploy('docs')
        print(f"   Created: {result}")
        workflow_file = repo_path / '.github' / 'workflows' / 'deploy-docs.yml'
        if workflow_file.exists():
            print(f"   Workflow file: {workflow_file}")
        print()
        
        print("3. Generating GitLab Pages configuration:")
        result = manager.deploy_to_gitlab_pages('public')
        print(f"   Created: {result}")
        if (repo_path / '.gitlab-ci.yml').exists():
            print("   GitLab CI configuration added")
        print()
        
        print("4. Deployment guide:")
        guide = generate_deployment_guide()
        print(f"   Generated {len(guide)} characters of deployment documentation")
        print("   First 300 characters:")
        print(guide[:300] + "...")
        print()
        
    finally:
        shutil.rmtree(temp_dir)
    
    print("✅ Auto-deployment demo completed!\n")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("AccuDoc New Features Demonstration")
    print("=" * 60)
    print()
    
    try:
        demo_version_history()
        demo_webhooks()
        demo_pr_documentation()
        demo_jenkins_integration()
        demo_auto_deploy()
        
        print("=" * 60)
        print("All Demonstrations Completed Successfully! ✅")
        print("=" * 60)
        print()
        print("Summary of new features:")
        print("  1. ✅ Version History - Track and document versions via git tags")
        print("  2. ✅ Webhook Support - Auto-update docs on GitHub/GitLab events")
        print("  3. ✅ PR Documentation - Generate documentation for pull requests")
        print("  4. ✅ Jenkins Integration - CI/CD pipelines for documentation")
        print("  5. ✅ Auto-Deploy - Deploy to GitHub Pages, GitLab Pages, Netlify")
        print()
        print("For more details, see:")
        print("  - accudoc/branch_comparison.py (version history)")
        print("  - accudoc/webhooks.py (webhook handlers)")
        print("  - accudoc/pr_docs.py (PR documentation)")
        print("  - accudoc/jenkins_integration.py (Jenkins integration)")
        print("  - accudoc/auto_deploy.py (auto-deployment)")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
