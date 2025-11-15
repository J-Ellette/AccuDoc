"""
Project database module for AccuDoc.

Provides SQLite database for storing scan results:
- Persistent storage of scan data
- Query scan history
- Track changes over time
- Export/import scan data
"""

import sqlite3
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import hashlib


class ProjectDatabase:
    """SQLite database for storing AccuDoc scan results."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize project database.
        
        Args:
            db_path: Path to database file (default: ~/.accudoc/projects.db)
        """
        if db_path is None:
            db_path = Path.home() / '.accudoc' / 'projects.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('accudoc.database')
        
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        cursor = self.conn.cursor()
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                repo_path TEXT NOT NULL UNIQUE,
                name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_scan_at TEXT,
                scan_count INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        
        # Scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                scanned_at TEXT NOT NULL,
                duration_seconds REAL,
                files_scanned INTEGER,
                files_changed INTEGER,
                status TEXT,
                config TEXT,
                results TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        ''')
        
        # Files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_hash TEXT,
                size_bytes INTEGER,
                language TEXT,
                loc INTEGER,
                complexity INTEGER,
                documentation_score REAL,
                metadata TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        # Comparison table for tracking changes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparisons (
                comparison_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                scan_id_from TEXT NOT NULL,
                scan_id_to TEXT NOT NULL,
                compared_at TEXT NOT NULL,
                changes TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (scan_id_from) REFERENCES scans(scan_id),
                FOREIGN KEY (scan_id_to) REFERENCES scans(scan_id)
            )
        ''')
        
        # Collaborative sessions metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collaborative_sessions (
                session_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                document_path TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                closed_at TEXT,
                status TEXT NOT NULL,
                participant_count INTEGER DEFAULT 0,
                operation_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                suggestion_count INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_project ON scans(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_scan ON files(scan_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comparisons_project ON comparisons(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_project ON collaborative_sessions(project_id)')
        
        self.conn.commit()
        self.logger.info(f"Database initialized: {self.db_path}")
    
    def _generate_id(self, prefix: str, *args) -> str:
        """
        Generate unique ID.
        
        Args:
            prefix: ID prefix
            *args: Values to hash
            
        Returns:
            Unique ID
        """
        data = ''.join(str(arg) for arg in args)
        hash_val = hashlib.md5(data.encode()).hexdigest()[:16]
        return f"{prefix}_{hash_val}"
    
    def add_project(self, repo_path: str, name: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> str:
        """
        Add or update a project.
        
        Args:
            repo_path: Path to repository
            name: Project name (default: directory name)
            metadata: Additional project metadata
            
        Returns:
            Project ID
        """
        abs_path = str(Path(repo_path).absolute())
        project_id = self._generate_id('proj', abs_path)
        
        if name is None:
            name = Path(repo_path).name
        
        now = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        
        # Check if project exists
        cursor.execute('SELECT project_id FROM projects WHERE project_id = ?', (project_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing project
            cursor.execute('''
                UPDATE projects 
                SET name = ?, updated_at = ?, metadata = ?
                WHERE project_id = ?
            ''', (name, now, json.dumps(metadata or {}), project_id))
        else:
            # Insert new project
            cursor.execute('''
                INSERT INTO projects 
                (project_id, repo_path, name, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (project_id, abs_path, name, now, now, json.dumps(metadata or {})))
        
        self.conn.commit()
        self.logger.info(f"Added/updated project: {project_id}")
        
        return project_id
    
    def add_scan(self, project_id: str, scan_data: Dict[str, Any]) -> str:
        """
        Add scan results to database.
        
        Args:
            project_id: Project ID
            scan_data: Scan results data
            
        Returns:
            Scan ID
        """
        now = datetime.now().isoformat()
        scan_id = self._generate_id('scan', project_id, now)
        
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO scans
            (scan_id, project_id, scanned_at, duration_seconds, files_scanned,
             files_changed, status, config, results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_id,
            project_id,
            now,
            scan_data.get('duration_seconds', 0),
            scan_data.get('files_scanned', 0),
            scan_data.get('files_changed', 0),
            scan_data.get('status', 'complete'),
            json.dumps(scan_data.get('config', {})),
            json.dumps(scan_data.get('results', {}))
        ))
        
        # Update project
        cursor.execute('''
            UPDATE projects
            SET last_scan_at = ?, updated_at = ?, scan_count = scan_count + 1
            WHERE project_id = ?
        ''', (now, now, project_id))
        
        # Add file data if present
        if 'files' in scan_data:
            for file_data in scan_data['files']:
                self.add_file(scan_id, file_data)
        
        self.conn.commit()
        self.logger.info(f"Added scan: {scan_id}")
        
        return scan_id
    
    def add_file(self, scan_id: str, file_data: Dict[str, Any]) -> None:
        """
        Add file data to scan.
        
        Args:
            scan_id: Scan ID
            file_data: File analysis data
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO files
            (scan_id, filepath, file_hash, size_bytes, language, loc,
             complexity, documentation_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_id,
            file_data.get('filepath', ''),
            file_data.get('hash', ''),
            file_data.get('size', 0),
            file_data.get('language', ''),
            file_data.get('loc', 0),
            file_data.get('complexity', 0),
            file_data.get('doc_score', 0.0),
            json.dumps(file_data.get('metadata', {}))
        ))
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project data or None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE project_id = ?', (project_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_project_by_path(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """
        Get project by repository path.
        
        Args:
            repo_path: Repository path
            
        Returns:
            Project data or None
        """
        abs_path = str(Path(repo_path).absolute())
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE repo_path = ?', (abs_path,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def list_projects(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Args:
            limit: Maximum number of projects to return
            
        Returns:
            List of projects
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM projects
            ORDER BY updated_at DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_scans(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get scans for a project.
        
        Args:
            project_id: Project ID
            limit: Maximum number of scans to return
            
        Returns:
            List of scans
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM scans
            WHERE project_id = ?
            ORDER BY scanned_at DESC
            LIMIT ?
        ''', (project_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_scan(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get scan by ID.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            Scan data or None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM scans WHERE scan_id = ?', (scan_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_scan_files(self, scan_id: str) -> List[Dict[str, Any]]:
        """
        Get files for a scan.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            List of file data
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM files
            WHERE scan_id = ?
            ORDER BY filepath
        ''', (scan_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def add_comparison(self, project_id: str, scan_id_from: str,
                      scan_id_to: str, changes: Dict[str, Any]) -> str:
        """
        Add comparison between two scans.
        
        Args:
            project_id: Project ID
            scan_id_from: Earlier scan ID
            scan_id_to: Later scan ID
            changes: Comparison results
            
        Returns:
            Comparison ID
        """
        now = datetime.now().isoformat()
        comparison_id = self._generate_id('cmp', project_id, scan_id_from, scan_id_to)
        
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO comparisons
            (comparison_id, project_id, scan_id_from, scan_id_to, compared_at, changes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (comparison_id, project_id, scan_id_from, scan_id_to, now, json.dumps(changes)))
        
        self.conn.commit()
        self.logger.info(f"Added comparison: {comparison_id}")
        
        return comparison_id
    
    def get_comparisons(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get comparisons for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of comparisons
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM comparisons
            WHERE project_id = ?
            ORDER BY compared_at DESC
        ''', (project_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def export_project_data(self, project_id: str, output_file: Path) -> None:
        """
        Export all project data to JSON file.
        
        Args:
            project_id: Project ID
            output_file: Output file path
        """
        project = self.get_project(project_id)
        scans = self.get_scans(project_id, limit=1000)
        comparisons = self.get_comparisons(project_id)
        
        data = {
            'project': project,
            'scans': scans,
            'comparisons': comparisons,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Exported project data to {output_file}")
    
    def add_collaborative_session(self, session_id: str, project_id: str,
                                 document_path: str, created_by: str,
                                 status: str = 'active') -> None:
        """
        Add collaborative session metadata.
        
        Args:
            session_id: Session ID
            project_id: Project ID
            document_path: Path to document
            created_by: User who created the session
            status: Session status
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO collaborative_sessions
            (session_id, project_id, document_path, created_by, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, project_id, document_path, created_by,
              datetime.now().isoformat(), status))
        self.conn.commit()
    
    def update_collaborative_session_stats(self, session_id: str,
                                          participant_count: Optional[int] = None,
                                          operation_count: Optional[int] = None,
                                          comment_count: Optional[int] = None,
                                          suggestion_count: Optional[int] = None) -> None:
        """
        Update collaborative session statistics.
        
        Args:
            session_id: Session ID
            participant_count: Number of participants
            operation_count: Number of operations
            comment_count: Number of comments
            suggestion_count: Number of suggestions
        """
        cursor = self.conn.cursor()
        updates = []
        values = []
        
        if participant_count is not None:
            updates.append('participant_count = ?')
            values.append(participant_count)
        if operation_count is not None:
            updates.append('operation_count = ?')
            values.append(operation_count)
        if comment_count is not None:
            updates.append('comment_count = ?')
            values.append(comment_count)
        if suggestion_count is not None:
            updates.append('suggestion_count = ?')
            values.append(suggestion_count)
        
        if updates:
            values.append(session_id)
            cursor.execute(f'''
                UPDATE collaborative_sessions
                SET {', '.join(updates)}
                WHERE session_id = ?
            ''', values)
            self.conn.commit()
    
    def close_collaborative_session(self, session_id: str) -> None:
        """
        Close a collaborative session.
        
        Args:
            session_id: Session ID
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE collaborative_sessions
            SET status = 'closed', closed_at = ?
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), session_id))
        self.conn.commit()
    
    def get_project_collaborative_sessions(self, project_id: str,
                                          status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get collaborative sessions for a project.
        
        Args:
            project_id: Project ID
            status: Optional status filter
            
        Returns:
            List of collaborative sessions
        """
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM collaborative_sessions
                WHERE project_id = ? AND status = ?
                ORDER BY created_at DESC
            ''', (project_id, status))
        else:
            cursor.execute('''
                SELECT * FROM collaborative_sessions
                WHERE project_id = ?
                ORDER BY created_at DESC
            ''', (project_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
