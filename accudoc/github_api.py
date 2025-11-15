"""
GitHub API integration module for AccuDoc.

Provides direct access to GitHub repositories via API without cloning,
significantly faster for remote repositories and lower disk usage.
"""

import json
import base64
import logging
from typing import Dict, List, Optional, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pathlib import Path
import tempfile
import shutil


class GitHubAPIClient:
    """Client for GitHub API integration."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token (optional but recommended)
        """
        self.token = token
        self.logger = logging.getLogger('accudoc.github')
        
    def _make_request(self, endpoint: str) -> Dict:
        """
        Make a request to GitHub API.
        
        Args:
            endpoint: API endpoint (e.g., '/repos/owner/repo')
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AccuDoc-Documentation-Generator'
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            if e.code == 403:
                self.logger.warning("Rate limit exceeded. Consider using authentication token.")
            raise Exception(f"GitHub API error: {e.code} {e.reason}")
        except URLError as e:
            raise Exception(f"Network error: {str(e)}")
    
    def parse_github_url(self, url: str) -> tuple:
        """
        Parse GitHub repository URL.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo)
        """
        # Handle various URL formats
        url = url.rstrip('/')
        
        if url.startswith('https://github.com/'):
            parts = url.replace('https://github.com/', '').split('/')
        elif url.startswith('git@github.com:'):
            parts = url.replace('git@github.com:', '').replace('.git', '').split('/')
        else:
            raise ValueError(f"Invalid GitHub URL: {url}")
        
        if len(parts) >= 2:
            return parts[0], parts[1].replace('.git', '')
        else:
            raise ValueError(f"Could not parse GitHub URL: {url}")
    
    def get_repository_info(self, owner: str, repo: str) -> Dict:
        """
        Get repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information
        """
        return self._make_request(f'/repos/{owner}/{repo}')
    
    def get_repository_tree(self, owner: str, repo: str, 
                           branch: str = 'main') -> List[Dict]:
        """
        Get repository file tree recursively.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            List of file/directory entries
        """
        try:
            # Get the tree SHA for the branch
            ref = self._make_request(f'/repos/{owner}/{repo}/git/ref/heads/{branch}')
            commit_sha = ref['object']['sha']
            
            # Get the commit to find tree SHA
            commit = self._make_request(f'/repos/{owner}/{repo}/git/commits/{commit_sha}')
            tree_sha = commit['tree']['sha']
            
            # Get the tree recursively
            tree = self._make_request(f'/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1')
            
            return tree.get('tree', [])
        except Exception as e:
            # Try 'master' branch if 'main' fails
            if branch == 'main':
                self.logger.info("Branch 'main' not found, trying 'master'")
                return self.get_repository_tree(owner, repo, branch='master')
            raise
    
    def get_file_content(self, owner: str, repo: str, path: str, 
                        branch: str = 'main') -> str:
        """
        Get content of a specific file.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path in repository
            branch: Branch name
            
        Returns:
            File content as string
        """
        try:
            data = self._make_request(f'/repos/{owner}/{repo}/contents/{path}?ref={branch}')
            
            if data.get('type') == 'file':
                # Decode base64 content
                content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                return content
            else:
                raise ValueError(f"Path is not a file: {path}")
        except Exception as e:
            self.logger.error(f"Error getting file {path}: {str(e)}")
            return ""
    
    def get_readme(self, owner: str, repo: str) -> str:
        """
        Get repository README content.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content
        """
        try:
            data = self._make_request(f'/repos/{owner}/{repo}/readme')
            content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
            return content
        except Exception:
            return ""
    
    def get_languages(self, owner: str, repo: str) -> Dict:
        """
        Get repository languages.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary of languages and byte counts
        """
        return self._make_request(f'/repos/{owner}/{repo}/languages')
    
    def get_contributors(self, owner: str, repo: str) -> List[Dict]:
        """
        Get repository contributors.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of contributors
        """
        try:
            return self._make_request(f'/repos/{owner}/{repo}/contributors')
        except Exception:
            return []
    
    def get_commits(self, owner: str, repo: str, 
                   per_page: int = 100) -> List[Dict]:
        """
        Get recent commits.
        
        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Number of commits to retrieve
            
        Returns:
            List of commits
        """
        try:
            return self._make_request(f'/repos/{owner}/{repo}/commits?per_page={per_page}')
        except Exception:
            return []
    
    def download_repository_snapshot(self, owner: str, repo: str, 
                                    branch: str = 'main') -> Path:
        """
        Download repository as a snapshot to temporary directory.
        
        This is a fallback when full API scanning isn't sufficient.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            Path to temporary directory with repository files
        """
        temp_dir = Path(tempfile.mkdtemp(prefix='accudoc_'))
        
        try:
            # Get file tree
            tree = self.get_repository_tree(owner, repo, branch)
            
            # Download files
            for item in tree:
                if item['type'] == 'blob':  # File
                    file_path = temp_dir / item['path']
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        content = self.get_file_content(owner, repo, item['path'], branch)
                        file_path.write_text(content, encoding='utf-8', errors='ignore')
                    except Exception as e:
                        self.logger.debug(f"Could not download {item['path']}: {str(e)}")
            
            return temp_dir
        except Exception as e:
            # Clean up on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to download repository snapshot: {str(e)}")
    
    def scan_via_api(self, owner: str, repo: str, branch: str = 'main') -> Dict:
        """
        Scan repository using GitHub API without cloning.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            Repository information suitable for AccuDoc scanner
        """
        self.logger.info(f"Scanning {owner}/{repo} via GitHub API")
        
        # Get repository metadata
        repo_info = self.get_repository_info(owner, repo)
        
        # Get file tree
        tree = self.get_repository_tree(owner, repo, branch)
        
        # Extract file list
        files = [item['path'] for item in tree if item['type'] == 'blob']
        
        # Get languages
        languages = self.get_languages(owner, repo)
        
        # Get README
        readme_content = self.get_readme(owner, repo)
        
        # Get contributors
        contributors = self.get_contributors(owner, repo)
        
        # Get recent commits
        commits = self.get_commits(owner, repo, per_page=50)
        
        # Build result similar to local scanner
        result = {
            'name': repo_info['name'],
            'description': repo_info.get('description', ''),
            'url': repo_info['html_url'],
            'files': files,
            'languages': {lang: count for lang, count in languages.items()},
            'readme_content': readme_content,
            'git_info': {
                'default_branch': repo_info['default_branch'],
                'created_at': repo_info['created_at'],
                'updated_at': repo_info['updated_at'],
                'stars': repo_info['stargazers_count'],
                'forks': repo_info['forks_count'],
                'open_issues': repo_info['open_issues_count'],
                'license': repo_info.get('license', {}).get('name', 'Unknown'),
                'contributors': [
                    {
                        'login': c['login'],
                        'contributions': c['contributions']
                    }
                    for c in contributors[:10]  # Top 10
                ],
                'recent_commits': [
                    {
                        'sha': c['sha'][:7],
                        'message': c['commit']['message'].split('\n')[0],
                        'author': c['commit']['author']['name'],
                        'date': c['commit']['author']['date']
                    }
                    for c in commits[:20]  # Last 20
                ]
            },
            'api_scan': True,
            'branch': branch
        }
        
        return result


def scan_github_repository(github_url: str, token: Optional[str] = None, 
                          branch: str = 'main') -> Dict:
    """
    Convenience function to scan a GitHub repository.
    
    Args:
        github_url: GitHub repository URL
        token: GitHub personal access token (optional)
        branch: Branch to scan
        
    Returns:
        Repository scan results
    """
    client = GitHubAPIClient(token=token)
    owner, repo = client.parse_github_url(github_url)
    return client.scan_via_api(owner, repo, branch)
