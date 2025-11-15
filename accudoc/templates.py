"""Template system for customizable documentation generation."""

from typing import Dict, List, Optional, Callable
from pathlib import Path
import json


class DocumentTemplate:
    """Base class for documentation templates."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize template.
        
        Args:
            name: Template name
            description: Template description
        """
        self.name = name
        self.description = description
        self.sections = []
    
    def add_section(self, section_name: str, generator_method: str, 
                   enabled: bool = True, order: int = 0):
        """
        Add a section to the template.
        
        Args:
            section_name: Display name of the section
            generator_method: Name of the generator method to call
            enabled: Whether this section is enabled by default
            order: Sort order for the section
        """
        self.sections.append({
            'name': section_name,
            'method': generator_method,
            'enabled': enabled,
            'order': order
        })
    
    def get_sections(self) -> List[Dict]:
        """Get ordered list of enabled sections."""
        return sorted(
            [s for s in self.sections if s['enabled']], 
            key=lambda x: x['order']
        )


class TemplateManager:
    """Manages documentation templates."""
    
    # Built-in templates
    BUILTIN_TEMPLATES = {
        'default': {
            'name': 'Default',
            'description': 'Complete documentation with all sections',
            'sections': [
                ('header', '_generate_header', 0),
                ('overview', '_generate_overview', 10),
                ('features', '_generate_features', 20),
                ('technology_stack', '_generate_technology_stack', 30),
                ('frameworks', '_generate_frameworks', 40),
                ('architecture', '_generate_architecture_diagram', 50),
                ('dependencies', '_generate_dependency_graph', 60),
                ('installation', '_generate_installation', 70),
                ('usage', '_generate_usage', 80),
                ('configuration', '_generate_configuration_files', 90),
                ('environment', '_generate_environment_variables', 100),
                ('api_docs', '_generate_api_documentation', 110),
                ('type_info', '_generate_type_information', 120),
                ('imports', '_generate_import_analysis', 130),
                ('examples', '_generate_code_examples', 140),
                ('structure', '_generate_project_structure', 150),
                ('statistics', '_generate_code_statistics', 160),
                ('todos', '_generate_todos', 170),
                ('changelog', '_generate_changelog', 180),
                ('contributors', '_generate_contributors', 190),
                ('license', '_generate_license_section', 200),
                ('footer', '_generate_footer', 210),
            ]
        },
        'minimal': {
            'name': 'Minimal',
            'description': 'Essential documentation only',
            'sections': [
                ('header', '_generate_header', 0),
                ('overview', '_generate_overview', 10),
                ('installation', '_generate_installation', 20),
                ('usage', '_generate_usage', 30),
                ('license', '_generate_license_section', 40),
                ('footer', '_generate_footer', 50),
            ]
        },
        'detailed': {
            'name': 'Detailed',
            'description': 'Comprehensive technical documentation',
            'sections': [
                ('header', '_generate_header', 0),
                ('overview', '_generate_overview', 10),
                ('features', '_generate_features', 20),
                ('technology_stack', '_generate_technology_stack', 30),
                ('frameworks', '_generate_frameworks', 40),
                ('architecture', '_generate_architecture_diagram', 50),
                ('dependencies', '_generate_dependency_graph', 60),
                ('api_docs', '_generate_api_documentation', 70),
                ('type_info', '_generate_type_information', 80),
                ('imports', '_generate_import_analysis', 90),
                ('code_statistics', '_generate_code_statistics', 100),
                ('structure', '_generate_project_structure', 110),
                ('configuration', '_generate_configuration_files', 120),
                ('environment', '_generate_environment_variables', 130),
                ('examples', '_generate_code_examples', 140),
                ('installation', '_generate_installation', 150),
                ('usage', '_generate_usage', 160),
                ('todos', '_generate_todos', 170),
                ('changelog', '_generate_changelog', 180),
                ('contributors', '_generate_contributors', 190),
                ('license', '_generate_license_section', 200),
                ('footer', '_generate_footer', 210),
            ]
        },
        'api': {
            'name': 'API Reference',
            'description': 'Focus on API documentation',
            'sections': [
                ('header', '_generate_header', 0),
                ('overview', '_generate_overview', 10),
                ('installation', '_generate_installation', 20),
                ('api_docs', '_generate_api_documentation', 30),
                ('type_info', '_generate_type_information', 40),
                ('imports', '_generate_import_analysis', 50),
                ('examples', '_generate_code_examples', 60),
                ('license', '_generate_license_section', 70),
                ('footer', '_generate_footer', 80),
            ]
        },
        'readme': {
            'name': 'README Style',
            'description': 'GitHub README style documentation',
            'sections': [
                ('header', '_generate_header', 0),
                ('overview', '_generate_overview', 10),
                ('features', '_generate_features', 20),
                ('installation', '_generate_installation', 30),
                ('usage', '_generate_usage', 40),
                ('examples', '_generate_code_examples', 50),
                ('contributors', '_generate_contributors', 60),
                ('license', '_generate_license_section', 70),
                ('footer', '_generate_footer', 80),
            ]
        },
        'student': {
            'name': 'Student Project',
            'description': 'Template for student and academic projects',
            'sections': [
                ('header', '_generate_header', 0),
                ('student_info', '_generate_student_info', 5),
                ('overview', '_generate_overview', 10),
                ('learning_objectives', '_generate_learning_objectives', 15),
                ('requirements', '_generate_assignment_requirements', 20),
                ('features', '_generate_features', 30),
                ('technology_stack', '_generate_technology_stack', 40),
                ('installation', '_generate_installation', 50),
                ('usage', '_generate_usage', 60),
                ('project_structure', '_generate_project_structure', 70),
                ('examples', '_generate_code_examples', 80),
                ('testing', '_generate_testing_section', 90),
                ('deliverables', '_generate_deliverables', 100),
                ('resources', '_generate_resources', 110),
                ('acknowledgments', '_generate_acknowledgments', 120),
                ('license', '_generate_license_section', 130),
            ]
        }
    }
    
    def __init__(self):
        """Initialize template manager."""
        self.custom_templates = {}
    
    def get_template(self, template_name: str) -> DocumentTemplate:
        """
        Get a template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            DocumentTemplate instance
            
        Raises:
            ValueError: If template not found
        """
        # Check built-in templates
        if template_name in self.BUILTIN_TEMPLATES:
            return self._build_template(
                template_name,
                self.BUILTIN_TEMPLATES[template_name]
            )
        
        # Check custom templates
        if template_name in self.custom_templates:
            return self._build_template(
                template_name,
                self.custom_templates[template_name]
            )
        
        raise ValueError(f"Template '{template_name}' not found")
    
    def _build_template(self, name: str, config: Dict) -> DocumentTemplate:
        """Build a DocumentTemplate from configuration."""
        template = DocumentTemplate(
            name=config['name'],
            description=config['description']
        )
        
        for section_name, method, order in config['sections']:
            template.add_section(section_name, method, True, order)
        
        return template
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        List all available templates.
        
        Returns:
            List of template info dictionaries
        """
        templates = []
        
        # Add built-in templates
        for key, config in self.BUILTIN_TEMPLATES.items():
            templates.append({
                'id': key,
                'name': config['name'],
                'description': config['description'],
                'type': 'builtin'
            })
        
        # Add custom templates
        for key, config in self.custom_templates.items():
            templates.append({
                'id': key,
                'name': config['name'],
                'description': config['description'],
                'type': 'custom'
            })
        
        return templates
    
    def load_custom_template(self, template_path: str) -> str:
        """
        Load a custom template from a JSON file.
        
        Args:
            template_path: Path to template JSON file
            
        Returns:
            Template ID
            
        Raises:
            ValueError: If template file is invalid
        """
        path = Path(template_path)
        if not path.exists():
            raise ValueError(f"Template file not found: {template_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate required fields
            required_fields = ['id', 'name', 'description', 'sections']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate sections format
            if not isinstance(config['sections'], list):
                raise ValueError("'sections' must be a list")
            
            for section in config['sections']:
                if not isinstance(section, list) or len(section) != 3:
                    raise ValueError("Each section must be [name, method, order]")
            
            # Store custom template
            template_id = config['id']
            self.custom_templates[template_id] = config
            
            return template_id
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template file: {e}")
    
    def save_custom_template(self, template: DocumentTemplate, 
                            template_id: str, output_path: str):
        """
        Save a custom template to a JSON file.
        
        Args:
            template: DocumentTemplate to save
            template_id: Unique ID for the template
            output_path: Path to save the template file
        """
        config = {
            'id': template_id,
            'name': template.name,
            'description': template.description,
            'sections': [
                (s['name'], s['method'], s['order']) 
                for s in template.sections
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def create_custom_template(self, template_id: str, name: str, 
                              description: str, sections: List[tuple]) -> DocumentTemplate:
        """
        Create a new custom template.
        
        Args:
            template_id: Unique ID for the template
            name: Display name
            description: Template description
            sections: List of (section_name, method_name, order) tuples
            
        Returns:
            Created DocumentTemplate
        """
        config = {
            'id': template_id,
            'name': name,
            'description': description,
            'sections': sections
        }
        
        self.custom_templates[template_id] = config
        return self._build_template(template_id, config)
