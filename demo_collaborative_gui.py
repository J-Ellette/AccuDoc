"""
Demo script for collaborative GUI.

Shows the collaborative editing interface.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Add parent directory to path
sys.path.insert(0, '.')

from accudoc.collaborative_gui import open_collaborative_session


def main():
    """Run the collaborative GUI demo."""
    root = tk.Tk()
    root.title("AccuDoc Collaborative Demo")
    root.geometry("500x300")
    
    # Main frame
    frame = ttk.Frame(root, padding=40)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(
        frame,
        text="AccuDoc Collaborative Editor",
        font=('Arial', 16, 'bold')
    )
    title_label.pack(pady=(0, 20))
    
    # Description
    desc_text = """
Welcome to AccuDoc's Collaborative Documentation Workspace!

Features:
• Multi-user real-time editing
• Comments and suggestions
• CRDT-based conflict resolution
• Role-based access control
    """
    
    desc_label = ttk.Label(
        frame,
        text=desc_text,
        justify=tk.LEFT
    )
    desc_label.pack(pady=(0, 30))
    
    # Button
    collab_button = ttk.Button(
        frame,
        text="Open Collaborative Session",
        command=lambda: open_collaborative_session(root),
        width=30
    )
    collab_button.pack()
    
    # Info label
    info_label = ttk.Label(
        frame,
        text="First-time users will need to create an account",
        font=('Arial', 9),
        foreground='gray'
    )
    info_label.pack(pady=(10, 0))
    
    # Instructions
    instructions_label = ttk.Label(
        frame,
        text="\nNote: Run demo_collaboration.py first to create test users",
        font=('Arial', 9, 'italic'),
        foreground='blue'
    )
    instructions_label.pack()
    
    root.mainloop()


if __name__ == '__main__':
    main()
