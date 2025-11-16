"""
Tests for backup and restore functionality.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from accudoc.backup import BackupManager, create_backup, restore_backup


def setup_test_data(accudoc_dir: Path):
    """Create test data for backup."""
    accudoc_dir.mkdir(parents=True, exist_ok=True)
    
    # Create settings file
    settings_file = accudoc_dir / 'settings.json'
    settings_file.write_text(json.dumps({'test': 'settings'}, indent=2))
    
    # Create audit log
    audit_file = accudoc_dir / 'audit.log'
    audit_file.write_text('Test audit log entry\n')
    
    # Create cache directory with some files
    cache_dir = accudoc_dir / 'cache'
    cache_dir.mkdir(exist_ok=True)
    (cache_dir / 'cache_file1.txt').write_text('Cache data 1')
    (cache_dir / 'cache_file2.txt').write_text('Cache data 2')
    
    # Create results directory
    results_dir = accudoc_dir / 'results'
    results_dir.mkdir(exist_ok=True)
    (results_dir / 'result1.json').write_text('{"result": 1}')


def test_zip_backup_creation():
    """Test creating a ZIP backup."""
    print("=" * 60)
    print("Test 1: ZIP Backup Creation")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        accudoc_dir = Path(tmpdir) / '.accudoc'
        setup_test_data(accudoc_dir)
        
        backup_file = Path(tmpdir) / 'backup.zip'
        
        manager = BackupManager(accudoc_dir)
        result = manager.create_backup(backup_file, format='zip')
        
        assert result.exists(), "Backup file should exist"
        assert result.suffix == '.zip', "Should have .zip extension"
        assert result.stat().st_size > 0, "Backup should not be empty"
        
        print(f"✓ Backup created: {result}")
        print(f"✓ File size: {result.stat().st_size} bytes")
    
    print("\n✓ Test PASSED: ZIP backup creation working\n")
    return True


def test_tar_backup_creation():
    """Test creating a tar.gz backup."""
    print("=" * 60)
    print("Test 2: Tar.gz Backup Creation")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        accudoc_dir = Path(tmpdir) / '.accudoc'
        setup_test_data(accudoc_dir)
        
        backup_file = Path(tmpdir) / 'backup.tar.gz'
        
        manager = BackupManager(accudoc_dir)
        result = manager.create_backup(backup_file, format='tar.gz')
        
        assert result.exists(), "Backup file should exist"
        assert str(result).endswith('.tar.gz'), "Should have .tar.gz extension"
        assert result.stat().st_size > 0, "Backup should not be empty"
        
        print(f"✓ Backup created: {result}")
        print(f"✓ File size: {result.stat().st_size} bytes")
    
    print("\n✓ Test PASSED: Tar.gz backup creation working\n")
    return True


def test_selective_backup():
    """Test selective backup (excluding certain items)."""
    print("=" * 60)
    print("Test 3: Selective Backup")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        accudoc_dir = Path(tmpdir) / '.accudoc'
        setup_test_data(accudoc_dir)
        
        backup_file = Path(tmpdir) / 'selective_backup.zip'
        
        manager = BackupManager(accudoc_dir)
        result = manager.create_backup(
            backup_file,
            format='zip',
            include_cache=False,  # Exclude cache
            include_settings=True,
            include_audit=True
        )
        
        # List contents
        contents = manager.list_backup_contents(result)
        
        # Check that cache is not included
        cache_files = [f for f in contents['files'] if '/cache/' in f]
        assert len(cache_files) == 0, "Cache should not be in backup"
        
        # Check that settings is included
        settings_files = [f for f in contents['files'] if 'settings.json' in f]
        assert len(settings_files) > 0, "Settings should be in backup"
        
        print(f"✓ Selective backup created")
        print(f"✓ Cache excluded as requested")
        print(f"✓ Settings included as requested")
    
    print("\n✓ Test PASSED: Selective backup working\n")
    return True


def test_zip_restore():
    """Test restoring from ZIP backup."""
    print("=" * 60)
    print("Test 4: ZIP Restore")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create original data
        original_dir = Path(tmpdir) / 'original' / '.accudoc'
        setup_test_data(original_dir)
        
        # Create backup
        backup_file = Path(tmpdir) / 'backup.zip'
        manager_orig = BackupManager(original_dir)
        manager_orig.create_backup(backup_file, format='zip')
        
        # Restore to new location
        restore_dir = Path(tmpdir) / 'restored' / '.accudoc'
        manager_new = BackupManager(restore_dir)
        manifest = manager_new.restore_backup(backup_file)
        
        # Verify restored files
        assert (restore_dir / 'settings.json').exists(), "Settings should be restored"
        assert (restore_dir / 'audit.log').exists(), "Audit log should be restored"
        assert (restore_dir / 'cache').exists(), "Cache dir should be restored"
        
        # Verify content
        settings_content = (restore_dir / 'settings.json').read_text()
        assert 'test' in settings_content, "Settings content should match"
        
        print(f"✓ Backup restored successfully")
        print(f"✓ Files verified")
        print(f"✓ Manifest: {manifest.file_count} files")
    
    print("\n✓ Test PASSED: ZIP restore working\n")
    return True


def test_tar_restore():
    """Test restoring from tar.gz backup."""
    print("=" * 60)
    print("Test 5: Tar.gz Restore")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create original data
        original_dir = Path(tmpdir) / 'original' / '.accudoc'
        setup_test_data(original_dir)
        
        # Create backup
        backup_file = Path(tmpdir) / 'backup.tar.gz'
        manager_orig = BackupManager(original_dir)
        manager_orig.create_backup(backup_file, format='tar.gz')
        
        # Restore to new location
        restore_dir = Path(tmpdir) / 'restored' / '.accudoc'
        manager_new = BackupManager(restore_dir)
        manifest = manager_new.restore_backup(backup_file)
        
        # Verify restored files
        assert (restore_dir / 'settings.json').exists(), "Settings should be restored"
        assert (restore_dir / 'audit.log').exists(), "Audit log should be restored"
        
        print(f"✓ Tar.gz backup restored successfully")
        print(f"✓ Files verified")
    
    print("\n✓ Test PASSED: Tar.gz restore working\n")
    return True


def test_selective_restore():
    """Test selective restore."""
    print("=" * 60)
    print("Test 6: Selective Restore")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and backup original data
        original_dir = Path(tmpdir) / 'original' / '.accudoc'
        setup_test_data(original_dir)
        
        backup_file = Path(tmpdir) / 'backup.zip'
        manager_orig = BackupManager(original_dir)
        manager_orig.create_backup(backup_file, format='zip')
        
        # Restore only settings (not cache or audit)
        restore_dir = Path(tmpdir) / 'restored' / '.accudoc'
        manager_new = BackupManager(restore_dir)
        manager_new.restore_backup(
            backup_file,
            restore_cache=False,
            restore_settings=True,
            restore_audit=False
        )
        
        # Verify selective restore
        assert (restore_dir / 'settings.json').exists(), "Settings should be restored"
        assert not (restore_dir / 'audit.log').exists(), "Audit should not be restored"
        assert not (restore_dir / 'cache').exists(), "Cache should not be restored"
        
        print(f"✓ Selective restore successful")
        print(f"✓ Only settings restored as requested")
    
    print("\n✓ Test PASSED: Selective restore working\n")
    return True


def test_overwrite_protection():
    """Test overwrite protection."""
    print("=" * 60)
    print("Test 7: Overwrite Protection")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and backup original data
        original_dir = Path(tmpdir) / 'original' / '.accudoc'
        setup_test_data(original_dir)
        
        backup_file = Path(tmpdir) / 'backup.zip'
        manager_orig = BackupManager(original_dir)
        manager_orig.create_backup(backup_file, format='zip')
        
        # Create existing data
        restore_dir = Path(tmpdir) / 'restored' / '.accudoc'
        restore_dir.mkdir(parents=True)
        existing_settings = restore_dir / 'settings.json'
        existing_settings.write_text('{"existing": "data"}')
        
        # Restore without overwrite
        manager_new = BackupManager(restore_dir)
        manager_new.restore_backup(backup_file, overwrite=False)
        
        # Verify existing file was not overwritten
        content = existing_settings.read_text()
        assert 'existing' in content, "Existing file should not be overwritten"
        assert 'test' not in content, "Original content should be preserved"
        
        print(f"✓ Overwrite protection working")
        print(f"✓ Existing files preserved")
    
    print("\n✓ Test PASSED: Overwrite protection working\n")
    return True


def test_list_backup_contents():
    """Test listing backup contents."""
    print("=" * 60)
    print("Test 8: List Backup Contents")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        accudoc_dir = Path(tmpdir) / '.accudoc'
        setup_test_data(accudoc_dir)
        
        backup_file = Path(tmpdir) / 'backup.zip'
        
        manager = BackupManager(accudoc_dir)
        manager.create_backup(backup_file, format='zip')
        
        # List contents
        contents = manager.list_backup_contents(backup_file)
        
        assert 'manifest' in contents
        assert 'files' in contents
        assert 'file_count' in contents
        assert contents['file_count'] > 0
        
        print(f"✓ Listed backup contents")
        print(f"✓ File count: {contents['file_count']}")
        print(f"✓ Backup size: {contents['backup_size']} bytes")
    
    print("\n✓ Test PASSED: List contents working\n")
    return True


def test_verify_backup():
    """Test backup verification."""
    print("=" * 60)
    print("Test 9: Backup Verification")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        accudoc_dir = Path(tmpdir) / '.accudoc'
        setup_test_data(accudoc_dir)
        
        backup_file = Path(tmpdir) / 'backup.zip'
        
        manager = BackupManager(accudoc_dir)
        manager.create_backup(backup_file, format='zip')
        
        # Verify valid backup
        is_valid = manager.verify_backup(backup_file)
        assert is_valid, "Valid backup should pass verification"
        
        print(f"✓ Valid backup verified")
        
        # Test with non-existent file
        fake_backup = Path(tmpdir) / 'fake.zip'
        is_valid = manager.verify_backup(fake_backup)
        assert not is_valid, "Non-existent backup should fail verification"
        
        print(f"✓ Invalid backup rejected")
    
    print("\n✓ Test PASSED: Backup verification working\n")
    return True


def test_convenience_functions():
    """Test convenience functions."""
    print("=" * 60)
    print("Test 10: Convenience Functions")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        accudoc_dir = Path(tmpdir) / '.accudoc'
        setup_test_data(accudoc_dir)
        
        backup_file = Path(tmpdir) / 'convenience_backup.zip'
        
        # Use convenience function to create backup
        # Temporarily override the default location
        import accudoc.backup as backup_module
        original_home = Path.home
        try:
            # Mock home directory
            backup_module.Path.home = lambda: Path(tmpdir)
            
            result = create_backup(backup_file, format='zip')
            assert result.exists()
            print(f"✓ Convenience create_backup works")
            
            # Restore
            restore_dir = Path(tmpdir) / 'restored' / '.accudoc'
            manifest = restore_backup(result)
            print(f"✓ Convenience restore_backup works")
            
        finally:
            backup_module.Path.home = original_home
    
    print("\n✓ Test PASSED: Convenience functions working\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AccuDoc Backup/Restore Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_zip_backup_creation,
        test_tar_backup_creation,
        test_selective_backup,
        test_zip_restore,
        test_tar_restore,
        test_selective_restore,
        test_overwrite_protection,
        test_list_backup_contents,
        test_verify_backup,
        test_convenience_functions,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test failed with exception: {str(e)}\n")
            import traceback
            traceback.print_exc()
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
