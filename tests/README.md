# AccuDoc Test Suite

This directory contains the core test suite for AccuDoc modules.

## Running Tests

### Run all tests:
```bash
python -m pytest tests/
```

### Run a specific test file:
```bash
python tests/test_accudoc.py
```

### Run tests with coverage:
```bash
python -m pytest tests/ --cov=accudoc --cov-report=html
```

## Test Files

Each test file corresponds to a module in the `accudoc/` package:

- `test_accudoc.py` - Core integration tests
- `test_archive.py` - Archive functionality
- `test_collaboration.py` - Collaboration features
- `test_dataflow.py` - Data flow analysis
- `test_health_dashboard.py` - Health dashboard
- `test_hooks_system.py` - Git hooks system
- `test_search.py` - Smart search functionality
- `test_rest_api.py` - REST API endpoints
- And more...

## Test Structure

All tests follow this pattern:
- Import from parent directory: `sys.path.insert(0, str(Path(__file__).parent.parent))`
- Import accudoc modules: `from accudoc.module import Class`
- Run test functions or classes

## Adding New Tests

When adding a new module to `accudoc/`, create a corresponding test file:

1. Create `tests/test_your_module.py`
2. Add the standard imports:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   from accudoc.your_module import YourClass
   ```
3. Write test functions or classes
4. Run the test to verify
