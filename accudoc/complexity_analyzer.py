"""
Complexity Analysis Module for AccuDoc.

This module analyzes code complexity to identify areas that need documentation.
It calculates various complexity metrics like cyclomatic complexity, cognitive complexity,
and identifies complex functions/classes that would benefit from better documentation.
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional


class ComplexityAnalyzer:
    """Analyzer for code complexity metrics."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the complexity analyzer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.results = []
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze complexity of a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary containing complexity metrics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'complexity': complexity,
                        'parameters': len(node.args.args),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len(methods),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
            
            return {
                'file': str(file_path.relative_to(self.repo_path)),
                'functions': functions,
                'classes': classes,
                'total_functions': len(functions),
                'total_classes': len(classes),
                'complex_functions': [f for f in functions if f['complexity'] > 10],
                'undocumented_functions': [f for f in functions if not f['has_docstring'] and f['complexity'] > 5]
            }
        except Exception as e:
            return {
                'file': str(file_path.relative_to(self.repo_path)),
                'error': str(e),
                'functions': [],
                'classes': []
            }
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity for a function.
        
        Cyclomatic complexity = number of decision points + 1
        Decision points include: if, elif, for, while, and, or, except
        
        Args:
            node: AST node representing a function
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Control flow statements - if statements
            if isinstance(child, ast.If):
                complexity += 1
                # Count elif branches
                if child.orelse:
                    for orelse_item in child.orelse:
                        if isinstance(orelse_item, ast.If):
                            complexity += 1
            # Loops
            elif isinstance(child, (ast.For, ast.While)):
                complexity += 1
            # Context managers
            elif isinstance(child, ast.With):
                complexity += 1
            # Exception handling
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            # Boolean operators (and, or)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Comprehensions
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity
    
    def analyze_javascript_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze complexity of a JavaScript/TypeScript file (basic analysis).
        
        Args:
            file_path: Path to the JS/TS file
            
        Returns:
            Dictionary containing complexity metrics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex-based analysis for JS
            # Count function declarations
            functions = re.findall(r'function\s+(\w+)\s*\(', content)
            arrow_functions = re.findall(r'const\s+(\w+)\s*=\s*\(.*?\)\s*=>', content)
            
            # Count classes
            classes = re.findall(r'class\s+(\w+)', content)
            
            # Count control flow statements
            if_statements = len(re.findall(r'\bif\s*\(', content))
            for_loops = len(re.findall(r'\bfor\s*\(', content))
            while_loops = len(re.findall(r'\bwhile\s*\(', content))
            
            total_complexity = if_statements + for_loops + while_loops
            
            return {
                'file': str(file_path.relative_to(self.repo_path)),
                'functions': len(functions) + len(arrow_functions),
                'classes': len(classes),
                'control_flow_count': total_complexity,
                'estimated_complexity': 'high' if total_complexity > 20 else 'medium' if total_complexity > 10 else 'low'
            }
        except Exception as e:
            return {
                'file': str(file_path.relative_to(self.repo_path)),
                'error': str(e)
            }
    
    def analyze_repository(self, file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze complexity across the entire repository.
        
        Args:
            file_extensions: List of file extensions to analyze (default: ['.py', '.js', '.ts'])
            
        Returns:
            Dictionary containing repository-wide complexity metrics
        """
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts']
        
        results = {
            'python_files': [],
            'javascript_files': [],
            'summary': {
                'total_files': 0,
                'total_functions': 0,
                'total_classes': 0,
                'high_complexity_functions': [],
                'undocumented_complex_functions': []
            }
        }
        
        # Analyze Python files
        if '.py' in file_extensions:
            for py_file in self.repo_path.rglob('*.py'):
                if '.git' not in str(py_file) and '__pycache__' not in str(py_file):
                    analysis = self.analyze_python_file(py_file)
                    results['python_files'].append(analysis)
                    results['summary']['total_files'] += 1
                    results['summary']['total_functions'] += analysis.get('total_functions', 0)
                    results['summary']['total_classes'] += analysis.get('total_classes', 0)
                    
                    # Collect high complexity functions
                    for func in analysis.get('complex_functions', []):
                        results['summary']['high_complexity_functions'].append({
                            'file': analysis['file'],
                            'function': func['name'],
                            'complexity': func['complexity'],
                            'line': func['line']
                        })
                    
                    # Collect undocumented complex functions
                    for func in analysis.get('undocumented_functions', []):
                        results['summary']['undocumented_complex_functions'].append({
                            'file': analysis['file'],
                            'function': func['name'],
                            'complexity': func['complexity'],
                            'line': func['line']
                        })
        
        # Analyze JavaScript/TypeScript files
        if '.js' in file_extensions or '.ts' in file_extensions:
            for ext in ['.js', '.ts']:
                if ext in file_extensions:
                    for js_file in self.repo_path.rglob(f'*{ext}'):
                        if 'node_modules' not in str(js_file) and '.git' not in str(js_file):
                            analysis = self.analyze_javascript_file(js_file)
                            results['javascript_files'].append(analysis)
                            results['summary']['total_files'] += 1
        
        # Sort high complexity functions by complexity
        results['summary']['high_complexity_functions'].sort(
            key=lambda x: x['complexity'], reverse=True
        )
        
        return results
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a markdown report of complexity analysis.
        
        Args:
            analysis: Analysis results from analyze_repository()
            
        Returns:
            Markdown formatted report
        """
        report = ["# Code Complexity Analysis Report\n"]
        
        # Summary
        report.append("## Summary\n")
        summary = analysis['summary']
        report.append(f"- **Total Files Analyzed**: {summary['total_files']}")
        report.append(f"- **Total Functions**: {summary['total_functions']}")
        report.append(f"- **Total Classes**: {summary['total_classes']}")
        report.append(f"- **High Complexity Functions**: {len(summary['high_complexity_functions'])}")
        report.append(f"- **Undocumented Complex Functions**: {len(summary['undocumented_complex_functions'])}\n")
        
        # High complexity functions
        if summary['high_complexity_functions']:
            report.append("## High Complexity Functions (>10)\n")
            report.append("These functions have high cyclomatic complexity and may benefit from refactoring or better documentation.\n")
            report.append("| File | Function | Complexity | Line |")
            report.append("|------|----------|------------|------|")
            
            for func in summary['high_complexity_functions'][:20]:  # Top 20
                report.append(f"| {func['file']} | {func['function']} | {func['complexity']} | {func['line']} |")
            report.append("")
        
        # Undocumented complex functions
        if summary['undocumented_complex_functions']:
            report.append("## Undocumented Complex Functions\n")
            report.append("These functions are complex but lack documentation.\n")
            report.append("| File | Function | Complexity | Line |")
            report.append("|------|----------|------------|------|")
            
            for func in summary['undocumented_complex_functions'][:20]:  # Top 20
                report.append(f"| {func['file']} | {func['function']} | {func['complexity']} | {func['line']} |")
            report.append("")
        
        # Python files details
        if analysis['python_files']:
            report.append("## Python Files Analysis\n")
            for file_analysis in analysis['python_files'][:10]:  # Top 10 files
                if 'error' in file_analysis:
                    continue
                    
                complex_funcs = file_analysis.get('complex_functions', [])
                if complex_funcs or file_analysis.get('total_functions', 0) > 5:
                    report.append(f"### {file_analysis['file']}\n")
                    report.append(f"- Functions: {file_analysis['total_functions']}")
                    report.append(f"- Classes: {file_analysis['total_classes']}")
                    report.append(f"- Complex Functions: {len(complex_funcs)}\n")
        
        # Recommendations
        report.append("## Recommendations\n")
        report.append("1. **Refactor high complexity functions**: Consider breaking down functions with complexity > 10")
        report.append("2. **Add documentation**: Document complex functions to improve code maintainability")
        report.append("3. **Follow best practices**: Keep functions focused on a single responsibility")
        report.append("4. **Regular reviews**: Periodically review complexity metrics to maintain code quality\n")
        
        return '\n'.join(report)
