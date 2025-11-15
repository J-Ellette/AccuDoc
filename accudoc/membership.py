"""
Membership and access control system for AccuDoc collaborative features.

Provides user management, role-based access control, and team management.
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class Role(Enum):
    """User roles for access control."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Permission(Enum):
    """Granular permissions."""
    READ = "read"
    WRITE = "write"
    COMMENT = "comment"
    MANAGE_USERS = "manage_users"
    MANAGE_SESSIONS = "manage_sessions"
    DELETE = "delete"


# Role permissions mapping
ROLE_PERMISSIONS = {
    Role.OWNER: [Permission.READ, Permission.WRITE, Permission.COMMENT, 
                 Permission.MANAGE_USERS, Permission.MANAGE_SESSIONS, Permission.DELETE],
    Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.COMMENT, 
                 Permission.MANAGE_USERS, Permission.MANAGE_SESSIONS],
    Role.EDITOR: [Permission.READ, Permission.WRITE, Permission.COMMENT],
    Role.VIEWER: [Permission.READ, Permission.COMMENT],
}


@dataclass
class User:
    """Represents a user in the system."""
    user_id: str
    username: str
    email: str
    role: Role
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True


@dataclass
class Team:
    """Represents a team/organization."""
    team_id: str
    name: str
    created_at: str
    owner_id: str
    description: Optional[str] = None


class MembershipManager:
    """Manages users, teams, and access control."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize membership manager.
        
        Args:
            db_path: Path to database file (default: ~/.accudoc/membership.db)
        """
        if db_path is None:
            db_path = Path.home() / '.accudoc' / 'membership.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Teams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (owner_id) REFERENCES users(user_id)
            )
        ''')
        
        # Team members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_members (
                team_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                PRIMARY KEY (team_id, user_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Project access control table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_access (
                project_id TEXT NOT NULL,
                user_id TEXT,
                team_id TEXT,
                role TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                granted_by TEXT NOT NULL,
                CHECK ((user_id IS NOT NULL AND team_id IS NULL) OR 
                       (user_id IS NULL AND team_id IS NOT NULL)),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        ''')
        
        # API tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_tokens (
                token_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                name TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                last_used TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.conn.commit()
    
    def create_user(self, username: str, email: str, password: str, 
                   role: Role = Role.VIEWER) -> User:
        """
        Create a new user.
        
        Args:
            username: Unique username
            email: User email
            password: User password (will be hashed)
            role: User role (default: VIEWER)
        
        Returns:
            Created User object
        """
        user_id = secrets.token_urlsafe(16)
        password_hash = self._hash_password(password)
        created_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, email, password_hash, role.value, created_at))
        self.conn.commit()
        
        return User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            created_at=created_at
        )
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            username: Username or email
            password: User password
        
        Returns:
            User object if authentication succeeds, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM users 
            WHERE (username = ? OR email = ?) AND is_active = 1
        ''', (username, username))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        password_hash = self._hash_password(password)
        if row['password_hash'] != password_hash:
            return None
        
        # Update last login
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE user_id = ?
        ''', (datetime.now().isoformat(), row['user_id']))
        self.conn.commit()
        
        return User(
            user_id=row['user_id'],
            username=row['username'],
            email=row['email'],
            role=Role(row['role']),
            created_at=row['created_at'],
            last_login=row['last_login'],
            is_active=bool(row['is_active'])
        )
    
    def create_team(self, name: str, owner_id: str, 
                   description: Optional[str] = None) -> Team:
        """
        Create a new team.
        
        Args:
            name: Team name
            owner_id: User ID of the team owner
            description: Optional team description
        
        Returns:
            Created Team object
        """
        team_id = secrets.token_urlsafe(16)
        created_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO teams (team_id, name, owner_id, created_at, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (team_id, name, owner_id, created_at, description))
        
        # Add owner as team member
        cursor.execute('''
            INSERT INTO team_members (team_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
        ''', (team_id, owner_id, Role.OWNER.value, created_at))
        
        self.conn.commit()
        
        return Team(
            team_id=team_id,
            name=name,
            created_at=created_at,
            owner_id=owner_id,
            description=description
        )
    
    def add_team_member(self, team_id: str, user_id: str, 
                       role: Role = Role.VIEWER) -> None:
        """
        Add a user to a team.
        
        Args:
            team_id: Team ID
            user_id: User ID
            role: User role in the team
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO team_members (team_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
        ''', (team_id, user_id, role.value, datetime.now().isoformat()))
        self.conn.commit()
    
    def grant_project_access(self, project_id: str, granted_by: str,
                            user_id: Optional[str] = None,
                            team_id: Optional[str] = None,
                            role: Role = Role.VIEWER) -> None:
        """
        Grant access to a project.
        
        Args:
            project_id: Project ID
            granted_by: User ID granting access
            user_id: User ID to grant access to (mutually exclusive with team_id)
            team_id: Team ID to grant access to (mutually exclusive with user_id)
            role: Access role
        """
        if not user_id and not team_id:
            raise ValueError("Either user_id or team_id must be provided")
        if user_id and team_id:
            raise ValueError("Cannot grant access to both user and team simultaneously")
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO project_access 
            (project_id, user_id, team_id, role, granted_at, granted_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_id, user_id, team_id, role.value, 
              datetime.now().isoformat(), granted_by))
        self.conn.commit()
    
    def check_permission(self, user_id: str, project_id: str, 
                        permission: Permission) -> bool:
        """
        Check if a user has a specific permission for a project.
        
        Args:
            user_id: User ID
            project_id: Project ID
            permission: Permission to check
        
        Returns:
            True if user has permission, False otherwise
        """
        cursor = self.conn.cursor()
        
        # Check direct user access
        cursor.execute('''
            SELECT role FROM project_access 
            WHERE project_id = ? AND user_id = ?
        ''', (project_id, user_id))
        
        row = cursor.fetchone()
        if row:
            user_role = Role(row['role'])
            if permission in ROLE_PERMISSIONS[user_role]:
                return True
        
        # Check team access
        cursor.execute('''
            SELECT pa.role FROM project_access pa
            JOIN team_members tm ON pa.team_id = tm.team_id
            WHERE pa.project_id = ? AND tm.user_id = ?
        ''', (project_id, user_id))
        
        for row in cursor.fetchall():
            team_role = Role(row['role'])
            if permission in ROLE_PERMISSIONS[team_role]:
                return True
        
        return False
    
    def create_api_token(self, user_id: str, name: Optional[str] = None,
                        expires_in_days: Optional[int] = None) -> str:
        """
        Create an API token for a user.
        
        Args:
            user_id: User ID
            name: Optional token name
            expires_in_days: Optional expiration in days
        
        Returns:
            Generated API token
        """
        token = secrets.token_urlsafe(32)
        token_id = secrets.token_urlsafe(16)
        token_hash = self._hash_token(token)
        created_at = datetime.now().isoformat()
        
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO api_tokens (token_id, user_id, token_hash, name, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (token_id, user_id, token_hash, name, created_at, expires_at))
        self.conn.commit()
        
        return token
    
    def verify_api_token(self, token: str) -> Optional[str]:
        """
        Verify an API token and return user ID.
        
        Args:
            token: API token
        
        Returns:
            User ID if token is valid, None otherwise
        """
        token_hash = self._hash_token(token)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, expires_at FROM api_tokens 
            WHERE token_hash = ?
        ''', (token_hash,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check expiration
        if row['expires_at']:
            expires_at = datetime.fromisoformat(row['expires_at'])
            if datetime.now() > expires_at:
                return None
        
        # Update last used
        cursor.execute('''
            UPDATE api_tokens SET last_used = ? WHERE token_hash = ?
        ''', (datetime.now().isoformat(), token_hash))
        self.conn.commit()
        
        return row['user_id']
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return User(
            user_id=row['user_id'],
            username=row['username'],
            email=row['email'],
            role=Role(row['role']),
            created_at=row['created_at'],
            last_login=row['last_login'],
            is_active=bool(row['is_active'])
        )
    
    def get_project_members(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all members with access to a project.
        
        Args:
            project_id: Project ID
        
        Returns:
            List of member information
        """
        cursor = self.conn.cursor()
        members = []
        
        # Get direct user access
        cursor.execute('''
            SELECT u.user_id, u.username, u.email, pa.role, pa.granted_at
            FROM project_access pa
            JOIN users u ON pa.user_id = u.user_id
            WHERE pa.project_id = ?
        ''', (project_id,))
        
        for row in cursor.fetchall():
            members.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'email': row['email'],
                'role': row['role'],
                'granted_at': row['granted_at'],
                'access_type': 'direct'
            })
        
        return members
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token using SHA-256."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
