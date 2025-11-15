"""
Keyboard shortcuts system for AccuDoc GUI.

Provides configurable keyboard shortcuts for common actions.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum


class ShortcutAction(Enum):
    """Available shortcut actions."""
    NEW_WINDOW = "new_window"
    OPEN_FILE = "open_file"
    SAVE_FILE = "save_file"
    SCAN_REPO = "scan_repo"
    GENERATE_DOCS = "generate_docs"
    EXPORT_DOCS = "export_docs"
    CLEAR_OUTPUT = "clear_output"
    COPY_OUTPUT = "copy_output"
    SETTINGS = "settings"
    HELP = "help"
    QUIT = "quit"
    TOGGLE_PREVIEW = "toggle_preview"
    INCREASE_FONT = "increase_font"
    DECREASE_FONT = "decrease_font"
    FIND = "find"
    FIND_NEXT = "find_next"
    FIND_PREVIOUS = "find_previous"


@dataclass
class KeyboardShortcut:
    """Represents a keyboard shortcut."""
    
    action: str
    key: str  # Tk key binding format, e.g., "<Control-n>"
    description: str
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'KeyboardShortcut':
        """Create from dictionary."""
        return cls(**data)


class ShortcutManager:
    """
    Manages keyboard shortcuts for AccuDoc GUI.
    
    Provides default shortcuts and allows customization.
    """
    
    # Default keyboard shortcuts
    DEFAULT_SHORTCUTS = {
        ShortcutAction.NEW_WINDOW: KeyboardShortcut(
            action=ShortcutAction.NEW_WINDOW.value,
            key="<Control-n>",
            description="Open new window"
        ),
        ShortcutAction.OPEN_FILE: KeyboardShortcut(
            action=ShortcutAction.OPEN_FILE.value,
            key="<Control-o>",
            description="Open file"
        ),
        ShortcutAction.SAVE_FILE: KeyboardShortcut(
            action=ShortcutAction.SAVE_FILE.value,
            key="<Control-s>",
            description="Save documentation"
        ),
        ShortcutAction.SCAN_REPO: KeyboardShortcut(
            action=ShortcutAction.SCAN_REPO.value,
            key="<Control-r>",
            description="Scan repository"
        ),
        ShortcutAction.GENERATE_DOCS: KeyboardShortcut(
            action=ShortcutAction.GENERATE_DOCS.value,
            key="<Control-g>",
            description="Generate documentation"
        ),
        ShortcutAction.EXPORT_DOCS: KeyboardShortcut(
            action=ShortcutAction.EXPORT_DOCS.value,
            key="<Control-e>",
            description="Export documentation"
        ),
        ShortcutAction.CLEAR_OUTPUT: KeyboardShortcut(
            action=ShortcutAction.CLEAR_OUTPUT.value,
            key="<Control-l>",
            description="Clear output"
        ),
        ShortcutAction.COPY_OUTPUT: KeyboardShortcut(
            action=ShortcutAction.COPY_OUTPUT.value,
            key="<Control-c>",
            description="Copy output"
        ),
        ShortcutAction.SETTINGS: KeyboardShortcut(
            action=ShortcutAction.SETTINGS.value,
            key="<Control-comma>",
            description="Open settings"
        ),
        ShortcutAction.HELP: KeyboardShortcut(
            action=ShortcutAction.HELP.value,
            key="<F1>",
            description="Show help"
        ),
        ShortcutAction.QUIT: KeyboardShortcut(
            action=ShortcutAction.QUIT.value,
            key="<Control-q>",
            description="Quit application"
        ),
        ShortcutAction.TOGGLE_PREVIEW: KeyboardShortcut(
            action=ShortcutAction.TOGGLE_PREVIEW.value,
            key="<Control-p>",
            description="Toggle preview"
        ),
        ShortcutAction.INCREASE_FONT: KeyboardShortcut(
            action=ShortcutAction.INCREASE_FONT.value,
            key="<Control-plus>",
            description="Increase font size"
        ),
        ShortcutAction.DECREASE_FONT: KeyboardShortcut(
            action=ShortcutAction.DECREASE_FONT.value,
            key="<Control-minus>",
            description="Decrease font size"
        ),
        ShortcutAction.FIND: KeyboardShortcut(
            action=ShortcutAction.FIND.value,
            key="<Control-f>",
            description="Find in output"
        ),
        ShortcutAction.FIND_NEXT: KeyboardShortcut(
            action=ShortcutAction.FIND_NEXT.value,
            key="<F3>",
            description="Find next"
        ),
        ShortcutAction.FIND_PREVIOUS: KeyboardShortcut(
            action=ShortcutAction.FIND_PREVIOUS.value,
            key="<Shift-F3>",
            description="Find previous"
        ),
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize shortcut manager.
        
        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = Path(config_dir or Path.home() / ".accudoc")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "shortcuts.json"
        self.shortcuts: Dict[ShortcutAction, KeyboardShortcut] = {}
        self.callbacks: Dict[ShortcutAction, Callable] = {}
        
        self._load_shortcuts()
    
    def _load_shortcuts(self):
        """Load shortcuts from config or use defaults."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for action_str, shortcut_data in data.get('shortcuts', {}).items():
                    action = ShortcutAction(action_str)
                    self.shortcuts[action] = KeyboardShortcut.from_dict(shortcut_data)
        else:
            # Use defaults
            self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
            self._save_shortcuts()
    
    def _save_shortcuts(self):
        """Save shortcuts to config file."""
        data = {
            'shortcuts': {
                k.value: v.to_dict() for k, v in self.shortcuts.items()
            }
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_shortcut(self, action: ShortcutAction) -> Optional[KeyboardShortcut]:
        """
        Get shortcut for an action.
        
        Args:
            action: Shortcut action
            
        Returns:
            KeyboardShortcut or None
        """
        return self.shortcuts.get(action)
    
    def set_shortcut(self, action: ShortcutAction, key: str):
        """
        Set or update a shortcut.
        
        Args:
            action: Shortcut action
            key: Key binding string
        """
        if action in self.shortcuts:
            self.shortcuts[action].key = key
        else:
            self.shortcuts[action] = KeyboardShortcut(
                action=action.value,
                key=key,
                description=action.value.replace('_', ' ').title()
            )
        self._save_shortcuts()
    
    def register_callback(self, action: ShortcutAction, callback: Callable):
        """
        Register a callback for an action.
        
        Args:
            action: Shortcut action
            callback: Function to call when shortcut is triggered
        """
        self.callbacks[action] = callback
    
    def bind_to_widget(self, widget, action: ShortcutAction):
        """
        Bind a shortcut to a Tkinter widget.
        
        Args:
            widget: Tkinter widget
            action: Shortcut action
        """
        shortcut = self.get_shortcut(action)
        if not shortcut or not shortcut.enabled:
            return
        
        callback = self.callbacks.get(action)
        if not callback:
            return
        
        widget.bind(shortcut.key, lambda e: callback())
    
    def bind_all_to_widget(self, widget):
        """
        Bind all enabled shortcuts to a widget.
        
        Args:
            widget: Tkinter widget
        """
        for action, shortcut in self.shortcuts.items():
            if shortcut.enabled and action in self.callbacks:
                self.bind_to_widget(widget, action)
    
    def get_shortcuts_help(self) -> str:
        """
        Get formatted help text for all shortcuts.
        
        Returns:
            Formatted help string
        """
        lines = []
        lines.append("Keyboard Shortcuts")
        lines.append("=" * 60)
        lines.append("")
        
        # Group by category
        categories = {
            "File": [ShortcutAction.NEW_WINDOW, ShortcutAction.OPEN_FILE, 
                     ShortcutAction.SAVE_FILE, ShortcutAction.QUIT],
            "Actions": [ShortcutAction.SCAN_REPO, ShortcutAction.GENERATE_DOCS, 
                       ShortcutAction.EXPORT_DOCS],
            "Edit": [ShortcutAction.CLEAR_OUTPUT, ShortcutAction.COPY_OUTPUT,
                    ShortcutAction.FIND, ShortcutAction.FIND_NEXT, 
                    ShortcutAction.FIND_PREVIOUS],
            "View": [ShortcutAction.TOGGLE_PREVIEW, ShortcutAction.INCREASE_FONT,
                    ShortcutAction.DECREASE_FONT],
            "Other": [ShortcutAction.SETTINGS, ShortcutAction.HELP]
        }
        
        for category, actions in categories.items():
            lines.append(f"{category}:")
            for action in actions:
                shortcut = self.get_shortcut(action)
                if shortcut and shortcut.enabled:
                    # Convert to readable format
                    key_display = shortcut.key.replace('<', '').replace('>', '')
                    key_display = key_display.replace('Control-', 'Ctrl+')
                    key_display = key_display.replace('Shift-', 'Shift+')
                    key_display = key_display.replace('Alt-', 'Alt+')
                    
                    lines.append(f"  {key_display:<20} {shortcut.description}")
            lines.append("")
        
        return "\n".join(lines)
    
    def reset_to_defaults(self):
        """Reset all shortcuts to defaults."""
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self._save_shortcuts()


def get_shortcut_manager() -> ShortcutManager:
    """
    Get the shortcut manager instance.
    
    Returns:
        ShortcutManager instance
    """
    return ShortcutManager()
