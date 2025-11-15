"""
Documentation testing and validation module for AccuDoc.

Verifies generated documentation for quality, accuracy, and completeness.
Supports custom validation rules for project-specific requirements.
"""

import re
import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set, Callable, Any
from dataclasses import dataclass, field
from urllib.parse import urlparse
from abc import ABC, abstractmethod


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: str  # error, warning, info
    category: str  # link, syntax, structure, content, custom
    message: str
    line_number: Optional[int] = None
    context: Optional[str] = None
    rule_id: Optional[str] = None  # ID of custom rule that generated this issue


class ValidationRule(ABC):
    """Base class for custom validation rules."""
    
    def __init__(self, rule_id: str, severity: str = 'warning', 
                 enabled: bool = True, config: Optional[Dict[str, Any]] = None):
        """
        Initialize validation rule.
        
        Args:
            rule_id: Unique identifier for this rule
            severity: Issue severity (error, warning, info)
            enabled: Whether rule is enabled
            config: Rule-specific configuration
        """
        self.rule_id = rule_id
        self.severity = severity
        self.enabled = enabled
        self.config = config or {}
    
    @abstractmethod
    def validate(self, content: str) -> List[ValidationIssue]:
        """
        Validate content against this rule.
        
        Args:
            content: Documentation content to validate
            
        Returns:
            List of validation issues found
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get rule description."""
        pass


# Built-in custom validation rules

class MaxLineLengthRule(ValidationRule):
    """Rule to enforce maximum line length."""
    
    def __init__(self, severity: str = 'warning', enabled: bool = True, 
                 config: Optional[Dict[str, Any]] = None):
        super().__init__('max-line-length', severity, enabled, config)
        self.max_length = self.config.get('max_length', 120)
    
    @property
    def description(self) -> str:
        return f"Lines should not exceed {self.max_length} characters"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks and tables
            if line.strip().startswith('```') or line.strip().startswith('|'):
                continue
            
            if len(line) > self.max_length:
                issues.append(ValidationIssue(
                    severity=self.severity,
                    category='custom',
                    message=f'Line exceeds maximum length ({len(line)} > {self.max_length})',
                    line_number=line_num,
                    context=line[:80] + '...' if len(line) > 80 else line,
                    rule_id=self.rule_id
                ))
        
        return issues


class RequiredSectionsRule(ValidationRule):
    """Rule to enforce required documentation sections."""
    
    def __init__(self, severity: str = 'error', enabled: bool = True, 
                 config: Optional[Dict[str, Any]] = None):
        super().__init__('required-sections', severity, enabled, config)
        self.required_sections = self.config.get('sections', [
            'Overview', 'Installation', 'Usage'
        ])
    
    @property
    def description(self) -> str:
        return f"Documentation must contain sections: {', '.join(self.required_sections)}"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        # Extract all section headers
        found_sections = set()
        header_pattern = r'^#+\s+(.+)$'
        
        for line in lines:
            match = re.match(header_pattern, line)
            if match:
                section_name = match.group(1).strip()
                found_sections.add(section_name.lower())
        
        # Check for missing required sections
        for required in self.required_sections:
            if required.lower() not in found_sections:
                issues.append(ValidationIssue(
                    severity=self.severity,
                    category='custom',
                    message=f'Missing required section: "{required}"',
                    line_number=None,
                    context=f'Required sections: {", ".join(self.required_sections)}',
                    rule_id=self.rule_id
                ))
        
        return issues


class ForbiddenWordsRule(ValidationRule):
    """Rule to detect forbidden or discouraged words/phrases."""
    
    def __init__(self, severity: str = 'warning', enabled: bool = True, 
                 config: Optional[Dict[str, Any]] = None):
        super().__init__('forbidden-words', severity, enabled, config)
        self.forbidden_words = self.config.get('words', [
            'simply', 'just', 'easy', 'obviously', 'basically'
        ])
        self.case_sensitive = self.config.get('case_sensitive', False)
    
    @property
    def description(self) -> str:
        return f"Avoid using discouraged words: {', '.join(self.forbidden_words)}"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith('```') or line.strip().startswith('    '):
                continue
            
            for word in self.forbidden_words:
                pattern = r'\b' + re.escape(word) + r'\b'
                flags = 0 if self.case_sensitive else re.IGNORECASE
                
                if re.search(pattern, line, flags):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Discouraged word found: "{word}"',
                        line_number=line_num,
                        context=line.strip(),
                        rule_id=self.rule_id
                    ))
        
        return issues


class NoConsecutiveBlankLinesRule(ValidationRule):
    """Rule to prevent multiple consecutive blank lines."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True, 
                 config: Optional[Dict[str, Any]] = None):
        super().__init__('no-consecutive-blanks', severity, enabled, config)
        self.max_consecutive = self.config.get('max_consecutive', 1)
    
    @property
    def description(self) -> str:
        return f"No more than {self.max_consecutive} consecutive blank line(s) allowed"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        consecutive_blanks = 0
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                consecutive_blanks += 1
                if consecutive_blanks > self.max_consecutive:
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message=f'Too many consecutive blank lines ({consecutive_blanks})',
                        line_number=line_num,
                        context=None,
                        rule_id=self.rule_id
                    ))
            else:
                consecutive_blanks = 0
        
        return issues


class HeadingCapitalizationRule(ValidationRule):
    """Rule to enforce heading capitalization style."""
    
    def __init__(self, severity: str = 'info', enabled: bool = True, 
                 config: Optional[Dict[str, Any]] = None):
        super().__init__('heading-capitalization', severity, enabled, config)
        self.style = self.config.get('style', 'title')  # title, sentence, upper, lower
    
    @property
    def description(self) -> str:
        return f"Headings should use {self.style} case"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        header_pattern = r'^(#+)\s+(.+)$'
        
        for line_num, line in enumerate(lines, 1):
            match = re.match(header_pattern, line)
            if match:
                heading_text = match.group(2).strip()
                
                if self.style == 'title' and not self._is_title_case(heading_text):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message='Heading should use Title Case',
                        line_number=line_num,
                        context=line.strip(),
                        rule_id=self.rule_id
                    ))
                elif self.style == 'sentence' and not self._is_sentence_case(heading_text):
                    issues.append(ValidationIssue(
                        severity=self.severity,
                        category='custom',
                        message='Heading should use Sentence case',
                        line_number=line_num,
                        context=line.strip(),
                        rule_id=self.rule_id
                    ))
        
        return issues
    
    def _is_title_case(self, text: str) -> bool:
        """Check if text is in Title Case (basic check)."""
        # Very basic title case check - first letter of each major word capitalized
        words = text.split()
        if not words:
            return True
        
        # Small words that can be lowercase in title case
        small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 
                      'in', 'of', 'on', 'or', 'the', 'to', 'with', 'is'}
        
        for i, word in enumerate(words):
            # Skip words with special characters or code
            if any(c in word for c in ['`', '(', ')', '[', ']']):
                continue
            
            # First and last words should be capitalized
            if i == 0 or i == len(words) - 1:
                if word and word[0].islower():
                    return False
            else:
                # Other words: either small word (lowercase) or capitalized
                clean_word = word.strip('.,;:!?')
                if clean_word.lower() not in small_words and clean_word and clean_word[0].islower():
                    return False
        
        return True
    
    def _is_sentence_case(self, text: str) -> bool:
        """Check if text is in Sentence case."""
        if not text:
            return True
        return text[0].isupper()


class CodeBlockLanguageRule(ValidationRule):
    """Rule to require language specification for code blocks."""
    
    def __init__(self, severity: str = 'warning', enabled: bool = True, 
                 config: Optional[Dict[str, Any]] = None):
        super().__init__('code-block-language', severity, enabled, config)
    
    @property
    def description(self) -> str:
        return "Code blocks should specify a language"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        in_code_block = False
        for line_num, line in enumerate(lines, 1):
            # Check for code block delimiter
            if line.strip().startswith('```'):
                if not in_code_block:
                    # This is an opening delimiter
                    if line.strip() == '```':
                        # No language specified
                        issues.append(ValidationIssue(
                            severity=self.severity,
                            category='custom',
                            message='Code block missing language specification',
                            line_number=line_num,
                            context=line.strip(),
                            rule_id=self.rule_id
                        ))
                    in_code_block = True
                else:
                    # This is a closing delimiter
                    in_code_block = False
        
        return issues


class DocumentationValidator:
    """Validates generated documentation."""
    
    def __init__(self, custom_rules: Optional[List[ValidationRule]] = None):
        """
        Initialize validator.
        
        Args:
            custom_rules: List of custom validation rules to apply
        """
        self.issues: List[ValidationIssue] = []
        self.custom_rules = custom_rules or []
    
    def add_rule(self, rule: ValidationRule):
        """
        Add a custom validation rule.
        
        Args:
            rule: Validation rule to add
        """
        self.custom_rules.append(rule)
    
    def load_rules_from_config(self, config_path: Path):
        """
        Load validation rules from a configuration file.
        
        Args:
            config_path: Path to configuration file (JSON or YAML)
        """
        if not config_path.exists():
            return
        
        # Load config based on file extension
        if config_path.suffix in ['.yml', '.yaml']:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        elif config_path.suffix == '.json':
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            return
        
        # Parse rules from config
        rules_config = config.get('validation_rules', [])
        for rule_def in rules_config:
            rule_type = rule_def.get('type')
            severity = rule_def.get('severity', 'warning')
            enabled = rule_def.get('enabled', True)
            rule_config = rule_def.get('config', {})
            
            if not enabled:
                continue
            
            # Create rule instance based on type
            rule = self._create_rule(rule_type, severity, enabled, rule_config)
            if rule:
                self.add_rule(rule)
    
    def _create_rule(self, rule_type: str, severity: str, enabled: bool, 
                     config: Dict[str, Any]) -> Optional[ValidationRule]:
        """Create a rule instance from configuration."""
        rule_classes = {
            'max-line-length': MaxLineLengthRule,
            'required-sections': RequiredSectionsRule,
            'forbidden-words': ForbiddenWordsRule,
            'no-consecutive-blanks': NoConsecutiveBlankLinesRule,
            'heading-capitalization': HeadingCapitalizationRule,
            'code-block-language': CodeBlockLanguageRule
        }
        
        rule_class = rule_classes.get(rule_type)
        if rule_class:
            return rule_class(severity, enabled, config)
        
        return None
    
    def validate(self, documentation: str, 
                check_links: bool = True,
                check_syntax: bool = True,
                check_structure: bool = True,
                check_content: bool = True,
                apply_custom_rules: bool = True) -> List[ValidationIssue]:
        """
        Validate documentation.
        
        Args:
            documentation: Documentation content to validate
            check_links: Check for broken links
            check_syntax: Check markdown syntax
            check_structure: Check document structure
            check_content: Check content quality
            apply_custom_rules: Apply custom validation rules
            
        Returns:
            List of validation issues
        """
        self.issues = []
        
        if check_links:
            self._check_links(documentation)
        
        if check_syntax:
            self._check_markdown_syntax(documentation)
        
        if check_structure:
            self._check_document_structure(documentation)
        
        if check_content:
            self._check_content_quality(documentation)
        
        # Apply custom rules
        if apply_custom_rules:
            for rule in self.custom_rules:
                if rule.enabled:
                    try:
                        rule_issues = rule.validate(documentation)
                        self.issues.extend(rule_issues)
                    except Exception as e:
                        # Log error but continue with other rules
                        self.issues.append(ValidationIssue(
                            severity='error',
                            category='custom',
                            message=f'Error applying rule {rule.rule_id}: {str(e)}',
                            line_number=None,
                            context=None,
                            rule_id=rule.rule_id
                        ))
        
        return self.issues
    
    def _check_links(self, content: str):
        """Check for broken or invalid links."""
        lines = content.split('\n')
        
        # Pattern for markdown links: [text](url) - allow empty URLs
        link_pattern = r'\[([^\]]+)\]\(([^\)]*)\)'
        
        for line_num, line in enumerate(lines, 1):
            for match in re.finditer(link_pattern, line):
                link_text = match.group(1)
                link_url = match.group(2)
                
                # Check for empty links
                if not link_url or link_url.strip() == '':
                    self.issues.append(ValidationIssue(
                        severity='error',
                        category='link',
                        message=f'Empty link URL for text "{link_text}"',
                        line_number=line_num,
                        context=line.strip()
                    ))
                    continue
                
                # Check for placeholder links
                if link_url in ['#', 'TODO', 'FIXME', 'http://example.com']:
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        category='link',
                        message=f'Placeholder link detected: "{link_url}"',
                        line_number=line_num,
                        context=line.strip()
                    ))
                
                # Check for relative links (might be broken)
                if link_url.startswith('#'):
                    # Internal anchor link - validate it exists
                    anchor = link_url[1:]
                    if anchor and not self._anchor_exists(content, anchor):
                        self.issues.append(ValidationIssue(
                            severity='warning',
                            category='link',
                            message=f'Anchor "{anchor}" not found in document',
                            line_number=line_num,
                            context=line.strip()
                        ))
                
                # Check for malformed URLs
                if link_url.startswith('http') or link_url.startswith('https'):
                    parsed = urlparse(link_url)
                    if not parsed.netloc:
                        self.issues.append(ValidationIssue(
                            severity='error',
                            category='link',
                            message=f'Malformed URL: "{link_url}"',
                            line_number=line_num,
                            context=line.strip()
                        ))
    
    def _anchor_exists(self, content: str, anchor: str) -> bool:
        """Check if an anchor exists in the document."""
        # Markdown headers become anchors
        # Convert header text to anchor format (lowercase, spaces to hyphens)
        header_pattern = r'^#+\s+(.+)$'
        
        for line in content.split('\n'):
            match = re.match(header_pattern, line)
            if match:
                header_text = match.group(1)
                # Simple anchor generation (may not match all parsers exactly)
                generated_anchor = re.sub(r'[^\w\s-]', '', header_text.lower())
                generated_anchor = re.sub(r'[\s_]+', '-', generated_anchor)
                
                if generated_anchor == anchor or header_text.lower() == anchor.lower():
                    return True
        
        return False
    
    def _check_markdown_syntax(self, content: str):
        """Check for markdown syntax issues."""
        lines = content.split('\n')
        
        code_block_count = 0
        in_code_block = False
        
        for line_num, line in enumerate(lines, 1):
            # Check for unmatched code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                code_block_count += 1
            
            # Check for unescaped special characters in non-code sections
            if not in_code_block:
                # Check for unmatched brackets
                if line.count('[') != line.count(']'):
                    # Could be legitimate, but flag for review
                    if '[' in line and ']' not in line:
                        self.issues.append(ValidationIssue(
                            severity='info',
                            category='syntax',
                            message='Unmatched opening bracket',
                            line_number=line_num,
                            context=line.strip()
                        ))
                
                # Check for bare URLs (should be in angle brackets or links)
                bare_url_pattern = r'(?<![(\[<])(https?://[^\s\)<>]+)(?![)\]>])'
                for match in re.finditer(bare_url_pattern, line):
                    url = match.group(1)
                    self.issues.append(ValidationIssue(
                        severity='info',
                        category='syntax',
                        message=f'Bare URL detected (consider using markdown link): {url}',
                        line_number=line_num,
                        context=line.strip()
                    ))
        
        # Check for unmatched code blocks
        if in_code_block:
            self.issues.append(ValidationIssue(
                severity='error',
                category='syntax',
                message='Unmatched code block delimiter (```)',
                line_number=None,
                context='Document has odd number of code block delimiters'
            ))
    
    def _check_document_structure(self, content: str):
        """Check document structure."""
        lines = content.split('\n')
        
        has_title = False
        header_levels = []
        
        for line_num, line in enumerate(lines, 1):
            # Check for headers - allow empty headers to detect them
            header_match = re.match(r'^(#+)\s*(.*)$', line)
            if header_match:
                level = len(header_match.group(1))
                header_text = header_match.group(2)
                
                if level == 1:
                    has_title = True
                
                header_levels.append(level)
                
                # Check for empty headers
                if not header_text.strip():
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        category='structure',
                        message='Empty header detected',
                        line_number=line_num,
                        context=line.strip()
                    ))
                
                # Check for header level skipping
                if len(header_levels) > 1:
                    prev_level = header_levels[-2]
                    if level > prev_level + 1:
                        self.issues.append(ValidationIssue(
                            severity='warning',
                            category='structure',
                            message=f'Header level skip (from h{prev_level} to h{level})',
                            line_number=line_num,
                            context=line.strip()
                        ))
        
        # Check if document has a title
        if not has_title:
            self.issues.append(ValidationIssue(
                severity='warning',
                category='structure',
                message='Document has no top-level heading (h1)',
                line_number=None,
                context='Consider adding a main title'
            ))
        
        # Check if document is too short
        non_empty_lines = [l for l in lines if l.strip()]
        if len(non_empty_lines) < 10:
            self.issues.append(ValidationIssue(
                severity='info',
                category='structure',
                message=f'Document seems short ({len(non_empty_lines)} non-empty lines)',
                line_number=None,
                context='Consider adding more content'
            ))
    
    def _check_content_quality(self, content: str):
        """Check content quality."""
        lines = content.split('\n')
        
        # Check for common issues
        for line_num, line in enumerate(lines, 1):
            # Check for TODO/FIXME markers
            if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='content',
                    message='TODO/FIXME marker found',
                    line_number=line_num,
                    context=line.strip()
                ))
            
            # Check for very long lines (might be tables or code)
            if len(line) > 200 and not line.strip().startswith('|'):
                self.issues.append(ValidationIssue(
                    severity='info',
                    category='content',
                    message=f'Very long line ({len(line)} characters)',
                    line_number=line_num,
                    context=line[:100] + '...'
                ))
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                self.issues.append(ValidationIssue(
                    severity='info',
                    category='content',
                    message='Trailing whitespace detected',
                    line_number=line_num,
                    context=line.strip()
                ))
        
        # Check for common typos (very basic)
        common_typos = {
            'teh': 'the',
            'recieve': 'receive',
            'seperate': 'separate',
            'occured': 'occurred'
        }
        
        for line_num, line in enumerate(lines, 1):
            for typo, correction in common_typos.items():
                if re.search(r'\b' + typo + r'\b', line, re.IGNORECASE):
                    self.issues.append(ValidationIssue(
                        severity='info',
                        category='content',
                        message=f'Possible typo: "{typo}" (did you mean "{correction}"?)',
                        line_number=line_num,
                        context=line.strip()
                    ))
    
    def get_summary(self) -> Dict[str, int]:
        """
        Get summary of validation issues.
        
        Returns:
            Dictionary with counts by severity and category
        """
        summary = {
            'total': len(self.issues),
            'by_severity': {'error': 0, 'warning': 0, 'info': 0},
            'by_category': {'link': 0, 'syntax': 0, 'structure': 0, 'content': 0, 'custom': 0}
        }
        
        for issue in self.issues:
            summary['by_severity'][issue.severity] += 1
            summary['by_category'][issue.category] += 1
        
        return summary
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """
        List all custom validation rules.
        
        Returns:
            List of rule information dictionaries
        """
        return [
            {
                'id': rule.rule_id,
                'description': rule.description,
                'severity': rule.severity,
                'enabled': rule.enabled
            }
            for rule in self.custom_rules
        ]
    
    def format_report(self, issues: Optional[List[ValidationIssue]] = None) -> str:
        """
        Format validation report.
        
        Args:
            issues: List of issues (uses self.issues if None)
            
        Returns:
            Formatted report string
        """
        if issues is None:
            issues = self.issues
        
        if not issues:
            return "✓ No validation issues found"
        
        # Group by severity
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']
        info = [i for i in issues if i.severity == 'info']
        
        report = [
            "Documentation Validation Report",
            "=" * 70,
            f"\nTotal Issues: {len(issues)}",
            f"Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(info)}",
            ""
        ]
        
        if errors:
            report.append("\n❌ ERRORS:")
            report.append("-" * 70)
            for i, issue in enumerate(errors, 1):
                rule_info = f" [{issue.rule_id}]" if issue.rule_id else ""
                report.append(f"\n{i}. [{issue.category.upper()}]{rule_info} {issue.message}")
                if issue.line_number:
                    report.append(f"   Line {issue.line_number}: {issue.context}")
                elif issue.context:
                    report.append(f"   {issue.context}")
        
        if warnings:
            report.append("\n\n⚠️  WARNINGS:")
            report.append("-" * 70)
            for i, issue in enumerate(warnings, 1):
                rule_info = f" [{issue.rule_id}]" if issue.rule_id else ""
                report.append(f"\n{i}. [{issue.category.upper()}]{rule_info} {issue.message}")
                if issue.line_number:
                    report.append(f"   Line {issue.line_number}: {issue.context}")
                elif issue.context:
                    report.append(f"   {issue.context}")
        
        if info:
            report.append("\n\nℹ️  INFO:")
            report.append("-" * 70)
            for i, issue in enumerate(info[:10], 1):  # Limit info messages
                rule_info = f" [{issue.rule_id}]" if issue.rule_id else ""
                report.append(f"\n{i}. [{issue.category.upper()}]{rule_info} {issue.message}")
                if issue.line_number:
                    report.append(f"   Line {issue.line_number}: {issue.context}")
            
            if len(info) > 10:
                report.append(f"\n... and {len(info) - 10} more info messages")
        
        return "\n".join(report)


def validate_documentation(documentation: str,
                          check_links: bool = True,
                          check_syntax: bool = True,
                          check_structure: bool = True,
                          check_content: bool = True) -> Tuple[List[ValidationIssue], str]:
    """
    Convenience function to validate documentation.
    
    Args:
        documentation: Documentation content
        check_links: Check links
        check_syntax: Check syntax
        check_structure: Check structure
        check_content: Check content
        
    Returns:
        Tuple of (issues, report)
    """
    validator = DocumentationValidator()
    issues = validator.validate(documentation, check_links, check_syntax,
                               check_structure, check_content)
    report = validator.format_report(issues)
    return issues, report
