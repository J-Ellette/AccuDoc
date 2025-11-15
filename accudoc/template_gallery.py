"""
Templates gallery system for AccuDoc.

Browse, preview, and select from available documentation templates.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class TemplateInfo:
    """Information about a documentation template."""
    
    id: str
    name: str
    description: str
    category: str
    author: str = "AccuDoc Team"
    version: str = "1.0.0"
    tags: List[str] = None
    preview: str = ""
    use_cases: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.use_cases is None:
            self.use_cases = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TemplateInfo':
        """Create from dictionary."""
        return cls(**data)


class TemplateGallery:
    """
    Template gallery for browsing and selecting documentation templates.
    
    Provides a searchable catalog of available templates with previews.
    """
    
    # Built-in template definitions
    BUILTIN_TEMPLATES = {
        'default': TemplateInfo(
            id='default',
            name='Complete Documentation',
            description='Comprehensive documentation with all available sections',
            category='General',
            tags=['comprehensive', 'complete', 'detailed'],
            preview='Includes: Overview, Features, Installation, Usage, Architecture, API, Contributing, License',
            use_cases=[
                'Production-ready projects',
                'Open source repositories',
                'Enterprise applications'
            ]
        ),
        'minimal': TemplateInfo(
            id='minimal',
            name='Minimal README',
            description='Essential sections only - quick and concise',
            category='General',
            tags=['minimal', 'quick', 'simple'],
            preview='Includes: Project name, Description, Installation, Usage',
            use_cases=[
                'Small utilities',
                'Personal projects',
                'Quick prototypes'
            ]
        ),
        'detailed': TemplateInfo(
            id='detailed',
            name='Detailed Technical Documentation',
            description='In-depth technical documentation for complex projects',
            category='Technical',
            tags=['detailed', 'technical', 'comprehensive'],
            preview='Includes: Architecture, Design Patterns, Code Analysis, Dependencies, Best Practices',
            use_cases=[
                'Large-scale applications',
                'Complex architectures',
                'Technical deep dives'
            ]
        ),
        'api': TemplateInfo(
            id='api',
            name='API Reference',
            description='Focus on API documentation and usage examples',
            category='Technical',
            tags=['api', 'reference', 'documentation'],
            preview='Includes: API endpoints, Functions, Classes, Parameters, Return values, Examples',
            use_cases=[
                'Libraries and SDKs',
                'REST APIs',
                'Developer tools'
            ]
        ),
        'readme': TemplateInfo(
            id='readme',
            name='GitHub README Style',
            description='GitHub-style README with badges and sections',
            category='General',
            tags=['github', 'readme', 'badges'],
            preview='Includes: Badges, Features list, Installation, Usage, Contributing, License',
            use_cases=[
                'GitHub projects',
                'Open source',
                'Community projects'
            ]
        ),
        'student': TemplateInfo(
            id='student',
            name='Student Project Report',
            description='Academic project documentation template',
            category='Academic',
            tags=['academic', 'student', 'educational'],
            preview='Includes: Learning objectives, Requirements, Implementation, Testing, Deliverables',
            use_cases=[
                'Course projects',
                'Academic assignments',
                'Educational repositories'
            ]
        )
    }
    
    def __init__(self, custom_templates_dir: Optional[str] = None):
        """
        Initialize template gallery.
        
        Args:
            custom_templates_dir: Optional directory for custom templates
        """
        self.templates: Dict[str, TemplateInfo] = self.BUILTIN_TEMPLATES.copy()
        self.custom_dir = Path(custom_templates_dir) if custom_templates_dir else None
        
        if self.custom_dir and self.custom_dir.exists():
            self._load_custom_templates()
    
    def _load_custom_templates(self):
        """Load custom templates from directory."""
        if not self.custom_dir:
            return
        
        for template_file in self.custom_dir.glob('*.json'):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template_info = TemplateInfo.from_dict(data)
                    self.templates[template_info.id] = template_info
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
    
    def list_all(self) -> List[TemplateInfo]:
        """
        Get all available templates.
        
        Returns:
            List of TemplateInfo objects
        """
        return list(self.templates.values())
    
    def get_template(self, template_id: str) -> Optional[TemplateInfo]:
        """
        Get information about a specific template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            TemplateInfo or None if not found
        """
        return self.templates.get(template_id)
    
    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[TemplateInfo]:
        """
        Search for templates.
        
        Args:
            query: Search query (matches name/description)
            category: Filter by category
            tags: Filter by tags
            
        Returns:
            List of matching TemplateInfo objects
        """
        results = list(self.templates.values())
        
        # Filter by query
        if query:
            query = query.lower()
            results = [
                t for t in results
                if query in t.name.lower() or query in t.description.lower()
            ]
        
        # Filter by category
        if category:
            results = [t for t in results if t.category.lower() == category.lower()]
        
        # Filter by tags
        if tags:
            results = [
                t for t in results
                if any(tag.lower() in [tt.lower() for tt in t.tags] for tag in tags)
            ]
        
        return results
    
    def list_categories(self) -> List[str]:
        """
        Get all unique categories.
        
        Returns:
            List of category names
        """
        return sorted(set(t.category for t in self.templates.values()))
    
    def list_tags(self) -> List[str]:
        """
        Get all unique tags.
        
        Returns:
            List of tags
        """
        all_tags = []
        for template in self.templates.values():
            all_tags.extend(template.tags)
        return sorted(set(all_tags))
    
    def get_by_category(self, category: str) -> List[TemplateInfo]:
        """
        Get templates in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of TemplateInfo objects
        """
        return [t for t in self.templates.values() if t.category.lower() == category.lower()]
    
    def format_template_list(self, templates: Optional[List[TemplateInfo]] = None) -> str:
        """
        Format templates as a human-readable list.
        
        Args:
            templates: Optional list of templates (defaults to all)
            
        Returns:
            Formatted string
        """
        if templates is None:
            templates = self.list_all()
        
        if not templates:
            return "No templates found."
        
        lines = []
        lines.append("=" * 70)
        lines.append("Available Documentation Templates")
        lines.append("=" * 70)
        lines.append("")
        
        # Group by category
        by_category = {}
        for template in templates:
            if template.category not in by_category:
                by_category[template.category] = []
            by_category[template.category].append(template)
        
        for category in sorted(by_category.keys()):
            lines.append(f"\n{category} Templates")
            lines.append("-" * 70)
            
            for template in sorted(by_category[category], key=lambda t: t.name):
                lines.append(f"\n📄 {template.name} ({template.id})")
                lines.append(f"   {template.description}")
                if template.tags:
                    lines.append(f"   Tags: {', '.join(template.tags)}")
                lines.append(f"   {template.preview}")
        
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)
    
    def format_template_detail(self, template_id: str) -> str:
        """
        Format detailed information about a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Formatted string
        """
        template = self.get_template(template_id)
        if not template:
            return f"Template '{template_id}' not found."
        
        lines = []
        lines.append("=" * 70)
        lines.append(f"Template: {template.name}")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"ID: {template.id}")
        lines.append(f"Category: {template.category}")
        lines.append(f"Author: {template.author}")
        lines.append(f"Version: {template.version}")
        lines.append("")
        lines.append(f"Description:")
        lines.append(f"  {template.description}")
        lines.append("")
        
        if template.tags:
            lines.append(f"Tags: {', '.join(template.tags)}")
            lines.append("")
        
        lines.append("Preview:")
        lines.append(f"  {template.preview}")
        lines.append("")
        
        if template.use_cases:
            lines.append("Best suited for:")
            for use_case in template.use_cases:
                lines.append(f"  • {use_case}")
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def export_catalog(self, output_path: str, format: str = 'json'):
        """
        Export template catalog to file.
        
        Args:
            output_path: Output file path
            format: Export format (json, markdown)
        """
        if format == 'json':
            data = {
                'templates': [t.to_dict() for t in self.templates.values()],
                'categories': self.list_categories(),
                'tags': self.list_tags()
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        elif format == 'markdown':
            content = self.format_template_list()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)


def get_gallery() -> TemplateGallery:
    """
    Get the default template gallery instance.
    
    Returns:
        TemplateGallery instance
    """
    return TemplateGallery()
