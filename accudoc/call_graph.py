"""
Call Graph Generator Module for AccuDoc.

This module generates call graphs showing function call relationships within code.
It helps understand code flow and dependencies between functions.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict


class CallGraphGenerator:
    """Generator for function call graphs."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the call graph generator.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.call_graph = defaultdict(set)
        self.functions = {}
        self.classes = {}
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a Python file to extract function calls.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary containing call graph information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract function definitions
            visitor = CallGraphVisitor(str(file_path.relative_to(self.repo_path)))
            visitor.visit(tree)
            
            return {
                'file': str(file_path.relative_to(self.repo_path)),
                'functions': visitor.functions,
                'classes': visitor.classes,
                'calls': visitor.calls,
                'imports': visitor.imports
            }
        except Exception as e:
            return {
                'file': str(file_path.relative_to(self.repo_path)),
                'error': str(e),
                'functions': {},
                'classes': {},
                'calls': {}
            }
    
    def build_call_graph(self, file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build a complete call graph from multiple file analyses.
        
        Args:
            file_analyses: List of file analysis results
            
        Returns:
            Complete call graph structure
        """
        call_graph = defaultdict(set)
        all_functions = {}
        all_classes = {}
        
        # Collect all functions and classes
        for analysis in file_analyses:
            if 'error' in analysis:
                continue
            
            file_name = analysis['file']
            
            # Store functions with their file location
            for func_name, func_info in analysis['functions'].items():
                qualified_name = f"{file_name}::{func_name}"
                all_functions[qualified_name] = {
                    'file': file_name,
                    'name': func_name,
                    'line': func_info['line'],
                    'parameters': func_info.get('parameters', [])
                }
            
            # Store classes
            for class_name, class_info in analysis['classes'].items():
                qualified_name = f"{file_name}::{class_name}"
                all_classes[qualified_name] = {
                    'file': file_name,
                    'name': class_name,
                    'line': class_info['line'],
                    'methods': class_info.get('methods', [])
                }
            
            # Build call relationships
            for caller, callees in analysis['calls'].items():
                qualified_caller = f"{file_name}::{caller}"
                for callee in callees:
                    # Try to qualify the callee
                    qualified_callee = f"{file_name}::{callee}"
                    call_graph[qualified_caller].add(qualified_callee)
        
        return {
            'functions': all_functions,
            'classes': all_classes,
            'call_graph': dict(call_graph),
            'summary': {
                'total_functions': len(all_functions),
                'total_classes': len(all_classes),
                'total_call_relationships': sum(len(v) for v in call_graph.values())
            }
        }
    
    def analyze_repository(self, file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze the entire repository to build call graph.
        
        Args:
            file_extensions: List of file extensions to analyze (default: ['.py'])
            
        Returns:
            Complete call graph for the repository
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        file_analyses = []
        
        # Analyze Python files
        if '.py' in file_extensions:
            for py_file in self.repo_path.rglob('*.py'):
                if '.git' not in str(py_file) and '__pycache__' not in str(py_file):
                    analysis = self.analyze_python_file(py_file)
                    file_analyses.append(analysis)
        
        return self.build_call_graph(file_analyses)
    
    def find_callers(self, function_name: str, call_graph: Dict[str, Any]) -> List[str]:
        """
        Find all functions that call a given function.
        
        Args:
            function_name: Name of the function to find callers for
            call_graph: The complete call graph
            
        Returns:
            List of function names that call the given function
        """
        callers = []
        graph = call_graph['call_graph']
        
        for caller, callees in graph.items():
            for callee in callees:
                if function_name in callee:
                    callers.append(caller)
        
        return callers
    
    def find_callees(self, function_name: str, call_graph: Dict[str, Any]) -> List[str]:
        """
        Find all functions called by a given function.
        
        Args:
            function_name: Name of the function to find callees for
            call_graph: The complete call graph
            
        Returns:
            List of function names called by the given function
        """
        graph = call_graph['call_graph']
        
        for caller, callees in graph.items():
            if function_name in caller:
                return list(callees)
        
        return []
    
    def generate_mermaid_diagram(self, call_graph: Dict[str, Any], max_nodes: int = 20) -> str:
        """
        Generate a Mermaid diagram representation of the call graph.
        
        Args:
            call_graph: The complete call graph
            max_nodes: Maximum number of nodes to include (to avoid huge diagrams)
            
        Returns:
            Mermaid diagram syntax
        """
        diagram = ["```mermaid", "graph TD"]
        
        graph = call_graph['call_graph']
        
        # Limit to most connected nodes
        node_counts = defaultdict(int)
        for caller, callees in graph.items():
            node_counts[caller] += len(callees)
            for callee in callees:
                node_counts[callee] += 1
        
        # Get top nodes
        top_nodes = sorted(node_counts.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
        top_node_names = {node for node, _ in top_nodes}
        
        # Generate node definitions with simplified names
        node_mapping = {}
        for i, (node, _) in enumerate(top_nodes):
            # Simplify node name
            simple_name = node.split('::')[-1]
            node_id = f"N{i}"
            node_mapping[node] = node_id
            diagram.append(f'    {node_id}["{simple_name}"]')
        
        # Generate edges
        for caller, callees in graph.items():
            if caller in top_node_names:
                for callee in callees:
                    if callee in top_node_names:
                        diagram.append(f'    {node_mapping[caller]} --> {node_mapping[callee]}')
        
        diagram.append("```")
        return '\n'.join(diagram)
    
    def generate_report(self, call_graph: Dict[str, Any]) -> str:
        """
        Generate a markdown report of the call graph.
        
        Args:
            call_graph: The complete call graph
            
        Returns:
            Markdown formatted report
        """
        report = ["# Call Graph Analysis Report\n"]
        
        # Summary
        report.append("## Summary\n")
        summary = call_graph['summary']
        report.append(f"- **Total Functions**: {summary['total_functions']}")
        report.append(f"- **Total Classes**: {summary['total_classes']}")
        report.append(f"- **Total Call Relationships**: {summary['total_call_relationships']}\n")
        
        # Most called functions
        graph = call_graph['call_graph']
        callee_counts = defaultdict(int)
        for callees in graph.values():
            for callee in callees:
                callee_counts[callee] += 1
        
        if callee_counts:
            report.append("## Most Called Functions\n")
            report.append("These functions are called most frequently across the codebase.\n")
            report.append("| Function | Times Called |")
            report.append("|----------|--------------|")
            
            sorted_callees = sorted(callee_counts.items(), key=lambda x: x[1], reverse=True)
            for callee, count in sorted_callees[:10]:
                simple_name = callee.split('::')[-1]
                report.append(f"| {simple_name} | {count} |")
            report.append("")
        
        # Functions that call many others
        caller_counts = {caller: len(callees) for caller, callees in graph.items()}
        if caller_counts:
            report.append("## Functions with Most Dependencies\n")
            report.append("These functions call many other functions.\n")
            report.append("| Function | Functions Called |")
            report.append("|----------|------------------|")
            
            sorted_callers = sorted(caller_counts.items(), key=lambda x: x[1], reverse=True)
            for caller, count in sorted_callers[:10]:
                if count > 0:
                    simple_name = caller.split('::')[-1]
                    report.append(f"| {simple_name} | {count} |")
            report.append("")
        
        # Call graph visualization
        if graph:
            report.append("## Call Graph Visualization\n")
            report.append("The following diagram shows the relationships between the most connected functions.\n")
            mermaid = self.generate_mermaid_diagram(call_graph)
            report.append(mermaid)
            report.append("")
        
        # Recommendations
        report.append("## Recommendations\n")
        report.append("1. **Review highly called functions**: Ensure they are well-tested and documented")
        report.append("2. **Reduce coupling**: Functions calling many others may need refactoring")
        report.append("3. **Identify core functions**: Most called functions are critical to the codebase")
        report.append("4. **Document dependencies**: Make function dependencies clear in documentation\n")
        
        return '\n'.join(report)


class CallGraphVisitor(ast.NodeVisitor):
    """AST visitor to extract function call information."""
    
    def __init__(self, file_name: str):
        """Initialize the visitor."""
        self.file_name = file_name
        self.functions = {}
        self.classes = {}
        self.calls = defaultdict(set)
        self.imports = []
        self.current_function = None
        self.current_class = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit a function definition."""
        func_name = node.name
        
        if self.current_class:
            func_name = f"{self.current_class}.{func_name}"
        
        self.functions[func_name] = {
            'line': node.lineno,
            'parameters': [arg.arg for arg in node.args.args]
        }
        
        # Track current function for call tracking
        old_function = self.current_function
        self.current_function = func_name
        
        # Visit function body
        self.generic_visit(node)
        
        self.current_function = old_function
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit a class definition."""
        class_name = node.name
        
        self.classes[class_name] = {
            'line': node.lineno,
            'methods': []
        }
        
        # Track current class
        old_class = self.current_class
        self.current_class = class_name
        
        # Visit class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.classes[class_name]['methods'].append(item.name)
        
        self.generic_visit(node)
        
        self.current_class = old_class
    
    def visit_Call(self, node: ast.Call):
        """Visit a function call."""
        if self.current_function:
            # Extract function name being called
            if isinstance(node.func, ast.Name):
                called_func = node.func.id
                self.calls[self.current_function].add(called_func)
            elif isinstance(node.func, ast.Attribute):
                # Handle method calls like obj.method()
                if isinstance(node.func.value, ast.Name):
                    called_func = f"{node.func.value.id}.{node.func.attr}"
                else:
                    called_func = node.func.attr
                self.calls[self.current_function].add(called_func)
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import):
        """Visit an import statement."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit a from...import statement."""
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)
