"""
Data export module for AccuDoc.
Provides functionality to export repository analysis data to CSV and Excel formats.
"""

import csv
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class DataExporter:
    """Exports repository data to various formats (CSV, Excel)."""
    
    def __init__(self, repo_info: Dict):
        """
        Initialize the data exporter.
        
        Args:
            repo_info: Dictionary containing repository information from scanner
        """
        self.repo_info = repo_info
    
    def export_to_csv(self, output_dir: str, report_type: str = 'all') -> List[str]:
        """
        Export repository data to CSV files.
        
        Args:
            output_dir: Directory to save CSV files
            report_type: Type of report ('all', 'files', 'dependencies', 'todos', 'metrics')
            
        Returns:
            List of created file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        if report_type in ['all', 'files']:
            files_csv = self._export_files_csv(output_path)
            if files_csv:
                created_files.append(files_csv)
        
        if report_type in ['all', 'dependencies']:
            deps_csv = self._export_dependencies_csv(output_path)
            if deps_csv:
                created_files.append(deps_csv)
        
        if report_type in ['all', 'todos']:
            todos_csv = self._export_todos_csv(output_path)
            if todos_csv:
                created_files.append(todos_csv)
        
        if report_type in ['all', 'metrics']:
            metrics_csv = self._export_metrics_csv(output_path)
            if metrics_csv:
                created_files.append(metrics_csv)
        
        if report_type in ['all', 'languages']:
            langs_csv = self._export_languages_csv(output_path)
            if langs_csv:
                created_files.append(langs_csv)
        
        return created_files
    
    def _export_files_csv(self, output_path: Path) -> Optional[str]:
        """Export file statistics to CSV."""
        files_csv = output_path / 'files.csv'
        
        # Get file information
        files_data = []
        languages = self.repo_info.get('languages', {})
        
        # Create a row for each language's files
        for lang, count in languages.items():
            files_data.append({
                'Language': lang,
                'File Count': count,
            })
        
        if not files_data:
            return None
        
        with open(files_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Language', 'File Count'])
            writer.writeheader()
            writer.writerows(files_data)
        
        return str(files_csv)
    
    def _export_dependencies_csv(self, output_path: Path) -> Optional[str]:
        """Export dependencies to CSV."""
        deps_csv = output_path / 'dependencies.csv'
        
        dependencies = self.repo_info.get('dependencies', {})
        if not dependencies:
            return None
        
        deps_data = []
        for pkg_manager, deps_list in dependencies.items():
            if isinstance(deps_list, list):
                for dep in deps_list:
                    if isinstance(dep, dict):
                        deps_data.append({
                            'Package Manager': pkg_manager,
                            'Dependency': dep.get('name', ''),
                            'Version': dep.get('version', 'N/A'),
                        })
                    else:
                        deps_data.append({
                            'Package Manager': pkg_manager,
                            'Dependency': str(dep),
                            'Version': 'N/A',
                        })
        
        if not deps_data:
            return None
        
        with open(deps_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Package Manager', 'Dependency', 'Version'])
            writer.writeheader()
            writer.writerows(deps_data)
        
        return str(deps_csv)
    
    def _export_todos_csv(self, output_path: Path) -> Optional[str]:
        """Export TODO/FIXME comments to CSV."""
        todos_csv = output_path / 'todos.csv'
        
        todos = self.repo_info.get('todos', [])
        if not todos:
            return None
        
        todos_data = []
        for todo in todos:
            todos_data.append({
                'File': todo.get('file', ''),
                'Line': todo.get('line', ''),
                'Type': todo.get('type', 'TODO'),
                'Comment': todo.get('comment', ''),
            })
        
        with open(todos_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['File', 'Line', 'Type', 'Comment'])
            writer.writeheader()
            writer.writerows(todos_data)
        
        return str(todos_csv)
    
    def _export_metrics_csv(self, output_path: Path) -> Optional[str]:
        """Export code metrics to CSV."""
        metrics_csv = output_path / 'metrics.csv'
        
        stats = self.repo_info.get('statistics', {})
        if not stats:
            return None
        
        metrics_data = [
            {'Metric': 'Total Files', 'Value': self.repo_info.get('files_count', 0)},
            {'Metric': 'Total Lines of Code', 'Value': stats.get('total_lines', 0)},
            {'Metric': 'Code Lines', 'Value': stats.get('code_lines', 0)},
            {'Metric': 'Comment Lines', 'Value': stats.get('comment_lines', 0)},
            {'Metric': 'Blank Lines', 'Value': stats.get('blank_lines', 0)},
        ]
        
        # Add language-specific metrics
        lang_stats = stats.get('by_language', {})
        for lang, lang_data in lang_stats.items():
            metrics_data.append({
                'Metric': f'{lang} - Lines',
                'Value': lang_data.get('lines', 0)
            })
        
        with open(metrics_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Metric', 'Value'])
            writer.writeheader()
            writer.writerows(metrics_data)
        
        return str(metrics_csv)
    
    def _export_languages_csv(self, output_path: Path) -> Optional[str]:
        """Export language breakdown to CSV."""
        langs_csv = output_path / 'languages.csv'
        
        languages = self.repo_info.get('languages', {})
        stats = self.repo_info.get('statistics', {})
        lang_stats = stats.get('by_language', {})
        
        if not languages:
            return None
        
        langs_data = []
        total_files = sum(languages.values())
        
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            lines = lang_stats.get(lang, {}).get('lines', 0)
            
            langs_data.append({
                'Language': lang,
                'File Count': count,
                'Percentage': f'{percentage:.2f}%',
                'Lines of Code': lines,
            })
        
        with open(langs_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Language', 'File Count', 'Percentage', 'Lines of Code'])
            writer.writeheader()
            writer.writerows(langs_data)
        
        return str(langs_csv)
    
    def export_summary_csv(self, output_path: str) -> str:
        """
        Export a single summary CSV with key metrics.
        
        Args:
            output_path: Path to output CSV file
            
        Returns:
            Path to created file
        """
        summary_data = [
            {'Category': 'General', 'Metric': 'Repository Name', 'Value': self.repo_info.get('name', 'Unknown')},
            {'Category': 'General', 'Metric': 'Repository Path', 'Value': self.repo_info.get('path', 'Unknown')},
            {'Category': 'General', 'Metric': 'Scan Date', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'Category': 'Files', 'Metric': 'Total Files', 'Value': self.repo_info.get('files_count', 0)},
            {'Category': 'Files', 'Metric': 'Programming Languages', 'Value': len(self.repo_info.get('languages', {}))},
        ]
        
        # Add statistics
        stats = self.repo_info.get('statistics', {})
        if stats:
            summary_data.extend([
                {'Category': 'Code Metrics', 'Metric': 'Total Lines', 'Value': stats.get('total_lines', 0)},
                {'Category': 'Code Metrics', 'Metric': 'Code Lines', 'Value': stats.get('code_lines', 0)},
                {'Category': 'Code Metrics', 'Metric': 'Comment Lines', 'Value': stats.get('comment_lines', 0)},
                {'Category': 'Code Metrics', 'Metric': 'Blank Lines', 'Value': stats.get('blank_lines', 0)},
            ])
        
        # Add dependency count
        dependencies = self.repo_info.get('dependencies', {})
        dep_count = sum(len(deps) if isinstance(deps, list) else 0 for deps in dependencies.values())
        summary_data.append({'Category': 'Dependencies', 'Metric': 'Total Dependencies', 'Value': dep_count})
        
        # Add TODO count
        todos = self.repo_info.get('todos', [])
        summary_data.append({'Category': 'Tasks', 'Metric': 'TODO/FIXME Count', 'Value': len(todos)})
        
        # Add license
        license_info = self.repo_info.get('license', 'Not found')
        summary_data.append({'Category': 'Legal', 'Metric': 'License', 'Value': license_info})
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Category', 'Metric', 'Value'])
            writer.writeheader()
            writer.writerows(summary_data)
        
        return output_path
    
    def export_to_json(self, output_path: str, pretty: bool = True) -> str:
        """
        Export repository data to JSON.
        
        Args:
            output_path: Path to output JSON file
            pretty: Whether to format JSON with indentation
            
        Returns:
            Path to created file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(self.repo_info, f, indent=2, ensure_ascii=False)
            else:
                json.dump(self.repo_info, f, ensure_ascii=False)
        
        return output_path


def export_data(repo_info: Dict, output_path: str, format: str = 'csv', 
                report_type: str = 'all') -> List[str]:
    """
    Export repository data to specified format.
    
    Args:
        repo_info: Repository information dictionary
        output_path: Output path (file or directory depending on format)
        format: Export format ('csv', 'json', 'summary')
        report_type: Type of report for CSV export
        
    Returns:
        List of created file paths
    """
    exporter = DataExporter(repo_info)
    
    if format == 'csv':
        return exporter.export_to_csv(output_path, report_type=report_type)
    elif format == 'summary':
        return [exporter.export_summary_csv(output_path)]
    elif format == 'json':
        return [exporter.export_to_json(output_path)]
    else:
        raise ValueError(f"Unsupported export format: {format}")
