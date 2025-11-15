"""
Collaborative session management for AccuDoc.

Manages real-time collaborative editing sessions, including session lifecycle,
participant tracking, and operation synchronization.
"""

import sqlite3
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from .crdt import CRDTDocument, Operation, OperationType
from .audit import AuditLogger


class SessionStatus(Enum):
    """Session status values."""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


@dataclass
class Participant:
    """Represents a participant in a collaborative session."""
    user_id: str
    username: str
    joined_at: str
    last_active: str
    cursor_position: int = 0
    is_active: bool = True


@dataclass
class CollaborativeSession:
    """Represents a collaborative editing session."""
    session_id: str
    project_id: str
    document_path: str
    created_by: str
    created_at: str
    status: SessionStatus
    participants: List[Participant]
    last_activity: str


class CollaborationManager:
    """Manages collaborative editing sessions."""
    
    def __init__(self, db_path: Optional[Path] = None, 
                 audit_logger: Optional[AuditLogger] = None):
        """
        Initialize collaboration manager.
        
        Args:
            db_path: Path to database file (default: ~/.accudoc/collaboration.db)
            audit_logger: Optional audit logger for activity tracking
        """
        if db_path is None:
            db_path = Path.home() / '.accudoc' / 'collaboration.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.audit_logger = audit_logger or AuditLogger()
        self.conn = None
        self.active_documents: Dict[str, CRDTDocument] = {}
        
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                document_path TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                closed_at TEXT,
                status TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Session participants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_participants (
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                left_at TEXT,
                last_active TEXT,
                cursor_position INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                PRIMARY KEY (session_id, user_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # Session operations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_operations (
                operation_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                op_type TEXT NOT NULL,
                position INTEGER NOT NULL,
                content TEXT,
                length INTEGER,
                applied BOOLEAN DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_comments (
                comment_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                position INTEGER,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # Suggestions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_suggestions (
                suggestion_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                position INTEGER NOT NULL,
                original_text TEXT,
                suggested_text TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                reviewed_by TEXT,
                reviewed_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        self.conn.commit()
    
    def create_session(self, project_id: str, document_path: str, 
                      created_by: str, initial_content: str = "") -> CollaborativeSession:
        """
        Create a new collaborative session.
        
        Args:
            project_id: Project identifier
            document_path: Path to document being edited
            created_by: User ID creating the session
            initial_content: Initial document content
        
        Returns:
            Created CollaborativeSession object
        """
        session_id = secrets.token_urlsafe(16)
        created_at = datetime.now().isoformat()
        
        # Create CRDT document
        doc_id = f"{session_id}:{document_path}"
        crdt_doc = CRDTDocument(doc_id, initial_content)
        self.active_documents[session_id] = crdt_doc
        
        # Store session in database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (session_id, project_id, document_path, 
                                 created_by, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, project_id, document_path, created_by, 
              created_at, SessionStatus.ACTIVE.value))
        
        self.conn.commit()
        
        # Log audit event
        self.audit_logger.log_operation(
            operation='create_collaborative_session',
            status='success',
            details={
                'session_id': session_id,
                'project_id': project_id,
                'document_path': document_path,
                'created_by': created_by
            }
        )
        
        return CollaborativeSession(
            session_id=session_id,
            project_id=project_id,
            document_path=document_path,
            created_by=created_by,
            created_at=created_at,
            status=SessionStatus.ACTIVE,
            participants=[],
            last_activity=created_at
        )
    
    def join_session(self, session_id: str, user_id: str, 
                    username: str) -> bool:
        """
        Add a participant to a session.
        
        Args:
            session_id: Session ID
            user_id: User ID joining
            username: Username
        
        Returns:
            True if joined successfully
        """
        joined_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO session_participants 
            (session_id, user_id, username, joined_at, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, username, joined_at, joined_at))
        
        self.conn.commit()
        
        # Log audit event
        self.audit_logger.log_operation(
            operation='join_collaborative_session',
            status='success',
            details={
                'session_id': session_id,
                'user_id': user_id,
                'username': username
            }
        )
        
        return True
    
    def leave_session(self, session_id: str, user_id: str) -> bool:
        """
        Remove a participant from a session.
        
        Args:
            session_id: Session ID
            user_id: User ID leaving
        
        Returns:
            True if left successfully
        """
        left_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE session_participants 
            SET left_at = ?, is_active = 0
            WHERE session_id = ? AND user_id = ?
        ''', (left_at, session_id, user_id))
        
        self.conn.commit()
        
        # Log audit event
        self.audit_logger.log_operation(
            operation='leave_collaborative_session',
            status='success',
            details={
                'session_id': session_id,
                'user_id': user_id
            }
        )
        
        return True
    
    def apply_operation(self, session_id: str, user_id: str, 
                       op_type: OperationType, position: int,
                       content: str = "", length: int = 0) -> Optional[Operation]:
        """
        Apply an edit operation to a session.
        
        Args:
            session_id: Session ID
            user_id: User performing operation
            op_type: Operation type
            position: Position in document
            content: Content to insert/replace
            length: Length to delete/replace
        
        Returns:
            Applied Operation or None if failed
        """
        # Get or create CRDT document
        if session_id not in self.active_documents:
            # Load from database
            self._load_session_document(session_id)
        
        doc = self.active_documents.get(session_id)
        if not doc:
            return None
        
        # Create and apply operation
        operation = doc.create_operation(user_id, op_type, position, content, length)
        
        if not doc.apply_operation(operation):
            return None
        
        # Store operation in database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO session_operations 
            (operation_id, session_id, user_id, timestamp, op_type, 
             position, content, length, applied)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (operation.op_id, session_id, user_id, operation.timestamp,
              operation.op_type.value, position, content, length))
        
        # Update participant activity
        cursor.execute('''
            UPDATE session_participants 
            SET last_active = ?, cursor_position = ?
            WHERE session_id = ? AND user_id = ?
        ''', (datetime.now().isoformat(), position, session_id, user_id))
        
        self.conn.commit()
        
        # Log audit event
        self.audit_logger.log_operation(
            operation='apply_collaborative_edit',
            status='success',
            details={
                'session_id': session_id,
                'user_id': user_id,
                'op_type': op_type.value,
                'position': position
            }
        )
        
        return operation
    
    def add_comment(self, session_id: str, user_id: str, username: str,
                   content: str, position: Optional[int] = None) -> str:
        """
        Add a comment to a session.
        
        Args:
            session_id: Session ID
            user_id: User adding comment
            username: Username
            content: Comment content
            position: Optional position in document
        
        Returns:
            Comment ID
        """
        comment_id = secrets.token_urlsafe(16)
        created_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO session_comments 
            (comment_id, session_id, user_id, username, position, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (comment_id, session_id, user_id, username, position, content, created_at))
        
        self.conn.commit()
        
        # Log audit event
        self.audit_logger.log_operation(
            operation='add_collaborative_comment',
            status='success',
            details={
                'session_id': session_id,
                'user_id': user_id,
                'comment_id': comment_id
            }
        )
        
        return comment_id
    
    def add_suggestion(self, session_id: str, user_id: str, username: str,
                      position: int, suggested_text: str, 
                      original_text: Optional[str] = None,
                      reason: Optional[str] = None) -> str:
        """
        Add a change suggestion to a session.
        
        Args:
            session_id: Session ID
            user_id: User making suggestion
            username: Username
            position: Position in document
            suggested_text: Suggested text
            original_text: Original text to replace
            reason: Reason for suggestion
        
        Returns:
            Suggestion ID
        """
        suggestion_id = secrets.token_urlsafe(16)
        created_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO session_suggestions 
            (suggestion_id, session_id, user_id, username, position, 
             original_text, suggested_text, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (suggestion_id, session_id, user_id, username, position,
              original_text, suggested_text, reason, created_at))
        
        self.conn.commit()
        
        # Log audit event
        self.audit_logger.log_operation(
            operation='add_collaborative_suggestion',
            status='success',
            details={
                'session_id': session_id,
                'user_id': user_id,
                'suggestion_id': suggestion_id
            }
        )
        
        return suggestion_id
    
    def review_suggestion(self, suggestion_id: str, reviewed_by: str,
                         accepted: bool) -> bool:
        """
        Review and accept/reject a suggestion.
        
        Args:
            suggestion_id: Suggestion ID
            reviewed_by: User ID reviewing
            accepted: Whether suggestion is accepted
        
        Returns:
            True if reviewed successfully
        """
        reviewed_at = datetime.now().isoformat()
        status = 'accepted' if accepted else 'rejected'
        
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE session_suggestions 
            SET status = ?, reviewed_by = ?, reviewed_at = ?
            WHERE suggestion_id = ?
        ''', (status, reviewed_by, reviewed_at, suggestion_id))
        
        self.conn.commit()
        
        # If accepted, apply the suggestion
        if accepted:
            cursor.execute('''
                SELECT session_id, position, original_text, suggested_text
                FROM session_suggestions WHERE suggestion_id = ?
            ''', (suggestion_id,))
            
            row = cursor.fetchone()
            if row:
                session_id = row['session_id']
                position = row['position']
                original_text = row['original_text'] or ""
                suggested_text = row['suggested_text']
                
                self.apply_operation(
                    session_id, reviewed_by, OperationType.REPLACE,
                    position, suggested_text, len(original_text)
                )
        
        # Log audit event
        self.audit_logger.log_operation(
            operation='review_collaborative_suggestion',
            status='success',
            details={
                'suggestion_id': suggestion_id,
                'reviewed_by': reviewed_by,
                'accepted': accepted
            }
        )
        
        return True
    
    def get_session(self, session_id: str) -> Optional[CollaborativeSession]:
        """Get session details."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Get participants
        participants = self.get_session_participants(session_id)
        
        return CollaborativeSession(
            session_id=row['session_id'],
            project_id=row['project_id'],
            document_path=row['document_path'],
            created_by=row['created_by'],
            created_at=row['created_at'],
            status=SessionStatus(row['status']),
            participants=participants,
            last_activity=row['created_at']  # Simplified
        )
    
    def get_session_participants(self, session_id: str) -> List[Participant]:
        """Get list of session participants."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM session_participants 
            WHERE session_id = ? AND is_active = 1
        ''', (session_id,))
        
        participants = []
        for row in cursor.fetchall():
            participants.append(Participant(
                user_id=row['user_id'],
                username=row['username'],
                joined_at=row['joined_at'],
                last_active=row['last_active'],
                cursor_position=row['cursor_position'],
                is_active=bool(row['is_active'])
            ))
        
        return participants
    
    def get_session_content(self, session_id: str) -> Optional[str]:
        """Get current document content for a session."""
        if session_id not in self.active_documents:
            self._load_session_document(session_id)
        
        doc = self.active_documents.get(session_id)
        return doc.content if doc else None
    
    def get_session_comments(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all comments for a session."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM session_comments 
            WHERE session_id = ? AND resolved = 0
            ORDER BY created_at DESC
        ''', (session_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_session_suggestions(self, session_id: str, 
                               status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get suggestions for a session."""
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM session_suggestions 
                WHERE session_id = ? AND status = ?
                ORDER BY created_at DESC
            ''', (session_id, status))
        else:
            cursor.execute('''
                SELECT * FROM session_suggestions 
                WHERE session_id = ?
                ORDER BY created_at DESC
            ''', (session_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close_session(self, session_id: str) -> bool:
        """Close a collaborative session."""
        closed_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE sessions SET status = ?, closed_at = ?
            WHERE session_id = ?
        ''', (SessionStatus.CLOSED.value, closed_at, session_id))
        
        self.conn.commit()
        
        # Remove from active documents
        if session_id in self.active_documents:
            del self.active_documents[session_id]
        
        # Log audit event
        self.audit_logger.log_operation(
            operation='close_collaborative_session',
            status='success',
            details={'session_id': session_id}
        )
        
        return True
    
    def _load_session_document(self, session_id: str) -> None:
        """Load session document from database."""
        cursor = self.conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT document_path FROM sessions WHERE session_id = ?
        ''', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            return
        
        # Create CRDT document
        doc_id = f"{session_id}:{row['document_path']}"
        doc = CRDTDocument(doc_id)
        
        # Load and apply operations
        cursor.execute('''
            SELECT * FROM session_operations 
            WHERE session_id = ? AND applied = 1
            ORDER BY timestamp
        ''', (session_id,))
        
        for op_row in cursor.fetchall():
            operation = Operation(
                op_id=op_row['operation_id'],
                user_id=op_row['user_id'],
                timestamp=op_row['timestamp'],
                op_type=OperationType(op_row['op_type']),
                position=op_row['position'],
                content=op_row['content'] or '',
                length=op_row['length'] or 0
            )
            doc.apply_operation(operation)
        
        self.active_documents[session_id] = doc
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
