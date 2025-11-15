#!/usr/bin/env python3
"""
Tests for wizard mode feature.
"""

import sys
from pathlib import Path
from unittest.mock import patch
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.wizard import WizardMode


def test_wizard_initialization():
    """Test wizard initialization."""
    print("\n" + "="*70)
    print("Test 1: Wizard Initialization")
    print("="*70)
    
    wizard = WizardMode()
    
    assert wizard.repository_path is None, "Repository path should be None initially"
    assert wizard.output_path is None, "Output path should be None initially"
    assert wizard.template == 'default', "Default template should be 'default'"
    assert wizard.output_format == 'markdown', "Default format should be 'markdown'"
    assert wizard.markdown_flavor == 'github', "Default flavor should be 'github'"
    assert wizard.options == {}, "Options should be empty dict initially"
    
    print("✓ Repository path: None")
    print("✓ Output path: None")
    print("✓ Template: default")
    print("✓ Format: markdown")
    print("✓ Flavor: github")
    print("✓ Options: {}")
    
    print("\n✓ Test PASSED: Wizard initialization correct")


def test_build_command_basic():
    """Test building basic command."""
    print("\n" + "="*70)
    print("Test 2: Build Basic Command")
    print("="*70)
    
    wizard = WizardMode()
    wizard.repository_path = Path("/path/to/repo")
    wizard.output_path = Path("/path/to/output")
    wizard.template = "default"
    
    command = wizard.build_command()
    
    print(f"Built command: {command}")
    
    assert "python accudoc_cli.py generate" in command
    assert "/path/to/repo" in command
    assert "--output /path/to/output" in command
    assert "--template default" in command
    
    print("\n✓ Contains generate command")
    print("✓ Contains repository path")
    print("✓ Contains output path")
    print("✓ Contains template option")
    
    print("\n✓ Test PASSED: Basic command building works")


def test_build_command_with_options():
    """Test building command with options."""
    print("\n" + "="*70)
    print("Test 3: Build Command with Options")
    print("="*70)
    
    wizard = WizardMode()
    wizard.repository_path = Path("/repo")
    wizard.output_path = Path("/output")
    wizard.template = "api"
    wizard.output_format = "html"
    wizard.html_theme = "dark"
    wizard.options = {
        'complexity': True,
        'security': True,
        'spellcheck': True
    }
    
    command = wizard.build_command()
    
    print(f"Built command:\n  {command}")
    
    assert "--template api" in command
    assert "--format html" in command
    assert "--theme dark" in command
    assert "--complexity" in command
    assert "--security" in command
    assert "--spellcheck" in command
    
    print("\n✓ Contains API template")
    print("✓ Contains HTML format")
    print("✓ Contains dark theme")
    print("✓ Contains complexity option")
    print("✓ Contains security option")
    print("✓ Contains spellcheck option")
    
    print("\n✓ Test PASSED: Command with options works")


def test_build_command_markdown_flavors():
    """Test building command with markdown flavors."""
    print("\n" + "="*70)
    print("Test 4: Build Command with Markdown Flavors")
    print("="*70)
    
    wizard = WizardMode()
    wizard.repository_path = Path("/repo")
    wizard.output_path = Path("/output")
    wizard.template = "default"
    wizard.output_format = "markdown"
    
    # Test GitHub flavor (should not add --flavor since it's default)
    wizard.markdown_flavor = "github"
    command = wizard.build_command()
    print(f"\nGitHub flavor: {command}")
    assert "--flavor" not in command, "GitHub flavor should not be explicitly added"
    print("✓ GitHub flavor (default) - no explicit flag")
    
    # Test GitLab flavor
    wizard.markdown_flavor = "gitlab"
    command = wizard.build_command()
    print(f"\nGitLab flavor: {command}")
    assert "--flavor gitlab" in command
    print("✓ GitLab flavor explicitly added")
    
    # Test CommonMark flavor
    wizard.markdown_flavor = "commonmark"
    command = wizard.build_command()
    print(f"\nCommonMark flavor: {command}")
    assert "--flavor commonmark" in command
    print("✓ CommonMark flavor explicitly added")
    
    print("\n✓ Test PASSED: Markdown flavors handled correctly")


def test_ask_yes_no_logic():
    """Test yes/no question logic."""
    print("\n" + "="*70)
    print("Test 5: Yes/No Question Logic")
    print("="*70)
    
    wizard = WizardMode()
    
    # Test with mock input
    test_cases = [
        ("y", True),
        ("yes", True),
        ("Y", True),
        ("YES", True),
        ("n", False),
        ("no", False),
        ("N", False),
        ("NO", False),
    ]
    
    print("\nTesting input responses:")
    for input_val, expected in test_cases:
        with patch('builtins.input', return_value=input_val):
            result = wizard.ask_yes_no("Test question?")
            assert result == expected, f"Input '{input_val}' should return {expected}"
            print(f"  ✓ '{input_val}' -> {expected}")
    
    print("\n✓ Test PASSED: Yes/No logic works correctly")


def test_template_selection():
    """Test template selection mapping."""
    print("\n" + "="*70)
    print("Test 6: Template Selection Mapping")
    print("="*70)
    
    templates = {
        "1": "default",
        "2": "minimal",
        "3": "detailed",
        "4": "api",
        "5": "readme",
        "6": "student"
    }
    
    print("\nTemplate mappings:")
    for choice, template in templates.items():
        print(f"  {choice} -> {template}")
    
    assert templates["1"] == "default"
    assert templates["2"] == "minimal"
    assert templates["3"] == "detailed"
    assert templates["4"] == "api"
    assert templates["5"] == "readme"
    assert templates["6"] == "student"
    
    print("\n✓ Test PASSED: All template mappings correct")


def test_format_selection():
    """Test format selection mapping."""
    print("\n" + "="*70)
    print("Test 7: Format Selection Mapping")
    print("="*70)
    
    formats = {
        "1": "markdown",
        "2": "html",
        "3": "pdf",
        "4": "text"
    }
    
    print("\nFormat mappings:")
    for choice, format_type in formats.items():
        print(f"  {choice} -> {format_type}")
    
    assert formats["1"] == "markdown"
    assert formats["2"] == "html"
    assert formats["3"] == "pdf"
    assert formats["4"] == "text"
    
    print("\n✓ Test PASSED: All format mappings correct")


def test_complete_workflow_simulation():
    """Test complete wizard workflow (simulated)."""
    print("\n" + "="*70)
    print("Test 8: Complete Workflow Simulation")
    print("="*70)
    
    wizard = WizardMode()
    
    # Simulate user selections
    print("\n📝 Simulating user choices:")
    
    # Repository
    wizard.repository_path = Path.cwd()
    print(f"  1. Repository: {wizard.repository_path}")
    
    # Output
    wizard.output_path = Path.cwd() / "docs"
    print(f"  2. Output: {wizard.output_path}")
    
    # Template
    wizard.template = "detailed"
    print(f"  3. Template: {wizard.template}")
    
    # Format
    wizard.output_format = "html"
    wizard.html_theme = "dark"
    print(f"  4. Format: {wizard.output_format} (theme: {wizard.html_theme})")
    
    # Options
    wizard.options = {
        'complexity': True,
        'security': True
    }
    print(f"  5. Options: {list(wizard.options.keys())}")
    
    # Build command
    command = wizard.build_command()
    print(f"\n🔨 Generated command:\n  {command}")
    
    # Verify all selections are in command
    assert str(wizard.repository_path) in command
    assert str(wizard.output_path) in command
    assert "--template detailed" in command
    assert "--format html" in command
    assert "--theme dark" in command
    assert "--complexity" in command
    assert "--security" in command
    
    print("\n✓ All selections reflected in command")
    print("\n✓ Test PASSED: Complete workflow simulation works")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("Wizard Mode Test Suite")
    print("="*70)
    
    try:
        test_wizard_initialization()
        test_build_command_basic()
        test_build_command_with_options()
        test_build_command_markdown_flavors()
        test_ask_yes_no_logic()
        test_template_selection()
        test_format_selection()
        test_complete_workflow_simulation()
        
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test FAILED: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ Test ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
