"""
Git hooks integration for AccuDoc.

Provides pre-commit and post-commit hooks for automatic documentation updates.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class GitHooks:
    """Manage Git hooks for automated documentation."""
    
    HOOK_TYPES = {
        'pre-commit': 'Run before commit (validate docs)',
        'post-commit': 'Run after commit (update docs)',
        'pre-push': 'Run before push (ensure docs are current)',
    }
    
    def __init__(self, repo_path: str = '.'):
        self.repo_path = Path(repo_path).resolve()
        self.hooks_dir = self.repo_path / '.git' / 'hooks'
        self.accudoc_cli = Path(__file__).parent.parent / 'accudoc_cli.py'
    
    def install_hooks(self, hook_types: Optional[list] = None) -> dict:
        """
        Install AccuDoc git hooks.
        
        Args:
            hook_types: List of hook types to install (default: all)
        
        Returns:
            dict: Installation results for each hook
        """
        if hook_types is None:
            hook_types = list(self.HOOK_TYPES.keys())
        
        if not self.hooks_dir.exists():
            return {'error': 'Not a git repository'}
        
        results = {}
        for hook_type in hook_types:
            if hook_type not in self.HOOK_TYPES:
                results[hook_type] = {'success': False, 'error': 'Unknown hook type'}
                continue
            
            hook_path = self.hooks_dir / hook_type
            hook_content = self._generate_hook_script(hook_type)
            
            try:
                # Backup existing hook
                if hook_path.exists():
                    backup_path = hook_path.with_suffix('.backup')
                    hook_path.rename(backup_path)
                    results[hook_type] = {'backup': str(backup_path)}
                
                # Write new hook
                hook_path.write_text(hook_content)
                hook_path.chmod(0o755)  # Make executable
                
                results[hook_type] = {
                    'success': True,
                    'path': str(hook_path),
                    'description': self.HOOK_TYPES[hook_type]
                }
            except Exception as e:
                results[hook_type] = {'success': False, 'error': str(e)}
        
        return results
    
    def uninstall_hooks(self, hook_types: Optional[list] = None) -> dict:
        """Remove AccuDoc git hooks and restore backups."""
        if hook_types is None:
            hook_types = list(self.HOOK_TYPES.keys())
        
        results = {}
        for hook_type in hook_types:
            hook_path = self.hooks_dir / hook_type
            backup_path = hook_path.with_suffix('.backup')
            
            try:
                if hook_path.exists():
                    hook_path.unlink()
                
                # Restore backup if exists
                if backup_path.exists():
                    backup_path.rename(hook_path)
                    results[hook_type] = {'restored_backup': True}
                else:
                    results[hook_type] = {'removed': True}
            except Exception as e:
                results[hook_type] = {'error': str(e)}
        
        return results
    
    def _generate_hook_script(self, hook_type: str) -> str:
        """Generate shell script for a specific hook type."""
        if hook_type == 'pre-commit':
            return self._pre_commit_script()
        elif hook_type == 'post-commit':
            return self._post_commit_script()
        elif hook_type == 'pre-push':
            return self._pre_push_script()
        return ''
    
    def _pre_commit_script(self) -> str:
        """Pre-commit hook: validate documentation exists and is current."""
        return f'''#!/bin/bash
# AccuDoc Pre-Commit Hook
# Validates documentation before commit

set -e

echo "🔍 AccuDoc: Checking documentation..."

# Check if README exists
if [ ! -f "README.md" ] && [ ! -f "DOCUMENTATION.md" ]; then
    echo "⚠️  No documentation found. Run 'python {self.accudoc_cli} export .' to generate."
    echo "   Commit will proceed, but documentation is recommended."
fi

# Check for broken links (if docs exist)
if [ -f "README.md" ]; then
    python {self.accudoc_cli} check-links README.md --quiet || echo "⚠️  Found broken links in documentation"
fi

# Validate completeness (non-blocking)
python {self.accudoc_cli} completeness . --threshold 50 --quiet || {{
    echo "⚠️  Documentation completeness below 50%"
    echo "   Consider improving documentation before commit"
}}

echo "✅ Pre-commit checks complete"
exit 0
'''
    
    def _post_commit_script(self) -> str:
        """Post-commit hook: update documentation after successful commit."""
        return f'''#!/bin/bash
# AccuDoc Post-Commit Hook
# Auto-updates documentation after commit

echo "📝 AccuDoc: Updating documentation..."

# Only update docs if source files changed
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Check if code files changed (not just docs)
if echo "$CHANGED_FILES" | grep -qE '\\.(py|js|ts|java|go|rs|cpp|c|h)$'; then
    echo "   Code changes detected, regenerating documentation..."
    
    # Generate updated docs
    python {self.accudoc_cli} export . -o DOCUMENTATION.md --no-cache --quiet
    
    # Check if docs changed
    if git diff --quiet DOCUMENTATION.md; then
        echo "   Documentation is up to date"
    else
        echo "   Documentation updated (not committed)"
        echo "   Run 'git add DOCUMENTATION.md && git commit --amend' to include in this commit"
    fi
else
    echo "   No code changes, skipping doc update"
fi

echo "✅ Post-commit hook complete"
exit 0
'''
    
    def _pre_push_script(self) -> str:
        """Pre-push hook: ensure docs are current before pushing."""
        return f'''#!/bin/bash
# AccuDoc Pre-Push Hook
# Ensures documentation is current before push

echo "🚀 AccuDoc: Checking documentation before push..."

# Run health check
HEALTH_OUTPUT=$(python {self.accudoc_cli} health . --json 2>/dev/null)
HEALTH_SCORE=$(echo "$HEALTH_OUTPUT" | python -c "import sys, json; print(json.load(sys.stdin).get('health_score', 0))" 2>/dev/null || echo "0")

if [ "$HEALTH_SCORE" -lt 50 ]; then
    echo "⚠️  Warning: Project health score is $HEALTH_SCORE/100"
    echo "   Consider improving documentation before pushing"
    read -p "   Continue with push? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Push cancelled"
        exit 1
    fi
fi

echo "✅ Pre-push checks complete"
exit 0
'''
    
    def list_installed_hooks(self) -> dict:
        """List all installed AccuDoc hooks."""
        hooks = {}
        for hook_type in self.HOOK_TYPES:
            hook_path = self.hooks_dir / hook_type
            if hook_path.exists():
                content = hook_path.read_text()
                is_accudoc = 'AccuDoc' in content
                hooks[hook_type] = {
                    'installed': True,
                    'is_accudoc': is_accudoc,
                    'path': str(hook_path)
                }
            else:
                hooks[hook_type] = {'installed': False}
        
        return hooks


def install_hooks_command(repo_path: str = '.', hooks: Optional[list] = None) -> int:
    """CLI command to install git hooks."""
    manager = GitHooks(repo_path)
    
    print("Installing AccuDoc git hooks...")
    results = manager.install_hooks(hooks)
    
    for hook_type, result in results.items():
        if result.get('success'):
            print(f"✅ {hook_type}: {result.get('description')}")
            print(f"   Installed at: {result['path']}")
            if 'backup' in result:
                print(f"   Backed up existing hook: {result['backup']}")
        else:
            print(f"❌ {hook_type}: {result.get('error', 'Failed')}")
    
    return 0 if all(r.get('success') for r in results.values()) else 1


def uninstall_hooks_command(repo_path: str = '.', hooks: Optional[list] = None) -> int:
    """CLI command to uninstall git hooks."""
    manager = GitHooks(repo_path)
    
    print("Uninstalling AccuDoc git hooks...")
    results = manager.uninstall_hooks(hooks)
    
    for hook_type, result in results.items():
        if 'error' not in result:
            if result.get('restored_backup'):
                print(f"✅ {hook_type}: Removed and restored backup")
            else:
                print(f"✅ {hook_type}: Removed")
        else:
            print(f"❌ {hook_type}: {result['error']}")
    
    return 0


def list_hooks_command(repo_path: str = '.') -> int:
    """CLI command to list installed hooks."""
    manager = GitHooks(repo_path)
    hooks = manager.list_installed_hooks()
    
    print("Git Hooks Status:")
    for hook_type, info in hooks.items():
        if info['installed']:
            status = "✅ Installed" if info['is_accudoc'] else "⚠️  Installed (non-AccuDoc)"
            print(f"  {hook_type}: {status}")
            print(f"    Path: {info['path']}")
        else:
            print(f"  {hook_type}: ❌ Not installed")
    
    return 0
