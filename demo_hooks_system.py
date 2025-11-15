#!/usr/bin/env python3
"""
Demo: AccuDoc Hooks System

Demonstrates the hooks system functionality with various examples.
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from accudoc.hooks_system import (
    HooksManager, Hook, ShellHook, HookPoint,
    get_hooks_manager, execute_hooks
)


def demo_basic_hooks():
    """Demonstrate basic hook functionality."""
    print("=" * 70)
    print("BASIC HOOKS DEMONSTRATION")
    print("=" * 70)
    print()
    
    manager = HooksManager()
    manager.clear_hooks()
    
    # Define some example hooks
    def before_scan_hook(context):
        print(f"  [Before Scan Hook] Preparing to scan: {context.get('path', 'unknown')}")
        context['scan_started'] = True
        return context
    
    def after_scan_hook(context):
        print(f"  [After Scan Hook] Scan completed successfully")
        context['scan_completed'] = True
        return context
    
    # Register the hooks
    manager.register_function(
        HookPoint.BEFORE_SCAN,
        "prepare_scan",
        before_scan_hook,
        priority=10
    )
    
    manager.register_function(
        HookPoint.AFTER_SCAN,
        "finalize_scan",
        after_scan_hook,
        priority=10
    )
    
    # Execute the hooks
    print("Executing BEFORE_SCAN hooks...")
    context = manager.execute(HookPoint.BEFORE_SCAN, {'path': '/path/to/repo'})
    print(f"Context after BEFORE_SCAN: {context}")
    print()
    
    print("Executing AFTER_SCAN hooks...")
    context = manager.execute(HookPoint.AFTER_SCAN, context)
    print(f"Context after AFTER_SCAN: {context}")
    print()


def demo_hook_priority():
    """Demonstrate hook priority and ordering."""
    print("=" * 70)
    print("HOOK PRIORITY DEMONSTRATION")
    print("=" * 70)
    print()
    
    manager = HooksManager()
    manager.clear_hooks()
    
    # Register hooks with different priorities
    def hook_priority_10(context):
        print("  [Priority 10] First hook (low priority number = high priority)")
        return context
    
    def hook_priority_50(context):
        print("  [Priority 50] Second hook (medium priority)")
        return context
    
    def hook_priority_90(context):
        print("  [Priority 90] Third hook (high priority number = low priority)")
        return context
    
    manager.register_function(HookPoint.BEFORE_GENERATE, "hook_50", hook_priority_50, priority=50)
    manager.register_function(HookPoint.BEFORE_GENERATE, "hook_10", hook_priority_10, priority=10)
    manager.register_function(HookPoint.BEFORE_GENERATE, "hook_90", hook_priority_90, priority=90)
    
    print("Executing hooks (should run in priority order: 10, 50, 90)...")
    manager.execute(HookPoint.BEFORE_GENERATE)
    print()


def demo_context_propagation():
    """Demonstrate context propagation through hooks."""
    print("=" * 70)
    print("CONTEXT PROPAGATION DEMONSTRATION")
    print("=" * 70)
    print()
    
    manager = HooksManager()
    manager.clear_hooks()
    
    def add_metadata(context):
        print("  [Hook 1] Adding metadata to context")
        context['metadata'] = {'version': '1.0', 'author': 'AccuDoc'}
        return context
    
    def add_timestamp(context):
        from datetime import datetime
        print("  [Hook 2] Adding timestamp to context")
        context['timestamp'] = datetime.now().isoformat()
        return context
    
    def summarize_context(context):
        print("  [Hook 3] Summarizing context:")
        for key, value in context.items():
            print(f"    - {key}: {value}")
        return context
    
    manager.register_function(HookPoint.BEFORE_GENERATE, "add_metadata", add_metadata, priority=10)
    manager.register_function(HookPoint.BEFORE_GENERATE, "add_timestamp", add_timestamp, priority=20)
    manager.register_function(HookPoint.BEFORE_GENERATE, "summarize", summarize_context, priority=30)
    
    print("Executing hooks with context propagation...")
    result = manager.execute(HookPoint.BEFORE_GENERATE, {'initial_data': 'test'})
    print()


def demo_shell_hooks():
    """Demonstrate shell command hooks."""
    print("=" * 70)
    print("SHELL HOOKS DEMONSTRATION")
    print("=" * 70)
    print()
    
    manager = HooksManager()
    manager.clear_hooks()
    
    # Register shell hooks
    manager.register_shell(
        HookPoint.BEFORE_EXPORT,
        "create_output_dir",
        "echo 'Creating output directory...' && mkdir -p /tmp/accudoc_output 2>/dev/null || true",
        priority=10
    )
    
    manager.register_shell(
        HookPoint.AFTER_EXPORT,
        "list_output",
        "echo 'Listing output directory...' && ls -la /tmp/accudoc_output 2>/dev/null || echo 'Directory not found'",
        priority=10
    )
    
    print("Executing shell hooks...")
    print("\nBEFORE_EXPORT hooks:")
    result = manager.execute(HookPoint.BEFORE_EXPORT)
    
    print("\nAFTER_EXPORT hooks:")
    result = manager.execute(HookPoint.AFTER_EXPORT)
    print()


def demo_enable_disable():
    """Demonstrate enabling and disabling hooks."""
    print("=" * 70)
    print("ENABLE/DISABLE HOOKS DEMONSTRATION")
    print("=" * 70)
    print()
    
    manager = HooksManager()
    manager.clear_hooks()
    
    def my_hook(context):
        print("  [Hook] This hook is enabled!")
        return context
    
    manager.register_function(HookPoint.BEFORE_SCAN, "my_hook", my_hook)
    
    print("Executing hook (enabled)...")
    manager.execute(HookPoint.BEFORE_SCAN)
    
    print("\nDisabling hook...")
    manager.disable_hook(HookPoint.BEFORE_SCAN, "my_hook")
    
    print("Executing hook (disabled - should not print)...")
    manager.execute(HookPoint.BEFORE_SCAN)
    
    print("\nRe-enabling hook...")
    manager.enable_hook(HookPoint.BEFORE_SCAN, "my_hook")
    
    print("Executing hook (enabled again)...")
    manager.execute(HookPoint.BEFORE_SCAN)
    print()


def demo_error_handling():
    """Demonstrate error handling in hooks."""
    print("=" * 70)
    print("ERROR HANDLING DEMONSTRATION")
    print("=" * 70)
    print()
    
    manager = HooksManager()
    manager.clear_hooks()
    
    def failing_hook(context):
        print("  [Hook 1] This hook will fail...")
        raise ValueError("Intentional error for demonstration")
    
    def successful_hook(context):
        print("  [Hook 2] This hook runs successfully despite previous failure")
        context['success'] = True
        return context
    
    manager.register_function(HookPoint.BEFORE_SCAN, "failing", failing_hook, priority=10)
    manager.register_function(HookPoint.BEFORE_SCAN, "success", successful_hook, priority=20)
    
    print("Executing hooks (one will fail, but execution continues)...")
    result = manager.execute(HookPoint.BEFORE_SCAN)
    print(f"\nFinal context: {result}")
    print("Notice: Hook 2 executed successfully even though Hook 1 failed")
    print()


def demo_all_hook_points():
    """Demonstrate all available hook points."""
    print("=" * 70)
    print("AVAILABLE HOOK POINTS")
    print("=" * 70)
    print()
    
    print("AccuDoc supports hooks at the following points:")
    print()
    
    for hook_point in HookPoint:
        print(f"  • {hook_point.name:25s} - {hook_point.value}")
    
    print()
    print("You can register hooks at any of these points to extend AccuDoc's functionality.")
    print()


def demo_practical_example():
    """Demonstrate a practical use case."""
    print("=" * 70)
    print("PRACTICAL EXAMPLE: Documentation Pipeline")
    print("=" * 70)
    print()
    
    manager = HooksManager()
    manager.clear_hooks()
    
    # Practical hooks for a documentation pipeline
    def validate_repo_path(context):
        path = context.get('path', '')
        print(f"  ✓ Validating repository path: {path}")
        context['path_validated'] = True
        return context
    
    def log_scan_progress(context):
        print(f"  ✓ Logging scan progress...")
        context['scan_logged'] = True
        return context
    
    def optimize_output(context):
        print(f"  ✓ Optimizing generated documentation...")
        context['output_optimized'] = True
        return context
    
    def notify_completion(context):
        print(f"  ✓ Sending completion notification...")
        print(f"    Documentation generated successfully!")
        context['notification_sent'] = True
        return context
    
    # Register the pipeline hooks
    manager.register_function(HookPoint.BEFORE_SCAN, "validate", validate_repo_path, priority=5)
    manager.register_function(HookPoint.AFTER_SCAN, "log", log_scan_progress, priority=10)
    manager.register_function(HookPoint.AFTER_GENERATE, "optimize", optimize_output, priority=10)
    manager.register_function(HookPoint.AFTER_EXPORT, "notify", notify_completion, priority=90)
    
    print("Running documentation pipeline with hooks...\n")
    
    context = {'path': '/path/to/my/repo'}
    
    print("1. Before Scan:")
    context = manager.execute(HookPoint.BEFORE_SCAN, context)
    
    print("\n2. After Scan:")
    context = manager.execute(HookPoint.AFTER_SCAN, context)
    
    print("\n3. After Generate:")
    context = manager.execute(HookPoint.AFTER_GENERATE, context)
    
    print("\n4. After Export:")
    context = manager.execute(HookPoint.AFTER_EXPORT, context)
    
    print(f"\nFinal pipeline context: {context}")
    print()


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ACCUDOC HOOKS SYSTEM DEMO" + " " * 28 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    demos = [
        ("Basic Hooks", demo_basic_hooks),
        ("Hook Priority", demo_hook_priority),
        ("Context Propagation", demo_context_propagation),
        ("Shell Hooks", demo_shell_hooks),
        ("Enable/Disable", demo_enable_disable),
        ("Error Handling", demo_error_handling),
        ("Available Hook Points", demo_all_hook_points),
        ("Practical Example", demo_practical_example),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'─' * 70}")
        print(f"Demo {i}/{len(demos)}: {name}")
        print('─' * 70)
        print()
        
        try:
            demo_func()
        except Exception as e:
            print(f"Error in demo: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos):
            input("\nPress Enter to continue to the next demo...")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("For more information, see the AccuDoc documentation.")
    print()


if __name__ == '__main__':
    main()
