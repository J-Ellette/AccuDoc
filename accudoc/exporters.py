"""Export documentation to various formats."""

from typing import Dict, Optional
from pathlib import Path
import re


class MarkdownExporter:
    """Export documentation as Markdown (default format)."""
    
    def __init__(self, flavor: str = 'github'):
        """
        Initialize markdown exporter.
        
        Args:
            flavor: Markdown flavor to use (github, gitlab, commonmark)
        """
        self.flavor = flavor
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export as markdown file with specified flavor.
        
        Args:
            content: Markdown content
            output_path: Output file path
            
        Returns:
            Path to generated file
        """
        from accudoc.markdown_flavors import MarkdownFlavorManager
        
        # Convert to specified flavor
        converted_content = MarkdownFlavorManager.convert(content, self.flavor)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        return output_path


class HTMLExporter:
    """Export documentation as HTML."""
    
    def __init__(self, title: str = "Documentation", theme: str = "default"):
        """
        Initialize HTML exporter.
        
        Args:
            title: Document title
            theme: Color theme (default, dark, minimal)
        """
        self.title = title
        self.theme = theme
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export markdown content as HTML.
        
        Args:
            content: Markdown content
            output_path: Output file path
            
        Returns:
            Path to generated HTML file
        """
        html_content = self._markdown_to_html(content)
        full_html = self._wrap_html(html_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return output_path
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Convert basic markdown to HTML."""
        html = markdown
        
        # Headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Code blocks (with language support)
        def replace_code_block(match):
            lang = match.group(1) if match.group(1) else ''
            code = match.group(2)
            code = code.replace('<', '&lt;').replace('>', '&gt;')
            return f'<pre><code class="language-{lang}">{code}</code></pre>'
        
        html = re.sub(r'```(\w+)?\n(.*?)```', replace_code_block, html, flags=re.DOTALL)
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Lists (unordered)
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # Tables
        html = self._convert_tables(html)
        
        # Paragraphs (lines not in other elements)
        lines = html.split('\n')
        in_block = False
        result = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('<') or not stripped:
                result.append(line)
                if stripped.startswith('<pre>') or stripped.startswith('<ul>') or stripped.startswith('<table>'):
                    in_block = True
                elif stripped.startswith('</pre>') or stripped.startswith('</ul>') or stripped.startswith('</table>'):
                    in_block = False
            elif not in_block:
                result.append(f'<p>{line}</p>')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _convert_tables(self, html: str) -> str:
        """Convert markdown tables to HTML tables."""
        # Find table patterns
        table_pattern = r'(\|.+\|\n)+\|[-\s|]+\|\n(\|.+\|\n)+'
        
        def replace_table(match):
            lines = match.group(0).strip().split('\n')
            if len(lines) < 2:
                return match.group(0)
            
            # Parse header
            header = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            
            # Parse rows (skip separator line)
            rows = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
            
            # Build HTML table
            table_html = ['<table>']
            table_html.append('<thead><tr>')
            for cell in header:
                table_html.append(f'<th>{cell}</th>')
            table_html.append('</tr></thead>')
            table_html.append('<tbody>')
            for row in rows:
                table_html.append('<tr>')
                for cell in row:
                    table_html.append(f'<td>{cell}</td>')
                table_html.append('</tr>')
            table_html.append('</tbody>')
            table_html.append('</table>')
            
            return '\n'.join(table_html)
        
        return re.sub(table_pattern, replace_table, html, flags=re.MULTILINE)
    
    def _wrap_html(self, content: str) -> str:
        """Wrap content in full HTML document."""
        css = self._get_css()
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="container">
{content}
    </div>
</body>
</html>"""
    
    def _get_css(self) -> str:
        """Get CSS styling based on theme."""
        base_css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin: 24px 0 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        
        h1 { font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 0.3em; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }
        
        p {
            margin: 16px 0;
        }
        
        code {
            background: #f6f8fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
        }
        
        pre {
            background: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 16px 0;
        }
        
        pre code {
            background: none;
            padding: 0;
        }
        
        ul, ol {
            margin: 16px 0;
            padding-left: 2em;
        }
        
        li {
            margin: 8px 0;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        
        th, td {
            border: 1px solid #dfe2e5;
            padding: 8px 12px;
            text-align: left;
        }
        
        th {
            background: #f6f8fa;
            font-weight: 600;
        }
        
        tr:nth-child(even) {
            background: #f6f8fa;
        }
        
        strong {
            font-weight: 600;
        }
        
        em {
            font-style: italic;
        }
        
        hr {
            border: none;
            border-top: 1px solid #eaecef;
            margin: 24px 0;
        }
"""
        
        if self.theme == "dark":
            base_css += """
        body { background-color: #1a1a1a; color: #e0e0e0; }
        .container { background: #2d2d2d; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
        h1, h2 { border-bottom-color: #444; }
        code, pre { background: #1a1a1a; color: #e0e0e0; }
        a { color: #58a6ff; }
        th, td { border-color: #444; }
        th { background: #1a1a1a; }
        tr:nth-child(even) { background: #1a1a1a; }
"""
        elif self.theme == "minimal":
            base_css += """
        body { background-color: #ffffff; color: #000000; padding: 10px; }
        .container { 
            max-width: 800px; 
            background: #ffffff; 
            padding: 20px; 
            box-shadow: none; 
            border-radius: 0;
        }
        h1, h2, h3 { border-bottom: none; margin: 16px 0 8px; }
        h1 { font-size: 1.75em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.25em; }
        code, pre { background: #f0f0f0; }
        table { border: 1px solid #ccc; }
        th { background: #f0f0f0; }
"""
        elif self.theme == "corporate":
            base_css += """
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container { 
            background: #ffffff;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            border-radius: 10px;
            border-top: 5px solid #667eea;
        }
        h1 { 
            color: #667eea; 
            border-bottom: 3px solid #667eea;
            padding-bottom: 0.5em;
        }
        h2 { 
            color: #764ba2; 
            border-bottom: 2px solid #764ba2;
            padding-bottom: 0.3em;
        }
        h3 { color: #667eea; }
        code { 
            background: #f0f4ff; 
            color: #667eea;
            border: 1px solid #d0d9ff;
        }
        pre { 
            background: #f8f9ff; 
            border-left: 4px solid #667eea;
        }
        a { color: #667eea; font-weight: 500; }
        a:hover { color: #764ba2; }
        th { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        tr:nth-child(even) { background: #f8f9ff; }
"""
        
        return base_css


class TextExporter:
    """Export documentation as plain text."""
    
    def export(self, content: str, output_path: str) -> str:
        """Export as plain text file."""
        # Strip markdown formatting
        text = content
        
        # Remove markdown syntax
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Inline code
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)  # Headers
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return output_path


class ReStructuredTextExporter:
    """Export documentation as reStructuredText (RST) for Sphinx."""
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export markdown as reStructuredText.
        
        Args:
            content: Markdown content
            output_path: Output file path
            
        Returns:
            Path to generated file
        """
        rst = self._markdown_to_rst(content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rst)
        
        return output_path
    
    def _markdown_to_rst(self, markdown: str) -> str:
        """Convert markdown to reStructuredText."""
        rst = markdown
        
        # Headers (convert markdown # to RST format)
        lines = rst.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # H1: # Title -> Title\n======
            if line.startswith('# ') and not line.startswith('## '):
                title = line[2:].strip()
                result.append(title)
                result.append('=' * len(title))
                result.append('')
                i += 1
                continue
            
            # H2: ## Title -> Title\n------
            if line.startswith('## ') and not line.startswith('### '):
                title = line[3:].strip()
                result.append(title)
                result.append('-' * len(title))
                result.append('')
                i += 1
                continue
            
            # H3: ### Title -> Title\n~~~~~~
            if line.startswith('### ') and not line.startswith('#### '):
                title = line[4:].strip()
                result.append(title)
                result.append('~' * len(title))
                result.append('')
                i += 1
                continue
            
            # H4: #### Title -> Title\n^^^^^^
            if line.startswith('#### '):
                title = line[5:].strip()
                result.append(title)
                result.append('^' * len(title))
                result.append('')
                i += 1
                continue
            
            result.append(line)
            i += 1
        
        rst = '\n'.join(result)
        
        # Code blocks: ```lang\ncode``` -> .. code-block:: lang\n\n   code
        def replace_code_block(match):
            lang = match.group(1) if match.group(1) else 'text'
            code = match.group(2).strip()
            # Indent code with 3 spaces
            indented_code = '\n   '.join(code.split('\n'))
            return f'.. code-block:: {lang}\n\n   {indented_code}\n'
        
        rst = re.sub(r'```(\w+)?\n(.*?)```', replace_code_block, rst, flags=re.DOTALL)
        
        # Inline code: `code` -> ``code``
        rst = re.sub(r'`([^`]+)`', r'``\1``', rst)
        
        # Bold: **text** -> **text** (same in RST)
        
        # Italic: *text* -> *text* (same in RST)
        
        # Links: [text](url) -> `text <url>`_
        rst = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'`\1 <\2>`_', rst)
        
        # Unordered lists: - item -> * item
        rst = re.sub(r'^- ', r'* ', rst, flags=re.MULTILINE)
        
        # Tables: Convert markdown tables to RST grid tables
        rst = self._convert_tables_to_rst(rst)
        
        return rst
    
    def _convert_tables_to_rst(self, text: str) -> str:
        """Convert markdown tables to RST simple tables."""
        # Find markdown tables
        table_pattern = r'(\|.+\|\n)+\|[-\s|]+\|\n(\|.+\|\n)+'
        
        def replace_table(match):
            lines = match.group(0).strip().split('\n')
            if len(lines) < 2:
                return match.group(0)
            
            # Parse header
            header = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            
            # Parse rows (skip separator line)
            rows = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
            
            # Calculate column widths
            col_widths = [len(h) for h in header]
            for row in rows:
                for i, cell in enumerate(row):
                    if i < len(col_widths):
                        col_widths[i] = max(col_widths[i], len(cell))
            
            # Build RST simple table
            separator = '  '.join(['=' * w for w in col_widths])
            
            table_lines = [separator]
            table_lines.append('  '.join([h.ljust(w) for h, w in zip(header, col_widths)]))
            table_lines.append(separator)
            
            for row in rows:
                padded_row = [cell.ljust(col_widths[i]) if i < len(col_widths) else cell 
                             for i, cell in enumerate(row)]
                table_lines.append('  '.join(padded_row))
            
            table_lines.append(separator)
            
            return '\n'.join(table_lines)
        
        return re.sub(table_pattern, replace_table, text, flags=re.MULTILINE)


class AsciiDocExporter:
    """Export documentation as AsciiDoc format."""
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export markdown as AsciiDoc.
        
        Args:
            content: Markdown content
            output_path: Output file path
            
        Returns:
            Path to generated file
        """
        asciidoc = self._markdown_to_asciidoc(content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(asciidoc)
        
        return output_path
    
    def _markdown_to_asciidoc(self, markdown: str) -> str:
        """Convert markdown to AsciiDoc."""
        doc = markdown
        
        # Headers: # Title -> = Title
        doc = re.sub(r'^# (.+)$', r'= \1', doc, flags=re.MULTILINE)
        doc = re.sub(r'^## (.+)$', r'== \1', doc, flags=re.MULTILINE)
        doc = re.sub(r'^### (.+)$', r'=== \1', doc, flags=re.MULTILINE)
        doc = re.sub(r'^#### (.+)$', r'==== \1', doc, flags=re.MULTILINE)
        doc = re.sub(r'^##### (.+)$', r'===== \1', doc, flags=re.MULTILINE)
        
        # Code blocks: ```lang\ncode``` -> [source,lang]\n----\ncode\n----
        def replace_code_block(match):
            lang = match.group(1) if match.group(1) else 'text'
            code = match.group(2).strip()
            return f'[source,{lang}]\n----\n{code}\n----\n'
        
        doc = re.sub(r'```(\w+)?\n(.*?)```', replace_code_block, doc, flags=re.DOTALL)
        
        # Inline code: `code` -> `code` (same in AsciiDoc)
        
        # Bold: **text** -> *text*
        doc = re.sub(r'\*\*(.+?)\*\*', r'*\1*', doc)
        
        # Italic: *text* -> _text_
        doc = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'_\1_', doc)
        
        # Links: [text](url) -> link:url[text]
        doc = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'link:\2[\1]', doc)
        
        # Unordered lists: - item -> * item
        doc = re.sub(r'^- ', r'* ', doc, flags=re.MULTILINE)
        
        # Tables: Convert markdown tables to AsciiDoc tables
        doc = self._convert_tables_to_asciidoc(doc)
        
        return doc
    
    def _convert_tables_to_asciidoc(self, text: str) -> str:
        """Convert markdown tables to AsciiDoc tables."""
        table_pattern = r'(\|.+\|\n)+\|[-\s|]+\|\n(\|.+\|\n)+'
        
        def replace_table(match):
            lines = match.group(0).strip().split('\n')
            if len(lines) < 2:
                return match.group(0)
            
            # Parse header
            header = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            
            # Parse rows (skip separator line)
            rows = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
            
            # Build AsciiDoc table
            table_lines = ['[options="header"]', '|===']
            
            # Header
            table_lines.append('| ' + ' | '.join(header))
            
            # Rows
            for row in rows:
                table_lines.append('| ' + ' | '.join(row))
            
            table_lines.append('|===')
            
            return '\n'.join(table_lines)
        
        return re.sub(table_pattern, replace_table, text, flags=re.MULTILINE)


class LaTeXExporter:
    """Export documentation as LaTeX for academic papers."""
    
    def __init__(self, document_class: str = 'article'):
        """
        Initialize LaTeX exporter.
        
        Args:
            document_class: LaTeX document class (article, report, book)
        """
        self.document_class = document_class
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export markdown as LaTeX.
        
        Args:
            content: Markdown content
            output_path: Output file path
            
        Returns:
            Path to generated file
        """
        latex = self._markdown_to_latex(content)
        full_latex = self._wrap_latex(latex)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_latex)
        
        return output_path
    
    def _markdown_to_latex(self, markdown: str) -> str:
        """Convert markdown to LaTeX."""
        import hashlib
        
        latex = markdown
        
        # First, extract and mark code blocks to protect them
        code_blocks = []
        def save_code_block(match):
            idx = len(code_blocks)
            code_blocks.append(match.group(0))
            # Use a unique marker that won't be escaped or interfere with content
            marker = f"CODEBLOCK{hashlib.md5(str(idx).encode()).hexdigest()}ENDBLOCK"
            return marker
        
        latex = re.sub(r'```.*?```', save_code_block, latex, flags=re.DOTALL)
        
        # Headers (before escaping!)
        latex = re.sub(r'^# (.+)$', r'\\section{\1}', latex, flags=re.MULTILINE)
        latex = re.sub(r'^## (.+)$', r'\\subsection{\1}', latex, flags=re.MULTILINE)
        latex = re.sub(r'^### (.+)$', r'\\subsubsection{\1}', latex, flags=re.MULTILINE)
        latex = re.sub(r'^#### (.+)$', r'\\paragraph{\1}', latex, flags=re.MULTILINE)
        
        # Inline code (before escaping!)
        inline_codes = []
        def save_inline_code(match):
            idx = len(inline_codes)
            inline_codes.append(match.group(1))
            marker = f"INLINECODE{hashlib.md5(str(idx).encode()).hexdigest()}ENDINLINE"
            return marker
        
        latex = re.sub(r'`([^`]+)`', save_inline_code, latex)
        
        # Links (before escaping!)
        latex = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\\href{\2}{\1}', latex)
        
        # Bold and Italic (before escaping!)
        latex = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', latex)
        latex = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\\textit{\1}', latex)
        
        # Now escape special LaTeX characters in regular text
        latex = self._escape_latex_text(latex)
        
        # Unordered lists: - item -> \item item
        latex = self._convert_lists_to_latex(latex)
        
        # Tables
        latex = self._convert_tables_to_latex(latex)
        
        # Restore code blocks with proper formatting
        for i, code_block in enumerate(code_blocks):
            marker = f"CODEBLOCK{hashlib.md5(str(i).encode()).hexdigest()}ENDBLOCK"
            match = re.match(r'```(\w+)?\n(.*?)```', code_block, flags=re.DOTALL)
            if match:
                lang = match.group(1) if match.group(1) else 'text'
                code = match.group(2).strip()
                replacement = f'\\begin{{lstlisting}}[language={lang}]\n{code}\n\\end{{lstlisting}}\n'
                latex = latex.replace(marker, replacement)
        
        # Restore inline code
        for i, code in enumerate(inline_codes):
            marker = f"INLINECODE{hashlib.md5(str(i).encode()).hexdigest()}ENDINLINE"
            latex = latex.replace(marker, f'\\texttt{{{code}}}')
        
        return latex
    
    def _escape_latex_text(self, text: str) -> str:
        """Escape special LaTeX characters in regular text."""
        # Build result character by character, but protect LaTeX commands
        result = []
        i = 0
        
        while i < len(text):
            # Check if this is the start of a LaTeX command
            if text[i] == '\\':
                # Find the end of the command (including any {...} arguments)
                cmd_start = i
                i += 1
                
                # Skip command name
                while i < len(text) and (text[i].isalnum() or text[i] in '*@'):
                    i += 1
                
                # Skip any arguments in {...}
                while i < len(text) and text[i] in ' \t':
                    i += 1
                
                if i < len(text) and text[i] == '{':
                    brace_count = 1
                    i += 1
                    while i < len(text) and brace_count > 0:
                        if text[i] == '{':
                            brace_count += 1
                        elif text[i] == '}':
                            brace_count -= 1
                        i += 1
                
                # Add the entire command as-is
                result.append(text[cmd_start:i])
                continue
            
            # Not a LaTeX command, escape special characters
            char = text[i]
            if char == '&':
                result.append('\\&')
            elif char == '%':
                result.append('\\%')
            elif char == '$':
                result.append('\\$')
            elif char == '_':
                result.append('\\_')
            elif char == '~':
                result.append('\\textasciitilde{}')
            elif char == '^':
                result.append('\\textasciicircum{}')
            elif char == '#':
                result.append('\\#')
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def _convert_lists_to_latex(self, text: str) -> str:
        """Convert markdown lists to LaTeX itemize/enumerate."""
        lines = text.split('\n')
        result = []
        in_list = False
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result.append('\\begin{itemize}')
                    in_list = True
                item = line.strip()[2:]
                result.append(f'\\item {item}')
            else:
                if in_list:
                    result.append('\\end{itemize}')
                    in_list = False
                result.append(line)
        
        if in_list:
            result.append('\\end{itemize}')
        
        return '\n'.join(result)
    
    def _convert_tables_to_latex(self, text: str) -> str:
        """Convert markdown tables to LaTeX tables."""
        table_pattern = r'(\|.+\|\n)+\|[-\s|]+\|\n(\|.+\|\n)+'
        
        def replace_table(match):
            lines = match.group(0).strip().split('\n')
            if len(lines) < 2:
                return match.group(0)
            
            # Parse header
            header = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            num_cols = len(header)
            
            # Parse rows (skip separator line)
            rows = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
            
            # Build LaTeX table
            col_format = '|' + 'l|' * num_cols
            table_lines = [
                '\\begin{table}[h]',
                '\\centering',
                f'\\begin{{tabular}}{{{col_format}}}',
                '\\hline'
            ]
            
            # Header
            table_lines.append(' & '.join(header) + ' \\\\')
            table_lines.append('\\hline')
            
            # Rows
            for row in rows:
                table_lines.append(' & '.join(row) + ' \\\\')
            
            table_lines.extend([
                '\\hline',
                '\\end{tabular}',
                '\\end{table}'
            ])
            
            return '\n'.join(table_lines)
        
        return re.sub(table_pattern, replace_table, text, flags=re.MULTILINE)
    
    def _wrap_latex(self, content: str) -> str:
        """Wrap content in full LaTeX document."""
        return f"""\\documentclass[12pt]{{{self.document_class}}}

% Packages
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{hyperref}}
\\usepackage{{listings}}
\\usepackage{{graphicx}}
\\usepackage{{xcolor}}

% Code listing settings
\\lstset{{
    basicstyle=\\ttfamily\\small,
    breaklines=true,
    frame=single,
    backgroundcolor=\\color{{gray!10}},
    keywordstyle=\\color{{blue}},
    commentstyle=\\color{{green!50!black}},
    stringstyle=\\color{{red}}
}}

% Hyperref settings
\\hypersetup{{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=cyan,
}}

\\begin{{document}}

{content}

\\end{{document}}
"""


class DocumentExporter:
    """Main exporter class that handles multiple formats."""
    
    SUPPORTED_FORMATS = {
        'markdown': MarkdownExporter,
        'md': MarkdownExporter,
        'html': HTMLExporter,
        'txt': TextExporter,
        'text': TextExporter,
        'pdf': 'PDFExporter',  # Lazy loaded
        'rst': ReStructuredTextExporter,
        'restructuredtext': ReStructuredTextExporter,
        'asciidoc': AsciiDocExporter,
        'adoc': AsciiDocExporter,
        'latex': LaTeXExporter,
        'tex': LaTeXExporter,
    }
    
    @classmethod
    def export(cls, content: str, output_path: str, format: str = 'markdown', 
               title: str = "Documentation", theme: str = "default",
               markdown_flavor: str = "github") -> str:
        """
        Export documentation to specified format.
        
        Args:
            content: Documentation content (markdown)
            output_path: Output file path
            format: Output format (markdown, html, txt, pdf)
            title: Document title (for HTML/PDF)
            theme: Theme for HTML export (default, dark, minimal, corporate)
            markdown_flavor: Markdown flavor for markdown export (github, gitlab, commonmark)
            
        Returns:
            Path to generated file
        """
        format_lower = format.lower()
        
        if format_lower not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Supported formats: {', '.join(cls.SUPPORTED_FORMATS.keys())}")
        
        exporter_class = cls.SUPPORTED_FORMATS[format_lower]
        
        # Handle PDF export (requires HTML conversion first)
        if format_lower == 'pdf':
            from accudoc.pdf_exporter import export_to_pdf
            from pathlib import Path as PathLib
            
            # First generate HTML content
            html_exporter = HTMLExporter(title=title, theme=theme)
            html_content = html_exporter._markdown_to_html(content)
            full_html = html_exporter._wrap_html(html_content)
            
            # Then convert to PDF
            return str(export_to_pdf(full_html, PathLib(output_path), title))
        
        if exporter_class == HTMLExporter:
            exporter = exporter_class(title=title, theme=theme)
        elif exporter_class == MarkdownExporter:
            exporter = exporter_class(flavor=markdown_flavor)
        else:
            exporter = exporter_class()
        
        return exporter.export(content, output_path)
    
    @classmethod
    def get_supported_formats(cls) -> list:
        """Get list of supported export formats."""
        return list(set(cls.SUPPORTED_FORMATS.keys()))
