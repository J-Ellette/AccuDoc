"""
Documentation version control system.

Tracks changes to generated documentation, allows versioning,
diffing, and rollback capabilities.
"""

import json
import hashlib
import difflib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class VersionStatus(Enum):
    """Status of a documentation version."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class DocumentVersion:
    """Represents a single version of documentation."""
    
    version_id: str
    timestamp: str
    content_hash: str
    file_path: str
    metadata: Dict = field(default_factory=dict)
    status: str = VersionStatus.PUBLISHED.value
    tags: List[str] = field(default_factory=list)
    message: str = ""
    
    @property
    def content_hash_short(self) -> str:
        """Return shortened content hash."""
        return self.content_hash[:8]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DocumentVersion':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class VersionDiff:
    """Represents differences between two versions."""
    
    old_version: str
    new_version: str
    timestamp: str
    changes: List[Tuple[str, str]]  # (type, line) - type: +, -, or ' '
    stats: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'old_version': self.old_version,
            'new_version': self.new_version,
            'timestamp': self.timestamp,
            'changes': self.changes,
            'stats': self.stats,
        }


class DocumentationVersionControl:
    """
    Version control system for documentation.
    
    Tracks documentation changes, supports diffing, tagging, and rollback.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize version control.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.versions_dir = self.repo_path / ".accudoc" / "versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.versions_dir / "index.json"
        self.versions: List[DocumentVersion] = []
        self._load_index()
    
    def _load_index(self):
        """Load version index from disk."""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.versions = [DocumentVersion.from_dict(v) for v in data.get('versions', [])]
    
    def _save_index(self):
        """Save version index to disk."""
        data = {
            'versions': [v.to_dict() for v in self.versions],
            'updated': datetime.now().isoformat()
        }
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _generate_version_id(self) -> str:
        """Generate unique version ID."""
        timestamp = datetime.now()
        return f"v{len(self.versions) + 1}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def save_version(
        self,
        content: str,
        file_path: str,
        message: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        status: VersionStatus = VersionStatus.PUBLISHED
    ) -> DocumentVersion:
        """
        Save a new version of documentation.
        
        Args:
            content: Documentation content
            file_path: Original file path
            message: Version commit message
            tags: Optional tags for this version
            metadata: Optional metadata dictionary
            status: Version status
            
        Returns:
            Created DocumentVersion
        """
        # Compute content hash
        content_hash = self._compute_hash(content)
        
        # Check if content has changed
        if self.versions and self.versions[-1].content_hash == content_hash:
            # Content hasn't changed, return existing version
            return self.versions[-1]
        
        # Generate version ID
        version_id = self._generate_version_id()
        
        # Create version object
        version = DocumentVersion(
            version_id=version_id,
            timestamp=datetime.now().isoformat(),
            content_hash=content_hash,
            file_path=file_path,
            metadata=metadata or {},
            status=status.value,
            tags=tags or [],
            message=message
        )
        
        # Save content to file
        version_file = self.versions_dir / f"{version_id}.md"
        version_file.write_text(content, encoding='utf-8')
        
        # Add to versions list and save index
        self.versions.append(version)
        self._save_index()
        
        return version
    
    def get_version(self, version_id: str) -> Optional[DocumentVersion]:
        """
        Get a specific version.
        
        Args:
            version_id: Version identifier
            
        Returns:
            DocumentVersion or None if not found
        """
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None
    
    def get_version_content(self, version_id: str) -> Optional[str]:
        """
        Get content of a specific version.
        
        Args:
            version_id: Version identifier
            
        Returns:
            Content string or None if not found
        """
        version_file = self.versions_dir / f"{version_id}.md"
        if version_file.exists():
            return version_file.read_text(encoding='utf-8')
        return None
    
    def list_versions(
        self,
        tags: Optional[List[str]] = None,
        status: Optional[VersionStatus] = None
    ) -> List[DocumentVersion]:
        """
        List all versions with optional filtering.
        
        Args:
            tags: Filter by tags
            status: Filter by status
            
        Returns:
            List of DocumentVersions
        """
        versions = self.versions
        
        if tags:
            versions = [v for v in versions if any(t in v.tags for t in tags)]
        
        if status:
            versions = [v for v in versions if v.status == status.value]
        
        return versions
    
    def tag_version(self, version_id: str, tag: str):
        """
        Add a tag to a version.
        
        Args:
            version_id: Version identifier
            tag: Tag to add
        """
        version = self.get_version(version_id)
        if version and tag not in version.tags:
            version.tags.append(tag)
            self._save_index()
    
    def untag_version(self, version_id: str, tag: str):
        """
        Remove a tag from a version.
        
        Args:
            version_id: Version identifier
            tag: Tag to remove
        """
        version = self.get_version(version_id)
        if version and tag in version.tags:
            version.tags.remove(tag)
            self._save_index()
    
    def update_status(self, version_id: str, status: VersionStatus):
        """
        Update version status.
        
        Args:
            version_id: Version identifier
            status: New status
        """
        version = self.get_version(version_id)
        if version:
            version.status = status.value
            self._save_index()
    
    def diff_versions(
        self,
        old_version_id: str,
        new_version_id: str
    ) -> Optional[VersionDiff]:
        """
        Compute diff between two versions.
        
        Args:
            old_version_id: Old version identifier
            new_version_id: New version identifier
            
        Returns:
            VersionDiff or None if versions not found
        """
        old_content = self.get_version_content(old_version_id)
        new_content = self.get_version_content(new_version_id)
        
        if not old_content or not new_content:
            return None
        
        # Compute line-by-line diff
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=old_version_id,
            tofile=new_version_id,
            lineterm=''
        ))
        
        # Convert to our format
        changes = []
        for line in diff:
            if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                continue
            if line.startswith('+'):
                changes.append(('+', line[1:]))
            elif line.startswith('-'):
                changes.append(('-', line[1:]))
            else:
                changes.append((' ', line))
        
        # Compute stats
        additions = sum(1 for t, _ in changes if t == '+')
        deletions = sum(1 for t, _ in changes if t == '-')
        
        stats = {
            'additions': additions,
            'deletions': deletions,
            'total_changes': additions + deletions
        }
        
        return VersionDiff(
            old_version=old_version_id,
            new_version=new_version_id,
            timestamp=datetime.now().isoformat(),
            changes=changes,
            stats=stats
        )
    
    def rollback(self, version_id: str, output_path: str) -> bool:
        """
        Rollback to a previous version.
        
        Args:
            version_id: Version to rollback to
            output_path: Where to write the rolled-back content
            
        Returns:
            True if successful
        """
        content = self.get_version_content(version_id)
        if not content:
            return False
        
        # Write to output path
        Path(output_path).write_text(content, encoding='utf-8')
        
        # Save as new version with rollback tag
        self.save_version(
            content=content,
            file_path=output_path,
            message=f"Rollback to {version_id}",
            tags=["rollback"],
            metadata={"rolled_back_from": version_id}
        )
        
        return True
    
    def get_latest_version(self) -> Optional[DocumentVersion]:
        """
        Get the most recent version.
        
        Returns:
            Latest DocumentVersion or None
        """
        return self.versions[-1] if self.versions else None
    
    def get_history(self, limit: Optional[int] = None) -> List[DocumentVersion]:
        """
        Get version history.
        
        Args:
            limit: Maximum number of versions to return
            
        Returns:
            List of DocumentVersions in reverse chronological order
        """
        versions = list(reversed(self.versions))
        if limit:
            versions = versions[:limit]
        return versions
    
    def format_diff_report(self, diff: VersionDiff) -> str:
        """
        Format diff as human-readable report.
        
        Args:
            diff: VersionDiff object
            
        Returns:
            Formatted report string
        """
        report = []
        report.append(f"Diff: {diff.old_version} -> {diff.new_version}")
        report.append(f"Generated: {diff.timestamp}")
        report.append(f"Changes: +{diff.stats['additions']} -{diff.stats['deletions']}")
        report.append("-" * 60)
        
        for change_type, line in diff.changes:
            if change_type == '+':
                report.append(f"+ {line}")
            elif change_type == '-':
                report.append(f"- {line}")
            else:
                report.append(f"  {line}")
        
        return "\n".join(report)
    
    def export_history(self, output_path: str, format: str = 'json'):
        """
        Export version history to file.
        
        Args:
            output_path: Output file path
            format: Export format (json, csv, markdown)
        """
        if format == 'json':
            data = {
                'repository': str(self.repo_path),
                'total_versions': len(self.versions),
                'versions': [v.to_dict() for v in self.versions]
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        elif format == 'csv':
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Version ID', 'Timestamp', 'Hash', 'Status', 'Tags', 'Message'])
                for v in self.versions:
                    writer.writerow([
                        v.version_id,
                        v.timestamp,
                        v.content_hash_short,
                        v.status,
                        ','.join(v.tags),
                        v.message
                    ])
        
        elif format == 'markdown':
            lines = []
            lines.append("# Documentation Version History")
            lines.append(f"\nRepository: {self.repo_path}")
            lines.append(f"Total Versions: {len(self.versions)}\n")
            
            for v in reversed(self.versions):
                lines.append(f"## {v.version_id}")
                lines.append(f"- **Timestamp**: {v.timestamp}")
                lines.append(f"- **Hash**: {v.content_hash_short}")
                lines.append(f"- **Status**: {v.status}")
                if v.tags:
                    lines.append(f"- **Tags**: {', '.join(v.tags)}")
                if v.message:
                    lines.append(f"- **Message**: {v.message}")
                lines.append("")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
