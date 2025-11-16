#!/usr/bin/env python3
"""
AccuDoc Visual Documentation Tools

Provides comprehensive visual documentation generation including:
- Architecture diagrams (Mermaid, PlantUML)
- Interactive API explorers
- Flowchart generation from code
- Dependency graph visualizations
- Sequence diagram creation
- Class relationship diagrams
- Entity-relationship diagrams
- State machine diagrams
"""

import argparse
import json
import re
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import ast


@dataclass
class DiagramConfig:
    """Configuration for diagram generation"""
    diagram_type: str  # mermaid, plantuml, graphviz
    output_format: str  # svg, png, pdf, html
    theme: str  # default, dark, forest, neutral
    direction: str  # TB, LR, RL, BT
    show_attributes: bool = True
    show_methods: bool = True
    max_depth: int = 3
    include_external: bool = False


@dataclass
class DiagramElement:
    """Base diagram element"""
    id: str
    label: str
    type: str
    properties: Dict[str, Any]


class MermaidGenerator:
    """Generate Mermaid diagrams from code analysis"""
    
    def __init__(self, theme: str = "default"):
        self.theme = theme
        self.elements = []
        self.relationships = []
    
    def generate_architecture_diagram(self, scan_data: Dict, config: DiagramConfig) -> str:
        """Generate high-level architecture diagram"""
        mermaid = [f"graph {config.direction}"]
        
        if self.theme != "default":
            mermaid.append(f"%%{{init: {{'theme':'{self.theme}'}}}}%%")
        
        # Group files by directory
        directories = defaultdict(list)
        for file in scan_data.get("files", []):
            dir_path = Path(file.get("path", "")).parent
            directories[str(dir_path)].append(file)
        
        # Create directory nodes
        for idx, (dir_path, files) in enumerate(directories.items()):
            dir_name = Path(dir_path).name or "root"
            mermaid.append(f"    subgraph {dir_name}_{idx}[\"{dir_name}\"]")
            
            # Add file nodes (limit to avoid clutter)
            for file in files[:5]:
                file_name = Path(file["path"]).name
                file_id = f"file_{idx}_{file_name.replace('.', '_')}"
                mermaid.append(f"        {file_id}[\"{file_name}\"]")
            
            if len(files) > 5:
                mermaid.append(f"        more_{idx}[\"... {len(files) - 5} more files\"]")
            
            mermaid.append("    end")
        
        return "\n".join(mermaid)
    
    def generate_class_diagram(self, python_file: str) -> str:
        """Generate class diagram from Python file"""
        mermaid = ["classDiagram"]
        
        try:
            with open(python_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            classes = {}
            
            # Extract classes and their members
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    classes[class_name] = {
                        'methods': [],
                        'attributes': [],
                        'bases': [base.id for base in node.bases if isinstance(base, ast.Name)]
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Extract method signature
                            args = [arg.arg for arg in item.args.args if arg.arg != 'self']
                            method_sig = f"{item.name}({', '.join(args)})"
                            classes[class_name]['methods'].append(method_sig)
                        elif isinstance(item, ast.Assign):
                            # Extract attributes
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    classes[class_name]['attributes'].append(target.id)
            
            # Generate Mermaid class definitions
            for class_name, class_info in classes.items():
                mermaid.append(f"    class {class_name} {{")
                
                # Add attributes
                for attr in class_info['attributes']:
                    mermaid.append(f"        +{attr}")
                
                # Add methods
                for method in class_info['methods']:
                    mermaid.append(f"        +{method}")
                
                mermaid.append("    }")
                
                # Add inheritance relationships
                for base in class_info['bases']:
                    if base in classes:
                        mermaid.append(f"    {base} <|-- {class_name}")
            
        except Exception as e:
            mermaid.append(f"    note \"Error parsing file: {str(e)}\"")
        
        return "\n".join(mermaid)
    
    def generate_sequence_diagram(self, interactions: List[Dict]) -> str:
        """Generate sequence diagram from interaction data"""
        mermaid = ["sequenceDiagram"]
        
        participants = set()
        for interaction in interactions:
            participants.add(interaction.get('from', 'Unknown'))
            participants.add(interaction.get('to', 'Unknown'))
        
        # Define participants
        for participant in participants:
            mermaid.append(f"    participant {participant}")
        
        # Add interactions
        for interaction in interactions:
            from_entity = interaction.get('from', 'Unknown')
            to_entity = interaction.get('to', 'Unknown')
            message = interaction.get('message', '')
            arrow_type = interaction.get('type', '->')
            
            mermaid.append(f"    {from_entity}{arrow_type}{to_entity}: {message}")
        
        return "\n".join(mermaid)
    
    def generate_flowchart(self, function_ast: ast.FunctionDef) -> str:
        """Generate flowchart from function AST"""
        mermaid = ["flowchart TD"]
        
        node_counter = [0]  # Use list to allow modification in nested function
        
        def get_node_id():
            node_counter[0] += 1
            return f"node{node_counter[0]}"
        
        def process_node(node, parent_id=None):
            if isinstance(node, ast.If):
                # Create decision node
                node_id = get_node_id()
                condition = ast.unparse(node.test) if hasattr(ast, 'unparse') else "condition"
                mermaid.append(f"    {node_id}{{{condition}?}}")
                
                if parent_id:
                    mermaid.append(f"    {parent_id} --> {node_id}")
                
                # Process true branch
                true_branch_id = get_node_id()
                mermaid.append(f"    {true_branch_id}[True Branch]")
                mermaid.append(f"    {node_id} -->|Yes| {true_branch_id}")
                
                for child in node.body:
                    process_node(child, true_branch_id)
                
                # Process false branch if exists
                if node.orelse:
                    false_branch_id = get_node_id()
                    mermaid.append(f"    {false_branch_id}[False Branch]")
                    mermaid.append(f"    {node_id} -->|No| {false_branch_id}")
                    
                    for child in node.orelse:
                        process_node(child, false_branch_id)
                
                return node_id
            
            elif isinstance(node, ast.For) or isinstance(node, ast.While):
                # Create loop node
                node_id = get_node_id()
                loop_type = "For Loop" if isinstance(node, ast.For) else "While Loop"
                mermaid.append(f"    {node_id}[({loop_type})]")
                
                if parent_id:
                    mermaid.append(f"    {parent_id} --> {node_id}")
                
                for child in node.body:
                    process_node(child, node_id)
                
                return node_id
            
            elif isinstance(node, ast.Return):
                # Create return node
                node_id = get_node_id()
                return_value = ast.unparse(node.value) if hasattr(ast, 'unparse') and node.value else "None"
                mermaid.append(f"    {node_id}([Return: {return_value[:30]}])")
                
                if parent_id:
                    mermaid.append(f"    {parent_id} --> {node_id}")
                
                return node_id
            
            elif isinstance(node, (ast.Expr, ast.Assign)):
                # Create statement node
                node_id = get_node_id()
                stmt = ast.unparse(node) if hasattr(ast, 'unparse') else "statement"
                mermaid.append(f"    {node_id}[\"{stmt[:40]}...\"]")
                
                if parent_id:
                    mermaid.append(f"    {parent_id} --> {node_id}")
                
                return node_id
            
            return parent_id
        
        # Start node
        start_id = get_node_id()
        mermaid.append(f"    {start_id}([Start: {function_ast.name}])")
        
        # Process function body
        last_node = start_id
        for node in function_ast.body:
            last_node = process_node(node, last_node) or last_node
        
        return "\n".join(mermaid)
    
    def generate_er_diagram(self, models: List[Dict]) -> str:
        """Generate Entity-Relationship diagram"""
        mermaid = ["erDiagram"]
        
        for model in models:
            entity_name = model.get('name', 'Unknown')
            attributes = model.get('attributes', [])
            
            # Define entity
            mermaid.append(f"    {entity_name} {{")
            for attr in attributes:
                attr_name = attr.get('name', '')
                attr_type = attr.get('type', 'string')
                mermaid.append(f"        {attr_type} {attr_name}")
            mermaid.append("    }")
        
        # Add relationships
        for model in models:
            entity_name = model.get('name', 'Unknown')
            relationships = model.get('relationships', [])
            
            for rel in relationships:
                target = rel.get('target', '')
                rel_type = rel.get('type', 'one-to-many')
                cardinality = rel.get('cardinality', '||--o{')
                
                mermaid.append(f"    {entity_name} {cardinality} {target} : \"{rel_type}\"")
        
        return "\n".join(mermaid)
    
    def generate_state_diagram(self, states: List[Dict]) -> str:
        """Generate state machine diagram"""
        mermaid = ["stateDiagram-v2"]
        
        mermaid.append("    [*] --> " + states[0]['name'])
        
        for state in states:
            state_name = state.get('name', 'Unknown')
            transitions = state.get('transitions', [])
            
            # Add state description if available
            description = state.get('description', '')
            if description:
                mermaid.append(f"    {state_name}: {description}")
            
            # Add transitions
            for transition in transitions:
                target = transition.get('target', '')
                event = transition.get('event', '')
                mermaid.append(f"    {state_name} --> {target}: {event}")
        
        # Add final state if specified
        final_state = next((s for s in states if s.get('is_final', False)), None)
        if final_state:
            mermaid.append(f"    {final_state['name']} --> [*]")
        
        return "\n".join(mermaid)
    
    def generate_dependency_graph(self, dependencies: Dict) -> str:
        """Generate dependency graph"""
        mermaid = ["graph LR"]
        
        processed = set()
        
        for package, info in dependencies.items():
            if package not in processed:
                package_id = package.replace('-', '_').replace('.', '_')
                mermaid.append(f"    {package_id}[\"{package}\"]")
                processed.add(package)
            
            deps = info.get('dependencies', [])
            for dep in deps:
                if dep not in processed:
                    dep_id = dep.replace('-', '_').replace('.', '_')
                    mermaid.append(f"    {dep_id}[\"{dep}\"]")
                    processed.add(dep)
                
                package_id = package.replace('-', '_').replace('.', '_')
                dep_id = dep.replace('-', '_').replace('.', '_')
                mermaid.append(f"    {package_id} --> {dep_id}")
        
        return "\n".join(mermaid)


class PlantUMLGenerator:
    """Generate PlantUML diagrams"""
    
    def __init__(self):
        self.elements = []
    
    def generate_component_diagram(self, components: List[Dict]) -> str:
        """Generate component diagram"""
        plantuml = ["@startuml", ""]
        
        for component in components:
            name = component.get('name', 'Unknown')
            type_name = component.get('type', 'component')
            
            plantuml.append(f"{type_name} [{name}]")
            
            interfaces = component.get('interfaces', [])
            for interface in interfaces:
                plantuml.append(f"interface {interface}")
                plantuml.append(f"[{name}] --> {interface}")
        
        # Add dependencies
        for component in components:
            name = component.get('name', 'Unknown')
            dependencies = component.get('dependencies', [])
            
            for dep in dependencies:
                plantuml.append(f"[{name}] ..> [{dep}]")
        
        plantuml.append("")
        plantuml.append("@enduml")
        
        return "\n".join(plantuml)
    
    def generate_deployment_diagram(self, nodes: List[Dict]) -> str:
        """Generate deployment diagram"""
        plantuml = ["@startuml", ""]
        
        for node in nodes:
            node_name = node.get('name', 'Unknown')
            node_type = node.get('type', 'node')
            
            plantuml.append(f"{node_type} \"{node_name}\" {{")
            
            artifacts = node.get('artifacts', [])
            for artifact in artifacts:
                artifact_name = artifact.get('name', '')
                plantuml.append(f"  artifact \"{artifact_name}\"")
            
            plantuml.append("}")
        
        plantuml.append("")
        plantuml.append("@enduml")
        
        return "\n".join(plantuml)


class InteractiveAPIExplorer:
    """Generate interactive API documentation with live examples"""
    
    def __init__(self):
        self.endpoints = []
        self.models = []
    
    def generate_html_explorer(self, api_data: Dict) -> str:
        """Generate interactive HTML API explorer"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>API Explorer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; border-radius: 8px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .sidebar { position: fixed; left: 0; top: 0; width: 280px; height: 100vh; background: white; border-right: 1px solid #e0e0e0; overflow-y: auto; padding: 20px; }
        .content { margin-left: 300px; }
        .endpoint { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .method { display: inline-block; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 0.9em; margin-right: 10px; }
        .method.get { background: #61affe; color: white; }
        .method.post { background: #49cc90; color: white; }
        .method.put { background: #fca130; color: white; }
        .method.delete { background: #f93e3e; color: white; }
        .path { font-family: 'Courier New', monospace; font-size: 1.1em; color: #333; }
        .description { color: #666; margin: 15px 0; line-height: 1.6; }
        .params { margin: 20px 0; }
        .param { background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 3px solid #667eea; }
        .param-name { font-weight: bold; color: #333; }
        .param-type { color: #667eea; font-size: 0.9em; }
        .try-it { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-top: 15px; }
        .try-it:hover { background: #5568d3; }
        .response { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 4px; padding: 15px; margin-top: 15px; }
        .response-code { font-family: 'Courier New', monospace; font-size: 0.9em; color: #333; white-space: pre-wrap; }
        .nav-item { padding: 8px 12px; margin: 4px 0; border-radius: 4px; cursor: pointer; transition: background 0.2s; }
        .nav-item:hover { background: #f0f0f0; }
        .nav-method { font-weight: bold; margin-right: 8px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>Endpoints</h3>
        <div id="navigation"></div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🚀 API Explorer</h1>
            <p>Interactive documentation for your API</p>
        </div>
        
        <div class="content" id="endpoints"></div>
    </div>
    
    <script>
        const apiData = """ + json.dumps(api_data) + """;
        
        function renderEndpoints() {
            const nav = document.getElementById('navigation');
            const content = document.getElementById('endpoints');
            
            apiData.endpoints.forEach((endpoint, idx) => {
                // Render navigation
                const navItem = document.createElement('div');
                navItem.className = 'nav-item';
                navItem.innerHTML = `
                    <span class="nav-method" style="color: ${getMethodColor(endpoint.method)}">${endpoint.method}</span>
                    <span>${endpoint.path}</span>
                `;
                navItem.onclick = () => document.getElementById('endpoint-' + idx).scrollIntoView({ behavior: 'smooth' });
                nav.appendChild(navItem);
                
                // Render endpoint
                const endpointDiv = document.createElement('div');
                endpointDiv.id = 'endpoint-' + idx;
                endpointDiv.className = 'endpoint';
                endpointDiv.innerHTML = `
                    <div>
                        <span class="method ${endpoint.method.toLowerCase()}">${endpoint.method}</span>
                        <span class="path">${endpoint.path}</span>
                    </div>
                    <div class="description">${endpoint.description || 'No description available'}</div>
                    
                    ${endpoint.parameters && endpoint.parameters.length > 0 ? `
                        <div class="params">
                            <h4>Parameters</h4>
                            ${endpoint.parameters.map(param => `
                                <div class="param">
                                    <span class="param-name">${param.name}</span>
                                    <span class="param-type">${param.type}</span>
                                    ${param.required ? '<span style="color: red;">*</span>' : ''}
                                    <div style="color: #666; font-size: 0.9em; margin-top: 5px;">${param.description || ''}</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    <button class="try-it" onclick="tryEndpoint(${idx})">Try it out</button>
                    <div id="response-${idx}" class="response" style="display: none;">
                        <h4>Response</h4>
                        <pre class="response-code" id="response-code-${idx}"></pre>
                    </div>
                `;
                content.appendChild(endpointDiv);
            });
        }
        
        function getMethodColor(method) {
            const colors = {
                'GET': '#61affe',
                'POST': '#49cc90',
                'PUT': '#fca130',
                'DELETE': '#f93e3e'
            };
            return colors[method] || '#999';
        }
        
        function tryEndpoint(idx) {
            const endpoint = apiData.endpoints[idx];
            const responseDiv = document.getElementById('response-' + idx);
            const responseCode = document.getElementById('response-code-' + idx);
            
            responseDiv.style.display = 'block';
            responseCode.textContent = 'Loading...';
            
            // Simulate API call
            setTimeout(() => {
                const mockResponse = {
                    status: 200,
                    data: endpoint.exampleResponse || { message: 'Success' }
                };
                responseCode.textContent = JSON.stringify(mockResponse, null, 2);
            }, 500);
        }
        
        renderEndpoints();
    </script>
</body>
</html>"""
        return html


class VisualDocumentationSystem:
    """Main system for visual documentation generation"""
    
    def __init__(self):
        self.mermaid_gen = MermaidGenerator()
        self.plantuml_gen = PlantUMLGenerator()
        self.api_explorer = InteractiveAPIExplorer()
    
    def generate_diagram(self, diagram_type: str, data: Any, config: DiagramConfig) -> str:
        """Generate diagram based on type"""
        if diagram_type == "architecture":
            return self.mermaid_gen.generate_architecture_diagram(data, config)
        elif diagram_type == "class":
            return self.mermaid_gen.generate_class_diagram(data)
        elif diagram_type == "sequence":
            return self.mermaid_gen.generate_sequence_diagram(data)
        elif diagram_type == "flowchart":
            return self.mermaid_gen.generate_flowchart(data)
        elif diagram_type == "er":
            return self.mermaid_gen.generate_er_diagram(data)
        elif diagram_type == "state":
            return self.mermaid_gen.generate_state_diagram(data)
        elif diagram_type == "dependency":
            return self.mermaid_gen.generate_dependency_graph(data)
        elif diagram_type == "component":
            return self.plantuml_gen.generate_component_diagram(data)
        elif diagram_type == "deployment":
            return self.plantuml_gen.generate_deployment_diagram(data)
        else:
            raise ValueError(f"Unknown diagram type: {diagram_type}")
    
    def analyze_code_for_diagrams(self, repo_path: str) -> Dict[str, List]:
        """Analyze code repository to extract data for diagram generation"""
        results = {
            'classes': [],
            'functions': [],
            'dependencies': {},
            'files': []
        }
        
        repo_path = Path(repo_path)
        
        # Find Python files
        for py_file in repo_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                file_info = {
                    'path': str(py_file.relative_to(repo_path)),
                    'classes': [],
                    'functions': []
                }
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        file_info['classes'].append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        file_info['functions'].append(node.name)
                
                results['files'].append(file_info)
                
            except Exception:
                continue
        
        return results
    
    def export_diagram(self, diagram_content: str, output_path: str, format_type: str = "html"):
        """Export diagram to file"""
        output_path = Path(output_path)
        
        if format_type == "html":
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Diagram</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</head>
<body>
    <div class="mermaid">
{diagram_content}
    </div>
</body>
</html>"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        elif format_type == "md":
            md_content = f"""# Diagram

```mermaid
{diagram_content}
```
"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
        
        else:  # plain text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(diagram_content)


def main():
    """CLI entry point for visual documentation tools"""
    parser = argparse.ArgumentParser(
        description="Generate visual documentation diagrams"
    )
    
    parser.add_argument('command', choices=[
        'diagram', 'api-explorer', 'analyze', 'export'
    ], help='Command to execute')
    
    parser.add_argument('--type', '-t', 
                       choices=['architecture', 'class', 'sequence', 'flowchart', 
                               'er', 'state', 'dependency', 'component', 'deployment'],
                       help='Diagram type')
    
    parser.add_argument('--input', '-i', help='Input file or directory')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['html', 'md', 'txt', 'svg', 'png'],
                       default='html', help='Output format')
    parser.add_argument('--theme', choices=['default', 'dark', 'forest', 'neutral'],
                       default='default', help='Diagram theme')
    parser.add_argument('--direction', choices=['TB', 'LR', 'RL', 'BT'],
                       default='TB', help='Diagram direction')
    
    args = parser.parse_args()
    
    system = VisualDocumentationSystem()
    
    try:
        if args.command == 'diagram':
            if not args.input or not args.type:
                print("Error: --input and --type required for diagram generation")
                return 1
            
            config = DiagramConfig(
                diagram_type=args.type,
                output_format=args.format,
                theme=args.theme,
                direction=args.direction
            )
            
            # Load input data
            if Path(args.input).is_file():
                with open(args.input, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Analyze directory
                data = system.analyze_code_for_diagrams(args.input)
            
            diagram = system.generate_diagram(args.type, data, config)
            
            if args.output:
                system.export_diagram(diagram, args.output, args.format)
                print(f"✓ Diagram exported to {args.output}")
            else:
                print(diagram)
        
        elif args.command == 'api-explorer':
            if not args.input:
                print("Error: --input required for API explorer")
                return 1
            
            with open(args.input, 'r', encoding='utf-8') as f:
                api_data = json.load(f)
            
            html = system.api_explorer.generate_html_explorer(api_data)
            
            output_path = args.output or 'api-explorer.html'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"✓ API Explorer generated: {output_path}")
        
        elif args.command == 'analyze':
            if not args.input:
                print("Error: --input required for analysis")
                return 1
            
            results = system.analyze_code_for_diagrams(args.input)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                print(f"✓ Analysis saved to {args.output}")
            else:
                print(json.dumps(results, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
