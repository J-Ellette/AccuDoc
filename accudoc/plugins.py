"""
Plugin system for AccuDoc.

Allows community to extend AccuDoc with custom analyzers, exporters,
and documentation generators.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional
from abc import ABC, abstractmethod


class PluginInterface(ABC):
    """Base interface for all AccuDoc plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass


class AnalyzerPlugin(PluginInterface):
    """Base class for analyzer plugins."""
    
    @abstractmethod
    def analyze(self, file_path: Path, content: str) -> Dict:
        """
        Analyze a file.
        
        Args:
            file_path: Path to file
            content: File content
            
        Returns:
            Analysis results
        """
        pass
    
    @abstractmethod
    def supports_file(self, file_path: Path) -> bool:
        """
        Check if this analyzer supports the file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported
        """
        pass


class ExporterPlugin(PluginInterface):
    """Base class for exporter plugins."""
    
    @abstractmethod
    def export(self, content: str, output_path: Path, **kwargs) -> Path:
        """
        Export documentation to a format.
        
        Args:
            content: Documentation content
            output_path: Output file path
            **kwargs: Additional export options
            
        Returns:
            Path to exported file
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get file extension for this format.
        
        Returns:
            File extension (e.g., '.pdf')
        """
        pass


class TemplatePlugin(PluginInterface):
    """Base class for template plugins."""
    
    @abstractmethod
    def get_sections(self) -> List[Dict]:
        """
        Get template sections.
        
        Returns:
            List of section definitions
        """
        pass
    
    @abstractmethod
    def generate_section(self, section_name: str, repo_info: Dict) -> str:
        """
        Generate a specific section.
        
        Args:
            section_name: Section name
            repo_info: Repository information
            
        Returns:
            Generated section content
        """
        pass


class PluginManager:
    """Manages AccuDoc plugins."""
    
    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """
        Initialize plugin manager.
        
        Args:
            plugin_dirs: Directories to search for plugins
        """
        self.logger = logging.getLogger('accudoc.plugins')
        self.plugin_dirs = plugin_dirs or []
        
        # Add default plugin directory
        default_plugin_dir = Path.home() / '.accudoc' / 'plugins'
        if default_plugin_dir.exists():
            self.plugin_dirs.append(default_plugin_dir)
        
        self.analyzers = {}
        self.exporters = {}
        self.templates = {}
        
        # Load built-in plugins
        self._load_builtin_plugins()
        
        # Load external plugins
        self._load_external_plugins()
    
    def _load_builtin_plugins(self):
        """Load built-in plugins."""
        # Built-in plugins can be registered here
        pass
    
    def _load_external_plugins(self):
        """Load external plugins from plugin directories."""
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            for plugin_file in plugin_dir.glob('*.py'):
                if plugin_file.name.startswith('_'):
                    continue
                
                try:
                    self._load_plugin_file(plugin_file)
                except Exception as e:
                    self.logger.error(f"Failed to load plugin {plugin_file}: {str(e)}")
    
    def _load_plugin_file(self, plugin_file: Path):
        """
        Load a plugin from a file.
        
        Args:
            plugin_file: Path to plugin file
        """
        # Import the module
        spec = importlib.util.spec_from_file_location(
            plugin_file.stem,
            plugin_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find plugin classes
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if issubclass(obj, AnalyzerPlugin) and obj != AnalyzerPlugin:
                    self._register_analyzer(obj)
                elif issubclass(obj, ExporterPlugin) and obj != ExporterPlugin:
                    self._register_exporter(obj)
                elif issubclass(obj, TemplatePlugin) and obj != TemplatePlugin:
                    self._register_template(obj)
    
    def _register_analyzer(self, analyzer_class):
        """Register an analyzer plugin."""
        try:
            analyzer = analyzer_class()
            self.analyzers[analyzer.name] = analyzer
            self.logger.info(f"Registered analyzer plugin: {analyzer.name} v{analyzer.version}")
        except Exception as e:
            self.logger.error(f"Failed to register analyzer {analyzer_class}: {str(e)}")
    
    def _register_exporter(self, exporter_class):
        """Register an exporter plugin."""
        try:
            exporter = exporter_class()
            self.exporters[exporter.name] = exporter
            self.logger.info(f"Registered exporter plugin: {exporter.name} v{exporter.version}")
        except Exception as e:
            self.logger.error(f"Failed to register exporter {exporter_class}: {str(e)}")
    
    def _register_template(self, template_class):
        """Register a template plugin."""
        try:
            template = template_class()
            self.templates[template.name] = template
            self.logger.info(f"Registered template plugin: {template.name} v{template.version}")
        except Exception as e:
            self.logger.error(f"Failed to register template {template_class}: {str(e)}")
    
    def register_analyzer(self, analyzer: AnalyzerPlugin):
        """
        Manually register an analyzer plugin.
        
        Args:
            analyzer: Analyzer plugin instance
        """
        self.analyzers[analyzer.name] = analyzer
        self.logger.info(f"Manually registered analyzer: {analyzer.name}")
    
    def register_exporter(self, exporter: ExporterPlugin):
        """
        Manually register an exporter plugin.
        
        Args:
            exporter: Exporter plugin instance
        """
        self.exporters[exporter.name] = exporter
        self.logger.info(f"Manually registered exporter: {exporter.name}")
    
    def register_template(self, template: TemplatePlugin):
        """
        Manually register a template plugin.
        
        Args:
            template: Template plugin instance
        """
        self.templates[template.name] = template
        self.logger.info(f"Manually registered template: {template.name}")
    
    def get_analyzer(self, name: str) -> Optional[AnalyzerPlugin]:
        """Get an analyzer plugin by name."""
        return self.analyzers.get(name)
    
    def get_exporter(self, name: str) -> Optional[ExporterPlugin]:
        """Get an exporter plugin by name."""
        return self.exporters.get(name)
    
    def get_template(self, name: str) -> Optional[TemplatePlugin]:
        """Get a template plugin by name."""
        return self.templates.get(name)
    
    def get_analyzers_for_file(self, file_path: Path) -> List[AnalyzerPlugin]:
        """
        Get all analyzers that support a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of compatible analyzers
        """
        return [
            analyzer for analyzer in self.analyzers.values()
            if analyzer.supports_file(file_path)
        ]
    
    def list_plugins(self) -> Dict[str, List[str]]:
        """
        List all loaded plugins.
        
        Returns:
            Dictionary of plugin types and names
        """
        return {
            'analyzers': list(self.analyzers.keys()),
            'exporters': list(self.exporters.keys()),
            'templates': list(self.templates.keys())
        }
    
    def get_plugin_info(self) -> List[Dict]:
        """
        Get detailed information about all plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        info = []
        
        for analyzer in self.analyzers.values():
            info.append({
                'type': 'analyzer',
                'name': analyzer.name,
                'version': analyzer.version,
                'description': analyzer.description
            })
        
        for exporter in self.exporters.values():
            info.append({
                'type': 'exporter',
                'name': exporter.name,
                'version': exporter.version,
                'description': exporter.description,
                'extension': exporter.get_file_extension()
            })
        
        for template in self.templates.values():
            info.append({
                'type': 'template',
                'name': template.name,
                'version': template.version,
                'description': template.description
            })
        
        return info


# Example plugin implementations

class MarkdownLintAnalyzer(AnalyzerPlugin):
    """Example analyzer plugin for Markdown linting."""
    
    @property
    def name(self) -> str:
        return "markdown-lint"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Analyzes Markdown files for common issues"
    
    def supports_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in ['.md', '.markdown']
    
    def analyze(self, file_path: Path, content: str) -> Dict:
        """Analyze Markdown file."""
        issues = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    'line': i,
                    'type': 'trailing-whitespace',
                    'message': 'Line has trailing whitespace'
                })
            
            # Check for consecutive blank lines
            if i > 1 and not line.strip() and not lines[i-2].strip():
                issues.append({
                    'line': i,
                    'type': 'consecutive-blank-lines',
                    'message': 'Multiple consecutive blank lines'
                })
        
        return {
            'file': str(file_path),
            'issues': issues,
            'issue_count': len(issues)
        }


# Global plugin manager instance
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def load_plugin(plugin_path: Path):
    """
    Load a plugin from a file.
    
    Args:
        plugin_path: Path to plugin file
    """
    manager = get_plugin_manager()
    manager._load_plugin_file(plugin_path)
