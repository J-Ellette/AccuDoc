# Documentation Archive Feature

## Overview

The AccuDoc Archive feature provides an immutable, cryptographically-signed documentation archival system that ensures the integrity and authenticity of stored documentation over time.

## Features

### Core Capabilities

- **Cryptographic Signatures**: Each archive is signed using HMAC-SHA256 to ensure authenticity and detect tampering
- **Timestamped Snapshots**: Every archive includes an immutable timestamp
- **Content Integrity**: SHA-256 hashing verifies content hasn't been modified
- **Compression**: Gzip compression reduces storage requirements
- **Multi-Format Support**: Archive Markdown, HTML, and PDF documentation
- **Database Storage**: Archives stored directly in AccuDoc's SQLite database
- **Audit Trail**: All archive operations logged for compliance and security review
- **Access Control**: Integration with membership system for role-based permissions

### Security Features

1. **HMAC-SHA256 Signatures**: Each archive is cryptographically signed
2. **Content Hashing**: SHA-256 hash of content for integrity verification
3. **Tampering Detection**: Any modification to archived content is detected
4. **Role-Based Access**: Owner, Admin, Editor, and Viewer roles control access
5. **Permission Checks**: Create (WRITE), Retrieve (READ), Delete (DELETE) permissions
6. **Audit Logging**: Complete trail of all archive operations

### Organization Features

- **Tags**: Categorize archives with multiple tags
- **Descriptions**: Add metadata descriptions to archives
- **Filtering**: Filter by project, format, tags
- **Search**: Find archives by various criteria
- **Statistics**: Track archive usage and storage

## Architecture

### Database Schema

The archive system uses three main tables:

```sql
-- Archives table
CREATE TABLE archives (
    archive_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    document_name TEXT NOT NULL,
    format TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    signature TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    compressed_content BLOB NOT NULL,
    compression TEXT NOT NULL,
    tags TEXT,
    description TEXT,
    metadata TEXT
);

-- Archive access log
CREATE TABLE archive_access_log (
    access_id INTEGER PRIMARY KEY AUTOINCREMENT,
    archive_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    accessed_at TEXT NOT NULL,
    operation TEXT NOT NULL,
    status TEXT NOT NULL
);

-- Signing keys table
CREATE TABLE signing_keys (
    key_id TEXT PRIMARY KEY,
    key_data TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1
);
```

### Components

1. **ArchiveManager** (`accudoc/archive.py`): Core archive management
2. **CLI Commands** (`accudoc_cli.py`): Command-line interface
3. **Dashboard** (`accudoc/archive_dashboard.py`): GUI for browsing archives
4. **Database** (`accudoc/project_database.py`): Storage integration
5. **Audit** (`accudoc/audit.py`): Activity logging
6. **Membership** (`accudoc/membership.py`): Access control

## Usage

### Command-Line Interface

#### Create an Archive

```bash
# Create archive from a document
python accudoc_cli.py archive create /path/to/repo /path/to/document.md \
    --tags "v1.0,documentation,public" \
    --description "Release 1.0 documentation"

# With authentication
python accudoc_cli.py archive create /path/to/repo /path/to/document.md \
    --use-auth --user alice_user_id
```

#### List Archives

```bash
# List all archives
python accudoc_cli.py archive list

# Filter by project
python accudoc_cli.py archive list --repository /path/to/repo

# Filter by format
python accudoc_cli.py archive list --format markdown

# Filter by tags
python accudoc_cli.py archive list --tags "public,v1.0"

# JSON output
python accudoc_cli.py archive list --json
```

#### Retrieve an Archive

```bash
# Retrieve and validate
python accudoc_cli.py archive retrieve arch_abc123 -o document.md

# Skip validation (not recommended)
python accudoc_cli.py archive retrieve arch_abc123 -o document.md --no-validate
```

#### Validate Archive Integrity

```bash
# Verify signature and content hash
python accudoc_cli.py archive validate arch_abc123
```

#### Delete an Archive

```bash
# Delete with confirmation
python accudoc_cli.py archive delete arch_abc123

# Skip confirmation
python accudoc_cli.py archive delete arch_abc123 --yes

# With authentication
python accudoc_cli.py archive delete arch_abc123 --use-auth --user owner_id
```

#### View Statistics

```bash
# Global statistics
python accudoc_cli.py archive stats

# Project-specific statistics
python accudoc_cli.py archive stats --repository /path/to/repo

# JSON output
python accudoc_cli.py archive stats --json
```

### Python API

```python
from pathlib import Path
from accudoc.archive import ArchiveManager, ArchiveFormat
from accudoc.project_database import ProjectDatabase
from accudoc.audit import get_audit_logger
from accudoc.membership import MembershipManager

# Initialize components
db = ProjectDatabase()
audit_logger = get_audit_logger()
membership = MembershipManager()
archive_mgr = ArchiveManager(db, audit_logger, membership)

# Create project
project_id = db.add_project('/path/to/repo', 'My Project')

# Create archive
archive_id = archive_mgr.create_archive(
    project_id=project_id,
    document_path=Path('README.md'),
    format=ArchiveFormat.MARKDOWN,
    created_by='user_id',
    tags=['documentation', 'v1.0'],
    description='Main README'
)
print(f"Created archive: {archive_id}")

# List archives
archives = archive_mgr.list_archives(project_id=project_id)
for archive in archives:
    print(f"- {archive.document_name} ({archive.format})")

# Retrieve and validate
content, metadata = archive_mgr.retrieve_archive(
    archive_id,
    user_id='user_id',
    validate=True
)
print(f"Retrieved: {metadata.document_name}")
print(f"Valid: {archive_mgr.validate_archive(archive_id)}")

# Get statistics
stats = archive_mgr.get_archive_statistics(project_id=project_id)
print(f"Total archives: {stats['total_archives']}")
print(f"Total size: {stats['total_size_bytes']:,} bytes")
print(f"Compressed: {stats['total_compressed_bytes']:,} bytes")

# Delete archive (requires DELETE permission)
archive_mgr.delete_archive(archive_id, user_id='owner_id')

# Clean up
db.close()
```

### GUI Dashboard

Launch the archive dashboard:

```bash
# Standalone dashboard
python -m accudoc.archive_dashboard

# Or from Python
from accudoc.archive_dashboard import ArchiveDashboard
dashboard = ArchiveDashboard()
dashboard.run()
```

**Dashboard Features:**
- Browse archives by project
- Filter by format, tags
- View archive details
- Create new archives
- Retrieve and validate archives
- Delete archives (with permissions)
- View statistics
- Export archive lists to JSON

## Security Best Practices

### Archive Creation

1. **Always use descriptive tags**: Help organize and find archives later
2. **Add meaningful descriptions**: Document what the archive contains
3. **Regular archiving**: Create archives at key milestones (releases, major updates)
4. **Verify permissions**: Ensure proper access controls are set up

### Archive Retrieval

1. **Always validate**: Use signature validation when retrieving (default behavior)
2. **Check audit logs**: Review who accessed what and when
3. **Monitor failed validations**: Investigate any signature validation failures
4. **Secure storage**: Keep retrieved archives in secure locations

### Access Control

Set up proper permissions:

```python
from accudoc.membership import MembershipManager, Role

membership = MembershipManager()

# Create users with appropriate roles
owner = membership.create_user('alice', 'alice@example.com', 'password', Role.OWNER)
editor = membership.create_user('bob', 'bob@example.com', 'password', Role.EDITOR)
viewer = membership.create_user('charlie', 'charlie@example.com', 'password', Role.VIEWER)

# Grant project access
membership.grant_project_access(
    project_id='proj_123',
    granted_by=owner.user_id,
    user_id=viewer.user_id,
    role=Role.VIEWER
)
```

**Permission Levels:**
- **OWNER**: Full access (create, retrieve, validate, delete)
- **ADMIN**: Manage archives (create, retrieve, validate, delete)
- **EDITOR**: Create and retrieve archives
- **VIEWER**: Retrieve and validate archives only

### Audit Trail

Review audit logs regularly:

```python
from accudoc.audit import get_audit_logger

audit_logger = get_audit_logger()

# Get recent archive operations
entries = audit_logger.get_recent_entries(count=100)

# Export audit log
audit_logger.export_to_json(Path('audit_log.json'))
audit_logger.export_to_csv(Path('audit_log.csv'))

# Get statistics
stats = audit_logger.get_statistics()
print(f"Total entries: {stats['total_entries']}")
print(f"By operation: {stats['by_operation']}")
```

## Integration Examples

### With Documentation Generation

```python
from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator
from accudoc.archive import ArchiveManager, ArchiveFormat
from accudoc.project_database import ProjectDatabase

# Scan repository
scanner = RepositoryScanner('/path/to/repo')
repo_info = scanner.scan()

# Generate documentation
generator = DocumentGenerator(repo_info)
doc_path = generator.generate_and_export('README.md')

# Archive the generated documentation
db = ProjectDatabase()
archive_mgr = ArchiveManager(db)
project_id = db.add_project('/path/to/repo', repo_info['name'])

archive_id = archive_mgr.create_archive(
    project_id=project_id,
    document_path=Path(doc_path),
    format=ArchiveFormat.MARKDOWN,
    created_by='automation',
    tags=['auto-generated', 'latest'],
    description=f"Auto-generated from commit {repo_info.get('latest_commit', 'unknown')}"
)

print(f"Documentation archived: {archive_id}")
```

### With CI/CD

```yaml
# .github/workflows/archive-docs.yml
name: Archive Documentation

on:
  push:
    tags:
      - 'v*'

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install AccuDoc
        run: pip install .
      
      - name: Generate and Archive Documentation
        run: |
          python accudoc_cli.py export . -o docs.md
          python accudoc_cli.py archive create . docs.md \
            --tags "release,${{ github.ref_name }},production" \
            --description "Release ${{ github.ref_name }} documentation" \
            --user ci-bot
```

## Troubleshooting

### Archive Validation Fails

**Problem**: `validate_archive()` returns False

**Possible Causes**:
1. Archive content has been tampered with
2. Signing key has changed
3. Database corruption

**Solution**:
```python
# Check content hash
archive = archive_mgr.list_archives()[0]  # Get archive
print(f"Stored hash: {archive.content_hash}")

# Retrieve and inspect
content, metadata = archive_mgr.retrieve_archive(archive_id, user_id, validate=False)
actual_hash = hashlib.sha256(content).hexdigest()
print(f"Actual hash: {actual_hash}")

# If hashes don't match, content was tampered with
```

### Permission Errors

**Problem**: `PermissionError` when creating/deleting archives

**Solution**:
```python
# Check user permissions
from accudoc.membership import Permission

can_write = membership.check_permission(user_id, project_id, Permission.WRITE)
can_delete = membership.check_permission(user_id, project_id, Permission.DELETE)

print(f"Can write: {can_write}")
print(f"Can delete: {can_delete}")

# Grant permissions if needed
membership.grant_project_access(
    project_id=project_id,
    granted_by=owner_id,
    user_id=user_id,
    role=Role.EDITOR  # or Role.ADMIN for delete access
)
```

### Large Archives

**Problem**: Archives are too large

**Solution**:
```python
# Check compression effectiveness
stats = archive_mgr.get_archive_statistics()
compression_ratio = stats['compression_ratio']
print(f"Compression ratio: {compression_ratio:.2%}")

# If compression ratio > 80%, content is already compressed
# Consider storing large files externally and archiving references

# For very large files, use streaming:
import gzip
with gzip.open('large_archive.gz', 'wb') as f:
    # Write in chunks
    pass
```

## Performance Considerations

### Compression

- Gzip compression reduces storage by 60-90% for text documents
- Already-compressed formats (PDF) see minimal benefit
- Compression/decompression adds minimal overhead (<10ms for typical documents)

### Database Size

- Each archive stores:
  - Metadata: ~500 bytes
  - Compressed content: Varies
  - Indexes: ~100 bytes per archive

### Best Practices

1. **Batch operations**: Archive multiple documents in a single transaction when possible
2. **Index management**: Ensure database indexes are optimized
3. **Periodic cleanup**: Delete old/unused archives
4. **Archive rotation**: Implement retention policies

```python
# Example: Delete archives older than 1 year
from datetime import datetime, timedelta

archives = archive_mgr.list_archives(project_id=project_id, limit=10000)
cutoff_date = datetime.now() - timedelta(days=365)

for archive in archives:
    created_at = datetime.fromisoformat(archive.created_at)
    if created_at < cutoff_date and 'keep' not in archive.tags:
        archive_mgr.delete_archive(archive.archive_id, admin_user_id)
        print(f"Deleted old archive: {archive.archive_id}")
```

## References

- **Module**: `accudoc/archive.py`
- **Tests**: `test_archive.py`
- **Demo**: `demo_archive.py`
- **CLI**: `python accudoc_cli.py archive --help`
- **Dashboard**: `python -m accudoc.archive_dashboard`
- **Issue**: Immutable Documentation Archive (#issue_number)
