"""
Collaborative GUI module for AccuDoc.

Provides a simple GUI interface for collaborative documentation editing.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
from pathlib import Path
from typing import Optional

try:
    from accudoc.membership import MembershipManager, Role
    from accudoc.collaboration import CollaborationManager
    from accudoc.crdt import OperationType
    from accudoc.project_database import ProjectDatabase
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


class CollaborativeEditorDialog(tk.Toplevel):
    """Simple collaborative editor dialog."""
    
    def __init__(self, parent, session_id: str, user_id: str, username: str):
        """
        Initialize collaborative editor.
        
        Args:
            parent: Parent window
            session_id: Collaborative session ID
            user_id: Current user ID
            username: Current username
        """
        super().__init__(parent)
        
        if not MODULES_AVAILABLE:
            messagebox.showerror("Error", "Collaborative modules not available")
            self.destroy()
            return
        
        self.session_id = session_id
        self.user_id = user_id
        self.username = username
        
        self.title(f"Collaborative Session: {session_id[:16]}...")
        self.geometry("900x700")
        
        self.collab_mgr = CollaborationManager()
        self.refresh_interval = 2000  # 2 seconds
        
        self._create_widgets()
        self._load_session_data()
        self._start_refresh_loop()
    
    def _create_widgets(self):
        """Create GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Session Info", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Session ID: {self.session_id}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"User: {self.username}").pack(anchor=tk.W)
        
        self.participants_label = ttk.Label(info_frame, text="Participants: 0")
        self.participants_label.pack(anchor=tk.W)
        
        # Content area
        content_frame = ttk.LabelFrame(main_frame, text="Document Content", padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.content_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            height=20,
            font=('Courier', 10)
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind text modification
        self.content_text.bind('<<Modified>>', self._on_text_modified)
        
        # Comments frame
        comments_frame = ttk.LabelFrame(main_frame, text="Comments", padding=10)
        comments_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Comments list
        comments_scroll_frame = ttk.Frame(comments_frame)
        comments_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.comments_list = tk.Listbox(comments_scroll_frame, height=5)
        comments_scrollbar = ttk.Scrollbar(
            comments_scroll_frame,
            orient=tk.VERTICAL,
            command=self.comments_list.yview
        )
        self.comments_list.config(yscrollcommand=comments_scrollbar.set)
        
        self.comments_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        comments_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Comment entry
        comment_entry_frame = ttk.Frame(comments_frame)
        comment_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.comment_entry = ttk.Entry(comment_entry_frame)
        self.comment_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(
            comment_entry_frame,
            text="Add Comment",
            command=self._add_comment
        ).pack(side=tk.RIGHT)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self._refresh_content
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Add Suggestion",
            command=self._add_suggestion_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Save & Close",
            command=self._save_and_close
        ).pack(side=tk.RIGHT)
    
    def _load_session_data(self):
        """Load initial session data."""
        try:
            # Get content
            content = self.collab_mgr.get_session_content(self.session_id)
            if content:
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(1.0, content)
                self.content_text.edit_modified(False)
            
            # Get participants
            participants = self.collab_mgr.get_session_participants(self.session_id)
            self.participants_label.config(
                text=f"Participants: {len(participants)} ({', '.join(p.username for p in participants)})"
            )
            
            # Get comments
            self._refresh_comments()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session: {str(e)}")
    
    def _refresh_content(self):
        """Refresh content from server."""
        try:
            content = self.collab_mgr.get_session_content(self.session_id)
            if content:
                # Save cursor position
                cursor_pos = self.content_text.index(tk.INSERT)
                
                # Update content
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(1.0, content)
                
                # Restore cursor
                try:
                    self.content_text.mark_set(tk.INSERT, cursor_pos)
                except:
                    pass
                
                self.content_text.edit_modified(False)
        except Exception as e:
            print(f"Refresh error: {e}")
    
    def _refresh_comments(self):
        """Refresh comments list."""
        try:
            comments = self.collab_mgr.get_session_comments(self.session_id)
            
            self.comments_list.delete(0, tk.END)
            for comment in comments:
                self.comments_list.insert(
                    tk.END,
                    f"{comment['username']}: {comment['content']}"
                )
        except Exception as e:
            print(f"Comment refresh error: {e}")
    
    def _on_text_modified(self, event):
        """Handle text modification."""
        if self.content_text.edit_modified():
            # Text was modified - could implement auto-save here
            self.content_text.edit_modified(False)
    
    def _add_comment(self):
        """Add a comment."""
        comment_text = self.comment_entry.get().strip()
        if not comment_text:
            return
        
        try:
            self.collab_mgr.add_comment(
                session_id=self.session_id,
                user_id=self.user_id,
                username=self.username,
                content=comment_text
            )
            
            self.comment_entry.delete(0, tk.END)
            self._refresh_comments()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add comment: {str(e)}")
    
    def _add_suggestion_dialog(self):
        """Show dialog to add a suggestion."""
        # Get current selection
        try:
            sel_start = self.content_text.index(tk.SEL_FIRST)
            sel_end = self.content_text.index(tk.SEL_LAST)
            original_text = self.content_text.get(sel_start, sel_end)
        except tk.TclError:
            original_text = ""
        
        # Dialog for suggestion
        suggestion = simpledialog.askstring(
            "Suggestion",
            f"Suggest replacement for:\n'{original_text}'\n\nNew text:",
            parent=self
        )
        
        if suggestion:
            try:
                # Get position
                if original_text:
                    position = int(sel_start.split('.')[1])
                else:
                    position = 0
                
                self.collab_mgr.add_suggestion(
                    session_id=self.session_id,
                    user_id=self.user_id,
                    username=self.username,
                    position=position,
                    original_text=original_text,
                    suggested_text=suggestion,
                    reason="User suggestion"
                )
                
                messagebox.showinfo("Success", "Suggestion added")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add suggestion: {str(e)}")
    
    def _save_and_close(self):
        """Save and close the session."""
        # Could implement actual save logic here
        self.collab_mgr.close()
        self.destroy()
    
    def _start_refresh_loop(self):
        """Start the refresh loop."""
        def refresh_loop():
            if self.winfo_exists():
                self._refresh_content()
                self._refresh_comments()
                self.after(self.refresh_interval, refresh_loop)
        
        self.after(self.refresh_interval, refresh_loop)


class CollaborativeLoginDialog(tk.Toplevel):
    """Login dialog for collaborative features."""
    
    def __init__(self, parent):
        """Initialize login dialog."""
        super().__init__(parent)
        
        self.title("Collaborative Login")
        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()
        
        self.user_id = None
        self.username = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create widgets."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            main_frame,
            text="Login to Collaborative Mode",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(main_frame, width=40)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(main_frame, width=40, show='*')
        self.password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Login",
            command=self._login
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self._login())
        self.username_entry.focus()
    
    def _login(self):
        """Perform login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        try:
            membership_mgr = MembershipManager()
            user = membership_mgr.authenticate_user(username, password)
            membership_mgr.close()
            
            if user:
                self.user_id = user.user_id
                self.username = user.username
                self.destroy()
            else:
                messagebox.showerror("Error", "Invalid credentials")
                
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")


def open_collaborative_session(parent):
    """
    Open collaborative session from GUI.
    
    Args:
        parent: Parent window
    """
    if not MODULES_AVAILABLE:
        messagebox.showerror(
            "Error",
            "Collaborative modules not available. Please check installation."
        )
        return
    
    # Show login dialog
    login_dialog = CollaborativeLoginDialog(parent)
    parent.wait_window(login_dialog)
    
    if not login_dialog.user_id:
        return  # Login cancelled or failed
    
    user_id = login_dialog.user_id
    username = login_dialog.username
    
    # Ask for session ID or create new
    choice = messagebox.askyesno(
        "Collaborative Session",
        "Do you want to join an existing session?\n\n"
        "Yes = Join existing session\n"
        "No = Create new session"
    )
    
    if choice:  # Join existing
        session_id = simpledialog.askstring(
            "Join Session",
            "Enter session ID:",
            parent=parent
        )
        
        if not session_id:
            return
        
        try:
            collab_mgr = CollaborationManager()
            result = collab_mgr.join_session(session_id, user_id, username)
            collab_mgr.close()
            
            if result:
                # Open editor
                CollaborativeEditorDialog(parent, session_id, user_id, username)
            else:
                messagebox.showerror("Error", "Failed to join session")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to join session: {str(e)}")
    
    else:  # Create new
        project_id = simpledialog.askstring(
            "Create Session",
            "Enter project ID:",
            parent=parent
        )
        
        if not project_id:
            return
        
        document_path = simpledialog.askstring(
            "Create Session",
            "Enter document path (e.g., /docs/README.md):",
            parent=parent
        )
        
        if not document_path:
            return
        
        try:
            collab_mgr = CollaborationManager()
            session = collab_mgr.create_session(
                project_id=project_id,
                document_path=document_path,
                created_by=user_id,
                initial_content="# New Document\n\nStart editing..."
            )
            
            # Join the session
            collab_mgr.join_session(session.session_id, user_id, username)
            
            # Add to database
            db = ProjectDatabase()
            db.add_collaborative_session(
                session_id=session.session_id,
                project_id=project_id,
                document_path=document_path,
                created_by=user_id
            )
            db.close()
            collab_mgr.close()
            
            messagebox.showinfo(
                "Success",
                f"Session created!\nSession ID: {session.session_id}"
            )
            
            # Open editor
            CollaborativeEditorDialog(parent, session.session_id, user_id, username)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create session: {str(e)}")


# Demo/test function
def demo_collaborative_gui():
    """Demo the collaborative GUI."""
    root = tk.Tk()
    root.title("AccuDoc Collaborative Demo")
    root.geometry("400x200")
    
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(
        frame,
        text="AccuDoc Collaborative Editor",
        font=('Arial', 14, 'bold')
    ).pack(pady=20)
    
    ttk.Button(
        frame,
        text="Open Collaborative Session",
        command=lambda: open_collaborative_session(root)
    ).pack()
    
    root.mainloop()


if __name__ == '__main__':
    demo_collaborative_gui()
