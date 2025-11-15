"""
Pull Request documentation module for AccuDoc.

Generates documentation for pull request reviews, including:
- PR summary and metadata
- Code changes analysis
- Documentation impact assessment
- Review checklist
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import json


class PRDocGenerator:
    """Generate documentation for pull request reviews."""
    
    def __init__(self, repo_path: str):
        """
        Initialize PR documentation generator.
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.pr_docs')
    
    def _run_git_command(self, args: List[str]) -> str:
        """
        Run a git command and return output.
        
        Args:
            args: Git command arguments
            
        Returns:
            Command output as string
        """
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                self.logger.warning(f"Git command failed: {result.stderr}")
                return ""
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            self.logger.error("Git command timed out")
            return ""
        except Exception as e:
            self.logger.error(f"Error running git command: {e}")
            return ""
    
    def analyze_pr_changes(self, base_branch: str, head_branch: str) -> Dict[str, Any]:
        """
        Analyze changes in a pull request.
        
        Args:
            base_branch: Base branch name
            head_branch: Head branch name (PR branch)
            
        Returns:
            Dictionary with PR analysis data
        """
        analysis = {
            'base_branch': base_branch,
            'head_branch': head_branch,
            'files_changed': [],
            'statistics': {
                'total_files': 0,
                'additions': 0,
                'deletions': 0,
                'commits': 0
            },
            'changes_by_type': {
                'code': [],
                'tests': [],
                'documentation': [],
                'config': [],
                'other': []
            },
            'commits': []
        }
        
        # Get file changes with stats
        diff_stat = self._run_git_command([
            'diff', '--stat',
            f'{base_branch}...{head_branch}'
        ])
        
        if diff_stat:
            lines = diff_stat.split('\n')
            for line in lines[:-1]:  # Last line is summary
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    filepath = parts[0].strip()
                    stats = parts[1].strip()
                    
                    file_info = {
                        'path': filepath,
                        'stats': stats
                    }
                    
                    analysis['files_changed'].append(file_info)
                    
                    # Categorize file
                    if any(ext in filepath for ext in ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rb', '.php']):
                        if 'test' in filepath.lower():
                            analysis['changes_by_type']['tests'].append(filepath)
                        else:
                            analysis['changes_by_type']['code'].append(filepath)
                    elif any(ext in filepath for ext in ['.md', '.rst', '.txt', '.adoc']):
                        analysis['changes_by_type']['documentation'].append(filepath)
                    elif any(ext in filepath for ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']):
                        analysis['changes_by_type']['config'].append(filepath)
                    else:
                        analysis['changes_by_type']['other'].append(filepath)
            
            # Parse summary line
            summary = lines[-1]
            analysis['statistics']['total_files'] = len(analysis['files_changed'])
        
        # Get detailed statistics
        shortstat = self._run_git_command([
            'diff', '--shortstat',
            f'{base_branch}...{head_branch}'
        ])
        
        if shortstat:
            parts = shortstat.split(',')
            for part in parts:
                part = part.strip()
                if 'insertion' in part:
                    analysis['statistics']['additions'] = int(part.split()[0])
                elif 'deletion' in part:
                    analysis['statistics']['deletions'] = int(part.split()[0])
        
        # Get commits
        commits_output = self._run_git_command([
            'log', '--oneline', '--no-merges',
            f'{base_branch}..{head_branch}'
        ])
        
        if commits_output:
            for line in commits_output.split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        analysis['commits'].append({
                            'hash': parts[0],
                            'message': parts[1]
                        })
            analysis['statistics']['commits'] = len(analysis['commits'])
        
        return analysis
    
    def generate_pr_documentation(self, pr_data: Dict[str, Any], 
                                 pr_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate markdown documentation for a pull request.
        
        Args:
            pr_data: PR analysis data from analyze_pr_changes()
            pr_metadata: Optional PR metadata (title, description, author, etc.)
            
        Returns:
            Markdown formatted PR documentation
        """
        md = []
        
        # Header
        if pr_metadata:
            md.append(f"# Pull Request: {pr_metadata.get('title', 'Untitled')}\n")
            if 'number' in pr_metadata:
                md.append(f"**PR #{pr_metadata['number']}**\n")
            if 'author' in pr_metadata:
                md.append(f"**Author**: {pr_metadata['author']}")
            if 'description' in pr_metadata and pr_metadata['description']:
                md.append(f"\n{pr_metadata['description']}\n")
        else:
            md.append("# Pull Request Documentation\n")
        
        # Branch information
        md.append("## Branch Information\n")
        md.append(f"- **Base branch**: `{pr_data['base_branch']}`")
        md.append(f"- **Head branch**: `{pr_data['head_branch']}`\n")
        
        # Statistics
        stats = pr_data['statistics']
        md.append("## Summary Statistics\n")
        md.append(f"- **Files changed**: {stats['total_files']}")
        md.append(f"- **Lines added**: +{stats['additions']}")
        md.append(f"- **Lines deleted**: -{stats['deletions']}")
        md.append(f"- **Commits**: {stats['commits']}\n")
        
        # Changes by type
        changes = pr_data['changes_by_type']
        if any(changes.values()):
            md.append("## Changes by Type\n")
            
            if changes['code']:
                md.append(f"### Code Files ({len(changes['code'])})")
                for filepath in changes['code'][:10]:
                    md.append(f"- `{filepath}`")
                if len(changes['code']) > 10:
                    md.append(f"- *... and {len(changes['code']) - 10} more*")
                md.append("")
            
            if changes['tests']:
                md.append(f"### Test Files ({len(changes['tests'])})")
                for filepath in changes['tests'][:10]:
                    md.append(f"- `{filepath}`")
                if len(changes['tests']) > 10:
                    md.append(f"- *... and {len(changes['tests']) - 10} more*")
                md.append("")
            
            if changes['documentation']:
                md.append(f"### Documentation Files ({len(changes['documentation'])})")
                for filepath in changes['documentation']:
                    md.append(f"- `{filepath}`")
                md.append("")
            
            if changes['config']:
                md.append(f"### Configuration Files ({len(changes['config'])})")
                for filepath in changes['config']:
                    md.append(f"- `{filepath}`")
                md.append("")
        
        # Commits
        if pr_data['commits']:
            md.append("## Commits\n")
            for commit in pr_data['commits'][:20]:
                md.append(f"- `{commit['hash']}` {commit['message']}")
            if len(pr_data['commits']) > 20:
                md.append(f"\n*... and {len(pr_data['commits']) - 20} more commits*")
            md.append("")
        
        # Review checklist
        md.append("## Review Checklist\n")
        md.append("- [ ] Code changes are properly documented")
        md.append("- [ ] Tests are included/updated for new functionality")
        md.append("- [ ] No breaking changes introduced")
        md.append("- [ ] Code follows project style guidelines")
        md.append("- [ ] All tests pass")
        md.append("- [ ] Documentation is updated")
        md.append("- [ ] No security vulnerabilities introduced")
        md.append("- [ ] Performance impact is acceptable\n")
        
        # Documentation impact assessment
        doc_impact = "Low"
        if changes['documentation']:
            doc_impact = "High"
        elif changes['code']:
            doc_impact = "Medium"
        
        md.append("## Documentation Impact\n")
        md.append(f"**Assessment**: {doc_impact}\n")
        
        if changes['code'] and not changes['documentation']:
            md.append("⚠️ **Note**: Code changes detected but no documentation updates found. "
                     "Consider updating relevant documentation.\n")
        
        return '\n'.join(md)
    
    def generate_pr_review_template(self) -> str:
        """
        Generate a template for PR reviews.
        
        Returns:
            Markdown template for PR reviews
        """
        return '''# Pull Request Review

## Summary
<!-- Briefly describe what this PR does -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test improvement

## Testing
<!-- Describe testing performed -->

## Documentation
<!-- List documentation changes or explain why none needed -->

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Backward compatibility maintained
- [ ] Security considerations addressed

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Additional Notes
<!-- Any additional information for reviewers -->
'''
