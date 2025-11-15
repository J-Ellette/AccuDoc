"""
Auto-deployment module for AccuDoc.

Provides automated deployment functionality for documentation
to various hosting platforms including:
- GitHub Pages
- GitLab Pages
- Netlify
"""

import logging
import subprocess
import json
from typing import Dict, Optional, List
from pathlib import Path


class DeploymentManager:
    """Manages automated documentation deployment."""
    
    def __init__(self, repo_path: str):
        """
        Initialize deployment manager.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.deployment')
    
    def _run_command(self, args: List[str], cwd: Optional[Path] = None) -> tuple:
        """
        Run a command and return output.
        
        Args:
            args: Command arguments
            cwd: Working directory (defaults to repo_path)
            
        Returns:
            Tuple of (success, output, error)
        """
        if cwd is None:
            cwd = self.repo_path
        
        try:
            result = subprocess.run(
                args,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def deploy_to_github_pages(self, docs_dir: str = 'docs', 
                               branch: str = 'gh-pages',
                               commit_message: str = 'Update documentation') -> bool:
        """
        Deploy documentation to GitHub Pages.
        
        Args:
            docs_dir: Directory containing documentation
            branch: Target branch (default: gh-pages)
            commit_message: Commit message
            
        Returns:
            True if deployment successful
        """
        self.logger.info(f"Deploying to GitHub Pages (branch: {branch})")
        
        docs_path = self.repo_path / docs_dir
        if not docs_path.exists():
            self.logger.error(f"Documentation directory not found: {docs_dir}")
            return False
        
        # Check if gh-pages branch exists
        success, output, error = self._run_command(['git', 'rev-parse', '--verify', branch])
        
        if not success:
            # Create gh-pages branch
            self.logger.info(f"Creating {branch} branch")
            success, _, error = self._run_command(['git', 'checkout', '--orphan', branch])
            if not success:
                self.logger.error(f"Failed to create branch: {error}")
                return False
            
            # Remove all files
            self._run_command(['git', 'rm', '-rf', '.'])
        else:
            # Checkout existing gh-pages branch
            success, _, error = self._run_command(['git', 'checkout', branch])
            if not success:
                self.logger.error(f"Failed to checkout branch: {error}")
                return False
        
        # Copy documentation files
        import shutil
        try:
            # Clear existing files (except .git)
            for item in self.repo_path.iterdir():
                if item.name != '.git' and item.name != docs_dir:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            
            # Copy new documentation
            for item in docs_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, self.repo_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, self.repo_path / item.name)
        except Exception as e:
            self.logger.error(f"Failed to copy files: {e}")
            return False
        
        # Commit and push
        self._run_command(['git', 'add', '.'])
        success, _, error = self._run_command(['git', 'commit', '-m', commit_message])
        if not success and 'nothing to commit' not in error:
            self.logger.error(f"Failed to commit: {error}")
            return False
        
        success, _, error = self._run_command(['git', 'push', 'origin', branch])
        if not success:
            self.logger.error(f"Failed to push: {error}")
            return False
        
        self.logger.info("Successfully deployed to GitHub Pages")
        return True
    
    def deploy_to_gitlab_pages(self, docs_dir: str = 'public') -> bool:
        """
        Generate GitLab Pages configuration.
        
        GitLab Pages works through CI/CD, so this generates the .gitlab-ci.yml
        
        Args:
            docs_dir: Directory for documentation (must be 'public' for GitLab Pages)
            
        Returns:
            True if configuration created successfully
        """
        self.logger.info("Setting up GitLab Pages deployment")
        
        gitlab_ci_content = f'''# GitLab Pages configuration for AccuDoc
pages:
  stage: deploy
  image: python:3.9
  script:
    - echo "Deploying to GitLab Pages"
    - mkdir -p public
    - cp -r {docs_dir}/* public/ || cp -r docs/* public/
  artifacts:
    paths:
      - public
  only:
    - main
    - master
'''
        
        ci_file = self.repo_path / '.gitlab-ci.yml'
        
        try:
            # Check if file exists
            if ci_file.exists():
                # Append to existing file
                with open(ci_file, 'r') as f:
                    content = f.read()
                
                if 'pages:' not in content:
                    with open(ci_file, 'a') as f:
                        f.write('\n' + gitlab_ci_content)
                    self.logger.info("Added pages job to existing .gitlab-ci.yml")
                else:
                    self.logger.info("GitLab Pages configuration already exists")
            else:
                # Create new file
                with open(ci_file, 'w') as f:
                    f.write(gitlab_ci_content)
                self.logger.info("Created .gitlab-ci.yml with pages configuration")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup GitLab Pages: {e}")
            return False
    
    def deploy_to_netlify(self, docs_dir: str = 'docs',
                         site_name: Optional[str] = None,
                         netlify_token: Optional[str] = None) -> bool:
        """
        Deploy documentation to Netlify.
        
        Requires netlify-cli to be installed: npm install -g netlify-cli
        
        Args:
            docs_dir: Directory containing documentation
            site_name: Netlify site name (optional)
            netlify_token: Netlify auth token (optional, can use NETLIFY_AUTH_TOKEN env var)
            
        Returns:
            True if deployment successful
        """
        self.logger.info(f"Deploying to Netlify from {docs_dir}")
        
        docs_path = self.repo_path / docs_dir
        if not docs_path.exists():
            self.logger.error(f"Documentation directory not found: {docs_dir}")
            return False
        
        # Check if netlify-cli is installed
        success, _, _ = self._run_command(['netlify', '--version'])
        if not success:
            self.logger.error("netlify-cli not found. Install with: npm install -g netlify-cli")
            return False
        
        # Build command
        cmd = ['netlify', 'deploy', '--prod', '--dir', docs_dir]
        
        if site_name:
            cmd.extend(['--site', site_name])
        
        if netlify_token:
            cmd.extend(['--auth', netlify_token])
        
        success, output, error = self._run_command(cmd)
        
        if success:
            self.logger.info("Successfully deployed to Netlify")
            self.logger.info(output)
            return True
        else:
            self.logger.error(f"Netlify deployment failed: {error}")
            return False
    
    def generate_netlify_toml(self, docs_dir: str = 'docs',
                              build_command: Optional[str] = None) -> bool:
        """
        Generate netlify.toml configuration file.
        
        Args:
            docs_dir: Directory containing documentation
            build_command: Optional build command
            
        Returns:
            True if file created successfully
        """
        build_cmd = build_command or 'python accudoc_cli.py export . -o docs/index.html --format html'
        
        netlify_config = f'''# Netlify configuration for AccuDoc
[build]
  command = "{build_cmd}"
  publish = "{docs_dir}"

[build.environment]
  PYTHON_VERSION = "3.9"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
'''
        
        netlify_file = self.repo_path / 'netlify.toml'
        
        try:
            with open(netlify_file, 'w') as f:
                f.write(netlify_config)
            self.logger.info("Created netlify.toml configuration")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create netlify.toml: {e}")
            return False
    
    def generate_github_actions_deploy(self, docs_dir: str = 'docs') -> bool:
        """
        Generate GitHub Actions workflow for automatic deployment.
        
        Args:
            docs_dir: Directory containing documentation
            
        Returns:
            True if workflow created successfully
        """
        workflow_content = f'''name: Deploy Documentation

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install AccuDoc
        run: |
          git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
      
      - name: Generate Documentation
        run: |
          python /tmp/accudoc/accudoc_cli.py export . \\
            -o {docs_dir}/index.html \\
            --format html \\
            --template default
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{{{ secrets.GITHUB_TOKEN }}}}
          publish_dir: ./{docs_dir}
          publish_branch: gh-pages
          user_name: 'github-actions[bot]'
          user_email: 'github-actions[bot]@users.noreply.github.com'
'''
        
        workflow_dir = self.repo_path / '.github' / 'workflows'
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflow_dir / 'deploy-docs.yml'
        
        try:
            with open(workflow_file, 'w') as f:
                f.write(workflow_content)
            self.logger.info(f"Created GitHub Actions workflow: {workflow_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {e}")
            return False


def generate_deployment_guide() -> str:
    """
    Generate comprehensive deployment guide.
    
    Returns:
        Markdown formatted deployment guide
    """
    return '''# AccuDoc Deployment Guide

## Overview

AccuDoc supports automated deployment to multiple hosting platforms:

1. **GitHub Pages** - Free hosting for GitHub repositories
2. **GitLab Pages** - Free hosting for GitLab repositories  
3. **Netlify** - Modern web hosting with continuous deployment

## GitHub Pages Deployment

### Option 1: Manual Deployment

```bash
# Generate documentation
python accudoc_cli.py export . -o docs/index.html --format html

# Deploy to gh-pages branch
git checkout gh-pages
cp -r docs/* .
git add .
git commit -m "Update documentation"
git push origin gh-pages
```

### Option 2: GitHub Actions (Recommended)

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate and Deploy Docs
        run: |
          # Your deployment script here
```

**Enable GitHub Pages:**
1. Go to repository Settings → Pages
2. Select `gh-pages` branch as source
3. Save

Your documentation will be available at: `https://username.github.io/repository/`

## GitLab Pages Deployment

Add to `.gitlab-ci.yml`:

```yaml
pages:
  stage: deploy
  script:
    - python accudoc_cli.py export . -o public/index.html --format html
  artifacts:
    paths:
      - public
  only:
    - main
```

Documentation will be available at: `https://username.gitlab.io/repository/`

## Netlify Deployment

### Option 1: Manual Deployment

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=docs
```

### Option 2: Continuous Deployment (Recommended)

1. Connect your repository to Netlify
2. Configure build settings:
   - **Build command**: `python accudoc_cli.py export . -o docs/index.html --format html`
   - **Publish directory**: `docs`

Create `netlify.toml`:

```toml
[build]
  command = "python accudoc_cli.py export . -o docs/index.html --format html"
  publish = "docs"

[build.environment]
  PYTHON_VERSION = "3.9"
```

## Deployment Best Practices

1. **Version Your Documentation** - Use git tags to track documentation versions
2. **Automate Everything** - Use CI/CD for automatic deployments
3. **Test Before Deploy** - Generate docs locally to verify
4. **Use HTTPS** - All platforms support HTTPS by default
5. **Monitor Deployments** - Set up notifications for deployment status

## Troubleshooting

### GitHub Pages not updating
- Ensure gh-pages branch exists
- Check Pages settings in repository
- Verify workflows have correct permissions

### Netlify build failing
- Check build logs in Netlify dashboard
- Verify Python version compatibility
- Ensure all dependencies are available

### GitLab Pages not working
- Verify .gitlab-ci.yml syntax
- Check CI/CD pipelines in GitLab
- Ensure artifacts path is `public`

## Advanced Configurations

### Custom Domain

**GitHub Pages:**
Add `CNAME` file with your domain:
```
docs.yourdomain.com
```

**Netlify:**
Configure in Netlify dashboard under Domain settings

### Build Optimization

- Use caching to speed up builds
- Generate only changed documentation
- Minimize asset sizes

### Multi-Version Documentation

Deploy different versions to subdirectories:
```
/latest/  - Latest documentation
/v1.0/    - Version 1.0 documentation  
/v2.0/    - Version 2.0 documentation
```

## Security Considerations

1. Don't commit secrets to repository
2. Use environment variables for tokens
3. Review generated documentation before deployment
4. Set up branch protection rules
5. Enable HTTPS and HSTS

## Support

For issues or questions:
- GitHub: https://github.com/jamesellette/AccuDoc
- Documentation: https://accudoc.readthedocs.io
'''
