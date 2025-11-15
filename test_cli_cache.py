#!/usr/bin/env python3
"""Test script for CLI and caching features."""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.scanner import RepositoryScanner
from accudoc.cache import CacheManager
from accudoc_cli import AccuDocCLI


def test_cache_manager():
    """Test cache manager functionality."""
    print("=" * 60)
    print("Test 1: Cache Manager")
    print("=" * 60)
    
    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some test files
            test_file = temp_path / "test.txt"
            test_file.write_text("Test content")
            
            # Initialize cache
            cache = CacheManager(str(temp_path))
            cache.initialize()
            
            # Test file caching
            cache.cache_file_data(test_file, {"key": "value"})
            
            # Check if file is cached
            if cache.is_file_cached(test_file):
                print("✓ File successfully cached")
            else:
                print("✗ File caching failed")
                return False
            
            # Get cached data
            cached_data = cache.get_cached_data(test_file)
            if cached_data and cached_data.get("key") == "value":
                print("✓ Cached data retrieved correctly")
            else:
                print("✗ Cached data retrieval failed")
                return False
            
            # Save cache
            cache.save()
            
            # Check cache stats
            stats = cache.get_stats()
            if stats['cached_files'] > 0:
                print(f"✓ Cache stats: {stats['cached_files']} files cached")
            else:
                print("✗ Cache stats incorrect")
                return False
            
            # Test cache clearing
            cache.clear()
            stats = cache.get_stats()
            if stats['cached_files'] == 0:
                print("✓ Cache cleared successfully")
            else:
                print("✗ Cache clearing failed")
                return False
        
        print("\n✓ Test PASSED: Cache manager working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_scanner_with_cache():
    """Test scanner with caching enabled."""
    print("\n" + "=" * 60)
    print("Test 2: Scanner with Cache")
    print("=" * 60)
    
    try:
        repo_path = str(Path(__file__).parent)
        
        # First scan (no cache)
        print("First scan (creating cache)...")
        scanner1 = RepositoryScanner(repo_path)
        repo_info1 = scanner1.scan()
        
        if repo_info1 and 'files' in repo_info1:
            print(f"✓ First scan completed: {len(repo_info1['files'])} files")
        else:
            print("✗ First scan failed")
            return False
        
        # Second scan (should use cache)
        print("\nSecond scan (using cache)...")
        scanner2 = RepositoryScanner(repo_path)
        repo_info2 = scanner2.scan()
        
        if repo_info2 and 'files' in repo_info2:
            print(f"✓ Second scan completed: {len(repo_info2['files'])} files")
        else:
            print("✗ Second scan failed")
            return False
        
        # Compare results
        if len(repo_info1['files']) == len(repo_info2['files']):
            print("✓ Both scans returned same number of files")
        else:
            print("✗ Scan results differ")
            return False
        
        # Test disabling cache
        print("\nThird scan (cache disabled)...")
        scanner3 = RepositoryScanner(repo_path)
        scanner3.disable_cache()
        repo_info3 = scanner3.scan()
        
        if repo_info3 and 'files' in repo_info3:
            print(f"✓ Third scan completed: {len(repo_info3['files'])} files")
        else:
            print("✗ Third scan failed")
            return False
        
        print("\n✓ Test PASSED: Scanner caching working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_commands():
    """Test CLI commands."""
    print("\n" + "=" * 60)
    print("Test 3: CLI Commands")
    print("=" * 60)
    
    try:
        import argparse
        
        cli = AccuDocCLI()
        
        # Test info command
        print("Testing info command...")
        args = argparse.Namespace(command='info', verbose=0, quiet=True)
        result = cli.info_command(args)
        if result == 0:
            print("✓ Info command successful")
        else:
            print("✗ Info command failed")
            return False
        
        # Test cache stats command
        print("\nTesting cache stats command...")
        repo_path = str(Path(__file__).parent)
        args = argparse.Namespace(
            command='cache',
            cache_action='stats',
            repository=repo_path,
            verbose=0,
            quiet=True
        )
        result = cli.cache_command(args)
        if result == 0:
            print("✓ Cache stats command successful")
        else:
            print("✗ Cache stats command failed")
            return False
        
        print("\n✓ Test PASSED: CLI commands working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_export():
    """Test CLI export command."""
    print("\n" + "=" * 60)
    print("Test 4: CLI Export Command")
    print("=" * 60)
    
    try:
        import argparse
        
        cli = AccuDocCLI()
        repo_path = str(Path(__file__).parent)
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_export.md"
            
            print("Testing export command...")
            args = argparse.Namespace(
                command='export',
                repository=repo_path,
                output=str(output_file),
                template='minimal',
                format='markdown',
                theme='default',
                markdown_flavor='github',
                no_cache=False,
                verbose=0,
                quiet=True
            )
            
            result = cli.export_command(args)
            
            if result == 0:
                print("✓ Export command completed successfully")
            else:
                print("✗ Export command failed")
                return False
            
            # Check if output file was created
            if output_file.exists():
                print(f"✓ Output file created: {output_file.stat().st_size} bytes")
            else:
                print("✗ Output file not created")
                return False
            
            # Test with different formats
            html_file = Path(temp_dir) / "test_export.html"
            args.output = str(html_file)
            args.format = 'html'
            args.theme = 'dark'
            
            result = cli.export_command(args)
            
            if result == 0 and html_file.exists():
                print(f"✓ HTML export successful: {html_file.stat().st_size} bytes")
            else:
                print("✗ HTML export failed")
                return False
        
        print("\n✓ Test PASSED: CLI export working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_scan_and_generate():
    """Test separate scan and generate commands."""
    print("\n" + "=" * 60)
    print("Test 5: Scan + Generate Commands")
    print("=" * 60)
    
    try:
        import argparse
        
        cli = AccuDocCLI()
        repo_path = str(Path(__file__).parent)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            scan_file = Path(temp_dir) / "scan.json"
            output_file = Path(temp_dir) / "docs.md"
            
            # Test scan command
            print("Testing scan command...")
            args = argparse.Namespace(
                command='scan',
                repository=repo_path,
                output=str(scan_file),
                json=False,
                no_cache=False,
                verbose=0,
                quiet=True
            )
            
            result = cli.scan_command(args)
            
            if result == 0 and scan_file.exists():
                print(f"✓ Scan completed: {scan_file.stat().st_size} bytes")
            else:
                print("✗ Scan failed")
                return False
            
            # Test generate command
            print("\nTesting generate command...")
            args = argparse.Namespace(
                command='generate',
                scan_file=str(scan_file),
                output=str(output_file),
                template='default',
                format='markdown',
                theme='default',
                markdown_flavor='github',
                verbose=0,
                quiet=True
            )
            
            result = cli.generate_command(args)
            
            if result == 0 and output_file.exists():
                print(f"✓ Generate completed: {output_file.stat().st_size} bytes")
            else:
                print("✗ Generate failed")
                return False
        
        print("\n✓ Test PASSED: Scan and generate working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc CLI and Caching Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_cache_manager,
        test_scanner_with_cache,
        test_cli_commands,
        test_cli_export,
        test_scan_and_generate,
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
