"""
Tests for archive functionality.
"""

import sys
import tempfile
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from accudoc.archive import ArchiveManager, ArchiveFormat
from accudoc.project_database import ProjectDatabase
from accudoc.audit import AuditLogger
from accudoc.membership import MembershipManager, Role, Permission


def test_create_and_retrieve_archive():
    """Test creating and retrieving an archive."""
    print("=" * 60)
    print("Test 1: Create and Retrieve Archive")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        db_path = tmpdir / 'test.db'
        
        # Create test document
        doc_path = tmpdir / 'test.md'
        doc_content = "# Test Documentation\n\nThis is a test document."
        doc_path.write_text(doc_content)
        
        # Initialize components
        db = ProjectDatabase(db_path)
        audit_log = AuditLogger(tmpdir / 'audit.log')
        archive_mgr = ArchiveManager(db, audit_log)
        
        # Create project
        project_id = db.add_project('/test/repo', 'Test Project')
        
        # Create archive
        archive_id = archive_mgr.create_archive(
            project_id=project_id,
            document_path=doc_path,
            format=ArchiveFormat.MARKDOWN,
            created_by='test_user',
            tags=['test', 'documentation'],
            description='Test archive'
        )
        
        print(f"✓ Archive created: {archive_id}")
        
        # Retrieve archive
        content, metadata = archive_mgr.retrieve_archive(archive_id, 'test_user')
        
        assert content.decode() == doc_content, "Retrieved content should match original"
        assert metadata.archive_id == archive_id, "Metadata should have correct archive_id"
        assert metadata.format == ArchiveFormat.MARKDOWN.value, "Format should be markdown"
        assert 'test' in metadata.tags, "Tags should be preserved"
        
        print(f"✓ Archive retrieved successfully")
        print(f"  - Archive ID: {metadata.archive_id}")
        print(f"  - Format: {metadata.format}")
        print(f"  - Size: {metadata.size_bytes} bytes")
        print(f"  - Tags: {metadata.tags}")
        print(f"  - Created: {metadata.created_at}")
        
        print("\n✓ Test PASSED: Create and retrieve archive working\n")


def test_archive_validation():
    """Test archive signature validation."""
    print("=" * 60)
    print("Test 2: Archive Validation")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        db_path = tmpdir / 'test.db'
        
        # Create test document
        doc_path = tmpdir / 'test.md'
        doc_content = "# Valid Document"
        doc_path.write_text(doc_content)
        
        # Initialize components
        db = ProjectDatabase(db_path)
        archive_mgr = ArchiveManager(db)
        
        # Create project and archive
        project_id = db.add_project('/test/repo', 'Test Project')
        archive_id = archive_mgr.create_archive(
            project_id=project_id,
            document_path=doc_path,
            format=ArchiveFormat.MARKDOWN,
            created_by='test_user'
        )
        
        # Validate archive
        is_valid = archive_mgr.validate_archive(archive_id)
        assert is_valid, "Archive should be valid"
        print("✓ Archive signature is valid")
        
        # Retrieve with validation
        content, metadata = archive_mgr.retrieve_archive(
            archive_id, 'test_user', validate=True
        )
        print("✓ Archive retrieved with validation")
        
        # Test tampering detection (modify database directly)
        cursor = db.conn.cursor()
        cursor.execute('''
            UPDATE archives SET content_hash = 'tampered_hash'
            WHERE archive_id = ?
        ''', (archive_id,))
        db.conn.commit()
        
        # Validation should fail
        is_valid = archive_mgr.validate_archive(archive_id)
        assert not is_valid, "Tampered archive should be invalid"
        print("✓ Tampering detected correctly")
        
        print("\n✓ Test PASSED: Archive validation working\n")


def test_list_archives():
    """Test listing archives with filters."""
    print("=" * 60)
    print("Test 3: List Archives")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        db_path = tmpdir / 'test.db'
        
        # Initialize components
        db = ProjectDatabase(db_path)
        archive_mgr = ArchiveManager(db)
        
        # Create project
        project_id = db.add_project('/test/repo', 'Test Project')
        
        # Create multiple archives
        for i in range(5):
            doc_path = tmpdir / f'test{i}.md'
            doc_path.write_text(f"# Document {i}")
            
            archive_mgr.create_archive(
                project_id=project_id,
                document_path=doc_path,
                format=ArchiveFormat.MARKDOWN,
                created_by='test_user',
                tags=['test', f'doc{i}']
            )
            time.sleep(0.01)  # Ensure different timestamps
        
        # Create HTML archive
        html_path = tmpdir / 'test.html'
        html_path.write_text('<h1>HTML Doc</h1>')
        archive_mgr.create_archive(
            project_id=project_id,
            document_path=html_path,
            format=ArchiveFormat.HTML,
            created_by='test_user',
            tags=['test', 'html']
        )
        
        # List all archives
        all_archives = archive_mgr.list_archives(project_id=project_id)
        assert len(all_archives) == 6, "Should have 6 archives"
        print(f"✓ Listed {len(all_archives)} total archives")
        
        # Filter by format
        md_archives = archive_mgr.list_archives(
            project_id=project_id,
            format=ArchiveFormat.MARKDOWN
        )
        assert len(md_archives) == 5, "Should have 5 markdown archives"
        print(f"✓ Filtered {len(md_archives)} markdown archives")
        
        # Filter by tags
        html_archives = archive_mgr.list_archives(
            project_id=project_id,
            tags=['html']
        )
        assert len(html_archives) == 1, "Should have 1 HTML archive"
        print(f"✓ Filtered {len(html_archives)} HTML archive by tag")
        
        # Test limit
        limited = archive_mgr.list_archives(project_id=project_id, limit=3)
        assert len(limited) == 3, "Should respect limit"
        print(f"✓ Limit working (limited to {len(limited)} archives)")
        
        print("\n✓ Test PASSED: List archives working\n")


def test_archive_with_membership():
    """Test archive with membership/permission system."""
    print("=" * 60)
    print("Test 4: Archive with Membership System")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        db_path = tmpdir / 'test.db'
        membership_db = tmpdir / 'membership.db'
        
        # Initialize components
        db = ProjectDatabase(db_path)
        membership = MembershipManager(membership_db)
        archive_mgr = ArchiveManager(db, membership_manager=membership)
        
        # Create users
        owner = membership.create_user('owner', 'owner@test.com', 'password', Role.OWNER)
        viewer = membership.create_user('viewer', 'viewer@test.com', 'password', Role.VIEWER)
        
        # Create project
        project_id = db.add_project('/test/repo', 'Test Project')
        
        # Grant access
        membership.grant_project_access(
            project_id=project_id,
            granted_by=owner.user_id,
            user_id=owner.user_id,
            role=Role.OWNER
        )
        membership.grant_project_access(
            project_id=project_id,
            granted_by=owner.user_id,
            user_id=viewer.user_id,
            role=Role.VIEWER
        )
        
        # Create test document
        doc_path = tmpdir / 'test.md'
        doc_path.write_text("# Secure Document")
        
        # Owner can create archive
        archive_id = archive_mgr.create_archive(
            project_id=project_id,
            document_path=doc_path,
            format=ArchiveFormat.MARKDOWN,
            created_by=owner.user_id
        )
        print(f"✓ Owner created archive: {archive_id}")
        
        # Viewer cannot create archive (no WRITE permission)
        try:
            archive_mgr.create_archive(
                project_id=project_id,
                document_path=doc_path,
                format=ArchiveFormat.MARKDOWN,
                created_by=viewer.user_id
            )
            assert False, "Viewer should not be able to create archive"
        except PermissionError:
            print("✓ Viewer correctly denied archive creation")
        
        # Viewer can retrieve archive (has READ permission)
        content, metadata = archive_mgr.retrieve_archive(archive_id, viewer.user_id)
        assert content.decode() == "# Secure Document"
        print("✓ Viewer retrieved archive successfully")
        
        # Viewer cannot delete archive (no DELETE permission)
        try:
            archive_mgr.delete_archive(archive_id, viewer.user_id)
            assert False, "Viewer should not be able to delete archive"
        except PermissionError:
            print("✓ Viewer correctly denied archive deletion")
        
        # Owner can delete archive
        archive_mgr.delete_archive(archive_id, owner.user_id)
        print("✓ Owner deleted archive successfully")
        
        print("\n✓ Test PASSED: Membership integration working\n")


def test_archive_statistics():
    """Test archive statistics."""
    print("=" * 60)
    print("Test 5: Archive Statistics")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        db_path = tmpdir / 'test.db'
        
        # Initialize components
        db = ProjectDatabase(db_path)
        archive_mgr = ArchiveManager(db)
        
        # Create project
        project_id = db.add_project('/test/repo', 'Test Project')
        
        # Create archives
        for i in range(3):
            doc_path = tmpdir / f'test{i}.md'
            doc_path.write_text(f"# Document {i}\n\n" + "Content " * 100)
            archive_mgr.create_archive(
                project_id=project_id,
                document_path=doc_path,
                format=ArchiveFormat.MARKDOWN,
                created_by='test_user'
            )
        
        # HTML archive
        html_path = tmpdir / 'test.html'
        html_path.write_text('<h1>HTML</h1>' * 50)
        archive_mgr.create_archive(
            project_id=project_id,
            document_path=html_path,
            format=ArchiveFormat.HTML,
            created_by='test_user'
        )
        
        # Get statistics
        stats = archive_mgr.get_archive_statistics(project_id=project_id)
        
        assert stats['total_archives'] == 4, "Should have 4 archives"
        assert stats['total_size_bytes'] > 0, "Should have size"
        assert stats['compression_ratio'] < 1.0, "Should be compressed"
        assert 'markdown' in stats['by_format'], "Should have markdown format"
        assert 'html' in stats['by_format'], "Should have HTML format"
        
        print(f"✓ Statistics calculated:")
        print(f"  - Total archives: {stats['total_archives']}")
        print(f"  - Total size: {stats['total_size_bytes']} bytes")
        print(f"  - Compressed: {stats['total_compressed_bytes']} bytes")
        print(f"  - Compression ratio: {stats['compression_ratio']:.2%}")
        print(f"  - By format: {stats['by_format']}")
        
        print("\n✓ Test PASSED: Archive statistics working\n")


def test_audit_trail_integration():
    """Test audit trail integration."""
    print("=" * 60)
    print("Test 6: Audit Trail Integration")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        db_path = tmpdir / 'test.db'
        audit_log_path = tmpdir / 'audit.log'
        
        # Initialize components
        db = ProjectDatabase(db_path)
        audit_log = AuditLogger(audit_log_path)
        archive_mgr = ArchiveManager(db, audit_logger=audit_log)
        
        # Create project
        project_id = db.add_project('/test/repo', 'Test Project')
        
        # Create archive
        doc_path = tmpdir / 'test.md'
        doc_path.write_text("# Test")
        archive_id = archive_mgr.create_archive(
            project_id=project_id,
            document_path=doc_path,
            format=ArchiveFormat.MARKDOWN,
            created_by='test_user'
        )
        
        # Retrieve archive
        archive_mgr.retrieve_archive(archive_id, 'test_user')
        
        # Delete archive
        archive_mgr.delete_archive(archive_id, 'test_user')
        
        # Check audit log
        audit_entries = audit_log.get_recent_entries(count=10)
        audit_text = ''.join(audit_entries)
        
        assert 'create_archive' in audit_text, "Should log create operation"
        assert 'retrieve_archive' in audit_text, "Should log retrieve operation"
        assert 'delete_archive' in audit_text, "Should log delete operation"
        assert archive_id in audit_text, "Should log archive ID"
        
        print("✓ Audit trail entries found:")
        for entry in audit_entries:
            if any(op in entry for op in ['create_archive', 'retrieve_archive', 'delete_archive']):
                print(f"  - {entry.strip()}")
        
        print("\n✓ Test PASSED: Audit trail integration working\n")


def run_all_tests():
    """Run all archive tests."""
    print("\n" + "=" * 60)
    print("AccuDoc Archive Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_create_and_retrieve_archive,
        test_archive_validation,
        test_list_archives,
        test_archive_with_membership,
        test_archive_statistics,
        test_audit_trail_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test FAILED: {test_func.__name__}")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
