"""
Tests for new export formats (RST, AsciiDoc, LaTeX).
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.exporters import (
    ReStructuredTextExporter,
    AsciiDocExporter, 
    LaTeXExporter,
    DocumentExporter
)


# Sample markdown content for testing
SAMPLE_MARKDOWN = """# Main Title

This is a paragraph with **bold** and *italic* text, plus some `inline code`.

## Section One

Here's a list:
- First item
- Second item
- Third item

### Subsection

Here's some code:

```python
def hello():
    print("Hello, World!")
```

## Section Two

A link: [AccuDoc](https://github.com/jamesellette/AccuDoc)

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |
"""


def test_rst_exporter():
    """Test reStructuredText exporter."""
    print("=" * 60)
    print("Test 1: reStructuredText (RST) Export")
    print("=" * 60)
    
    try:
        exporter = ReStructuredTextExporter()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rst', delete=False) as f:
            output_path = f.name
        
        result = exporter.export(SAMPLE_MARKDOWN, output_path)
        
        # Read result
        with open(result, 'r') as f:
            rst_content = f.read()
        
        # Basic validation
        assert 'Main Title' in rst_content
        assert '=========' in rst_content  # RST header underline
        assert '.. code-block::' in rst_content
        assert '``inline code``' in rst_content
        assert '`AccuDoc <https://github.com/jamesellette/AccuDoc>`_' in rst_content
        
        print(f"✓ RST file created: {result}")
        print(f"✓ File size: {len(rst_content)} characters")
        print(f"✓ Contains proper RST formatting")
        
        # Show sample
        print("\nSample RST output:")
        print("-" * 60)
        print(rst_content[:300] + "...")
        
        # Clean up
        Path(result).unlink()
        
        print("\n✓ Test PASSED: RST export working\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_asciidoc_exporter():
    """Test AsciiDoc exporter."""
    print("=" * 60)
    print("Test 2: AsciiDoc Export")
    print("=" * 60)
    
    try:
        exporter = AsciiDocExporter()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            output_path = f.name
        
        result = exporter.export(SAMPLE_MARKDOWN, output_path)
        
        # Read result
        with open(result, 'r') as f:
            adoc_content = f.read()
        
        # Basic validation
        assert '= Main Title' in adoc_content
        assert '== Section One' in adoc_content
        assert '[source,python]' in adoc_content
        assert '----' in adoc_content  # Code block delimiters
        assert 'link:https://github.com/jamesellette/AccuDoc[AccuDoc]' in adoc_content
        
        print(f"✓ AsciiDoc file created: {result}")
        print(f"✓ File size: {len(adoc_content)} characters")
        print(f"✓ Contains proper AsciiDoc formatting")
        
        # Show sample
        print("\nSample AsciiDoc output:")
        print("-" * 60)
        print(adoc_content[:300] + "...")
        
        # Clean up
        Path(result).unlink()
        
        print("\n✓ Test PASSED: AsciiDoc export working\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_latex_exporter():
    """Test LaTeX exporter."""
    print("=" * 60)
    print("Test 3: LaTeX Export")
    print("=" * 60)
    
    try:
        exporter = LaTeXExporter(document_class='article')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            output_path = f.name
        
        result = exporter.export(SAMPLE_MARKDOWN, output_path)
        
        # Read result
        with open(result, 'r') as f:
            latex_content = f.read()
        
        # Basic validation
        assert '\\documentclass' in latex_content
        assert '\\section{Main Title}' in latex_content
        assert '\\subsection{Section One}' in latex_content
        assert '\\begin{lstlisting}' in latex_content
        assert '\\texttt{inline code}' in latex_content
        assert '\\href{' in latex_content
        assert '\\begin{itemize}' in latex_content
        assert '\\end{document}' in latex_content
        
        print(f"✓ LaTeX file created: {result}")
        print(f"✓ File size: {len(latex_content)} characters")
        print(f"✓ Contains proper LaTeX formatting")
        print(f"✓ Complete LaTeX document with packages")
        
        # Show sample
        print("\nSample LaTeX output:")
        print("-" * 60)
        print(latex_content[:400] + "...")
        
        # Clean up
        Path(result).unlink()
        
        print("\n✓ Test PASSED: LaTeX export working\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_document_exporter_integration():
    """Test DocumentExporter integration with new formats."""
    print("=" * 60)
    print("Test 4: DocumentExporter Integration")
    print("=" * 60)
    
    try:
        formats_to_test = [
            ('rst', '.rst'),
            ('asciidoc', '.adoc'),
            ('latex', '.tex'),
            ('restructuredtext', '.rst'),
            ('adoc', '.adoc'),
            ('tex', '.tex'),
        ]
        
        passed = 0
        for format_name, extension in formats_to_test:
            with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as f:
                output_path = f.name
            
            result = DocumentExporter.export(
                SAMPLE_MARKDOWN,
                output_path,
                format=format_name
            )
            
            # Verify file exists and has content
            if Path(result).exists() and Path(result).stat().st_size > 0:
                print(f"  ✓ Format '{format_name}' export successful")
                Path(result).unlink()
                passed += 1
            else:
                print(f"  ✗ Format '{format_name}' export failed")
        
        print(f"\n✓ DocumentExporter supports all new formats: {passed}/{len(formats_to_test)}")
        print("\n✓ Test PASSED: Integration working\n")
        return passed == len(formats_to_test)
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_supported_formats():
    """Test that new formats are in supported formats list."""
    print("=" * 60)
    print("Test 5: Supported Formats List")
    print("=" * 60)
    
    try:
        supported = DocumentExporter.get_supported_formats()
        
        required_formats = ['rst', 'asciidoc', 'latex', 'restructuredtext', 'adoc', 'tex']
        
        print(f"Supported formats: {', '.join(sorted(supported))}")
        
        for fmt in required_formats:
            if fmt in supported:
                print(f"  ✓ '{fmt}' is supported")
            else:
                print(f"  ✗ '{fmt}' is NOT supported")
                return False
        
        print("\n✓ Test PASSED: All new formats are registered\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc New Export Formats Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_rst_exporter,
        test_asciidoc_exporter,
        test_latex_exporter,
        test_document_exporter_integration,
        test_supported_formats,
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
