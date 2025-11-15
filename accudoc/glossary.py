"""
Organization-wide Glossary & Style Standardization for AccuDoc.

Maintains and enforces terminology and language conventions across documentation projects.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import re

from accudoc.membership import MembershipManager, Permission


@dataclass
class GlossaryTerm:
    """Represents a glossary term."""
    term_id: str
    term: str
    definition: str
    preferred_usage: str
    aliases: List[str]
    deprecated_terms: List[str]
    category: Optional[str] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    organization_id: Optional[str] = None


@dataclass
class StyleRule:
    """Represents a style rule."""
    rule_id: str
    name: str
    description: str
    pattern: str
    replacement: Optional[str] = None
    severity: str = 'info'  # info, warning, error
    enabled: bool = True
    category: Optional[str] = None
    organization_id: Optional[str] = None


@dataclass
class GlossaryViolation:
    """Represents a glossary/style violation."""
    term: str
    preferred: str
    line_number: int
    context: str
    severity: str
    category: str


class GlossaryManager:
    """Manages organization-wide glossary and style standards."""
    
    def __init__(self, db_path: Optional[Path] = None, membership_manager: Optional[MembershipManager] = None):
        """
        Initialize glossary manager.
        
        Args:
            db_path: Path to database file
            membership_manager: Optional membership manager for access control
        """
        if db_path is None:
            db_path = Path.home() / '.accudoc' / 'glossary.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.membership_manager = membership_manager
        
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Glossary terms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS glossary_terms (
                term_id TEXT PRIMARY KEY,
                organization_id TEXT,
                term TEXT NOT NULL,
                definition TEXT NOT NULL,
                preferred_usage TEXT NOT NULL,
                aliases TEXT,
                deprecated_terms TEXT,
                category TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT,
                updated_at TEXT
            )
        ''')
        
        # Style rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS style_rules (
                rule_id TEXT PRIMARY KEY,
                organization_id TEXT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                pattern TEXT NOT NULL,
                replacement TEXT,
                severity TEXT DEFAULT 'info',
                enabled BOOLEAN DEFAULT 1,
                category TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Scan results table for tracking violations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS glossary_scans (
                scan_id TEXT PRIMARY KEY,
                repository_path TEXT NOT NULL,
                organization_id TEXT,
                scanned_at TEXT NOT NULL,
                total_violations INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                info_count INTEGER DEFAULT 0,
                scan_data TEXT
            )
        ''')
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_term_org ON glossary_terms(organization_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rule_org ON style_rules(organization_id)')
        
        self.conn.commit()
    
    def add_term(self, term: str, definition: str, preferred_usage: str,
                 aliases: Optional[List[str]] = None,
                 deprecated_terms: Optional[List[str]] = None,
                 category: Optional[str] = None,
                 organization_id: Optional[str] = None,
                 user_id: Optional[str] = None) -> GlossaryTerm:
        """
        Add a glossary term.
        
        Args:
            term: The term to define
            definition: Definition of the term
            preferred_usage: Example of preferred usage
            aliases: Alternative terms
            deprecated_terms: Terms to avoid
            category: Category for organization
            organization_id: Organization this term belongs to
            user_id: User creating the term
            
        Returns:
            Created GlossaryTerm
        """
        # Check permission if membership manager is available
        if self.membership_manager and user_id and organization_id:
            if not self.membership_manager.check_permission(user_id, organization_id, Permission.WRITE):
                raise PermissionError("User does not have permission to add terms")
        
        import secrets
        term_id = f"term_{secrets.token_urlsafe(12)}"
        created_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO glossary_terms 
            (term_id, organization_id, term, definition, preferred_usage, aliases, 
             deprecated_terms, category, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            term_id,
            organization_id,
            term,
            definition,
            preferred_usage,
            json.dumps(aliases or []),
            json.dumps(deprecated_terms or []),
            category,
            created_at,
            user_id
        ))
        self.conn.commit()
        
        return GlossaryTerm(
            term_id=term_id,
            term=term,
            definition=definition,
            preferred_usage=preferred_usage,
            aliases=aliases or [],
            deprecated_terms=deprecated_terms or [],
            category=category,
            created_at=created_at,
            created_by=user_id,
            organization_id=organization_id
        )
    
    def add_style_rule(self, name: str, description: str, pattern: str,
                       replacement: Optional[str] = None,
                       severity: str = 'info',
                       category: Optional[str] = None,
                       organization_id: Optional[str] = None) -> StyleRule:
        """
        Add a style rule.
        
        Args:
            name: Rule name
            description: Rule description
            pattern: Regex pattern to match
            replacement: Suggested replacement
            severity: Severity level (info, warning, error)
            category: Category for organization
            organization_id: Organization this rule belongs to
            
        Returns:
            Created StyleRule
        """
        import secrets
        rule_id = f"rule_{secrets.token_urlsafe(12)}"
        created_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO style_rules 
            (rule_id, organization_id, name, description, pattern, replacement, 
             severity, category, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule_id,
            organization_id,
            name,
            description,
            pattern,
            replacement,
            severity,
            category,
            created_at
        ))
        self.conn.commit()
        
        return StyleRule(
            rule_id=rule_id,
            name=name,
            description=description,
            pattern=pattern,
            replacement=replacement,
            severity=severity,
            category=category,
            organization_id=organization_id
        )
    
    def get_terms(self, organization_id: Optional[str] = None) -> List[GlossaryTerm]:
        """
        Get all glossary terms for an organization.
        
        Args:
            organization_id: Filter by organization
            
        Returns:
            List of glossary terms
        """
        cursor = self.conn.cursor()
        
        if organization_id:
            cursor.execute(
                'SELECT * FROM glossary_terms WHERE organization_id = ? OR organization_id IS NULL',
                (organization_id,)
            )
        else:
            cursor.execute('SELECT * FROM glossary_terms WHERE organization_id IS NULL')
        
        terms = []
        for row in cursor.fetchall():
            terms.append(GlossaryTerm(
                term_id=row['term_id'],
                term=row['term'],
                definition=row['definition'],
                preferred_usage=row['preferred_usage'],
                aliases=json.loads(row['aliases']) if row['aliases'] else [],
                deprecated_terms=json.loads(row['deprecated_terms']) if row['deprecated_terms'] else [],
                category=row['category'],
                created_at=row['created_at'],
                created_by=row['created_by'],
                organization_id=row['organization_id']
            ))
        
        return terms
    
    def get_style_rules(self, organization_id: Optional[str] = None, 
                        enabled_only: bool = True) -> List[StyleRule]:
        """
        Get style rules for an organization.
        
        Args:
            organization_id: Filter by organization
            enabled_only: Only return enabled rules
            
        Returns:
            List of style rules
        """
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM style_rules WHERE '
        params = []
        
        if organization_id:
            query += '(organization_id = ? OR organization_id IS NULL)'
            params.append(organization_id)
        else:
            query += 'organization_id IS NULL'
        
        if enabled_only:
            query += ' AND enabled = 1'
        
        cursor.execute(query, params)
        
        rules = []
        for row in cursor.fetchall():
            rules.append(StyleRule(
                rule_id=row['rule_id'],
                name=row['name'],
                description=row['description'],
                pattern=row['pattern'],
                replacement=row['replacement'],
                severity=row['severity'],
                enabled=bool(row['enabled']),
                category=row['category'],
                organization_id=row['organization_id']
            ))
        
        return rules
    
    def scan_content(self, content: str, organization_id: Optional[str] = None) -> List[GlossaryViolation]:
        """
        Scan content for glossary and style violations.
        
        Args:
            content: Content to scan
            organization_id: Organization context
            
        Returns:
            List of violations
        """
        violations = []
        lines = content.split('\n')
        
        # Get terms and rules
        terms = self.get_terms(organization_id)
        rules = self.get_style_rules(organization_id)
        
        # Check for deprecated terms
        for term in terms:
            if term.deprecated_terms:
                for deprecated in term.deprecated_terms:
                    pattern = r'\b' + re.escape(deprecated) + r'\b'
                    for line_num, line in enumerate(lines, 1):
                        # Skip code blocks
                        if line.strip().startswith(('```', '    ', '#')):
                            continue
                        
                        if re.search(pattern, line, re.IGNORECASE):
                            violations.append(GlossaryViolation(
                                term=deprecated,
                                preferred=term.preferred_usage,
                                line_number=line_num,
                                context=line.strip()[:100],
                                severity='warning',
                                category='deprecated-term'
                            ))
        
        # Check style rules
        for rule in rules:
            if not rule.enabled:
                continue
            
            try:
                pattern = re.compile(rule.pattern, re.IGNORECASE)
                for line_num, line in enumerate(lines, 1):
                    # Skip code blocks
                    if line.strip().startswith(('```', '    ')):
                        continue
                    
                    if pattern.search(line):
                        violations.append(GlossaryViolation(
                            term=rule.name,
                            preferred=rule.replacement or 'See rule description',
                            line_number=line_num,
                            context=line.strip()[:100],
                            severity=rule.severity,
                            category='style-rule'
                        ))
            except re.error:
                # Skip invalid regex patterns
                continue
        
        return violations
    
    def generate_report(self, violations: List[GlossaryViolation], 
                       repository_path: Optional[str] = None) -> str:
        """
        Generate a report of violations.
        
        Args:
            violations: List of violations
            repository_path: Optional repository path for context
            
        Returns:
            Formatted report
        """
        lines = []
        lines.append("# Glossary & Style Compliance Report\n")
        
        if repository_path:
            lines.append(f"**Repository**: {repository_path}\n")
        
        lines.append(f"**Total Violations**: {len(violations)}\n")
        
        # Count by severity
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        info_count = sum(1 for v in violations if v.severity == 'info')
        
        lines.append("## Summary\n")
        lines.append(f"- Errors: {error_count}")
        lines.append(f"- Warnings: {warning_count}")
        lines.append(f"- Info: {info_count}\n")
        
        # Group by category
        by_category = {}
        for violation in violations:
            if violation.category not in by_category:
                by_category[violation.category] = []
            by_category[violation.category].append(violation)
        
        for category, items in sorted(by_category.items()):
            lines.append(f"## {category.replace('-', ' ').title()} ({len(items)})\n")
            lines.append("| Line | Found | Preferred | Context |")
            lines.append("|------|-------|-----------|---------|")
            
            for item in sorted(items, key=lambda x: x.line_number)[:50]:
                context = item.context.replace('|', '\\|')
                lines.append(f"| {item.line_number} | {item.term} | {item.preferred} | {context} |")
            
            if len(items) > 50:
                lines.append(f"\n*... and {len(items) - 50} more*\n")
            lines.append("")
        
        return '\n'.join(lines)
    
    def save_scan_results(self, repository_path: str, violations: List[GlossaryViolation],
                         organization_id: Optional[str] = None) -> str:
        """
        Save scan results to database.
        
        Args:
            repository_path: Repository path
            violations: List of violations
            organization_id: Organization context
            
        Returns:
            Scan ID
        """
        import secrets
        scan_id = f"scan_{secrets.token_urlsafe(12)}"
        scanned_at = datetime.now().isoformat()
        
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        info_count = sum(1 for v in violations if v.severity == 'info')
        
        # Serialize violation data
        scan_data = json.dumps([{
            'term': v.term,
            'preferred': v.preferred,
            'line_number': v.line_number,
            'context': v.context,
            'severity': v.severity,
            'category': v.category
        } for v in violations])
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO glossary_scans 
            (scan_id, repository_path, organization_id, scanned_at, 
             total_violations, error_count, warning_count, info_count, scan_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_id,
            repository_path,
            organization_id,
            scanned_at,
            len(violations),
            error_count,
            warning_count,
            info_count,
            scan_data
        ))
        self.conn.commit()
        
        return scan_id
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
