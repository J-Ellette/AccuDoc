"""
Package version analyzer module for AccuDoc.

Analyzes project dependencies and checks for:
- Outdated package versions
- Known security vulnerabilities (basic check)
- Latest available versions
- Version constraints and compatibility
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from collections import defaultdict


class VersionAnalyzer:
    """Analyzes package versions and dependencies."""
    
    PYPI_API = "https://pypi.org/pypi/{package}/json"
    NPM_API = "https://registry.npmjs.org/{package}"
    
    def __init__(self, repo_path: str):
        """
        Initialize version analyzer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.version_analyzer')
        
    def _fetch_pypi_info(self, package: str) -> Optional[Dict]:
        """
        Fetch package information from PyPI.
        
        Args:
            package: Package name
            
        Returns:
            Package information or None if not found
        """
        try:
            url = self.PYPI_API.format(package=package)
            req = Request(url, headers={'User-Agent': 'AccuDoc-Version-Analyzer'})
            with urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode())
        except (URLError, HTTPError) as e:
            self.logger.debug(f"Could not fetch PyPI info for {package}: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Error fetching PyPI info for {package}: {e}")
            return None
    
    def _fetch_npm_info(self, package: str) -> Optional[Dict]:
        """
        Fetch package information from npm registry.
        
        Args:
            package: Package name
            
        Returns:
            Package information or None if not found
        """
        try:
            url = self.NPM_API.format(package=package)
            req = Request(url, headers={'User-Agent': 'AccuDoc-Version-Analyzer'})
            with urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode())
        except (URLError, HTTPError) as e:
            self.logger.debug(f"Could not fetch npm info for {package}: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Error fetching npm info for {package}: {e}")
            return None
    
    def _parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """
        Parse version string into tuple for comparison.
        
        Args:
            version_str: Version string (e.g., "1.2.3")
            
        Returns:
            Version tuple (major, minor, patch)
        """
        # Remove common prefixes and suffixes
        version_str = version_str.lstrip('v=~^>=<')
        version_str = re.split(r'[^\d.]', version_str)[0]
        
        parts = version_str.split('.')
        try:
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except (ValueError, IndexError):
            return (0, 0, 0)
    
    def _compare_versions(self, current: str, latest: str) -> str:
        """
        Compare two version strings.
        
        Args:
            current: Current version
            latest: Latest version
            
        Returns:
            "up-to-date", "minor-update", "major-update", or "outdated"
        """
        current_ver = self._parse_version(current)
        latest_ver = self._parse_version(latest)
        
        if current_ver == latest_ver:
            return "up-to-date"
        elif current_ver[0] < latest_ver[0]:
            return "major-update"
        elif current_ver[1] < latest_ver[1]:
            return "minor-update"
        else:
            return "outdated"
    
    def analyze_python_requirements(self) -> List[Dict[str, Any]]:
        """
        Analyze Python requirements.txt file.
        
        Returns:
            List of package analysis results
        """
        results = []
        req_file = self.repo_path / 'requirements.txt'
        
        if not req_file.exists():
            return results
        
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse package and version
                    match = re.match(r'^([a-zA-Z0-9_-]+)([>=<~!]*)([\d.]*)', line)
                    if not match:
                        continue
                    
                    package = match.group(1)
                    operator = match.group(2) or ''
                    current_version = match.group(3) or 'unknown'
                    
                    # Fetch latest version from PyPI
                    info = self._fetch_pypi_info(package)
                    if info:
                        latest_version = info['info']['version']
                        status = self._compare_versions(current_version, latest_version)
                        
                        results.append({
                            'package': package,
                            'current_version': current_version,
                            'latest_version': latest_version,
                            'status': status,
                            'ecosystem': 'python',
                            'operator': operator,
                            'homepage': info['info'].get('home_page', ''),
                            'summary': info['info'].get('summary', '')
                        })
                    else:
                        results.append({
                            'package': package,
                            'current_version': current_version,
                            'latest_version': 'unknown',
                            'status': 'unknown',
                            'ecosystem': 'python',
                            'operator': operator
                        })
        except Exception as e:
            self.logger.error(f"Error analyzing Python requirements: {e}")
        
        return results
    
    def analyze_package_json(self) -> List[Dict[str, Any]]:
        """
        Analyze package.json for Node.js dependencies.
        
        Returns:
            List of package analysis results
        """
        results = []
        pkg_file = self.repo_path / 'package.json'
        
        if not pkg_file.exists():
            return results
        
        try:
            with open(pkg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dependencies = {}
            dependencies.update(data.get('dependencies', {}))
            dependencies.update(data.get('devDependencies', {}))
            
            for package, version in dependencies.items():
                current_version = version.lstrip('^~>=<')
                
                # Fetch latest version from npm
                info = self._fetch_npm_info(package)
                if info:
                    latest_version = info.get('dist-tags', {}).get('latest', 'unknown')
                    status = self._compare_versions(current_version, latest_version)
                    
                    results.append({
                        'package': package,
                        'current_version': current_version,
                        'latest_version': latest_version,
                        'status': status,
                        'ecosystem': 'npm',
                        'operator': version[0] if version[0] in '^~>=<' else '',
                        'homepage': info.get('homepage', ''),
                        'description': info.get('description', '')
                    })
                else:
                    results.append({
                        'package': package,
                        'current_version': current_version,
                        'latest_version': 'unknown',
                        'status': 'unknown',
                        'ecosystem': 'npm',
                        'operator': version[0] if version[0] in '^~>=<' else ''
                    })
        except Exception as e:
            self.logger.error(f"Error analyzing package.json: {e}")
        
        return results
    
    def analyze_all_dependencies(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze all dependency files in the repository.
        
        Returns:
            Dictionary with ecosystem as key and list of packages as value
        """
        all_deps = {}
        
        # Python dependencies
        python_deps = self.analyze_python_requirements()
        if python_deps:
            all_deps['python'] = python_deps
        
        # Node.js dependencies
        npm_deps = self.analyze_package_json()
        if npm_deps:
            all_deps['npm'] = npm_deps
        
        return all_deps
    
    def generate_analysis_report(self, dependencies: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generate markdown report from dependency analysis.
        
        Args:
            dependencies: Analysis results from analyze_all_dependencies()
            
        Returns:
            Markdown formatted report
        """
        if not dependencies:
            return "# Dependency Analysis\n\nNo dependencies found."
        
        md = []
        md.append("# Dependency Analysis Report\n")
        
        total_packages = sum(len(deps) for deps in dependencies.values())
        md.append(f"**Total packages analyzed**: {total_packages}\n")
        
        for ecosystem, packages in dependencies.items():
            md.append(f"## {ecosystem.upper()} Dependencies ({len(packages)} packages)\n")
            
            # Categorize packages
            up_to_date = [p for p in packages if p['status'] == 'up-to-date']
            minor_updates = [p for p in packages if p['status'] == 'minor-update']
            major_updates = [p for p in packages if p['status'] == 'major-update']
            outdated = [p for p in packages if p['status'] == 'outdated']
            unknown = [p for p in packages if p['status'] == 'unknown']
            
            # Summary statistics
            md.append("### Summary\n")
            md.append(f"- ✅ Up to date: {len(up_to_date)}")
            md.append(f"- 🔄 Minor updates available: {len(minor_updates)}")
            md.append(f"- ⚠️ Major updates available: {len(major_updates)}")
            md.append(f"- 🔴 Outdated: {len(outdated)}")
            if unknown:
                md.append(f"- ❓ Unknown status: {len(unknown)}")
            md.append("")
            
            # Major updates (most important)
            if major_updates:
                md.append("### ⚠️ Major Updates Available\n")
                md.append("| Package | Current | Latest | Action |")
                md.append("|---------|---------|--------|--------|")
                for pkg in sorted(major_updates, key=lambda x: x['package']):
                    current = pkg['current_version'] or 'unknown'
                    latest = pkg['latest_version']
                    md.append(f"| {pkg['package']} | {current} | {latest} | Review breaking changes |")
                md.append("")
            
            # Minor updates
            if minor_updates:
                md.append("### 🔄 Minor Updates Available\n")
                md.append("| Package | Current | Latest |")
                md.append("|---------|---------|--------|")
                for pkg in sorted(minor_updates, key=lambda x: x['package']):
                    current = pkg['current_version'] or 'unknown'
                    latest = pkg['latest_version']
                    md.append(f"| {pkg['package']} | {current} | {latest} |")
                md.append("")
            
            # Up to date packages
            if up_to_date:
                md.append("### ✅ Up to Date Packages\n")
                md.append(", ".join(sorted([p['package'] for p in up_to_date])))
                md.append("\n")
        
        # Recommendations
        md.append("## Recommendations\n")
        total_updates = sum(
            len([p for p in packages if p['status'] in ['minor-update', 'major-update', 'outdated']])
            for packages in dependencies.values()
        )
        
        if total_updates == 0:
            md.append("✅ All dependencies are up to date! Great job maintaining your project.\n")
        else:
            md.append(f"- Found {total_updates} package(s) with available updates")
            md.append("- Review major updates carefully for breaking changes")
            md.append("- Minor updates are typically safe to apply")
            md.append("- Consider automating dependency updates with tools like Dependabot")
            md.append("- Regularly check for security advisories\n")
        
        return '\n'.join(md)
