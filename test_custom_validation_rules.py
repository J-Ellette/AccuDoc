#!/usr/bin/env python3
"""
Tests for custom validation rules feature.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.doc_validator import (
    DocumentationValidator,
    MaxLineLengthRule,
    RequiredSectionsRule,
    ForbiddenWordsRule,
    NoConsecutiveBlankLinesRule,
    HeadingCapitalizationRule,
    CodeBlockLanguageRule
)


def test_max_line_length_rule():
    """Test max line length rule."""
    print("\n" + "="*70)
    print("Test 1: Max Line Length Rule")
    print("="*70)
    
    rule = MaxLineLengthRule(config={'max_length': 80})
    
    # Test content with long lines
    content = """# Test Document

This is a short line.

This is a very long line that exceeds the maximum allowed length and should trigger a validation warning from the rule.

Another short line.
"""
    
    issues = rule.validate(content)
    
    print(f"✓ Rule ID: {rule.rule_id}")
    print(f"✓ Description: {rule.description}")
    print(f"✓ Issues found: {len(issues)}")
    
    for issue in issues:
        print(f"  - Line {issue.line_number}: {issue.message}")
    
    assert len(issues) == 1, "Should find 1 long line"
    assert issues[0].line_number == 5, "Long line should be line 5"
    
    print("✓ Test PASSED: Max line length rule working correctly")


def test_required_sections_rule():
    """Test required sections rule."""
    print("\n" + "="*70)
    print("Test 2: Required Sections Rule")
    print("="*70)
    
    rule = RequiredSectionsRule(config={
        'sections': ['Overview', 'Installation', 'Usage']
    })
    
    # Test content missing some sections
    content = """# Test Document

## Overview
This is the overview.

## Installation
Installation instructions.
"""
    
    issues = rule.validate(content)
    
    print(f"✓ Rule ID: {rule.rule_id}")
    print(f"✓ Description: {rule.description}")
    print(f"✓ Issues found: {len(issues)}")
    
    for issue in issues:
        print(f"  - {issue.message}")
    
    assert len(issues) == 1, "Should find 1 missing section (Usage)"
    assert 'Usage' in issues[0].message, "Should report missing Usage section"
    
    print("✓ Test PASSED: Required sections rule working correctly")


def test_forbidden_words_rule():
    """Test forbidden words rule."""
    print("\n" + "="*70)
    print("Test 3: Forbidden Words Rule")
    print("="*70)
    
    rule = ForbiddenWordsRule(config={
        'words': ['simply', 'just', 'easy'],
        'case_sensitive': False
    })
    
    # Test content with forbidden words
    content = """# Test Document

You can simply run the command.

It's just that easy to use.

This line is fine.
"""
    
    issues = rule.validate(content)
    
    print(f"✓ Rule ID: {rule.rule_id}")
    print(f"✓ Description: {rule.description}")
    print(f"✓ Issues found: {len(issues)}")
    
    for issue in issues:
        print(f"  - Line {issue.line_number}: {issue.message}")
    
    assert len(issues) == 3, "Should find 3 forbidden words"
    
    print("✓ Test PASSED: Forbidden words rule working correctly")


def test_no_consecutive_blanks_rule():
    """Test no consecutive blank lines rule."""
    print("\n" + "="*70)
    print("Test 4: No Consecutive Blank Lines Rule")
    print("="*70)
    
    rule = NoConsecutiveBlankLinesRule(config={'max_consecutive': 1})
    
    # Test content with multiple blank lines
    content = """# Test Document

This is a paragraph.


This has two blank lines above.



This has three blank lines above.
"""
    
    issues = rule.validate(content)
    
    print(f"✓ Rule ID: {rule.rule_id}")
    print(f"✓ Description: {rule.description}")
    print(f"✓ Issues found: {len(issues)}")
    
    for issue in issues:
        print(f"  - Line {issue.line_number}: {issue.message}")
    
    assert len(issues) >= 2, "Should find at least 2 violations"
    
    print("✓ Test PASSED: No consecutive blanks rule working correctly")


def test_heading_capitalization_rule():
    """Test heading capitalization rule."""
    print("\n" + "="*70)
    print("Test 5: Heading Capitalization Rule")
    print("="*70)
    
    rule = HeadingCapitalizationRule(config={'style': 'title'})
    
    # Test content with mixed capitalization
    content = """# Test Document

## This is a Good Title

## this is a bad title

## Another Good One
"""
    
    issues = rule.validate(content)
    
    print(f"✓ Rule ID: {rule.rule_id}")
    print(f"✓ Description: {rule.description}")
    print(f"✓ Issues found: {len(issues)}")
    
    for issue in issues:
        print(f"  - Line {issue.line_number}: {issue.message}")
    
    assert len(issues) == 1, "Should find 1 bad heading"
    
    print("✓ Test PASSED: Heading capitalization rule working correctly")


def test_code_block_language_rule():
    """Test code block language specification rule."""
    print("\n" + "="*70)
    print("Test 6: Code Block Language Rule")
    print("="*70)
    
    rule = CodeBlockLanguageRule()
    
    # Test content with code blocks
    content = """# Test Document

Good code block:
```python
print("Hello")
```

Bad code block:
```
print("Hello")
```
"""
    
    issues = rule.validate(content)
    
    print(f"✓ Rule ID: {rule.rule_id}")
    print(f"✓ Description: {rule.description}")
    print(f"✓ Issues found: {len(issues)}")
    
    for issue in issues:
        print(f"  - Line {issue.line_number}: {issue.message}")
    
    assert len(issues) == 1, "Should find 1 code block without language"
    
    print("✓ Test PASSED: Code block language rule working correctly")


def test_validator_with_custom_rules():
    """Test DocumentationValidator with custom rules."""
    print("\n" + "="*70)
    print("Test 7: DocumentationValidator with Custom Rules")
    print("="*70)
    
    # Create validator with custom rules
    validator = DocumentationValidator()
    validator.add_rule(MaxLineLengthRule(config={'max_length': 80}))
    validator.add_rule(RequiredSectionsRule(config={
        'sections': ['Overview', 'Usage']
    }))
    validator.add_rule(ForbiddenWordsRule(config={
        'words': ['simply', 'easy']
    }))
    
    # Test content
    content = """# Test Document

## Overview
This is simply the overview with a very long line that definitely exceeds eighty characters and will trigger a validation warning.

Some content here.
"""
    
    issues = validator.validate(content)
    
    print(f"✓ Total issues found: {len(issues)}")
    print(f"✓ Custom rules loaded: {len(validator.custom_rules)}")
    
    # Show summary
    summary = validator.get_summary()
    print(f"✓ By severity: {summary['by_severity']}")
    print(f"✓ By category: {summary['by_category']}")
    
    # List rules
    rules = validator.list_rules()
    print(f"\n✓ Loaded rules:")
    for rule in rules:
        print(f"  - {rule['id']}: {rule['description']} ({rule['severity']})")
    
    # Format report
    report = validator.format_report()
    print(f"\n{report}")
    
    assert len(issues) >= 3, "Should find multiple issues from different rules"
    assert summary['by_category']['custom'] >= 3, "Should have custom rule issues"
    
    print("\n✓ Test PASSED: Validator with custom rules working correctly")


def test_load_rules_from_config():
    """Test loading rules from configuration file."""
    print("\n" + "="*70)
    print("Test 8: Load Rules from Configuration File")
    print("="*70)
    
    # Create validator
    validator = DocumentationValidator()
    
    # Load rules from example config
    config_path = Path(__file__).parent / 'examples' / 'validation_rules.yaml'
    
    if config_path.exists():
        validator.load_rules_from_config(config_path)
        
        print(f"✓ Configuration file loaded: {config_path}")
        print(f"✓ Rules loaded: {len(validator.custom_rules)}")
        
        # List loaded rules
        rules = validator.list_rules()
        print(f"\n✓ Loaded rules from config:")
        for rule in rules:
            status = "enabled" if rule['enabled'] else "disabled"
            print(f"  - {rule['id']}: {status} ({rule['severity']})")
        
        assert len(validator.custom_rules) > 0, "Should load rules from config"
        
        print("\n✓ Test PASSED: Configuration loading working correctly")
    else:
        print(f"⚠️  Test SKIPPED: Config file not found at {config_path}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("Custom Validation Rules Test Suite")
    print("="*70)
    
    try:
        test_max_line_length_rule()
        test_required_sections_rule()
        test_forbidden_words_rule()
        test_no_consecutive_blanks_rule()
        test_heading_capitalization_rule()
        test_code_block_language_rule()
        test_validator_with_custom_rules()
        test_load_rules_from_config()
        
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
