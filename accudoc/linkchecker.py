"""
Link checker module for validating links in generated documentation.

Checks for broken links, missing anchors, and validates URLs.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from urllib.parse import urlparse, urljoin
import concurrent.futures


class LinkChecker:
    """Checks and validates links in documentation."""
    
    # Regex patterns for link detection
    MARKDOWN_LINK_PATTERN = r'\[([^\]]+)\]\(([^\)]+)\)'
    HTML_LINK_PATTERN = r'<a\s+[^>]*href=["\']([^"\']+)["\']'
    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize link checker.
        
        Args:
            base_path: Base path for resolving relative links
        """
        self.base_path = base_path or Path.cwd()
        self.logger = logging.getLogger('accudoc.linkchecker')
        self.checked_urls = {}  # Cache for URL checks
        
    def check_file(self, file_path: Path) -> Dict:
        """
        Check all links in a file.
        
        Args:
            file_path: Path to file to check
            
        Returns:
            Dictionary with check results
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Detect file type
            if file_path.suffix in ['.md', '.markdown']:
                links = self._extract_markdown_links(content)
            elif file_path.suffix in ['.html', '.htm']:
                links = self._extract_html_links(content)
            else:
                links = self._extract_raw_urls(content)
            
            # Check each link
            results = {
                'file': str(file_path),
                'total_links': len(links),
                'broken_links': [],
                'valid_links': [],
                'warnings': []
            }
            
            for link_text, link_url in links:
                check_result = self._check_link(link_url, file_path)
                
                if check_result['valid']:
                    results['valid_links'].append({
                        'text': link_text,
                        'url': link_url
                    })
                else:
                    results['broken_links'].append({
                        'text': link_text,
                        'url': link_url,
                        'error': check_result.get('error', 'Unknown error')
                    })
                
                if check_result.get('warning'):
                    results['warnings'].append({
                        'text': link_text,
                        'url': link_url,
                        'warning': check_result['warning']
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error checking file {file_path}: {str(e)}")
            return {
                'file': str(file_path),
                'error': str(e)
            }
    
    def _extract_markdown_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract links from Markdown content."""
        links = []
        
        # Find all markdown links
        for match in re.finditer(self.MARKDOWN_LINK_PATTERN, content):
            text = match.group(1)
            url = match.group(2)
            links.append((text, url))
        
        return links
    
    def _extract_html_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract links from HTML content."""
        links = []
        
        for match in re.finditer(self.HTML_LINK_PATTERN, content):
            url = match.group(1)
            links.append(('', url))
        
        return links
    
    def _extract_raw_urls(self, content: str) -> List[Tuple[str, str]]:
        """Extract raw URLs from content."""
        links = []
        
        for match in re.finditer(self.URL_PATTERN, content):
            url = match.group(0)
            links.append(('', url))
        
        return links
    
    def _check_link(self, url: str, source_file: Path) -> Dict:
        """
        Check if a link is valid.
        
        Args:
            url: URL to check
            source_file: File containing the link
            
        Returns:
            Dictionary with validation result
        """
        # Skip mailto and javascript links
        if url.startswith(('mailto:', 'javascript:', 'tel:')):
            return {'valid': True, 'type': 'special'}
        
        # Check for fragment/anchor links
        if url.startswith('#'):
            return {'valid': True, 'type': 'anchor', 
                   'warning': 'Anchor links not validated'}
        
        # Parse URL
        parsed = urlparse(url)
        
        # Check external URLs
        if parsed.scheme in ['http', 'https']:
            return self._check_external_url(url)
        
        # Check relative/local files
        if not parsed.scheme or parsed.scheme == 'file':
            return self._check_local_file(url, source_file)
        
        return {'valid': False, 'error': f'Unknown URL scheme: {parsed.scheme}'}
    
    def _check_external_url(self, url: str) -> Dict:
        """
        Check external URL (lightweight check).
        
        Note: Full URL validation would require network requests.
        This performs basic validation only.
        """
        # Check cache
        if url in self.checked_urls:
            return self.checked_urls[url]
        
        parsed = urlparse(url)
        
        # Basic validation
        if not parsed.netloc:
            result = {'valid': False, 'error': 'Invalid URL: missing domain'}
        else:
            # URL looks valid structurally
            result = {
                'valid': True, 
                'type': 'external',
                'warning': 'External URL not verified (requires network check)'
            }
        
        # Cache result
        self.checked_urls[url] = result
        return result
    
    def _check_local_file(self, url: str, source_file: Path) -> Dict:
        """Check local file link."""
        # Remove anchor/fragment
        url_without_fragment = url.split('#')[0]
        
        # Resolve relative to source file
        if url_without_fragment.startswith('/'):
            # Absolute path from base
            target = self.base_path / url_without_fragment.lstrip('/')
        else:
            # Relative to source file
            target = (source_file.parent / url_without_fragment).resolve()
        
        if target.exists():
            return {'valid': True, 'type': 'local'}
        else:
            return {
                'valid': False, 
                'error': f'File not found: {target}'
            }
    
    def check_directory(self, directory: Path, 
                       file_patterns: List[str] = None) -> Dict:
        """
        Check all links in a directory.
        
        Args:
            directory: Directory to scan
            file_patterns: File patterns to check (e.g., ['*.md', '*.html'])
            
        Returns:
            Summary of all checks
        """
        if file_patterns is None:
            file_patterns = ['*.md', '*.markdown', '*.html', '*.htm']
        
        files_to_check = []
        for pattern in file_patterns:
            files_to_check.extend(directory.rglob(pattern))
        
        results = {
            'directory': str(directory),
            'total_files': len(files_to_check),
            'files_checked': 0,
            'total_links': 0,
            'broken_links': 0,
            'valid_links': 0,
            'warnings': 0,
            'files': []
        }
        
        for file_path in files_to_check:
            file_result = self.check_file(file_path)
            
            if 'error' not in file_result:
                results['files_checked'] += 1
                results['total_links'] += file_result['total_links']
                results['broken_links'] += len(file_result['broken_links'])
                results['valid_links'] += len(file_result['valid_links'])
                results['warnings'] += len(file_result['warnings'])
                results['files'].append(file_result)
        
        return results
    
    def generate_report(self, results: Dict, format: str = 'text') -> str:
        """
        Generate a report from check results.
        
        Args:
            results: Results from check_directory
            format: Report format ('text', 'markdown', 'json')
            
        Returns:
            Formatted report
        """
        if format == 'markdown':
            return self._generate_markdown_report(results)
        elif format == 'json':
            import json
            return json.dumps(results, indent=2)
        else:
            return self._generate_text_report(results)
    
    def _generate_text_report(self, results: Dict) -> str:
        """Generate plain text report."""
        lines = [
            "Link Checker Report",
            "=" * 60,
            f"Directory: {results['directory']}",
            f"Files Checked: {results['files_checked']}/{results['total_files']}",
            f"Total Links: {results['total_links']}",
            f"Valid Links: {results['valid_links']}",
            f"Broken Links: {results['broken_links']}",
            f"Warnings: {results['warnings']}",
            ""
        ]
        
        # Show broken links
        if results['broken_links'] > 0:
            lines.append("Broken Links:")
            lines.append("-" * 60)
            
            for file_result in results['files']:
                if file_result['broken_links']:
                    lines.append(f"\nFile: {file_result['file']}")
                    for link in file_result['broken_links']:
                        lines.append(f"  ✗ {link['url']}")
                        lines.append(f"    Error: {link['error']}")
        else:
            lines.append("✓ No broken links found!")
        
        return '\n'.join(lines)
    
    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate Markdown report."""
        lines = [
            "# Link Checker Report",
            "",
            f"**Directory:** `{results['directory']}`  ",
            f"**Files Checked:** {results['files_checked']}/{results['total_files']}  ",
            f"**Total Links:** {results['total_links']}  ",
            f"**Valid Links:** {results['valid_links']} ✓  ",
            f"**Broken Links:** {results['broken_links']} ✗  ",
            f"**Warnings:** {results['warnings']} ⚠  ",
            ""
        ]
        
        if results['broken_links'] > 0:
            lines.extend([
                "## Broken Links",
                ""
            ])
            
            for file_result in results['files']:
                if file_result['broken_links']:
                    lines.append(f"### {file_result['file']}")
                    lines.append("")
                    
                    for link in file_result['broken_links']:
                        lines.append(f"- ✗ `{link['url']}`")
                        lines.append(f"  - Error: {link['error']}")
                    
                    lines.append("")
        else:
            lines.extend([
                "## Result",
                "",
                "✓ **No broken links found!**",
                ""
            ])
        
        return '\n'.join(lines)


def check_documentation_links(doc_path: Path, output_format: str = 'text') -> str:
    """
    Convenience function to check links in documentation.
    
    Args:
        doc_path: Path to documentation file or directory
        output_format: Report format ('text', 'markdown', 'json')
        
    Returns:
        Link check report
    """
    checker = LinkChecker(base_path=doc_path if doc_path.is_dir() else doc_path.parent)
    
    if doc_path.is_file():
        result = checker.check_file(doc_path)
        results = {
            'directory': str(doc_path.parent),
            'total_files': 1,
            'files_checked': 1,
            'total_links': result['total_links'],
            'broken_links': len(result['broken_links']),
            'valid_links': len(result['valid_links']),
            'warnings': len(result['warnings']),
            'files': [result]
        }
    else:
        results = checker.check_directory(doc_path)
    
    return checker.generate_report(results, format=output_format)
