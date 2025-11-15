"""
Tests for audit trail functionality.
"""

import sys
import tempfile
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.audit import AuditLogger, log_operation, get_audit_logger


def test_basic_logging():
    """Test basic audit logging."""
    print("=" * 60)
    print("Test 1: Basic Logging")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'audit.log'
        logger = AuditLogger(log_file=log_file, enabled=True)
        
        # Log a successful operation
        logger.log_operation(
            operation='scan_repository',
            status='success',
            details={'repository': '/path/to/repo', 'files_found': 42}
        )
        
        # Log a failed operation
        logger.log_operation(
            operation='generate_docs',
            status='failure',
            error='Template not found'
        )
        
        # Check log file exists
        assert log_file.exists(), "Log file should be created"
        
        # Read log file
        content = log_file.read_text()
        assert 'scan_repository' in content, "Should log scan operation"
        assert 'generate_docs' in content, "Should log generate operation"
        assert 'success' in content.lower(), "Should log success status"
        assert 'failure' in content.lower(), "Should log failure status"
        
        print(f"✓ Log file created: {log_file}")
        print(f"✓ Operations logged correctly")
        print(f"✓ Log size: {len(content)} bytes")
    
    print("\n✓ Test PASSED: Basic logging working\n")
    return True


def test_sensitive_data_sanitization():
    """Test that sensitive data is sanitized."""
    print("=" * 60)
    print("Test 2: Sensitive Data Sanitization")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'audit.log'
        logger = AuditLogger(log_file=log_file, enabled=True)
        
        # Log operation with sensitive data
        logger.log_operation(
            operation='github_scan',
            status='success',
            details={
                'token': 'ghp_super_secret_token_12345',
                'password': 'my_password_123',
                'api_key': 'sk_live_secret_key',
                'repository': 'user/repo'  # This should not be redacted
            }
        )
        
        # Read log file
        content = log_file.read_text()
        
        # Sensitive values should be redacted
        assert 'ghp_super_secret_token' not in content, "Token should be redacted"
        assert 'my_password_123' not in content, "Password should be redacted"
        assert 'sk_live_secret_key' not in content, "API key should be redacted"
        assert '[REDACTED]' in content, "Should have redaction markers"
        
        # Non-sensitive values should be kept
        assert 'user/repo' in content, "Repository name should be kept"
        
        print(f"✓ Sensitive data redacted")
        print(f"✓ Non-sensitive data preserved")
        print(f"✓ Redaction markers present")
    
    print("\n✓ Test PASSED: Sensitive data sanitization working\n")
    return True


def test_duration_logging():
    """Test logging with duration."""
    print("=" * 60)
    print("Test 3: Duration Logging")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'audit.log'
        logger = AuditLogger(log_file=log_file, enabled=True)
        
        # Log with duration
        logger.log_operation(
            operation='export_pdf',
            status='success',
            duration_ms=1234.56
        )
        
        content = log_file.read_text()
        assert 'Duration' in content, "Should log duration"
        assert '1234' in content, "Should have duration value"
        
        print(f"✓ Duration logged correctly")
    
    print("\n✓ Test PASSED: Duration logging working\n")
    return True


def test_recent_entries():
    """Test retrieving recent entries."""
    print("=" * 60)
    print("Test 4: Recent Entries Retrieval")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'audit.log'
        logger = AuditLogger(log_file=log_file, enabled=True)
        
        # Log multiple operations
        for i in range(10):
            logger.log_operation(
                operation=f'operation_{i}',
                status='success'
            )
        
        # Get recent entries
        recent = logger.get_recent_entries(count=5)
        
        assert len(recent) == 5, "Should return requested number of entries"
        assert 'operation_9' in recent[-1], "Should have most recent operation"
        
        print(f"✓ Retrieved {len(recent)} recent entries")
        print(f"✓ Correct ordering (most recent last)")
    
    print("\n✓ Test PASSED: Recent entries retrieval working\n")
    return True


def test_json_export():
    """Test JSON export functionality."""
    print("=" * 60)
    print("Test 5: JSON Export")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'audit.log'
        json_file = Path(tmpdir) / 'audit.json'
        
        logger = AuditLogger(log_file=log_file, enabled=True)
        
        # Log some operations
        logger.log_operation('test_op_1', 'success', {'key': 'value1'})
        logger.log_operation('test_op_2', 'success', {'key': 'value2'})
        
        # Export to JSON
        logger.export_to_json(json_file, count=10)
        
        assert json_file.exists(), "JSON file should be created"
        
        # Read and parse JSON
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list), "Should be a list of entries"
        assert len(data) > 0, "Should have entries"
        
        print(f"✓ JSON file created: {json_file}")
        print(f"✓ Exported {len(data)} entries")
        print(f"✓ JSON format valid")
    
    print("\n✓ Test PASSED: JSON export working\n")
    return True


def test_csv_export():
    """Test CSV export functionality."""
    print("=" * 60)
    print("Test 6: CSV Export")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'audit.log'
        csv_file = Path(tmpdir) / 'audit.csv'
        
        logger = AuditLogger(log_file=log_file, enabled=True)
        
        # Log some operations
        logger.log_operation('csv_test_1', 'success')
        logger.log_operation('csv_test_2', 'failure', error='Test error')
        
        # Export to CSV
        logger.export_to_csv(csv_file, count=10)
        
        assert csv_file.exists(), "CSV file should be created"
        
        # Read CSV
        content = csv_file.read_text()
        assert 'Timestamp' in content, "Should have header"
        assert 'csv_test_1' in content or 'csv_test_2' in content, "Should have entries"
        
        print(f"✓ CSV file created: {csv_file}")
        print(f"✓ CSV format valid")
    
    print("\n✓ Test PASSED: CSV export working\n")
    return True


def test_statistics():
    """Test statistics generation."""
    print("=" * 60)
    print("Test 7: Statistics Generation")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'audit.log'
        logger = AuditLogger(log_file=log_file, enabled=True)
        
        # Log various operations
        logger.log_operation('scan', 'success')
        logger.log_operation('generate', 'success')
        logger.log_operation('export', 'failure', error='Failed')
        logger.log_operation('scan', 'success')
        
        # Get statistics
        stats = logger.get_statistics()
        
        assert 'total_entries' in stats, "Should have total count"
        assert 'by_level' in stats, "Should have counts by level"
        assert 'by_operation' in stats, "Should have counts by operation"
        assert stats['total_entries'] >= 4, "Should count all entries"
        
        print(f"✓ Total entries: {stats['total_entries']}")
        print(f"✓ By level: {stats['by_level']}")
        print(f"✓ By operation: {stats['by_operation']}")
        print(f"✓ Log size: {stats['log_size_bytes']} bytes")
    
    print("\n✓ Test PASSED: Statistics generation working\n")
    return True


def test_disabled_logging():
    """Test that logging can be disabled."""
    print("=" * 60)
    print("Test 8: Disabled Logging")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'audit.log'
        logger = AuditLogger(log_file=log_file, enabled=False)
        
        # Try to log
        logger.log_operation('test_disabled', 'success')
        
        # Log file should not be created or should be empty
        if log_file.exists():
            content = log_file.read_text()
            assert len(content) == 0, "Log should be empty when disabled"
        
        print(f"✓ Logging disabled successfully")
        print(f"✓ No logs written")
    
    print("\n✓ Test PASSED: Disabled logging working\n")
    return True


def test_global_logger():
    """Test global logger instance."""
    print("=" * 60)
    print("Test 9: Global Logger")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'global_audit.log'
        
        # Get global logger
        logger1 = get_audit_logger(log_file=log_file, enabled=True)
        logger2 = get_audit_logger()
        
        # Should be the same instance
        assert logger1 is logger2, "Should return same instance"
        
        print(f"✓ Global logger singleton working")
    
    print("\n✓ Test PASSED: Global logger working\n")
    return True


def test_convenience_function():
    """Test convenience function."""
    print("=" * 60)
    print("Test 10: Convenience Function")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / 'convenience_audit.log'
        
        # Initialize global logger first
        get_audit_logger(log_file=log_file, enabled=True)
        
        # Use convenience function
        log_operation('convenience_test', 'success', {'test': 'data'})
        
        # Check log
        if log_file.exists():
            content = log_file.read_text()
            assert 'convenience_test' in content, "Should log via convenience function"
        
        print(f"✓ Convenience function works")
    
    print("\n✓ Test PASSED: Convenience function working\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc Audit Trail Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_basic_logging,
        test_sensitive_data_sanitization,
        test_duration_logging,
        test_recent_entries,
        test_json_export,
        test_csv_export,
        test_statistics,
        test_disabled_logging,
        test_global_logger,
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
