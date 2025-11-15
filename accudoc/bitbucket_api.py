"""
Bitbucket API integration module for AccuDoc.

Provides direct access to Bitbucket repositories via API without cloning,
similar to GitHub and GitLab API integrations.
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


class BitbucketAPIClient:
    """Client for Bitbucket API integration."""
    
    BASE_URL = "https://api.bitbucket.org/2.0"
    
    def __init__(self, username: Optional[str] = None, app_password: Optional[str] = None):
        """
        Initialize Bitbucket API client.
        
        Args:
            username: Bitbucket username (optional but recommended for private repos)
            app_password: Bitbucket app password (optional but recommended for private repos)
        """
        self.username = username
        self.app_password = app_password
        self.logger = logging.getLogger('accudoc.bitbucket')
        
    def _make_request(self, endpoint: str) -> Dict:
        """
        Make a request to Bitbucket API.
        
        Args:
            endpoint: API endpoint (e.g., '/repositories/workspace/repo')
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'AccuDoc-Documentation-Generator'
        }
        
        # Add authentication if credentials provided
        if self.username and self.app_password:
            auth_string = f"{self.username}:{self.app_password}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            headers['Authorization'] = f'Basic {auth_b64}'
        
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            if e.code == 429:
                self.logger.warning("Rate limit exceeded. Consider using authentication.")
            elif e.code == 401:
                self.logger.warning("Authentication failed. Check credentials.")
            raise Exception(f"Bitbucket API error: {e.code} {e.reason}")
        except URLError as e:
            raise Exception(f"Network error: {str(e)}")
    
    def parse_bitbucket_url(self, url: str) -> tuple:
        """
        Parse Bitbucket repository URL.
        
        Args:
            url: Bitbucket repository URL
            
        Returns:
            Tuple of (workspace, repo_slug)
        """
        # Handle various URL formats
        url = url.rstrip('/')
        
        if url.startswith('https://bitbucket.org/'):
            parts = url.replace('https://bitbucket.org/', '').split('/')
        elif url.startswith('http://bitbucket.org/'):
            parts = url.replace('http://bitbucket.org/', '').split('/')
        elif url.startswith('git@bitbucket.org:'):
            parts = url.replace('git@bitbucket.org:', '').replace('.git', '').split('/')
        else:
            raise ValueError(f"Invalid Bitbucket URL: {url}")
        
        if len(parts) >= 2:
            workspace = parts[0]
            repo_slug = parts[1].replace('.git', '')
            return workspace, repo_slug
        else:
            raise ValueError(f"Could not parse Bitbucket URL: {url}")
    
    def get_repository_info(self, workspace: str, repo_slug: str) -> Dict:
        """
        Get repository information.
        
        Args:
            workspace: Repository workspace
            repo_slug: Repository slug/name
            
        Returns:
            Repository information
        """
        return self._make_request(f'/repositories/{workspace}/{repo_slug}')
    
    def get_repository_tree(self, workspace: str, repo_slug: str, 
                           branch: str = 'main') -> List[Dict]:
        """
        Get repository file tree recursively.
        
        Args:
            workspace: Repository workspace
            repo_slug: Repository slug/name
            branch: Branch name
            
        Returns:
            List of file/directory entries
        """
        all_files = []
        
        def fetch_tree(path: str = ''):
            """Recursively fetch directory tree."""
            endpoint = f'/repositories/{workspace}/{repo_slug}/src/{branch}/{path}'
            try:
                response = self._make_request(endpoint)
                
                if 'values' in response:
                    for item in response['values']:
                        if item['type'] == 'commit_file':
                            all_files.append({
                                'path': item['path'],
                                'type': 'file',
                                'size': item.get('size', 0)
                            })
                        elif item['type'] == 'commit_directory':
                            # Recursively fetch subdirectory
                            fetch_tree(item['path'])
            except Exception as e:
                self.logger.debug(f"Error fetching tree for {path}: {str(e)}")
        
        try:
            fetch_tree()
            return all_files
        except Exception as e:
            # Try 'master' branch if 'main' fails
            if branch == 'main':
                self.logger.info("Branch 'main' not found, trying 'master'")
                return self.get_repository_tree(workspace, repo_slug, branch='master')
            raise
    
    def get_file_content(self, workspace: str, repo_slug: str, path: str, 
                        branch: str = 'main') -> str:
        """
        Get content of a specific file.
        
        Args:
            workspace: Repository workspace
            repo_slug: Repository slug/name
            path: File path in repository
            branch: Branch name
            
        Returns:
            File content as string
        """
        try:
            # Bitbucket returns raw file content
            url = f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/src/{branch}/{path}"
            headers = {
                'User-Agent': 'AccuDoc-Documentation-Generator'
            }
            
            if self.username and self.app_password:
                auth_string = f"{self.username}:{self.app_password}"
                auth_bytes = auth_string.encode('ascii')
                auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                headers['Authorization'] = f'Basic {auth_b64}'
            
            request = Request(url, headers=headers)
            with urlopen(request, timeout=30) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            self.logger.error(f"Error getting file {path}: {str(e)}")
            return ""
    
    def get_readme(self, workspace: str, repo_slug: str, branch: str = 'main') -> str:
        """
        Get repository README content.
        
        Args:
            workspace: Repository workspace
            repo_slug: Repository slug/name
            branch: Branch name
            
        Returns:
            README content
        """
        # Try common README filenames
        readme_names = ['README.md', 'README', 'readme.md', 'readme']
        
        for name in readme_names:
            try:
                content = self.get_file_content(workspace, repo_slug, name, branch)
                if content:
                    return content
            except Exception:
                continue
        
        return ""
    
    def get_languages(self, workspace: str, repo_slug: str) -> Dict:
        """
        Get repository languages (estimated from file extensions).
        
        Note: Bitbucket API doesn't provide language statistics directly,
        so this is a basic implementation based on file extensions.
        
        Args:
            workspace: Repository workspace
            repo_slug: Repository slug/name
            
        Returns:
            Dictionary of languages and file counts
        """
        try:
            tree = self.get_repository_tree(workspace, repo_slug)
            
            # Simple language detection based on file extensions
            language_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.java': 'Java',
                '.c': 'C',
                '.cpp': 'C++',
                '.cs': 'C#',
                '.rb': 'Ruby',
                '.go': 'Go',
                '.php': 'PHP',
                '.swift': 'Swift',
                '.kt': 'Kotlin',
                '.rs': 'Rust',
                '.scala': 'Scala',
                '.r': 'R',
                '.m': 'Objective-C',
                '.sh': 'Shell',
                '.sql': 'SQL',
                '.html': 'HTML',
                '.css': 'CSS',
                '.json': 'JSON',
                '.xml': 'XML',
                '.yaml': 'YAML',
                '.yml': 'YAML',
            }
            
            languages = {}
            for item in tree:
                if item['type'] == 'file':
                    path = item['path']
                    ext = Path(path).suffix.lower()
                    if ext in language_map:
                        lang = language_map[ext]
                        languages[lang] = languages.get(lang, 0) + 1
            
            return languages
        except Exception:
            return {}
    
    def get_commits(self, workspace: str, repo_slug: str, 
                   branch: str = 'main', limit: int = 50) -> List[Dict]:
        """
        Get recent commits.
        
        Args:
            workspace: Repository workspace
            repo_slug: Repository slug/name
            branch: Branch name
            limit: Number of commits to retrieve
            
        Returns:
            List of commits
        """
        try:
            endpoint = f'/repositories/{workspace}/{repo_slug}/commits/{branch}?pagelen={limit}'
            response = self._make_request(endpoint)
            return response.get('values', [])
        except Exception:
            return []
    
    def scan_via_api(self, workspace: str, repo_slug: str, branch: str = 'main') -> Dict:
        """
        Scan repository using Bitbucket API without cloning.
        
        Args:
            workspace: Repository workspace
            repo_slug: Repository slug/name
            branch: Branch name
            
        Returns:
            Repository information suitable for AccuDoc scanner
        """
        self.logger.info(f"Scanning {workspace}/{repo_slug} via Bitbucket API")
        
        # Get repository metadata
        repo_info = self.get_repository_info(workspace, repo_slug)
        
        # Get file tree
        tree = self.get_repository_tree(workspace, repo_slug, branch)
        
        # Extract file list
        files = [item['path'] for item in tree if item['type'] == 'file']
        
        # Get languages (basic implementation)
        languages = self.get_languages(workspace, repo_slug)
        
        # Get README
        readme_content = self.get_readme(workspace, repo_slug, branch)
        
        # Get recent commits
        commits = self.get_commits(workspace, repo_slug, branch, limit=50)
        
        # Build result similar to local scanner
        result = {
            'name': repo_info['name'],
            'description': repo_info.get('description', ''),
            'url': repo_info['links']['html']['href'],
            'files': files,
            'languages': languages,
            'readme_content': readme_content,
            'git_info': {
                'default_branch': repo_info['mainbranch']['name'] if 'mainbranch' in repo_info else 'main',
                'created_at': repo_info['created_on'],
                'updated_at': repo_info['updated_on'],
                'size': repo_info.get('size', 0),
                'is_private': repo_info.get('is_private', False),
                'recent_commits': [
                    {
                        'sha': c['hash'][:7],
                        'message': c['message'].split('\n')[0],
                        'author': c['author']['user']['display_name'] if 'user' in c['author'] else c['author']['raw'],
                        'date': c['date']
                    }
                    for c in commits[:20]  # Last 20
                ]
            },
            'api_scan': True,
            'source': 'bitbucket',
            'branch': branch
        }
        
        return result


def scan_bitbucket_repository(bitbucket_url: str, username: Optional[str] = None,
                              app_password: Optional[str] = None,
                              branch: str = 'main') -> Dict:
    """
    Convenience function to scan a Bitbucket repository.
    
    Args:
        bitbucket_url: Bitbucket repository URL
        username: Bitbucket username (optional)
        app_password: Bitbucket app password (optional)
        branch: Branch to scan
        
    Returns:
        Repository scan results
    """
    client = BitbucketAPIClient(username=username, app_password=app_password)
    workspace, repo_slug = client.parse_bitbucket_url(bitbucket_url)
    return client.scan_via_api(workspace, repo_slug, branch)
