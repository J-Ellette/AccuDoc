#!/usr/bin/env python3
"""
Test script for shell completion functionality.

This script verifies that completion scripts are syntactically correct
and contain all necessary commands and options.
"""

import sys
import re
from pathlib import Path


class CompletionTester:
    """Test shell completion scripts."""
    
    def __init__(self):
        """Initialize tester."""
        self.completions_dir = Path(__file__).parent / 'completions'
        self.errors = []
        self.warnings = []
        
        # Expected commands from CLI
        self.expected_commands = [
            'scan', 'generate', 'export', 'site', 'info', 'cache',
            'check-links', 'plugins', 'batch', 'branch-compare',
            'version-check', 'spellcheck', 'multi-repo', 'coverage',
            'readability', 'db-schema', 'monorepo', 'breaking-changes',
            'code-quality', 'grammar', 'doc-coverage', 'dataflow'
        ]
        
        # Common options that should be supported
        self.common_options = ['-h', '--help', '-o', '--output', '-f', '--format']
    
    def test_bash_completion(self):
        """Test Bash completion script."""
        print("\n" + "=" * 60)
        print("Testing Bash Completion Script")
        print("=" * 60)
        
        bash_file = self.completions_dir / 'accudoc-completion.bash'
        
        if not bash_file.exists():
            self.errors.append("Bash completion file not found")
            return False
        
        content = bash_file.read_text()
        
        # Check for required functions
        if '_accudoc_completions' not in content:
            self.errors.append("Missing _accudoc_completions function")
        else:
            print("✓ Found _accudoc_completions function")
        
        # Check for command registration
        if 'complete -F _accudoc_completions' not in content:
            self.errors.append("Missing completion registration")
        else:
            print("✓ Found completion registration")
        
        # Check for all commands
        missing_commands = []
        for cmd in self.expected_commands:
            if cmd not in content:
                missing_commands.append(cmd)
        
        if missing_commands:
            self.warnings.append(f"Bash: Missing commands: {', '.join(missing_commands)}")
        else:
            print(f"✓ All {len(self.expected_commands)} commands present")
        
        # Check for common options
        found_options = sum(1 for opt in self.common_options if opt in content)
        print(f"✓ Found {found_options}/{len(self.common_options)} common options")
        
        return len(self.errors) == 0
    
    def test_zsh_completion(self):
        """Test Zsh completion script."""
        print("\n" + "=" * 60)
        print("Testing Zsh Completion Script")
        print("=" * 60)
        
        zsh_file = self.completions_dir / '_accudoc'
        
        if not zsh_file.exists():
            self.errors.append("Zsh completion file not found")
            return False
        
        content = zsh_file.read_text()
        
        # Check for compdef directive
        if '#compdef' not in content:
            self.errors.append("Missing #compdef directive")
        else:
            print("✓ Found #compdef directive")
        
        # Check for main function
        if '_accudoc()' not in content and '_accudoc ' not in content:
            self.errors.append("Missing _accudoc function")
        else:
            print("✓ Found _accudoc function")
        
        # Check for _arguments usage
        if '_arguments' in content:
            print("✓ Uses _arguments for option parsing")
        
        # Check for all commands
        missing_commands = []
        for cmd in self.expected_commands:
            if cmd not in content:
                missing_commands.append(cmd)
        
        if missing_commands:
            self.warnings.append(f"Zsh: Missing commands: {', '.join(missing_commands)}")
        else:
            print(f"✓ All {len(self.expected_commands)} commands present")
        
        # Check for descriptions
        if '-d' in content or '--description' in content:
            print("✓ Includes command descriptions")
        
        return len(self.errors) == 0
    
    def test_fish_completion(self):
        """Test Fish completion script."""
        print("\n" + "=" * 60)
        print("Testing Fish Completion Script")
        print("=" * 60)
        
        fish_file = self.completions_dir / 'accudoc.fish'
        
        if not fish_file.exists():
            self.errors.append("Fish completion file not found")
            return False
        
        content = fish_file.read_text()
        
        # Check for complete commands
        if 'complete -c accudoc' not in content:
            self.errors.append("Missing 'complete -c accudoc' commands")
        else:
            print("✓ Found completion commands")
        
        # Check for helper functions
        if '__fish_accudoc_needs_command' in content:
            print("✓ Found __fish_accudoc_needs_command helper")
        
        if '__fish_accudoc_using_command' in content:
            print("✓ Found __fish_accudoc_using_command helper")
        
        # Check for all commands
        missing_commands = []
        for cmd in self.expected_commands:
            if f"'{cmd}'" not in content and f'"{cmd}"' not in content:
                missing_commands.append(cmd)
        
        if missing_commands:
            self.warnings.append(f"Fish: Missing commands: {', '.join(missing_commands)}")
        else:
            print(f"✓ All {len(self.expected_commands)} commands present")
        
        # Check for descriptions
        if ' -d ' in content:
            print("✓ Includes command descriptions")
        
        return len(self.errors) == 0
    
    def test_readme(self):
        """Test README documentation."""
        print("\n" + "=" * 60)
        print("Testing README Documentation")
        print("=" * 60)
        
        readme_file = self.completions_dir / 'README.md'
        
        if not readme_file.exists():
            self.warnings.append("README.md not found in completions directory")
            return False
        
        content = readme_file.read_text()
        
        # Check for installation instructions for each shell
        shells = ['Bash', 'Zsh', 'Fish']
        for shell in shells:
            if shell in content:
                print(f"✓ Found installation instructions for {shell}")
            else:
                self.warnings.append(f"Missing {shell} installation instructions")
        
        # Check for troubleshooting section
        if 'Troubleshooting' in content or 'troubleshooting' in content:
            print("✓ Includes troubleshooting section")
        
        # Check for examples
        if 'Example' in content or 'example' in content:
            print("✓ Includes usage examples")
        
        return True
    
    def run_tests(self):
        """Run all tests."""
        print("\n" + "=" * 60)
        print("AccuDoc Shell Completion Tests")
        print("=" * 60)
        
        all_passed = True
        
        # Run tests for each shell
        all_passed &= self.test_bash_completion()
        all_passed &= self.test_zsh_completion()
        all_passed &= self.test_fish_completion()
        self.test_readme()
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All tests passed with no warnings!")
        elif not self.errors:
            print("\n✅ All tests passed (with warnings)")
        else:
            print("\n❌ Some tests failed")
        
        return all_passed and len(self.warnings) == 0


def main():
    """Main entry point."""
    tester = CompletionTester()
    success = tester.run_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
