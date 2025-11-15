"""
Backup and restore module for AccuDoc.

Allows users to backup and restore scan results, settings, cache, and audit logs.
"""

import json
import tarfile
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import datetime


@dataclass
class BackupManifest:
    """Manifest describing backup contents."""
    backup_date: str
    backup_version: str
    accudoc_version: str
    includes_cache: bool
    includes_settings: bool
    includes_audit: bool
    includes_scan_results: bool
    file_count: int
    total_size_bytes: int


class BackupManager:
    """Manage backup and restore operations for AccuDoc data."""
    
    def __init__(self, accudoc_dir: Optional[Path] = None):
        """
        Initialize backup manager.
        
        Args:
            accudoc_dir: AccuDoc data directory (default: ~/.accudoc)
        """
        if accudoc_dir is None:
            self.accudoc_dir = Path.home() / '.accudoc'
        else:
            self.accudoc_dir = Path(accudoc_dir)
        
        self.accudoc_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, output_path: Path,
                     format: str = 'zip',
                     include_cache: bool = True,
                     include_settings: bool = True,
                     include_audit: bool = True,
                     include_scan_results: bool = False) -> Path:
        """
        Create a backup archive.
        
        Args:
            output_path: Path for backup file
            format: Archive format ('zip' or 'tar.gz')
            include_cache: Include cache directory
            include_settings: Include settings file
            include_audit: Include audit logs
            include_scan_results: Include scan result files
            
        Returns:
            Path to created backup file
        """
        output_path = Path(output_path)
        
        # Collect files to backup
        files_to_backup = self._collect_files(
            include_cache=include_cache,
            include_settings=include_settings,
            include_audit=include_audit,
            include_scan_results=include_scan_results
        )
        
        if not files_to_backup:
            raise ValueError("No files to backup. AccuDoc directory may be empty.")
        
        # Create manifest
        manifest = BackupManifest(
            backup_date=datetime.datetime.now().isoformat(),
            backup_version='1.0',
            accudoc_version='1.0',  # Should be read from package
            includes_cache=include_cache,
            includes_settings=include_settings,
            includes_audit=include_audit,
            includes_scan_results=include_scan_results,
            file_count=len(files_to_backup),
            total_size_bytes=sum(f.stat().st_size for f in files_to_backup if f.exists())
        )
        
        # Create archive
        if format.lower() == 'zip':
            return self._create_zip_backup(output_path, files_to_backup, manifest)
        elif format.lower() in ['tar.gz', 'tgz']:
            return self._create_tar_backup(output_path, files_to_backup, manifest)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'zip' or 'tar.gz'")
    
    def _collect_files(self, include_cache: bool, include_settings: bool,
                      include_audit: bool, include_scan_results: bool) -> List[Path]:
        """Collect files to include in backup."""
        files = []
        
        # Settings file
        if include_settings:
            settings_file = self.accudoc_dir / 'settings.json'
            if settings_file.exists():
                files.append(settings_file)
        
        # Audit log
        if include_audit:
            audit_file = self.accudoc_dir / 'audit.log'
            if audit_file.exists():
                files.append(audit_file)
        
        # Cache directory
        if include_cache:
            cache_dir = self.accudoc_dir / 'cache'
            if cache_dir.exists():
                files.extend(cache_dir.rglob('*'))
        
        # Scan results (if any)
        if include_scan_results:
            results_dir = self.accudoc_dir / 'results'
            if results_dir.exists():
                files.extend(results_dir.rglob('*'))
        
        # Filter out directories, keep only files
        return [f for f in files if f.is_file()]
    
    def _create_zip_backup(self, output_path: Path, files: List[Path],
                          manifest: BackupManifest) -> Path:
        """Create ZIP backup archive."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Write manifest
            zf.writestr('manifest.json', json.dumps(asdict(manifest), indent=2))
            
            # Write files
            for file in files:
                arcname = file.relative_to(self.accudoc_dir.parent)
                zf.write(file, arcname)
        
        return output_path
    
    def _create_tar_backup(self, output_path: Path, files: List[Path],
                          manifest: BackupManifest) -> Path:
        """Create tar.gz backup archive."""
        # Ensure .tar.gz extension
        if not str(output_path).endswith('.tar.gz'):
            output_path = output_path.with_suffix('.tar.gz')
        
        with tarfile.open(output_path, 'w:gz') as tf:
            # Write manifest
            import io
            manifest_data = json.dumps(asdict(manifest), indent=2).encode('utf-8')
            tarinfo = tarfile.TarInfo(name='manifest.json')
            tarinfo.size = len(manifest_data)
            tf.addfile(tarinfo, io.BytesIO(manifest_data))
            
            # Write files
            for file in files:
                arcname = file.relative_to(self.accudoc_dir.parent)
                tf.add(file, arcname=arcname)
        
        return output_path
    
    def restore_backup(self, backup_path: Path,
                      restore_cache: bool = True,
                      restore_settings: bool = True,
                      restore_audit: bool = True,
                      restore_scan_results: bool = False,
                      overwrite: bool = False) -> BackupManifest:
        """
        Restore from backup archive.
        
        Args:
            backup_path: Path to backup file
            restore_cache: Restore cache directory
            restore_settings: Restore settings file
            restore_audit: Restore audit logs
            restore_scan_results: Restore scan results
            overwrite: Overwrite existing files
            
        Returns:
            BackupManifest from the backup
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Read manifest
        manifest = self._read_manifest(backup_path)
        
        # Extract based on format
        if backup_path.suffix == '.zip':
            self._restore_from_zip(backup_path, manifest, restore_cache,
                                  restore_settings, restore_audit,
                                  restore_scan_results, overwrite)
        elif backup_path.suffix == '.gz' or str(backup_path).endswith('.tar.gz'):
            self._restore_from_tar(backup_path, manifest, restore_cache,
                                  restore_settings, restore_audit,
                                  restore_scan_results, overwrite)
        else:
            raise ValueError(f"Unknown backup format: {backup_path.suffix}")
        
        return manifest
    
    def _read_manifest(self, backup_path: Path) -> BackupManifest:
        """Read manifest from backup archive."""
        if backup_path.suffix == '.zip':
            with zipfile.ZipFile(backup_path, 'r') as zf:
                manifest_data = zf.read('manifest.json')
        else:  # tar.gz
            with tarfile.open(backup_path, 'r:gz') as tf:
                manifest_file = tf.extractfile('manifest.json')
                manifest_data = manifest_file.read()
        
        manifest_dict = json.loads(manifest_data)
        return BackupManifest(**manifest_dict)
    
    def _restore_from_zip(self, backup_path: Path, manifest: BackupManifest,
                         restore_cache: bool, restore_settings: bool,
                         restore_audit: bool, restore_scan_results: bool,
                         overwrite: bool):
        """Restore from ZIP archive."""
        with zipfile.ZipFile(backup_path, 'r') as zf:
            for member in zf.namelist():
                if member == 'manifest.json':
                    continue
                
                # Check if we should restore this file
                if not self._should_restore_file(member, restore_cache,
                                                restore_settings, restore_audit,
                                                restore_scan_results):
                    continue
                
                # Extract file
                target_path = self.accudoc_dir.parent / member
                
                if target_path.exists() and not overwrite:
                    continue  # Skip existing files
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                with zf.open(member) as source, open(target_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
    
    def _restore_from_tar(self, backup_path: Path, manifest: BackupManifest,
                         restore_cache: bool, restore_settings: bool,
                         restore_audit: bool, restore_scan_results: bool,
                         overwrite: bool):
        """Restore from tar.gz archive."""
        with tarfile.open(backup_path, 'r:gz') as tf:
            for member in tf.getmembers():
                if member.name == 'manifest.json':
                    continue
                
                # Check if we should restore this file
                if not self._should_restore_file(member.name, restore_cache,
                                                restore_settings, restore_audit,
                                                restore_scan_results):
                    continue
                
                # Extract file
                target_path = self.accudoc_dir.parent / member.name
                
                if target_path.exists() and not overwrite:
                    continue  # Skip existing files
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract member
                tf.extract(member, path=self.accudoc_dir.parent)
    
    def _should_restore_file(self, file_path: str, restore_cache: bool,
                           restore_settings: bool, restore_audit: bool,
                           restore_scan_results: bool) -> bool:
        """Check if a file should be restored based on user preferences."""
        file_path = file_path.replace('\\', '/')  # Normalize path separators
        
        if not restore_cache and '/cache/' in file_path:
            return False
        
        if not restore_settings and file_path.endswith('settings.json'):
            return False
        
        if not restore_audit and file_path.endswith('audit.log'):
            return False
        
        if not restore_scan_results and '/results/' in file_path:
            return False
        
        return True
    
    def list_backup_contents(self, backup_path: Path) -> Dict[str, Any]:
        """
        List contents of a backup archive.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Dictionary with backup information
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Read manifest
        manifest = self._read_manifest(backup_path)
        
        # List files
        if backup_path.suffix == '.zip':
            with zipfile.ZipFile(backup_path, 'r') as zf:
                files = [name for name in zf.namelist() if name != 'manifest.json']
        else:  # tar.gz
            with tarfile.open(backup_path, 'r:gz') as tf:
                files = [m.name for m in tf.getmembers() if m.name != 'manifest.json']
        
        return {
            'manifest': asdict(manifest),
            'files': files,
            'file_count': len(files),
            'backup_size': backup_path.stat().st_size
        }
    
    def verify_backup(self, backup_path: Path) -> bool:
        """
        Verify backup integrity.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if backup is valid
        """
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                return False
            
            # Try to read manifest
            manifest = self._read_manifest(backup_path)
            
            # Try to list contents
            if backup_path.suffix == '.zip':
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    # Test archive integrity
                    bad_file = zf.testzip()
                    if bad_file:
                        return False
            else:  # tar.gz
                with tarfile.open(backup_path, 'r:gz') as tf:
                    # Try to list members (this will fail if corrupt)
                    list(tf.getmembers())
            
            return True
            
        except Exception:
            return False


def create_backup(output_path: Path, format: str = 'zip',
                 include_cache: bool = True,
                 include_settings: bool = True,
                 include_audit: bool = True) -> Path:
    """
    Convenience function to create a backup.
    
    Args:
        output_path: Output path for backup
        format: Archive format ('zip' or 'tar.gz')
        include_cache: Include cache
        include_settings: Include settings
        include_audit: Include audit logs
        
    Returns:
        Path to created backup
    """
    manager = BackupManager()
    return manager.create_backup(output_path, format, include_cache,
                                include_settings, include_audit)


def restore_backup(backup_path: Path, overwrite: bool = False) -> BackupManifest:
    """
    Convenience function to restore from backup.
    
    Args:
        backup_path: Path to backup file
        overwrite: Overwrite existing files
        
    Returns:
        BackupManifest
    """
    manager = BackupManager()
    return manager.restore_backup(backup_path, overwrite=overwrite)
