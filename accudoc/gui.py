"""GUI module for AccuDoc application."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from .scanner import RepositoryScanner
from .generator import DocumentGenerator
from .i18n import I18n, get_i18n
from .settings import SettingsManager, AccuDocSettings
from .membership import MembershipManager, Permission

# Try to import live testbed (optional)
try:
    from .live_testbed import LiveTestbed, Language, ExecutionStatus
    TESTBED_AVAILABLE = True
except ImportError:
    TESTBED_AVAILABLE = False


class AccuDocGUI:
    """Main GUI application for AccuDoc."""
    
    # Theme definition
    THEME = {
        'bg': '#ffffff',
        'fg': '#000000',
        'text_bg': '#ffffff',
        'text_fg': '#000000',
        'button_bg': '#f0f0f0',
        'entry_bg': '#ffffff',
        'status_fg': '#0066cc',
        'highlight': '#e6f2ff',
    }
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        
        # Load settings first to get language preference
        self.settings_manager = SettingsManager()
        self.settings = self._load_or_create_settings()
        
        # Initialize i18n with saved language preference
        lang = self.settings.language if self.settings.language != 'auto' else None
        self.i18n = I18n(lang)
        
        self.root.title(self.i18n.get('app_title'))
        self.root.geometry("900x700")
        
        # Variables
        self.repo_url = tk.StringVar()
        self.status_text = tk.StringVar(value=self.i18n.get('ready'))
        self.scanning = False
        
        # Initialize membership manager (optional)
        self.membership_manager = None
        if self.settings.testbed_require_auth:
            try:
                self.membership_manager = MembershipManager()
            except Exception as e:
                self._log(f"Failed to initialize membership manager: {e}", 'warning')
        
        # Initialize live testbed (optional)
        self.testbed = None
        if TESTBED_AVAILABLE and self.settings.enable_live_testbed:
            try:
                self.testbed = LiveTestbed(
                    timeout=self.settings.testbed_timeout,
                    memory_limit=self.settings.testbed_memory_limit,
                    cpu_quota=self.settings.testbed_cpu_quota,
                    network_disabled=self.settings.testbed_network_disabled,
                    enable_cache=self.settings.testbed_enable_cache
                )
                self._log("Live testbed initialized", 'info')
            except Exception as e:
                self._log(f"Failed to initialize live testbed: {e}", 'warning')
                self.testbed = None
        
        # Recent repositories and favorites
        self.recent_repos = []
        self.favorite_repos = []
        self.config_file = Path.home() / '.accudoc' / 'config.json'
        self._load_config()
        
        # Setup logging
        self.log_messages = []
        self._setup_logging()
        
        self._create_widgets()
        self._setup_drag_and_drop()
        self._apply_theme()
        self._update_recent_menu()
        self._update_favorites_menu()
        
        # Apply RTL if needed
        if self.i18n.is_rtl():
            self._apply_rtl_layout()
        
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.i18n.get('file'), menu=file_menu)
        
        file_menu.add_command(
            label=self.i18n.get('new_window'),
            command=self._open_new_window,
            accelerator="Ctrl+N"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=self.i18n.get('exit'),
            command=self.root.quit,
            accelerator="Ctrl+Q"
        )
        
        # Window menu
        window_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Window", menu=window_menu)
        
        window_menu.add_command(
            label=self.i18n.get('new_window'),
            command=self._open_new_window,
            accelerator="Ctrl+N"
        )
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.i18n.get('help'), menu=help_menu)
        
        help_menu.add_command(
            label=self.i18n.get('about'),
            command=self._show_about
        )
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self._open_new_window())
        self.root.bind('<Control-N>', lambda e: self._open_new_window())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())
    
    def _create_widgets(self):
        """Create and layout GUI widgets."""
        # Create menu bar
        self._create_menu_bar()
        
        # Main container
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(6, weight=1)
        
        # Top bar with title
        top_bar = tk.Frame(self.main_frame)
        top_bar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        top_bar.columnconfigure(0, weight=1)
        
        # Title
        self.title_label = tk.Label(
            top_bar, 
            text=self.i18n.get('app_title'),
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Settings button
        self.settings_button = tk.Button(
            top_bar,
            text="⚙️ " + self.i18n.get('settings'),
            command=self._show_settings,
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.settings_button.pack(side=tk.RIGHT, padx=5)
        
        # Repository URL input
        self.url_label = tk.Label(self.main_frame, text=self.i18n.get('repository'))
        self.url_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.repo_entry = tk.Entry(self.main_frame, textvariable=self.repo_url, width=50)
        self.repo_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Update favorites menu when URL changes
        self.repo_url.trace('w', lambda *args: self._update_favorites_menu())
        
        # Scan button
        self.scan_button = tk.Button(
            self.main_frame, 
            text=self.i18n.get('scan'), 
            command=self._scan_repository,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.scan_button.grid(row=1, column=2, pady=5, padx=5)
        
        # Browse local folder button
        self.browse_button = tk.Button(
            self.main_frame,
            text=self.i18n.get('browse'),
            command=self._browse_local_folder,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.browse_button.grid(row=2, column=2, pady=5, padx=5)
        
        # Recent repositories button with dropdown
        self.recent_button = tk.Menubutton(
            self.main_frame,
            text="Recent ▼",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.recent_button.grid(row=3, column=2, pady=5, padx=5)
        self.recent_menu = tk.Menu(self.recent_button, tearoff=0)
        self.recent_button.config(menu=self.recent_menu)
        
        # Favorites button with dropdown
        self.favorites_button = tk.Menubutton(
            self.main_frame,
            text="★ Favorites",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.favorites_button.grid(row=3, column=1, pady=5, padx=5, sticky=tk.E)
        self.favorites_menu = tk.Menu(self.favorites_button, tearoff=0)
        self.favorites_button.config(menu=self.favorites_menu)
        
        # Status bar
        status_frame = tk.Frame(self.main_frame)
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.status_label_text = tk.Label(status_frame, text="Status:")
        self.status_label_text.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            status_frame, 
            textvariable=self.status_text,
            foreground="blue"
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Detailed progress label
        self.detailed_progress = tk.StringVar(value="")
        self.detailed_progress_label = tk.Label(
            status_frame,
            textvariable=self.detailed_progress,
            font=("Arial", 8, "italic")
        )
        self.detailed_progress_label.pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame, 
            mode='indeterminate',
            length=300
        )
        self.progress.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Output notebook for tabbed interface
        self.output_label = tk.Label(self.main_frame, text="Generated Documentation:")
        self.output_label.grid(row=6, column=0, sticky=(tk.W, tk.N), pady=5)
        
        self.output_notebook = ttk.Notebook(self.main_frame)
        self.output_notebook.grid(
            row=6, column=0, columnspan=3, 
            sticky=(tk.W, tk.E, tk.N, tk.S), 
            pady=5
        )
        
        # Create tabs for different documentation sections
        self.doc_tabs = {}
        self._create_doc_tabs()
        
        # Button frame
        button_frame = tk.Frame(self.main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        # Save button
        self.save_button = tk.Button(
            button_frame,
            text="Save Documentation",
            command=self._save_documentation,
            state=tk.DISABLED,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self._clear_output,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Log Viewer button
        self.log_button = tk.Button(
            button_frame,
            text="📋 View Logs",
            command=self._show_log_viewer,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.log_button.pack(side=tk.LEFT, padx=5)
    
    def _create_doc_tabs(self):
        """Create tabs for different documentation sections."""
        tab_names = [
            "Full Documentation",
            "Overview",
            "Technology Stack",
            "Installation",
            "Usage",
            "Project Structure",
            "Changelog",
            "Contributors"
        ]
        
        for tab_name in tab_names:
            # Create frame for tab
            frame = tk.Frame(self.output_notebook)
            
            # Create text widget for tab
            text_widget = scrolledtext.ScrolledText(
                frame,
                wrap=tk.WORD,
                width=80,
                height=25,
                font=("Courier", 9)
            )
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Add tab to notebook
            self.output_notebook.add(frame, text=tab_name)
            
            # Store reference to text widget
            self.doc_tabs[tab_name] = text_widget
        
        # Add a special "Preview" tab with side-by-side view
        self._create_preview_tab()
    
    def _create_preview_tab(self):
        """Create a preview tab with side-by-side markdown and HTML view."""
        # Create frame for preview tab
        preview_frame = tk.Frame(self.output_notebook)
        
        # Create PanedWindow for split view
        paned = tk.PanedWindow(preview_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Raw Markdown
        left_frame = tk.Frame(paned)
        left_label = tk.Label(left_frame, text="Markdown Source", font=("Arial", 10, "bold"))
        left_label.pack(side=tk.TOP, pady=5)
        
        markdown_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            width=40,
            height=25,
            font=("Courier", 9)
        )
        markdown_text.pack(fill=tk.BOTH, expand=True)
        paned.add(left_frame)
        
        # Right side - HTML Preview
        right_frame = tk.Frame(paned)
        right_label = tk.Label(right_frame, text="HTML Preview", font=("Arial", 10, "bold"))
        right_label.pack(side=tk.TOP, pady=5)
        
        # Try to use tkinterweb or tkhtmlview for HTML rendering if available
        # Otherwise fall back to plain text with basic formatting
        try:
            import tkinterweb
            html_widget = tkinterweb.HtmlFrame(right_frame)
            html_widget.pack(fill=tk.BOTH, expand=True)
            self.html_preview_type = 'tkinterweb'
        except ImportError:
            try:
                from tkhtmlview import HTMLLabel
                html_widget = HTMLLabel(right_frame, html="<p>Preview will appear here</p>")
                html_widget.pack(fill=tk.BOTH, expand=True)
                self.html_preview_type = 'tkhtmlview'
            except ImportError:
                # Fall back to text widget with basic formatting
                html_widget = scrolledtext.ScrolledText(
                    right_frame,
                    wrap=tk.WORD,
                    width=40,
                    height=25,
                    font=("Arial", 9),
                    background="#f9f9f9"
                )
                html_widget.pack(fill=tk.BOTH, expand=True)
                self.html_preview_type = 'text'
                self._log("HTML preview libraries not available. Using text preview. Install tkinterweb or tkhtmlview for better preview.", 'info')
        
        paned.add(right_frame)
        
        # Add tab to notebook
        self.output_notebook.add(preview_frame, text="Preview")
        
        # Store references
        self.preview_markdown = markdown_text
        self.preview_html = html_widget
        
        # Add Live Example tab if testbed is available
        if self.testbed is not None:
            self._create_live_example_tab()
    
    def _create_live_example_tab(self):
        """Create a Live Example tab for executing code snippets."""
        # Create frame for Live Example tab
        live_frame = tk.Frame(self.output_notebook)
        
        # Top section: Code snippet selector
        selector_frame = tk.Frame(live_frame)
        selector_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(selector_frame, text="Code Snippet:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.snippet_var = tk.StringVar()
        self.snippet_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.snippet_var,
            state='readonly',
            width=50
        )
        self.snippet_combo.pack(side=tk.LEFT, padx=5)
        self.snippet_combo.bind('<<ComboboxSelected>>', self._on_snippet_selected)
        
        # Refresh button
        refresh_btn = tk.Button(
            selector_frame,
            text="↻ Refresh Snippets",
            command=self._refresh_code_snippets,
            bg=self.THEME['button_bg']
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Create PanedWindow for split view
        paned = tk.PanedWindow(live_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left side - Code Editor
        left_frame = tk.Frame(paned)
        left_label = tk.Label(left_frame, text="Code", font=("Arial", 10, "bold"))
        left_label.pack(side=tk.TOP, pady=5)
        
        self.live_code_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            width=40,
            height=20,
            font=("Courier", 9)
        )
        self.live_code_text.pack(fill=tk.BOTH, expand=True)
        
        # Execution controls
        controls_frame = tk.Frame(left_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        self.execute_btn = tk.Button(
            controls_frame,
            text="▶ Execute Code",
            command=self._execute_code_snippet,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 10, "bold")
        )
        self.execute_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            controls_frame,
            text="Clear Output",
            command=self._clear_execution_output,
            bg=self.THEME['button_bg']
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        paned.add(left_frame)
        
        # Right side - Execution Output
        right_frame = tk.Frame(paned)
        right_label = tk.Label(right_frame, text="Output", font=("Arial", 10, "bold"))
        right_label.pack(side=tk.TOP, pady=5)
        
        # Status and badge display
        status_frame = tk.Frame(right_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.execution_status = tk.Label(
            status_frame,
            text="Ready",
            font=("Arial", 9),
            bg='#f0f0f0',
            padx=10,
            pady=5
        )
        self.execution_status.pack(side=tk.LEFT, padx=5)
        
        self.execution_badge = tk.Label(
            status_frame,
            text="",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=5
        )
        self.execution_badge.pack(side=tk.LEFT, padx=5)
        
        # Output text area
        self.live_output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=40,
            height=20,
            font=("Courier", 9),
            bg='#f9f9f9'
        )
        self.live_output_text.pack(fill=tk.BOTH, expand=True)
        
        paned.add(right_frame)
        
        # Add tab to notebook
        self.output_notebook.add(live_frame, text="Live Example")
        
        # Store references
        self.code_snippets = []
        self.current_snippet_index = -1
    
    def _refresh_code_snippets(self):
        """Extract and refresh code snippets from current documentation."""
        if not self.testbed:
            messagebox.showwarning("Testbed Unavailable", "Live testbed is not available.")
            return
        
        # Get markdown content from preview tab
        markdown_content = self.preview_markdown.get('1.0', tk.END)
        
        if not markdown_content or markdown_content.strip() == '':
            messagebox.showinfo("No Content", "Please generate documentation first.")
            return
        
        # Extract code snippets
        self.code_snippets = self.testbed.extract_code_snippets(markdown_content)
        
        if not self.code_snippets:
            messagebox.showinfo("No Code Snippets", "No executable code snippets found in the documentation.")
            self.snippet_combo['values'] = []
            return
        
        # Populate combo box
        snippet_labels = [
            f"Snippet {i+1}: {snippet.language.value} (line {snippet.line_number})"
            for i, snippet in enumerate(self.code_snippets)
        ]
        self.snippet_combo['values'] = snippet_labels
        
        if snippet_labels:
            self.snippet_combo.current(0)
            self._on_snippet_selected(None)
        
        self._log(f"Found {len(self.code_snippets)} code snippets", 'info')
    
    def _on_snippet_selected(self, event):
        """Handle snippet selection from dropdown."""
        selection = self.snippet_combo.current()
        if selection >= 0 and selection < len(self.code_snippets):
            self.current_snippet_index = selection
            snippet = self.code_snippets[selection]
            
            # Display code in editor
            self.live_code_text.delete('1.0', tk.END)
            self.live_code_text.insert('1.0', snippet.code)
            
            # Reset status
            self.execution_status.config(text=f"Ready - {snippet.language.value}", bg='#f0f0f0')
            self.execution_badge.config(text="")
    
    def _execute_code_snippet(self):
        """Execute the current code snippet in Docker container."""
        if not self.testbed:
            messagebox.showerror("Error", "Live testbed is not available.")
            return
        
        if self.current_snippet_index < 0:
            messagebox.showwarning("No Snippet", "Please select a code snippet to execute.")
            return
        
        # Check authentication if required
        if self.settings.testbed_require_auth and self.membership_manager:
            # For demo purposes, we'll assume user is authenticated
            # In a real implementation, you would have a login system
            pass
        
        snippet = self.code_snippets[self.current_snippet_index]
        code = self.live_code_text.get('1.0', tk.END).strip()
        
        if not code:
            messagebox.showwarning("Empty Code", "Code editor is empty.")
            return
        
        # Update status
        self.execution_status.config(text="Executing...", bg='#fff3cd')
        self.execute_btn.config(state='disabled')
        self.root.update()
        
        # Execute in background thread
        def execute():
            try:
                result = self.testbed.execute_code(code, snippet.language)
                
                # Update UI in main thread
                self.root.after(0, lambda: self._display_execution_result(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Execution Error", str(e)))
            finally:
                self.root.after(0, lambda: self.execute_btn.config(state='normal'))
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
    
    def _display_execution_result(self, result):
        """Display execution result in the output area."""
        # Clear output
        self.live_output_text.delete('1.0', tk.END)
        
        # Display result
        if result.status == ExecutionStatus.SUCCESS:
            self.execution_status.config(text="✓ Success", bg='#d4edda', fg='#155724')
            self.execution_badge.config(text=result.badge, bg='#44cc11', fg='white')
            self.live_output_text.insert('1.0', result.output)
        elif result.status == ExecutionStatus.FAILURE:
            self.execution_status.config(text="✗ Failed", bg='#f8d7da', fg='#721c24')
            self.execution_badge.config(text=result.badge, bg='#e05d44', fg='white')
            self.live_output_text.insert('1.0', f"Error:\n{result.error}")
        elif result.status == ExecutionStatus.TIMEOUT:
            self.execution_status.config(text="⏱ Timeout", bg='#fff3cd', fg='#856404')
            self.execution_badge.config(text=result.badge, bg='#fe7d37', fg='white')
            self.live_output_text.insert('1.0', f"Execution timed out after {self.settings.testbed_timeout}s")
        else:
            self.execution_status.config(text="⚠ Error", bg='#f8d7da', fg='#721c24')
            self.execution_badge.config(text=result.badge, bg='#9f9f9f', fg='white')
            self.live_output_text.insert('1.0', f"Error:\n{result.error}")
        
        # Add execution time
        self.live_output_text.insert(tk.END, f"\n\n--- Execution time: {result.execution_time:.2f}s ---")
        
        self._log(f"Code execution completed: {result.status.value}", 'info')
    
    def _clear_execution_output(self):
        """Clear execution output area."""
        self.live_output_text.delete('1.0', tk.END)
        self.execution_status.config(text="Ready", bg='#f0f0f0', fg='#000000')
        self.execution_badge.config(text="", bg=self.THEME['bg'])
    
    def _setup_drag_and_drop(self):
        """Setup drag and drop functionality for repository folders."""
        try:
            # Try to use tkinterdnd2 for native drag and drop support
            from tkinterdnd2 import DND_FILES, TkinterDnD
            
            # Check if root is already a TkinterDnD.Tk instance
            # If not, we can't add DnD to existing window, so we skip
            if not isinstance(self.root, TkinterDnD.Tk):
                self._log("Drag & drop requires TkinterDnD.Tk root window. Feature disabled.", 'info')
                return
            
            # Register the entry and main frame as drop targets
            self.repo_entry.drop_target_register(DND_FILES)
            self.main_frame.drop_target_register(DND_FILES)
            
            # Bind drop events
            self.repo_entry.dnd_bind('<<Drop>>', self._on_drop)
            self.main_frame.dnd_bind('<<Drop>>', self._on_drop)
            
            # Bind drag enter/leave for visual feedback
            self.repo_entry.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.repo_entry.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            self.main_frame.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.main_frame.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            
            self._log("Drag & drop support enabled", 'info')
            
        except ImportError:
            # tkinterdnd2 not available - drag and drop will not work
            # This is not critical, so we just log it
            self._log("tkinterdnd2 not installed. Drag & drop feature disabled. Install with: pip install tkinterdnd2", 'info')
    
    def _on_drop(self, event):
        """Handle file/folder drop event."""
        try:
            # Get the dropped data - could be file path or folder path
            data = event.data
            
            # Parse the dropped data (may contain multiple files)
            # The data format varies by platform, but typically contains file paths
            if isinstance(data, str):
                # Clean up the path (remove curly braces if present)
                path = data.strip('{}').strip()
                
                # Handle multiple files - take the first one
                if '\n' in path:
                    path = path.split('\n')[0].strip()
                
                # Handle space-separated paths (Windows style with quotes)
                if path.startswith('"') and '"' in path[1:]:
                    path = path.split('"')[1]
                elif ' ' in path and not os.path.exists(path):
                    # May have multiple files separated by spaces (Unix style)
                    path = path.split()[0]
                
                # Further clean path
                path = path.strip('{}').strip('"').strip("'").strip()
                
                # Verify the path exists
                if os.path.exists(path):
                    # Convert to absolute path
                    path = os.path.abspath(path)
                    
                    # Update the repo URL field
                    self.repo_url.set(path)
                    self._log(f"Repository path set via drag & drop: {path}")
                    self._update_status(f"Ready to scan: {os.path.basename(path)}")
                    
                    # Reset drag visual feedback
                    self._reset_drag_feedback()
                    return 'copy'
                else:
                    self._log(f"Invalid path dropped: {path}", 'warning')
                    messagebox.showwarning("Invalid Path", f"The dropped path does not exist:\n{path}")
            
        except Exception as e:
            self._log(f"Error handling drop: {str(e)}", 'error')
            messagebox.showerror("Drop Error", f"Failed to process dropped item:\n{str(e)}")
        
        # Reset visual feedback
        self._reset_drag_feedback()
        return 'none'
    
    def _on_drag_enter(self, event):
        """Handle drag enter event for visual feedback."""
        # Change background to highlight when dragging over
        try:
            self.main_frame.configure(bg=self.THEME['highlight'])
            self.repo_entry.configure(bg=self.THEME['highlight'])
        except:
            pass
    
    def _on_drag_leave(self, event):
        """Handle drag leave event to reset visual feedback."""
        # Reset background
        self._reset_drag_feedback()
    
    def _reset_drag_feedback(self):
        """Reset visual feedback after drag operation."""
        try:
            self.main_frame.configure(bg=self.THEME['bg'])
            self.repo_entry.configure(bg=self.THEME['entry_bg'])
        except:
            pass
    
    def _setup_logging(self):
        """Setup logging to capture messages."""
        # Create a custom handler that stores log messages
        class ListHandler(logging.Handler):
            def __init__(self, log_list):
                super().__init__()
                self.log_list = log_list
            
            def emit(self, record):
                log_entry = self.format(record)
                self.log_list.append(log_entry)
        
        # Setup logger
        self.logger = logging.getLogger('AccuDoc')
        self.logger.setLevel(logging.DEBUG)
        
        # Add our custom handler
        handler = ListHandler(self.log_messages)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info("AccuDoc initialized")
    
    def _log(self, message, level='info'):
        """Log a message."""
        if level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'debug':
            self.logger.debug(message)
    
    def _apply_theme(self):
        """Apply the theme to all widgets."""
        theme = self.THEME
        
        # Apply to root window
        self.root.configure(bg=theme['bg'])
        
        # Apply to main frame
        self.main_frame.configure(bg=theme['bg'])
        
        # Apply to labels
        for label in [self.title_label, self.url_label, self.status_label_text, 
                     self.status_label, self.output_label, self.detailed_progress_label]:
            label.configure(bg=theme['bg'], fg=theme['fg'])
        
        # Update status label color
        self.status_label.configure(fg=theme['status_fg'])
        
        # Apply to entry
        self.repo_entry.configure(
            bg=theme['entry_bg'],
            fg=theme['fg'],
            insertbackground=theme['fg'],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=theme['fg']
        )
        
        # Apply to buttons
        for button in [self.scan_button, self.browse_button, self.save_button, 
                      self.clear_button, self.recent_button, 
                      self.settings_button, self.favorites_button, self.log_button]:
            button.configure(
                bg=theme['button_bg'],
                fg=theme['fg'],
                activebackground=theme['highlight'],
                activeforeground=theme['fg'],
                relief=tk.FLAT
            )
        
        # Apply to text areas in tabs
        for tab_name, text_widget in self.doc_tabs.items():
            text_widget.configure(
                bg=theme['text_bg'],
                fg=theme['text_fg'],
                insertbackground=theme['text_fg'],
                selectbackground=theme['highlight'],
                selectforeground=theme['fg']
            )
        
        # Apply to recent menu
        self.recent_menu.configure(
            bg=theme['bg'],
            fg=theme['fg'],
            activebackground=theme['highlight'],
            activeforeground=theme['fg']
        )
        
        # Apply to favorites menu
        self.favorites_menu.configure(
            bg=theme['bg'],
            fg=theme['fg'],
            activebackground=theme['highlight'],
            activeforeground=theme['fg']
        )
        
    def _load_config(self):
        """Load configuration from config file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.recent_repos = config.get('recent_repos', [])
                    # Limit to 10 most recent
                    self.recent_repos = self.recent_repos[:10]
                    # Load favorites
                    self.favorite_repos = config.get('favorites', [])
        except Exception:
            self.recent_repos = []
            self.favorite_repos = []
    
    def _save_config(self):
        """Save configuration to config file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config = {
                'recent_repos': self.recent_repos,
                'favorites': self.favorite_repos
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass  # Fail silently if we can't save
    
    def _add_recent_repo(self, repo_path):
        """Add a repository to the recent list."""
        # Remove if already exists
        if repo_path in self.recent_repos:
            self.recent_repos.remove(repo_path)
        
        # Add to beginning
        self.recent_repos.insert(0, repo_path)
        
        # Limit to 10 items
        self.recent_repos = self.recent_repos[:10]
        
        # Save to disk
        self._save_config()
        
        # Update menu
        self._update_recent_menu()
    
    def _add_to_favorites(self, repo_path):
        """Add a repository to favorites."""
        if repo_path not in self.favorite_repos:
            self.favorite_repos.append(repo_path)
            self._save_config()
            self._update_favorites_menu()
            messagebox.showinfo("Favorites", "Repository added to favorites!")
        else:
            messagebox.showinfo("Favorites", "Repository is already in favorites!")
    
    def _remove_from_favorites(self, repo_path):
        """Remove a repository from favorites."""
        if repo_path in self.favorite_repos:
            self.favorite_repos.remove(repo_path)
            self._save_config()
            self._update_favorites_menu()
    
    def _update_favorites_menu(self):
        """Update the favorites menu."""
        self.favorites_menu.delete(0, tk.END)
        
        # Add current repo to favorites option
        current_repo = self.repo_url.get().strip()
        if current_repo:
            if current_repo not in self.favorite_repos:
                self.favorites_menu.add_command(
                    label="★ Add Current to Favorites",
                    command=lambda: self._add_to_favorites(current_repo)
                )
            else:
                self.favorites_menu.add_command(
                    label="☆ Remove Current from Favorites",
                    command=lambda: self._remove_from_favorites(current_repo)
                )
            self.favorites_menu.add_separator()
        
        if not self.favorite_repos:
            self.favorites_menu.add_command(
                label="No favorite repositories",
                state=tk.DISABLED
            )
        else:
            for repo in self.favorite_repos:
                # Shorten path for display
                display_path = repo
                if len(display_path) > 45:
                    display_path = "..." + display_path[-42:]
                
                # Create submenu for each favorite with options
                self.favorites_menu.add_command(
                    label=display_path,
                    command=lambda r=repo: self._select_favorite_repo(r)
                )
    
    def _select_favorite_repo(self, repo_path):
        """Select a repository from favorites."""
        self.repo_url.set(repo_path)
        self._update_favorites_menu()  # Update menu to show remove option
    
    def _update_recent_menu(self):
        """Update the recent repositories menu."""
        self.recent_menu.delete(0, tk.END)
        
        if not self.recent_repos:
            self.recent_menu.add_command(
                label="No recent repositories",
                state=tk.DISABLED
            )
        else:
            for repo in self.recent_repos:
                # Shorten path for display
                display_path = repo
                if len(display_path) > 50:
                    display_path = "..." + display_path[-47:]
                
                self.recent_menu.add_command(
                    label=display_path,
                    command=lambda r=repo: self._select_recent_repo(r)
                )
            
            self.recent_menu.add_separator()
            self.recent_menu.add_command(
                label="Clear Recent",
                command=self._clear_recent_repos
            )
    
    def _select_recent_repo(self, repo_path):
        """Select a repository from the recent list."""
        self.repo_url.set(repo_path)
    
    def _clear_recent_repos(self):
        """Clear the recent repositories list."""
        if messagebox.askyesno("Clear Recent", "Clear all recent repositories?"):
            self.recent_repos = []
            self._save_config()
            self._update_recent_menu()
        
    def _browse_local_folder(self):
        """Browse for a local folder."""
        folder_path = filedialog.askdirectory(title="Select Repository Folder")
        if folder_path:
            self.repo_url.set(folder_path)
            
    def _scan_repository(self):
        """Scan the repository and generate documentation."""
        repo_path = self.repo_url.get().strip()
        
        if not repo_path:
            messagebox.showwarning("Input Required", "Please enter a repository URL or path.")
            return
            
        if self.scanning:
            messagebox.showinfo("Scanning", "A scan is already in progress.")
            return
        
        # Start scanning in a separate thread
        thread = threading.Thread(target=self._scan_thread, args=(repo_path,))
        thread.daemon = True
        thread.start()
        
    def _scan_thread(self, repo_path):
        """Thread function to scan repository."""
        try:
            self.scanning = True
            self._log(f"Starting scan of repository: {repo_path}")
            self._update_status("Scanning repository...")
            self.progress.start()
            self.scan_button.config(state=tk.DISABLED)
            
            # Start timing
            import time
            start_time = time.time()
            
            # Clear previous output from all tabs
            for text_widget in self.doc_tabs.values():
                text_widget.delete(1.0, tk.END)
            
            # Initialize stats for use in progress callback
            stats = {}
            
            # Scan repository with progress callback
            def progress_callback(message):
                elapsed = time.time() - start_time
                # Rough estimation: scanning typically takes 0.1-0.5s per file
                est_total = stats.get('total_files', 100) * 0.2  # estimate
                if elapsed > 0:
                    progress_pct = min(int((elapsed / est_total) * 100), 95)
                    time_msg = f"{message} | Elapsed: {elapsed:.1f}s"
                    self.detailed_progress.set(time_msg)
                else:
                    self.detailed_progress.set(message)
                self._log(f"Scan progress: {message}", 'debug')
                self.root.update_idletasks()
            
            scanner = RepositoryScanner(repo_path, progress_callback=progress_callback)
            
            # Estimate time based on file count
            quick_scan_files = []
            if os.path.isdir(repo_path):
                # Quick count of files for estimation
                try:
                    for root, dirs, files in os.walk(repo_path):
                        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'}]
                        quick_scan_files.extend(files)
                        if len(quick_scan_files) > 1000:  # Cap at 1000 for estimation
                            break
                except:
                    pass
            
            file_count = len(quick_scan_files)
            if file_count > 0:
                est_time = file_count * 0.2  # 0.2 seconds per file estimate
                if est_time > 60:
                    est_str = f"{est_time/60:.1f} minutes"
                else:
                    est_str = f"{est_time:.0f} seconds"
                self.detailed_progress.set(f"Estimated time: ~{est_str} (analyzing {file_count} files)")
                self._log(f"Estimated scan time: {est_str} for {file_count} files")
                self.root.update_idletasks()
                time.sleep(0.5)  # Show estimation briefly
            
            repo_info = scanner.scan()
            scan_time = time.time() - start_time
            
            # Display statistics
            stats = repo_info.get('stats', {})
            stats_msg = f"Completed in {scan_time:.1f}s | Found: {stats.get('total_files', 0)} files, {stats.get('total_languages', 0)} languages, {stats.get('total_docs', 0)} docs"
            self.detailed_progress.set(stats_msg)
            self._log(f"Scan completed in {scan_time:.1f}s: {stats_msg}")
            
            self._update_status("Generating documentation...")
            self.root.update_idletasks()
            
            # Generate documentation
            self._log("Generating documentation sections...")
            generator = DocumentGenerator(repo_info)
            
            # Generate full documentation for first tab
            full_doc = generator.generate_all()
            self.doc_tabs["Full Documentation"].insert(tk.END, full_doc)
            
            # Generate individual sections for other tabs
            sections = {
                "Overview": generator._generate_header() + "\n\n" + generator._generate_overview(),
                "Technology Stack": generator._generate_technology_stack(),
                "Installation": generator._generate_installation(),
                "Usage": generator._generate_usage(),
                "Project Structure": generator._generate_project_structure(),
                "Changelog": generator._generate_changelog(),
                "Contributors": generator._generate_contributors()
            }
            
            for tab_name, content in sections.items():
                if content and tab_name in self.doc_tabs:
                    self.doc_tabs[tab_name].insert(tk.END, content)
            
            # Update preview tab with markdown and HTML
            self._update_preview(full_doc)
            
            # Add to recent repositories
            self._add_recent_repo(repo_path)
            
            self._update_status("Documentation generated successfully!")
            self._log("Documentation generation completed successfully")
            self.detailed_progress.set("")
            self.save_button.config(state=tk.NORMAL)
            self._apply_theme()  # Reapply theme after state changes
            
        except Exception as e:
            self._update_status(f"Error: {str(e)}")
            self._log(f"Error during scan: {str(e)}", 'error')
            self.detailed_progress.set("")
            messagebox.showerror("Error", f"Failed to scan repository:\n{str(e)}")
            
        finally:
            self.scanning = False
            self.progress.stop()
            self.scan_button.config(state=tk.NORMAL)
            self._apply_theme()  # Reapply theme after state changes
            
    def _save_documentation(self):
        """Save the generated documentation to a file."""
        # Get content from the current active tab
        current_tab_index = self.output_notebook.index(self.output_notebook.select())
        tab_text = self.output_notebook.tab(current_tab_index, "text")
        
        if tab_text in self.doc_tabs:
            text_widget = self.doc_tabs[tab_text]
            content = text_widget.get(1.0, tk.END)
        else:
            content = ""
        
        if not content.strip():
            messagebox.showwarning("No Content", "No documentation to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            title=f"Save Documentation - {tab_text}"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Documentation saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
                
    def _update_preview(self, markdown_content):
        """Update the preview tab with markdown and HTML rendering."""
        if not hasattr(self, 'preview_markdown') or not hasattr(self, 'preview_html'):
            return
        
        # Clear previous content
        self.preview_markdown.delete(1.0, tk.END)
        
        # Insert markdown content
        self.preview_markdown.insert(tk.END, markdown_content)
        
        # Convert markdown to HTML and display
        html_content = self._markdown_to_html(markdown_content)
        
        if self.html_preview_type == 'tkinterweb':
            self.preview_html.load_html(html_content)
        elif self.html_preview_type == 'tkhtmlview':
            self.preview_html.set_html(html_content)
        else:
            # Text-based preview - show simplified version
            self.preview_html.delete(1.0, tk.END)
            # Remove markdown syntax for basic preview
            simple_preview = self._simplify_markdown(markdown_content)
            self.preview_html.insert(tk.END, simple_preview)
    
    def _markdown_to_html(self, markdown_content):
        """Convert markdown to HTML."""
        try:
            # Try to use markdown library if available
            import markdown
            html = markdown.markdown(markdown_content, extensions=['extra', 'codehilite', 'tables'])
        except ImportError:
            # Fall back to basic conversion
            html = self._basic_markdown_to_html(markdown_content)
        
        # Wrap in HTML document with styling
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                }}
                h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                h3 {{ font-size: 1.25em; }}
                code {{
                    background-color: #f6f8fa;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                pre {{
                    background-color: #f6f8fa;
                    padding: 16px;
                    border-radius: 6px;
                    overflow-x: auto;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                ul, ol {{
                    padding-left: 2em;
                }}
                blockquote {{
                    border-left: 4px solid #dfe2e5;
                    padding-left: 16px;
                    color: #6a737d;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #dfe2e5;
                    padding: 6px 13px;
                }}
                th {{
                    background-color: #f6f8fa;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        return full_html
    
    def _basic_markdown_to_html(self, markdown_content):
        """Basic markdown to HTML conversion without external libraries."""
        import re
        
        html = markdown_content
        
        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html)
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # Lists (basic)
        lines = html.split('\n')
        in_list = False
        result = []
        for line in lines:
            if re.match(r'^\s*[-*+]\s+', line):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                item = re.sub(r'^\s*[-*+]\s+', '', line)
                result.append(f'<li>{item}</li>')
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append(line)
        if in_list:
            result.append('</ul>')
        
        html = '\n'.join(result)
        
        # Paragraphs
        html = re.sub(r'\n\n', r'</p><p>', html)
        html = f'<p>{html}</p>'
        html = html.replace('<p><h', '<h').replace('</h1></p>', '</h1>')
        html = html.replace('</h2></p>', '</h2>').replace('</h3></p>', '</h3>')
        html = html.replace('<p><ul>', '<ul>').replace('</ul></p>', '</ul>')
        html = html.replace('<p><pre>', '<pre>').replace('</pre></p>', '</pre>')
        
        return html
    
    def _simplify_markdown(self, markdown_content):
        """Simplify markdown for text-based preview (remove syntax)."""
        import re
        
        text = markdown_content
        
        # Remove code blocks
        text = re.sub(r'```.*?```', '[Code Block]', text, flags=re.DOTALL)
        
        # Remove inline code backticks
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove headers markers but keep text
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove bold/italic markers
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove list markers but keep indentation
        text = re.sub(r'^\s*[-*+]\s+', '  • ', text, flags=re.MULTILINE)
        
        return text
    
    def _clear_output(self):
        """Clear the output text area."""
        for text_widget in self.doc_tabs.values():
            text_widget.delete(1.0, tk.END)
        
        # Clear preview tab
        if hasattr(self, 'preview_markdown'):
            self.preview_markdown.delete(1.0, tk.END)
        if hasattr(self, 'preview_html'):
            if self.html_preview_type in ['tkinterweb', 'tkhtmlview']:
                try:
                    if self.html_preview_type == 'tkinterweb':
                        self.preview_html.load_html("<p>Preview will appear here</p>")
                    else:
                        self.preview_html.set_html("<p>Preview will appear here</p>")
                except:
                    pass
            else:
                self.preview_html.delete(1.0, tk.END)
        
        self.save_button.config(state=tk.DISABLED)
        self._update_status("Ready")
        self._apply_theme()  # Reapply theme after state changes
        
    def _update_status(self, message):
        """Update the status message."""
        self.status_text.set(message)
        self.root.update_idletasks()
    
    def _show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title(self.i18n.get('settings'))
        settings_window.geometry("450x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Apply theme to settings window
        theme = self.THEME
        settings_window.configure(bg=theme['bg'])
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General tab with language selection
        general_frame = tk.Frame(notebook, bg=theme['bg'], padx=20, pady=20)
        notebook.add(general_frame, text=self.i18n.get('general'))
        
        # Language setting
        lang_label = tk.Label(
            general_frame,
            text=self.i18n.get('language_setting') + ":",
            bg=theme['bg'],
            fg=theme['fg'],
            font=("Arial", 10)
        )
        lang_label.grid(row=0, column=0, sticky=tk.W, pady=10)
        
        # Language dropdown
        lang_var = tk.StringVar(value=self.settings.language)
        lang_options = ['auto'] + list(self.i18n.get_supported_languages().keys())
        lang_display = {
            'auto': self.i18n.get('auto_detect')
        }
        lang_display.update(self.i18n.get_supported_languages())
        
        lang_combo = ttk.Combobox(
            general_frame,
            textvariable=lang_var,
            values=[lang_display.get(code, code) for code in lang_options],
            state='readonly',
            width=25
        )
        lang_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # Map display names back to codes for saving
        display_to_code = {v: k for k, v in lang_display.items()}
        
        # Restart note
        restart_label = tk.Label(
            general_frame,
            text="⚠ " + self.i18n.get('restart_required'),
            bg=theme['bg'],
            fg='#ff6600',
            font=("Arial", 9, "italic"),
            wraplength=350,
            justify=tk.LEFT
        )
        restart_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # Live Testbed tab (if testbed is available)
        if TESTBED_AVAILABLE:
            testbed_frame = tk.Frame(notebook, bg=theme['bg'], padx=20, pady=20)
            notebook.add(testbed_frame, text="Live Testbed")
            
            # Enable/Disable testbed
            enable_var = tk.BooleanVar(value=self.settings.enable_live_testbed)
            enable_check = tk.Checkbutton(
                testbed_frame,
                text="Enable Live Testbed",
                variable=enable_var,
                bg=theme['bg'],
                fg=theme['fg'],
                font=("Arial", 10, "bold")
            )
            enable_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)
            
            # Timeout setting
            tk.Label(
                testbed_frame,
                text="Execution Timeout (seconds):",
                bg=theme['bg'],
                fg=theme['fg'],
                font=("Arial", 9)
            ).grid(row=1, column=0, sticky=tk.W, pady=5)
            
            timeout_var = tk.IntVar(value=self.settings.testbed_timeout)
            timeout_spin = tk.Spinbox(
                testbed_frame,
                from_=5,
                to=300,
                textvariable=timeout_var,
                width=10
            )
            timeout_spin.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
            
            # Memory limit setting
            tk.Label(
                testbed_frame,
                text="Memory Limit:",
                bg=theme['bg'],
                fg=theme['fg'],
                font=("Arial", 9)
            ).grid(row=2, column=0, sticky=tk.W, pady=5)
            
            memory_var = tk.StringVar(value=self.settings.testbed_memory_limit)
            memory_entry = tk.Entry(testbed_frame, textvariable=memory_var, width=12)
            memory_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
            
            # Network disabled setting
            network_var = tk.BooleanVar(value=self.settings.testbed_network_disabled)
            network_check = tk.Checkbutton(
                testbed_frame,
                text="Disable network access in containers",
                variable=network_var,
                bg=theme['bg'],
                fg=theme['fg'],
                font=("Arial", 9)
            )
            network_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
            
            # Require authentication setting
            auth_var = tk.BooleanVar(value=self.settings.testbed_require_auth)
            auth_check = tk.Checkbutton(
                testbed_frame,
                text="Require user authentication",
                variable=auth_var,
                bg=theme['bg'],
                fg=theme['fg'],
                font=("Arial", 9)
            )
            auth_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
            
            # Cache setting
            cache_var = tk.BooleanVar(value=self.settings.testbed_enable_cache)
            cache_check = tk.Checkbutton(
                testbed_frame,
                text="Enable execution cache",
                variable=cache_var,
                bg=theme['bg'],
                fg=theme['fg'],
                font=("Arial", 9)
            )
            cache_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
            
            # Info label
            info_label = tk.Label(
                testbed_frame,
                text="ℹ Live Testbed requires Docker to be installed and running.",
                bg=theme['bg'],
                fg='#666',
                font=("Arial", 8, "italic"),
                wraplength=350,
                justify=tk.LEFT
            )
            info_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # About tab
        about_frame = tk.Frame(notebook, bg=theme['bg'])
        notebook.add(about_frame, text=self.i18n.get('about'))
        
        about_text = tk.Label(
            about_frame,
            text="AccuDoc\n\nRepository Documentation Generator\n\nVersion 1.0\n\n"
                 "Automatically generates comprehensive\ndocumentation for your repositories.\n\n"
                 "© 2024 AccuDoc Project",
            bg=theme['bg'],
            fg=theme['fg'],
            justify=tk.CENTER,
            font=("Arial", 10)
        )
        about_text.pack(expand=True, pady=20)
        
        # Button frame
        button_frame = tk.Frame(settings_window, bg=theme['bg'])
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def apply_settings():
            """Apply and save settings."""
            # Get selected language code
            selected_display = lang_combo.get()
            selected_code = display_to_code.get(selected_display, 'auto')
            
            # Update settings
            self.settings.language = selected_code
            
            # Update testbed settings if available
            if TESTBED_AVAILABLE:
                self.settings.enable_live_testbed = enable_var.get()
                self.settings.testbed_timeout = timeout_var.get()
                self.settings.testbed_memory_limit = memory_var.get()
                self.settings.testbed_network_disabled = network_var.get()
                self.settings.testbed_require_auth = auth_var.get()
                self.settings.testbed_enable_cache = cache_var.get()
            
            self._save_settings()
            
            # Show confirmation
            messagebox.showinfo(
                self.i18n.get('success'),
                self.i18n.get('restart_required')
            )
        
        apply_button = tk.Button(
            button_frame,
            text=self.i18n.get('apply'),
            command=apply_settings,
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['highlight'],
            activeforeground=theme['fg'],
            cursor="hand2",
            padx=20,
            pady=5
        )
        apply_button.pack(side=tk.RIGHT, padx=5)
        
        close_button = tk.Button(
            button_frame,
            text=self.i18n.get('close'),
            command=settings_window.destroy,
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['highlight'],
            activeforeground=theme['fg'],
            cursor="hand2",
            padx=20,
            pady=5
        )
        close_button.pack(side=tk.RIGHT, padx=5)
    
    def _show_log_viewer(self):
        """Show the log viewer window."""
        log_window = tk.Toplevel(self.root)
        log_window.title("Log Viewer")
        log_window.geometry("700x500")
        log_window.transient(self.root)
        
        # Apply theme
        theme = self.THEME
        log_window.configure(bg=theme['bg'])
        
        # Create frame
        frame = tk.Frame(log_window, bg=theme['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label
        label = tk.Label(
            frame,
            text="Application Logs:",
            bg=theme['bg'],
            fg=theme['fg'],
            font=("Arial", 10, "bold")
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # Log text area
        log_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=("Courier", 9),
            bg=theme['text_bg'],
            fg=theme['text_fg']
        )
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert log messages
        if self.log_messages:
            log_text.insert(tk.END, '\n'.join(self.log_messages))
        else:
            log_text.insert(tk.END, "No log messages yet.")
        
        log_text.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = tk.Frame(log_window, bg=theme['bg'])
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Clear logs button
        def clear_logs():
            self.log_messages.clear()
            log_text.config(state=tk.NORMAL)
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, "Logs cleared.")
            log_text.config(state=tk.DISABLED)
            self._log("Logs cleared by user")
        
        clear_button = tk.Button(
            button_frame,
            text="Clear Logs",
            command=clear_logs,
            bg=theme['button_bg'],
            fg=theme['fg'],
            cursor="hand2",
            padx=15,
            pady=5
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=log_window.destroy,
            bg=theme['button_bg'],
            fg=theme['fg'],
            cursor="hand2",
            padx=15,
            pady=5
        )
        close_button.pack(side=tk.RIGHT, padx=5)
    
    def _open_new_window(self):
        """Open a new AccuDoc window."""
        try:
            # Create a new top-level window
            new_window = tk.Toplevel()
            
            # Try to use TkinterDnD for the new window if available
            try:
                from tkinterdnd2 import TkinterDnD
                # We can't convert an existing Toplevel to TkinterDnD.Tk
                # So we'll create a new root window instead
                new_window.destroy()
                new_window = TkinterDnD.Tk()
            except ImportError:
                # Just use the Toplevel we already created
                pass
            
            # Create a new AccuDoc instance in this window
            new_app = AccuDocGUI(new_window)
            
            self._log("Opened new window")
            
        except Exception as e:
            self._log(f"Error opening new window: {str(e)}", 'error')
            messagebox.showerror("Error", f"Failed to open new window:\n{str(e)}")
    
    def _show_about(self):
        """Show the about dialog."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About AccuDoc")
        about_window.geometry("500x400")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Apply theme
        theme = self.THEME
        about_window.configure(bg=theme['bg'])
        
        # Create frame
        frame = tk.Frame(about_window, bg=theme['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            frame,
            text="AccuDoc",
            font=("Arial", 24, "bold"),
            bg=theme['bg'],
            fg=theme['fg']
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = tk.Label(
            frame,
            text="Automated Repository Documentation Generator",
            font=("Arial", 12),
            bg=theme['bg'],
            fg=theme['fg']
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Description
        description = """AccuDoc automatically scans repositories and generates
comprehensive documentation based on what it finds.

Features:
• Automatic code analysis and documentation
• Multiple output formats (Markdown, HTML, PDF)
• Smart caching and parallel processing
• Drag & drop support
• Live preview with side-by-side view
• Multi-window support for productivity

Version: 1.0
License: GNU General Public License v3.0"""
        
        desc_label = tk.Label(
            frame,
            text=description,
            font=("Arial", 10),
            bg=theme['bg'],
            fg=theme['fg'],
            justify=tk.LEFT
        )
        desc_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(about_window, bg=theme['bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Close button
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=about_window.destroy,
            bg=theme['button_bg'],
            fg=theme['fg'],
            cursor="hand2",
            padx=20,
            pady=5
        )
        close_button.pack()



    def _load_or_create_settings(self) -> AccuDocSettings:
        """Load settings from file or create default settings."""
        try:
            settings = self.settings_manager.load_current_settings()
            if settings is None:
                return self.settings_manager.get_default_settings()
            return settings
        except Exception:
            # Return default settings if loading fails
            return self.settings_manager.get_default_settings()
    
    def _save_settings(self):
        """Save current settings to file."""
        try:
            self.settings_manager.save_current_settings(self.settings)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

def _apply_rtl_layout(self):
    """Apply right-to-left layout for RTL languages."""
    # Note: Full RTL support in Tkinter is limited
    # This is a basic implementation that reverses some layout elements
    try:
        # Set text direction for text widgets if supported
        # Most text widgets in Tkinter don't support RTL natively
        # This is a placeholder for future enhancement
        pass
    except Exception as e:
        logging.debug(f"RTL layout adjustment failed: {e}")


def main():
    """Main entry point for GUI application."""
    try:
        # Try to use TkinterDnD for drag-and-drop support
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        # Fall back to regular Tk if TkinterDnD is not available
        root = tk.Tk()
    
    app = AccuDocGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
