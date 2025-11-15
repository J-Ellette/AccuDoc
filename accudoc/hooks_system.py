"""
AccuDoc Hooks System

Provides a flexible hook system for extending AccuDoc functionality.
Allows users to register and execute hooks at various points in the documentation generation process.
"""

import subprocess
import sys
from typing import Dict, List, Callable, Any, Optional
from enum import Enum


class HookPoint(Enum):
    """Enumeration of available hook points."""
    
    # Scanning hooks
    BEFORE_SCAN = "before_scan"
    AFTER_SCAN = "after_scan"
    BEFORE_FILE_ANALYSIS = "before_file_analysis"
    AFTER_FILE_ANALYSIS = "after_file_analysis"
    
    # Generation hooks
    BEFORE_GENERATE = "before_generate"
    AFTER_GENERATE = "after_generate"
    
    # Export hooks
    BEFORE_EXPORT = "before_export"
    AFTER_EXPORT = "after_export"
    
    # Health metrics hooks
    BEFORE_HEALTH_METRICS = "before_health_metrics"
    AFTER_HEALTH_METRICS = "after_health_metrics"
    
    # Custom hooks
    CUSTOM = "custom"


class Hook:
    """Represents a single hook."""
    
    def __init__(self, name: str, callback: Callable, priority: int = 50, enabled: bool = True):
        """
        Initialize a hook.
        
        Args:
            name: Hook name
            callback: Function to call when hook is triggered
            priority: Hook priority (lower numbers run first)
            enabled: Whether hook is enabled
        """
        self.name = name
        self.callback = callback
        self.priority = priority
        self.enabled = enabled
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the hook with given context.
        
        Args:
            context: Context data for the hook
            
        Returns:
            Updated context
        """
        if not self.enabled:
            return context
        
        try:
            result = self.callback(context)
            # If callback returns something, use it to update context
            if result is not None and isinstance(result, dict):
                context.update(result)
        except Exception as e:
            print(f"Warning: Hook '{self.name}' failed: {e}", file=sys.stderr)
        
        return context


class ShellHook(Hook):
    """Hook that executes a shell command."""
    
    def __init__(self, name: str, command: str, priority: int = 50, enabled: bool = True):
        """
        Initialize a shell hook.
        
        Args:
            name: Hook name
            command: Shell command to execute
            priority: Hook priority
            enabled: Whether hook is enabled
        """
        self.command = command
        super().__init__(name, self._execute_shell, priority, enabled)
    
    def _execute_shell(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the shell command."""
        try:
            # Replace context variables in command
            cmd = self.command
            for key, value in context.items():
                if isinstance(value, str):
                    cmd = cmd.replace(f"{{{key}}}", value)
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                f"{self.name}_output": result.stdout,
                f"{self.name}_error": result.stderr,
                f"{self.name}_return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            print(f"Warning: Shell hook '{self.name}' timed out", file=sys.stderr)
            return {}
        except Exception as e:
            print(f"Warning: Shell hook '{self.name}' failed: {e}", file=sys.stderr)
            return {}


class HooksManager:
    """Manages hooks and their execution."""
    
    def __init__(self):
        """Initialize the hooks manager."""
        self.hooks: Dict[HookPoint, List[Hook]] = {point: [] for point in HookPoint}
        self._register_builtin_hooks()
    
    def register(self, hook_point: HookPoint, hook: Hook):
        """
        Register a hook at a specific hook point.
        
        Args:
            hook_point: Where to register the hook
            hook: Hook to register
        """
        self.hooks[hook_point].append(hook)
        # Sort by priority (lower priority runs first)
        self.hooks[hook_point].sort(key=lambda h: h.priority)
    
    def register_function(
        self,
        hook_point: HookPoint,
        name: str,
        callback: Callable,
        priority: int = 50,
        enabled: bool = True
    ):
        """
        Register a function as a hook.
        
        Args:
            hook_point: Where to register the hook
            name: Hook name
            callback: Function to call
            priority: Hook priority
            enabled: Whether hook is enabled
        """
        hook = Hook(name, callback, priority, enabled)
        self.register(hook_point, hook)
    
    def register_shell(
        self,
        hook_point: HookPoint,
        name: str,
        command: str,
        priority: int = 50,
        enabled: bool = True
    ):
        """
        Register a shell command as a hook.
        
        Args:
            hook_point: Where to register the hook
            name: Hook name
            command: Shell command to execute
            priority: Hook priority
            enabled: Whether hook is enabled
        """
        hook = ShellHook(name, command, priority, enabled)
        self.register(hook_point, hook)
    
    def execute(self, hook_point: HookPoint, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute all hooks at a specific hook point.
        
        Args:
            hook_point: Hook point to execute
            context: Context data for hooks
            
        Returns:
            Updated context after all hooks have executed
        """
        if context is None:
            context = {}
        
        context['hook_point'] = hook_point.value
        
        for hook in self.hooks[hook_point]:
            if hook.enabled:
                context = hook.execute(context)
        
        return context
    
    def enable_hook(self, hook_point: HookPoint, hook_name: str):
        """Enable a specific hook."""
        for hook in self.hooks[hook_point]:
            if hook.name == hook_name:
                hook.enabled = True
    
    def disable_hook(self, hook_point: HookPoint, hook_name: str):
        """Disable a specific hook."""
        for hook in self.hooks[hook_point]:
            if hook.name == hook_name:
                hook.enabled = False
    
    def get_hooks(self, hook_point: HookPoint) -> List[Hook]:
        """Get all hooks at a specific hook point."""
        return self.hooks[hook_point]
    
    def clear_hooks(self, hook_point: Optional[HookPoint] = None):
        """
        Clear hooks.
        
        Args:
            hook_point: Specific hook point to clear, or None to clear all
        """
        if hook_point:
            self.hooks[hook_point] = []
        else:
            self.hooks = {point: [] for point in HookPoint}
            self._register_builtin_hooks()
    
    def _register_builtin_hooks(self):
        """Register built-in hooks."""
        # Example built-in hook: Log scan start
        def log_scan_start(context):
            path = context.get('path', 'unknown')
            print(f"[HOOK] Starting scan of: {path}")
            return context
        
        # Example built-in hook: Log generation complete
        def log_generation_complete(context):
            print(f"[HOOK] Documentation generation complete")
            return context
        
        # These are disabled by default and can be enabled by users
        self.register_function(
            HookPoint.BEFORE_SCAN,
            "log_scan_start",
            log_scan_start,
            priority=10,
            enabled=False
        )
        
        self.register_function(
            HookPoint.AFTER_GENERATE,
            "log_generation_complete",
            log_generation_complete,
            priority=90,
            enabled=False
        )


# Global hooks manager instance
_hooks_manager = None


def get_hooks_manager() -> HooksManager:
    """Get the global hooks manager instance."""
    global _hooks_manager
    if _hooks_manager is None:
        _hooks_manager = HooksManager()
    return _hooks_manager


def register_hook(hook_point: HookPoint, hook: Hook):
    """Register a hook (convenience function)."""
    get_hooks_manager().register(hook_point, hook)


def execute_hooks(hook_point: HookPoint, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute hooks at a specific point (convenience function)."""
    return get_hooks_manager().execute(hook_point, context)
