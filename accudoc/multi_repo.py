"""
Multi-repository support module for AccuDoc.

Provides functionality to scan and document multiple related repositories
as a unified documentation set. Useful for microservices, monorepos with
separate repositories, and related project ecosystems.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator


class MultiRepositoryManager:
    """Manages scanning and documentation of multiple repositories."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize multi-repository manager.
        
        Args:
            max_workers: Maximum number of concurrent repository scans
        """
        self.max_workers = max_workers
        self.logger = logging.getLogger('accudoc.multi_repo')
        
    def scan_repositories(self, 
                         repositories: List[Dict[str, Any]], 
                         progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Scan multiple repositories in parallel.
        
        Args:
            repositories: List of repository configurations, each with:
                - path: Repository path or URL
                - name: Optional display name
                - group: Optional group/category
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with scan results for each repository
        """
        results = {
            'repositories': {},
            'summary': {
                'total': len(repositories),
                'successful': 0,
                'failed': 0
            }
        }
        
        self.logger.info(f"Scanning {len(repositories)} repositories")
        
        # Scan repositories in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_repo = {
                executor.submit(self._scan_single_repository, repo): repo
                for repo in repositories
            }
            
            for future in as_completed(future_to_repo):
                repo_config = future_to_repo[future]
                repo_path = repo_config.get('path', 'unknown')
                repo_name = repo_config.get('name', Path(repo_path).name)
                
                try:
                    scan_result = future.result()
                    results['repositories'][repo_name] = {
                        'config': repo_config,
                        'scan': scan_result,
                        'status': 'success'
                    }
                    results['summary']['successful'] += 1
                    
                    if progress_callback:
                        progress_callback(f"✓ Scanned: {repo_name}")
                        
                except Exception as e:
                    self.logger.error(f"Failed to scan {repo_name}: {e}")
                    results['repositories'][repo_name] = {
                        'config': repo_config,
                        'error': str(e),
                        'status': 'failed'
                    }
                    results['summary']['failed'] += 1
                    
                    if progress_callback:
                        progress_callback(f"✗ Failed: {repo_name} - {e}")
        
        return results
    
    def _scan_single_repository(self, repo_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan a single repository.
        
        Args:
            repo_config: Repository configuration
            
        Returns:
            Scan results
        """
        repo_path = repo_config['path']
        scanner = RepositoryScanner(repo_path)
        return scanner.scan()
    
    def generate_unified_documentation(self, 
                                      scan_results: Dict[str, Any],
                                      title: str = "Multi-Repository Documentation") -> str:
        """
        Generate unified documentation for multiple repositories.
        
        Args:
            scan_results: Results from scan_repositories()
            title: Documentation title
            
        Returns:
            Unified markdown documentation
        """
        md = []
        md.append(f"# {title}\n")
        
        summary = scan_results['summary']
        md.append("## Overview\n")
        md.append(f"This documentation covers {summary['total']} related repositories.\n")
        md.append(f"- **Successfully scanned**: {summary['successful']}")
        md.append(f"- **Failed**: {summary['failed']}\n")
        
        # Group repositories by group if specified
        grouped = {}
        ungrouped = []
        
        for repo_name, repo_data in scan_results['repositories'].items():
            if repo_data['status'] != 'success':
                continue
                
            group = repo_data['config'].get('group', None)
            if group:
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append((repo_name, repo_data))
            else:
                ungrouped.append((repo_name, repo_data))
        
        # Generate documentation for grouped repositories
        for group_name in sorted(grouped.keys()):
            md.append(f"## {group_name}\n")
            
            for repo_name, repo_data in grouped[group_name]:
                md.extend(self._generate_repository_section(repo_name, repo_data))
        
        # Generate documentation for ungrouped repositories
        if ungrouped:
            md.append("## Repositories\n")
            for repo_name, repo_data in ungrouped:
                md.extend(self._generate_repository_section(repo_name, repo_data))
        
        # Summary table
        md.append("## Repository Summary\n")
        md.append("| Repository | Languages | Files | Dependencies |")
        md.append("|------------|-----------|-------|--------------|")
        
        for repo_name, repo_data in scan_results['repositories'].items():
            if repo_data['status'] == 'success':
                scan = repo_data['scan']
                languages = ', '.join(list(scan.get('languages', {}).keys())[:3])
                files = len(scan.get('files', []))
                deps = len(scan.get('dependencies', {}))
                md.append(f"| {repo_name} | {languages} | {files} | {deps} |")
        
        md.append("")
        
        return '\n'.join(md)
    
    def _generate_repository_section(self, repo_name: str, repo_data: Dict[str, Any]) -> List[str]:
        """
        Generate documentation section for a single repository.
        
        Args:
            repo_name: Repository name
            repo_data: Repository scan data
            
        Returns:
            List of markdown lines
        """
        md = []
        scan = repo_data['scan']
        config = repo_data['config']
        
        md.append(f"### {repo_name}\n")
        
        # Description if provided
        if 'description' in config:
            md.append(f"{config['description']}\n")
        
        # Basic info
        md.append(f"**Path**: `{config['path']}`\n")
        
        # Languages
        languages = scan.get('languages', {})
        if languages:
            lang_list = [f"{lang} ({count} files)" for lang, count in list(languages.items())[:5]]
            md.append(f"**Languages**: {', '.join(lang_list)}\n")
        
        # Dependencies
        dependencies = scan.get('dependencies', {})
        if dependencies:
            md.append(f"**Dependencies**: {len(dependencies)}")
            dep_list = []
            for dep_type, deps in dependencies.items():
                if deps:
                    dep_list.append(f"{dep_type.upper()}")
            if dep_list:
                md.append(f" ({', '.join(dep_list)})")
            md.append("\n")
        
        # Key files
        files = scan.get('files', [])
        if files:
            md.append(f"**Total Files**: {len(files)}\n")
        
        return md
    
    def generate_comparison_matrix(self, scan_results: Dict[str, Any]) -> str:
        """
        Generate a comparison matrix showing features across repositories.
        
        Args:
            scan_results: Results from scan_repositories()
            
        Returns:
            Markdown formatted comparison matrix
        """
        md = []
        md.append("# Repository Comparison Matrix\n")
        
        # Collect all unique languages
        all_languages = set()
        all_dep_types = set()
        
        for repo_name, repo_data in scan_results['repositories'].items():
            if repo_data['status'] == 'success':
                scan = repo_data['scan']
                all_languages.update(scan.get('languages', {}).keys())
                all_dep_types.update(scan.get('dependencies', {}).keys())
        
        # Language comparison
        if all_languages:
            md.append("## Programming Languages\n")
            md.append("| Repository | " + " | ".join(sorted(all_languages)) + " |")
            md.append("|------------|" + "|".join(["---" for _ in all_languages]) + "|")
            
            for repo_name, repo_data in scan_results['repositories'].items():
                if repo_data['status'] == 'success':
                    scan = repo_data['scan']
                    languages = scan.get('languages', {})
                    row = [repo_name]
                    for lang in sorted(all_languages):
                        count = languages.get(lang, 0)
                        row.append("✓" if count > 0 else "")
                    md.append("| " + " | ".join(row) + " |")
            md.append("")
        
        # Dependency comparison
        if all_dep_types:
            md.append("## Dependency Managers\n")
            md.append("| Repository | " + " | ".join(sorted(all_dep_types)) + " |")
            md.append("|------------|" + "|".join(["---" for _ in all_dep_types]) + "|")
            
            for repo_name, repo_data in scan_results['repositories'].items():
                if repo_data['status'] == 'success':
                    scan = repo_data['scan']
                    dependencies = scan.get('dependencies', {})
                    row = [repo_name]
                    for dep_type in sorted(all_dep_types):
                        has_deps = dep_type in dependencies and len(dependencies[dep_type]) > 0
                        row.append("✓" if has_deps else "")
                    md.append("| " + " | ".join(row) + " |")
            md.append("")
        
        # Statistics comparison
        md.append("## Statistics\n")
        md.append("| Repository | Files | Total Lines | Languages |")
        md.append("|------------|-------|-------------|-----------|")
        
        for repo_name, repo_data in scan_results['repositories'].items():
            if repo_data['status'] == 'success':
                scan = repo_data['scan']
                files = len(scan.get('files', []))
                languages = len(scan.get('languages', {}))
                # Approximate lines (would need to count actual lines in full implementation)
                lines = "N/A"
                md.append(f"| {repo_name} | {files} | {lines} | {languages} |")
        
        md.append("")
        
        return '\n'.join(md)
    
    def export_results(self, scan_results: Dict[str, Any], output_path: str, format: str = 'json'):
        """
        Export multi-repository scan results.
        
        Args:
            scan_results: Results from scan_repositories()
            output_path: Output file path
            format: Export format ('json', 'markdown')
        """
        output_file = Path(output_path)
        
        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump(scan_results, f, indent=2, default=str)
        elif format == 'markdown':
            doc = self.generate_unified_documentation(scan_results)
            with open(output_file, 'w') as f:
                f.write(doc)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Results exported to: {output_file}")
