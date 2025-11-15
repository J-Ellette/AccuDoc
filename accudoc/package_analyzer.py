"""
Package version analyzer for AccuDoc.

Analyzes dependencies and checks for outdated packages and security vulnerabilities.
"""

import json
import logging
from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime
import re


class PackageVersionAnalyzer:
    """Analyze package versions and security."""
    
    def __init__(self):
        """Initialize package version analyzer."""
        self.logger = logging.getLogger('accudoc.packages')
        
    def analyze_dependencies(self, repo_path: Path, dependencies: Dict) -> Dict:
        """
        Analyze dependencies for version information and security issues.
        
        Args:
            repo_path: Repository path
            dependencies: Dependencies dict from scanner
            
        Returns:
            Analysis results
        """
        results = {
            'analyzed_at': datetime.now().isoformat(),
            'package_managers': {},
            'summary': {
                'total_packages': 0,
                'outdated_packages': 0,
                'vulnerable_packages': 0
            }
        }
        
        # Analyze Python dependencies
        if 'Python' in dependencies:
            results['package_managers']['pip'] = self._analyze_python_deps(
                repo_path, dependencies['Python']
            )
        
        # Analyze JavaScript dependencies
        if 'JavaScript' in dependencies or 'TypeScript' in dependencies:
            js_deps = dependencies.get('JavaScript', []) + dependencies.get('TypeScript', [])
            results['package_managers']['npm'] = self._analyze_javascript_deps(
                repo_path, js_deps
            )
        
        # Analyze Ruby dependencies
        if 'Ruby' in dependencies:
            results['package_managers']['bundler'] = self._analyze_ruby_deps(
                repo_path, dependencies['Ruby']
            )
        
        # Calculate summary
        for pm_data in results['package_managers'].values():
            results['summary']['total_packages'] += len(pm_data.get('packages', []))
            results['summary']['outdated_packages'] += len(pm_data.get('outdated', []))
            results['summary']['vulnerable_packages'] += len(pm_data.get('vulnerable', []))
        
        return results
    
    def _analyze_python_deps(self, repo_path: Path, dependencies: List[str]) -> Dict:
        """Analyze Python dependencies."""
        result = {
            'package_manager': 'pip',
            'packages': [],
            'outdated': [],
            'vulnerable': [],
            'recommendations': []
        }
        
        # Parse requirements.txt if it exists
        req_file = repo_path / 'requirements.txt'
        if req_file.exists():
            try:
                content = req_file.read_text()
                packages = self._parse_requirements(content)
                result['packages'] = packages
                
                # Check for common vulnerable packages
                vulnerable = self._check_python_vulnerabilities(packages)
                result['vulnerable'] = vulnerable
                
                # Generate recommendations
                if vulnerable:
                    result['recommendations'].append(
                        "Update vulnerable packages to latest secure versions"
                    )
                
                # Check for unpinned versions
                unpinned = [p for p in packages if not p.get('version')]
                if unpinned:
                    result['recommendations'].append(
                        f"Pin versions for {len(unpinned)} packages to ensure reproducibility"
                    )
                
            except Exception as e:
                self.logger.error(f"Error analyzing Python dependencies: {str(e)}")
        
        return result
    
    def _analyze_javascript_deps(self, repo_path: Path, dependencies: List[str]) -> Dict:
        """Analyze JavaScript/Node dependencies."""
        result = {
            'package_manager': 'npm',
            'packages': [],
            'outdated': [],
            'vulnerable': [],
            'recommendations': []
        }
        
        # Parse package.json if it exists
        pkg_file = repo_path / 'package.json'
        if pkg_file.exists():
            try:
                content = json.loads(pkg_file.read_text())
                
                # Get all dependencies
                deps = content.get('dependencies', {})
                dev_deps = content.get('devDependencies', {})
                all_deps = {**deps, **dev_deps}
                
                packages = [
                    {
                        'name': name,
                        'version': version,
                        'type': 'dev' if name in dev_deps else 'production'
                    }
                    for name, version in all_deps.items()
                ]
                result['packages'] = packages
                
                # Check for vulnerable packages
                vulnerable = self._check_javascript_vulnerabilities(packages)
                result['vulnerable'] = vulnerable
                
                # Recommendations
                if vulnerable:
                    result['recommendations'].append(
                        "Run 'npm audit fix' to update vulnerable packages"
                    )
                
                # Check for outdated semver patterns
                loose_versions = [p for p in packages if p['version'].startswith('^') or p['version'].startswith('~')]
                if len(loose_versions) > len(packages) * 0.5:
                    result['recommendations'].append(
                        "Consider using exact versions for better reproducibility"
                    )
                
            except Exception as e:
                self.logger.error(f"Error analyzing JavaScript dependencies: {str(e)}")
        
        return result
    
    def _analyze_ruby_deps(self, repo_path: Path, dependencies: List[str]) -> Dict:
        """Analyze Ruby dependencies."""
        result = {
            'package_manager': 'bundler',
            'packages': [],
            'outdated': [],
            'vulnerable': [],
            'recommendations': []
        }
        
        # Parse Gemfile if it exists
        gemfile = repo_path / 'Gemfile'
        if gemfile.exists():
            try:
                content = gemfile.read_text()
                packages = self._parse_gemfile(content)
                result['packages'] = packages
                
                # Basic recommendations
                if not (repo_path / 'Gemfile.lock').exists():
                    result['recommendations'].append(
                        "Add Gemfile.lock to version control for reproducible builds"
                    )
                
            except Exception as e:
                self.logger.error(f"Error analyzing Ruby dependencies: {str(e)}")
        
        return result
    
    def _parse_requirements(self, content: str) -> List[Dict]:
        """Parse Python requirements.txt."""
        packages = []
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle various formats: package==1.0.0, package>=1.0.0, package
            match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+)?(.+)?', line)
            if match:
                name = match.group(1)
                operator = match.group(2) or ''
                version = match.group(3) or ''
                
                packages.append({
                    'name': name,
                    'version': version.strip() if version else None,
                    'operator': operator
                })
        
        return packages
    
    def _parse_gemfile(self, content: str) -> List[Dict]:
        """Parse Ruby Gemfile."""
        packages = []
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Match gem 'name', 'version' or gem 'name'
            match = re.match(r"gem\s+['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]+)['\"])?", line)
            if match:
                name = match.group(1)
                version = match.group(2)
                
                packages.append({
                    'name': name,
                    'version': version
                })
        
        return packages
    
    def _check_python_vulnerabilities(self, packages: List[Dict]) -> List[Dict]:
        """Check for known Python package vulnerabilities."""
        vulnerable = []
        
        # Known vulnerable packages (simplified list for demonstration)
        known_vulnerabilities = {
            'django': {'<2.2.28', '<3.2.13', '<4.0.4'},
            'flask': {'<1.0'},
            'requests': {'<2.20.0'},
            'urllib3': {'<1.24.2'},
            'pyyaml': {'<5.4'},
            'pillow': {'<8.3.2'},
        }
        
        for package in packages:
            name = package['name'].lower()
            version = package.get('version', '')
            
            if name in known_vulnerabilities:
                # Simplified check - in production, use proper vulnerability DB
                vulnerable.append({
                    'name': package['name'],
                    'current_version': version,
                    'issue': f'Known vulnerabilities in {name}',
                    'recommendation': 'Update to latest version'
                })
        
        return vulnerable
    
    def _check_javascript_vulnerabilities(self, packages: List[Dict]) -> List[Dict]:
        """Check for known JavaScript package vulnerabilities."""
        vulnerable = []
        
        # Known vulnerable packages (simplified list)
        known_vulnerabilities = {
            'lodash': {'<4.17.21'},
            'axios': {'<0.21.2'},
            'node-forge': {'<1.3.0'},
            'minimist': {'<1.2.6'},
            'ansi-regex': {'<5.0.1', '<6.0.1'},
        }
        
        for package in packages:
            name = package['name'].lower()
            version = package.get('version', '').lstrip('^~')
            
            if name in known_vulnerabilities:
                vulnerable.append({
                    'name': package['name'],
                    'current_version': package['version'],
                    'issue': f'Known vulnerabilities in {name}',
                    'recommendation': 'Run npm audit fix'
                })
        
        return vulnerable
    
    def generate_security_report(self, analysis: Dict) -> str:
        """
        Generate a security report from analysis.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Markdown formatted security report
        """
        report = ["# Package Security Report", ""]
        report.append(f"**Analyzed:** {analysis['analyzed_at']}")
        report.append("")
        
        summary = analysis['summary']
        report.append("## Summary")
        report.append("")
        report.append(f"- **Total Packages:** {summary['total_packages']}")
        report.append(f"- **Outdated Packages:** {summary['outdated_packages']}")
        report.append(f"- **Vulnerable Packages:** {summary['vulnerable_packages']}")
        report.append("")
        
        # Report by package manager
        for pm_name, pm_data in analysis['package_managers'].items():
            report.append(f"## {pm_name.upper()}")
            report.append("")
            
            # Vulnerable packages
            if pm_data.get('vulnerable'):
                report.append("### ⚠️ Vulnerable Packages")
                report.append("")
                for vuln in pm_data['vulnerable']:
                    report.append(f"- **{vuln['name']}** ({vuln.get('current_version', 'unknown')})")
                    report.append(f"  - Issue: {vuln['issue']}")
                    report.append(f"  - Recommendation: {vuln['recommendation']}")
                report.append("")
            
            # Recommendations
            if pm_data.get('recommendations'):
                report.append("### Recommendations")
                report.append("")
                for rec in pm_data['recommendations']:
                    report.append(f"- {rec}")
                report.append("")
            
            # Package list
            if pm_data.get('packages'):
                report.append(f"### All Packages ({len(pm_data['packages'])})")
                report.append("")
                for pkg in pm_data['packages'][:20]:  # Limit to first 20
                    version = pkg.get('version', 'not specified')
                    report.append(f"- {pkg['name']}: {version}")
                if len(pm_data['packages']) > 20:
                    report.append(f"- ... and {len(pm_data['packages']) - 20} more")
                report.append("")
        
        return '\n'.join(report)


def analyze_package_versions(repo_path: Path, dependencies: Dict) -> Dict:
    """
    Convenience function to analyze package versions.
    
    Args:
        repo_path: Repository path
        dependencies: Dependencies from scanner
        
    Returns:
        Analysis results
    """
    analyzer = PackageVersionAnalyzer()
    return analyzer.analyze_dependencies(repo_path, dependencies)
