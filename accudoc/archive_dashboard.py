"""
Archive Dashboard GUI for AccuDoc.

Provides a graphical interface for browsing, validating, and managing
immutable documentation archives.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json


class ArchiveDashboard:
    """Archive browsing and management dashboard."""
    
    def __init__(self, parent=None):
        """
        Initialize archive dashboard.
        
        Args:
            parent: Parent Tkinter window (creates new window if None)
        """
        if parent is None:
            self.root = tk.Tk()
            self.root.title("AccuDoc - Archive Dashboard")
            self.own_window = True
        else:
            self.root = tk.Toplevel(parent)
            self.root.title("Archive Dashboard")
            self.own_window = False
        
        self.root.geometry("1000x700")
        
        # Initialize components
        from accudoc.archive import ArchiveManager
        from accudoc.project_database import ProjectDatabase
        from accudoc.audit import get_audit_logger
        from accudoc.membership import MembershipManager
        
        self.db = ProjectDatabase()
        self.audit_logger = get_audit_logger()
        self.archive_mgr = ArchiveManager(self.db, self.audit_logger)
        
        # State
        self.current_project_id = None
        self.selected_archive_id = None
        self.archives = []
        
        self._create_widgets()
        self._refresh_projects()
    
    def _create_widgets(self):
        """Create dashboard widgets."""
        # Top controls
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Project:").pack(side=tk.LEFT, padx=5)
        
        self.project_var = tk.StringVar()
        self.project_combo = ttk.Combobox(
            top_frame,
            textvariable=self.project_var,
            state='readonly',
            width=40
        )
        self.project_combo.pack(side=tk.LEFT, padx=5)
        self.project_combo.bind('<<ComboboxSelected>>', self._on_project_selected)
        
        ttk.Button(
            top_frame,
            text="Refresh",
            command=self._refresh_archives
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            top_frame,
            text="All Projects",
            command=self._show_all_archives
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter controls
        filter_frame = ttk.Frame(self.root, padding=5)
        filter_frame.pack(fill=tk.X)
        
        ttk.Label(filter_frame, text="Format:").pack(side=tk.LEFT, padx=5)
        
        self.format_var = tk.StringVar(value="All")
        format_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.format_var,
            values=["All", "markdown", "html", "pdf"],
            state='readonly',
            width=15
        )
        format_combo.pack(side=tk.LEFT, padx=5)
        format_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_archives())
        
        ttk.Label(filter_frame, text="Tags:").pack(side=tk.LEFT, padx=5)
        
        self.tags_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.tags_var, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            filter_frame,
            text="Filter",
            command=self._refresh_archives
        ).pack(side=tk.LEFT, padx=5)
        
        # Archive list
        list_frame = ttk.Frame(self.root, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for archives
        columns = ("Document", "Format", "Created", "By", "Size", "Tags")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading("Document", text="Document")
        self.tree.heading("Format", text="Format")
        self.tree.heading("Created", text="Created")
        self.tree.heading("By", text="By")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Tags", text="Tags")
        
        self.tree.column("Document", width=200)
        self.tree.column("Format", width=80)
        self.tree.column("Created", width=150)
        self.tree.column("By", width=100)
        self.tree.column("Size", width=80)
        self.tree.column("Tags", width=150)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_archive_selected)
        self.tree.bind('<Double-1>', self._on_archive_double_click)
        
        # Details panel
        details_frame = ttk.LabelFrame(self.root, text="Archive Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.details_text = scrolledtext.ScrolledText(
            details_frame,
            height=8,
            wrap=tk.WORD,
            state='disabled'
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Create Archive",
            command=self._create_archive_dialog
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Retrieve",
            command=self._retrieve_archive
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Validate",
            command=self._validate_archive
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Delete",
            command=self._delete_archive
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Statistics",
            command=self._show_statistics
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Export List",
            command=self._export_list
        ).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _refresh_projects(self):
        """Refresh project list."""
        projects = self.db.list_projects(limit=1000)
        project_names = ["All Projects"] + [
            f"{p['name']} ({p['project_id']})"
            for p in projects
        ]
        self.project_combo['values'] = project_names
        if project_names:
            self.project_combo.current(0)
    
    def _on_project_selected(self, event):
        """Handle project selection."""
        selected = self.project_var.get()
        if selected == "All Projects":
            self.current_project_id = None
        else:
            # Extract project_id from "name (project_id)"
            self.current_project_id = selected.split('(')[1].rstrip(')')
        self._refresh_archives()
    
    def _show_all_archives(self):
        """Show archives from all projects."""
        self.current_project_id = None
        self.project_combo.set("All Projects")
        self._refresh_archives()
    
    def _refresh_archives(self):
        """Refresh archive list."""
        # Get filter values
        format_filter = None
        if self.format_var.get() != "All":
            from accudoc.archive import ArchiveFormat
            format_filter = ArchiveFormat(self.format_var.get())
        
        tags_filter = None
        if self.tags_var.get().strip():
            tags_filter = [t.strip() for t in self.tags_var.get().split(',')]
        
        # Get archives
        self.archives = self.archive_mgr.list_archives(
            project_id=self.current_project_id,
            tags=tags_filter,
            format=format_filter,
            limit=1000
        )
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate tree
        for archive in self.archives:
            # Format size
            size_kb = archive.size_bytes / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            
            # Format date
            try:
                created_dt = datetime.fromisoformat(archive.created_at)
                created_str = created_dt.strftime("%Y-%m-%d %H:%M")
            except:
                created_str = archive.created_at
            
            # Format tags
            tags_str = ", ".join(archive.tags) if archive.tags else ""
            
            self.tree.insert('', tk.END, values=(
                archive.document_name,
                archive.format,
                created_str,
                archive.created_by,
                size_str,
                tags_str
            ), tags=(archive.archive_id,))
        
        self.status_var.set(f"Showing {len(self.archives)} archive(s)")
    
    def _on_archive_selected(self, event):
        """Handle archive selection in tree."""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get selected archive
        item = self.tree.item(selection[0])
        self.selected_archive_id = item['tags'][0]
        
        # Find archive in list
        archive = next((a for a in self.archives if a.archive_id == self.selected_archive_id), None)
        if not archive:
            return
        
        # Update details
        details = f"""Archive ID: {archive.archive_id}
Project ID: {archive.project_id}
Document: {archive.document_name}
Format: {archive.format}
Created: {archive.created_at}
Created By: {archive.created_by}
Size: {archive.size_bytes:,} bytes
Content Hash: {archive.content_hash}
Signature: {archive.signature[:32]}...
Compression: {archive.compression}
Tags: {', '.join(archive.tags) if archive.tags else 'None'}
Description: {archive.description or 'None'}
"""
        
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert('1.0', details)
        self.details_text.config(state='disabled')
    
    def _on_archive_double_click(self, event):
        """Handle double-click on archive (retrieve)."""
        self._retrieve_archive()
    
    def _create_archive_dialog(self):
        """Show create archive dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Archive")
        dialog.geometry("500x400")
        
        # Repository
        ttk.Label(dialog, text="Repository Path:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        repo_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=repo_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(
            dialog,
            text="Browse...",
            command=lambda: repo_var.set(filedialog.askdirectory())
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Document
        ttk.Label(dialog, text="Document File:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        doc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=doc_var, width=40).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(
            dialog,
            text="Browse...",
            command=lambda: doc_var.set(filedialog.askopenfilename(
                filetypes=[("All files", "*.*"), ("Markdown", "*.md"), ("HTML", "*.html"), ("PDF", "*.pdf")]
            ))
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # Format
        ttk.Label(dialog, text="Format:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        format_var = tk.StringVar(value="auto")
        ttk.Combobox(
            dialog,
            textvariable=format_var,
            values=["auto", "markdown", "html", "pdf"],
            state='readonly'
        ).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Tags
        ttk.Label(dialog, text="Tags (comma-separated):").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        tags_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=tags_var, width=40).grid(row=3, column=1, padx=10, pady=5)
        
        # Description
        ttk.Label(dialog, text="Description:").grid(row=4, column=0, sticky=tk.NW, padx=10, pady=5)
        desc_text = tk.Text(dialog, width=40, height=5)
        desc_text.grid(row=4, column=1, padx=10, pady=5)
        
        def create():
            repo_path = repo_var.get()
            doc_path = doc_var.get()
            
            if not repo_path or not doc_path:
                messagebox.showerror("Error", "Please specify repository and document paths")
                return
            
            try:
                # Get or create project
                project = self.db.get_project_by_path(repo_path)
                if not project:
                    project_id = self.db.add_project(repo_path, Path(repo_path).name)
                else:
                    project_id = project['project_id']
                
                # Determine format
                from accudoc.archive import ArchiveFormat
                if format_var.get() == "auto":
                    ext = Path(doc_path).suffix.lower()
                    format_map = {'.md': ArchiveFormat.MARKDOWN, '.html': ArchiveFormat.HTML, '.pdf': ArchiveFormat.PDF}
                    format = format_map.get(ext, ArchiveFormat.MARKDOWN)
                else:
                    format = ArchiveFormat(format_var.get())
                
                # Create archive
                import os
                tags = [t.strip() for t in tags_var.get().split(',') if t.strip()]
                archive_id = self.archive_mgr.create_archive(
                    project_id=project_id,
                    document_path=Path(doc_path),
                    format=format,
                    created_by=os.getenv('USER', 'gui_user'),
                    tags=tags,
                    description=desc_text.get('1.0', tk.END).strip() or None
                )
                
                messagebox.showinfo("Success", f"Archive created successfully!\nArchive ID: {archive_id}")
                dialog.destroy()
                self._refresh_archives()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create archive: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Create", command=create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _retrieve_archive(self):
        """Retrieve selected archive."""
        if not self.selected_archive_id:
            messagebox.showwarning("Warning", "Please select an archive first")
            return
        
        # Ask for output location
        output_path = filedialog.asksaveasfilename(
            title="Save Archive As",
            defaultextension=".md"
        )
        
        if not output_path:
            return
        
        try:
            import os
            content, metadata = self.archive_mgr.retrieve_archive(
                self.selected_archive_id,
                os.getenv('USER', 'gui_user'),
                validate=True
            )
            
            with open(output_path, 'wb') as f:
                f.write(content)
            
            messagebox.showinfo(
                "Success",
                f"Archive retrieved successfully!\n\nDocument: {metadata.document_name}\nSize: {metadata.size_bytes:,} bytes\nSaved to: {output_path}\n\n✓ Signature validated"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve archive: {str(e)}")
    
    def _validate_archive(self):
        """Validate selected archive."""
        if not self.selected_archive_id:
            messagebox.showwarning("Warning", "Please select an archive first")
            return
        
        try:
            is_valid = self.archive_mgr.validate_archive(self.selected_archive_id)
            
            if is_valid:
                messagebox.showinfo(
                    "Validation Result",
                    "✓ Archive is VALID\n\nSignature: VERIFIED\nContent integrity: OK"
                )
            else:
                messagebox.showwarning(
                    "Validation Result",
                    "✗ Archive is INVALID\n\nSignature: FAILED\nContent may have been tampered with!"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to validate archive: {str(e)}")
    
    def _delete_archive(self):
        """Delete selected archive."""
        if not self.selected_archive_id:
            messagebox.showwarning("Warning", "Please select an archive first")
            return
        
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this archive?\n\nArchive ID: {self.selected_archive_id}\n\nThis action cannot be undone."
        ):
            return
        
        try:
            import os
            self.archive_mgr.delete_archive(
                self.selected_archive_id,
                os.getenv('USER', 'gui_user')
            )
            
            messagebox.showinfo("Success", "Archive deleted successfully")
            self._refresh_archives()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete archive: {str(e)}")
    
    def _show_statistics(self):
        """Show archive statistics."""
        try:
            stats = self.archive_mgr.get_archive_statistics(
                project_id=self.current_project_id
            )
            
            stats_text = f"""Archive Statistics
{'=' * 50}

Total Archives: {stats['total_archives']}
Total Size: {stats['total_size_bytes']:,} bytes
Compressed Size: {stats['total_compressed_bytes']:,} bytes
Compression Ratio: {stats['compression_ratio']:.2%}

By Format:
"""
            for fmt, count in stats['by_format'].items():
                stats_text += f"  {fmt}: {count}\n"
            
            if stats['oldest_archive']:
                stats_text += f"\nOldest Archive: {stats['oldest_archive']}"
            if stats['newest_archive']:
                stats_text += f"\nNewest Archive: {stats['newest_archive']}"
            
            messagebox.showinfo("Archive Statistics", stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get statistics: {str(e)}")
    
    def _export_list(self):
        """Export archive list to JSON."""
        output_path = filedialog.asksaveasfilename(
            title="Export Archive List",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not output_path:
            return
        
        try:
            archive_list = [
                {
                    'archive_id': a.archive_id,
                    'project_id': a.project_id,
                    'document_name': a.document_name,
                    'format': a.format,
                    'created_at': a.created_at,
                    'created_by': a.created_by,
                    'size_bytes': a.size_bytes,
                    'tags': a.tags,
                    'description': a.description
                }
                for a in self.archives
            ]
            
            with open(output_path, 'w') as f:
                json.dump(archive_list, f, indent=2)
            
            messagebox.showinfo("Success", f"Archive list exported to:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export list: {str(e)}")
    
    def run(self):
        """Run the dashboard (if standalone)."""
        if self.own_window:
            self.root.mainloop()


def main():
    """Run standalone archive dashboard."""
    dashboard = ArchiveDashboard()
    dashboard.run()


if __name__ == '__main__':
    main()
