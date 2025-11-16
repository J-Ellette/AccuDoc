#!/usr/bin/env python3
"""Test script for AccuDoc application."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator


def test_scanner_local_repo():
    """Test scanning a local repository."""
    print("=" * 60)
    print("Test 1: Scanning Local Repository")
    print("=" * 60)
    
    try:
        scanner = RepositoryScanner(str(Path(__file__).parent))
        repo_info = scanner.scan()
        
        print(f"✓ Repository Name: {repo_info['name']}")
        print(f"✓ Files Found: {len(repo_info['files'])}")
        print(f"✓ Languages: {repo_info['languages']}")
        print(f"✓ Dependencies: {list(repo_info['dependencies'].keys())}")
        print(f"✓ Documentation Files: {len(repo_info['documentation'])}")
        
        if repo_info['files']:
            print("\n✓ Test PASSED: Scanner successfully analyzed local repository")
            return True
        else:
            print("\n✗ Test FAILED: No files found")
            return False
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        return False


def test_generator():
    """Test document generation."""
    print("\n" + "=" * 60)
    print("Test 2: Generating Documentation")
    print("=" * 60)
    
    try:
        scanner = RepositoryScanner(str(Path(__file__).parent))
        repo_info = scanner.scan()
        
        generator = DocumentGenerator(repo_info)
        documentation = generator.generate_all()
        
        print(f"✓ Generated documentation: {len(documentation)} characters")
        
        # Check for key sections
        sections = [
            "## Overview",
            "## Features",
            "## Technology Stack",
            "## Installation",
            "## Usage",
            "## Project Structure",
            "## License"
        ]
        
        found_sections = []
        for section in sections:
            if section in documentation:
                found_sections.append(section)
                print(f"✓ Found section: {section}")
            else:
                print(f"✗ Missing section: {section}")
                
        if len(found_sections) >= 5:
            print(f"\n✓ Test PASSED: Generated documentation with {len(found_sections)} sections")
            return True
        else:
            print(f"\n✗ Test FAILED: Only found {len(found_sections)} sections")
            return False
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        return False


def test_language_detection():
    """Test language detection functionality."""
    print("\n" + "=" * 60)
    print("Test 3: Language Detection")
    print("=" * 60)
    
    try:
        scanner = RepositoryScanner(str(Path(__file__).parent))
        repo_info = scanner.scan()
        
        languages = repo_info['languages']
        
        if 'Python' in languages and languages['Python'] > 0:
            print(f"✓ Detected Python: {languages['Python']} files")
            print("\n✓ Test PASSED: Language detection working")
            return True
        else:
            print("\n✗ Test FAILED: Python not detected")
            return False
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        return False


def test_file_structure():
    """Test file structure detection."""
    print("\n" + "=" * 60)
    print("Test 4: File Structure Detection")
    print("=" * 60)
    
    try:
        scanner = RepositoryScanner(str(Path(__file__).parent))
        repo_info = scanner.scan()
        
        files = repo_info['files']
        
        # Check for expected files
        expected_files = ['main.py', 'README.md', 'requirements.txt']
        found = []
        
        for expected in expected_files:
            if expected in files:
                found.append(expected)
                print(f"✓ Found expected file: {expected}")
                
        if len(found) >= 2:
            print(f"\n✓ Test PASSED: Found {len(found)} expected files")
            return True
        else:
            print(f"\n✗ Test FAILED: Only found {len(found)} expected files")
            return False
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_scanner_local_repo,
        test_generator,
        test_language_detection,
        test_file_structure,
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
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
