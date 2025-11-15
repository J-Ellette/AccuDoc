#!/usr/bin/env python3
"""Test script for GitLab API and package analyzer."""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.gitlab_api import GitLabAPIClient
from accudoc.package_analyzer import PackageVersionAnalyzer


def test_gitlab_url_parsing():
    """Test GitLab URL parsing."""
    print("=" * 60)
    print("Test 1: GitLab URL Parsing")
    print("=" * 60)
    
    try:
        client = GitLabAPIClient()
        
        # Test various URL formats
        test_cases = [
            ('https://gitlab.com/owner/project', ('owner', 'project')),
            ('https://gitlab.com/owner/project/', ('owner', 'project')),
            ('https://gitlab.com/owner/project.git', ('owner', 'project')),
            ('git@gitlab.com:owner/project.git', ('owner', 'project')),
            ('https://gitlab.com/group/subgroup/project', ('group/subgroup', 'project')),
        ]
        
        for url, expected in test_cases:
            result = client.parse_gitlab_url(url)
            if result == expected:
                print(f"✓ Parsed {url} correctly")
            else:
                print(f"✗ Failed to parse {url}: got {result}, expected {expected}")
                return False
        
        print("\n✓ Test PASSED: GitLab URL parsing working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_package_analyzer_python():
    """Test package analyzer for Python."""
    print("\n" + "=" * 60)
    print("Test 2: Package Analyzer - Python")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test requirements.txt
            req_file = temp_path / 'requirements.txt'
            req_file.write_text("""
django==2.2.0
flask>=1.0
requests==2.25.0
# Comment
pytest>=6.0.0
""")
            
            analyzer = PackageVersionAnalyzer()
            dependencies = {'Python': ['django', 'flask', 'requests', 'pytest']}
            
            result = analyzer.analyze_dependencies(temp_path, dependencies)
            
            if 'package_managers' in result:
                print("✓ Analysis completed")
            else:
                print("✗ Analysis failed")
                return False
            
            pip_data = result['package_managers'].get('pip', {})
            packages = pip_data.get('packages', [])
            
            if len(packages) > 0:
                print(f"✓ Found {len(packages)} packages")
            else:
                print("✗ No packages found")
                return False
            
            # Check if vulnerabilities were detected
            vulnerable = pip_data.get('vulnerable', [])
            if len(vulnerable) > 0:
                print(f"✓ Detected {len(vulnerable)} vulnerable package(s)")
            else:
                print("⚠ No vulnerabilities detected (may be expected)")
            
            print("\n✓ Test PASSED: Python package analyzer working")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_package_analyzer_javascript():
    """Test package analyzer for JavaScript."""
    print("\n" + "=" * 60)
    print("Test 3: Package Analyzer - JavaScript")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test package.json
            pkg_file = temp_path / 'package.json'
            pkg_file.write_text("""{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "lodash": "^4.17.20",
    "axios": "^0.21.0"
  },
  "devDependencies": {
    "jest": "^27.0.0"
  }
}""")
            
            analyzer = PackageVersionAnalyzer()
            dependencies = {'JavaScript': ['lodash', 'axios', 'jest']}
            
            result = analyzer.analyze_dependencies(temp_path, dependencies)
            
            npm_data = result['package_managers'].get('npm', {})
            packages = npm_data.get('packages', [])
            
            if len(packages) >= 3:
                print(f"✓ Found {len(packages)} packages")
            else:
                print(f"✗ Expected at least 3 packages, found {len(packages)}")
                return False
            
            # Check package types
            prod_packages = [p for p in packages if p.get('type') == 'production']
            dev_packages = [p for p in packages if p.get('type') == 'dev']
            
            if len(prod_packages) > 0 and len(dev_packages) > 0:
                print(f"✓ Correctly identified production and dev dependencies")
            else:
                print("✗ Failed to classify dependencies")
                return False
            
            print("\n✓ Test PASSED: JavaScript package analyzer working")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_security_report_generation():
    """Test security report generation."""
    print("\n" + "=" * 60)
    print("Test 4: Security Report Generation")
    print("=" * 60)
    
    try:
        analyzer = PackageVersionAnalyzer()
        
        # Create sample analysis result
        analysis = {
            'analyzed_at': '2025-11-14T08:00:00',
            'package_managers': {
                'pip': {
                    'packages': [
                        {'name': 'django', 'version': '2.2.0'},
                        {'name': 'flask', 'version': '1.0'}
                    ],
                    'vulnerable': [
                        {
                            'name': 'django',
                            'current_version': '2.2.0',
                            'issue': 'Known vulnerabilities',
                            'recommendation': 'Update to latest'
                        }
                    ],
                    'recommendations': ['Update vulnerable packages']
                }
            },
            'summary': {
                'total_packages': 2,
                'outdated_packages': 0,
                'vulnerable_packages': 1
            }
        }
        
        report = analyzer.generate_security_report(analysis)
        
        if 'Package Security Report' in report:
            print("✓ Report generated")
        else:
            print("✗ Report generation failed")
            return False
        
        if 'Vulnerable Packages' in report:
            print("✓ Vulnerabilities section included")
        else:
            print("✗ Vulnerabilities section missing")
            return False
        
        if 'django' in report:
            print("✓ Vulnerable package listed")
        else:
            print("✗ Vulnerable package not listed")
            return False
        
        print(f"  Report length: {len(report)} characters")
        
        print("\n✓ Test PASSED: Security report generation working")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc GitLab & Package Analyzer Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_gitlab_url_parsing,
        test_package_analyzer_python,
        test_package_analyzer_javascript,
        test_security_report_generation,
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
