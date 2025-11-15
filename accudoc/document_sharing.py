"""
Granular Document Sharing Controls for AccuDoc.

Enables selective sharing of documentation sections with external parties
via secure exports, expiring access, watermarking, and download tracking.
"""

import json
import sqlite3
import hashlib
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import base64


from accudoc.membership import MembershipManager, Permission


@dataclass
class SharedDocument:
    """Represents a shared documentation section."""
    share_id: str
    document_path: str
    section_id: Optional[str]
    section_title: Optional[str]
    content: str
    shared_by: str
    shared_with: Optional[str]  # email or user_id
    created_at: str
    expires_at: Optional[str] = None
    access_token: Optional[str] = None
    watermark: bool = False
    download_limit: Optional[int] = None
    download_count: int = 0
    is_active: bool = True


@dataclass
class ShareAccess:
    """Represents an access event for a shared document."""
    access_id: str
    share_id: str
    accessed_at: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action: str = 'view'  # view, download, export


class DocumentSharingManager:
    """Manages secure document sharing with granular controls."""
    
    def __init__(self, db_path: Optional[Path] = None,
                 membership_manager: Optional[MembershipManager] = None):
        """
        Initialize document sharing manager.
        
        Args:
            db_path: Path to database file
            membership_manager: Optional membership manager for access control
        """
        if db_path is None:
            db_path = Path.home() / '.accudoc' / 'document_sharing.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.membership_manager = membership_manager
        
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Shared documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_documents (
                share_id TEXT PRIMARY KEY,
                document_path TEXT NOT NULL,
                section_id TEXT,
                section_title TEXT,
                content TEXT NOT NULL,
                shared_by TEXT NOT NULL,
                shared_with TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                access_token TEXT NOT NULL UNIQUE,
                watermark BOOLEAN DEFAULT 0,
                download_limit INTEGER,
                download_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Access log table for tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS share_access_log (
                access_id TEXT PRIMARY KEY,
                share_id TEXT NOT NULL,
                accessed_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                action TEXT DEFAULT 'view',
                FOREIGN KEY (share_id) REFERENCES shared_documents(share_id)
            )
        ''')
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_token ON shared_documents(access_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_user ON shared_documents(shared_by)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_share ON share_access_log(share_id)')
        
        self.conn.commit()
    
    def share_document_section(self, document_path: str, content: str,
                               shared_by: str,
                               section_id: Optional[str] = None,
                               section_title: Optional[str] = None,
                               shared_with: Optional[str] = None,
                               expires_in_days: Optional[int] = None,
                               watermark: bool = False,
                               download_limit: Optional[int] = None,
                               organization_id: Optional[str] = None) -> SharedDocument:
        """
        Share a document section with external parties.
        
        Args:
            document_path: Path to original document
            content: Content to share
            shared_by: User ID sharing the document
            section_id: Optional section identifier
            section_title: Optional section title
            shared_with: Optional email or user_id of recipient
            expires_in_days: Optional expiration in days
            watermark: Whether to add watermark
            download_limit: Optional download limit
            organization_id: Organization context
            
        Returns:
            Created SharedDocument
        """
        # Check permission if needed
        if self.membership_manager and shared_by and organization_id:
            if not self.membership_manager.check_permission(shared_by, organization_id, Permission.WRITE):
                raise PermissionError("User does not have permission to share documents")
        
        share_id = f"share_{secrets.token_urlsafe(12)}"
        access_token = secrets.token_urlsafe(32)
        created_at = datetime.now().isoformat()
        
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        # Apply watermark if requested
        if watermark:
            content = self._apply_watermark(content, shared_by, created_at)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO shared_documents 
            (share_id, document_path, section_id, section_title, content, shared_by,
             shared_with, created_at, expires_at, access_token, watermark,
             download_limit, download_count, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            share_id,
            document_path,
            section_id,
            section_title,
            content,
            shared_by,
            shared_with,
            created_at,
            expires_at,
            access_token,
            watermark,
            download_limit,
            0,
            True
        ))
        self.conn.commit()
        
        return SharedDocument(
            share_id=share_id,
            document_path=document_path,
            section_id=section_id,
            section_title=section_title,
            content=content,
            shared_by=shared_by,
            shared_with=shared_with,
            created_at=created_at,
            expires_at=expires_at,
            access_token=access_token,
            watermark=watermark,
            download_limit=download_limit,
            download_count=0,
            is_active=True
        )
    
    def _apply_watermark(self, content: str, shared_by: str, timestamp: str) -> str:
        """
        Apply watermark to document content.
        
        Args:
            content: Original content
            shared_by: User who shared
            timestamp: When shared
            
        Returns:
            Content with watermark
        """
        watermark = f"\n\n---\n*This document was shared by {shared_by} on {timestamp}*\n"
        watermark += "*Confidential - Do not redistribute*\n"
        return content + watermark
    
    def get_shared_document(self, access_token: str,
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None) -> Optional[SharedDocument]:
        """
        Access a shared document using access token.
        
        Args:
            access_token: Access token
            ip_address: Optional IP address for logging
            user_agent: Optional user agent for logging
            
        Returns:
            SharedDocument if valid, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM shared_documents WHERE access_token = ? AND is_active = 1
        ''', (access_token,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Check expiration
        if row['expires_at']:
            expires_at = datetime.fromisoformat(row['expires_at'])
            if datetime.now() > expires_at:
                # Deactivate expired share
                cursor.execute('UPDATE shared_documents SET is_active = 0 WHERE share_id = ?',
                             (row['share_id'],))
                self.conn.commit()
                return None
        
        # Check download limit
        if row['download_limit'] and row['download_count'] >= row['download_limit']:
            return None
        
        # Log access
        self._log_access(row['share_id'], 'view', ip_address, user_agent)
        
        return SharedDocument(
            share_id=row['share_id'],
            document_path=row['document_path'],
            section_id=row['section_id'],
            section_title=row['section_title'],
            content=row['content'],
            shared_by=row['shared_by'],
            shared_with=row['shared_with'],
            created_at=row['created_at'],
            expires_at=row['expires_at'],
            access_token=row['access_token'],
            watermark=bool(row['watermark']),
            download_limit=row['download_limit'],
            download_count=row['download_count'],
            is_active=bool(row['is_active'])
        )
    
    def record_download(self, share_id: str,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None) -> bool:
        """
        Record a download of a shared document.
        
        Args:
            share_id: Share ID
            ip_address: Optional IP address
            user_agent: Optional user agent
            
        Returns:
            True if download allowed, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM shared_documents WHERE share_id = ?', (share_id,))
        row = cursor.fetchone()
        
        if not row or not row['is_active']:
            return False
        
        # Check download limit
        if row['download_limit'] and row['download_count'] >= row['download_limit']:
            return False
        
        # Increment download count
        cursor.execute('''
            UPDATE shared_documents SET download_count = download_count + 1
            WHERE share_id = ?
        ''', (share_id,))
        self.conn.commit()
        
        # Log download
        self._log_access(share_id, 'download', ip_address, user_agent)
        
        return True
    
    def _log_access(self, share_id: str, action: str,
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None) -> None:
        """Log access to a shared document."""
        access_id = f"access_{secrets.token_urlsafe(12)}"
        accessed_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO share_access_log 
            (access_id, share_id, accessed_at, ip_address, user_agent, action)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (access_id, share_id, accessed_at, ip_address, user_agent, action))
        self.conn.commit()
    
    def revoke_share(self, share_id: str, user_id: str) -> bool:
        """
        Revoke a shared document.
        
        Args:
            share_id: Share ID to revoke
            user_id: User requesting revocation
            
        Returns:
            True if revoked successfully
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT shared_by FROM shared_documents WHERE share_id = ?
        ''', (share_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        # Only allow creator to revoke
        if row['shared_by'] != user_id:
            raise PermissionError("Only the creator can revoke this share")
        
        cursor.execute('''
            UPDATE shared_documents SET is_active = 0 WHERE share_id = ?
        ''', (share_id,))
        self.conn.commit()
        
        return True
    
    def get_access_log(self, share_id: str) -> List[ShareAccess]:
        """
        Get access log for a shared document.
        
        Args:
            share_id: Share ID
            
        Returns:
            List of access events
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM share_access_log WHERE share_id = ?
            ORDER BY accessed_at DESC
        ''', (share_id,))
        
        accesses = []
        for row in cursor.fetchall():
            accesses.append(ShareAccess(
                access_id=row['access_id'],
                share_id=row['share_id'],
                accessed_at=row['accessed_at'],
                ip_address=row['ip_address'],
                user_agent=row['user_agent'],
                action=row['action']
            ))
        
        return accesses
    
    def get_user_shares(self, user_id: str, active_only: bool = True) -> List[SharedDocument]:
        """
        Get all shares created by a user.
        
        Args:
            user_id: User ID
            active_only: Only return active shares
            
        Returns:
            List of shared documents
        """
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM shared_documents WHERE shared_by = ?'
        params = [user_id]
        
        if active_only:
            query += ' AND is_active = 1'
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        
        shares = []
        for row in cursor.fetchall():
            shares.append(SharedDocument(
                share_id=row['share_id'],
                document_path=row['document_path'],
                section_id=row['section_id'],
                section_title=row['section_title'],
                content=row['content'],
                shared_by=row['shared_by'],
                shared_with=row['shared_with'],
                created_at=row['created_at'],
                expires_at=row['expires_at'],
                access_token=row['access_token'],
                watermark=bool(row['watermark']),
                download_limit=row['download_limit'],
                download_count=row['download_count'],
                is_active=bool(row['is_active'])
            ))
        
        return shares
    
    def generate_share_report(self, user_id: str) -> str:
        """
        Generate a report of all shares for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted report
        """
        shares = self.get_user_shares(user_id, active_only=False)
        
        lines = []
        lines.append("# Document Sharing Report\n")
        lines.append(f"**User**: {user_id}")
        lines.append(f"**Total Shares**: {len(shares)}\n")
        
        active_count = sum(1 for s in shares if s.is_active)
        expired_count = sum(1 for s in shares if not s.is_active)
        
        lines.append("## Summary\n")
        lines.append(f"- Active: {active_count}")
        lines.append(f"- Expired/Revoked: {expired_count}\n")
        
        # Active shares
        active_shares = [s for s in shares if s.is_active]
        if active_shares:
            lines.append("## Active Shares\n")
            lines.append("| Section | Shared With | Created | Expires | Downloads | Link |")
            lines.append("|---------|-------------|---------|---------|-----------|------|")
            
            for share in active_shares[:20]:
                section = share.section_title or share.section_id or "Full Document"
                shared_with = share.shared_with or "Public"
                created = share.created_at[:10]
                expires = share.expires_at[:10] if share.expires_at else "Never"
                downloads = f"{share.download_count}"
                if share.download_limit:
                    downloads += f"/{share.download_limit}"
                link = f"`{share.access_token[:16]}...`"
                
                lines.append(f"| {section} | {shared_with} | {created} | {expires} | {downloads} | {link} |")
            
            if len(active_shares) > 20:
                lines.append(f"\n*... and {len(active_shares) - 20} more*\n")
        
        return '\n'.join(lines)
    
    def export_secure(self, share_id: str, format: str = 'markdown') -> Dict[str, Any]:
        """
        Export shared document in secure format.
        
        Args:
            share_id: Share ID
            format: Export format (markdown, html, pdf)
            
        Returns:
            Export data with metadata
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM shared_documents WHERE share_id = ?', (share_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError("Share not found")
        
        content = row['content']
        
        # Format content based on requested format
        if format == 'html':
            # Basic HTML wrapping
            content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{row['section_title'] or 'Shared Document'}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
    </style>
</head>
<body>
    <pre>{content}</pre>
</body>
</html>
"""
        
        return {
            'share_id': share_id,
            'format': format,
            'content': content,
            'section_title': row['section_title'],
            'created_at': row['created_at'],
            'watermark': bool(row['watermark'])
        }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
