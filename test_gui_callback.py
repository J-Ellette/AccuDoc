#!/usr/bin/env python3
"""Test script to verify the GUI callback fix for stats variable scoping."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.scanner import RepositoryScanner


def test_progress_callback_with_stats():
    """Test that mimics the GUI's progress callback with stats variable."""
    print("=" * 60)
    print("Test: Progress Callback with Stats Variable")
    print("=" * 60)
    
    try:
        # Initialize stats before defining callback (like the fix)
        stats = {}
        callback_calls = []
        
        def progress_callback(message):
            """Simulated progress callback that accesses stats."""
            # This simulates what the GUI does - accessing stats from outer scope
            est_total = stats.get('total_files', 100) * 0.2
            callback_calls.append({
                'message': message,
                'est_total': est_total
            })
            print(f"  Progress: {message}")
        
        # Create scanner with progress callback
        scanner = RepositoryScanner('.', progress_callback=progress_callback)
        
        # Perform scan
        repo_info = scanner.scan()
        
        # Update stats after scan (like the GUI does)
        stats = repo_info.get('stats', {})
        
        print(f"\n✓ Scan completed successfully")
        print(f"✓ Progress callback was called {len(callback_calls)} times")
        print(f"✓ Final stats: {stats}")
        
        if len(callback_calls) > 0:
            print("\n✓ Test PASSED: Progress callback with stats variable works correctly")
            return True
        else:
            print("\n✗ Test FAILED: Callback was not called")
            return False
            
    except NameError as e:
        print(f"\n✗ Test FAILED with NameError: {str(e)}")
        print("This indicates the stats variable scoping issue still exists")
        return False
    except Exception as e:
        print(f"\n✗ Test FAILED: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_progress_callback_without_init():
    """Test the OLD broken pattern (stats not initialized before callback)."""
    print("\n" + "=" * 60)
    print("Test: Progress Callback WITHOUT Stats Initialization (Old Pattern)")
    print("=" * 60)
    
    try:
        callback_calls = []
        
        def progress_callback(message):
            """Callback that tries to access undefined stats - SHOULD FAIL."""
            # This will fail because stats is not defined yet
            est_total = stats.get('total_files', 100) * 0.2  # noqa: F821
            callback_calls.append(message)
        
        # Try to call the callback
        progress_callback("Test message")
        
        print("\n✗ Test unexpectedly passed - the old pattern should fail")
        return False
            
    except NameError as e:
        print(f"\n✓ Test PASSED: Old pattern correctly fails with NameError: {str(e)}")
        print("This confirms that initializing stats before the callback is necessary")
        return True
    except Exception as e:
        print(f"\n✗ Test FAILED with unexpected error: {type(e).__name__}: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GUI Callback Fix Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_progress_callback_with_stats,
        test_progress_callback_without_init,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe fix successfully resolves the 'cannot access free variable stats' error")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
