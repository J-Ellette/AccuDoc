"""
Best Practices Checker Module for AccuDoc.

This module checks code against common best practices and coding standards.
It identifies violations and provides recommendations for improvement.
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional


class BestPracticesChecker:
    """Checker for coding best practices and standards."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the best practices checker.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.results = []
    
    def check_python_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Check a Python file for best practices violations.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary containing violations and recommendations
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            tree = ast.parse(content)
            
            violations = []
            
            # Check for missing module docstring
            module_docstring = ast.get_docstring(tree)
            if not module_docstring:
                violations.append({
                    'type': 'missing_module_docstring',
                    'severity': 'medium',
                    'line': 1,
                    'message': 'Module is missing a docstring',
                    'recommendation': 'Add a module-level docstring describing the purpose of this file'
                })
            
            # Check functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    violations.extend(self._check_function(node, file_path))
                elif isinstance(node, ast.ClassDef):
                    violations.extend(self._check_class(node, file_path))
            
            # Check line length (PEP 8)
            for i, line in enumerate(lines, 1):
                if len(line) > 120:  # Using 120 as a reasonable limit
                    violations.append({
                        'type': 'line_too_long',
                        'severity': 'low',
                        'line': i,
                        'message': f'Line exceeds 120 characters ({len(line)} chars)',
                        'recommendation': 'Break long lines into multiple lines for better readability'
                    })
            
            # Check for magic numbers
            violations.extend(self._check_magic_numbers(tree))
            
            # Check for broad exception catching
            violations.extend(self._check_exception_handling(tree))
            
            return {
                'file': str(file_path.relative_to(self.repo_path)),
                'violations': violations,
                'total_violations': len(violations),
                'severity_counts': self._count_severities(violations)
            }
        except Exception as e:
            return {
                'file': str(file_path.relative_to(self.repo_path)),
                'error': str(e),
                'violations': []
            }
    
    def _check_function(self, node: ast.FunctionDef, file_path: Path) -> List[Dict[str, Any]]:
        """Check function for best practices violations."""
        violations = []
        
        # Check for missing docstring (except for private methods and __init__)
        if not node.name.startswith('_') or node.name == '__init__':
            docstring = ast.get_docstring(node)
            if not docstring:
                violations.append({
                    'type': 'missing_function_docstring',
                    'severity': 'medium',
                    'line': node.lineno,
                    'message': f'Function "{node.name}" is missing a docstring',
                    'recommendation': 'Add a docstring describing the function purpose, parameters, and return value'
                })
        
        # Check for too many parameters
        num_params = len(node.args.args)
        if num_params > 5:
            violations.append({
                'type': 'too_many_parameters',
                'severity': 'medium',
                'line': node.lineno,
                'message': f'Function "{node.name}" has {num_params} parameters (max recommended: 5)',
                'recommendation': 'Consider using a configuration object or breaking the function into smaller functions'
            })
        
        # Check for function length
        if hasattr(node, 'end_lineno'):
            func_length = node.end_lineno - node.lineno
            if func_length > 50:
                violations.append({
                    'type': 'function_too_long',
                    'severity': 'medium',
                    'line': node.lineno,
                    'message': f'Function "{node.name}" is {func_length} lines long (max recommended: 50)',
                    'recommendation': 'Break down large functions into smaller, more focused functions'
                })
        
        # Check for mutable default arguments
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                violations.append({
                    'type': 'mutable_default_argument',
                    'severity': 'high',
                    'line': node.lineno,
                    'message': f'Function "{node.name}" uses mutable default argument',
                    'recommendation': 'Use None as default and initialize inside the function'
                })
        
        return violations
    
    def _check_class(self, node: ast.ClassDef, file_path: Path) -> List[Dict[str, Any]]:
        """Check class for best practices violations."""
        violations = []
        
        # Check for missing class docstring
        docstring = ast.get_docstring(node)
        if not docstring:
            violations.append({
                'type': 'missing_class_docstring',
                'severity': 'medium',
                'line': node.lineno,
                'message': f'Class "{node.name}" is missing a docstring',
                'recommendation': 'Add a docstring describing the class purpose and usage'
            })
        
        # Check for too many methods
        methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:
            violations.append({
                'type': 'too_many_methods',
                'severity': 'medium',
                'line': node.lineno,
                'message': f'Class "{node.name}" has {len(methods)} methods (max recommended: 20)',
                'recommendation': 'Consider splitting the class into smaller, more focused classes'
            })
        
        return violations
    
    def _check_magic_numbers(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check for magic numbers in code."""
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Num):
                # Ignore common numbers like 0, 1, 2, -1, 100, 1000
                if node.n not in [0, 1, 2, -1, 10, 100, 1000]:
                    violations.append({
                        'type': 'magic_number',
                        'severity': 'low',
                        'line': node.lineno,
                        'message': f'Magic number {node.n} found',
                        'recommendation': 'Consider using a named constant for better code readability'
                    })
        
        return violations
    
    def _check_exception_handling(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check for exception handling best practices."""
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check for bare except
                if node.type is None:
                    violations.append({
                        'type': 'bare_except',
                        'severity': 'high',
                        'line': node.lineno,
                        'message': 'Bare except clause found',
                        'recommendation': 'Specify the exception type or use "except Exception" at minimum'
                    })
                # Check for catching too broad exceptions
                elif isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                    violations.append({
                        'type': 'broad_exception',
                        'severity': 'medium',
                        'line': node.lineno,
                        'message': 'Catching broad Exception type',
                        'recommendation': 'Catch specific exception types when possible'
                    })
        
        return violations
    
    def _count_severities(self, violations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count violations by severity."""
        counts = {'high': 0, 'medium': 0, 'low': 0}
        for v in violations:
            counts[v['severity']] += 1
        return counts
    
    def check_repository(self, file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check best practices across the entire repository.
        
        Args:
            file_extensions: List of file extensions to check (default: ['.py'])
            
        Returns:
            Dictionary containing repository-wide best practices results
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        results = {
            'files': [],
            'summary': {
                'total_files': 0,
                'files_with_violations': 0,
                'total_violations': 0,
                'severity_counts': {'high': 0, 'medium': 0, 'low': 0},
                'violation_types': {}
            }
        }
        
        # Check Python files
        if '.py' in file_extensions:
            for py_file in self.repo_path.rglob('*.py'):
                if '.git' not in str(py_file) and '__pycache__' not in str(py_file):
                    check_result = self.check_python_file(py_file)
                    results['files'].append(check_result)
                    results['summary']['total_files'] += 1
                    
                    if check_result.get('total_violations', 0) > 0:
                        results['summary']['files_with_violations'] += 1
                        results['summary']['total_violations'] += check_result['total_violations']
                        
                        # Update severity counts
                        for severity, count in check_result.get('severity_counts', {}).items():
                            results['summary']['severity_counts'][severity] += count
                        
                        # Count violation types
                        for violation in check_result.get('violations', []):
                            vtype = violation['type']
                            if vtype not in results['summary']['violation_types']:
                                results['summary']['violation_types'][vtype] = 0
                            results['summary']['violation_types'][vtype] += 1
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a markdown report of best practices check.
        
        Args:
            results: Results from check_repository()
            
        Returns:
            Markdown formatted report
        """
        report = ["# Best Practices Check Report\n"]
        
        # Summary
        report.append("## Summary\n")
        summary = results['summary']
        report.append(f"- **Total Files Checked**: {summary['total_files']}")
        report.append(f"- **Files with Violations**: {summary['files_with_violations']}")
        report.append(f"- **Total Violations**: {summary['total_violations']}")
        report.append(f"- **High Severity**: {summary['severity_counts']['high']}")
        report.append(f"- **Medium Severity**: {summary['severity_counts']['medium']}")
        report.append(f"- **Low Severity**: {summary['severity_counts']['low']}\n")
        
        # Violation types
        if summary['violation_types']:
            report.append("## Violation Types\n")
            report.append("| Violation Type | Count |")
            report.append("|----------------|-------|")
            
            # Sort by count
            sorted_types = sorted(summary['violation_types'].items(), key=lambda x: x[1], reverse=True)
            for vtype, count in sorted_types:
                report.append(f"| {vtype.replace('_', ' ').title()} | {count} |")
            report.append("")
        
        # High severity violations
        high_violations = []
        for file_result in results['files']:
            for violation in file_result.get('violations', []):
                if violation['severity'] == 'high':
                    high_violations.append({
                        'file': file_result['file'],
                        **violation
                    })
        
        if high_violations:
            report.append("## High Severity Violations\n")
            report.append("These issues should be addressed as soon as possible.\n")
            report.append("| File | Line | Type | Message |")
            report.append("|------|------|------|---------|")
            
            for v in high_violations[:20]:  # Top 20
                report.append(f"| {v['file']} | {v['line']} | {v['type']} | {v['message']} |")
            report.append("")
        
        # Files with most violations
        files_by_violations = sorted(
            [f for f in results['files'] if f.get('total_violations', 0) > 0],
            key=lambda x: x.get('total_violations', 0),
            reverse=True
        )
        
        if files_by_violations:
            report.append("## Files with Most Violations\n")
            report.append("| File | Total | High | Medium | Low |")
            report.append("|------|-------|------|--------|-----|")
            
            for file_result in files_by_violations[:10]:  # Top 10
                sc = file_result.get('severity_counts', {})
                report.append(
                    f"| {file_result['file']} | {file_result['total_violations']} | "
                    f"{sc.get('high', 0)} | {sc.get('medium', 0)} | {sc.get('low', 0)} |"
                )
            report.append("")
        
        # Recommendations
        report.append("## General Recommendations\n")
        report.append("1. **Documentation**: Add docstrings to all public modules, classes, and functions")
        report.append("2. **Function Design**: Keep functions small and focused (< 50 lines, < 5 parameters)")
        report.append("3. **Exception Handling**: Catch specific exceptions instead of broad Exception types")
        report.append("4. **Code Readability**: Use named constants instead of magic numbers")
        report.append("5. **Class Design**: Keep classes focused with reasonable number of methods (< 20)\n")
        
        return '\n'.join(report)
