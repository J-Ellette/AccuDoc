"""
Documentation search system for AccuDoc.

Search through AccuDoc's own documentation and help files.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """A search result."""
    
    file: str
    line_number: int
    line_content: str
    context_before: List[str]
    context_after: List[str]
    relevance_score: float = 0.0
    
    def format(self) -> str:
        """Format result for display."""
        lines = []
        lines.append(f"{self.file}:{self.line_number}")
        
        # Add context before
        for i, line in enumerate(self.context_before):
            lines.append(f"  {self.line_number - len(self.context_before) + i}: {line}")
        
        # Add matched line (highlighted)
        lines.append(f"➤ {self.line_number}: {self.line_content}")
        
        # Add context after
        for i, line in enumerate(self.context_after):
            lines.append(f"  {self.line_number + i + 1}: {line}")
        
        return "\n".join(lines)


class DocumentationSearch:
    """
    Search system for AccuDoc documentation.
    
    Searches through README, help files, and other documentation.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize documentation search.
        
        Args:
            repo_path: Path to AccuDoc repository (defaults to current directory)
        """
        if repo_path:
            self.repo_path = Path(repo_path)
        else:
            # Try to find AccuDoc root
            current = Path(__file__).parent
            while current.parent != current:
                if (current / "README.md").exists():
                    self.repo_path = current
                    break
                current = current.parent
            else:
                self.repo_path = Path.cwd()
        
        self.doc_files = self._find_documentation_files()
    
    def _find_documentation_files(self) -> List[Path]:
        """Find all documentation files."""
        doc_files = []
        
        # Common documentation file patterns
        patterns = [
            "README.md",
            "*.md",
            "docs/**/*.md",
            "docs/**/*.rst",
            "*.rst",
        ]
        
        for pattern in patterns:
            doc_files.extend(self.repo_path.glob(pattern))
        
        # Remove duplicates
        return list(set(doc_files))
    
    def _calculate_relevance(
        self,
        query: str,
        line: str,
        file_name: str
    ) -> float:
        """
        Calculate relevance score for a match.
        
        Args:
            query: Search query
            line: Matched line
            file_name: File name
            
        Returns:
            Relevance score (0-1)
        """
        score = 0.0
        query_lower = query.lower()
        line_lower = line.lower()
        
        # Exact match bonus
        if query_lower in line_lower:
            score += 0.5
        
        # Word match bonus
        query_words = query_lower.split()
        line_words = line_lower.split()
        matching_words = sum(1 for w in query_words if w in line_words)
        score += (matching_words / len(query_words)) * 0.3
        
        # File name relevance
        if query_lower in file_name.lower():
            score += 0.2
        
        return min(score, 1.0)
    
    def search(
        self,
        query: str,
        case_sensitive: bool = False,
        regex: bool = False,
        context_lines: int = 2,
        max_results: int = 50
    ) -> List[SearchResult]:
        """
        Search documentation.
        
        Args:
            query: Search query
            case_sensitive: Case-sensitive search
            regex: Treat query as regex
            context_lines: Number of context lines to include
            max_results: Maximum number of results
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        # Compile regex if needed
        if regex:
            try:
                pattern = re.compile(query, 0 if case_sensitive else re.IGNORECASE)
            except re.error:
                return []
        
        for doc_file in self.doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    # Check for match
                    matched = False
                    if regex:
                        matched = pattern.search(line) is not None
                    else:
                        if case_sensitive:
                            matched = query in line
                        else:
                            matched = query.lower() in line.lower()
                    
                    if matched:
                        # Get context
                        context_before = []
                        context_after = []
                        
                        for j in range(max(0, i - context_lines), i):
                            context_before.append(lines[j].rstrip('\n'))
                        
                        for j in range(i + 1, min(len(lines), i + context_lines + 1)):
                            context_after.append(lines[j].rstrip('\n'))
                        
                        # Calculate relevance
                        relevance = self._calculate_relevance(
                            query,
                            line,
                            doc_file.name
                        )
                        
                        result = SearchResult(
                            file=str(doc_file.relative_to(self.repo_path)),
                            line_number=i + 1,
                            line_content=line.rstrip('\n'),
                            context_before=context_before,
                            context_after=context_after,
                            relevance_score=relevance
                        )
                        
                        results.append(result)
                        
                        if len(results) >= max_results:
                            break
                
                if len(results) >= max_results:
                    break
                    
            except Exception as e:
                continue
        
        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return results[:max_results]
    
    def search_section(
        self,
        section: str,
        query: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search within a specific documentation section.
        
        Args:
            section: Section name (e.g., "Installation", "Usage")
            query: Optional query within section
            
        Returns:
            List of SearchResult objects
        """
        # First find the section
        section_pattern = rf"^#+\s+{re.escape(section)}"
        section_results = self.search(section_pattern, regex=True, context_lines=50)
        
        if not section_results:
            return []
        
        # If no query, return section content
        if not query:
            return section_results
        
        # Search within section context
        filtered_results = []
        for result in section_results:
            # Check if query appears in the section content
            all_content = (
                result.context_before +
                [result.line_content] +
                result.context_after
            )
            content_text = '\n'.join(all_content)
            
            if query.lower() in content_text.lower():
                filtered_results.append(result)
        
        return filtered_results
    
    def get_topic_help(self, topic: str) -> Optional[str]:
        """
        Get help for a specific topic.
        
        Args:
            topic: Topic name
            
        Returns:
            Help text or None
        """
        results = self.search_section(topic)
        
        if not results:
            return None
        
        # Format the first result
        result = results[0]
        help_lines = []
        help_lines.append(f"Help: {topic}")
        help_lines.append("=" * 60)
        help_lines.extend(result.context_after[:20])  # Get up to 20 lines
        
        return "\n".join(help_lines)
    
    def list_topics(self) -> List[str]:
        """
        List all documentation topics (sections).
        
        Returns:
            List of topic names
        """
        topics = []
        header_pattern = re.compile(r'^#+\s+(.+)$')
        
        for doc_file in self.doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        match = header_pattern.match(line)
                        if match:
                            topic = match.group(1).strip()
                            if topic not in topics:
                                topics.append(topic)
            except Exception:
                continue
        
        return sorted(topics)
    
    def format_results(self, results: List[SearchResult]) -> str:
        """
        Format search results for display.
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results found."
        
        lines = []
        lines.append(f"Found {len(results)} result(s)")
        lines.append("=" * 60)
        lines.append("")
        
        for i, result in enumerate(results, 1):
            lines.append(f"Result {i} (relevance: {result.relevance_score:.2f})")
            lines.append(result.format())
            lines.append("")
        
        return "\n".join(lines)


def search_documentation(query: str, **kwargs) -> List[SearchResult]:
    """
    Convenience function to search AccuDoc documentation.
    
    Args:
        query: Search query
        **kwargs: Additional search options
        
    Returns:
        List of SearchResult objects
    """
    searcher = DocumentationSearch()
    return searcher.search(query, **kwargs)
