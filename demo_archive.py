#!/usr/bin/env python3
"""
Demo script for AccuDoc Archive feature.

Demonstrates creating, listing, validating, and retrieving
immutable documentation archives with cryptographic signatures.
"""

import sys
import tempfile
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.archive import ArchiveManager, ArchiveFormat
from accudoc.project_database import ProjectDatabase
from accudoc.audit import get_audit_logger
from accudoc.membership import MembershipManager, Role


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_basic_archive():
    """Demo basic archive creation and retrieval."""
    print_header("Demo 1: Basic Archive Creation and Retrieval")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Setup
        db = ProjectDatabase(tmpdir / 'accudoc.db')
        audit_log = get_audit_logger(tmpdir / 'audit.log')
        archive_mgr = ArchiveManager(db, audit_log)
        
        # Create sample documents
        md_doc = tmpdir / 'README.md'
        md_doc.write_text("""# Project Documentation

## Overview
This is comprehensive project documentation for the AccuDoc system.

## Features
- Automated scanning
- Documentation generation
- Multiple export formats
- **Archive support with cryptographic signatures**

## Installation
```bash
pip install accudoc
```

## Usage
```python
from accudoc.scanner import RepositoryScanner
scanner = RepositoryScanner('/path/to/repo')
repo_info = scanner.scan()
```
""")
        
        html_doc = tmpdir / 'api-docs.html'
        html_doc.write_text("""<!DOCTYPE html>
<html>
<head>
    <title>API Documentation</title>
</head>
<body>
    <h1>API Reference</h1>
    <h2>ArchiveManager</h2>
    <p>Manages immutable documentation archives with cryptographic signatures.</p>
    
    <h3>Methods</h3>
    <ul>
        <li><code>create_archive()</code> - Create a signed archive</li>
        <li><code>retrieve_archive()</code> - Retrieve and validate archive</li>
        <li><code>validate_archive()</code> - Verify archive integrity</li>
    </ul>
</body>
</html>
""")
        
        # Create project
        project_id = db.add_project('/demo/project', 'Demo Project')
        print(f"✓ Created project: {project_id}\n")
        
        # Create archives
        print("Creating archives...")
        
        md_archive_id = archive_mgr.create_archive(
            project_id=project_id,
            document_path=md_doc,
            format=ArchiveFormat.MARKDOWN,
            created_by='demo_user',
            tags=['documentation', 'readme', 'v1.0'],
            description='Main project README documentation'
        )
        print(f"  ✓ Markdown archive: {md_archive_id}")
        time.sleep(0.1)  # Small delay for different timestamps
        
        html_archive_id = archive_mgr.create_archive(
            project_id=project_id,
            document_path=html_doc,
            format=ArchiveFormat.HTML,
            created_by='demo_user',
            tags=['api', 'reference', 'v1.0'],
            description='API reference documentation'
        )
        print(f"  ✓ HTML archive: {html_archive_id}\n")
        
        # List archives
        print("Listing all archives:")
        archives = archive_mgr.list_archives(project_id=project_id)
        for i, archive in enumerate(archives, 1):
            print(f"\n{i}. {archive.document_name}")
            print(f"   Archive ID: {archive.archive_id}")
            print(f"   Format: {archive.format}")
            print(f"   Size: {archive.size_bytes:,} bytes")
            print(f"   Tags: {', '.join(archive.tags)}")
            print(f"   Created: {archive.created_at}")
        
        # Validate archives
        print("\n\nValidating archives:")
        for archive_id in [md_archive_id, html_archive_id]:
            is_valid = archive_mgr.validate_archive(archive_id)
            status = "✓ VALID" if is_valid else "✗ INVALID"
            print(f"  {archive_id[:20]}... - {status}")
        
        # Retrieve archive
        print("\n\nRetrieving archive:")
        content, metadata = archive_mgr.retrieve_archive(md_archive_id, 'demo_user')
        print(f"  ✓ Retrieved: {metadata.document_name}")
        print(f"  ✓ Size: {metadata.size_bytes:,} bytes")
        print(f"  ✓ Format: {metadata.format}")
        print(f"  ✓ Signature validated")
        print(f"\n  First 100 characters of content:")
        print(f"  {content.decode()[:100]}...")
        
        db.close()
    
    print("\n✓ Demo 1 complete!\n")


def demo_filtering():
    """Demo filtering archives by format and tags."""
    print_header("Demo 2: Filtering Archives")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Setup
        db = ProjectDatabase(tmpdir / 'accudoc.db')
        archive_mgr = ArchiveManager(db)
        
        # Create project
        project_id = db.add_project('/demo/project', 'Demo Project')
        
        # Create multiple archives with different tags
        print("Creating archives with various tags...")
        
        archives_data = [
            ('doc1.md', ['user-guide', 'v1.0', 'public'], 'User guide'),
            ('doc2.md', ['api', 'v1.0', 'public'], 'API docs'),
            ('doc3.md', ['internal', 'v1.0', 'private'], 'Internal notes'),
            ('doc4.html', ['tutorial', 'v1.0', 'public'], 'Tutorial'),
            ('doc5.html', ['api', 'v1.1', 'public'], 'API v1.1'),
        ]
        
        for filename, tags, desc in archives_data:
            doc_path = tmpdir / filename
            doc_path.write_text(f"# {desc}\n\nContent for {filename}")
            
            format = ArchiveFormat.MARKDOWN if filename.endswith('.md') else ArchiveFormat.HTML
            archive_mgr.create_archive(
                project_id=project_id,
                document_path=doc_path,
                format=format,
                created_by='demo_user',
                tags=tags,
                description=desc
            )
            print(f"  ✓ Created: {filename} - Tags: {', '.join(tags)}")
            time.sleep(0.01)
        
        # Filter by format
        print("\n\nFiltering by format (Markdown):")
        md_archives = archive_mgr.list_archives(
            project_id=project_id,
            format=ArchiveFormat.MARKDOWN
        )
        for archive in md_archives:
            print(f"  • {archive.document_name} - {', '.join(archive.tags)}")
        
        # Filter by tags
        print("\n\nFiltering by tags (api):")
        api_archives = archive_mgr.list_archives(
            project_id=project_id,
            tags=['api']
        )
        for archive in api_archives:
            print(f"  • {archive.document_name} - {archive.format} - {', '.join(archive.tags)}")
        
        # Filter by multiple criteria
        print("\n\nFiltering by tags (public + v1.0):")
        public_v1_archives = archive_mgr.list_archives(
            project_id=project_id,
            tags=['public', 'v1.0']
        )
        for archive in public_v1_archives:
            print(f"  • {archive.document_name} - {', '.join(archive.tags)}")
        
        db.close()
    
    print("\n✓ Demo 2 complete!\n")


def demo_security():
    """Demo security features with membership integration."""
    print_header("Demo 3: Security and Access Control")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Setup
        db = ProjectDatabase(tmpdir / 'accudoc.db')
        membership = MembershipManager(tmpdir / 'membership.db')
        audit_log = get_audit_logger(tmpdir / 'audit.log')
        archive_mgr = ArchiveManager(db, audit_log, membership)
        
        # Create users
        print("Creating users with different roles:")
        owner = membership.create_user('alice', 'alice@example.com', 'password', Role.OWNER)
        editor = membership.create_user('bob', 'bob@example.com', 'password', Role.EDITOR)
        viewer = membership.create_user('charlie', 'charlie@example.com', 'password', Role.VIEWER)
        
        print(f"  ✓ Alice (Owner): {owner.user_id}")
        print(f"  ✓ Bob (Editor): {editor.user_id}")
        print(f"  ✓ Charlie (Viewer): {viewer.user_id}")
        
        # Create project and grant access
        print("\n\nSetting up project access:")
        project_id = db.add_project('/secure/project', 'Secure Project')
        
        membership.grant_project_access(
            project_id=project_id,
            granted_by=owner.user_id,
            user_id=owner.user_id,
            role=Role.OWNER
        )
        membership.grant_project_access(
            project_id=project_id,
            granted_by=owner.user_id,
            user_id=editor.user_id,
            role=Role.EDITOR
        )
        membership.grant_project_access(
            project_id=project_id,
            granted_by=owner.user_id,
            user_id=viewer.user_id,
            role=Role.VIEWER
        )
        print("  ✓ Granted access to all users")
        
        # Create archive as owner
        doc_path = tmpdir / 'secure-doc.md'
        doc_path.write_text("# Confidential Documentation\n\nThis is secure content.")
        
        print("\n\nOwner creating archive:")
        archive_id = archive_mgr.create_archive(
            project_id=project_id,
            document_path=doc_path,
            format=ArchiveFormat.MARKDOWN,
            created_by=owner.user_id,
            tags=['confidential'],
            description='Secure documentation'
        )
        print(f"  ✓ Archive created: {archive_id}")
        
        # Editor tries to create (should succeed - has WRITE permission)
        print("\n\nEditor creating archive:")
        doc_path2 = tmpdir / 'editor-doc.md'
        doc_path2.write_text("# Editor's Document")
        try:
            archive_id2 = archive_mgr.create_archive(
                project_id=project_id,
                document_path=doc_path2,
                format=ArchiveFormat.MARKDOWN,
                created_by=editor.user_id,
                tags=['draft']
            )
            print(f"  ✓ Editor successfully created archive: {archive_id2}")
        except PermissionError as e:
            print(f"  ✗ Permission denied: {e}")
        
        # Viewer tries to create (should fail - no WRITE permission)
        print("\n\nViewer attempting to create archive:")
        try:
            archive_mgr.create_archive(
                project_id=project_id,
                document_path=doc_path,
                format=ArchiveFormat.MARKDOWN,
                created_by=viewer.user_id
            )
            print("  ✗ Viewer should NOT have been able to create archive!")
        except PermissionError:
            print("  ✓ Viewer correctly denied (no WRITE permission)")
        
        # Viewer retrieves archive (should succeed - has READ permission)
        print("\n\nViewer retrieving archive:")
        try:
            content, metadata = archive_mgr.retrieve_archive(archive_id, viewer.user_id)
            print(f"  ✓ Viewer successfully retrieved: {metadata.document_name}")
        except PermissionError as e:
            print(f"  ✗ Permission denied: {e}")
        
        # Viewer tries to delete (should fail - no DELETE permission)
        print("\n\nViewer attempting to delete archive:")
        try:
            archive_mgr.delete_archive(archive_id, viewer.user_id)
            print("  ✗ Viewer should NOT have been able to delete archive!")
        except PermissionError:
            print("  ✓ Viewer correctly denied (no DELETE permission)")
        
        # Owner deletes archive (should succeed)
        print("\n\nOwner deleting archive:")
        try:
            archive_mgr.delete_archive(archive_id, owner.user_id)
            print("  ✓ Owner successfully deleted archive")
        except PermissionError as e:
            print(f"  ✗ Permission denied: {e}")
        
        # Check audit log
        print("\n\nAudit trail (recent entries):")
        audit_entries = audit_log.get_recent_entries(count=5)
        for entry in audit_entries[-3:]:  # Show last 3
            if 'archive' in entry.lower():
                print(f"  {entry.strip()}")
        
        membership.close()
        db.close()
    
    print("\n✓ Demo 3 complete!\n")


def demo_statistics():
    """Demo archive statistics."""
    print_header("Demo 4: Archive Statistics")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Setup
        db = ProjectDatabase(tmpdir / 'accudoc.db')
        archive_mgr = ArchiveManager(db)
        
        # Create projects
        proj1 = db.add_project('/project1', 'Project One')
        proj2 = db.add_project('/project2', 'Project Two')
        
        print("Creating sample archives...")
        
        # Project 1 archives
        for i in range(5):
            doc_path = tmpdir / f'p1_doc{i}.md'
            doc_path.write_text(f"# Document {i}\n\n" + "Content " * 50)
            archive_mgr.create_archive(
                project_id=proj1,
                document_path=doc_path,
                format=ArchiveFormat.MARKDOWN,
                created_by='user1'
            )
        
        # Project 2 archives
        for i in range(3):
            doc_path = tmpdir / f'p2_doc{i}.html'
            doc_path.write_text(f"<h1>Document {i}</h1>" + "<p>Content</p>" * 30)
            archive_mgr.create_archive(
                project_id=proj2,
                document_path=doc_path,
                format=ArchiveFormat.HTML,
                created_by='user2'
            )
        
        print("  ✓ Created 5 Markdown archives for Project 1")
        print("  ✓ Created 3 HTML archives for Project 2")
        
        # Global statistics
        print("\n\nGlobal Statistics:")
        global_stats = archive_mgr.get_archive_statistics()
        print(f"  Total archives: {global_stats['total_archives']}")
        print(f"  Total size: {global_stats['total_size_bytes']:,} bytes")
        print(f"  Compressed size: {global_stats['total_compressed_bytes']:,} bytes")
        print(f"  Compression ratio: {global_stats['compression_ratio']:.2%}")
        print(f"  Space saved: {global_stats['total_size_bytes'] - global_stats['total_compressed_bytes']:,} bytes")
        print("\n  By format:")
        for fmt, count in global_stats['by_format'].items():
            print(f"    {fmt}: {count}")
        
        # Project-specific statistics
        print("\n\nProject 1 Statistics:")
        proj1_stats = archive_mgr.get_archive_statistics(project_id=proj1)
        print(f"  Archives: {proj1_stats['total_archives']}")
        print(f"  Total size: {proj1_stats['total_size_bytes']:,} bytes")
        print(f"  Compressed: {proj1_stats['total_compressed_bytes']:,} bytes")
        
        print("\n\nProject 2 Statistics:")
        proj2_stats = archive_mgr.get_archive_statistics(project_id=proj2)
        print(f"  Archives: {proj2_stats['total_archives']}")
        print(f"  Total size: {proj2_stats['total_size_bytes']:,} bytes")
        print(f"  Compressed: {proj2_stats['total_compressed_bytes']:,} bytes")
        
        db.close()
    
    print("\n✓ Demo 4 complete!\n")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  AccuDoc Archive Feature Demo")
    print("  Immutable Documentation Archives with Cryptographic Signatures")
    print("=" * 70)
    
    demos = [
        ("Basic Archive Operations", demo_basic_archive),
        ("Filtering and Search", demo_filtering),
        ("Security and Access Control", demo_security),
        ("Archive Statistics", demo_statistics),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n[{i}/{len(demos)}] Running: {name}")
        input("Press Enter to continue...")
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ Demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("  All Demos Complete!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Cryptographically signed archives with HMAC-SHA256")
    print("  ✓ Gzip compression for efficient storage")
    print("  ✓ Multi-format support (Markdown, HTML, PDF)")
    print("  ✓ Tag-based organization and filtering")
    print("  ✓ Role-based access control integration")
    print("  ✓ Complete audit trail")
    print("  ✓ Archive validation and integrity checking")
    print("  ✓ Statistics and reporting")
    print("\nFor more information, see:")
    print("  - accudoc/archive.py - Core archive module")
    print("  - test_archive.py - Comprehensive test suite")
    print("  - Archive CLI: python accudoc_cli.py archive --help")
    print("  - Archive Dashboard: python -m accudoc.archive_dashboard")
    print()


if __name__ == '__main__':
    main()
