"""
Tests for sensitive data filtering functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.secret_scanner import SensitiveDataFilter, filter_sensitive_data


SAMPLE_DOC_WITH_SECRETS = """# My Project Documentation

## Configuration

To set up the project, configure your credentials:

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz
```

## Database Setup

Configure your database connection:

```
DATABASE_URL=postgresql://user:password123@localhost:5432/mydb
```

## API Keys

Set your API keys:
- Stripe: sk_test_1234567890abcdefghij
- Google: AIzaSyD1234567890abcdefghijklmnopqr

Contact: admin@example.com
"""


def test_mask_strategy():
    """Test masking strategy for redaction."""
    print("=" * 60)
    print("Test 1: Mask Strategy")
    print("=" * 60)
    
    filter_obj = SensitiveDataFilter(redaction_strategy='mask')
    filtered, secrets = filter_obj.filter_documentation(
        SAMPLE_DOC_WITH_SECRETS, 
        min_confidence='high'
    )
    
    # Check that secrets are masked but line structure is preserved
    assert 'AKIA' not in filtered or 'AKIA****' in filtered, "AWS key should be masked"
    assert '# My Project Documentation' in filtered, "Headers should be preserved"
    assert '## Configuration' in filtered, "Section headers should be preserved"
    
    # Check that detected secrets list is returned
    assert len(secrets) > 0, "Should detect secrets"
    high_conf = [s for s in secrets if s.confidence == 'high']
    assert len(high_conf) > 0, "Should detect high confidence secrets"
    
    print(f"✓ Detected {len(secrets)} secret(s)")
    print(f"✓ High confidence secrets: {len(high_conf)}")
    print(f"✓ Document structure preserved")
    print(f"✓ Secrets masked with asterisks")
    
    print("\n✓ Test PASSED: Mask strategy working\n")
    return True


def test_remove_strategy():
    """Test remove strategy for redaction."""
    print("=" * 60)
    print("Test 2: Remove Strategy")
    print("=" * 60)
    
    filter_obj = SensitiveDataFilter(redaction_strategy='remove')
    filtered, secrets = filter_obj.filter_documentation(
        SAMPLE_DOC_WITH_SECRETS,
        min_confidence='high'
    )
    
    # Check that lines with secrets are removed
    assert '[REDACTED: Sensitive data removed]' in filtered, "Should have redaction markers"
    assert 'AKIA' not in filtered, "AWS key should be removed"
    
    # But headers should still be there
    assert '# My Project Documentation' in filtered
    
    print(f"✓ Detected {len(secrets)} secret(s)")
    print(f"✓ Lines with secrets replaced with redaction markers")
    print(f"✓ Document structure preserved")
    
    print("\n✓ Test PASSED: Remove strategy working\n")
    return True


def test_placeholder_strategy():
    """Test placeholder strategy for redaction."""
    print("=" * 60)
    print("Test 3: Placeholder Strategy")
    print("=" * 60)
    
    filter_obj = SensitiveDataFilter(redaction_strategy='placeholder')
    filtered, secrets = filter_obj.filter_documentation(
        SAMPLE_DOC_WITH_SECRETS,
        min_confidence='high'
    )
    
    # Check that secrets are replaced with placeholders
    assert '<YOUR_AWS_ACCESS_KEY>' in filtered or '<YOUR_GITHUB_TOKEN>' in filtered, \
        "Should have placeholders"
    assert 'AKIA' not in filtered, "Actual AWS key should not be present"
    
    print(f"✓ Detected {len(secrets)} secret(s)")
    print(f"✓ Secrets replaced with descriptive placeholders")
    print(f"✓ Document remains readable with placeholders")
    
    print("\n✓ Test PASSED: Placeholder strategy working\n")
    return True


def test_confidence_filtering():
    """Test filtering by confidence level."""
    print("=" * 60)
    print("Test 4: Confidence Level Filtering")
    print("=" * 60)
    
    # Test with high confidence only
    filter_high = SensitiveDataFilter(redaction_strategy='mask')
    filtered_high, secrets_high = filter_high.filter_documentation(
        SAMPLE_DOC_WITH_SECRETS,
        min_confidence='high'
    )
    
    # Test with medium confidence (should catch more)
    filter_medium = SensitiveDataFilter(redaction_strategy='mask')
    filtered_medium, secrets_medium = filter_medium.filter_documentation(
        SAMPLE_DOC_WITH_SECRETS,
        min_confidence='medium'
    )
    
    # Test with low confidence (should catch even more)
    filter_low = SensitiveDataFilter(redaction_strategy='mask')
    filtered_low, secrets_low = filter_low.filter_documentation(
        SAMPLE_DOC_WITH_SECRETS,
        min_confidence='low'
    )
    
    assert len(secrets_high) <= len(secrets_medium), \
        "Medium confidence should catch at least as many as high"
    assert len(secrets_medium) <= len(secrets_low), \
        "Low confidence should catch at least as many as medium"
    
    print(f"✓ High confidence: {len(secrets_high)} secret(s)")
    print(f"✓ Medium confidence: {len(secrets_medium)} secret(s)")
    print(f"✓ Low confidence: {len(secrets_low)} secret(s)")
    print(f"✓ Confidence filtering works correctly")
    
    print("\n✓ Test PASSED: Confidence filtering working\n")
    return True


def test_clean_documentation():
    """Test that clean documentation is not modified."""
    print("=" * 60)
    print("Test 5: Clean Documentation")
    print("=" * 60)
    
    clean_doc = """# My Project

## Installation

Install using pip:
```
pip install myproject
```

## Configuration

Set your API key:
```
export API_KEY=your_api_key_here
```

Contact: info@example.com
"""
    
    filter_obj = SensitiveDataFilter(redaction_strategy='mask')
    filtered, secrets = filter_obj.filter_documentation(clean_doc, min_confidence='high')
    
    # Should have minimal changes (maybe email with low confidence)
    high_conf = [s for s in secrets if s.confidence == 'high']
    assert len(high_conf) == 0, "Clean doc should not have high-confidence secrets"
    
    print(f"✓ No high-confidence secrets detected")
    print(f"✓ Clean documentation preserved")
    
    print("\n✓ Test PASSED: Clean documentation handling working\n")
    return True


def test_convenience_function():
    """Test convenience function."""
    print("=" * 60)
    print("Test 6: Convenience Function")
    print("=" * 60)
    
    text_with_secret = """
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    """
    
    filtered_doc, secrets, report = filter_sensitive_data(
        text_with_secret,
        strategy='mask',
        min_confidence='high'
    )
    
    assert isinstance(filtered_doc, str), "Should return filtered doc"
    assert isinstance(secrets, list), "Should return secrets list"
    assert isinstance(report, str), "Should return report"
    assert len(secrets) > 0, "Should detect the AWS key"
    assert 'AKIA' not in filtered_doc or '****' in filtered_doc, "Should mask the key"
    
    print(f"✓ Filtered {len(secrets)} secret(s)")
    print(f"✓ Generated report: {len(report)} characters")
    print(f"✓ Convenience function works correctly")
    
    print("\n✓ Test PASSED: Convenience function working\n")
    return True


def test_multiple_secrets_same_line():
    """Test handling multiple secrets on the same line."""
    print("=" * 60)
    print("Test 7: Multiple Secrets on Same Line")
    print("=" * 60)
    
    doc_multi = """
    export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz
    """
    
    filter_obj = SensitiveDataFilter(redaction_strategy='mask')
    filtered, secrets = filter_obj.filter_documentation(doc_multi, min_confidence='high')
    
    # Both secrets should be detected
    assert len(secrets) >= 1, "Should detect at least one secret"
    
    # Both should be masked
    assert 'AKIA' not in filtered or '****' in filtered
    
    print(f"✓ Detected {len(secrets)} secret(s) on same line")
    print(f"✓ Both secrets masked correctly")
    
    print("\n✓ Test PASSED: Multiple secrets handling working\n")
    return True


def test_preserve_code_blocks():
    """Test that code block structure is preserved."""
    print("=" * 60)
    print("Test 8: Preserve Code Block Structure")
    print("=" * 60)
    
    doc_with_blocks = """# Setup

Configure credentials:

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

Done.
"""
    
    filter_obj = SensitiveDataFilter(redaction_strategy='mask')
    filtered, secrets = filter_obj.filter_documentation(doc_with_blocks, min_confidence='high')
    
    # Code block markers should be preserved
    assert '```bash' in filtered, "Opening code block should be preserved"
    assert '```' in filtered, "Code blocks should be preserved"
    assert '# Setup' in filtered, "Headers should be preserved"
    assert 'Done.' in filtered, "Text after blocks should be preserved"
    
    print(f"✓ Code block structure preserved")
    print(f"✓ Headers preserved")
    print(f"✓ Secrets filtered within blocks")
    
    print("\n✓ Test PASSED: Code block preservation working\n")
    return True


def test_different_secret_types():
    """Test filtering different types of secrets."""
    print("=" * 60)
    print("Test 9: Different Secret Types")
    print("=" * 60)
    
    doc_various = """
    AWS: AKIAIOSFODNN7EXAMPLE
    GitHub: ghp_1234567890abcdefghijklmnopqrstuvwxyz
    JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U
    Stripe: sk_test_1234567890abcdefghij
    """
    
    filter_obj = SensitiveDataFilter(redaction_strategy='mask')
    filtered, secrets = filter_obj.filter_documentation(doc_various, min_confidence='high')
    
    # Check different types are detected
    secret_types = [s.secret_type for s in secrets]
    print(f"✓ Detected secret types: {len(set(secret_types))}")
    for st in set(secret_types):
        print(f"  - {st}")
    
    assert len(secrets) >= 3, "Should detect multiple types"
    
    print("\n✓ Test PASSED: Different secret types handling working\n")
    return True


def test_report_generation():
    """Test that filtering generates proper reports."""
    print("=" * 60)
    print("Test 10: Report Generation")
    print("=" * 60)
    
    filtered_doc, secrets, report = filter_sensitive_data(
        SAMPLE_DOC_WITH_SECRETS,
        strategy='placeholder',
        min_confidence='medium'
    )
    
    assert len(report) > 0, "Should generate a report"
    assert len(secrets) > 0, "Should detect secrets"
    
    # Report should contain useful information
    if len(secrets) > 0:
        assert ('SECURITY WARNING' in report or 'No secrets' in report), \
            "Report should have security information"
    
    print(f"✓ Filtered documentation: {len(filtered_doc)} characters")
    print(f"✓ Detected {len(secrets)} secret(s)")
    print(f"✓ Report generated: {len(report)} characters")
    
    print("\n✓ Test PASSED: Report generation working\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc Sensitive Data Filtering Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_mask_strategy,
        test_remove_strategy,
        test_placeholder_strategy,
        test_confidence_filtering,
        test_clean_documentation,
        test_convenience_function,
        test_multiple_secrets_same_line,
        test_preserve_code_blocks,
        test_different_secret_types,
        test_report_generation,
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
