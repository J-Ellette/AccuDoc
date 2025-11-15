"""
Tests for AccuDoc Hooks System
"""

import unittest
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from accudoc.hooks_system import (
    HooksManager, Hook, ShellHook, HookPoint,
    get_hooks_manager, register_hook, execute_hooks
)


class TestHook(unittest.TestCase):
    """Test the Hook class."""
    
    def test_hook_creation(self):
        """Test creating a hook."""
        def callback(context):
            return {"result": "success"}
        
        hook = Hook("test_hook", callback, priority=10, enabled=True)
        
        self.assertEqual(hook.name, "test_hook")
        self.assertEqual(hook.priority, 10)
        self.assertTrue(hook.enabled)
    
    def test_hook_execution(self):
        """Test hook execution."""
        def callback(context):
            context["executed"] = True
            return context
        
        hook = Hook("test_hook", callback)
        context = {"initial": "value"}
        result = hook.execute(context)
        
        self.assertTrue(result.get("executed"))
        self.assertEqual(result.get("initial"), "value")
    
    def test_hook_disabled(self):
        """Test that disabled hooks don't execute."""
        def callback(context):
            context["executed"] = True
            return context
        
        hook = Hook("test_hook", callback, enabled=False)
        context = {}
        result = hook.execute(context)
        
        self.assertFalse(result.get("executed", False))
    
    def test_hook_error_handling(self):
        """Test hook error handling."""
        def failing_callback(context):
            raise ValueError("Test error")
        
        hook = Hook("failing_hook", failing_callback)
        context = {"initial": "value"}
        
        # Should not raise, just print warning
        result = hook.execute(context)
        self.assertEqual(result.get("initial"), "value")


class TestShellHook(unittest.TestCase):
    """Test the ShellHook class."""
    
    def test_shell_hook_creation(self):
        """Test creating a shell hook."""
        hook = ShellHook("test_shell", "echo test", priority=10)
        
        self.assertEqual(hook.name, "test_shell")
        self.assertEqual(hook.command, "echo test")
        self.assertEqual(hook.priority, 10)
    
    def test_shell_hook_execution(self):
        """Test shell hook execution."""
        hook = ShellHook("echo_test", "echo 'Hello World'")
        context = {}
        result = hook.execute(context)
        
        self.assertIn("echo_test_output", result)
        self.assertIn("Hello World", result["echo_test_output"])
        self.assertEqual(result["echo_test_return_code"], 0)
    
    def test_shell_hook_variable_substitution(self):
        """Test variable substitution in shell commands."""
        hook = ShellHook("var_test", "echo '{name}'")
        context = {"name": "AccuDoc"}
        result = hook.execute(context)
        
        self.assertIn("AccuDoc", result["var_test_output"])


class TestHooksManager(unittest.TestCase):
    """Test the HooksManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = HooksManager()
        # Clear hooks but built-in hooks will be re-registered
        # So we need to clear them completely without re-registering
        self.manager.hooks = {point: [] for point in HookPoint}
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsInstance(self.manager.hooks, dict)
        for hook_point in HookPoint:
            self.assertIn(hook_point, self.manager.hooks)
    
    def test_register_hook(self):
        """Test registering a hook."""
        def callback(context):
            return context
        
        hook = Hook("test", callback)
        self.manager.register(HookPoint.BEFORE_SCAN, hook)
        
        hooks = self.manager.get_hooks(HookPoint.BEFORE_SCAN)
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0].name, "test")
    
    def test_register_function(self):
        """Test registering a function as a hook."""
        def callback(context):
            context["called"] = True
            return context
        
        self.manager.register_function(
            HookPoint.BEFORE_SCAN,
            "func_hook",
            callback
        )
        
        hooks = self.manager.get_hooks(HookPoint.BEFORE_SCAN)
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0].name, "func_hook")
    
    def test_register_shell(self):
        """Test registering a shell command as a hook."""
        self.manager.register_shell(
            HookPoint.BEFORE_SCAN,
            "shell_hook",
            "echo test"
        )
        
        hooks = self.manager.get_hooks(HookPoint.BEFORE_SCAN)
        self.assertEqual(len(hooks), 1)
        self.assertIsInstance(hooks[0], ShellHook)
    
    def test_hook_priority_ordering(self):
        """Test that hooks are ordered by priority."""
        def callback1(context):
            return context
        
        def callback2(context):
            return context
        
        hook1 = Hook("high_priority", callback1, priority=10)
        hook2 = Hook("low_priority", callback2, priority=50)
        
        self.manager.register(HookPoint.BEFORE_SCAN, hook2)
        self.manager.register(HookPoint.BEFORE_SCAN, hook1)
        
        hooks = self.manager.get_hooks(HookPoint.BEFORE_SCAN)
        self.assertEqual(hooks[0].name, "high_priority")
        self.assertEqual(hooks[1].name, "low_priority")
    
    def test_execute_hooks(self):
        """Test executing hooks."""
        execution_order = []
        
        def hook1(context):
            execution_order.append(1)
            context["hook1_executed"] = True
            return context
        
        def hook2(context):
            execution_order.append(2)
            context["hook2_executed"] = True
            return context
        
        self.manager.register_function(HookPoint.BEFORE_SCAN, "hook1", hook1, priority=10)
        self.manager.register_function(HookPoint.BEFORE_SCAN, "hook2", hook2, priority=20)
        
        result = self.manager.execute(HookPoint.BEFORE_SCAN, {"initial": "value"})
        
        self.assertEqual(execution_order, [1, 2])
        self.assertTrue(result.get("hook1_executed"))
        self.assertTrue(result.get("hook2_executed"))
        self.assertEqual(result.get("initial"), "value")
    
    def test_enable_disable_hook(self):
        """Test enabling and disabling hooks."""
        def callback(context):
            context["executed"] = True
            return context
        
        self.manager.register_function(HookPoint.BEFORE_SCAN, "test_hook", callback)
        
        # Disable the hook
        self.manager.disable_hook(HookPoint.BEFORE_SCAN, "test_hook")
        result = self.manager.execute(HookPoint.BEFORE_SCAN)
        self.assertFalse(result.get("executed", False))
        
        # Enable the hook
        self.manager.enable_hook(HookPoint.BEFORE_SCAN, "test_hook")
        result = self.manager.execute(HookPoint.BEFORE_SCAN)
        self.assertTrue(result.get("executed"))
    
    def test_clear_hooks(self):
        """Test clearing hooks."""
        def callback(context):
            return context
        
        self.manager.register_function(HookPoint.BEFORE_SCAN, "hook1", callback)
        self.manager.register_function(HookPoint.AFTER_SCAN, "hook2", callback)
        
        # Clear specific hook point
        self.manager.clear_hooks(HookPoint.BEFORE_SCAN)
        self.assertEqual(len(self.manager.get_hooks(HookPoint.BEFORE_SCAN)), 0)
        self.assertEqual(len(self.manager.get_hooks(HookPoint.AFTER_SCAN)), 1)
        
        # Clear all hooks
        self.manager.clear_hooks()
        self.assertEqual(len(self.manager.get_hooks(HookPoint.AFTER_SCAN)), 0)
    
    def test_context_propagation(self):
        """Test that context is properly propagated through hooks."""
        def hook1(context):
            context["value1"] = "from_hook1"
            return context
        
        def hook2(context):
            # Should have access to value1 from hook1
            self.assertEqual(context.get("value1"), "from_hook1")
            context["value2"] = "from_hook2"
            return context
        
        self.manager.register_function(HookPoint.BEFORE_SCAN, "hook1", hook1, priority=10)
        self.manager.register_function(HookPoint.BEFORE_SCAN, "hook2", hook2, priority=20)
        
        result = self.manager.execute(HookPoint.BEFORE_SCAN)
        
        self.assertEqual(result.get("value1"), "from_hook1")
        self.assertEqual(result.get("value2"), "from_hook2")


class TestHookPoints(unittest.TestCase):
    """Test hook points enumeration."""
    
    def test_all_hook_points_exist(self):
        """Test that all expected hook points exist."""
        expected_points = [
            "BEFORE_SCAN", "AFTER_SCAN",
            "BEFORE_FILE_ANALYSIS", "AFTER_FILE_ANALYSIS",
            "BEFORE_GENERATE", "AFTER_GENERATE",
            "BEFORE_EXPORT", "AFTER_EXPORT",
            "BEFORE_HEALTH_METRICS", "AFTER_HEALTH_METRICS",
            "CUSTOM"
        ]
        
        for point in expected_points:
            self.assertTrue(hasattr(HookPoint, point))
    
    def test_hook_point_values(self):
        """Test hook point values."""
        self.assertEqual(HookPoint.BEFORE_SCAN.value, "before_scan")
        self.assertEqual(HookPoint.AFTER_SCAN.value, "after_scan")


class TestGlobalFunctions(unittest.TestCase):
    """Test global convenience functions."""
    
    def test_get_hooks_manager(self):
        """Test getting the global hooks manager."""
        manager1 = get_hooks_manager()
        manager2 = get_hooks_manager()
        
        # Should return the same instance
        self.assertIs(manager1, manager2)
    
    def test_register_hook_function(self):
        """Test the global register_hook function."""
        def callback(context):
            return context
        
        hook = Hook("test", callback)
        register_hook(HookPoint.BEFORE_SCAN, hook)
        
        manager = get_hooks_manager()
        hooks = manager.get_hooks(HookPoint.BEFORE_SCAN)
        
        # Should find the registered hook
        hook_names = [h.name for h in hooks]
        self.assertIn("test", hook_names)
    
    def test_execute_hooks_function(self):
        """Test the global execute_hooks function."""
        def callback(context):
            context["executed"] = True
            return context
        
        manager = get_hooks_manager()
        manager.clear_hooks()
        manager.register_function(HookPoint.BEFORE_SCAN, "test", callback)
        
        result = execute_hooks(HookPoint.BEFORE_SCAN)
        self.assertTrue(result.get("executed"))


class TestBuiltInHooks(unittest.TestCase):
    """Test built-in hooks."""
    
    def test_builtin_hooks_registered(self):
        """Test that built-in hooks are registered."""
        manager = HooksManager()
        
        # Built-in hooks should be registered
        before_scan_hooks = manager.get_hooks(HookPoint.BEFORE_SCAN)
        after_generate_hooks = manager.get_hooks(HookPoint.AFTER_GENERATE)
        
        # Should have built-in hooks (disabled by default)
        hook_names = [h.name for h in before_scan_hooks]
        self.assertIn("log_scan_start", hook_names)
        
        hook_names = [h.name for h in after_generate_hooks]
        self.assertIn("log_generation_complete", hook_names)
    
    def test_builtin_hooks_disabled_by_default(self):
        """Test that built-in hooks are disabled by default."""
        manager = HooksManager()
        
        hooks = manager.get_hooks(HookPoint.BEFORE_SCAN)
        for hook in hooks:
            if hook.name == "log_scan_start":
                self.assertFalse(hook.enabled)


if __name__ == '__main__':
    unittest.main()
