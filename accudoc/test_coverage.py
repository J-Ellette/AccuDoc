"""
Test coverage analyzer module for AccuDoc.

Extracts and displays test coverage information from various coverage tools:
- Python: coverage.py, pytest-cov
- JavaScript: Istanbul/NYC, Jest
- Java: JaCoCo
- Go: go test -cover

Parses coverage reports and generates documentation.
"""

import json
import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import re


class TestCoverageAnalyzer:
    """Analyzes test coverage from various formats."""
    
    def __init__(self, repo_path: str):
        """
        Initialize coverage analyzer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.coverage')
        
    def detect_coverage_files(self) -> Dict[str, List[Path]]:
        """
        Detect coverage report files in the repository.
        
        Returns:
            Dictionary mapping coverage tool to list of report files
        """
        coverage_files = {
            'python': [],
            'javascript': [],
            'java': [],
            'go': [],
            'generic': []
        }
        
        # Python coverage files
        for pattern in ['.coverage', 'coverage.xml', 'htmlcov/index.html', '.coverage.*']:
            coverage_files['python'].extend(self.repo_path.glob(pattern))
        
        # JavaScript coverage files
        for pattern in ['coverage/coverage-final.json', 'coverage/lcov.info', 'coverage/clover.xml']:
            coverage_files['javascript'].extend(self.repo_path.glob(pattern))
        
        # Java coverage files (JaCoCo)
        for pattern in ['target/site/jacoco/jacoco.xml', 'build/reports/jacoco/test/jacocoTestReport.xml']:
            coverage_files['java'].extend(self.repo_path.glob(pattern))
        
        # Go coverage files
        for pattern in ['coverage.out', 'coverage.txt']:
            coverage_files['go'].extend(self.repo_path.glob(pattern))
        
        # Generic XML coverage (Cobertura format)
        coverage_files['generic'].extend(self.repo_path.glob('**/coverage.xml'))
        
        return {k: v for k, v in coverage_files.items() if v}
    
    def parse_python_coverage_xml(self, xml_path: Path) -> Dict[str, Any]:
        """
        Parse Python coverage.xml file.
        
        Args:
            xml_path: Path to coverage.xml
            
        Returns:
            Coverage data dictionary
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            coverage = {
                'tool': 'python-coverage',
                'overall': {},
                'packages': [],
                'files': []
            }
            
            # Overall coverage
            if root.tag == 'coverage':
                coverage['overall'] = {
                    'line_rate': float(root.get('line-rate', 0)) * 100,
                    'branch_rate': float(root.get('branch-rate', 0)) * 100,
                    'lines_covered': int(root.get('lines-covered', 0)),
                    'lines_valid': int(root.get('lines-valid', 0)),
                }
            
            # Package/File level coverage
            for package in root.findall('.//package'):
                pkg_name = package.get('name', 'unknown')
                pkg_line_rate = float(package.get('line-rate', 0)) * 100
                
                coverage['packages'].append({
                    'name': pkg_name,
                    'coverage': pkg_line_rate
                })
                
                for cls in package.findall('.//class'):
                    filename = cls.get('filename', 'unknown')
                    file_line_rate = float(cls.get('line-rate', 0)) * 100
                    
                    coverage['files'].append({
                        'name': filename,
                        'coverage': file_line_rate
                    })
            
            return coverage
            
        except Exception as e:
            self.logger.error(f"Error parsing Python coverage XML: {e}")
            return None
    
    def parse_javascript_coverage_json(self, json_path: Path) -> Dict[str, Any]:
        """
        Parse JavaScript coverage-final.json file (Istanbul/NYC format).
        
        Args:
            json_path: Path to coverage-final.json
            
        Returns:
            Coverage data dictionary
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            coverage = {
                'tool': 'javascript-coverage',
                'overall': {
                    'lines': 0,
                    'statements': 0,
                    'functions': 0,
                    'branches': 0
                },
                'files': []
            }
            
            total_metrics = {'lines': [0, 0], 'statements': [0, 0], 'functions': [0, 0], 'branches': [0, 0]}
            
            for filepath, file_data in data.items():
                # Calculate coverage for each metric
                metrics = {}
                
                # Lines
                lines = file_data.get('l', {})
                if lines:
                    covered = sum(1 for v in lines.values() if v > 0)
                    total = len(lines)
                    metrics['lines'] = (covered / total * 100) if total > 0 else 0
                    total_metrics['lines'][0] += covered
                    total_metrics['lines'][1] += total
                
                # Statements
                statements = file_data.get('s', {})
                if statements:
                    covered = sum(1 for v in statements.values() if v > 0)
                    total = len(statements)
                    metrics['statements'] = (covered / total * 100) if total > 0 else 0
                    total_metrics['statements'][0] += covered
                    total_metrics['statements'][1] += total
                
                # Functions
                functions = file_data.get('f', {})
                if functions:
                    covered = sum(1 for v in functions.values() if v > 0)
                    total = len(functions)
                    metrics['functions'] = (covered / total * 100) if total > 0 else 0
                    total_metrics['functions'][0] += covered
                    total_metrics['functions'][1] += total
                
                # Branches
                branches = file_data.get('b', {})
                if branches:
                    covered = sum(sum(1 for v in branch if v > 0) for branch in branches.values())
                    total = sum(len(branch) for branch in branches.values())
                    metrics['branches'] = (covered / total * 100) if total > 0 else 0
                    total_metrics['branches'][0] += covered
                    total_metrics['branches'][1] += total
                
                coverage['files'].append({
                    'name': filepath,
                    'metrics': metrics
                })
            
            # Calculate overall coverage
            for metric, (covered, total) in total_metrics.items():
                coverage['overall'][metric] = (covered / total * 100) if total > 0 else 0
            
            return coverage
            
        except Exception as e:
            self.logger.error(f"Error parsing JavaScript coverage JSON: {e}")
            return None
    
    def parse_go_coverage(self, coverage_path: Path) -> Dict[str, Any]:
        """
        Parse Go coverage file (coverage.out format).
        
        Args:
            coverage_path: Path to coverage.out
            
        Returns:
            Coverage data dictionary
        """
        try:
            coverage = {
                'tool': 'go-coverage',
                'overall': {'coverage': 0},
                'files': []
            }
            
            file_coverage = {}
            
            with open(coverage_path, 'r') as f:
                lines = f.readlines()
                
                # Skip mode line
                if lines and lines[0].startswith('mode:'):
                    lines = lines[1:]
                
                for line in lines:
                    if not line.strip():
                        continue
                    
                    # Format: filename:startline.startcol,endline.endcol statements count
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    
                    location = parts[0]
                    statements = int(parts[1])
                    count = int(parts[2])
                    
                    filename = location.split(':')[0]
                    
                    if filename not in file_coverage:
                        file_coverage[filename] = {'covered': 0, 'total': 0}
                    
                    file_coverage[filename]['total'] += statements
                    if count > 0:
                        file_coverage[filename]['covered'] += statements
            
            # Calculate per-file and overall coverage
            total_covered = 0
            total_statements = 0
            
            for filename, data in file_coverage.items():
                file_pct = (data['covered'] / data['total'] * 100) if data['total'] > 0 else 0
                coverage['files'].append({
                    'name': filename,
                    'coverage': file_pct
                })
                total_covered += data['covered']
                total_statements += data['total']
            
            coverage['overall']['coverage'] = (total_covered / total_statements * 100) if total_statements > 0 else 0
            
            return coverage
            
        except Exception as e:
            self.logger.error(f"Error parsing Go coverage: {e}")
            return None
    
    def analyze_coverage(self) -> Dict[str, Any]:
        """
        Analyze test coverage for the repository.
        
        Returns:
            Comprehensive coverage analysis
        """
        coverage_files = self.detect_coverage_files()
        
        if not coverage_files:
            return {'status': 'no_coverage', 'message': 'No coverage files found'}
        
        results = {
            'status': 'success',
            'coverage_data': []
        }
        
        # Parse Python coverage
        if 'python' in coverage_files:
            for file in coverage_files['python']:
                if file.name == 'coverage.xml':
                    data = self.parse_python_coverage_xml(file)
                    if data:
                        results['coverage_data'].append(data)
        
        # Parse JavaScript coverage
        if 'javascript' in coverage_files:
            for file in coverage_files['javascript']:
                if file.name == 'coverage-final.json':
                    data = self.parse_javascript_coverage_json(file)
                    if data:
                        results['coverage_data'].append(data)
        
        # Parse Go coverage
        if 'go' in coverage_files:
            for file in coverage_files['go']:
                data = self.parse_go_coverage(file)
                if data:
                    results['coverage_data'].append(data)
        
        return results
    
    def generate_coverage_report(self, coverage_data: Dict[str, Any]) -> str:
        """
        Generate markdown report from coverage analysis.
        
        Args:
            coverage_data: Coverage data from analyze_coverage()
            
        Returns:
            Markdown formatted report
        """
        if coverage_data.get('status') == 'no_coverage':
            return "# Test Coverage Report\n\nNo coverage data found."
        
        md = []
        md.append("# Test Coverage Report\n")
        
        for data in coverage_data.get('coverage_data', []):
            tool = data.get('tool', 'unknown')
            md.append(f"## {tool.replace('-', ' ').title()}\n")
            
            # Overall coverage
            overall = data.get('overall', {})
            if 'line_rate' in overall:
                # Python coverage format
                md.append("### Overall Coverage\n")
                md.append(f"- **Line Coverage**: {overall['line_rate']:.1f}%")
                md.append(f"- **Branch Coverage**: {overall['branch_rate']:.1f}%")
                md.append(f"- **Lines Covered**: {overall['lines_covered']} / {overall['lines_valid']}\n")
                
                # Coverage badge
                line_rate = overall['line_rate']
                badge_color = 'brightgreen' if line_rate >= 80 else 'yellow' if line_rate >= 60 else 'red'
                md.append(f"![Coverage](https://img.shields.io/badge/coverage-{line_rate:.0f}%25-{badge_color})\n")
                
            elif 'lines' in overall:
                # JavaScript coverage format
                md.append("### Overall Coverage\n")
                md.append(f"- **Lines**: {overall['lines']:.1f}%")
                md.append(f"- **Statements**: {overall['statements']:.1f}%")
                md.append(f"- **Functions**: {overall['functions']:.1f}%")
                md.append(f"- **Branches**: {overall['branches']:.1f}%\n")
                
            elif 'coverage' in overall:
                # Go coverage format
                md.append("### Overall Coverage\n")
                md.append(f"- **Coverage**: {overall['coverage']:.1f}%\n")
            
            # File-level coverage (top 10 lowest coverage files)
            files = data.get('files', [])
            if files:
                # Sort by coverage (ascending)
                sorted_files = sorted(files, key=lambda x: x.get('coverage', x.get('metrics', {}).get('lines', 0)))
                
                if len(sorted_files) > 0:
                    md.append("### Files Needing Attention (Lowest Coverage)\n")
                    md.append("| File | Coverage |")
                    md.append("|------|----------|")
                    
                    for file_data in sorted_files[:10]:
                        filename = file_data['name']
                        # Shorten path if too long
                        if len(filename) > 50:
                            filename = "..." + filename[-47:]
                        
                        if 'coverage' in file_data:
                            coverage = file_data['coverage']
                            icon = "✓" if coverage >= 80 else "⚠️" if coverage >= 60 else "❌"
                            md.append(f"| {icon} {filename} | {coverage:.1f}% |")
                        elif 'metrics' in file_data:
                            lines = file_data['metrics'].get('lines', 0)
                            icon = "✓" if lines >= 80 else "⚠️" if lines >= 60 else "❌"
                            md.append(f"| {icon} {filename} | {lines:.1f}% |")
                    
                    md.append("")
        
        md.append("## Recommendations\n")
        md.append("- Aim for at least 80% code coverage")
        md.append("- Focus on testing files with low coverage")
        md.append("- Ensure critical business logic is well tested")
        md.append("- Consider adding integration and end-to-end tests\n")
        
        return '\n'.join(md)
