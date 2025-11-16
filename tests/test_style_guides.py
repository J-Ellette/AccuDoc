#!/usr/bin/env python3
"""
Tests for style guide enforcement feature.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from accudoc.style_guides import (
    get_style_guide,
    list_style_guides,
    GoogleStyleGuide,
    MicrosoftStyleGuide,
    PlainLanguageGuide
)
from accudoc.doc_validator import DocumentationValidator


def test_list_style_guides():
    """Test listing available style guides."""
    print("\n" + "="*70)
    print("Test 1: List Available Style Guides")
    print("="*70)
    
    guides = list_style_guides()
    
    print(f"✓ Found {len(guides)} style guides:")
    for guide in guides:
        print(f"  - {guide['name']}: {guide['title']}")
        print(f"      {guide['description']}")
        print(f"      Rules: {guide['rule_count']}")
    
    assert len(guides) >= 3, "Should have at least 3 style guides"
    assert any(g['name'] == 'google' for g in guides), "Should have Google guide"
    assert any(g['name'] == 'microsoft' for g in guides), "Should have Microsoft guide"
    assert any(g['name'] == 'plain-language' for g in guides), "Should have Plain Language guide"
    
    print("\n✓ Test PASSED: Style guide listing works")


def test_google_style_guide():
    """Test Google style guide."""
    print("\n" + "="*70)
    print("Test 2: Google Developer Documentation Style Guide")
    print("="*70)
    
    guide = GoogleStyleGuide()
    
    print(f"✓ Name: {guide.name}")
    print(f"✓ Description: {guide.description}")
    print(f"✓ Rules: {len(guide.get_rules())}")
    
    # Test with sample content that violates Google style
    content = """# Documentation

Please follow these instructions carefully!

The function will return a value.

We recommend using this approach.
"""
    
    validator = DocumentationValidator()
    for rule in guide.get_rules():
        validator.add_rule(rule)
    
    issues = validator.validate(content, 
                                check_links=False,
                                check_syntax=False,
                                check_structure=False,
                                check_content=False)
    
    print(f"\n✓ Found {len(issues)} style issues:")
    for issue in issues[:5]:  # Show first 5
        print(f"  - Line {issue.line_number}: {issue.message}")
    
    assert len(issues) > 0, "Should find style violations"
    
    print("\n✓ Test PASSED: Google style guide working")


def test_microsoft_style_guide():
    """Test Microsoft style guide."""
    print("\n" + "="*70)
    print("Test 3: Microsoft Writing Style Guide")
    print("="*70)
    
    guide = MicrosoftStyleGuide()
    
    print(f"✓ Name: {guide.name}")
    print(f"✓ Description: {guide.description}")
    print(f"✓ Rules: {len(guide.get_rules())}")
    
    # Test with sample content
    content = """# Documentation

In order to configure the system, you should use the following steps.

Due to the fact that the system is complex, make use of the documentation.

Don't use the old method, it doesn't work.
"""
    
    validator = DocumentationValidator()
    for rule in guide.get_rules():
        validator.add_rule(rule)
    
    issues = validator.validate(content,
                                check_links=False,
                                check_syntax=False,
                                check_structure=False,
                                check_content=False)
    
    print(f"\n✓ Found {len(issues)} style issues:")
    for issue in issues[:5]:
        print(f"  - Line {issue.line_number}: {issue.message}")
    
    assert len(issues) > 0, "Should find style violations"
    
    print("\n✓ Test PASSED: Microsoft style guide working")


def test_plain_language_guide():
    """Test Plain Language guide."""
    print("\n" + "="*70)
    print("Test 4: Plain Language Guidelines")
    print("="*70)
    
    guide = PlainLanguageGuide()
    
    print(f"✓ Name: {guide.name}")
    print(f"✓ Description: {guide.description}")
    print(f"✓ Rules: {len(guide.get_rules())}")
    
    # Test with sample content
    content = """# Documentation

In order to utilize the system effectively, you must commence by implementing 
the configuration and then endeavor to ascertain the optimal settings that will
facilitate the most efficient utilization of resources in your implementation.

This sentence has more than twenty-five words and should probably be broken up into multiple sentences for better readability and comprehension by the reader.
"""
    
    validator = DocumentationValidator()
    for rule in guide.get_rules():
        validator.add_rule(rule)
    
    issues = validator.validate(content,
                                check_links=False,
                                check_syntax=False,
                                check_structure=False,
                                check_content=False)
    
    print(f"\n✓ Found {len(issues)} style issues:")
    for issue in issues[:10]:
        print(f"  - Line {issue.line_number if issue.line_number else 'N/A'}: {issue.message[:80]}")
    
    assert len(issues) > 0, "Should find style violations"
    
    print("\n✓ Test PASSED: Plain Language guide working")


def test_get_style_guide():
    """Test getting style guide by name."""
    print("\n" + "="*70)
    print("Test 5: Get Style Guide by Name")
    print("="*70)
    
    # Test valid names
    google = get_style_guide('google')
    microsoft = get_style_guide('microsoft')
    plain = get_style_guide('plain-language')
    
    assert google is not None, "Should get Google guide"
    assert microsoft is not None, "Should get Microsoft guide"
    assert plain is not None, "Should get Plain Language guide"
    
    print("✓ Retrieved Google guide")
    print("✓ Retrieved Microsoft guide")
    print("✓ Retrieved Plain Language guide")
    
    # Test invalid name
    invalid = get_style_guide('nonexistent')
    assert invalid is None, "Should return None for invalid name"
    print("✓ Returns None for invalid name")
    
    # Test case insensitivity
    google_upper = get_style_guide('GOOGLE')
    assert google_upper is not None, "Should work with uppercase"
    print("✓ Case insensitive name matching works")
    
    print("\n✓ Test PASSED: Style guide retrieval working")


def test_combined_validation():
    """Test using multiple style guides together."""
    print("\n" + "="*70)
    print("Test 6: Combined Style Guide Validation")
    print("="*70)
    
    # Create validator with rules from multiple guides
    validator = DocumentationValidator()
    
    # Add Google style rules
    google = GoogleStyleGuide()
    for rule in google.get_rules():
        validator.add_rule(rule)
    
    # Add Plain Language rules
    plain = PlainLanguageGuide()
    for rule in plain.get_rules():
        validator.add_rule(rule)
    
    print(f"✓ Loaded {len(validator.custom_rules)} rules from 2 style guides")
    
    # Test content with various issues
    content = """# Project Documentation

Please follow these instructions! In order to utilize the system effectively,
you will need to commence the implementation process. We recommend that you
should carefully read the documentation prior to starting.

The system was designed to facilitate the utilization of resources and will
be updated regularly.
"""
    
    issues = validator.validate(content,
                                check_links=False,
                                check_syntax=False,
                                check_structure=False,
                                check_content=False)
    
    print(f"\n✓ Found {len(issues)} total issues")
    
    # Group by rule
    rule_counts = {}
    for issue in issues:
        rule_id = issue.rule_id or 'unknown'
        rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
    
    print("\n✓ Issues by rule:")
    for rule_id, count in sorted(rule_counts.items()):
        print(f"  - {rule_id}: {count}")
    
    assert len(issues) > 5, "Should find multiple style violations"
    
    print("\n✓ Test PASSED: Combined validation working")


def test_full_report():
    """Test generating full validation report with style guide."""
    print("\n" + "="*70)
    print("Test 7: Full Validation Report with Style Guide")
    print("="*70)
    
    # Create validator with Google style guide
    validator = DocumentationValidator()
    google = GoogleStyleGuide()
    
    for rule in google.get_rules():
        validator.add_rule(rule)
    
    # Sample documentation
    content = """# API Documentation

Please review the API endpoints carefully!

## Authentication

The user will be authenticated using OAuth 2.0.

## Endpoints

We provide the following endpoints:

- GET /api/users - Returns user list
- POST /api/users - Creates new user

Don't forget to include authentication headers!
"""
    
    issues = validator.validate(content)
    report = validator.format_report()
    
    print("\n" + "="*70)
    print(report)
    print("="*70)
    
    # Check summary
    summary = validator.get_summary()
    print(f"\n✓ Summary:")
    print(f"  Total issues: {summary['total']}")
    print(f"  Custom (style): {summary['by_category']['custom']}")
    
    assert summary['total'] > 0, "Should find issues"
    assert summary['by_category']['custom'] > 0, "Should have style issues"
    
    print("\n✓ Test PASSED: Full report generation working")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("Style Guide Enforcement Test Suite")
    print("="*70)
    
    try:
        test_list_style_guides()
        test_google_style_guide()
        test_microsoft_style_guide()
        test_plain_language_guide()
        test_get_style_guide()
        test_combined_validation()
        test_full_report()
        
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
