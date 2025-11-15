"""
Tests for documentation validation functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.doc_validator import DocumentationValidator, validate_documentation


def test_valid_document():
    """Test validation of a valid document."""
    print("=" * 60)
    print("Test 1: Valid Document")
    print("=" * 60)
    
    valid_doc = """# My Project

## Overview

This is a well-formed markdown document with proper structure.

## Installation

Install using pip:

```bash
pip install myproject
```

## Usage

See the [documentation](https://example.com/docs) for more information.

## Contributing

Please read our [contributing guidelines](CONTRIBUTING.md).
"""
    
    validator = DocumentationValidator()
    issues = validator.validate(valid_doc)
    
    # Should have minimal issues
    errors = [i for i in issues if i.severity == 'error']
    assert len(errors) == 0, "Valid document should have no errors"
    
    print(f"✓ No errors found")
    print(f"✓ Total issues: {len(issues)} (mostly info)")
    
    print("\n✓ Test PASSED: Valid document validation working\n")
    return True


def test_broken_links():
    """Test detection of broken links."""
    print("=" * 60)
    print("Test 2: Broken Links Detection")
    print("=" * 60)
    
    doc_with_broken_links = """# Test Document

Check out [this link]() with no URL.

Also see [placeholder](#) and [TODO link](TODO).

Visit [our site](#nonexistent-anchor).
"""
    
    validator = DocumentationValidator()
    issues = validator.validate(doc_with_broken_links, check_links=True)
    
    link_issues = [i for i in issues if i.category == 'link']
    assert len(link_issues) > 0, "Should detect broken links"
    
    # Check for empty link
    empty_link_issues = [i for i in link_issues if 'Empty link' in i.message]
    assert len(empty_link_issues) > 0, "Should detect empty link"
    
    # Check for placeholder links
    placeholder_issues = [i for i in link_issues if 'Placeholder' in i.message]
    assert len(placeholder_issues) > 0, "Should detect placeholder links"
    
    print(f"✓ Detected {len(link_issues)} link issues")
    print(f"  - Empty links: {len(empty_link_issues)}")
    print(f"  - Placeholder links: {len(placeholder_issues)}")
    
    print("\n✓ Test PASSED: Broken links detection working\n")
    return True


def test_syntax_issues():
    """Test detection of syntax issues."""
    print("=" * 60)
    print("Test 3: Syntax Issues Detection")
    print("=" * 60)
    
    doc_with_syntax_issues = """# Test Document

This has an unmatched [bracket.

Code block starts here:
```python
def hello():
    print("Hello")
```

Another code block:
```
Some code

# This should cause unmatched code block warning
"""
    
    validator = DocumentationValidator()
    issues = validator.validate(doc_with_syntax_issues, check_syntax=True)
    
    syntax_issues = [i for i in issues if i.category == 'syntax']
    assert len(syntax_issues) > 0, "Should detect syntax issues"
    
    # Check for unmatched code block
    code_block_issues = [i for i in syntax_issues if 'code block' in i.message.lower()]
    assert len(code_block_issues) > 0, "Should detect unmatched code blocks"
    
    print(f"✓ Detected {len(syntax_issues)} syntax issues")
    print(f"  - Unmatched code blocks: {len(code_block_issues)}")
    
    print("\n✓ Test PASSED: Syntax issues detection working\n")
    return True


def test_structure_issues():
    """Test detection of structure issues."""
    print("=" * 60)
    print("Test 4: Structure Issues Detection")
    print("=" * 60)
    
    doc_with_structure_issues = """## Starting with h2 instead of h1

### Then jumping to h3

##### And skipping to h5

## Empty header below:

### 

Content here.
"""
    
    validator = DocumentationValidator()
    issues = validator.validate(doc_with_structure_issues, check_structure=True)
    
    structure_issues = [i for i in issues if i.category == 'structure']
    assert len(structure_issues) > 0, "Should detect structure issues"
    
    # Check for missing h1
    no_title_issues = [i for i in structure_issues if 'top-level heading' in i.message]
    assert len(no_title_issues) > 0, "Should detect missing h1"
    
    # Check for header level skip
    skip_issues = [i for i in structure_issues if 'skip' in i.message.lower()]
    assert len(skip_issues) > 0, "Should detect header level skipping"
    
    # Check for empty header
    empty_header_issues = [i for i in structure_issues if 'Empty header' in i.message]
    assert len(empty_header_issues) > 0, "Should detect empty headers"
    
    print(f"✓ Detected {len(structure_issues)} structure issues")
    print(f"  - Missing h1: {len(no_title_issues)}")
    print(f"  - Level skipping: {len(skip_issues)}")
    print(f"  - Empty headers: {len(empty_header_issues)}")
    
    print("\n✓ Test PASSED: Structure issues detection working\n")
    return True


def test_content_quality():
    """Test content quality checks."""
    print("=" * 60)
    print("Test 5: Content Quality Checks")
    print("=" * 60)
    
    doc_with_quality_issues = """# My Project

This is a test document.

TODO: Add more content here.

This line has trailing whitespace.   

FIXME: Fix this section.

This is a line with the word teh instead of the.

This is a very long line that exceeds the reasonable character limit and should be flagged as potentially problematic for readability and could benefit from being broken up into multiple shorter lines for better presentation and easier reading by users who might find such long lines difficult to parse quickly.
"""
    
    validator = DocumentationValidator()
    issues = validator.validate(doc_with_quality_issues, check_content=True)
    
    content_issues = [i for i in issues if i.category == 'content']
    assert len(content_issues) > 0, "Should detect content issues"
    
    # Check for TODO markers
    todo_issues = [i for i in content_issues if 'TODO' in i.message or 'FIXME' in i.message]
    assert len(todo_issues) > 0, "Should detect TODO/FIXME markers"
    
    # Check for typos
    typo_issues = [i for i in content_issues if 'typo' in i.message.lower()]
    assert len(typo_issues) > 0, "Should detect typos"
    
    print(f"✓ Detected {len(content_issues)} content issues")
    print(f"  - TODO/FIXME markers: {len(todo_issues)}")
    print(f"  - Typos: {len(typo_issues)}")
    
    print("\n✓ Test PASSED: Content quality checks working\n")
    return True


def test_anchor_validation():
    """Test anchor link validation."""
    print("=" * 60)
    print("Test 6: Anchor Link Validation")
    print("=" * 60)
    
    doc_with_anchors = """# Main Title

## Section One

Link to [existing section](#section-one) works.

Link to [non-existent section](#section-missing) should fail.

## Section Two

Another valid [link](#main-title).
"""
    
    validator = DocumentationValidator()
    issues = validator.validate(doc_with_anchors, check_links=True)
    
    anchor_issues = [i for i in issues if 'Anchor' in i.message and 'not found' in i.message]
    assert len(anchor_issues) > 0, "Should detect missing anchors"
    
    print(f"✓ Detected {len(anchor_issues)} missing anchor(s)")
    
    print("\n✓ Test PASSED: Anchor validation working\n")
    return True


def test_selective_validation():
    """Test selective validation options."""
    print("=" * 60)
    print("Test 7: Selective Validation")
    print("=" * 60)
    
    doc = """# Test

[broken link]()

```
unmatched code block
"""
    
    validator = DocumentationValidator()
    
    # Only check links
    link_issues = validator.validate(doc, check_links=True, check_syntax=False,
                                    check_structure=False, check_content=False)
    link_count = len([i for i in link_issues if i.category == 'link'])
    assert link_count > 0, "Should find link issues"
    
    # Only check syntax
    validator2 = DocumentationValidator()
    syntax_issues = validator2.validate(doc, check_links=False, check_syntax=True,
                                       check_structure=False, check_content=False)
    syntax_count = len([i for i in syntax_issues if i.category == 'syntax'])
    assert syntax_count > 0, "Should find syntax issues"
    
    print(f"✓ Link-only validation: {link_count} issues")
    print(f"✓ Syntax-only validation: {syntax_count} issues")
    
    print("\n✓ Test PASSED: Selective validation working\n")
    return True


def test_summary_generation():
    """Test summary generation."""
    print("=" * 60)
    print("Test 8: Summary Generation")
    print("=" * 60)
    
    doc = """# Test

[broken]()

TODO: fix this

```
unmatched
"""
    
    validator = DocumentationValidator()
    issues = validator.validate(doc)
    summary = validator.get_summary()
    
    assert 'total' in summary
    assert 'by_severity' in summary
    assert 'by_category' in summary
    assert summary['total'] == len(issues)
    
    print(f"✓ Total issues: {summary['total']}")
    print(f"✓ By severity: {summary['by_severity']}")
    print(f"✓ By category: {summary['by_category']}")
    
    print("\n✓ Test PASSED: Summary generation working\n")
    return True


def test_report_formatting():
    """Test report formatting."""
    print("=" * 60)
    print("Test 9: Report Formatting")
    print("=" * 60)
    
    doc = """# Test Document

[empty link]()

TODO: Add content
"""
    
    validator = DocumentationValidator()
    issues = validator.validate(doc)
    report = validator.format_report(issues)
    
    assert len(report) > 0, "Report should not be empty"
    assert 'Validation Report' in report or 'Issues' in report or 'link' in report.lower()
    
    print(f"✓ Report generated")
    print(f"✓ Report length: {len(report)} characters")
    print("\nSample report:")
    print("-" * 60)
    print(report[:400] + "..." if len(report) > 400 else report)
    
    print("\n✓ Test PASSED: Report formatting working\n")
    return True


def test_convenience_function():
    """Test convenience function."""
    print("=" * 60)
    print("Test 10: Convenience Function")
    print("=" * 60)
    
    doc = """# Test

[broken]()
"""
    
    issues, report = validate_documentation(doc)
    
    assert isinstance(issues, list), "Should return list of issues"
    assert isinstance(report, str), "Should return report string"
    assert len(issues) > 0, "Should find issues"
    assert len(report) > 0, "Should generate report"
    
    print(f"✓ Convenience function works")
    print(f"✓ Found {len(issues)} issue(s)")
    
    print("\n✓ Test PASSED: Convenience function working\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc Documentation Validation Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_valid_document,
        test_broken_links,
        test_syntax_issues,
        test_structure_issues,
        test_content_quality,
        test_anchor_validation,
        test_selective_validation,
        test_summary_generation,
        test_report_formatting,
        test_convenience_function,
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
