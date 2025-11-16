"""
Tests for ReadTheDocs/Sphinx integration.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from accudoc.readthedocs import ReadTheDocsGenerator, generate_readthedocs_project


SAMPLE_MARKDOWN = """# My Project

This is a sample project documentation.

## Installation

Install using pip:

```bash
pip install myproject
```

## Usage

Here's how to use it:

```python
import myproject
myproject.run()
```

## API Reference

### MyClass

A useful class.
"""


def test_basic_sphinx_generation():
    """Test basic Sphinx project generation."""
    print("=" * 60)
    print("Test 1: Basic Sphinx Project Generation")
    print("=" * 60)
    
    try:
        generator = ReadTheDocsGenerator(
            project_name="TestProject",
            author="Test Author",
            version="1.0.0",
            theme="sphinx_rtd_theme"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / 'sphinx-project'
            
            result = generator.generate_sphinx_project(output_dir, SAMPLE_MARKDOWN)
            
            # Check directory structure
            assert result.exists(), "Output directory should exist"
            assert (result / 'source').exists(), "source/ directory should exist"
            assert (result / 'source' / '_static').exists(), "_static/ should exist"
            assert (result / 'source' / '_templates').exists(), "_templates/ should exist"
            
            print(f"✓ Sphinx project created at: {result}")
            print(f"✓ Directory structure is correct")
            
            # Check required files
            required_files = [
                'source/conf.py',
                'source/index.rst',
                'Makefile',
                'make.bat',
                'requirements.txt',
                '.readthedocs.yaml'
            ]
            
            for file_path in required_files:
                file = result / file_path
                assert file.exists(), f"{file_path} should exist"
                print(f"✓ {file_path} exists")
            
            print("\n✓ Test PASSED: Basic Sphinx project generation working\n")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_conf_py_content():
    """Test conf.py content."""
    print("=" * 60)
    print("Test 2: conf.py Configuration File")
    print("=" * 60)
    
    try:
        generator = ReadTheDocsGenerator(
            project_name="TestProject",
            author="Test Author",
            version="2.0.0"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / 'sphinx-project'
            result = generator.generate_sphinx_project(output_dir, SAMPLE_MARKDOWN)
            
            conf_path = result / 'source' / 'conf.py'
            conf_content = conf_path.read_text()
            
            # Check required configuration elements
            assert "project = 'TestProject'" in conf_content
            assert "author = 'Test Author'" in conf_content
            assert "version = '2.0.0'" in conf_content
            assert "sphinx.ext.autodoc" in conf_content
            assert "html_theme = 'sphinx_rtd_theme'" in conf_content
            
            print("✓ Project name is set correctly")
            print("✓ Author is set correctly")
            print("✓ Version is set correctly")
            print("✓ Extensions are configured")
            print("✓ Theme is configured")
            
            print("\n✓ Test PASSED: conf.py configuration is correct\n")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_index_rst_content():
    """Test index.rst content."""
    print("=" * 60)
    print("Test 3: index.rst Content")
    print("=" * 60)
    
    try:
        generator = ReadTheDocsGenerator(
            project_name="TestProject",
            author="Test Author"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / 'sphinx-project'
            result = generator.generate_sphinx_project(output_dir, SAMPLE_MARKDOWN)
            
            index_path = result / 'source' / 'index.rst'
            index_content = index_path.read_text()
            
            # Check RST formatting
            assert 'TestProject' in index_content
            assert '.. toctree::' in index_content
            assert ':maxdepth:' in index_content
            assert 'My Project' in index_content
            assert 'Installation' in index_content
            assert '.. code-block::' in index_content
            assert ':ref:`genindex`' in index_content
            
            print("✓ Project title is present")
            print("✓ TOC tree directive is present")
            print("✓ Markdown content converted to RST")
            print("✓ Code blocks formatted correctly")
            print("✓ Index references included")
            
            # Show sample
            print("\nSample index.rst:")
            print("-" * 60)
            print(index_content[:300] + "...")
            
            print("\n✓ Test PASSED: index.rst content is correct\n")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_makefile_content():
    """Test Makefile content."""
    print("=" * 60)
    print("Test 4: Makefile and Build Files")
    print("=" * 60)
    
    try:
        generator = ReadTheDocsGenerator(project_name="TestProject", author="Test")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / 'sphinx-project'
            result = generator.generate_sphinx_project(output_dir, SAMPLE_MARKDOWN)
            
            # Check Makefile
            makefile = result / 'Makefile'
            makefile_content = makefile.read_text()
            assert 'SPHINXBUILD' in makefile_content
            assert 'SOURCEDIR' in makefile_content
            assert 'BUILDDIR' in makefile_content
            print("✓ Makefile is properly formatted")
            
            # Check make.bat
            make_bat = result / 'make.bat'
            make_bat_content = make_bat.read_text()
            assert 'sphinx-build' in make_bat_content
            print("✓ make.bat exists for Windows support")
            
            print("\n✓ Test PASSED: Build files are correct\n")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_requirements_file():
    """Test requirements.txt file."""
    print("=" * 60)
    print("Test 5: Requirements File")
    print("=" * 60)
    
    try:
        generator = ReadTheDocsGenerator(project_name="TestProject", author="Test")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / 'sphinx-project'
            result = generator.generate_sphinx_project(output_dir, SAMPLE_MARKDOWN)
            
            req_path = result / 'requirements.txt'
            req_content = req_path.read_text()
            
            assert 'sphinx' in req_content
            assert 'sphinx_rtd_theme' in req_content
            
            print("✓ Sphinx is in requirements")
            print("✓ Theme is in requirements")
            print(f"\nRequirements:")
            print("-" * 60)
            print(req_content)
            
            print("\n✓ Test PASSED: Requirements file is correct\n")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_readthedocs_yaml():
    """Test .readthedocs.yaml configuration."""
    print("=" * 60)
    print("Test 6: ReadTheDocs Configuration")
    print("=" * 60)
    
    try:
        generator = ReadTheDocsGenerator(project_name="TestProject", author="Test")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / 'sphinx-project'
            result = generator.generate_sphinx_project(output_dir, SAMPLE_MARKDOWN)
            
            rtd_path = result / '.readthedocs.yaml'
            rtd_content = rtd_path.read_text()
            
            assert 'version: 2' in rtd_content
            assert 'sphinx:' in rtd_content
            assert 'python:' in rtd_content
            assert 'formats:' in rtd_content
            
            print("✓ ReadTheDocs config version is set")
            print("✓ Sphinx build is configured")
            print("✓ Python version is specified")
            print("✓ Output formats are configured")
            
            print("\n✓ Test PASSED: ReadTheDocs configuration is correct\n")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_function():
    """Test convenience function."""
    print("=" * 60)
    print("Test 7: Convenience Function")
    print("=" * 60)
    
    try:
        repo_info = {
            'name': 'MyRepo',
            'git_info': {
                'version': '1.2.3'
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = str(Path(tmpdir) / 'docs')
            
            result = generate_readthedocs_project(repo_info, output_dir, SAMPLE_MARKDOWN)
            
            assert result.exists()
            assert (result / 'source' / 'conf.py').exists()
            assert (result / 'source' / 'index.rst').exists()
            
            # Check that repo_info was used
            conf_content = (result / 'source' / 'conf.py').read_text()
            assert 'MyRepo' in conf_content
            assert '1.2.3' in conf_content
            
            print("✓ Convenience function works")
            print("✓ Repository info is used correctly")
            
            print("\n✓ Test PASSED: Convenience function working\n")
            return True
            
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc ReadTheDocs Integration Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_basic_sphinx_generation,
        test_conf_py_content,
        test_index_rst_content,
        test_makefile_content,
        test_requirements_file,
        test_readthedocs_yaml,
        test_convenience_function,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test failed with exception: {str(e)}\n")
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
