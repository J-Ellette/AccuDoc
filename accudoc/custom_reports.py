"""
Custom Reports module for AccuDoc.
Allows users to create custom report templates and generate reports.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import re
from datetime import datetime


class ReportTemplate:
    """Represents a custom report template."""
    
    def __init__(self, template_data: Dict):
        """
        Initialize report template.
        
        Args:
            template_data: Template configuration dictionary
        """
        self.template_data = template_data
        self.name = template_data.get('name', 'Unnamed Template')
        self.description = template_data.get('description', '')
        self.sections = template_data.get('sections', [])
        self.format = template_data.get('format', 'markdown')
        self.variables = template_data.get('variables', {})
    
    def validate(self) -> List[str]:
        """
        Validate template configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if 'name' not in self.template_data or not self.template_data['name']:
            errors.append("Template must have a name")
        
        if not self.sections:
            errors.append("Template must have at least one section")
        
        for i, section in enumerate(self.sections):
            if 'title' not in section:
                errors.append(f"Section {i} missing 'title' field")
            
            if 'content' not in section and 'data' not in section:
                errors.append(f"Section {i} must have either 'content' or 'data' field")
        
        return errors


class CustomReportGenerator:
    """Generates custom reports based on templates."""
    
    # Built-in templates
    BUILTIN_TEMPLATES = {
        'minimal': {
            'name': 'Minimal Report',
            'description': 'Essential project information only',
            'format': 'markdown',
            'sections': [
                {
                    'title': 'Project Overview',
                    'data': ['name', 'path', 'files_count', 'languages']
                },
                {
                    'title': 'Statistics',
                    'data': ['statistics.total_lines', 'statistics.code_lines', 'statistics.comment_lines']
                }
            ]
        },
        'detailed': {
            'name': 'Detailed Report',
            'description': 'Comprehensive project analysis',
            'format': 'markdown',
            'sections': [
                {
                    'title': 'Project Information',
                    'data': ['name', 'path', 'files_count', 'languages', 'license']
                },
                {
                    'title': 'Code Statistics',
                    'data': ['statistics']
                },
                {
                    'title': 'Dependencies',
                    'data': ['dependencies']
                },
                {
                    'title': 'Documentation',
                    'data': ['documentation', 'api_docs', 'code_examples']
                },
                {
                    'title': 'Tasks',
                    'data': ['todos']
                }
            ]
        },
        'executive': {
            'name': 'Executive Summary',
            'description': 'High-level overview for stakeholders',
            'format': 'markdown',
            'sections': [
                {
                    'title': 'Executive Summary',
                    'content': 'Project: {name}\nTotal Files: {files_count}\nPrimary Languages: {languages_list}'
                },
                {
                    'title': 'Key Metrics',
                    'data': ['files_count', 'statistics.total_lines', 'dependencies_count', 'license']
                },
                {
                    'title': 'Health Score',
                    'data': ['health_score']
                }
            ]
        },
        'technical': {
            'name': 'Technical Deep Dive',
            'description': 'In-depth technical analysis',
            'format': 'markdown',
            'sections': [
                {
                    'title': 'Architecture',
                    'data': ['languages', 'file_structure']
                },
                {
                    'title': 'Code Quality',
                    'data': ['statistics', 'todos', 'complexity']
                },
                {
                    'title': 'Dependencies',
                    'data': ['dependencies']
                },
                {
                    'title': 'Test Coverage',
                    'data': ['test_files', 'coverage']
                }
            ]
        }
    }
    
    def __init__(self, repo_info: Dict):
        """
        Initialize custom report generator.
        
        Args:
            repo_info: Repository information from scanner
        """
        self.repo_info = repo_info
    
    def load_template(self, template_path: str) -> ReportTemplate:
        """
        Load template from JSON file.
        
        Args:
            template_path: Path to template JSON file
            
        Returns:
            ReportTemplate object
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        return ReportTemplate(template_data)
    
    def get_builtin_template(self, template_name: str) -> ReportTemplate:
        """
        Get a built-in template.
        
        Args:
            template_name: Name of built-in template
            
        Returns:
            ReportTemplate object
        """
        if template_name not in self.BUILTIN_TEMPLATES:
            raise ValueError(f"Unknown built-in template: {template_name}")
        
        return ReportTemplate(self.BUILTIN_TEMPLATES[template_name])
    
    def list_builtin_templates(self) -> List[Dict[str, str]]:
        """
        List available built-in templates.
        
        Returns:
            List of template info dictionaries
        """
        templates = []
        for name, data in self.BUILTIN_TEMPLATES.items():
            templates.append({
                'name': name,
                'title': data['name'],
                'description': data['description']
            })
        return templates
    
    def generate(self, template: ReportTemplate) -> str:
        """
        Generate report from template.
        
        Args:
            template: ReportTemplate object
            
        Returns:
            Generated report as string
        """
        # Validate template
        errors = template.validate()
        if errors:
            raise ValueError(f"Template validation failed: {', '.join(errors)}")
        
        # Prepare context with repository data
        context = self._prepare_context()
        
        # Generate report sections
        sections = []
        for section in template.sections:
            section_content = self._generate_section(section, context)
            sections.append(section_content)
        
        # Combine sections based on format
        if template.format == 'markdown':
            return self._format_markdown(template.name, sections)
        elif template.format == 'html':
            return self._format_html(template.name, sections)
        elif template.format == 'text':
            return self._format_text(template.name, sections)
        else:
            return '\n\n'.join(sections)
    
    def _prepare_context(self) -> Dict:
        """Prepare context with all available data."""
        context = self.repo_info.copy()
        
        # Add computed fields
        context['languages_list'] = ', '.join(list(context.get('languages', {}).keys())[:3])
        
        deps = context.get('dependencies', {})
        context['dependencies_count'] = sum(len(d) if isinstance(d, list) else 0 for d in deps.values())
        
        # Add timestamp
        context['generated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Try to get health score if available
        try:
            from accudoc.health_dashboard import HealthMetrics
            metrics = HealthMetrics(self.repo_info)
            summary = metrics.get_summary()
            context['health_score'] = summary['overall_score']
            context['health_grade'] = summary['overall_grade']
        except Exception:
            context['health_score'] = 'N/A'
            context['health_grade'] = 'N/A'
        
        return context
    
    def _generate_section(self, section: Dict, context: Dict) -> str:
        """Generate a single section."""
        title = section.get('title', 'Untitled Section')
        lines = [f"## {title}", ""]
        
        # Handle content template
        if 'content' in section:
            content = section['content']
            # Replace variables
            content = self._replace_variables(content, context)
            lines.append(content)
        
        # Handle data fields
        elif 'data' in section:
            data_fields = section['data']
            for field in data_fields:
                value = self._get_nested_value(context, field)
                if value is not None:
                    lines.append(self._format_field(field, value))
        
        return '\n'.join(lines)
    
    def _replace_variables(self, text: str, context: Dict) -> str:
        """Replace variables in text with values from context."""
        # Find all {variable} patterns
        pattern = r'\{([^}]+)\}'
        
        def replace(match):
            var_name = match.group(1)
            value = self._get_nested_value(context, var_name)
            return str(value) if value is not None else f"{{{var_name}}}"
        
        return re.sub(pattern, replace, text)
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _format_field(self, field: str, value: Any) -> str:
        """Format a field and its value."""
        # Format field name
        field_name = field.split('.')[-1].replace('_', ' ').title()
        
        # Format value based on type
        if isinstance(value, dict):
            lines = [f"**{field_name}:**"]
            for k, v in value.items():
                if isinstance(v, (int, str, float)):
                    lines.append(f"  - {k}: {v}")
            return '\n'.join(lines)
        
        elif isinstance(value, list):
            if not value:
                return f"**{field_name}:** None"
            
            lines = [f"**{field_name}:**"]
            for item in value[:10]:  # Limit to first 10 items
                if isinstance(item, dict):
                    item_str = ', '.join(f"{k}: {v}" for k, v in item.items())
                    lines.append(f"  - {item_str}")
                else:
                    lines.append(f"  - {item}")
            
            if len(value) > 10:
                lines.append(f"  ... and {len(value) - 10} more")
            
            return '\n'.join(lines)
        
        else:
            return f"**{field_name}:** {value}"
    
    def _format_markdown(self, title: str, sections: List[str]) -> str:
        """Format report as Markdown."""
        lines = [
            f"# {title}",
            "",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "---",
            ""
        ]
        
        lines.extend([section for section in sections])
        
        return '\n'.join(lines)
    
    def _format_html(self, title: str, sections: List[str]) -> str:
        """Format report as HTML."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        .timestamp {{ color: #888; font-style: italic; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <hr>
"""
        
        # Convert markdown sections to HTML (simple conversion)
        for section in sections:
            # Convert ## to h2
            section = re.sub(r'^## (.+)$', r'<h2>\1</h2>', section, flags=re.MULTILINE)
            # Convert **text** to <strong>
            section = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', section)
            # Convert - to <li>
            section = re.sub(r'^  - (.+)$', r'<li>\1</li>', section, flags=re.MULTILINE)
            
            html += f"    <div>{section}</div>\n"
        
        html += """</body>
</html>"""
        
        return html
    
    def _format_text(self, title: str, sections: List[str]) -> str:
        """Format report as plain text."""
        lines = [
            "=" * 70,
            title.upper(),
            "=" * 70,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "-" * 70,
            ""
        ]
        
        for section in sections:
            # Remove markdown formatting
            section = re.sub(r'##\s+', '', section)
            section = re.sub(r'\*\*(.+?)\*\*', r'\1', section)
            lines.append(section)
            lines.append("")
        
        return '\n'.join(lines)
    
    def save_template(self, template: ReportTemplate, output_path: str):
        """
        Save template to JSON file.
        
        Args:
            template: ReportTemplate object
            output_path: Path to save template
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template.template_data, f, indent=2)


def create_sample_template(template_type: str = 'basic') -> Dict:
    """
    Create a sample template.
    
    Args:
        template_type: Type of sample template
        
    Returns:
        Template configuration dictionary
    """
    if template_type == 'basic':
        return {
            'name': 'Basic Custom Report',
            'description': 'A basic custom report template',
            'format': 'markdown',
            'sections': [
                {
                    'title': 'Project Information',
                    'content': 'Repository: {name}\nPath: {path}\nGenerated: {generated_date}'
                },
                {
                    'title': 'Overview',
                    'data': ['files_count', 'languages', 'license']
                }
            ]
        }
    elif template_type == 'comprehensive':
        return {
            'name': 'Comprehensive Report',
            'description': 'Complete project analysis',
            'format': 'markdown',
            'sections': [
                {
                    'title': 'Project Overview',
                    'data': ['name', 'path', 'files_count']
                },
                {
                    'title': 'Languages & Statistics',
                    'data': ['languages', 'statistics']
                },
                {
                    'title': 'Dependencies & Documentation',
                    'data': ['dependencies', 'documentation']
                }
            ]
        }
    else:
        return create_sample_template('basic')
