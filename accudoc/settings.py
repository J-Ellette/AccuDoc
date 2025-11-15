"""
Settings export/import module for AccuDoc.

Allows users to share configuration between machines and backup preferences.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import datetime


@dataclass
class AccuDocSettings:
    """AccuDoc user settings and preferences."""
    
    # General settings
    default_template: str = 'detailed'
    default_format: str = 'markdown'
    markdown_flavor: str = 'github'
    html_theme: str = 'default'
    language: str = 'auto'  # UI language (auto, en, es, fr, de, zh, ja, ar)
    
    # Output settings
    output_directory: str = './docs'
    include_toc: bool = True
    include_badges: bool = True
    include_statistics: bool = True
    
    # Scanning settings
    exclude_patterns: List[str] = None
    include_hidden_files: bool = False
    max_file_size_mb: int = 10
    follow_symlinks: bool = False
    
    # Cache settings
    enable_cache: bool = True
    cache_directory: str = '~/.accudoc/cache'
    
    # Security settings
    enable_secret_scanning: bool = True
    redaction_strategy: str = 'mask'  # mask, remove, placeholder
    min_confidence: str = 'medium'  # high, medium, low
    
    # Audit settings
    enable_audit_trail: bool = False
    audit_log_location: str = '~/.accudoc/audit.log'
    
    # API settings
    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    bitbucket_username: Optional[str] = None
    bitbucket_app_password: Optional[str] = None
    
    # Live Testbed settings
    enable_live_testbed: bool = False
    testbed_timeout: int = 30
    testbed_memory_limit: str = '256m'
    testbed_cpu_quota: int = 50000  # 50% of one CPU
    testbed_network_disabled: bool = True
    testbed_enable_cache: bool = True
    testbed_require_auth: bool = True  # Require user authentication
    testbed_allowed_languages: List[str] = None  # None = all languages allowed
    
    # Export metadata
    export_date: Optional[str] = None
    export_version: str = '1.0'
    
    def __post_init__(self):
        """Initialize default values."""
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                '*.pyc', '__pycache__', '.git', 'node_modules',
                'venv', '.env', '*.log'
            ]
        if self.testbed_allowed_languages is None:
            self.testbed_allowed_languages = [
                'python', 'javascript', 'java', 'go', 'ruby', 'rust'
            ]


class SettingsManager:
    """Manage export and import of AccuDoc settings."""
    
    DEFAULT_SETTINGS_FILE = Path.home() / '.accudoc' / 'settings.json'
    
    def __init__(self, settings_file: Optional[Path] = None):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Path to settings file (default: ~/.accudoc/settings.json)
        """
        self.settings_file = settings_file or self.DEFAULT_SETTINGS_FILE
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
    
    def export_settings(self, settings: AccuDocSettings, 
                       output_path: Path,
                       format: str = 'json',
                       include_secrets: bool = False) -> Path:
        """
        Export settings to file.
        
        Args:
            settings: AccuDoc settings to export
            output_path: Output file path
            format: Export format ('json' or 'yaml')
            include_secrets: Whether to include API tokens (default: False)
            
        Returns:
            Path to exported file
        """
        # Convert to dictionary
        settings_dict = asdict(settings)
        
        # Add export metadata
        settings_dict['export_date'] = datetime.datetime.now().isoformat()
        settings_dict['export_version'] = '1.0'
        
        # Remove secrets if requested
        if not include_secrets:
            settings_dict['github_token'] = None
            settings_dict['gitlab_token'] = None
            settings_dict['bitbucket_username'] = None
            settings_dict['bitbucket_app_password'] = None
        
        # Export to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=2)
        elif format.lower() == 'yaml':
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(settings_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'yaml'")
        
        return output_path
    
    def import_settings(self, input_path: Path,
                       validate: bool = True) -> AccuDocSettings:
        """
        Import settings from file.
        
        Args:
            input_path: Path to settings file
            validate: Whether to validate settings (default: True)
            
        Returns:
            AccuDocSettings object
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Settings file not found: {input_path}")
        
        # Determine format from extension
        if input_path.suffix.lower() in ['.json']:
            with open(input_path, 'r', encoding='utf-8') as f:
                settings_dict = json.load(f)
        elif input_path.suffix.lower() in ['.yaml', '.yml']:
            with open(input_path, 'r', encoding='utf-8') as f:
                settings_dict = yaml.safe_load(f)
        else:
            # Try JSON first, then YAML
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    settings_dict = json.load(f)
            except json.JSONDecodeError:
                with open(input_path, 'r', encoding='utf-8') as f:
                    settings_dict = yaml.safe_load(f)
        
        # Remove metadata fields
        settings_dict.pop('export_date', None)
        settings_dict.pop('export_version', None)
        
        # Create settings object
        settings = AccuDocSettings(**settings_dict)
        
        # Validate if requested
        if validate:
            self._validate_settings(settings)
        
        return settings
    
    def _validate_settings(self, settings: AccuDocSettings):
        """
        Validate settings.
        
        Args:
            settings: Settings to validate
            
        Raises:
            ValueError: If settings are invalid
        """
        # Validate format
        valid_formats = ['markdown', 'html', 'txt', 'pdf', 'rst', 'asciidoc', 'latex']
        if settings.default_format not in valid_formats:
            raise ValueError(f"Invalid format: {settings.default_format}")
        
        # Validate markdown flavor
        valid_flavors = ['github', 'gitlab', 'commonmark']
        if settings.markdown_flavor not in valid_flavors:
            raise ValueError(f"Invalid markdown flavor: {settings.markdown_flavor}")
        
        # Validate theme
        valid_themes = ['default', 'dark', 'minimal', 'corporate']
        if settings.html_theme not in valid_themes:
            raise ValueError(f"Invalid theme: {settings.html_theme}")
    
    def save_settings(self, settings: AccuDocSettings) -> Path:
        """
        Save settings to the default settings file.
        
        Args:
            settings: AccuDocSettings object to save
            
        Returns:
            Path to saved settings file
        """
        return self.export_settings(
            settings, 
            self.settings_file, 
            format='json',
            include_secrets=True
        )
    
    def load_settings(self) -> AccuDocSettings:
        """
        Load settings from the default settings file.
        
        Returns:
            AccuDocSettings object
            
        Raises:
            FileNotFoundError: If settings file doesn't exist
        """
        if not self.settings_file.exists():
            # Return default settings if file doesn't exist
            return AccuDocSettings()
        
        return self.import_settings(self.settings_file, validate=True)
        
        # Validate redaction strategy
        valid_strategies = ['mask', 'remove', 'placeholder']
        if settings.redaction_strategy not in valid_strategies:
            raise ValueError(f"Invalid redaction strategy: {settings.redaction_strategy}")
        
        # Validate confidence level
        valid_confidence = ['high', 'medium', 'low']
        if settings.min_confidence not in valid_confidence:
            raise ValueError(f"Invalid confidence level: {settings.min_confidence}")
        
        # Validate file size
        if settings.max_file_size_mb <= 0:
            raise ValueError("Max file size must be positive")
    
    def save_current_settings(self, settings: AccuDocSettings):
        """
        Save settings to default location.
        
        Args:
            settings: Settings to save
        """
        self.export_settings(settings, self.settings_file, format='json', 
                           include_secrets=True)
    
    def load_current_settings(self) -> Optional[AccuDocSettings]:
        """
        Load settings from default location.
        
        Returns:
            AccuDocSettings if file exists, None otherwise
        """
        if not self.settings_file.exists():
            return None
        
        return self.import_settings(self.settings_file)
    
    def get_default_settings(self) -> AccuDocSettings:
        """
        Get default settings.
        
        Returns:
            Default AccuDocSettings
        """
        return AccuDocSettings()
    
    def merge_settings(self, base: AccuDocSettings, 
                      override: AccuDocSettings) -> AccuDocSettings:
        """
        Merge two settings objects, with override taking precedence.
        
        Args:
            base: Base settings
            override: Override settings
            
        Returns:
            Merged settings
        """
        base_dict = asdict(base)
        override_dict = asdict(override)
        
        # Merge dictionaries
        merged = {**base_dict, **{k: v for k, v in override_dict.items() if v is not None}}
        
        return AccuDocSettings(**merged)
    
    def export_template(self, output_path: Path, format: str = 'json'):
        """
        Export a template settings file with comments.
        
        Args:
            output_path: Output file path
            format: Export format ('json' or 'yaml')
        """
        settings = self.get_default_settings()
        
        if format.lower() == 'yaml':
            # YAML supports comments
            template = f"""# AccuDoc Settings Template
# Generated: {datetime.datetime.now().isoformat()}

# General Settings
default_template: {settings.default_template}  # Template to use (detailed, simple, readme)
default_format: {settings.default_format}  # Output format (markdown, html, pdf, etc.)
markdown_flavor: {settings.markdown_flavor}  # Markdown flavor (github, gitlab, commonmark)
html_theme: {settings.html_theme}  # HTML theme (default, dark, minimal, corporate)

# Output Settings
output_directory: {settings.output_directory}  # Where to save generated documentation
include_toc: {settings.include_toc}  # Include table of contents
include_badges: {settings.include_badges}  # Include status badges
include_statistics: {settings.include_statistics}  # Include code statistics

# Scanning Settings
exclude_patterns:  # Patterns to exclude from scanning
{chr(10).join('  - ' + p for p in settings.exclude_patterns)}
include_hidden_files: {settings.include_hidden_files}  # Include hidden files
max_file_size_mb: {settings.max_file_size_mb}  # Maximum file size to process
follow_symlinks: {settings.follow_symlinks}  # Follow symbolic links

# Cache Settings
enable_cache: {settings.enable_cache}  # Enable caching
cache_directory: {settings.cache_directory}  # Cache directory location

# Security Settings
enable_secret_scanning: {settings.enable_secret_scanning}  # Scan for exposed secrets
redaction_strategy: {settings.redaction_strategy}  # How to redact secrets (mask, remove, placeholder)
min_confidence: {settings.min_confidence}  # Minimum confidence to redact (high, medium, low)

# Audit Settings
enable_audit_trail: {settings.enable_audit_trail}  # Log all operations
audit_log_location: {settings.audit_log_location}  # Audit log file location

# API Settings (leave blank for prompts)
github_token: null  # GitHub personal access token
gitlab_token: null  # GitLab personal access token
bitbucket_username: null  # Bitbucket username
bitbucket_app_password: null  # Bitbucket app password
"""
            output_path = Path(output_path)
            output_path.write_text(template, encoding='utf-8')
        else:
            # JSON doesn't support comments, add them as a separate field
            settings_dict = asdict(settings)
            settings_dict['_comments'] = {
                'default_template': 'Template to use (detailed, simple, readme)',
                'default_format': 'Output format (markdown, html, pdf, rst, asciidoc, latex)',
                'markdown_flavor': 'Markdown flavor (github, gitlab, commonmark)',
                'html_theme': 'HTML theme (default, dark, minimal, corporate)',
                'redaction_strategy': 'How to redact secrets (mask, remove, placeholder)',
                'min_confidence': 'Minimum confidence to redact (high, medium, low)',
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=2)


def export_settings(settings: AccuDocSettings, output_path: Path,
                   format: str = 'json', include_secrets: bool = False) -> Path:
    """
    Convenience function to export settings.
    
    Args:
        settings: Settings to export
        output_path: Output file path
        format: Export format
        include_secrets: Include API tokens
        
    Returns:
        Path to exported file
    """
    manager = SettingsManager()
    return manager.export_settings(settings, output_path, format, include_secrets)


def import_settings(input_path: Path, validate: bool = True) -> AccuDocSettings:
    """
    Convenience function to import settings.
    
    Args:
        input_path: Input file path
        validate: Validate settings
        
    Returns:
        AccuDocSettings object
    """
    manager = SettingsManager()
    return manager.import_settings(input_path, validate)
