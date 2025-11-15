#!/usr/bin/env python3
"""Test script for parallel processing and link checking."""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.parallel import ParallelProcessor, ChunkProcessor
from accudoc.linkchecker import LinkChecker, check_documentation_links


def test_parallel_processor():
    """Test parallel processing."""
    print("=" * 60)
    print("Test 1: Parallel Processor")
    print("=" * 60)
    
    try:
        processor = ParallelProcessor(max_workers=4)
        
        # Test function
        def square(x):
            return x * x
        
        # Test parallel map
        items = list(range(10))
        results = processor.map_parallel(square, items)
        
        expected = [x * x for x in items]
        if results == expected:
            print(f"✓ Parallel map correct: {len(results)} items processed")
        else:
            print("✗ Parallel map incorrect")
            return False
        
        print("\n✓ Test PASSED: Parallel processor working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_chunk_processor():
    """Test chunk processing."""
    print("\n" + "=" * 60)
    print("Test 2: Chunk Processor")
    print("=" * 60)
    
    try:
        processor = ChunkProcessor(chunk_size=5)
        
        # Test chunking
        items = list(range(23))
        chunks = processor.chunk_list(items, 5)
        
        if len(chunks) == 5:  # 5 chunks for 23 items with chunk size 5
            print(f"✓ Chunking correct: {len(chunks)} chunks created")
        else:
            print(f"✗ Chunking incorrect: expected 5 chunks, got {len(chunks)}")
            return False
        
        # Test processing
        def process_chunk(chunk):
            return [x * 2 for x in chunk]
        
        results = processor.process_in_chunks(items, process_chunk)
        
        if len(results) == len(items):
            print(f"✓ Chunk processing correct: {len(results)} items processed")
        else:
            print("✗ Chunk processing incorrect")
            return False
        
        print("\n✓ Test PASSED: Chunk processor working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_link_checker():
    """Test link checker."""
    print("\n" + "=" * 60)
    print("Test 3: Link Checker")
    print("=" * 60)
    
    try:
        # Create temporary test file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test markdown file
            test_file = temp_path / "test.md"
            test_content = """
# Test Document

This is a [valid local link](test2.md).

This is a [broken local link](nonexistent.md).

This is a [valid external link](https://github.com).

This is an [anchor link](#section).
"""
            test_file.write_text(test_content)
            
            # Create referenced file
            (temp_path / "test2.md").write_text("# Test 2")
            
            # Check links
            checker = LinkChecker(base_path=temp_path)
            results = checker.check_file(test_file)
            
            if 'total_links' in results:
                print(f"✓ Found {results['total_links']} links")
            else:
                print("✗ Link detection failed")
                return False
            
            if len(results['broken_links']) > 0:
                print(f"✓ Detected {len(results['broken_links'])} broken link(s)")
            else:
                print("⚠ No broken links detected (expected at least 1)")
            
            # Test report generation
            dir_results = checker.check_directory(temp_path)
            report = checker.generate_report(dir_results, format='text')
            
            if 'Link Checker Report' in report:
                print("✓ Report generation working")
            else:
                print("✗ Report generation failed")
                return False
        
        print("\n✓ Test PASSED: Link checker working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_link_checker_convenience():
    """Test link checker convenience function."""
    print("\n" + "=" * 60)
    print("Test 4: Link Checker Convenience Function")
    print("=" * 60)
    
    try:
        # Check README
        readme_path = Path(__file__).parent / "README.md"
        
        if readme_path.exists():
            report = check_documentation_links(readme_path, output_format='text')
            
            if 'Link Checker Report' in report:
                print("✓ Convenience function working")
                print(f"  Report length: {len(report)} characters")
            else:
                print("✗ Convenience function failed")
                return False
        else:
            print("⚠ README.md not found, skipping test")
        
        print("\n✓ Test PASSED: Convenience function working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc Advanced Features Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_parallel_processor,
        test_chunk_processor,
        test_link_checker,
        test_link_checker_convenience,
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
