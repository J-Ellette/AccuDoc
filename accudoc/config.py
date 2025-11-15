"""
Configuration as Code module for AccuDoc.

This module provides functionality to define and manage AccuDoc settings
through configuration files (YAML, JSON, TOML), enabling version-controlled
and reusable documentation generation configurations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class ScanConfig:
    """Configuration for repository scanning."""
    exclude_patterns: List[str] = field(default_factory=lambda: [
        '.git', '__pycache__', 'node_modules', '.venv', 'venv'
    ])
    include_hidden: bool = False
    use_cache: bool = True
    extensions: List[str] = field(default_factory=lambda: [
        '.py', '.js', '.java', '.cpp', '.c', '.go', '.rb', '.php'
    ])


@dataclass
class GenerateConfig:
    """Configuration for documentation generation."""
    template: str = 'default'
    format: str = 'markdown'
    theme: str = 'default'
    title: Optional[str] = None
    include_toc: bool = True
    include_badges: bool = True
    include_stats: bool = True


@dataclass
class OutputConfig:
    """Configuration for output settings."""
    output_file: Optional[str] = None
    output_dir: Optional[str] = None
    create_index: bool = True
    separate_files: bool = False


@dataclass
class FeaturesConfig:
    """Configuration for optional features."""
    enable_dataflow: bool = False
    enable_call_graph: bool = False
    enable_complexity: bool = False
    enable_coverage: bool = False
    enable_spellcheck: bool = False
    enable_readability: bool = False
    enable_breaking_changes: bool = False


@dataclass
class AccuDocConfig:
    """Main AccuDoc configuration."""
    version: str = '1.0'
    repository: Optional[str] = None
    scan: ScanConfig = field(default_factory=ScanConfig)
    generate: GenerateConfig = field(default_factory=GenerateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Manages AccuDoc configuration files."""
    
    SUPPORTED_FORMATS = ['.yml', '.yaml', '.json', '.toml']
    DEFAULT_CONFIG_NAMES = [
        'accudoc.yml', 'accudoc.yaml', '.accudoc.yml',
        'accudoc.json', '.accudoc.json',
        'accudoc.toml', '.accudoc.toml'
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_path: Optional path to config file
        """
        self.logger = logging.getLogger('accudoc.config')
        self.config_path = Path(config_path) if config_path else None
        self.config = AccuDocConfig()
    
    def load_config(self, config_path: Optional[str] = None) -> AccuDocConfig:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to config file. If None, searches for default config files.
            
        Returns:
            Loaded configuration
        """
        if config_path:
            path = Path(config_path)
        else:
            path = self._find_config_file()
        
        if not path or not path.exists():
            self.logger.info("No config file found, using defaults")
            return self.config
        
        self.logger.info(f"Loading config from: {path}")
        
        try:
            suffix = path.suffix.lower()
            
            if suffix in ['.yml', '.yaml']:
                data = self._load_yaml(path)
            elif suffix == '.json':
                data = self._load_json(path)
            elif suffix == '.toml':
                data = self._load_toml(path)
            else:
                raise ValueError(f"Unsupported config format: {suffix}")
            
            self.config = self._dict_to_config(data)
            self.config_path = path
            
            return self.config
            
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise
    
    def save_config(self, config: AccuDocConfig, output_path: str,
                   format: str = 'yaml') -> Path:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            output_path: Output file path
            format: Output format (yaml, json, toml)
            
        Returns:
            Path to saved config file
        """
        path = Path(output_path)
        
        # Add extension if not present
        if not path.suffix:
            if format == 'yaml':
                path = path.with_suffix('.yml')
            elif format == 'json':
                path = path.with_suffix('.json')
            elif format == 'toml':
                path = path.with_suffix('.toml')
        
        data = self._config_to_dict(config)
        
        if format == 'yaml' or path.suffix in ['.yml', '.yaml']:
            self._save_yaml(data, path)
        elif format == 'json' or path.suffix == '.json':
            self._save_json(data, path)
        elif format == 'toml' or path.suffix == '.toml':
            self._save_toml(data, path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Config saved to: {path}")
        return path
    
    def _find_config_file(self) -> Optional[Path]:
        """
        Find config file in current directory.
        
        Returns:
            Path to config file or None
        """
        cwd = Path.cwd()
        
        for name in self.DEFAULT_CONFIG_NAMES:
            path = cwd / name
            if path.exists():
                return path
        
        return None
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML config file."""
        try:
            import yaml
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            # Fallback: basic YAML parsing for simple cases
            self.logger.warning("PyYAML not installed, using basic YAML parser")
            return self._load_basic_yaml(path)
    
    def _load_basic_yaml(self, path: Path) -> Dict[str, Any]:
        """Basic YAML parser for simple configs (no PyYAML dependency)."""
        data = {}
        current_section = None
        
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Section header
                if line.endswith(':') and not line.startswith(' '):
                    current_section = line[:-1]
                    data[current_section] = {}
                # Key-value pair
                elif ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Parse value types
                    if value.lower() in ['true', 'yes']:
                        value = True
                    elif value.lower() in ['false', 'no']:
                        value = False
                    elif value.startswith('[') and value.endswith(']'):
                        # Parse list
                        value = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]
                    elif value.startswith('"') or value.startswith("'"):
                        value = value.strip('"\'')
                    
                    if current_section:
                        data[current_section][key] = value
                    else:
                        data[key] = value
        
        return data
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON config file."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _load_toml(self, path: Path) -> Dict[str, Any]:
        """Load TOML config file."""
        try:
            import tomli
            with open(path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            try:
                import toml
                with open(path, 'r') as f:
                    return toml.load(f)
            except ImportError:
                raise ImportError("TOML support requires 'tomli' or 'toml' package. "
                                "Install with: pip install tomli")
    
    def _save_yaml(self, data: Dict[str, Any], path: Path):
        """Save config as YAML."""
        try:
            import yaml
            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        except ImportError:
            # Fallback: simple YAML writing
            self._save_basic_yaml(data, path)
    
    def _save_basic_yaml(self, data: Dict[str, Any], path: Path):
        """Basic YAML writer (no PyYAML dependency)."""
        lines = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, list):
                        list_str = ', '.join(f'"{v}"' if isinstance(v, str) else str(v) for v in subvalue)
                        lines.append(f"  {subkey}: [{list_str}]")
                    elif isinstance(subvalue, bool):
                        lines.append(f"  {subkey}: {'true' if subvalue else 'false'}")
                    elif isinstance(subvalue, str):
                        lines.append(f'  {subkey}: "{subvalue}"')
                    else:
                        lines.append(f"  {subkey}: {subvalue}")
            else:
                if isinstance(value, str):
                    lines.append(f'{key}: "{value}"')
                else:
                    lines.append(f"{key}: {value}")
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines) + '\n')
    
    def _save_json(self, data: Dict[str, Any], path: Path):
        """Save config as JSON."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_toml(self, data: Dict[str, Any], path: Path):
        """Save config as TOML."""
        try:
            import tomli_w
            with open(path, 'wb') as f:
                tomli_w.dump(data, f)
        except ImportError:
            try:
                import toml
                with open(path, 'w') as f:
                    toml.dump(data, f)
            except ImportError:
                raise ImportError("TOML support requires 'tomli-w' or 'toml' package. "
                                "Install with: pip install tomli-w")
    
    def _dict_to_config(self, data: Dict[str, Any]) -> AccuDocConfig:
        """Convert dictionary to config object."""
        config = AccuDocConfig()
        
        # Version
        if 'version' in data:
            config.version = str(data['version'])
        
        # Repository
        if 'repository' in data:
            config.repository = data['repository']
        
        # Scan config
        if 'scan' in data:
            scan_data = data['scan']
            config.scan = ScanConfig(
                exclude_patterns=scan_data.get('exclude_patterns', config.scan.exclude_patterns),
                include_hidden=scan_data.get('include_hidden', config.scan.include_hidden),
                use_cache=scan_data.get('use_cache', config.scan.use_cache),
                extensions=scan_data.get('extensions', config.scan.extensions)
            )
        
        # Generate config
        if 'generate' in data:
            gen_data = data['generate']
            config.generate = GenerateConfig(
                template=gen_data.get('template', config.generate.template),
                format=gen_data.get('format', config.generate.format),
                theme=gen_data.get('theme', config.generate.theme),
                title=gen_data.get('title'),
                include_toc=gen_data.get('include_toc', config.generate.include_toc),
                include_badges=gen_data.get('include_badges', config.generate.include_badges),
                include_stats=gen_data.get('include_stats', config.generate.include_stats)
            )
        
        # Output config
        if 'output' in data:
            out_data = data['output']
            config.output = OutputConfig(
                output_file=out_data.get('output_file'),
                output_dir=out_data.get('output_dir'),
                create_index=out_data.get('create_index', config.output.create_index),
                separate_files=out_data.get('separate_files', config.output.separate_files)
            )
        
        # Features config
        if 'features' in data:
            feat_data = data['features']
            config.features = FeaturesConfig(
                enable_dataflow=feat_data.get('enable_dataflow', False),
                enable_call_graph=feat_data.get('enable_call_graph', False),
                enable_complexity=feat_data.get('enable_complexity', False),
                enable_coverage=feat_data.get('enable_coverage', False),
                enable_spellcheck=feat_data.get('enable_spellcheck', False),
                enable_readability=feat_data.get('enable_readability', False),
                enable_breaking_changes=feat_data.get('enable_breaking_changes', False)
            )
        
        # Metadata
        if 'metadata' in data:
            config.metadata = data['metadata']
        
        return config
    
    def _config_to_dict(self, config: AccuDocConfig) -> Dict[str, Any]:
        """Convert config object to dictionary."""
        return {
            'version': config.version,
            'repository': config.repository,
            'scan': asdict(config.scan),
            'generate': asdict(config.generate),
            'output': asdict(config.output),
            'features': asdict(config.features),
            'metadata': config.metadata
        }
    
    def generate_example_config(self, format: str = 'yaml') -> str:
        """
        Generate example configuration file content.
        
        Args:
            format: Output format (yaml, json, toml)
            
        Returns:
            Example config as string
        """
        example = AccuDocConfig(
            version='1.0',
            repository='.',
            scan=ScanConfig(
                exclude_patterns=['.git', '__pycache__', 'node_modules', '.venv'],
                include_hidden=False,
                use_cache=True,
                extensions=['.py', '.js', '.java', '.cpp']
            ),
            generate=GenerateConfig(
                template='default',
                format='markdown',
                theme='default',
                title='My Project Documentation',
                include_toc=True,
                include_badges=True,
                include_stats=True
            ),
            output=OutputConfig(
                output_file='docs/README.md',
                output_dir='docs',
                create_index=True,
                separate_files=False
            ),
            features=FeaturesConfig(
                enable_dataflow=True,
                enable_call_graph=True,
                enable_complexity=True,
                enable_coverage=False,
                enable_spellcheck=True,
                enable_readability=True,
                enable_breaking_changes=False
            ),
            metadata={
                'author': 'Your Name',
                'project_url': 'https://github.com/username/project',
                'license': 'MIT'
            }
        )
        
        data = self._config_to_dict(example)
        
        if format == 'yaml':
            lines = []
            lines.append("# AccuDoc Configuration File")
            lines.append("# This file defines settings for documentation generation")
            lines.append("")
            lines.append(f"version: \"{data['version']}\"")
            lines.append(f"repository: \"{data['repository']}\"")
            lines.append("")
            
            for section in ['scan', 'generate', 'output', 'features', 'metadata']:
                lines.append(f"{section}:")
                for key, value in data[section].items():
                    if isinstance(value, list):
                        lines.append(f"  {key}:")
                        for item in value:
                            lines.append(f"    - {item}")
                    elif isinstance(value, dict):
                        lines.append(f"  {key}:")
                        for k, v in value.items():
                            lines.append(f"    {k}: {v}")
                    elif isinstance(value, bool):
                        lines.append(f"  {key}: {'true' if value else 'false'}")
                    elif isinstance(value, str):
                        lines.append(f'  {key}: "{value}"')
                    elif value is not None:
                        lines.append(f"  {key}: {value}")
                lines.append("")
            
            return '\n'.join(lines)
        
        elif format == 'json':
            return json.dumps(data, indent=2)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
