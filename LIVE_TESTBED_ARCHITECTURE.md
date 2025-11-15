# Live Testbed Architecture and Implementation Summary

## Overview

The Live Documentation Testbed feature enables interactive documentation by executing code snippets in secure Docker containers. This document provides an architectural overview and implementation details.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AccuDoc GUI                                 │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Documentation Preview Tabs                                    │ │
│  │                                                               │ │
│  │  [Markdown] [HTML] [Preview] [Live Example] ⬅ NEW!          │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Live Example Tab                                              │ │
│  │                                                               │ │
│  │  ┌────────────────────┐  ┌────────────────────┐              │ │
│  │  │ Code Snippet       │  │ Output Display     │              │ │
│  │  │ Selector           │  │                    │              │ │
│  │  ├────────────────────┤  │ Status: ✓ Success  │              │ │
│  │  │                    │  │ Badge: [Validated] │              │ │
│  │  │ Code Editor        │  │                    │              │ │
│  │  │                    │  │ Output:            │              │ │
│  │  │ print("Hello")     │  │ Hello, World!      │              │ │
│  │  │                    │  │                    │              │ │
│  │  └────────────────────┘  │ Time: 1.2s         │              │ │
│  │  [▶ Execute] [Clear]     └────────────────────┘              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Settings Dialog                                               │ │
│  │                                                               │ │
│  │  [General] [Live Testbed] ⬅ NEW! [About]                    │ │
│  │                                                               │ │
│  │  ☑ Enable Live Testbed                                       │ │
│  │  Timeout: [30] seconds                                       │ │
│  │  Memory Limit: [256m]                                        │ │
│  │  ☑ Disable network access                                    │ │
│  │  ☑ Require authentication                                    │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     LiveTestbed Module                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ extract_code_snippets(markdown)                              │  │
│  │   • Parse markdown with regex                                │  │
│  │   • Detect language from fence markers                       │  │
│  │   • Return list of CodeSnippet objects                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                     │
│                               ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ execute_code(code, language)                                 │  │
│  │   1. Check execution cache (optional)                        │  │
│  │   2. Create temporary directory                              │  │
│  │   3. Write code to file                                      │  │
│  │   4. Ensure Docker image available                           │  │
│  │   5. Run container with security limits                      │  │
│  │   6. Capture output/errors                                   │  │
│  │   7. Generate badge                                          │  │
│  │   8. Cache result                                            │  │
│  │   9. Return ExecutionResult                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Docker Engine                                  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Container 1  │  │ Container 2  │  │ Container 3  │             │
│  │              │  │              │  │              │             │
│  │ python:3.11  │  │ node:18      │  │ openjdk:11   │             │
│  │              │  │              │  │              │             │
│  │ Limits:      │  │ Limits:      │  │ Limits:      │             │
│  │ • 256MB RAM  │  │ • 256MB RAM  │  │ • 256MB RAM  │             │
│  │ • 50% CPU    │  │ • 50% CPU    │  │ • 50% CPU    │             │
│  │ • 30s timeout│  │ • 30s timeout│  │ • 30s timeout│             │
│  │ • No network │  │ • No network │  │ • No network │             │
│  │ • Read-only  │  │ • Read-only  │  │ • Read-only  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. GUI Components (accudoc/gui.py)

#### New "Live Example" Tab
- **Location**: Added to `output_notebook` after "Preview" tab
- **Components**:
  - Code snippet selector (dropdown)
  - Refresh button to extract snippets from documentation
  - Split pane with code editor and output display
  - Execute and clear buttons
  - Status indicator with color coding
  - Badge display

#### Live Testbed Settings Tab
- **Location**: New tab in settings dialog
- **Controls**:
  - Enable/disable checkbox
  - Timeout spinbox (5-300 seconds)
  - Memory limit entry
  - Network disabled checkbox
  - Require authentication checkbox
  - Cache enable checkbox

### 2. Core Module (accudoc/live_testbed.py)

#### Classes

**LiveTestbed**
- Manages Docker client connection
- Configures security limits
- Executes code in containers
- Handles caching

**CodeSnippet (dataclass)**
```python
@dataclass
class CodeSnippet:
    code: str
    language: Language
    line_number: int
    title: Optional[str] = None
```

**ExecutionResult (dataclass)**
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

#### Enums

**Language**
- PYTHON, JAVASCRIPT, JAVA, GO, RUBY, RUST

**ExecutionStatus**
- SUCCESS, FAILURE, TIMEOUT, ERROR, DENIED

### 3. Settings Module (accudoc/settings.py)

#### New Fields in AccuDocSettings
```python
# Live Testbed settings
enable_live_testbed: bool = False
testbed_timeout: int = 30
testbed_memory_limit: str = '256m'
testbed_cpu_quota: int = 50000
testbed_network_disabled: bool = True
testbed_enable_cache: bool = True
testbed_require_auth: bool = True
testbed_allowed_languages: List[str] = None
```

### 4. Membership Integration

The testbed integrates with AccuDoc's membership system for access control:

```python
# In GUI initialization
if self.settings.testbed_require_auth:
    self.membership_manager = MembershipManager()

# Before execution
if self.settings.testbed_require_auth and self.membership_manager:
    # Check user permissions
    # Verify user has WRITE permission
```

## Security Features

### Container Isolation
1. **Separate Containers**: Each execution gets a fresh container
2. **Auto-Cleanup**: Containers removed after execution
3. **Resource Limits**:
   - Memory: 256MB default (configurable)
   - CPU: 50% of one core (configurable)
   - Timeout: 30 seconds (configurable)

### Network Security
- Network access disabled by default
- Prevents data exfiltration
- Blocks malicious downloads
- Can be enabled if needed for specific use cases

### Code Security
- Read-only code mounts
- Temporary directories auto-cleaned
- No persistent storage
- Isolated from host system

### Access Control
- Optional user authentication
- Role-based permissions via membership system
- Audit trail of executions (when enabled)

## Data Flow

### Code Execution Flow

```
1. User clicks "Refresh Snippets"
   ↓
2. Extract code from markdown preview
   ↓
3. Parse and detect languages
   ↓
4. Populate dropdown with snippets
   ↓
5. User selects snippet
   ↓
6. Code displayed in editor
   ↓
7. User clicks "Execute Code"
   ↓
8. [If auth required] Check user permissions
   ↓
9. [If cached] Return cached result → Skip to 17
   ↓
10. Create temporary directory
    ↓
11. Write code to file
    ↓
12. Pull Docker image (if needed)
    ↓
13. Run container with security limits
    ↓
14. Wait for completion (with timeout)
    ↓
15. Capture output/errors
    ↓
16. Generate badge based on status
    ↓
17. Cache result (if enabled)
    ↓
18. Display result in UI
    ↓
19. Update status indicator
```

## File Structure

```
AccuDoc/
├── accudoc/
│   ├── live_testbed.py          ⬅ NEW: Core testbed module
│   ├── gui.py                   ⬅ MODIFIED: Added Live Example tab
│   ├── settings.py              ⬅ MODIFIED: Added testbed settings
│   └── membership.py            ⬅ EXISTING: Used for access control
├── test_live_testbed.py         ⬅ NEW: Unit tests
├── test_live_testbed_integration.py ⬅ NEW: Integration tests
├── demo_live_testbed.py         ⬅ NEW: Demo script
├── LIVE_TESTBED.md              ⬅ NEW: Feature documentation
├── README.md                    ⬅ MODIFIED: Added feature mention
├── requirements.txt             ⬅ MODIFIED: Added docker dependency
└── setup.py                     ⬅ MODIFIED: Added testbed extras
```

## Language Support Configuration

```python
LANGUAGE_CONFIG = {
    Language.PYTHON: {
        "image": "python:3.11-slim",
        "extension": ".py",
        "run_command": ["python", "/code/script.py"]
    },
    Language.JAVASCRIPT: {
        "image": "node:18-slim",
        "extension": ".js",
        "run_command": ["node", "/code/script.js"]
    },
    # ... more languages
}
```

## Usage Examples

### Programmatic Usage

```python
from accudoc.live_testbed import LiveTestbed, Language

# Create testbed
with LiveTestbed(timeout=30) as testbed:
    # Execute code
    result = testbed.execute_code(
        'print("Hello, World!")',
        Language.PYTHON
    )
    
    print(f"Status: {result.status.value}")
    print(f"Output: {result.output}")
```

### GUI Usage

1. Generate documentation
2. Switch to "Live Example" tab
3. Click "Refresh Snippets"
4. Select a snippet
5. Click "Execute Code"
6. View results

## Performance Considerations

### Caching Strategy
- **Key**: SHA256 hash of code (first 16 chars)
- **Storage**: In-memory dictionary
- **Invalidation**: Never (cleared only on restart or manual clear)
- **Benefits**: 10-100x faster for repeated executions

### Docker Image Caching
- Images pulled once and reused
- Stored in Docker's local cache
- First pull: ~100MB download
- Subsequent uses: Instant

## Error Handling

### Graceful Degradation
1. **No Docker**: Feature disabled, GUI shows message
2. **No docker package**: Module import fails, GUI handles gracefully
3. **Docker not running**: Clear error message to user
4. **Image pull fails**: Retry logic and error reporting
5. **Execution timeout**: Container stopped, timeout status returned

## Testing Strategy

### Unit Tests (test_live_testbed.py)
- Code snippet extraction
- Language detection
- Badge generation
- Execution flow (mocked)
- Cache operations

### Integration Tests (test_live_testbed_integration.py)
- Settings integration
- GUI module compatibility
- Feature documentation existence
- End-to-end workflow

## Future Enhancements

1. **More Languages**: C++, C#, PHP, Kotlin, Swift
2. **Interactive REPL**: Multi-statement execution with state
3. **Debugging Support**: Step-through execution, breakpoints
4. **Collaborative Execution**: Share results with team
5. **Custom Images**: Allow users to specify Docker images
6. **Execution History**: Track and replay past executions
7. **Auto-Fix Suggestions**: AI-powered error fixes
8. **Browser Execution**: WebAssembly for client-side execution

## Dependencies

### Required
- Python 3.7+
- Docker (engine/desktop)

### Optional
- `docker` Python package (pip install docker)
- `tkinter` (for GUI)

### Docker Images (pulled on demand)
- python:3.11-slim (~45MB)
- node:18-slim (~70MB)
- openjdk:11-slim (~200MB)
- golang:1.20-alpine (~150MB)
- ruby:3.1-slim (~50MB)
- rust:1.70-slim (~350MB)

## Security Checklist

- [x] Container isolation
- [x] Resource limits (memory, CPU)
- [x] Execution timeouts
- [x] Network isolation
- [x] Read-only code mounts
- [x] Auto container cleanup
- [x] User authentication (optional)
- [x] Role-based permissions
- [x] No persistent storage
- [x] Input validation
- [x] Error sanitization
- [x] Audit trail support

## Conclusion

The Live Documentation Testbed feature provides a secure, flexible, and user-friendly way to create interactive documentation. By leveraging Docker's isolation capabilities and implementing comprehensive security measures, it enables users to validate code snippets while maintaining system security.

The feature is designed to be:
- **Secure**: Multiple layers of isolation and resource limits
- **Flexible**: Configurable settings for different use cases
- **User-Friendly**: Intuitive GUI with clear status indicators
- **Performant**: Caching and optimization for fast repeated executions
- **Extensible**: Easy to add new languages and features
- **Robust**: Comprehensive error handling and graceful degradation

---

*Implementation completed for AccuDoc v1.0*
