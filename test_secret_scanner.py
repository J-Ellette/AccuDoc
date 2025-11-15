"""
Tests for secret scanning functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.secret_scanner import SecretScanner, scan_documentation


def test_aws_key_detection():
    """Test detection of AWS keys."""
    print("=" * 60)
    print("Test 1: AWS Key Detection")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    # Test AWS access key
    text_with_aws = """
    Here's my AWS configuration:
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    """
    
    matches = scanner.scan(text_with_aws)
    
    assert len(matches) >= 1, "Should detect AWS keys"
    aws_matches = [m for m in matches if 'AWS' in m.secret_type]
    assert len(aws_matches) >= 1, "Should detect at least one AWS credential"
    
    print(f"✓ Detected {len(aws_matches)} AWS credential(s)")
    for match in aws_matches:
        print(f"  - {match.secret_type} on line {match.line_number}")
    
    print("\n✓ Test PASSED: AWS key detection working\n")
    return True


def test_github_token_detection():
    """Test detection of GitHub tokens."""
    print("=" * 60)
    print("Test 2: GitHub Token Detection")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    text_with_github = """
    To authenticate, use:
    export GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz
    """
    
    matches = scanner.scan(text_with_github)
    github_matches = [m for m in matches if 'GitHub' in m.secret_type]
    
    assert len(github_matches) >= 1, "Should detect GitHub token"
    assert github_matches[0].confidence == 'high', "Should be high confidence"
    
    print(f"✓ Detected GitHub token")
    print(f"  Confidence: {github_matches[0].confidence}")
    print(f"  Suggestion: {github_matches[0].suggestion[:50]}...")
    
    print("\n✓ Test PASSED: GitHub token detection working\n")
    return True


def test_private_key_detection():
    """Test detection of private keys."""
    print("=" * 60)
    print("Test 3: Private Key Detection")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    text_with_key = """
    -----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEA...
    -----END RSA PRIVATE KEY-----
    """
    
    matches = scanner.scan(text_with_key)
    key_matches = [m for m in matches if 'Private Key' in m.secret_type]
    
    assert len(key_matches) >= 1, "Should detect private key"
    assert key_matches[0].confidence == 'high', "Should be high confidence"
    
    print(f"✓ Detected private key")
    print(f"  This is a critical security issue")
    
    print("\n✓ Test PASSED: Private key detection working\n")
    return True


def test_api_key_detection():
    """Test detection of generic API keys."""
    print("=" * 60)
    print("Test 4: Generic API Key Detection")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    text_with_api = """
    Configure your API:
    api_key = "[REDACTED]"
    API_SECRET: "abcdefghijklmnopqrstuvwxyz123456"
    """
    
    matches = scanner.scan(text_with_api)
    api_matches = [m for m in matches if 'API' in m.secret_type or 'Stripe' in m.secret_type]
    
    assert len(api_matches) >= 1, "Should detect API keys"
    
    print(f"✓ Detected {len(api_matches)} API key(s)")
    for match in api_matches:
        print(f"  - {match.secret_type}")
    
    print("\n✓ Test PASSED: API key detection working\n")
    return True


def test_connection_string_detection():
    """Test detection of database connection strings."""
    print("=" * 60)
    print("Test 5: Database Connection String Detection")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    text_with_conn = """
    Database configuration:
    DATABASE_URL=postgresql://user:password@localhost:5432/mydb
    MONGO_URI=mongodb://admin:secret@mongo.example.com:27017/prod
    """
    
    matches = scanner.scan(text_with_conn)
    conn_matches = [m for m in matches if 'Connection String' in m.secret_type]
    
    assert len(conn_matches) >= 1, "Should detect connection strings"
    
    print(f"✓ Detected {len(conn_matches)} connection string(s)")
    print(f"  These contain embedded credentials")
    
    print("\n✓ Test PASSED: Connection string detection working\n")
    return True


def test_false_positive_filtering():
    """Test that false positives are filtered."""
    print("=" * 60)
    print("Test 6: False Positive Filtering")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    text_with_placeholders = """
    Example configuration:
    email = "user@domain.com"
    api_key = "YOUR_API_KEY"
    password = "${PASSWORD}"
    token = "xxxxxxxxxxxxxxxx"
    """
    
    matches = scanner.scan(text_with_placeholders)
    
    # Should detect email (low confidence) but filter placeholders
    high_conf = [m for m in matches if m.confidence == 'high']
    
    # Should not have high confidence matches for obvious placeholders
    assert len(high_conf) == 0, "Should not detect placeholders as high-confidence secrets"
    
    print(f"✓ Filtered placeholder patterns")
    print(f"✓ Total matches: {len(matches)} (low confidence only)")
    
    print("\n✓ Test PASSED: False positive filtering working\n")
    return True


def test_report_formatting():
    """Test report formatting."""
    print("=" * 60)
    print("Test 7: Report Formatting")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    text = """
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    api_key="test-key-1234567890abcdefghij"
    email@example.com
    """
    
    matches = scanner.scan(text)
    report = scanner.format_report(matches)
    
    assert len(report) > 0, "Report should not be empty"
    assert "SECURITY WARNING" in report or "No secrets" in report
    
    print(f"✓ Report generated successfully")
    print(f"✓ Report length: {len(report)} characters")
    
    print("\nSample report:")
    print("-" * 60)
    print(report[:400] + "..." if len(report) > 400 else report)
    
    print("\n✓ Test PASSED: Report formatting working\n")
    return True


def test_summary_statistics():
    """Test summary statistics."""
    print("=" * 60)
    print("Test 8: Summary Statistics")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    text = """
    AKIA1234567890ABCDEF
    api_key="sk_test_1234567890"
    password="secret123"
    user@example.com
    """
    
    matches = scanner.scan(text)
    summary = scanner.get_summary(matches)
    
    assert 'total' in summary
    assert 'high' in summary
    assert 'medium' in summary
    assert 'low' in summary
    assert summary['total'] >= 0
    
    print(f"✓ Summary generated")
    print(f"  Total: {summary['total']}")
    print(f"  High confidence: {summary['high']}")
    print(f"  Medium confidence: {summary['medium']}")
    print(f"  Low confidence: {summary['low']}")
    
    print("\n✓ Test PASSED: Summary statistics working\n")
    return True


def test_convenience_function():
    """Test convenience function."""
    print("=" * 60)
    print("Test 9: Convenience Function")
    print("=" * 60)
    
    text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
    
    matches, report = scan_documentation(text)
    
    assert isinstance(matches, list)
    assert isinstance(report, str)
    assert len(matches) > 0, "Should detect the AWS key"
    assert len(report) > 0, "Should generate a report"
    
    print(f"✓ Convenience function works")
    print(f"✓ Detected {len(matches)} secret(s)")
    print(f"✓ Generated {len(report)} character report")
    
    print("\n✓ Test PASSED: Convenience function working\n")
    return True


def test_clean_documentation():
    """Test that clean documentation passes."""
    print("=" * 60)
    print("Test 10: Clean Documentation")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    clean_text = """
    # My Project

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
    
    matches = scanner.scan(clean_text)
    high_conf = [m for m in matches if m.confidence == 'high']
    
    assert len(high_conf) == 0, "Clean documentation should not have high-confidence secrets"
    
    report = scanner.format_report(matches)
    
    print(f"✓ No high-confidence secrets in clean documentation")
    if len(matches) > 0:
        print(f"  (Found {len(matches)} low-confidence items, which is normal)")
    
    print("\n✓ Test PASSED: Clean documentation handling working\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc Secret Scanner Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_aws_key_detection,
        test_github_token_detection,
        test_private_key_detection,
        test_api_key_detection,
        test_connection_string_detection,
        test_false_positive_filtering,
        test_report_formatting,
        test_summary_statistics,
        test_convenience_function,
        test_clean_documentation,
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
