"""
Monorepo support module for AccuDoc.

Detects and handles monorepo structures with multiple projects,
including package managers like Lerna, Nx, Turborepo, Yarn Workspaces,
and simple directory-based monorepos.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from accudoc.scanner import RepositoryScanner


class MonorepoDetector:
    """Detects and analyzes monorepo structures."""
    
    def __init__(self, repo_path: str):
        """
        Initialize monorepo detector.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.monorepo')
        
    def is_monorepo(self) -> bool:
        """
        Detect if repository is a monorepo.
        
        Returns:
            True if monorepo structure detected
        """
        indicators = [
            self._has_lerna(),
            self._has_nx(),
            self._has_turborepo(),
            self._has_yarn_workspaces(),
            self._has_pnpm_workspaces(),
            self._has_multi_package_structure()
        ]
        
        return any(indicators)
    
    def _has_lerna(self) -> bool:
        """Check for Lerna monorepo."""
        return (self.repo_path / 'lerna.json').exists()
    
    def _has_nx(self) -> bool:
        """Check for Nx monorepo."""
        return (self.repo_path / 'nx.json').exists()
    
    def _has_turborepo(self) -> bool:
        """Check for Turborepo."""
        return (self.repo_path / 'turbo.json').exists()
    
    def _has_yarn_workspaces(self) -> bool:
        """Check for Yarn workspaces."""
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                return 'workspaces' in data
            except:
                pass
        return False
    
    def _has_pnpm_workspaces(self) -> bool:
        """Check for pnpm workspaces."""
        return (self.repo_path / 'pnpm-workspace.yaml').exists()
    
    def _has_multi_package_structure(self) -> bool:
        """Check for common multi-package directory structures."""
        common_dirs = ['packages', 'apps', 'libs', 'modules', 'services']
        for dirname in common_dirs:
            dir_path = self.repo_path / dirname
            if dir_path.is_dir():
                # Check if it has multiple subdirectories with package files
                subdirs = [d for d in dir_path.iterdir() if d.is_dir()]
                if len(subdirs) >= 2:
                    # Check if at least 2 have package indicators
                    package_indicators = 0
                    for subdir in subdirs[:5]:  # Check first 5
                        if self._has_package_indicators(subdir):
                            package_indicators += 1
                    if package_indicators >= 2:
                        return True
        return False
    
    def _has_package_indicators(self, path: Path) -> bool:
        """Check if directory has package indicators."""
        indicators = [
            'package.json', 'setup.py', 'pyproject.toml', 'Cargo.toml',
            'pom.xml', 'build.gradle', 'go.mod', 'composer.json'
        ]
        return any((path / indicator).exists() for indicator in indicators)
    
    def detect_monorepo_type(self) -> str:
        """
        Detect the type of monorepo.
        
        Returns:
            Monorepo type string
        """
        if self._has_lerna():
            return 'lerna'
        elif self._has_nx():
            return 'nx'
        elif self._has_turborepo():
            return 'turborepo'
        elif self._has_yarn_workspaces():
            return 'yarn_workspaces'
        elif self._has_pnpm_workspaces():
            return 'pnpm_workspaces'
        elif self._has_multi_package_structure():
            return 'multi_package'
        return 'unknown'
    
    def find_projects(self) -> List[Dict[str, Any]]:
        """
        Find all projects/packages in the monorepo.
        
        Returns:
            List of project information dictionaries
        """
        projects = []
        monorepo_type = self.detect_monorepo_type()
        
        if monorepo_type == 'lerna':
            projects = self._find_lerna_projects()
        elif monorepo_type == 'nx':
            projects = self._find_nx_projects()
        elif monorepo_type in ['yarn_workspaces', 'pnpm_workspaces']:
            projects = self._find_workspace_projects()
        else:
            projects = self._find_generic_projects()
        
        return projects
    
    def _find_lerna_projects(self) -> List[Dict[str, Any]]:
        """Find projects in Lerna monorepo."""
        projects = []
        lerna_json = self.repo_path / 'lerna.json'
        
        try:
            with open(lerna_json, 'r') as f:
                config = json.load(f)
            
            packages = config.get('packages', ['packages/*'])
            for pattern in packages:
                # Simple glob pattern handling
                if '*' in pattern:
                    base_dir = pattern.split('*')[0].rstrip('/')
                    base_path = self.repo_path / base_dir
                    if base_path.is_dir():
                        for subdir in base_path.iterdir():
                            if subdir.is_dir() and (subdir / 'package.json').exists():
                                projects.append(self._get_project_info(subdir))
                else:
                    project_path = self.repo_path / pattern
                    if project_path.is_dir() and (project_path / 'package.json').exists():
                        projects.append(self._get_project_info(project_path))
        except Exception as e:
            self.logger.error(f"Error finding Lerna projects: {e}")
        
        return projects
    
    def _find_nx_projects(self) -> List[Dict[str, Any]]:
        """Find projects in Nx monorepo."""
        projects = []
        workspace_json = self.repo_path / 'workspace.json'
        
        # Nx can use workspace.json or angular.json or project.json files
        if workspace_json.exists():
            try:
                with open(workspace_json, 'r') as f:
                    config = json.load(f)
                
                for project_name, project_config in config.get('projects', {}).items():
                    project_root = project_config.get('root', project_name)
                    project_path = self.repo_path / project_root
                    if project_path.is_dir():
                        projects.append(self._get_project_info(project_path, project_name))
            except Exception as e:
                self.logger.error(f"Error finding Nx projects: {e}")
        else:
            # Fall back to common directory structure
            for dirname in ['apps', 'libs', 'packages']:
                dir_path = self.repo_path / dirname
                if dir_path.is_dir():
                    for subdir in dir_path.iterdir():
                        if subdir.is_dir() and self._has_package_indicators(subdir):
                            projects.append(self._get_project_info(subdir))
        
        return projects
    
    def _find_workspace_projects(self) -> List[Dict[str, Any]]:
        """Find projects in Yarn/pnpm workspaces."""
        projects = []
        package_json = self.repo_path / 'package.json'
        
        try:
            with open(package_json, 'r') as f:
                config = json.load(f)
            
            workspaces = config.get('workspaces', [])
            if isinstance(workspaces, dict):
                workspaces = workspaces.get('packages', [])
            
            for pattern in workspaces:
                # Simple glob pattern handling
                if '*' in pattern:
                    base_dir = pattern.split('*')[0].rstrip('/')
                    base_path = self.repo_path / base_dir
                    if base_path.is_dir():
                        for subdir in base_path.iterdir():
                            if subdir.is_dir() and (subdir / 'package.json').exists():
                                projects.append(self._get_project_info(subdir))
                else:
                    project_path = self.repo_path / pattern
                    if project_path.is_dir():
                        projects.append(self._get_project_info(project_path))
        except Exception as e:
            self.logger.error(f"Error finding workspace projects: {e}")
        
        return projects
    
    def _find_generic_projects(self) -> List[Dict[str, Any]]:
        """Find projects in generic multi-package structure."""
        projects = []
        common_dirs = ['packages', 'apps', 'libs', 'modules', 'services']
        
        for dirname in common_dirs:
            dir_path = self.repo_path / dirname
            if dir_path.is_dir():
                for subdir in dir_path.iterdir():
                    if subdir.is_dir() and self._has_package_indicators(subdir):
                        projects.append(self._get_project_info(subdir))
        
        return projects
    
    def _get_project_info(self, project_path: Path, name: str = None) -> Dict[str, Any]:
        """
        Get information about a project.
        
        Args:
            project_path: Path to project
            name: Optional project name
            
        Returns:
            Project information dictionary
        """
        info = {
            'name': name or project_path.name,
            'path': str(project_path.relative_to(self.repo_path)),
            'absolute_path': str(project_path)
        }
        
        # Try to get package name from package.json
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                info['package_name'] = data.get('name', info['name'])
                info['version'] = data.get('version', 'unknown')
                info['description'] = data.get('description', '')
                info['type'] = 'javascript'
            except:
                pass
        
        # Check for Python package
        elif (project_path / 'setup.py').exists() or (project_path / 'pyproject.toml').exists():
            info['type'] = 'python'
        
        # Check for other types
        elif (project_path / 'Cargo.toml').exists():
            info['type'] = 'rust'
        elif (project_path / 'go.mod').exists():
            info['type'] = 'go'
        elif (project_path / 'pom.xml').exists():
            info['type'] = 'java'
        
        return info
    
    def scan_monorepo(self) -> Dict[str, Any]:
        """
        Scan entire monorepo and return comprehensive information.
        
        Returns:
            Monorepo information and project scans
        """
        if not self.is_monorepo():
            return {
                'is_monorepo': False,
                'message': 'Not a monorepo structure'
            }
        
        monorepo_type = self.detect_monorepo_type()
        projects = self.find_projects()
        
        result = {
            'is_monorepo': True,
            'type': monorepo_type,
            'project_count': len(projects),
            'projects': []
        }
        
        # Scan each project
        for project in projects:
            project_info = project.copy()
            
            # Use RepositoryScanner for detailed analysis
            try:
                scanner = RepositoryScanner(project['absolute_path'])
                scan_result = scanner.scan()
                project_info['scan'] = {
                    'languages': scan_result.get('languages', {}),
                    'files': len(scan_result.get('files', [])),
                    'dependencies': list(scan_result.get('dependencies', {}).keys())
                }
            except Exception as e:
                self.logger.error(f"Error scanning project {project['name']}: {e}")
                project_info['scan_error'] = str(e)
            
            result['projects'].append(project_info)
        
        return result
    
    def generate_monorepo_documentation(self, monorepo_data: Dict[str, Any]) -> str:
        """
        Generate markdown documentation for monorepo.
        
        Args:
            monorepo_data: Data from scan_monorepo()
            
        Returns:
            Markdown documentation
        """
        if not monorepo_data.get('is_monorepo'):
            return "# Repository Analysis\n\nThis is not a monorepo structure."
        
        md = []
        md.append("# Monorepo Documentation\n")
        md.append(f"**Type**: {monorepo_data['type']}")
        md.append(f"**Projects**: {monorepo_data['project_count']}\n")
        
        md.append("## Projects Overview\n")
        md.append("| Project | Type | Path | Languages |")
        md.append("|---------|------|------|-----------|")
        
        for project in monorepo_data['projects']:
            proj_type = project.get('type', 'unknown')
            path = project.get('path', '')
            
            if 'scan' in project:
                languages = ', '.join(project['scan'].get('languages', {}).keys())
            else:
                languages = 'N/A'
            
            md.append(f"| {project['name']} | {proj_type} | {path} | {languages} |")
        
        md.append("")
        
        # Detailed project information
        md.append("## Project Details\n")
        
        for project in monorepo_data['projects']:
            md.append(f"### {project['name']}\n")
            md.append(f"**Path**: `{project.get('path', '')}`")
            
            if 'version' in project:
                md.append(f"**Version**: {project['version']}")
            
            if 'description' in project and project['description']:
                md.append(f"**Description**: {project['description']}")
            
            if 'scan' in project:
                scan = project['scan']
                md.append(f"**Files**: {scan.get('files', 0)}")
                
                languages = scan.get('languages', {})
                if languages:
                    md.append(f"**Languages**: {', '.join(languages.keys())}")
                
                dependencies = scan.get('dependencies', [])
                if dependencies:
                    md.append(f"**Dependency Managers**: {', '.join(dependencies)}")
            
            md.append("")
        
        return '\n'.join(md)
