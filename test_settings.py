"""
Tests for settings export/import functionality.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.settings import (
    AccuDocSettings, SettingsManager, 
    export_settings, import_settings
)


def test_default_settings():
    """Test default settings creation."""
    print("=" * 60)
    print("Test 1: Default Settings")
    print("=" * 60)
    
    settings = AccuDocSettings()
    
    # Check defaults
    assert settings.default_template == 'detailed'
    assert settings.default_format == 'markdown'
    assert settings.markdown_flavor == 'github'
    assert settings.enable_cache == True
    assert settings.enable_secret_scanning == True
    assert len(settings.exclude_patterns) > 0
    
    print(f"✓ Default template: {settings.default_template}")
    print(f"✓ Default format: {settings.default_format}")
    print(f"✓ Markdown flavor: {settings.markdown_flavor}")
    print(f"✓ Cache enabled: {settings.enable_cache}")
    print(f"✓ Secret scanning enabled: {settings.enable_secret_scanning}")
    print(f"✓ Exclude patterns: {len(settings.exclude_patterns)} patterns")
    
    print("\n✓ Test PASSED: Default settings working\n")
    return True


def test_json_export():
    """Test JSON export."""
    print("=" * 60)
    print("Test 2: JSON Export")
    print("=" * 60)
    
    settings = AccuDocSettings(
        default_template='simple',
        default_format='html',
        html_theme='dark'
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / 'settings.json'
        
        manager = SettingsManager()
        result = manager.export_settings(settings, output_file, format='json')
        
        assert result.exists(), "Export file should exist"
        
        # Read and verify
        with open(result, 'r') as f:
            data = json.load(f)
        
        assert data['default_template'] == 'simple'
        assert data['default_format'] == 'html'
        assert data['html_theme'] == 'dark'
        assert 'export_date' in data
        
        print(f"✓ Exported to: {result}")
        print(f"✓ File size: {result.stat().st_size} bytes")
        print(f"✓ Settings preserved correctly")
    
    print("\n✓ Test PASSED: JSON export working\n")
    return True


def test_yaml_export():
    """Test YAML export."""
    print("=" * 60)
    print("Test 3: YAML Export")
    print("=" * 60)
    
    settings = AccuDocSettings(
        default_template='readme',
        include_toc=False,
        include_badges=False
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / 'settings.yaml'
        
        manager = SettingsManager()
        result = manager.export_settings(settings, output_file, format='yaml')
        
        assert result.exists(), "Export file should exist"
        
        # Read content
        content = result.read_text()
        assert 'default_template:' in content
        assert 'readme' in content
        
        print(f"✓ Exported to: {result}")
        print(f"✓ YAML format valid")
    
    print("\n✓ Test PASSED: YAML export working\n")
    return True


def test_json_import():
    """Test JSON import."""
    print("=" * 60)
    print("Test 4: JSON Import")
    print("=" * 60)
    
    # Create settings and export
    original = AccuDocSettings(
        default_template='custom',
        default_format='pdf',
        enable_cache=False
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_file = Path(tmpdir) / 'test_settings.json'
        
        manager = SettingsManager()
        manager.export_settings(original, settings_file, format='json')
        
        # Import
        imported = manager.import_settings(settings_file)
        
        # Verify
        assert imported.default_template == 'custom'
        assert imported.default_format == 'pdf'
        assert imported.enable_cache == False
        
        print(f"✓ Imported from: {settings_file}")
        print(f"✓ Settings match original")
    
    print("\n✓ Test PASSED: JSON import working\n")
    return True


def test_yaml_import():
    """Test YAML import."""
    print("=" * 60)
    print("Test 5: YAML Import")
    print("=" * 60)
    
    original = AccuDocSettings(
        markdown_flavor='gitlab',
        html_theme='minimal',
        max_file_size_mb=20
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_file = Path(tmpdir) / 'test_settings.yml'
        
        manager = SettingsManager()
        manager.export_settings(original, settings_file, format='yaml')
        
        # Import
        imported = manager.import_settings(settings_file)
        
        # Verify
        assert imported.markdown_flavor == 'gitlab'
        assert imported.html_theme == 'minimal'
        assert imported.max_file_size_mb == 20
        
        print(f"✓ Imported from: {settings_file}")
        print(f"✓ Settings match original")
    
    print("\n✓ Test PASSED: YAML import working\n")
    return True


def test_secrets_exclusion():
    """Test that secrets can be excluded from export."""
    print("=" * 60)
    print("Test 6: Secrets Exclusion")
    print("=" * 60)
    
    settings = AccuDocSettings(
        github_token='ghp_secret_token_123',
        gitlab_token='glpat_secret_456',
        bitbucket_username='user123',
        bitbucket_app_password='app_pass_789'
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Export without secrets
        no_secrets_file = Path(tmpdir) / 'no_secrets.json'
        manager = SettingsManager()
        manager.export_settings(settings, no_secrets_file, 
                              format='json', include_secrets=False)
        
        # Verify secrets are not in file
        content = no_secrets_file.read_text()
        assert 'ghp_secret_token' not in content
        assert 'glpat_secret' not in content
        assert 'app_pass_789' not in content
        
        # Export with secrets
        with_secrets_file = Path(tmpdir) / 'with_secrets.json'
        manager.export_settings(settings, with_secrets_file,
                              format='json', include_secrets=True)
        
        # Verify secrets are in file
        content = with_secrets_file.read_text()
        assert 'ghp_secret_token_123' in content
        assert 'glpat_secret_456' in content
        
        print(f"✓ Secrets excluded when requested")
        print(f"✓ Secrets included when requested")
    
    print("\n✓ Test PASSED: Secrets exclusion working\n")
    return True


def test_validation():
    """Test settings validation."""
    print("=" * 60)
    print("Test 7: Settings Validation")
    print("=" * 60)
    
    manager = SettingsManager()
    
    # Valid settings
    valid = AccuDocSettings(
        default_format='markdown',
        markdown_flavor='github',
        html_theme='default'
    )
    
    try:
        manager._validate_settings(valid)
        print(f"✓ Valid settings passed validation")
    except ValueError as e:
        print(f"✗ Valid settings failed: {e}")
        return False
    
    # Invalid format
    invalid_format = AccuDocSettings(default_format='invalid_format')
    try:
        manager._validate_settings(invalid_format)
        print(f"✗ Invalid format should have failed")
        return False
    except ValueError:
        print(f"✓ Invalid format caught")
    
    # Invalid markdown flavor
    invalid_flavor = AccuDocSettings(markdown_flavor='invalid')
    try:
        manager._validate_settings(invalid_flavor)
        print(f"✗ Invalid flavor should have failed")
        return False
    except ValueError:
        print(f"✓ Invalid flavor caught")
    
    print("\n✓ Test PASSED: Validation working\n")
    return True


def test_merge_settings():
    """Test merging settings."""
    print("=" * 60)
    print("Test 8: Settings Merging")
    print("=" * 60)
    
    base = AccuDocSettings(
        default_template='detailed',
        default_format='markdown',
        enable_cache=True
    )
    
    override = AccuDocSettings(
        default_format='html',  # Override this
        html_theme='dark'  # Add this
    )
    
    manager = SettingsManager()
    merged = manager.merge_settings(base, override)
    
    # Check merged values
    assert merged.default_template == 'detailed'  # From base
    assert merged.default_format == 'html'  # From override
    assert merged.html_theme == 'dark'  # From override
    assert merged.enable_cache == True  # From base
    
    print(f"✓ Base settings preserved")
    print(f"✓ Override settings applied")
    print(f"✓ Merge successful")
    
    print("\n✓ Test PASSED: Settings merging working\n")
    return True


def test_template_export():
    """Test template export."""
    print("=" * 60)
    print("Test 9: Template Export")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_template = Path(tmpdir) / 'template.yaml'
        json_template = Path(tmpdir) / 'template.json'
        
        manager = SettingsManager()
        
        # Export YAML template
        manager.export_template(yaml_template, format='yaml')
        assert yaml_template.exists()
        content = yaml_template.read_text()
        assert '#' in content, "YAML template should have comments"
        print(f"✓ YAML template created with comments")
        
        # Export JSON template
        manager.export_template(json_template, format='json')
        assert json_template.exists()
        with open(json_template, 'r') as f:
            data = json.load(f)
        assert '_comments' in data, "JSON template should have comments field"
        print(f"✓ JSON template created with comments")
    
    print("\n✓ Test PASSED: Template export working\n")
    return True


def test_convenience_functions():
    """Test convenience functions."""
    print("=" * 60)
    print("Test 10: Convenience Functions")
    print("=" * 60)
    
    settings = AccuDocSettings(default_template='test')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_file = Path(tmpdir) / 'convenience.json'
        
        # Export using convenience function
        result = export_settings(settings, settings_file, format='json')
        assert result.exists()
        print(f"✓ Convenience export function works")
        
        # Import using convenience function
        imported = import_settings(settings_file)
        assert imported.default_template == 'test'
        print(f"✓ Convenience import function works")
    
    print("\n✓ Test PASSED: Convenience functions working\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc Settings Export/Import Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_default_settings,
        test_json_export,
        test_yaml_export,
        test_json_import,
        test_yaml_import,
        test_secrets_exclusion,
        test_validation,
        test_merge_settings,
        test_template_export,
        test_convenience_functions,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test failed with exception: {str(e)}\n")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
