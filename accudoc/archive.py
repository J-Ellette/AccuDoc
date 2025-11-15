"""
Immutable Documentation Archive module for AccuDoc.

Provides cryptographically signed, timestamped archival snapshots of documentation
stored in AccuDoc's database with validation and retrieval capabilities.
"""

import hashlib
import hmac
import secrets
import json
import base64
import gzip
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ArchiveFormat(Enum):
    """Supported archive formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


@dataclass
class ArchiveMetadata:
    """Metadata for an archived document."""
    archive_id: str
    project_id: str
    document_name: str
    format: str
    created_at: str
    created_by: str
    content_hash: str
    signature: str
    size_bytes: int
    compression: str
    tags: List[str]
    description: Optional[str] = None


class ArchiveManager:
    """Manages immutable documentation archives."""
    
    def __init__(self, database, audit_logger=None, membership_manager=None):
        """
        Initialize archive manager.
        
        Args:
            database: ProjectDatabase instance
            audit_logger: AuditLogger instance (optional)
            membership_manager: MembershipManager instance (optional)
        """
        from accudoc.project_database import ProjectDatabase
        
        if isinstance(database, str) or isinstance(database, Path):
            self.db = ProjectDatabase(Path(database))
        else:
            self.db = database
            
        self.audit_logger = audit_logger
        self.membership_manager = membership_manager
        self._ensure_archive_schema()
        
        # Secret key for signing (in production, should be stored securely)
        self.signing_key = self._get_or_create_signing_key()
    
    def _ensure_archive_schema(self) -> None:
        """Ensure archive tables exist in database."""
        cursor = self.db.conn.cursor()
        
        # Archives table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archives (
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
                metadata TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        ''')
        
        # Archive access log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archive_access_log (
                access_id INTEGER PRIMARY KEY AUTOINCREMENT,
                archive_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                accessed_at TEXT NOT NULL,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (archive_id) REFERENCES archives(archive_id)
            )
        ''')
        
        # Signing keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signing_keys (
                key_id TEXT PRIMARY KEY,
                key_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_archives_project ON archives(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_archives_created ON archives(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_archive_access ON archive_access_log(archive_id)')
        
        self.db.conn.commit()
    
    def _get_or_create_signing_key(self) -> bytes:
        """Get or create signing key."""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT key_data FROM signing_keys WHERE is_active = 1 LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            return base64.b64decode(row['key_data'])
        
        # Create new key
        key = secrets.token_bytes(32)  # 256-bit key
        key_id = secrets.token_urlsafe(16)
        
        cursor.execute('''
            INSERT INTO signing_keys (key_id, key_data, created_at, is_active)
            VALUES (?, ?, ?, 1)
        ''', (key_id, base64.b64encode(key).decode(), datetime.now().isoformat()))
        self.db.conn.commit()
        
        return key
    
    def create_archive(self, project_id: str, document_path: Path,
                      format: ArchiveFormat, created_by: str,
                      tags: Optional[List[str]] = None,
                      description: Optional[str] = None) -> str:
        """
        Create an immutable archive of a document.
        
        Args:
            project_id: Project ID
            document_path: Path to document file
            format: Document format
            created_by: User ID creating the archive
            tags: Optional tags for categorization
            description: Optional description
            
        Returns:
            Archive ID
        """
        start_time = datetime.now()
        
        # Check permissions if membership manager available
        if self.membership_manager:
            from accudoc.membership import Permission
            if not self.membership_manager.check_permission(created_by, project_id, Permission.WRITE):
                error_msg = f"User {created_by} lacks permission to create archive"
                self._log_audit('create_archive', 'failure', 
                              {'project_id': project_id}, error=error_msg)
                raise PermissionError(error_msg)
        
        # Read document content
        try:
            with open(document_path, 'rb') as f:
                content = f.read()
        except Exception as e:
            self._log_audit('create_archive', 'failure',
                          {'project_id': project_id, 'document': str(document_path)},
                          error=str(e))
            raise
        
        # Compress content
        compressed_content = gzip.compress(content)
        
        # Calculate content hash
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Generate archive ID and timestamp
        archive_id = self._generate_archive_id(project_id, content_hash)
        created_at = datetime.now().isoformat()
        
        # Create signature
        signature_data = {
            'archive_id': archive_id,
            'project_id': project_id,
            'content_hash': content_hash,
            'created_at': created_at,
            'format': format.value
        }
        signature = self._sign_data(signature_data)
        
        # Store in database
        cursor = self.db.conn.cursor()
        cursor.execute('''
            INSERT INTO archives
            (archive_id, project_id, document_name, format, created_at, created_by,
             content_hash, signature, size_bytes, compressed_content, compression,
             tags, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            archive_id,
            project_id,
            document_path.name,
            format.value,
            created_at,
            created_by,
            content_hash,
            signature,
            len(content),
            compressed_content,
            'gzip',
            json.dumps(tags or []),
            description,
            json.dumps({'original_size': len(content), 'compressed_size': len(compressed_content)})
        ))
        self.db.conn.commit()
        
        # Log access
        self._log_archive_access(archive_id, created_by, 'create', 'success')
        
        # Audit log
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self._log_audit('create_archive', 'success', {
            'archive_id': archive_id,
            'project_id': project_id,
            'document_name': document_path.name,
            'format': format.value,
            'size_bytes': len(content),
            'compressed_size': len(compressed_content)
        }, duration_ms=duration_ms)
        
        return archive_id
    
    def retrieve_archive(self, archive_id: str, user_id: str,
                        validate: bool = True) -> Tuple[bytes, ArchiveMetadata]:
        """
        Retrieve an archived document.
        
        Args:
            archive_id: Archive ID
            user_id: User ID requesting retrieval
            validate: Whether to validate signature (default: True)
            
        Returns:
            Tuple of (document content, metadata)
        """
        start_time = datetime.now()
        
        # Get archive from database
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM archives WHERE archive_id = ?', (archive_id,))
        row = cursor.fetchone()
        
        if not row:
            self._log_audit('retrieve_archive', 'failure',
                          {'archive_id': archive_id}, error='Archive not found')
            raise ValueError(f"Archive not found: {archive_id}")
        
        # Check permissions
        project_id = row['project_id']
        if self.membership_manager:
            from accudoc.membership import Permission
            if not self.membership_manager.check_permission(user_id, project_id, Permission.READ):
                error_msg = f"User {user_id} lacks permission to retrieve archive"
                self._log_audit('retrieve_archive', 'failure',
                              {'archive_id': archive_id}, error=error_msg)
                self._log_archive_access(archive_id, user_id, 'retrieve', 'denied')
                raise PermissionError(error_msg)
        
        # Decompress content
        compressed_content = row['compressed_content']
        content = gzip.decompress(compressed_content)
        
        # Create metadata
        metadata = ArchiveMetadata(
            archive_id=row['archive_id'],
            project_id=row['project_id'],
            document_name=row['document_name'],
            format=row['format'],
            created_at=row['created_at'],
            created_by=row['created_by'],
            content_hash=row['content_hash'],
            signature=row['signature'],
            size_bytes=row['size_bytes'],
            compression=row['compression'],
            tags=json.loads(row['tags']),
            description=row['description']
        )
        
        # Validate signature if requested
        if validate:
            if not self.validate_archive(archive_id, content):
                self._log_audit('retrieve_archive', 'failure',
                              {'archive_id': archive_id}, error='Signature validation failed')
                self._log_archive_access(archive_id, user_id, 'retrieve', 'validation_failed')
                raise ValueError(f"Archive validation failed: {archive_id}")
        
        # Log access
        self._log_archive_access(archive_id, user_id, 'retrieve', 'success')
        
        # Audit log
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self._log_audit('retrieve_archive', 'success', {
            'archive_id': archive_id,
            'project_id': project_id,
            'validated': validate
        }, duration_ms=duration_ms)
        
        return content, metadata
    
    def validate_archive(self, archive_id: str, content: Optional[bytes] = None) -> bool:
        """
        Validate an archive's signature and integrity.
        
        Args:
            archive_id: Archive ID
            content: Optional content to validate (if None, fetches from DB)
            
        Returns:
            True if valid, False otherwise
        """
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM archives WHERE archive_id = ?', (archive_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        # Get content if not provided
        if content is None:
            compressed_content = row['compressed_content']
            content = gzip.decompress(compressed_content)
        
        # Verify content hash
        content_hash = hashlib.sha256(content).hexdigest()
        if content_hash != row['content_hash']:
            return False
        
        # Verify signature
        signature_data = {
            'archive_id': row['archive_id'],
            'project_id': row['project_id'],
            'content_hash': row['content_hash'],
            'created_at': row['created_at'],
            'format': row['format']
        }
        
        expected_signature = self._sign_data(signature_data)
        return hmac.compare_digest(row['signature'], expected_signature)
    
    def list_archives(self, project_id: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     format: Optional[ArchiveFormat] = None,
                     limit: int = 100) -> List[ArchiveMetadata]:
        """
        List archives with optional filtering.
        
        Args:
            project_id: Optional project ID filter
            tags: Optional tag filter
            format: Optional format filter
            limit: Maximum number of results
            
        Returns:
            List of archive metadata
        """
        cursor = self.db.conn.cursor()
        
        query = 'SELECT * FROM archives WHERE 1=1'
        params = []
        
        if project_id:
            query += ' AND project_id = ?'
            params.append(project_id)
        
        if format:
            query += ' AND format = ?'
            params.append(format.value)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        archives = []
        for row in cursor.fetchall():
            # Filter by tags if specified
            if tags:
                archive_tags = json.loads(row['tags'])
                if not any(tag in archive_tags for tag in tags):
                    continue
            
            archives.append(ArchiveMetadata(
                archive_id=row['archive_id'],
                project_id=row['project_id'],
                document_name=row['document_name'],
                format=row['format'],
                created_at=row['created_at'],
                created_by=row['created_by'],
                content_hash=row['content_hash'],
                signature=row['signature'],
                size_bytes=row['size_bytes'],
                compression=row['compression'],
                tags=json.loads(row['tags']),
                description=row['description']
            ))
        
        return archives
    
    def delete_archive(self, archive_id: str, user_id: str) -> None:
        """
        Delete an archive (admin/owner only).
        
        Args:
            archive_id: Archive ID
            user_id: User ID requesting deletion
        """
        # Get project ID for permission check
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT project_id FROM archives WHERE archive_id = ?', (archive_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Archive not found: {archive_id}")
        
        project_id = row['project_id']
        
        # Check permissions
        if self.membership_manager:
            from accudoc.membership import Permission
            if not self.membership_manager.check_permission(user_id, project_id, Permission.DELETE):
                error_msg = f"User {user_id} lacks permission to delete archive"
                self._log_audit('delete_archive', 'failure',
                              {'archive_id': archive_id}, error=error_msg)
                raise PermissionError(error_msg)
        
        # Delete archive
        cursor.execute('DELETE FROM archives WHERE archive_id = ?', (archive_id,))
        self.db.conn.commit()
        
        # Log access
        self._log_archive_access(archive_id, user_id, 'delete', 'success')
        
        # Audit log
        self._log_audit('delete_archive', 'success', {
            'archive_id': archive_id,
            'project_id': project_id
        })
    
    def get_archive_statistics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get archive statistics.
        
        Args:
            project_id: Optional project ID filter
            
        Returns:
            Statistics dictionary
        """
        cursor = self.db.conn.cursor()
        
        query = 'SELECT * FROM archives'
        params = []
        if project_id:
            query += ' WHERE project_id = ?'
            params.append(project_id)
        
        cursor.execute(query, params)
        archives = cursor.fetchall()
        
        total_size = sum(row['size_bytes'] for row in archives)
        total_compressed = sum(len(row['compressed_content']) for row in archives)
        
        formats = {}
        for row in archives:
            fmt = row['format']
            formats[fmt] = formats.get(fmt, 0) + 1
        
        return {
            'total_archives': len(archives),
            'total_size_bytes': total_size,
            'total_compressed_bytes': total_compressed,
            'compression_ratio': total_compressed / total_size if total_size > 0 else 0,
            'by_format': formats,
            'oldest_archive': archives[-1]['created_at'] if archives else None,
            'newest_archive': archives[0]['created_at'] if archives else None
        }
    
    def _generate_archive_id(self, project_id: str, content_hash: str) -> str:
        """Generate unique archive ID."""
        data = f"{project_id}:{content_hash}:{datetime.now().isoformat()}".encode()
        hash_val = hashlib.sha256(data).hexdigest()[:16]
        return f"arch_{hash_val}"
    
    def _sign_data(self, data: Dict[str, Any]) -> str:
        """Create HMAC signature for data."""
        data_str = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            self.signing_key,
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _log_archive_access(self, archive_id: str, user_id: str,
                           operation: str, status: str) -> None:
        """Log archive access."""
        cursor = self.db.conn.cursor()
        cursor.execute('''
            INSERT INTO archive_access_log
            (archive_id, user_id, accessed_at, operation, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (archive_id, user_id, datetime.now().isoformat(), operation, status))
        self.db.conn.commit()
    
    def _log_audit(self, operation: str, status: str,
                  details: Optional[Dict] = None,
                  duration_ms: Optional[float] = None,
                  error: Optional[str] = None) -> None:
        """Log to audit trail if available."""
        if self.audit_logger:
            self.audit_logger.log_operation(
                operation=operation,
                status=status,
                details=details,
                duration_ms=duration_ms,
                error=error
            )
