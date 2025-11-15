"""
License and Copyright Management Toolkit for AccuDoc.

Tools for bulk management of license notices, copyright headers,
and attribution information across documentation content.
"""

import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from accudoc.membership import MembershipManager, Permission
from accudoc.license_compliance import LicenseAnalyzer


@dataclass
class CopyrightHeader:
    """Represents a copyright header."""
    header_id: str
    organization: str
    year: str
    license_type: str
    header_text: str
    file_patterns: List[str]
    created_at: str
    created_by: Optional[str] = None


@dataclass
class Attribution:
    """Represents attribution information."""
    attribution_id: str
    component_name: str
    author: str
    license: str
    source_url: Optional[str] = None
    description: Optional[str] = None
    required_notice: Optional[str] = None


class LicenseManagementToolkit:
    """Manages licenses, copyright headers, and attributions."""
    
    def __init__(self, db_path: Optional[Path] = None,
                 membership_manager: Optional[MembershipManager] = None):
        """
        Initialize license management toolkit.
        
        Args:
            db_path: Path to database file
            membership_manager: Optional membership manager for access control
        """
        if db_path is None:
            db_path = Path.home() / '.accudoc' / 'license_management.db'
        
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
        
        # Copyright headers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copyright_headers (
                header_id TEXT PRIMARY KEY,
                organization TEXT NOT NULL,
                year TEXT NOT NULL,
                license_type TEXT NOT NULL,
                header_text TEXT NOT NULL,
                file_patterns TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT,
                organization_id TEXT
            )
        ''')
        
        # Attributions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attributions (
                attribution_id TEXT PRIMARY KEY,
                component_name TEXT NOT NULL,
                author TEXT NOT NULL,
                license TEXT NOT NULL,
                source_url TEXT,
                description TEXT,
                required_notice TEXT,
                created_at TEXT NOT NULL,
                project_id TEXT
            )
        ''')
        
        # License compliance scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS license_scans (
                scan_id TEXT PRIMARY KEY,
                repository_path TEXT NOT NULL,
                scanned_at TEXT NOT NULL,
                project_license TEXT,
                total_files INTEGER DEFAULT 0,
                files_with_headers INTEGER DEFAULT 0,
                missing_headers INTEGER DEFAULT 0,
                scan_data TEXT
            )
        ''')
        
        self.conn.commit()
    
    def create_copyright_header(self, organization: str, year: str, license_type: str,
                               file_patterns: Optional[List[str]] = None,
                               organization_id: Optional[str] = None,
                               user_id: Optional[str] = None) -> CopyrightHeader:
        """
        Create a copyright header template.
        
        Args:
            organization: Organization name
            year: Copyright year or range
            license_type: License type (MIT, Apache-2.0, etc.)
            file_patterns: File patterns to apply header to
            organization_id: Organization context
            user_id: User creating the header
            
        Returns:
            Created CopyrightHeader
        """
        # Check permission
        if self.membership_manager and user_id and organization_id:
            if not self.membership_manager.check_permission(user_id, organization_id, Permission.WRITE):
                raise PermissionError("User does not have permission to create headers")
        
        import secrets
        header_id = f"header_{secrets.token_urlsafe(12)}"
        created_at = datetime.now().isoformat()
        
        # Generate header text based on license type
        header_text = self._generate_header_text(organization, year, license_type)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO copyright_headers 
            (header_id, organization, year, license_type, header_text, file_patterns,
             created_at, created_by, organization_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            header_id,
            organization,
            year,
            license_type,
            header_text,
            json.dumps(file_patterns or ['*.py', '*.js', '*.java']),
            created_at,
            user_id,
            organization_id
        ))
        self.conn.commit()
        
        return CopyrightHeader(
            header_id=header_id,
            organization=organization,
            year=year,
            license_type=license_type,
            header_text=header_text,
            file_patterns=file_patterns or ['*.py', '*.js', '*.java'],
            created_at=created_at,
            created_by=user_id
        )
    
    def _generate_header_text(self, organization: str, year: str, license_type: str) -> str:
        """Generate copyright header text based on license type."""
        headers = {
            'MIT': f'''# Copyright (c) {year} {organization}
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.''',
            
            'Apache-2.0': f'''# Copyright {year} {organization}
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.''',
            
            'GPL-3.0': f'''# Copyright (C) {year} {organization}
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.''',
            
            'BSD-3-Clause': f'''# Copyright (c) {year}, {organization}
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.'''
        }
        
        return headers.get(license_type, f'# Copyright (c) {year} {organization}\n# Licensed under {license_type}')
    
    def add_attribution(self, component_name: str, author: str, license: str,
                       source_url: Optional[str] = None,
                       description: Optional[str] = None,
                       required_notice: Optional[str] = None,
                       project_id: Optional[str] = None) -> Attribution:
        """
        Add an attribution for a third-party component.
        
        Args:
            component_name: Name of the component
            author: Author or organization
            license: License type
            source_url: Optional source URL
            description: Optional description
            required_notice: Optional required attribution notice
            project_id: Optional project ID
            
        Returns:
            Created Attribution
        """
        import secrets
        attribution_id = f"attr_{secrets.token_urlsafe(12)}"
        created_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO attributions 
            (attribution_id, component_name, author, license, source_url,
             description, required_notice, created_at, project_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            attribution_id,
            component_name,
            author,
            license,
            source_url,
            description,
            required_notice,
            created_at,
            project_id
        ))
        self.conn.commit()
        
        return Attribution(
            attribution_id=attribution_id,
            component_name=component_name,
            author=author,
            license=license,
            source_url=source_url,
            description=description,
            required_notice=required_notice
        )
    
    def scan_for_headers(self, repository_path: str) -> Dict[str, Any]:
        """
        Scan repository for copyright headers.
        
        Args:
            repository_path: Path to repository
            
        Returns:
            Scan results
        """
        repo_path = Path(repository_path)
        
        results = {
            'total_files': 0,
            'files_with_headers': 0,
            'missing_headers': [],
            'found_headers': [],
            'unrecognized_headers': []
        }
        
        # Common source file extensions
        extensions = {'.py', '.js', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.ts'}
        
        for file in repo_path.rglob('*'):
            if file.is_file() and file.suffix in extensions:
                results['total_files'] += 1
                
                try:
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    lines = content.split('\n')[:20]  # Check first 20 lines
                    
                    header_text = '\n'.join(lines)
                    
                    # Check for copyright notice
                    if re.search(r'Copyright|©', header_text, re.IGNORECASE):
                        results['files_with_headers'] += 1
                        results['found_headers'].append(str(file.relative_to(repo_path)))
                    else:
                        results['missing_headers'].append(str(file.relative_to(repo_path)))
                        
                except Exception:
                    # Skip files that can't be read
                    continue
        
        return results
    
    def apply_header_to_file(self, file_path: Path, header: CopyrightHeader) -> bool:
        """
        Apply copyright header to a file.
        
        Args:
            file_path: Path to file
            header: Copyright header to apply
            
        Returns:
            True if successful
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check if header already exists
            if 'Copyright' in content[:500]:
                return False  # Header already exists
            
            # Determine comment style based on extension
            ext = file_path.suffix
            comment_styles = {
                '.py': '#',
                '.sh': '#',
                '.rb': '#',
                '.js': '//',
                '.ts': '//',
                '.java': '//',
                '.cpp': '//',
                '.c': '//',
                '.h': '//',
                '.go': '//',
                '.rs': '//'
            }
            
            comment_char = comment_styles.get(ext, '#')
            
            # Adapt header to comment style
            header_lines = header.header_text.split('\n')
            if comment_char != '#':
                header_lines = [line.replace('#', comment_char, 1) if line.startswith('#') else line 
                               for line in header_lines]
            
            # Prepend header to file
            new_content = '\n'.join(header_lines) + '\n\n' + content
            
            # Write back
            file_path.write_text(new_content, encoding='utf-8')
            
            return True
            
        except Exception as e:
            print(f"Error applying header to {file_path}: {e}")
            return False
    
    def bulk_apply_headers(self, repository_path: str, header_id: str) -> Dict[str, Any]:
        """
        Apply copyright headers to all matching files in repository.
        
        Args:
            repository_path: Path to repository
            header_id: Header template ID to apply
            
        Returns:
            Results of bulk operation
        """
        # Get header template
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM copyright_headers WHERE header_id = ?', (header_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError("Header not found")
        
        header = CopyrightHeader(
            header_id=row['header_id'],
            organization=row['organization'],
            year=row['year'],
            license_type=row['license_type'],
            header_text=row['header_text'],
            file_patterns=json.loads(row['file_patterns']),
            created_at=row['created_at'],
            created_by=row['created_by']
        )
        
        repo_path = Path(repository_path)
        results = {
            'total_processed': 0,
            'headers_added': 0,
            'already_had_header': 0,
            'failed': 0,
            'processed_files': []
        }
        
        # Process files matching patterns
        for pattern in header.file_patterns:
            for file in repo_path.rglob(pattern):
                if file.is_file():
                    results['total_processed'] += 1
                    
                    if self.apply_header_to_file(file, header):
                        results['headers_added'] += 1
                        results['processed_files'].append(str(file.relative_to(repo_path)))
                    else:
                        # Check if it's because header exists
                        try:
                            content = file.read_text(encoding='utf-8')
                            if 'Copyright' in content[:500]:
                                results['already_had_header'] += 1
                            else:
                                results['failed'] += 1
                        except:
                            results['failed'] += 1
        
        return results
    
    def generate_attribution_file(self, project_id: Optional[str] = None) -> str:
        """
        Generate ATTRIBUTIONS or THIRD_PARTY_LICENSES file.
        
        Args:
            project_id: Optional project ID to filter attributions
            
        Returns:
            Formatted attribution file content
        """
        cursor = self.conn.cursor()
        
        if project_id:
            cursor.execute('SELECT * FROM attributions WHERE project_id = ?', (project_id,))
        else:
            cursor.execute('SELECT * FROM attributions')
        
        attributions = []
        for row in cursor.fetchall():
            attributions.append(Attribution(
                attribution_id=row['attribution_id'],
                component_name=row['component_name'],
                author=row['author'],
                license=row['license'],
                source_url=row['source_url'],
                description=row['description'],
                required_notice=row['required_notice']
            ))
        
        lines = []
        lines.append("# Third-Party Attributions\n")
        lines.append("This project uses the following third-party components:\n")
        
        for attr in sorted(attributions, key=lambda a: a.component_name):
            lines.append(f"## {attr.component_name}\n")
            
            if attr.description:
                lines.append(f"{attr.description}\n")
            
            lines.append(f"**Author**: {attr.author}")
            lines.append(f"**License**: {attr.license}")
            
            if attr.source_url:
                lines.append(f"**Source**: {attr.source_url}")
            
            if attr.required_notice:
                lines.append(f"\n{attr.required_notice}")
            
            lines.append("\n---\n")
        
        return '\n'.join(lines)
    
    def check_license_compliance(self, repository_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive license compliance check.
        
        Args:
            repository_path: Path to repository
            
        Returns:
            Compliance check results
        """
        # Use existing LicenseAnalyzer
        analyzer = LicenseAnalyzer(repository_path)
        
        # Get project license
        project_license = analyzer.get_project_license()
        
        # Scan for headers
        header_scan = self.scan_for_headers(repository_path)
        
        # Combine results
        results = {
            'project_license': project_license,
            'header_compliance': header_scan,
            'compliance_percentage': 0.0,
            'issues': []
        }
        
        if header_scan['total_files'] > 0:
            results['compliance_percentage'] = (
                header_scan['files_with_headers'] / header_scan['total_files']
            ) * 100
        
        # Check for issues
        if not project_license:
            results['issues'].append({
                'severity': 'high',
                'message': 'No license file found in repository'
            })
        
        if results['compliance_percentage'] < 80:
            results['issues'].append({
                'severity': 'medium',
                'message': f'Only {results["compliance_percentage"]:.1f}% of files have copyright headers'
            })
        
        return results
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
