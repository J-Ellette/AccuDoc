"""
Data Flow Analysis module for AccuDoc.

This module provides functionality to analyze and document how data
flows through an application by tracking variables, parameters, and
return values across functions and methods.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict


class DataFlowNode:
    """Represents a node in the data flow graph."""
    
    def __init__(self, name: str, node_type: str, location: str = ""):
        """
        Initialize a data flow node.
        
        Args:
            name: Name of the variable/parameter
            node_type: Type of node (variable, parameter, return, etc.)
            location: Source location (file:line)
        """
        self.name = name
        self.node_type = node_type
        self.location = location
        self.sources = []  # Where data comes from
        self.targets = []  # Where data goes to
        self.transformations = []  # How data is transformed
        
    def __repr__(self):
        return f"DataFlowNode({self.name}, {self.node_type})"


class DataFlowAnalyzer:
    """Analyzes data flow in Python code."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the analyzer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.flows = defaultdict(list)  # function_name -> [DataFlowNode]
        self.variables = defaultdict(set)  # function_name -> {variable_names}
        self.assignments = defaultdict(list)  # function_name -> [(var, value, line)]
        
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze data flow in a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary containing data flow information
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            result = {
                'file': str(file_path),
                'functions': [],
                'classes': []
            }
            
            # Analyze all functions and methods
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node, str(file_path))
                    result['functions'].append(func_info)
                elif isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node, str(file_path))
                    result['classes'].append(class_info)
            
            return result
            
        except Exception as e:
            return {
                'file': str(file_path),
                'error': str(e),
                'functions': [],
                'classes': []
            }
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: str) -> Dict[str, Any]:
        """
        Analyze data flow in a function.
        
        Args:
            node: AST FunctionDef node
            file_path: Path to source file
            
        Returns:
            Function data flow information
        """
        func_name = node.name
        location = f"{file_path}:{node.lineno}"
        
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            param_name = arg.arg
            parameters.append({
                'name': param_name,
                'line': arg.lineno if hasattr(arg, 'lineno') else node.lineno
            })
        
        # Track variable assignments and usage
        assignments = []
        variables_read = set()
        variables_written = set()
        
        for child in ast.walk(node):
            # Track assignments
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        variables_written.add(var_name)
                        
                        # Try to get the value being assigned
                        value_str = self._get_value_string(child.value)
                        assignments.append({
                            'variable': var_name,
                            'value': value_str,
                            'line': child.lineno
                        })
            
            # Track augmented assignments (+=, -=, etc.)
            elif isinstance(child, ast.AugAssign):
                if isinstance(child.target, ast.Name):
                    var_name = child.target.id
                    variables_written.add(var_name)
                    variables_read.add(var_name)
                    
                    op_str = self._get_operator_string(child.op)
                    value_str = self._get_value_string(child.value)
                    assignments.append({
                        'variable': var_name,
                        'value': f"{var_name} {op_str} {value_str}",
                        'line': child.lineno
                    })
            
            # Track variable reads
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                variables_read.add(child.id)
        
        # Find return statements
        returns = []
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                return_str = self._get_value_string(child.value)
                returns.append({
                    'value': return_str,
                    'line': child.lineno
                })
        
        return {
            'name': func_name,
            'location': location,
            'parameters': parameters,
            'assignments': assignments,
            'variables_read': sorted(list(variables_read)),
            'variables_written': sorted(list(variables_written)),
            'returns': returns
        }
    
    def _analyze_class(self, node: ast.ClassDef, file_path: str) -> Dict[str, Any]:
        """
        Analyze data flow in a class.
        
        Args:
            node: AST ClassDef node
            file_path: Path to source file
            
        Returns:
            Class data flow information
        """
        class_name = node.name
        location = f"{file_path}:{node.lineno}"
        
        methods = []
        attributes = set()
        
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                method_info = self._analyze_function(child, file_path)
                method_info['is_method'] = True
                methods.append(method_info)
                
                # Track instance attributes (self.x)
                for grandchild in ast.walk(child):
                    if isinstance(grandchild, ast.Attribute):
                        if isinstance(grandchild.value, ast.Name) and grandchild.value.id == 'self':
                            attributes.add(grandchild.attr)
        
        return {
            'name': class_name,
            'location': location,
            'methods': methods,
            'attributes': sorted(list(attributes))
        }
    
    def _get_value_string(self, node: ast.AST) -> str:
        """
        Get a string representation of an AST value node.
        
        Args:
            node: AST node
            
        Returns:
            String representation
        """
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            left = self._get_value_string(node.left)
            right = self._get_value_string(node.right)
            op = self._get_operator_string(node.op)
            return f"{left} {op} {right}"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            else:
                func_name = "function"
            
            args = [self._get_value_string(arg) for arg in node.args[:2]]  # Limit to 2 args
            if len(node.args) > 2:
                args.append("...")
            return f"{func_name}({', '.join(args)})"
        elif isinstance(node, ast.List):
            if len(node.elts) <= 3:
                elements = [self._get_value_string(e) for e in node.elts]
                return f"[{', '.join(elements)}]"
            else:
                return f"[... {len(node.elts)} items ...]"
        elif isinstance(node, ast.Dict):
            return f"{{... {len(node.keys)} items ...}}"
        elif isinstance(node, ast.Attribute):
            value = self._get_value_string(node.value)
            return f"{value}.{node.attr}"
        else:
            return f"<{type(node).__name__}>"
    
    def _get_operator_string(self, op: ast.operator) -> str:
        """
        Get string representation of an operator.
        
        Args:
            op: AST operator node
            
        Returns:
            Operator string
        """
        op_map = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
            ast.Pow: '**',
            ast.FloorDiv: '//',
            ast.BitOr: '|',
            ast.BitAnd: '&',
            ast.BitXor: '^',
        }
        return op_map.get(type(op), '?')
    
    def analyze_repository(self, extensions: List[str] = None) -> Dict[str, Any]:
        """
        Analyze data flow across entire repository.
        
        Args:
            extensions: File extensions to analyze (default: ['.py'])
            
        Returns:
            Repository-wide data flow information
        """
        if extensions is None:
            extensions = ['.py']
        
        results = {
            'repository': str(self.repo_path),
            'files': [],
            'summary': {
                'total_files': 0,
                'total_functions': 0,
                'total_classes': 0,
                'total_assignments': 0
            }
        }
        
        # Find all Python files
        for ext in extensions:
            for file_path in self.repo_path.rglob(f'*{ext}'):
                if '.git' in str(file_path) or '__pycache__' in str(file_path):
                    continue
                
                file_result = self.analyze_file(file_path)
                
                if 'error' not in file_result:
                    results['files'].append(file_result)
                    results['summary']['total_files'] += 1
                    results['summary']['total_functions'] += len(file_result['functions'])
                    results['summary']['total_classes'] += len(file_result['classes'])
                    
                    # Count assignments
                    for func in file_result['functions']:
                        results['summary']['total_assignments'] += len(func['assignments'])
                    for cls in file_result['classes']:
                        for method in cls['methods']:
                            results['summary']['total_assignments'] += len(method['assignments'])
        
        return results
    
    def generate_mermaid_diagram(self, function_data: Dict[str, Any]) -> str:
        """
        Generate a Mermaid flowchart showing data flow in a function.
        
        Args:
            function_data: Function data from analyze_function
            
        Returns:
            Mermaid diagram syntax
        """
        lines = [
            "```mermaid",
            "graph TD",
            f"    START([Start: {function_data['name']}])"
        ]
        
        # Add parameters
        if function_data['parameters']:
            for param in function_data['parameters']:
                param_id = f"PARAM_{param['name']}"
                lines.append(f"    {param_id}[/Parameter: {param['name']}/]")
                lines.append(f"    START --> {param_id}")
        
        # Add assignments
        for i, assignment in enumerate(function_data['assignments']):
            var_name = assignment['variable']
            value = assignment['value']
            assign_id = f"ASSIGN_{i}"
            
            # Truncate long values
            if len(value) > 30:
                value = value[:27] + "..."
            
            lines.append(f"    {assign_id}[\"{var_name} = {value}\"]")
            
            # Connect from parameters or previous assignments
            if i == 0 and function_data['parameters']:
                lines.append(f"    PARAM_{function_data['parameters'][0]['name']} --> {assign_id}")
            elif i > 0:
                lines.append(f"    ASSIGN_{i-1} --> {assign_id}")
            else:
                lines.append(f"    START --> {assign_id}")
        
        # Add returns
        if function_data['returns']:
            for i, ret in enumerate(function_data['returns']):
                return_id = f"RETURN_{i}"
                value = ret['value']
                
                # Truncate long values
                if len(value) > 30:
                    value = value[:27] + "..."
                
                lines.append(f"    {return_id}([Return: {value}])")
                
                if function_data['assignments']:
                    last_assign = f"ASSIGN_{len(function_data['assignments'])-1}"
                    lines.append(f"    {last_assign} --> {return_id}")
                else:
                    lines.append(f"    START --> {return_id}")
        
        lines.append("```")
        return "\n".join(lines)
    
    def generate_report(self, analysis_results: Dict[str, Any], 
                       include_diagrams: bool = True) -> str:
        """
        Generate a markdown report of data flow analysis.
        
        Args:
            analysis_results: Results from analyze_repository or analyze_file
            include_diagrams: Whether to include Mermaid diagrams
            
        Returns:
            Markdown report
        """
        lines = [
            "# Data Flow Analysis Report",
            "",
            f"**Repository**: {analysis_results.get('repository', 'N/A')}",
            ""
        ]
        
        # Summary
        if 'summary' in analysis_results:
            summary = analysis_results['summary']
            lines.extend([
                "## Summary",
                "",
                f"- **Total Files Analyzed**: {summary['total_files']}",
                f"- **Total Functions**: {summary['total_functions']}",
                f"- **Total Classes**: {summary['total_classes']}",
                f"- **Total Variable Assignments**: {summary['total_assignments']}",
                ""
            ])
        
        # File details
        files = analysis_results.get('files', [analysis_results])
        
        for file_data in files[:10]:  # Limit to first 10 files
            if 'error' in file_data:
                continue
            
            lines.extend([
                f"## File: `{file_data['file']}`",
                ""
            ])
            
            # Functions
            if file_data['functions']:
                lines.append("### Functions")
                lines.append("")
                
                for func in file_data['functions']:
                    lines.extend([
                        f"#### `{func['name']}()`",
                        "",
                        f"**Location**: {func['location']}",
                        ""
                    ])
                    
                    # Parameters
                    if func['parameters']:
                        lines.append("**Parameters**:")
                        for param in func['parameters']:
                            lines.append(f"- `{param['name']}`")
                        lines.append("")
                    
                    # Assignments
                    if func['assignments']:
                        lines.append("**Variable Assignments**:")
                        for assign in func['assignments'][:5]:  # Limit to 5
                            lines.append(f"- Line {assign['line']}: `{assign['variable']} = {assign['value']}`")
                        if len(func['assignments']) > 5:
                            lines.append(f"- ... and {len(func['assignments']) - 5} more")
                        lines.append("")
                    
                    # Variables read/written
                    if func['variables_read']:
                        lines.append(f"**Variables Read**: {', '.join(f'`{v}`' for v in func['variables_read'][:10])}")
                        lines.append("")
                    
                    if func['variables_written']:
                        lines.append(f"**Variables Written**: {', '.join(f'`{v}`' for v in func['variables_written'][:10])}")
                        lines.append("")
                    
                    # Returns
                    if func['returns']:
                        lines.append("**Return Values**:")
                        for ret in func['returns'][:3]:
                            lines.append(f"- Line {ret['line']}: `{ret['value']}`")
                        lines.append("")
                    
                    # Diagram
                    if include_diagrams and (func['parameters'] or func['assignments'] or func['returns']):
                        lines.append("**Data Flow Diagram**:")
                        lines.append("")
                        lines.append(self.generate_mermaid_diagram(func))
                        lines.append("")
            
            # Classes
            if file_data['classes']:
                lines.append("### Classes")
                lines.append("")
                
                for cls in file_data['classes']:
                    lines.extend([
                        f"#### `{cls['name']}`",
                        "",
                        f"**Location**: {cls['location']}",
                        ""
                    ])
                    
                    # Attributes
                    if cls['attributes']:
                        lines.append(f"**Instance Attributes**: {', '.join(f'`{a}`' for a in cls['attributes'])}")
                        lines.append("")
                    
                    # Methods
                    if cls['methods']:
                        lines.append("**Methods**:")
                        for method in cls['methods'][:5]:
                            lines.append(f"- `{method['name']}()` - {len(method['assignments'])} assignments")
                        if len(cls['methods']) > 5:
                            lines.append(f"- ... and {len(cls['methods']) - 5} more methods")
                        lines.append("")
        
        if len(files) > 10:
            lines.extend([
                "---",
                "",
                f"*Note: Showing details for first 10 files. Total files analyzed: {len(files)}*"
            ])
        
        return "\n".join(lines)
