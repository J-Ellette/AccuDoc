#!/usr/bin/env python3
"""
AccuDoc Collaboration CLI Commands

Commands for managing real-time collaboration features:
- start-collab-server: Start collaboration WebSocket server
- collab-status: Check collaboration server status
- manage-sessions: Manage collaboration sessions
- manage-comments: Manage document comments
- manage-reviews: Manage review workflows
"""

import argparse
import asyncio
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests
import subprocess
import signal
import os

def start_collaboration_server(args):
    """Start the collaboration WebSocket server"""
    try:
        server_script = Path(__file__).parent / "collaboration_server.py"
        
        cmd = [sys.executable, str(server_script)]
        cmd.extend(["--port", str(args.port)])
        cmd.extend(["--db", args.database])
        
        if args.slack_webhook:
            cmd.extend(["--slack-webhook", args.slack_webhook])
            
        if args.teams_webhook:
            cmd.extend(["--teams-webhook", args.teams_webhook])
            
        print(f"Starting collaboration server on port {args.port}...")
        print(f"Database: {args.database}")
        
        if args.daemon:
            # Run as daemon process
            with open("collaboration_server.pid", "w") as f:
                process = subprocess.Popen(cmd)
                f.write(str(process.pid))
            print(f"Collaboration server started as daemon (PID: {process.pid})")
            print("Use 'accudoc collab-status' to check server status")
        else:
            # Run in foreground
            subprocess.run(cmd)
            
    except Exception as e:
        print(f"Error starting collaboration server: {e}")
        return 1
        
    return 0

def collaboration_status(args):
    """Check collaboration server status"""
    try:
        # Check if PID file exists
        pid_file = Path("collaboration_server.pid")
        if pid_file.exists():
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
                
            try:
                os.kill(pid, 0)  # Check if process exists
                print(f"✓ Collaboration server is running (PID: {pid})")
                
                # Try to connect to WebSocket
                try:
                    import websockets
                    async def check_connection():
                        try:
                            async with websockets.connect(f"ws://localhost:{args.port}"):
                                return True
                        except:
                            return False
                    
                    if asyncio.run(check_connection()):
                        print(f"✓ WebSocket server responding on port {args.port}")
                    else:
                        print(f"✗ WebSocket server not responding on port {args.port}")
                        
                except ImportError:
                    print("  (Install 'websockets' package to test connection)")
                    
            except OSError:
                print(f"✗ Process {pid} not found (server may have crashed)")
                pid_file.unlink()  # Remove stale PID file
                
        else:
            print("✗ No collaboration server running")
            
        # Check database
        db_path = args.database
        if Path(db_path).exists():
            print(f"✓ Database found: {db_path}")
            
            # Show basic stats
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM comments")
            comment_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reviews")
            review_count = cursor.fetchone()[0]
            
            print(f"  Users: {user_count}")
            print(f"  Comments: {comment_count}")
            print(f"  Reviews: {review_count}")
            
            conn.close()
        else:
            print(f"✗ Database not found: {db_path}")
            
    except Exception as e:
        print(f"Error checking collaboration status: {e}")
        return 1
        
    return 0

def stop_collaboration_server(args):
    """Stop the collaboration server"""
    try:
        pid_file = Path("collaboration_server.pid")
        if pid_file.exists():
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
                
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"✓ Collaboration server stopped (PID: {pid})")
                pid_file.unlink()
            except OSError:
                print(f"✗ Process {pid} not found")
                pid_file.unlink()
        else:
            print("✗ No collaboration server running")
            
    except Exception as e:
        print(f"Error stopping collaboration server: {e}")
        return 1
        
    return 0

def manage_sessions(args):
    """Manage collaboration sessions"""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()
        
        if args.action == "list":
            cursor.execute('''
                SELECT DISTINCT document_id, COUNT(*) as active_users
                FROM document_edits 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY document_id
                ORDER BY active_users DESC
            ''')
            
            sessions = cursor.fetchall()
            if sessions:
                print("Active Collaboration Sessions (last hour):")
                print("-" * 50)
                for doc_id, user_count in sessions:
                    print(f"Document: {doc_id}")
                    print(f"Active Users: {user_count}")
                    print()
            else:
                print("No active collaboration sessions found")
                
        elif args.action == "history":
            document_id = args.document_id
            if not document_id:
                print("Error: --document-id required for history action")
                return 1
                
            cursor.execute('''
                SELECT de.operation, de.position, de.content, de.timestamp, u.name
                FROM document_edits de
                JOIN users u ON de.user_id = u.id
                WHERE de.document_id = ?
                ORDER BY de.timestamp DESC
                LIMIT 50
            ''', (document_id,))
            
            edits = cursor.fetchall()
            if edits:
                print(f"Edit History for {document_id}:")
                print("-" * 50)
                for operation, position, content, timestamp, user_name in edits:
                    print(f"{timestamp} - {user_name}")
                    print(f"  {operation} at position {position}")
                    if content:
                        content_preview = content[:50] + "..." if len(content) > 50 else content
                        print(f"  Content: {content_preview}")
                    print()
            else:
                print(f"No edit history found for document: {document_id}")
                
        conn.close()
        
    except Exception as e:
        print(f"Error managing sessions: {e}")
        return 1
        
    return 0

def manage_comments(args):
    """Manage document comments"""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()
        
        if args.action == "list":
            document_id = args.document_id
            where_clause = "WHERE c.document_id = ?" if document_id else ""
            params = (document_id,) if document_id else ()
            
            cursor.execute(f'''
                SELECT c.id, c.document_id, c.content, c.line_start, c.line_end, 
                       c.resolved, c.created_at, u.name
                FROM comments c
                JOIN users u ON c.user_id = u.id
                {where_clause}
                ORDER BY c.created_at DESC
            ''', params)
            
            comments = cursor.fetchall()
            if comments:
                print("Document Comments:")
                print("-" * 50)
                for comment_id, doc_id, content, line_start, line_end, resolved, created_at, user_name in comments:
                    status = "✓ Resolved" if resolved else "○ Open"
                    print(f"Comment ID: {comment_id}")
                    print(f"Document: {doc_id}")
                    print(f"Author: {user_name}")
                    print(f"Lines: {line_start}-{line_end}")
                    print(f"Status: {status}")
                    print(f"Created: {created_at}")
                    print(f"Content: {content}")
                    print()
            else:
                print("No comments found")
                
        elif args.action == "resolve":
            comment_id = args.comment_id
            if not comment_id:
                print("Error: --comment-id required for resolve action")
                return 1
                
            cursor.execute('''
                UPDATE comments SET resolved = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (comment_id,))
            
            if cursor.rowcount > 0:
                print(f"✓ Comment {comment_id} marked as resolved")
            else:
                print(f"✗ Comment {comment_id} not found")
                
            conn.commit()
            
        conn.close()
        
    except Exception as e:
        print(f"Error managing comments: {e}")
        return 1
        
    return 0

def manage_reviews(args):
    """Manage review workflows"""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()
        
        if args.action == "list":
            cursor.execute('''
                SELECT r.id, r.document_id, r.status, r.comments, r.created_at, 
                       u.name as reviewer_name
                FROM reviews r
                JOIN users u ON r.reviewer_id = u.id
                ORDER BY r.created_at DESC
            ''')
            
            reviews = cursor.fetchall()
            if reviews:
                print("Review Requests:")
                print("-" * 50)
                for review_id, doc_id, status, comments, created_at, reviewer_name in reviews:
                    status_icon = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(status, "❓")
                    print(f"Review ID: {review_id}")
                    print(f"Document: {doc_id}")
                    print(f"Reviewer: {reviewer_name}")
                    print(f"Status: {status_icon} {status.title()}")
                    print(f"Created: {created_at}")
                    if comments:
                        print(f"Comments: {comments}")
                    print()
            else:
                print("No review requests found")
                
        elif args.action == "stats":
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM reviews
                GROUP BY status
            ''')
            
            stats = cursor.fetchall()
            if stats:
                print("Review Statistics:")
                print("-" * 20)
                total = sum(count for _, count in stats)
                for status, count in stats:
                    percentage = (count / total * 100) if total > 0 else 0
                    print(f"{status.title()}: {count} ({percentage:.1f}%)")
            else:
                print("No review statistics available")
                
        conn.close()
        
    except Exception as e:
        print(f"Error managing reviews: {e}")
        return 1
        
    return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AccuDoc Collaboration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start collaboration server
    start_parser = subparsers.add_parser(
        "start-collab-server", 
        help="Start collaboration WebSocket server"
    )
    start_parser.add_argument("--port", type=int, default=8765, help="WebSocket server port")
    start_parser.add_argument("--database", default="collaboration.db", help="Database file path")
    start_parser.add_argument("--slack-webhook", help="Slack webhook URL for notifications")
    start_parser.add_argument("--teams-webhook", help="Microsoft Teams webhook URL")
    start_parser.add_argument("--daemon", action="store_true", help="Run as daemon process")
    start_parser.set_defaults(func=start_collaboration_server)
    
    # Check server status
    status_parser = subparsers.add_parser(
        "collab-status", 
        help="Check collaboration server status"
    )
    status_parser.add_argument("--port", type=int, default=8765, help="WebSocket server port")
    status_parser.add_argument("--database", default="collaboration.db", help="Database file path")
    status_parser.set_defaults(func=collaboration_status)
    
    # Stop collaboration server
    stop_parser = subparsers.add_parser(
        "stop-collab-server", 
        help="Stop collaboration server"
    )
    stop_parser.set_defaults(func=stop_collaboration_server)
    
    # Manage sessions
    sessions_parser = subparsers.add_parser(
        "manage-sessions", 
        help="Manage collaboration sessions"
    )
    sessions_parser.add_argument("action", choices=["list", "history"], help="Action to perform")
    sessions_parser.add_argument("--database", default="collaboration.db", help="Database file path")
    sessions_parser.add_argument("--document-id", help="Document ID for history action")
    sessions_parser.set_defaults(func=manage_sessions)
    
    # Manage comments
    comments_parser = subparsers.add_parser(
        "manage-comments", 
        help="Manage document comments"
    )
    comments_parser.add_argument("action", choices=["list", "resolve"], help="Action to perform")
    comments_parser.add_argument("--database", default="collaboration.db", help="Database file path")
    comments_parser.add_argument("--document-id", help="Filter by document ID")
    comments_parser.add_argument("--comment-id", help="Comment ID for resolve action")
    comments_parser.set_defaults(func=manage_comments)
    
    # Manage reviews
    reviews_parser = subparsers.add_parser(
        "manage-reviews", 
        help="Manage review workflows"
    )
    reviews_parser.add_argument("action", choices=["list", "stats"], help="Action to perform")
    reviews_parser.add_argument("--database", default="collaboration.db", help="Database file path")
    reviews_parser.set_defaults(func=manage_reviews)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
        
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())