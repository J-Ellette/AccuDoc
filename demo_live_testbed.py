#!/usr/bin/env python3
"""
Demo: Live Documentation Testbed

Demonstrates the interactive documentation testbed feature that executes
code snippets in secure Docker containers.
"""

import sys
from pathlib import Path

# Try to import live testbed
try:
    from accudoc.live_testbed import LiveTestbed, Language, ExecutionStatus
    TESTBED_AVAILABLE = True
except ImportError:
    print("❌ Live testbed is not available.")
    print("   Install docker package: pip install docker")
    print("   And ensure Docker is installed and running.")
    sys.exit(1)


def print_separator(title=""):
    """Print a separator line."""
    if title:
        print(f"\n{'=' * 70}")
        print(f"  {title}")
        print('=' * 70)
    else:
        print('-' * 70)


def demo_extract_snippets():
    """Demonstrate extracting code snippets from markdown."""
    print_separator("1. Extracting Code Snippets from Documentation")
    
    markdown_doc = '''
# Sample Documentation

Here's a Python example:

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

And a JavaScript example:

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}

console.log(greet("World"));
```

A simple Go program:

```go
package main
import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```
'''
    
    try:
        with LiveTestbed() as testbed:
            snippets = testbed.extract_code_snippets(markdown_doc)
            
            print(f"\n✓ Found {len(snippets)} code snippets:")
            for i, snippet in enumerate(snippets, 1):
                print(f"\n  Snippet {i}:")
                print(f"  - Language: {snippet.language.value}")
                print(f"  - Line number: {snippet.line_number}")
                print(f"  - Code preview: {snippet.code[:50]}...")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_execute_code():
    """Demonstrate executing code in Docker containers."""
    print_separator("2. Executing Code in Docker Containers")
    
    examples = [
        {
            'name': 'Python - Success',
            'language': Language.PYTHON,
            'code': '''import math
result = math.sqrt(16)
print(f"Square root of 16 is {result}")'''
        },
        {
            'name': 'JavaScript - Success',
            'language': Language.JAVASCRIPT,
            'code': '''const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log('Sum:', sum);'''
        },
        {
            'name': 'Python - Syntax Error',
            'language': Language.PYTHON,
            'code': 'print("Missing closing quote'
        }
    ]
    
    try:
        with LiveTestbed(timeout=15) as testbed:
            for example in examples:
                print(f"\n{example['name']}:")
                print_separator()
                
                result = testbed.execute_code(
                    example['code'],
                    example['language'],
                    check_cache=False
                )
                
                print(f"Status: {result.status.value}")
                print(f"Badge: {result.badge}")
                print(f"Execution time: {result.execution_time:.2f}s")
                
                if result.status == ExecutionStatus.SUCCESS:
                    print(f"\n✓ Output:\n{result.output}")
                elif result.status == ExecutionStatus.FAILURE:
                    print(f"\n✗ Error:\n{result.error}")
                else:
                    print(f"\n⚠ Error:\n{result.error}")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_caching():
    """Demonstrate execution result caching."""
    print_separator("3. Execution Result Caching")
    
    code = '''for i in range(5):
    print(f"Number: {i}")'''
    
    try:
        with LiveTestbed(enable_cache=True) as testbed:
            print("\nFirst execution (will execute in Docker):")
            import time
            start = time.time()
            result1 = testbed.execute_code(code, Language.PYTHON)
            time1 = time.time() - start
            print(f"  Execution time: {time1:.3f}s")
            print(f"  Status: {result1.status.value}")
            
            print("\nSecond execution (will use cache):")
            start = time.time()
            result2 = testbed.execute_code(code, Language.PYTHON)
            time2 = time.time() - start
            print(f"  Execution time: {time2:.3f}s")
            print(f"  Status: {result2.status.value}")
            
            print(f"\n✓ Cache speedup: {time1/time2:.1f}x faster")
            
            # Show cache stats
            stats = testbed.get_cache_stats()
            print(f"\nCache statistics:")
            print(f"  Cached executions: {stats['cached_executions']}")
            print(f"  Languages: {', '.join(stats['languages'])}")
            print(f"  Success rate: {stats['success_rate']:.1f}%")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_validate_documentation():
    """Demonstrate validating all snippets in documentation."""
    print_separator("4. Validating Complete Documentation")
    
    markdown_doc = '''
# API Documentation

## Example 1: Basic Usage

```python
# Simple calculation
result = 2 + 2
print(result)
```

## Example 2: Using Lists

```python
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Total: {total}")
```

## Example 3: Error Example

```python
# This will fail
undefined_variable
```
'''
    
    try:
        with LiveTestbed() as testbed:
            print("\nValidating documentation (auto-execute)...")
            report = testbed.validate_documentation(markdown_doc, auto_execute=True)
            
            print(f"\n✓ Validation Report:")
            print(f"  Total snippets: {report['total_snippets']}")
            print(f"  Executed: {report['executed']}")
            print(f"  Success: {report['success']}")
            print(f"  Failure: {report['failure']}")
            print(f"  Timeout: {report['timeout']}")
            print(f"  Error: {report['error']}")
            
            print(f"\n  Snippet Details:")
            for snippet in report['snippets']:
                status_emoji = '✓' if snippet['status'] == 'success' else '✗'
                print(f"    {status_emoji} Line {snippet['line']}: {snippet['language']} - {snippet['badge']}")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_security_features():
    """Demonstrate security features of the testbed."""
    print_separator("5. Security Features")
    
    print("\n✓ Security measures in place:")
    print("  - Isolated Docker containers for each execution")
    print("  - Network access disabled by default")
    print("  - Memory limits (default: 256MB)")
    print("  - CPU quota limits (default: 50% of one CPU)")
    print("  - Execution timeouts (default: 30 seconds)")
    print("  - Read-only code volume mounts")
    print("  - Containers automatically removed after execution")
    
    print("\nTesting timeout protection:")
    
    # Infinite loop that should timeout
    timeout_code = '''import time
print("Starting long task...")
time.sleep(100)  # This will timeout
print("This won't be printed")'''
    
    try:
        with LiveTestbed(timeout=5) as testbed:
            print("  Executing code with 100s sleep (5s timeout)...")
            result = testbed.execute_code(timeout_code, Language.PYTHON, check_cache=False)
            
            if result.status == ExecutionStatus.TIMEOUT:
                print(f"  ✓ Timeout protection worked! {result.badge}")
            else:
                print(f"  Status: {result.status.value}")
    except Exception as e:
        print(f"  ⚠ Error: {e}")


def main():
    """Run all demos."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║           AccuDoc Live Documentation Testbed Demo                 ║
║                                                                    ║
║  Interactive documentation with validated code snippets           ║
║  executed in secure Docker containers.                            ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    print("Prerequisites:")
    print("  ✓ Docker installed and running")
    print("  ✓ Python docker package installed")
    
    # Check Docker availability
    try:
        import docker
        client = docker.from_env()
        client.ping()
        print("  ✓ Docker daemon accessible\n")
    except Exception as e:
        print(f"\n❌ Docker is not accessible: {e}")
        print("   Please install Docker and ensure it's running.")
        sys.exit(1)
    
    # Run demos
    demo_extract_snippets()
    demo_execute_code()
    demo_caching()
    demo_validate_documentation()
    demo_security_features()
    
    print_separator("Demo Complete")
    print("""
✓ Live testbed features demonstrated successfully!

Next steps:
  1. Enable live testbed in GUI settings
  2. Generate documentation for a repository
  3. Switch to the "Live Example" tab
  4. Select and execute code snippets interactively

For more information, see the AccuDoc documentation.
""")


if __name__ == '__main__':
    main()
