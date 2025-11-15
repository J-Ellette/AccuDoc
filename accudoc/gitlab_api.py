"""
GitLab API integration module for AccuDoc.

Provides direct access to GitLab repositories via API without cloning,
similar to GitHub API integration.
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


class GitLabAPIClient:
    """Client for GitLab API integration."""
    
    BASE_URL = "https://gitlab.com/api/v4"
    
    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize GitLab API client.
        
        Args:
            token: GitLab personal access token (optional but recommended)
            base_url: Custom GitLab instance URL (defaults to gitlab.com)
        """
        self.token = token
        self.base_url = base_url or self.BASE_URL
        self.logger = logging.getLogger('accudoc.gitlab')
        
    def _make_request(self, endpoint: str) -> Dict:
        """
        Make a request to GitLab API.
        
        Args:
            endpoint: API endpoint (e.g., '/projects/12345')
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'AccuDoc-Documentation-Generator'
        }
        
        if self.token:
            headers['PRIVATE-TOKEN'] = self.token
        
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            if e.code == 429:
                self.logger.warning("Rate limit exceeded. Consider using authentication token.")
            raise Exception(f"GitLab API error: {e.code} {e.reason}")
        except URLError as e:
            raise Exception(f"Network error: {str(e)}")
    
    def parse_gitlab_url(self, url: str) -> tuple:
        """
        Parse GitLab repository URL.
        
        Args:
            url: GitLab repository URL
            
        Returns:
            Tuple of (namespace, project)
        """
        # Handle various URL formats
        url = url.rstrip('/')
        
        # Extract base URL and project path
        if url.startswith('https://gitlab.com/'):
            parts = url.replace('https://gitlab.com/', '').split('/')
        elif url.startswith('http://gitlab.com/'):
            parts = url.replace('http://gitlab.com/', '').split('/')
        elif url.startswith('git@gitlab.com:'):
            parts = url.replace('git@gitlab.com:', '').replace('.git', '').split('/')
        elif 'gitlab' in url and url.startswith('https://'):
            # Custom GitLab instance
            base_url = url.split('/')[0] + '//' + url.split('/')[2]
            self.base_url = base_url + '/api/v4'
            path = '/'.join(url.split('/')[3:])
            parts = path.replace('.git', '').split('/')
        else:
            raise ValueError(f"Invalid GitLab URL: {url}")
        
        if len(parts) >= 2:
            # For nested groups: namespace/subgroup/project
            namespace = '/'.join(parts[:-1])
            project = parts[-1].replace('.git', '')
            return namespace, project
        else:
            raise ValueError(f"Could not parse GitLab URL: {url}")
    
    def get_project_id(self, namespace: str, project: str) -> int:
        """
        Get project ID from namespace and project name.
        
        Args:
            namespace: Project namespace (user or group)
            project: Project name
            
        Returns:
            Project ID
        """
        # URL encode the project path
        import urllib.parse
        project_path = f"{namespace}/{project}"
        encoded_path = urllib.parse.quote(project_path, safe='')
        
        project_info = self._make_request(f'/projects/{encoded_path}')
        return project_info['id']
    
    def get_project_info(self, project_id: int) -> Dict:
        """
        Get project information.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project information
        """
        return self._make_request(f'/projects/{project_id}')
    
    def get_repository_tree(self, project_id: int, 
                           branch: str = 'main', 
                           recursive: bool = True) -> List[Dict]:
        """
        Get repository file tree.
        
        Args:
            project_id: Project ID
            branch: Branch name
            recursive: Whether to get tree recursively
            
        Returns:
            List of file/directory entries
        """
        params = f"?ref={branch}&recursive={str(recursive).lower()}&per_page=100"
        
        try:
            return self._make_request(f'/projects/{project_id}/repository/tree{params}')
        except Exception as e:
            # Try 'master' branch if 'main' fails
            if branch == 'main':
                self.logger.info("Branch 'main' not found, trying 'master'")
                return self.get_repository_tree(project_id, branch='master', recursive=recursive)
            raise
    
    def get_file_content(self, project_id: int, file_path: str, 
                        branch: str = 'main') -> str:
        """
        Get content of a specific file.
        
        Args:
            project_id: Project ID
            file_path: File path in repository
            branch: Branch name
            
        Returns:
            File content as string
        """
        import urllib.parse
        encoded_path = urllib.parse.quote(file_path, safe='')
        
        try:
            data = self._make_request(
                f'/projects/{project_id}/repository/files/{encoded_path}?ref={branch}'
            )
            
            # Decode base64 content
            content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
            return content
        except Exception as e:
            self.logger.error(f"Error getting file {file_path}: {str(e)}")
            return ""
    
    def get_readme(self, project_id: int, branch: str = 'main') -> str:
        """
        Get project README content.
        
        Args:
            project_id: Project ID
            branch: Branch name
            
        Returns:
            README content
        """
        # Try common README filenames
        readme_names = ['README.md', 'README', 'readme.md', 'readme']
        
        for name in readme_names:
            try:
                return self.get_file_content(project_id, name, branch)
            except Exception:
                continue
        
        return ""
    
    def get_languages(self, project_id: int) -> Dict:
        """
        Get project languages.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary of languages and percentages
        """
        return self._make_request(f'/projects/{project_id}/languages')
    
    def get_contributors(self, project_id: int) -> List[Dict]:
        """
        Get project contributors.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of contributors
        """
        try:
            return self._make_request(f'/projects/{project_id}/repository/contributors')
        except Exception:
            return []
    
    def get_commits(self, project_id: int, per_page: int = 50) -> List[Dict]:
        """
        Get recent commits.
        
        Args:
            project_id: Project ID
            per_page: Number of commits to retrieve
            
        Returns:
            List of commits
        """
        try:
            return self._make_request(f'/projects/{project_id}/repository/commits?per_page={per_page}')
        except Exception:
            return []
    
    def scan_via_api(self, namespace: str, project: str, branch: str = 'main') -> Dict:
        """
        Scan repository using GitLab API without cloning.
        
        Args:
            namespace: Project namespace
            project: Project name
            branch: Branch name
            
        Returns:
            Repository information suitable for AccuDoc scanner
        """
        self.logger.info(f"Scanning {namespace}/{project} via GitLab API")
        
        # Get project ID
        project_id = self.get_project_id(namespace, project)
        
        # Get project metadata
        project_info = self.get_project_info(project_id)
        
        # Get file tree
        tree = self.get_repository_tree(project_id, branch)
        
        # Extract file list (only blobs/files)
        files = [item['path'] for item in tree if item['type'] == 'blob']
        
        # Get languages
        languages = self.get_languages(project_id)
        
        # Get README
        readme_content = self.get_readme(project_id, branch)
        
        # Get contributors
        contributors = self.get_contributors(project_id)
        
        # Get recent commits
        commits = self.get_commits(project_id, per_page=50)
        
        # Build result similar to local scanner
        result = {
            'name': project_info['name'],
            'description': project_info.get('description', ''),
            'url': project_info['web_url'],
            'files': files,
            'languages': languages,
            'readme_content': readme_content,
            'git_info': {
                'default_branch': project_info['default_branch'],
                'created_at': project_info['created_at'],
                'updated_at': project_info['last_activity_at'],
                'stars': project_info.get('star_count', 0),
                'forks': project_info.get('forks_count', 0),
                'open_issues': project_info.get('open_issues_count', 0),
                'license': 'Unknown',  # GitLab API doesn't provide license info easily
                'contributors': [
                    {
                        'name': c['name'],
                        'email': c['email'],
                        'commits': c['commits']
                    }
                    for c in contributors[:10]  # Top 10
                ],
                'recent_commits': [
                    {
                        'sha': c['id'][:7],
                        'message': c['message'].split('\n')[0],
                        'author': c['author_name'],
                        'date': c['created_at']
                    }
                    for c in commits[:20]  # Last 20
                ]
            },
            'api_scan': True,
            'source': 'gitlab',
            'branch': branch
        }
        
        return result


def scan_gitlab_repository(gitlab_url: str, token: Optional[str] = None, 
                          branch: str = 'main') -> Dict:
    """
    Convenience function to scan a GitLab repository.
    
    Args:
        gitlab_url: GitLab repository URL
        token: GitLab personal access token (optional)
        branch: Branch to scan
        
    Returns:
        Repository scan results
    """
    client = GitLabAPIClient(token=token)
    namespace, project = client.parse_gitlab_url(gitlab_url)
    return client.scan_via_api(namespace, project, branch)
