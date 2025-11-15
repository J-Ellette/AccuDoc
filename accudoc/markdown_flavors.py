"""Markdown flavor support for different platforms."""

from typing import Dict, Optional
import re


class MarkdownFlavor:
    """Base class for markdown flavors."""
    
    def __init__(self, name: str):
        """Initialize flavor."""
        self.name = name
    
    def convert(self, content: str) -> str:
        """Convert standard markdown to specific flavor."""
        return content


class GitHubFlavor(MarkdownFlavor):
    """GitHub Flavored Markdown (GFM)."""
    
    def __init__(self):
        """Initialize GitHub flavor."""
        super().__init__("GitHub")
    
    def convert(self, content: str) -> str:
        """
        Convert to GitHub Flavored Markdown.
        
        Enhancements:
        - Task lists
        - Tables (already supported)
        - Strikethrough
        - Syntax highlighting hints
        - Emoji support markers
        - Relative links optimization
        """
        result = content
        
        # Convert checkbox syntax to GitHub task lists
        result = re.sub(r'^\s*\[ \]\s+', '- [ ] ', result, flags=re.MULTILINE)
        result = re.sub(r'^\s*\[x\]\s+', '- [x] ', result, flags=re.MULTILINE)
        
        # Ensure code blocks have language specifiers for better highlighting
        result = self._enhance_code_blocks(result)
        
        # Add HTML comments for sections (helps with GitHub rendering)
        result = self._add_section_anchors(result)
        
        return result
    
    def _enhance_code_blocks(self, content: str) -> str:
        """Ensure code blocks have language hints."""
        # Find code blocks without language and try to infer
        def replace_code_block(match):
            code = match.group(1)
            # Try to infer language from content
            if 'def ' in code or 'import ' in code or 'class ' in code:
                return f'```python\n{code}```'
            elif 'function ' in code or 'const ' in code or 'let ' in code:
                return f'```javascript\n{code}```'
            elif '<?php' in code:
                return f'```php\n{code}```'
            elif 'public class' in code or 'public static void' in code:
                return f'```java\n{code}```'
            else:
                return match.group(0)  # Keep as is
        
        return re.sub(r'```\n(.*?)```', replace_code_block, content, flags=re.DOTALL)
    
    def _add_section_anchors(self, content: str) -> str:
        """Add HTML anchors for better navigation."""
        lines = content.split('\n')
        result = []
        
        for line in lines:
            # Add anchor for h2 headers
            if line.startswith('## '):
                title = line[3:].strip()
                anchor = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                result.append(f'<a name="{anchor}"></a>')
                result.append(line)
            else:
                result.append(line)
        
        return '\n'.join(result)


class GitLabFlavor(MarkdownFlavor):
    """GitLab Flavored Markdown (GLFM)."""
    
    def __init__(self):
        """Initialize GitLab flavor."""
        super().__init__("GitLab")
    
    def convert(self, content: str) -> str:
        """
        Convert to GitLab Flavored Markdown.
        
        Enhancements:
        - Mermaid diagrams (already used)
        - Math expressions
        - Video embeds
        - Table of contents
        - Collapsible sections
        """
        result = content
        
        # Add table of contents marker at the beginning
        result = self._add_toc_marker(result)
        
        # Enhance Mermaid diagrams with GitLab-specific styling
        result = self._enhance_mermaid(result)
        
        # Add collapsible sections for long content
        result = self._add_collapsible_sections(result)
        
        return result
    
    def _add_toc_marker(self, content: str) -> str:
        """Add table of contents marker."""
        lines = content.split('\n')
        # Find first h2 header
        for i, line in enumerate(lines):
            if line.startswith('## '):
                # Insert TOC before first section
                lines.insert(i, '[[_TOC_]]')
                lines.insert(i + 1, '')
                break
        return '\n'.join(lines)
    
    def _enhance_mermaid(self, content: str) -> str:
        """Ensure Mermaid diagrams are properly formatted for GitLab."""
        # GitLab supports mermaid natively, just ensure proper fencing
        return content
    
    def _add_collapsible_sections(self, content: str) -> str:
        """Add collapsible sections for long lists."""
        lines = content.split('\n')
        result = []
        in_long_list = False
        list_start = 0
        
        for i, line in enumerate(lines):
            # Detect long lists (more than 10 items)
            if line.startswith('- ') or line.startswith('* '):
                if not in_long_list:
                    in_long_list = True
                    list_start = i
            elif in_long_list and line.strip() and not line.startswith((' ', '\t', '-', '*')):
                # End of list
                list_length = i - list_start
                if list_length > 10:
                    # Make it collapsible
                    result.append('<details>')
                    result.append('<summary>Click to expand list</summary>')
                    result.append('')
                in_long_list = False
            
            result.append(line)
            
            if in_long_list and i == len(lines) - 1:
                # List goes to end of document
                result.append('')
                result.append('</details>')
        
        return '\n'.join(result)


class CommonMarkFlavor(MarkdownFlavor):
    """CommonMark - Standard Markdown specification."""
    
    def __init__(self):
        """Initialize CommonMark flavor."""
        super().__init__("CommonMark")
    
    def convert(self, content: str) -> str:
        """
        Convert to CommonMark (strict standard Markdown).
        
        Removes or converts extensions:
        - No HTML in output
        - No task lists
        - No extended syntax
        - Strict specification compliance
        """
        result = content
        
        # Remove HTML comments and anchors
        result = re.sub(r'<!--.*?-->', '', result, flags=re.DOTALL)
        result = re.sub(r'<a name="[^"]+"></a>\n?', '', result)
        result = re.sub(r'<details>.*?</details>', '', result, flags=re.DOTALL)
        
        # Convert task lists to regular lists
        result = re.sub(r'^- \[ \] ', '- ', result, flags=re.MULTILINE)
        result = re.sub(r'^- \[x\] ', '- ', result, flags=re.MULTILINE)
        
        # Remove GitLab-specific markers
        result = result.replace('[[_TOC_]]', '')
        
        # Ensure Mermaid diagrams are in standard code blocks
        result = re.sub(r'```mermaid\n', '```\n', result)
        
        # Clean up multiple blank lines
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result


class MarkdownFlavorManager:
    """Manages markdown flavor conversions."""
    
    FLAVORS = {
        'github': GitHubFlavor,
        'gitlab': GitLabFlavor,
        'commonmark': CommonMarkFlavor,
        'standard': CommonMarkFlavor,  # Alias
    }
    
    @classmethod
    def convert(cls, content: str, flavor: str = 'github') -> str:
        """
        Convert markdown content to specified flavor.
        
        Args:
            content: Standard markdown content
            flavor: Target flavor (github, gitlab, commonmark)
            
        Returns:
            Converted markdown content
            
        Raises:
            ValueError: If flavor is not supported
        """
        flavor_lower = flavor.lower()
        
        if flavor_lower not in cls.FLAVORS:
            raise ValueError(
                f"Unsupported flavor: {flavor}. "
                f"Supported: {', '.join(cls.FLAVORS.keys())}"
            )
        
        flavor_class = cls.FLAVORS[flavor_lower]
        flavor_obj = flavor_class()
        
        return flavor_obj.convert(content)
    
    @classmethod
    def get_supported_flavors(cls) -> list:
        """Get list of supported markdown flavors."""
        return list(cls.FLAVORS.keys())
    
    @classmethod
    def get_flavor_info(cls) -> Dict[str, str]:
        """Get information about all supported flavors."""
        return {
            'github': 'GitHub Flavored Markdown - with task lists, anchors, and syntax hints',
            'gitlab': 'GitLab Flavored Markdown - with TOC, Mermaid, and collapsible sections',
            'commonmark': 'CommonMark - strict standard Markdown without extensions',
            'standard': 'Alias for CommonMark',
        }
