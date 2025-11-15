"""
Unit tests for live testbed functionality.
"""

import unittest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Try to import live testbed
try:
    from accudoc.live_testbed import (
        LiveTestbed,
        Language,
        ExecutionStatus,
        CodeSnippet,
        ExecutionResult
    )
    TESTBED_AVAILABLE = True
except ImportError:
    TESTBED_AVAILABLE = False


@unittest.skipUnless(TESTBED_AVAILABLE, "Live testbed not available (docker package required)")
class TestLiveTestbed(unittest.TestCase):
    """Test cases for LiveTestbed class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.markdown_sample = '''
# Example Documentation

Here's a Python example:

```python
print("Hello, World!")
```

And a JavaScript example:

```javascript
console.log("Hello from JS!");
```

Some Java code:

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}
```
'''
    
    def test_extract_code_snippets(self):
        """Test extracting code snippets from markdown."""
        with patch('accudoc.live_testbed.docker'):
            testbed = LiveTestbed()
            snippets = testbed.extract_code_snippets(self.markdown_sample)
            
            self.assertEqual(len(snippets), 3)
            self.assertEqual(snippets[0].language, Language.PYTHON)
            self.assertEqual(snippets[1].language, Language.JAVASCRIPT)
            self.assertEqual(snippets[2].language, Language.JAVA)
            self.assertIn("print", snippets[0].code)
            self.assertIn("console.log", snippets[1].code)
            self.assertIn("System.out.println", snippets[2].code)
    
    def test_detect_language(self):
        """Test language detection."""
        with patch('accudoc.live_testbed.docker'):
            testbed = LiveTestbed()
            
            self.assertEqual(testbed._detect_language('python'), Language.PYTHON)
            self.assertEqual(testbed._detect_language('py'), Language.PYTHON)
            self.assertEqual(testbed._detect_language('javascript'), Language.JAVASCRIPT)
            self.assertEqual(testbed._detect_language('js'), Language.JAVASCRIPT)
            self.assertEqual(testbed._detect_language('java'), Language.JAVA)
            self.assertEqual(testbed._detect_language('go'), Language.GO)
            self.assertIsNone(testbed._detect_language('unknown'))
    
    @patch('accudoc.live_testbed.docker')
    def test_execute_code_success(self, mock_docker):
        """Test successful code execution."""
        # Mock Docker client
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        # Mock container
        mock_container = MagicMock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b'Hello, World!'
        mock_client.containers.run.return_value = mock_container
        
        # Mock image exists
        mock_client.images.get.return_value = MagicMock()
        
        testbed = LiveTestbed(enable_cache=False)
        
        result = testbed.execute_code('print("Hello, World!")', Language.PYTHON, check_cache=False)
        
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.output, 'Hello, World!')
        self.assertEqual(result.language, Language.PYTHON)
        self.assertIn('Validated', result.badge)
    
    @patch('accudoc.live_testbed.docker')
    def test_execute_code_failure(self, mock_docker):
        """Test failed code execution."""
        # Mock Docker client
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        # Mock container with error
        mock_container = MagicMock()
        mock_container.wait.return_value = {'StatusCode': 1}
        mock_container.logs.return_value = b'SyntaxError: invalid syntax'
        mock_client.containers.run.return_value = mock_container
        
        # Mock image exists
        mock_client.images.get.return_value = MagicMock()
        
        testbed = LiveTestbed(enable_cache=False)
        
        result = testbed.execute_code('print(', Language.PYTHON, check_cache=False)
        
        self.assertEqual(result.status, ExecutionStatus.FAILURE)
        self.assertIn('SyntaxError', result.error)
        self.assertIn('Failed', result.badge)
    
    @patch('accudoc.live_testbed.docker')
    def test_execution_cache(self, mock_docker):
        """Test execution result caching."""
        # Mock Docker client
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        # Mock container
        mock_container = MagicMock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b'Cached result'
        mock_client.containers.run.return_value = mock_container
        
        # Mock image exists
        mock_client.images.get.return_value = MagicMock()
        
        testbed = LiveTestbed(enable_cache=True)
        
        code = 'print("Test")'
        
        # First execution
        result1 = testbed.execute_code(code, Language.PYTHON)
        self.assertEqual(mock_client.containers.run.call_count, 1)
        
        # Second execution (should use cache)
        result2 = testbed.execute_code(code, Language.PYTHON)
        self.assertEqual(mock_client.containers.run.call_count, 1)  # Still 1, not called again
        
        # Results should be identical
        self.assertEqual(result1.code_hash, result2.code_hash)
    
    def test_generate_badge(self):
        """Test badge generation for different statuses."""
        with patch('accudoc.live_testbed.docker'):
            testbed = LiveTestbed()
            
            success_badge = testbed._generate_badge(ExecutionStatus.SUCCESS)
            self.assertIn('Validated', success_badge)
            
            failure_badge = testbed._generate_badge(ExecutionStatus.FAILURE)
            self.assertIn('Failed', failure_badge)
            
            timeout_badge = testbed._generate_badge(ExecutionStatus.TIMEOUT)
            self.assertIn('Timeout', timeout_badge)
            
            error_badge = testbed._generate_badge(ExecutionStatus.ERROR)
            self.assertIn('Error', error_badge)
    
    @patch('accudoc.live_testbed.docker')
    def test_validate_documentation(self, mock_docker):
        """Test documentation validation without execution."""
        # Mock Docker client
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        testbed = LiveTestbed()
        
        # Validate without auto-execution
        report = testbed.validate_documentation(self.markdown_sample, auto_execute=False)
        
        self.assertEqual(report['total_snippets'], 3)
        self.assertEqual(report['executed'], 0)
        self.assertEqual(len(report['snippets']), 3)
    
    @patch('accudoc.live_testbed.docker')
    def test_validate_documentation_with_execution(self, mock_docker):
        """Test documentation validation with auto-execution."""
        # Mock Docker client
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        # Mock successful execution
        mock_container = MagicMock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b'Success'
        mock_client.containers.run.return_value = mock_container
        mock_client.images.get.return_value = MagicMock()
        
        testbed = LiveTestbed(enable_cache=False)
        
        # Validate with auto-execution
        report = testbed.validate_documentation(self.markdown_sample, auto_execute=True)
        
        self.assertEqual(report['total_snippets'], 3)
        self.assertEqual(report['executed'], 3)
        self.assertEqual(report['success'], 3)
    
    def test_cache_stats(self):
        """Test cache statistics."""
        with patch('accudoc.live_testbed.docker'):
            testbed = LiveTestbed(enable_cache=True)
            
            # Empty cache
            stats = testbed.get_cache_stats()
            self.assertEqual(stats['cached_executions'], 0)
            
            # Add mock cached result
            from accudoc.live_testbed import ExecutionResult
            mock_result = ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output='test',
                error='',
                execution_time=0.5,
                timestamp='2024-01-01',
                badge='[✓ Validated]',
                language=Language.PYTHON,
                code_hash='abc123'
            )
            testbed.cache['abc123'] = mock_result
            
            stats = testbed.get_cache_stats()
            self.assertEqual(stats['cached_executions'], 1)
            self.assertEqual(stats['success_rate'], 100.0)
    
    def test_clear_cache(self):
        """Test cache clearing."""
        with patch('accudoc.live_testbed.docker'):
            testbed = LiveTestbed(enable_cache=True)
            
            # Add mock cache entry
            testbed.cache['test'] = 'value'
            self.assertEqual(len(testbed.cache), 1)
            
            # Clear cache
            testbed.clear_cache()
            self.assertEqual(len(testbed.cache), 0)
    
    def test_context_manager(self):
        """Test using testbed as context manager."""
        with patch('accudoc.live_testbed.docker') as mock_docker:
            mock_client = MagicMock()
            mock_docker.from_env.return_value = mock_client
            
            with LiveTestbed() as testbed:
                self.assertIsNotNone(testbed)
            
            # Should close client
            mock_client.close.assert_called_once()


@unittest.skipUnless(TESTBED_AVAILABLE, "Live testbed not available (docker package required)")
class TestCodeSnippet(unittest.TestCase):
    """Test cases for CodeSnippet class."""
    
    def test_code_snippet_creation(self):
        """Test creating a code snippet."""
        from accudoc.live_testbed import CodeSnippet
        snippet = CodeSnippet(
            code='print("test")',
            language=Language.PYTHON,
            line_number=10,
            title='Test snippet'
        )
        
        self.assertEqual(snippet.code, 'print("test")')
        self.assertEqual(snippet.language, Language.PYTHON)
        self.assertEqual(snippet.line_number, 10)
        self.assertEqual(snippet.title, 'Test snippet')


@unittest.skipUnless(TESTBED_AVAILABLE, "Live testbed not available (docker package required)")
class TestExecutionResult(unittest.TestCase):
    """Test cases for ExecutionResult class."""
    
    def test_execution_result_to_dict(self):
        """Test converting execution result to dictionary."""
        from accudoc.live_testbed import ExecutionResult
        result = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            output='Hello',
            error='',
            execution_time=1.5,
            timestamp='2024-01-01T00:00:00',
            badge='[✓ Validated]',
            language=Language.PYTHON,
            code_hash='abc123'
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict['status'], 'success')
        self.assertEqual(result_dict['output'], 'Hello')
        self.assertEqual(result_dict['language'], 'python')
        self.assertEqual(result_dict['execution_time'], 1.5)


if __name__ == '__main__':
    unittest.main()
