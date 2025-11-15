#!/usr/bin/env python3
"""Test script for GitHub API integration and plugin system."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.github_api import GitHubAPIClient
from accudoc.plugins import (
    PluginManager, AnalyzerPlugin, ExporterPlugin,
    TemplatePlugin, MarkdownLintAnalyzer
)


def test_github_api_url_parsing():
    """Test GitHub URL parsing."""
    print("=" * 60)
    print("Test 1: GitHub URL Parsing")
    print("=" * 60)
    
    try:
        client = GitHubAPIClient()
        
        # Test various URL formats
        test_cases = [
            ('https://github.com/owner/repo', ('owner', 'repo')),
            ('https://github.com/owner/repo/', ('owner', 'repo')),
            ('https://github.com/owner/repo.git', ('owner', 'repo')),
            ('git@github.com:owner/repo.git', ('owner', 'repo')),
        ]
        
        for url, expected in test_cases:
            result = client.parse_github_url(url)
            if result == expected:
                print(f"✓ Parsed {url} correctly")
            else:
                print(f"✗ Failed to parse {url}: got {result}, expected {expected}")
                return False
        
        print("\n✓ Test PASSED: URL parsing working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_plugin_manager():
    """Test plugin manager."""
    print("\n" + "=" * 60)
    print("Test 2: Plugin Manager")
    print("=" * 60)
    
    try:
        manager = PluginManager()
        
        # Create a test analyzer
        analyzer = MarkdownLintAnalyzer()
        
        # Register it
        manager.register_analyzer(analyzer)
        
        # Check if registered
        plugins = manager.list_plugins()
        if 'markdown-lint' in plugins['analyzers']:
            print("✓ Analyzer registered successfully")
        else:
            print("✗ Analyzer registration failed")
            return False
        
        # Get the analyzer
        retrieved = manager.get_analyzer('markdown-lint')
        if retrieved is not None:
            print("✓ Analyzer retrieved successfully")
        else:
            print("✗ Analyzer retrieval failed")
            return False
        
        # Test file support
        md_file = Path("test.md")
        py_file = Path("test.py")
        
        if analyzer.supports_file(md_file):
            print("✓ Supports .md files")
        else:
            print("✗ Should support .md files")
            return False
        
        if not analyzer.supports_file(py_file):
            print("✓ Doesn't support .py files")
        else:
            print("✗ Should not support .py files")
            return False
        
        print("\n✓ Test PASSED: Plugin manager working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_markdown_lint_analyzer():
    """Test Markdown lint analyzer."""
    print("\n" + "=" * 60)
    print("Test 3: Markdown Lint Analyzer")
    print("=" * 60)
    
    try:
        analyzer = MarkdownLintAnalyzer()
        
        # Test with problematic markdown
        test_content = """# Test Document

This line has trailing spaces   

This is fine.


Multiple blank lines above.
"""
        
        result = analyzer.analyze(Path("test.md"), test_content)
        
        if 'issues' in result:
            print(f"✓ Analysis completed: {result['issue_count']} issues found")
        else:
            print("✗ Analysis failed")
            return False
        
        # Should find trailing whitespace
        trailing_ws = any(issue['type'] == 'trailing-whitespace' for issue in result['issues'])
        if trailing_ws:
            print("✓ Detected trailing whitespace")
        else:
            print("⚠ Should detect trailing whitespace")
        
        # Should find consecutive blank lines
        blank_lines = any(issue['type'] == 'consecutive-blank-lines' for issue in result['issues'])
        if blank_lines:
            print("✓ Detected consecutive blank lines")
        else:
            print("⚠ Should detect consecutive blank lines")
        
        print("\n✓ Test PASSED: Markdown lint analyzer working")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_plugin_info():
    """Test plugin information retrieval."""
    print("\n" + "=" * 60)
    print("Test 4: Plugin Information")
    print("=" * 60)
    
    try:
        manager = PluginManager()
        analyzer = MarkdownLintAnalyzer()
        manager.register_analyzer(analyzer)
        
        # Get plugin info
        info = manager.get_plugin_info()
        
        if len(info) > 0:
            print(f"✓ Retrieved info for {len(info)} plugin(s)")
        else:
            print("✗ No plugin info retrieved")
            return False
        
        # Check info structure
        first_plugin = info[0]
        required_fields = ['type', 'name', 'version', 'description']
        
        if all(field in first_plugin for field in required_fields):
            print("✓ Plugin info has all required fields")
        else:
            print("✗ Plugin info missing required fields")
            return False
        
        print(f"  Plugin: {first_plugin['name']} v{first_plugin['version']}")
        print(f"  Type: {first_plugin['type']}")
        print(f"  Description: {first_plugin['description']}")
        
        print("\n✓ Test PASSED: Plugin information system working")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc GitHub API & Plugins Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_github_api_url_parsing,
        test_plugin_manager,
        test_markdown_lint_analyzer,
        test_plugin_info,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"\nPassed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
