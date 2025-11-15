"""
Caching module for AccuDoc to enable smart caching and incremental updates.

This module provides file-level caching to avoid re-scanning unchanged files
in large repositories, significantly improving performance.
"""

import json
import hashlib
import os
import time
from pathlib import Path
from typing import Dict, Optional, Set, Any
from datetime import datetime


class CacheManager:
    """Manages caching for repository scans."""
    
    CACHE_VERSION = "1.0"
    CACHE_DIR_NAME = ".accudoc_cache"
    
    def __init__(self, repo_path: str):
        """
        Initialize the cache manager.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.cache_dir = self.repo_path / self.CACHE_DIR_NAME
        self.cache_file = self.cache_dir / "cache.json"
        self.metadata_file = self.cache_dir / "metadata.json"
        self.cache_data = {}
        self.metadata = {}
        self.enabled = True
        
    def initialize(self):
        """Initialize cache directory and load existing cache."""
        if not self.enabled:
            return
            
        try:
            # Create cache directory if it doesn't exist
            self.cache_dir.mkdir(exist_ok=True)
            
            # Load existing cache
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
            
            # Load metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                    
            # Validate cache version
            if self.metadata.get('version') != self.CACHE_VERSION:
                self._invalidate_cache()
                self.metadata = {
                    'version': self.CACHE_VERSION,
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            # If cache loading fails, start fresh
            self.cache_data = {}
            self.metadata = {
                'version': self.CACHE_VERSION,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hex digest of file hash
        """
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            # If we can't read the file, return a unique identifier
            return f"error_{file_path.stat().st_mtime}"
    
    def _get_file_metadata(self, file_path: Path) -> Dict:
        """
        Get metadata for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'hash': self._compute_file_hash(file_path)
            }
        except Exception:
            return {}
    
    def is_file_cached(self, file_path: Path) -> bool:
        """
        Check if a file is cached and unchanged.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is cached and unchanged
        """
        if not self.enabled:
            return False
            
        try:
            # Get relative path
            rel_path = str(file_path.relative_to(self.repo_path))
            
            # Check if in cache
            if rel_path not in self.cache_data:
                return False
            
            # Get current metadata
            current_meta = self._get_file_metadata(file_path)
            cached_meta = self.cache_data[rel_path].get('metadata', {})
            
            # Compare hash (most reliable)
            if current_meta.get('hash') != cached_meta.get('hash'):
                return False
            
            # Also check mtime and size for quick validation
            if current_meta.get('mtime') != cached_meta.get('mtime'):
                return False
            if current_meta.get('size') != cached_meta.get('size'):
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_cached_data(self, file_path: Path) -> Optional[Dict]:
        """
        Get cached data for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Cached data or None if not cached
        """
        if not self.enabled:
            return None
            
        try:
            rel_path = str(file_path.relative_to(self.repo_path))
            if self.is_file_cached(file_path):
                return self.cache_data[rel_path].get('data')
            return None
        except Exception:
            return None
    
    def cache_file_data(self, file_path: Path, data: Any):
        """
        Cache data for a file.
        
        Args:
            file_path: Path to the file
            data: Data to cache
        """
        if not self.enabled:
            return
            
        try:
            rel_path = str(file_path.relative_to(self.repo_path))
            metadata = self._get_file_metadata(file_path)
            
            self.cache_data[rel_path] = {
                'metadata': metadata,
                'data': data,
                'cached_at': datetime.now().isoformat()
            }
        except Exception:
            pass
    
    def get_changed_files(self, file_list: list) -> tuple:
        """
        Determine which files have changed since last scan.
        
        Args:
            file_list: List of file paths to check
            
        Returns:
            Tuple of (changed_files, cached_files)
        """
        if not self.enabled:
            return file_list, []
            
        changed = []
        cached = []
        
        for file_path in file_list:
            path = Path(file_path) if isinstance(file_path, str) else file_path
            if self.is_file_cached(path):
                cached.append(path)
            else:
                changed.append(path)
        
        return changed, cached
    
    def save(self):
        """Save cache to disk."""
        if not self.enabled:
            return
            
        try:
            # Update metadata
            self.metadata['last_updated'] = datetime.now().isoformat()
            self.metadata['file_count'] = len(self.cache_data)
            
            # Save cache data
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, indent=2, default=str)
            
            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
                
        except Exception as e:
            # Silently fail - caching is optional
            pass
    
    def clear(self):
        """Clear all cached data."""
        self.cache_data = {}
        self.metadata = {
            'version': self.CACHE_VERSION,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        """Remove cache files from disk."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
        except Exception:
            pass
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_size = 0
        for cached_item in self.cache_data.values():
            metadata = cached_item.get('metadata', {})
            total_size += metadata.get('size', 0)
        
        return {
            'enabled': self.enabled,
            'cache_dir': str(self.cache_dir),
            'version': self.metadata.get('version', 'unknown'),
            'created_at': self.metadata.get('created_at', 'unknown'),
            'last_updated': self.metadata.get('last_updated', 'unknown'),
            'cached_files': len(self.cache_data),
            'total_size_bytes': total_size,
            'cache_exists': self.cache_file.exists()
        }
    
    def disable(self):
        """Disable caching."""
        self.enabled = False
    
    def enable(self):
        """Enable caching."""
        self.enabled = True
