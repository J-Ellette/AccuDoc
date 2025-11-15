"""
Grammar checking module for AccuDoc.

Provides basic grammar validation for documentation files using
rule-based checking for common grammar issues.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict


class GrammarChecker:
    """Simple rule-based grammar checker for documentation."""
    
    # Common grammar rules
    GRAMMAR_RULES = [
        {
            'name': 'double_negatives',
            'pattern': r'\b(don\'t|doesn\'t|didn\'t|won\'t|can\'t|couldn\'t|wouldn\'t|shouldn\'t)\s+(no|never|nothing|nobody|nowhere)\b',
            'message': 'Possible double negative',
            'severity': 'warning'
        },
        {
            'name': 'passive_voice',
            'pattern': r'\b(is|are|was|were|been|being)\s+\w+ed\b',
            'message': 'Possible passive voice (consider active voice)',
            'severity': 'suggestion'
        },
        {
            'name': 'repeated_words',
            'pattern': r'\b(\w+)\s+\1\b',
            'message': 'Repeated word',
            'severity': 'error'
        },
        {
            'name': 'its_vs_its',
            'pattern': r'\bit\'s\s+\w+',
            'message': 'Check if "it\'s" (it is) or "its" (possessive) is correct',
            'severity': 'suggestion'
        },
        {
            'name': 'their_vs_there',
            'pattern': r'\b(their|there|they\'re)\b',
            'message': 'Verify correct usage: their (possessive), there (location), they\'re (they are)',
            'severity': 'suggestion'
        },
        {
            'name': 'your_vs_youre',
            'pattern': r'\b(your|you\'re)\b',
            'message': 'Verify correct usage: your (possessive), you\'re (you are)',
            'severity': 'suggestion'
        },
        {
            'name': 'then_vs_than',
            'pattern': r'\b(then|than)\b',
            'message': 'Verify correct usage: then (time), than (comparison)',
            'severity': 'suggestion'
        },
        {
            'name': 'affect_vs_effect',
            'pattern': r'\b(affect|effect)\b',
            'message': 'Verify correct usage: affect (verb), effect (noun)',
            'severity': 'suggestion'
        },
        {
            'name': 'sentence_spacing',
            'pattern': r'\.\s{2,}[A-Z]',
            'message': 'Multiple spaces after period',
            'severity': 'style'
        },
        {
            'name': 'missing_article',
            'pattern': r'\b(is|are|was|were)\s+\w+\s+(noun|verb|adjective)\b',
            'message': 'Possible missing article (a, an, the)',
            'severity': 'suggestion'
        },
        {
            'name': 'comma_splice',
            'pattern': r',\s*[a-z]+\s+(is|are|was|were|have|has|had)\b',
            'message': 'Possible comma splice (consider semicolon or period)',
            'severity': 'warning'
        },
        {
            'name': 'sentence_fragment',
            'pattern': r'^\s*[A-Z][a-z]+\s+(and|but|or|because)\s+\w+\.',
            'message': 'Possible sentence fragment',
            'severity': 'warning'
        }
    ]
    
    def __init__(self):
        """Initialize grammar checker."""
        self.logger = logging.getLogger('accudoc.grammar')
        
    def check_text(self, text: str) -> Dict[str, Any]:
        """
        Check text for grammar issues.
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with grammar issues found
        """
        issues = []
        
        # Split into sentences for context
        sentences = self._split_sentences(text)
        
        for line_num, sentence in enumerate(sentences, 1):
            # Skip code blocks
            if '```' in sentence or sentence.strip().startswith('    '):
                continue
            
            # Apply each grammar rule
            for rule in self.GRAMMAR_RULES:
                matches = list(re.finditer(rule['pattern'], sentence, re.IGNORECASE))
                for match in matches:
                    # Filter out some false positives
                    if self._is_false_positive(rule['name'], match.group(), sentence):
                        continue
                    
                    issues.append({
                        'rule': rule['name'],
                        'line': line_num,
                        'text': match.group(),
                        'message': rule['message'],
                        'severity': rule['severity'],
                        'context': sentence.strip()[:100]
                    })
        
        return {
            'issues': issues,
            'total_issues': len(issues),
            'by_severity': self._count_by_severity(issues),
            'by_rule': self._count_by_rule(issues)
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Remove code blocks first
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _is_false_positive(self, rule_name: str, matched_text: str, context: str) -> bool:
        """Check if a match is a false positive."""
        # Skip technical terms and code-like patterns
        if rule_name == 'passive_voice':
            # Allow passive voice in technical documentation sometimes
            technical_verbs = ['configured', 'initialized', 'defined', 'specified', 'documented']
            if any(verb in matched_text.lower() for verb in technical_verbs):
                return True
        
        if rule_name in ['their_vs_there', 'your_vs_youre', 'then_vs_than', 'affect_vs_effect']:
            # These are just suggestions, not necessarily errors
            # Only flag if there's obvious context clues
            return False
        
        if rule_name == 'repeated_words':
            # Allow repeated words like "that that" in some contexts
            if matched_text.lower() in ['that that', 'had had']:
                return True
        
        return False
    
    def _count_by_severity(self, issues: List[Dict]) -> Dict[str, int]:
        """Count issues by severity."""
        counts = defaultdict(int)
        for issue in issues:
            counts[issue['severity']] += 1
        return dict(counts)
    
    def _count_by_rule(self, issues: List[Dict]) -> Dict[str, int]:
        """Count issues by rule."""
        counts = defaultdict(int)
        for issue in issues:
            counts[issue['rule']] += 1
        return dict(counts)
    
    def check_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Check a file for grammar issues.
        
        Args:
            filepath: Path to file
            
        Returns:
            Dictionary with check results
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            result = self.check_text(content)
            result['file'] = str(filepath)
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking file {filepath}: {e}")
            return {'file': str(filepath), 'error': str(e)}
    
    def check_directory(self, dirpath: Path, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Check all documentation files in a directory.
        
        Args:
            dirpath: Directory to check
            extensions: File extensions to check
            
        Returns:
            List of check results
        """
        if extensions is None:
            extensions = ['.md', '.txt', '.rst', '.markdown']
        
        results = []
        for ext in extensions:
            for filepath in dirpath.rglob(f'*{ext}'):
                result = self.check_file(filepath)
                if result.get('issues'):
                    results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate grammar check report.
        
        Args:
            results: Results from check_directory() or list of check_file() results
            
        Returns:
            Markdown formatted report
        """
        if not results:
            return "# Grammar Check Report\n\n✅ No grammar issues found!"
        
        md = []
        md.append("# Grammar Check Report\n")
        
        total_issues = sum(r.get('total_issues', 0) for r in results)
        total_files = len(results)
        
        md.append(f"**Files checked**: {total_files}")
        md.append(f"**Total issues**: {total_issues}\n")
        
        if total_issues == 0:
            md.append("✅ No grammar issues found!")
            return '\n'.join(md)
        
        # Aggregate severity counts
        all_severity = defaultdict(int)
        for result in results:
            for severity, count in result.get('by_severity', {}).items():
                all_severity[severity] += count
        
        md.append("## Issue Summary\n")
        severity_icons = {
            'error': '🔴',
            'warning': '🟡',
            'suggestion': '💡',
            'style': '📝'
        }
        for severity in ['error', 'warning', 'suggestion', 'style']:
            if severity in all_severity:
                icon = severity_icons.get(severity, '•')
                md.append(f"- {icon} **{severity.title()}**: {all_severity[severity]}")
        md.append("")
        
        # Group by file
        for result in results:
            if not result.get('issues'):
                continue
            
            filepath = result.get('file', 'Unknown')
            issues = result['issues']
            
            md.append(f"## {filepath}\n")
            md.append(f"**Issues**: {len(issues)}\n")
            
            # Group by severity
            by_severity = defaultdict(list)
            for issue in issues:
                by_severity[issue['severity']].append(issue)
            
            for severity in ['error', 'warning', 'suggestion', 'style']:
                if severity not in by_severity:
                    continue
                
                icon = severity_icons.get(severity, '•')
                md.append(f"### {icon} {severity.title()}\n")
                
                for issue in by_severity[severity][:10]:  # Limit to first 10 per category
                    md.append(f"**Line {issue['line']}**: {issue['message']}")
                    md.append(f"- Text: `{issue['text']}`")
                    if issue.get('context'):
                        md.append(f"- Context: {issue['context'][:80]}...")
                    md.append("")
                
                if len(by_severity[severity]) > 10:
                    md.append(f"*... and {len(by_severity[severity]) - 10} more {severity} issues*\n")
        
        # Recommendations
        md.append("## Recommendations\n")
        
        if all_severity.get('error', 0) > 0:
            md.append(f"- Fix {all_severity['error']} grammar errors")
        
        if all_severity.get('warning', 0) > 0:
            md.append(f"- Review {all_severity['warning']} warnings")
        
        if all_severity.get('suggestion', 0) > 0:
            md.append(f"- Consider {all_severity['suggestion']} suggestions for improvement")
        
        md.append("\n**Note**: This is a basic grammar checker. Some suggestions may be false positives.")
        md.append("Always use your judgment when applying grammar corrections.\n")
        
        return '\n'.join(md)
