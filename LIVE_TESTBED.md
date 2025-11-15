# Live Documentation Testbed

AccuDoc's Live Documentation Testbed enables interactive documentation by allowing users to execute code snippets in secure Docker containers. This feature provides validated outputs and trust badges to enhance documentation trustworthiness.

## Features

### 🔒 Security First

- **Isolated Execution**: Each code snippet runs in a separate Docker container
- **Network Isolation**: Network access disabled by default to prevent malicious code
- **Resource Limits**: Memory and CPU quotas prevent resource exhaustion
- **Timeout Protection**: Configurable execution timeouts prevent infinite loops
- **Read-Only Mounts**: Code is mounted read-only in containers
- **Auto-Cleanup**: Containers automatically removed after execution

### 🌐 Multi-Language Support

Supports execution of code snippets in multiple programming languages:

- **Python** (python:3.11-slim)
- **JavaScript/Node.js** (node:18-slim)
- **Java** (openjdk:11-slim)
- **Go** (golang:1.20-alpine)
- **Ruby** (ruby:3.1-slim)
- **Rust** (rust:1.70-slim)

### 📊 Validated Documentation

- **Trust Badges**: Visual indicators of code execution status
  - ✓ Validated - Code executes successfully
  - ✗ Failed - Code has errors
  - ⏱ Timeout - Execution exceeded time limit
  - ⚠ Error - System error during execution
- **Output Capture**: Real-time capture of stdout and stderr
- **Execution Metrics**: Timing information for performance analysis

### 🔐 Access Control

- **Membership Integration**: Role-based access control via AccuDoc's membership system
- **Authentication Required**: Optional user authentication for execution
- **Permission Management**: Fine-grained control over who can execute code

## Installation

### Prerequisites

1. **Docker**: Install Docker Desktop or Docker Engine
   - macOS: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - Linux: [Docker Engine](https://docs.docker.com/engine/install/)

2. **Python Docker Library**: Install the Python Docker SDK
   ```bash
   pip install docker
   ```

   Or install AccuDoc with testbed support:
   ```bash
   pip install .[testbed]  # From source
   ```

### Verify Installation

Check that Docker is running:
```bash
docker ps
```

## Configuration

### GUI Settings

1. Open AccuDoc GUI
2. Click **Settings** (⚙️ button)
3. Navigate to the **Live Testbed** tab
4. Configure options:

| Setting | Default | Description |
|---------|---------|-------------|
| Enable Live Testbed | False | Turn on/off the testbed feature |
| Execution Timeout | 30s | Maximum time for code execution |
| Memory Limit | 256m | Maximum memory per container |
| Network Disabled | True | Disable network access in containers |
| Require Authentication | True | Require user login for execution |
| Enable Cache | True | Cache execution results for performance |

### Programmatic Configuration

```python
from accudoc.settings import AccuDocSettings

settings = AccuDocSettings(
    enable_live_testbed=True,
    testbed_timeout=30,
    testbed_memory_limit='256m',
    testbed_network_disabled=True,
    testbed_require_auth=True,
    testbed_enable_cache=True
)
```

## Usage

### GUI Usage

1. **Generate Documentation**
   - Open a repository in AccuDoc
   - Click "Scan Repository" and "Generate Documentation"

2. **Access Live Example Tab**
   - Navigate to the "Live Example" tab in the preview area
   - Click "↻ Refresh Snippets" to extract code from documentation

3. **Execute Code**
   - Select a code snippet from the dropdown
   - Review or edit the code in the editor
   - Click "▶ Execute Code" to run in Docker container
   - View output and execution status

4. **Review Results**
   - Check the status indicator (Success/Failed/Timeout/Error)
   - See the trust badge
   - Read the output or error messages
   - Note the execution time

### Programmatic Usage

```python
from accudoc.live_testbed import LiveTestbed, Language

# Create testbed instance
with LiveTestbed(timeout=30) as testbed:
    # Execute Python code
    result = testbed.execute_code(
        'print("Hello, World!")',
        Language.PYTHON
    )
    
    print(f"Status: {result.status.value}")
    print(f"Output: {result.output}")
    print(f"Badge: {result.badge}")
    print(f"Time: {result.execution_time:.2f}s")
```

#### Extract and Execute from Documentation

```python
from accudoc.live_testbed import LiveTestbed

markdown_doc = '''
# Example

```python
print("Hello from docs!")
```
'''

with LiveTestbed() as testbed:
    # Extract snippets
    snippets = testbed.extract_code_snippets(markdown_doc)
    
    # Execute each snippet
    for snippet in snippets:
        result = testbed.execute_code(snippet.code, snippet.language)
        print(f"{snippet.language.value}: {result.status.value}")
```

#### Validate Complete Documentation

```python
from accudoc.live_testbed import LiveTestbed

with LiveTestbed() as testbed:
    report = testbed.validate_documentation(
        markdown_content,
        auto_execute=True
    )
    
    print(f"Total snippets: {report['total_snippets']}")
    print(f"Success: {report['success']}")
    print(f"Failure: {report['failure']}")
```

## Security Considerations

### Container Isolation

Each code execution runs in a fresh Docker container that is:
- Isolated from the host system
- Limited in resources (memory, CPU)
- Restricted from network access (by default)
- Automatically removed after execution

### Resource Limits

Default limits prevent resource exhaustion:
- **Memory**: 256MB per container
- **CPU**: 50% of one CPU core (50,000 microseconds)
- **Timeout**: 30 seconds execution limit
- **Disk**: No persistent storage

### Network Isolation

Network access is disabled by default to prevent:
- Downloading malicious code
- Exfiltrating data
- Connecting to external services
- DDoS attacks

### User Authentication

When `testbed_require_auth` is enabled:
- Users must authenticate before executing code
- Execution permissions tied to user roles
- Audit trail of all executions
- Rate limiting by user/role

## Performance

### Caching

Execution results are cached by code hash:
- Identical code snippets return cached results
- No Docker execution needed for cached results
- Typically 10-100x faster for cached executions
- Cache can be disabled if needed

### Docker Image Caching

Docker images are pulled once and reused:
- First execution downloads the image (~100MB per language)
- Subsequent executions are much faster
- Images stored in Docker's local cache

### Optimization Tips

1. **Enable caching** for repeated executions
2. **Pre-pull images** before bulk validation
   ```bash
   docker pull python:3.11-slim
   docker pull node:18-slim
   docker pull openjdk:11-slim
   ```
3. **Adjust timeouts** based on expected execution time
4. **Batch validate** during CI/CD, not on every edit

## Troubleshooting

### Docker Not Available

**Error**: "Failed to connect to Docker"

**Solution**:
1. Ensure Docker is installed and running
2. Check Docker daemon: `docker ps`
3. Verify Docker socket: `ls -la /var/run/docker.sock`
4. On Windows/Mac: Start Docker Desktop

### Permission Denied

**Error**: "Permission denied while connecting to Docker daemon"

**Solution** (Linux):
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Image Pull Failures

**Error**: "Failed to pull Docker image"

**Solution**:
1. Check internet connectivity
2. Verify Docker Hub access
3. Try manual pull: `docker pull python:3.11-slim`
4. Configure proxy if behind firewall

### Timeout Issues

**Error**: Code execution timing out

**Solution**:
1. Increase timeout in settings
2. Optimize code for faster execution
3. Check for infinite loops
4. Consider code complexity

## Examples

See `demo_live_testbed.py` for comprehensive examples demonstrating:
- Extracting code snippets from markdown
- Executing code in multiple languages
- Handling execution errors
- Caching mechanism
- Validating complete documentation
- Security features

Run the demo:
```bash
python demo_live_testbed.py
```

## API Reference

### LiveTestbed Class

```python
class LiveTestbed:
    def __init__(
        self,
        timeout: int = 30,
        memory_limit: str = "256m",
        cpu_quota: int = 50000,
        network_disabled: bool = True,
        enable_cache: bool = True
    )
```

#### Methods

- `extract_code_snippets(markdown_content: str) -> List[CodeSnippet]`
  - Extract code snippets from markdown documentation

- `execute_code(code: str, language: Language, check_cache: bool = True) -> ExecutionResult`
  - Execute code in Docker container

- `validate_documentation(markdown_content: str, auto_execute: bool = False) -> Dict`
  - Validate all snippets in documentation

- `clear_cache() -> None`
  - Clear execution result cache

- `get_cache_stats() -> Dict`
  - Get cache statistics

### Data Classes

#### CodeSnippet
```python
@dataclass
class CodeSnippet:
    code: str
    language: Language
    line_number: int
    title: Optional[str] = None
```

#### ExecutionResult
```python
@dataclass
class ExecutionResult:
    status: ExecutionStatus
    output: str
    error: str
    execution_time: float
    timestamp: str
    badge: str
    language: Language
    code_hash: str
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Validate Documentation

on: [push, pull_request]

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install .[testbed]
      
      - name: Validate documentation snippets
        run: |
          python -c "
          from accudoc.live_testbed import LiveTestbed
          from pathlib import Path
          
          docs = Path('docs/README.md').read_text()
          
          with LiveTestbed() as testbed:
              report = testbed.validate_documentation(docs, auto_execute=True)
              
              if report['failure'] > 0 or report['error'] > 0:
                  print(f'❌ Validation failed: {report}')
                  exit(1)
              else:
                  print(f'✓ All {report[\"success\"]} snippets validated')
          "
```

## Future Enhancements

Planned features for future releases:

- [ ] Support for more languages (PHP, C++, C#, etc.)
- [ ] Interactive REPL mode for iterative development
- [ ] Code snippet auto-fix suggestions
- [ ] Visual execution timeline/debugger
- [ ] Collaborative execution (share results)
- [ ] Custom Docker images per project
- [ ] Execution history and analytics
- [ ] Browser-based execution (WebAssembly)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This feature is part of AccuDoc and is licensed under the GNU General Public License v3.0.

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/jamesellette/AccuDoc/issues
- Documentation: https://github.com/jamesellette/AccuDoc

---

*Live Documentation Testbed - Making documentation interactive and trustworthy*
