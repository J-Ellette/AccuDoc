#!/usr/bin/env python3
"""
Real-Time Collaboration Server for AccuDoc

Provides WebSocket-based real-time collaboration features including:
- Multi-user document editing
- Comment threads
- Review/approval workflows
- Slack/Teams integration
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Set, List, Optional
import websockets
import sqlite3
from pathlib import Path
import requests
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """WebSocket event types"""
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    DOCUMENT_EDIT = "document_edit"
    CURSOR_MOVE = "cursor_move"
    COMMENT_ADD = "comment_add"
    COMMENT_UPDATE = "comment_update"
    COMMENT_DELETE = "comment_delete"
    REVIEW_REQUEST = "review_request"
    REVIEW_APPROVE = "review_approve"
    REVIEW_REJECT = "review_reject"
    NOTIFICATION = "notification"

@dataclass
class User:
    """User session information"""
    id: str
    name: str
    email: str
    avatar: str = ""
    role: str = "editor"  # viewer, editor, reviewer, admin
    session_id: str = ""
    last_seen: datetime = None

@dataclass
class Comment:
    """Document comment"""
    id: str
    document_id: str
    user_id: str
    content: str
    line_start: int
    line_end: int
    resolved: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    replies: List['Comment'] = None

@dataclass
class DocumentEdit:
    """Document edit operation"""
    id: str
    document_id: str
    user_id: str
    operation: str  # insert, delete, replace
    position: int
    content: str
    timestamp: datetime = None

class CollaborationServer:
    """Real-time collaboration server"""
    
    def __init__(self, db_path: str = "collaboration.db", port: int = 8765):
        self.port = port
        self.db_path = db_path
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.documents: Dict[str, Set[str]] = {}  # document_id -> set of client_ids
        self.users: Dict[str, User] = {}
        self.cursors: Dict[str, Dict] = {}  # client_id -> cursor position
        self.init_database()
        
        # Integration settings
        self.slack_webhook = None
        self.teams_webhook = None
        
    def init_database(self):
        """Initialize SQLite database for persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                avatar TEXT,
                role TEXT DEFAULT 'editor',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                line_start INTEGER NOT NULL,
                line_end INTEGER NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                parent_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (parent_id) REFERENCES comments (id)
            )
        ''')
        
        # Document edits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_edits (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                position INTEGER NOT NULL,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                reviewer_id TEXT NOT NULL,
                status TEXT NOT NULL, -- pending, approved, rejected
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reviewer_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def register_client(self, websocket: websockets.WebSocketServerProtocol, client_id: str):
        """Register a new WebSocket client"""
        self.clients[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        
    async def unregister_client(self, client_id: str):
        """Unregister a WebSocket client"""
        if client_id in self.clients:
            del self.clients[client_id]
            
        # Remove from all documents
        for doc_id, client_set in self.documents.items():
            client_set.discard(client_id)
            
        # Remove cursor
        if client_id in self.cursors:
            del self.cursors[client_id]
            
        logger.info(f"Client {client_id} disconnected")
        
    async def join_document(self, client_id: str, document_id: str, user: User):
        """Join a client to a document session"""
        if document_id not in self.documents:
            self.documents[document_id] = set()
            
        self.documents[document_id].add(client_id)
        self.users[client_id] = user
        
        # Notify other users
        await self.broadcast_to_document(document_id, {
            "type": EventType.USER_JOIN.value,
            "user": asdict(user),
            "document_id": document_id
        }, exclude_client=client_id)
        
        logger.info(f"User {user.name} joined document {document_id}")
        
    async def leave_document(self, client_id: str, document_id: str):
        """Remove a client from a document session"""
        if document_id in self.documents:
            self.documents[document_id].discard(client_id)
            
        user = self.users.get(client_id)
        if user:
            await self.broadcast_to_document(document_id, {
                "type": EventType.USER_LEAVE.value,
                "user": asdict(user),
                "document_id": document_id
            }, exclude_client=client_id)
            
    async def handle_document_edit(self, client_id: str, data: dict):
        """Handle document edit operations"""
        document_id = data.get("document_id")
        operation = data.get("operation")
        position = data.get("position")
        content = data.get("content", "")
        
        user = self.users.get(client_id)
        if not user:
            return
            
        # Store edit in database
        edit_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO document_edits (id, document_id, user_id, operation, position, content)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (edit_id, document_id, user.id, operation, position, content))
        
        conn.commit()
        conn.close()
        
        # Broadcast edit to other users
        await self.broadcast_to_document(document_id, {
            "type": EventType.DOCUMENT_EDIT.value,
            "edit_id": edit_id,
            "document_id": document_id,
            "user": asdict(user),
            "operation": operation,
            "position": position,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, exclude_client=client_id)
        
    async def handle_cursor_move(self, client_id: str, data: dict):
        """Handle cursor movement"""
        document_id = data.get("document_id")
        position = data.get("position")
        
        self.cursors[client_id] = {
            "document_id": document_id,
            "position": position,
            "user": asdict(self.users.get(client_id, {}))
        }
        
        # Broadcast cursor position
        await self.broadcast_to_document(document_id, {
            "type": EventType.CURSOR_MOVE.value,
            "client_id": client_id,
            "position": position,
            "user": asdict(self.users.get(client_id, {}))
        }, exclude_client=client_id)
        
    async def handle_comment(self, client_id: str, data: dict):
        """Handle comment operations"""
        action = data.get("action")  # add, update, delete
        
        if action == "add":
            await self.add_comment(client_id, data)
        elif action == "update":
            await self.update_comment(client_id, data)
        elif action == "delete":
            await self.delete_comment(client_id, data)
            
    async def add_comment(self, client_id: str, data: dict):
        """Add a new comment"""
        user = self.users.get(client_id)
        if not user:
            return
            
        comment_id = str(uuid.uuid4())
        document_id = data.get("document_id")
        content = data.get("content")
        line_start = data.get("line_start")
        line_end = data.get("line_end")
        parent_id = data.get("parent_id")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comments (id, document_id, user_id, content, line_start, line_end, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (comment_id, document_id, user.id, content, line_start, line_end, parent_id))
        
        conn.commit()
        conn.close()
        
        comment_data = {
            "type": EventType.COMMENT_ADD.value,
            "comment": {
                "id": comment_id,
                "document_id": document_id,
                "user": asdict(user),
                "content": content,
                "line_start": line_start,
                "line_end": line_end,
                "parent_id": parent_id,
                "resolved": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        await self.broadcast_to_document(document_id, comment_data)
        
        # Send notification to integrations
        await self.send_notification(f"New comment by {user.name}", content)
        
    async def handle_review(self, client_id: str, data: dict):
        """Handle review operations"""
        action = data.get("action")  # request, approve, reject
        
        user = self.users.get(client_id)
        if not user:
            return
            
        document_id = data.get("document_id")
        
        if action == "request":
            review_id = str(uuid.uuid4())
            reviewer_id = data.get("reviewer_id")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO reviews (id, document_id, reviewer_id, status)
                VALUES (?, ?, ?, ?)
            ''', (review_id, document_id, reviewer_id, "pending"))
            
            conn.commit()
            conn.close()
            
            await self.broadcast_to_document(document_id, {
                "type": EventType.REVIEW_REQUEST.value,
                "review_id": review_id,
                "document_id": document_id,
                "requester": asdict(user),
                "reviewer_id": reviewer_id
            })
            
            await self.send_notification(f"Review requested by {user.name}", f"Document: {document_id}")
            
    async def broadcast_to_document(self, document_id: str, message: dict, exclude_client: str = None):
        """Broadcast message to all clients in a document"""
        if document_id not in self.documents:
            return
            
        clients = self.documents[document_id]
        if exclude_client:
            clients = clients - {exclude_client}
            
        disconnected_clients = []
        
        for client_id in clients:
            if client_id in self.clients:
                try:
                    await self.clients[client_id].send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.append(client_id)
                    
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.unregister_client(client_id)
            
    async def send_notification(self, title: str, content: str):
        """Send notifications to Slack/Teams"""
        if self.slack_webhook:
            try:
                payload = {
                    "text": f"*{title}*\n{content}",
                    "username": "AccuDoc",
                    "icon_emoji": ":memo:"
                }
                requests.post(self.slack_webhook, json=payload, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")
                
        if self.teams_webhook:
            try:
                payload = {
                    "@type": "MessageCard",
                    "@context": "http://schema.org/extensions",
                    "themeColor": "0076D7",
                    "summary": title,
                    "sections": [{
                        "activityTitle": title,
                        "activitySubtitle": "AccuDoc Collaboration",
                        "text": content
                    }]
                }
                requests.post(self.teams_webhook, json=payload, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send Teams notification: {e}")
                
    async def handle_client_message(self, websocket: websockets.WebSocketServerProtocol, client_id: str):
        """Handle messages from WebSocket clients"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    event_type = data.get("type")
                    
                    if event_type == EventType.USER_JOIN.value:
                        user_data = data.get("user", {})
                        user = User(
                            id=user_data.get("id"),
                            name=user_data.get("name"),
                            email=user_data.get("email"),
                            avatar=user_data.get("avatar", ""),
                            role=user_data.get("role", "editor"),
                            session_id=client_id
                        )
                        await self.join_document(client_id, data.get("document_id"), user)
                        
                    elif event_type == EventType.DOCUMENT_EDIT.value:
                        await self.handle_document_edit(client_id, data)
                        
                    elif event_type == EventType.CURSOR_MOVE.value:
                        await self.handle_cursor_move(client_id, data)
                        
                    elif event_type in [EventType.COMMENT_ADD.value, EventType.COMMENT_UPDATE.value, EventType.COMMENT_DELETE.value]:
                        await self.handle_comment(client_id, data)
                        
                    elif event_type in [EventType.REVIEW_REQUEST.value, EventType.REVIEW_APPROVE.value, EventType.REVIEW_REJECT.value]:
                        await self.handle_review(client_id, data)
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client {client_id}")
                except Exception as e:
                    logger.error(f"Error handling message from client {client_id}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(client_id)
            
    async def handle_client_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle new WebSocket connections"""
        client_id = str(uuid.uuid4())
        await self.register_client(websocket, client_id)
        
        # Send client ID to client
        await websocket.send(json.dumps({
            "type": "connection_established",
            "client_id": client_id
        }))
        
        await self.handle_client_message(websocket, client_id)
        
    def configure_integrations(self, slack_webhook: str = None, teams_webhook: str = None):
        """Configure Slack and Teams webhook URLs"""
        self.slack_webhook = slack_webhook
        self.teams_webhook = teams_webhook
        
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting collaboration server on port {self.port}")
        
        start_server = websockets.serve(
            self.handle_client_connection,
            "localhost",
            self.port
        )
        
        await start_server
        logger.info(f"Collaboration server running on ws://localhost:{self.port}")
        
        # Keep the server running
        await asyncio.Future()  # Run forever

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AccuDoc Collaboration Server")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket server port")
    parser.add_argument("--db", type=str, default="collaboration.db", help="Database file path")
    parser.add_argument("--slack-webhook", type=str, help="Slack webhook URL")
    parser.add_argument("--teams-webhook", type=str, help="Microsoft Teams webhook URL")
    
    args = parser.parse_args()
    
    server = CollaborationServer(db_path=args.db, port=args.port)
    
    if args.slack_webhook or args.teams_webhook:
        server.configure_integrations(
            slack_webhook=args.slack_webhook,
            teams_webhook=args.teams_webhook
        )
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

if __name__ == "__main__":
    main()