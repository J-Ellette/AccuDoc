"""
Progress resume module for AccuDoc.

Provides functionality to save and resume interrupted scans:
- Checkpoint management
- State persistence
- Resume from last checkpoint
- Progress tracking
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
from datetime import datetime
import hashlib


class ProgressManager:
    """Manage scan progress and enable resumption of interrupted scans."""
    
    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """
        Initialize progress manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files (default: .accudoc/checkpoints)
        """
        if checkpoint_dir is None:
            checkpoint_dir = Path.home() / '.accudoc' / 'checkpoints'
        
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('accudoc.progress')
        self.current_checkpoint = None
    
    def _get_checkpoint_id(self, repo_path: str) -> str:
        """
        Generate unique checkpoint ID for a repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Unique checkpoint ID
        """
        # Use hash of absolute path
        abs_path = str(Path(repo_path).absolute())
        return hashlib.md5(abs_path.encode()).hexdigest()[:16]
    
    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """
        Get path to checkpoint file.
        
        Args:
            checkpoint_id: Checkpoint ID
            
        Returns:
            Path to checkpoint file
        """
        return self.checkpoint_dir / f"checkpoint_{checkpoint_id}.json"
    
    def create_checkpoint(self, repo_path: str, scan_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new checkpoint for a scan.
        
        Args:
            repo_path: Path to repository being scanned
            scan_config: Configuration for the scan
            
        Returns:
            Checkpoint data
        """
        checkpoint_id = self._get_checkpoint_id(repo_path)
        
        checkpoint = {
            'checkpoint_id': checkpoint_id,
            'repo_path': str(Path(repo_path).absolute()),
            'scan_config': scan_config,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'in_progress',
            'processed_files': [],
            'failed_files': [],
            'statistics': {
                'total_files': 0,
                'processed': 0,
                'failed': 0,
                'skipped': 0
            },
            'last_file': None,
            'resume_count': 0
        }
        
        self.current_checkpoint = checkpoint
        self.save_checkpoint(checkpoint)
        
        self.logger.info(f"Created checkpoint: {checkpoint_id}")
        return checkpoint
    
    def save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """
        Save checkpoint to disk.
        
        Args:
            checkpoint: Checkpoint data to save
        """
        checkpoint['updated_at'] = datetime.now().isoformat()
        
        checkpoint_path = self._get_checkpoint_path(checkpoint['checkpoint_id'])
        
        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
            
            self.logger.debug(f"Saved checkpoint: {checkpoint['checkpoint_id']}")
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
    
    def load_checkpoint(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint for a repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Checkpoint data if exists, None otherwise
        """
        checkpoint_id = self._get_checkpoint_id(repo_path)
        checkpoint_path = self._get_checkpoint_path(checkpoint_id)
        
        if not checkpoint_path.exists():
            return None
        
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            self.current_checkpoint = checkpoint
            self.logger.info(f"Loaded checkpoint: {checkpoint_id}")
            return checkpoint
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    def update_progress(self, filepath: str, success: bool = True) -> None:
        """
        Update progress with a processed file.
        
        Args:
            filepath: Path to processed file
            success: Whether processing was successful
        """
        if not self.current_checkpoint:
            return
        
        if success:
            self.current_checkpoint['processed_files'].append(filepath)
            self.current_checkpoint['statistics']['processed'] += 1
        else:
            self.current_checkpoint['failed_files'].append(filepath)
            self.current_checkpoint['statistics']['failed'] += 1
        
        self.current_checkpoint['last_file'] = filepath
        
        # Save checkpoint every 10 files
        if self.current_checkpoint['statistics']['processed'] % 10 == 0:
            self.save_checkpoint(self.current_checkpoint)
    
    def mark_complete(self) -> None:
        """Mark current checkpoint as complete."""
        if not self.current_checkpoint:
            return
        
        self.current_checkpoint['status'] = 'complete'
        self.current_checkpoint['completed_at'] = datetime.now().isoformat()
        self.save_checkpoint(self.current_checkpoint)
        
        self.logger.info(f"Checkpoint complete: {self.current_checkpoint['checkpoint_id']}")
    
    def mark_failed(self, error: str) -> None:
        """
        Mark current checkpoint as failed.
        
        Args:
            error: Error message
        """
        if not self.current_checkpoint:
            return
        
        self.current_checkpoint['status'] = 'failed'
        self.current_checkpoint['error'] = error
        self.save_checkpoint(self.current_checkpoint)
        
        self.logger.error(f"Checkpoint failed: {error}")
    
    def can_resume(self, repo_path: str) -> bool:
        """
        Check if a scan can be resumed.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            True if resumable checkpoint exists
        """
        checkpoint = self.load_checkpoint(repo_path)
        return checkpoint is not None and checkpoint['status'] == 'in_progress'
    
    def get_processed_files(self) -> Set[str]:
        """
        Get set of already processed files.
        
        Returns:
            Set of processed file paths
        """
        if not self.current_checkpoint:
            return set()
        
        return set(self.current_checkpoint['processed_files'])
    
    def cleanup_old_checkpoints(self, days: int = 7) -> int:
        """
        Clean up old checkpoint files.
        
        Args:
            days: Remove checkpoints older than this many days
            
        Returns:
            Number of checkpoints removed
        """
        removed = 0
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for checkpoint_file in self.checkpoint_dir.glob('checkpoint_*.json'):
            if checkpoint_file.stat().st_mtime < cutoff_time:
                try:
                    checkpoint_file.unlink()
                    removed += 1
                    self.logger.debug(f"Removed old checkpoint: {checkpoint_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to remove checkpoint {checkpoint_file}: {e}")
        
        return removed
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint summaries
        """
        checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob('checkpoint_*.json'):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                
                summary = {
                    'checkpoint_id': checkpoint['checkpoint_id'],
                    'repo_path': checkpoint['repo_path'],
                    'status': checkpoint['status'],
                    'created_at': checkpoint['created_at'],
                    'updated_at': checkpoint['updated_at'],
                    'processed': checkpoint['statistics']['processed'],
                    'failed': checkpoint['statistics']['failed']
                }
                
                checkpoints.append(summary)
            except Exception as e:
                self.logger.error(f"Failed to read checkpoint {checkpoint_file}: {e}")
        
        return sorted(checkpoints, key=lambda x: x['updated_at'], reverse=True)
    
    def delete_checkpoint(self, repo_path: str) -> bool:
        """
        Delete checkpoint for a repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            True if deleted successfully
        """
        checkpoint_id = self._get_checkpoint_id(repo_path)
        checkpoint_path = self._get_checkpoint_path(checkpoint_id)
        
        if checkpoint_path.exists():
            try:
                checkpoint_path.unlink()
                self.logger.info(f"Deleted checkpoint: {checkpoint_id}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to delete checkpoint: {e}")
                return False
        
        return False
    
    def get_progress_percentage(self) -> float:
        """
        Get current progress percentage.
        
        Returns:
            Progress percentage (0-100)
        """
        if not self.current_checkpoint:
            return 0.0
        
        stats = self.current_checkpoint['statistics']
        total = stats['total_files']
        
        if total == 0:
            return 0.0
        
        processed = stats['processed'] + stats['failed'] + stats['skipped']
        return (processed / total) * 100.0
    
    def generate_progress_report(self) -> str:
        """
        Generate progress report.
        
        Returns:
            Markdown formatted progress report
        """
        if not self.current_checkpoint:
            return "No active checkpoint."
        
        cp = self.current_checkpoint
        stats = cp['statistics']
        
        md = []
        md.append("# Scan Progress Report\n")
        md.append(f"**Repository**: {cp['repo_path']}")
        md.append(f"**Status**: {cp['status']}")
        md.append(f"**Started**: {cp['created_at']}")
        md.append(f"**Last Updated**: {cp['updated_at']}\n")
        
        md.append("## Statistics\n")
        md.append(f"- **Total Files**: {stats['total_files']}")
        md.append(f"- **Processed**: {stats['processed']}")
        md.append(f"- **Failed**: {stats['failed']}")
        md.append(f"- **Skipped**: {stats['skipped']}")
        md.append(f"- **Progress**: {self.get_progress_percentage():.1f}%\n")
        
        if cp['last_file']:
            md.append(f"**Last File**: `{cp['last_file']}`\n")
        
        if cp['resume_count'] > 0:
            md.append(f"*This scan has been resumed {cp['resume_count']} time(s)*\n")
        
        return '\n'.join(md)
