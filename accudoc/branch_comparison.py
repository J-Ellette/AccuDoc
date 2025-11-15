"""
Branch comparison module for AccuDoc.

Provides functionality to compare different branches and generate
comparison documentation including:
- File changes (added, modified, deleted)
- Line changes (additions, deletions)
- Commit differences
- Summary statistics
"""

import subprocess
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from collections import defaultdict


class BranchComparator:
    """Compares two branches/tags and generates comparison documentation."""
    
    def __init__(self, repo_path: str):
        """
        Initialize branch comparator.
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.branch_comparison')
        
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
    
    def get_available_branches(self) -> List[str]:
        """
        Get list of available branches in the repository.
        
        Returns:
            List of branch names
        """
        output = self._run_git_command(['branch', '-a'])
        if not output:
            return []
        
        branches = []
        for line in output.split('\n'):
            # Remove '* ' prefix for current branch and whitespace
            branch = line.strip().lstrip('* ')
            # Skip HEAD references
            if 'HEAD' not in branch and branch:
                # Remove 'remotes/origin/' prefix if present
                if branch.startswith('remotes/origin/'):
                    branch = branch.replace('remotes/origin/', '')
                if branch not in branches:
                    branches.append(branch)
        
        return sorted(branches)
    
    def get_current_branch(self) -> str:
        """
        Get the current branch name.
        
        Returns:
            Current branch name
        """
        output = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        return output if output else 'main'
    
    def get_available_tags(self) -> List[Dict[str, str]]:
        """
        Get list of available tags in the repository.
        
        Returns:
            List of dictionaries with tag info (name, date, message)
        """
        output = self._run_git_command(['tag', '-l', '--sort=-version:refname'])
        if not output:
            return []
        
        tags = []
        for tag_name in output.split('\n'):
            if not tag_name.strip():
                continue
            
            # Get tag details
            tag_info = {'name': tag_name}
            
            # Get tag date
            date_output = self._run_git_command(['log', '-1', '--format=%ai', tag_name])
            if date_output:
                tag_info['date'] = date_output
            
            # Get tag message (if annotated tag)
            msg_output = self._run_git_command(['tag', '-l', '--format=%(contents:subject)', tag_name])
            if msg_output:
                tag_info['message'] = msg_output
            
            tags.append(tag_info)
        
        return tags
    
    def compare_tags(self, base_tag: str, compare_tag: str) -> Dict[str, Any]:
        """
        Compare two tags and return detailed comparison data.
        
        Args:
            base_tag: Base tag name
            compare_tag: Tag to compare against base
            
        Returns:
            Dictionary containing comparison data
        """
        # Use the same comparison logic as branches
        return self.compare_branches(base_tag, compare_tag)
    
    def generate_version_history(self, tags: Optional[List[str]] = None) -> str:
        """
        Generate version history documentation from git tags.
        
        Args:
            tags: Optional list of specific tags to include. If None, uses all tags.
            
        Returns:
            Markdown formatted version history
        """
        available_tags = self.get_available_tags()
        
        if not available_tags:
            return "# Version History\n\nNo tags found in repository."
        
        # Filter to specific tags if provided
        if tags:
            available_tags = [t for t in available_tags if t['name'] in tags]
        
        md = []
        md.append("# Version History\n")
        md.append(f"**Total versions**: {len(available_tags)}\n")
        
        for i, tag in enumerate(available_tags):
            md.append(f"## {tag['name']}")
            
            if 'date' in tag:
                md.append(f"*Released: {tag['date']}*\n")
            
            if 'message' in tag and tag['message']:
                md.append(f"**{tag['message']}**\n")
            
            # Get commits since previous version
            if i < len(available_tags) - 1:
                prev_tag = available_tags[i + 1]['name']
                commits_output = self._run_git_command([
                    'log', '--oneline', '--no-merges',
                    f'{prev_tag}..{tag["name"]}'
                ])
                
                if commits_output:
                    md.append("### Changes:")
                    for line in commits_output.split('\n')[:20]:  # Limit to 20 commits
                        if line.strip():
                            md.append(f"- {line}")
                    
                    # Count total commits
                    total_commits = len(commits_output.split('\n'))
                    if total_commits > 20:
                        md.append(f"\n*... and {total_commits - 20} more commits*")
                md.append("")
            else:
                # First version
                md.append("*Initial release*\n")
        
        return '\n'.join(md)
    
    def compare_branches(self, base_branch: str, compare_branch: str) -> Dict[str, Any]:
        """
        Compare two branches and return detailed comparison data.
        
        Args:
            base_branch: Base branch name
            compare_branch: Branch to compare against base
            
        Returns:
            Dictionary containing comparison data
        """
        self.logger.info(f"Comparing branches: {base_branch} vs {compare_branch}")
        
        comparison = {
            'base_branch': base_branch,
            'compare_branch': compare_branch,
            'files_changed': [],
            'files_added': [],
            'files_deleted': [],
            'files_modified': [],
            'commits_ahead': [],
            'commits_behind': [],
            'statistics': {
                'files_changed': 0,
                'insertions': 0,
                'deletions': 0,
                'commits_ahead': 0,
                'commits_behind': 0
            }
        }
        
        # Get file changes
        diff_output = self._run_git_command([
            'diff', '--name-status',
            f'{base_branch}...{compare_branch}'
        ])
        
        if diff_output:
            for line in diff_output.split('\n'):
                if not line.strip():
                    continue
                parts = line.split('\t', 1)
                if len(parts) < 2:
                    continue
                
                status, filepath = parts[0], parts[1]
                
                if status == 'A':
                    comparison['files_added'].append(filepath)
                elif status == 'D':
                    comparison['files_deleted'].append(filepath)
                elif status.startswith('M'):
                    comparison['files_modified'].append(filepath)
                
                comparison['files_changed'].append({
                    'status': status,
                    'path': filepath
                })
        
        # Get statistics
        stat_output = self._run_git_command([
            'diff', '--shortstat',
            f'{base_branch}...{compare_branch}'
        ])
        
        if stat_output:
            # Parse: "X files changed, Y insertions(+), Z deletions(-)"
            parts = stat_output.split(',')
            for part in parts:
                part = part.strip()
                if 'file' in part:
                    comparison['statistics']['files_changed'] = int(part.split()[0])
                elif 'insertion' in part:
                    comparison['statistics']['insertions'] = int(part.split()[0])
                elif 'deletion' in part:
                    comparison['statistics']['deletions'] = int(part.split()[0])
        
        # Get commits ahead (in compare_branch but not in base_branch)
        commits_ahead = self._run_git_command([
            'log', '--oneline', '--no-merges',
            f'{base_branch}..{compare_branch}'
        ])
        
        if commits_ahead:
            for line in commits_ahead.split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        comparison['commits_ahead'].append({
                            'hash': parts[0],
                            'message': parts[1]
                        })
            comparison['statistics']['commits_ahead'] = len(comparison['commits_ahead'])
        
        # Get commits behind (in base_branch but not in compare_branch)
        commits_behind = self._run_git_command([
            'log', '--oneline', '--no-merges',
            f'{compare_branch}..{base_branch}'
        ])
        
        if commits_behind:
            for line in commits_behind.split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        comparison['commits_behind'].append({
                            'hash': parts[0],
                            'message': parts[1]
                        })
            comparison['statistics']['commits_behind'] = len(comparison['commits_behind'])
        
        return comparison
    
    def generate_comparison_markdown(self, comparison: Dict[str, Any]) -> str:
        """
        Generate markdown documentation from branch comparison.
        
        Args:
            comparison: Comparison data from compare_branches()
            
        Returns:
            Markdown formatted comparison report
        """
        base = comparison['base_branch']
        compare = comparison['compare_branch']
        stats = comparison['statistics']
        
        md = []
        md.append(f"# Branch Comparison: {compare} vs {base}\n")
        md.append("## Summary Statistics\n")
        md.append(f"- **Files Changed**: {stats['files_changed']}")
        md.append(f"- **Lines Added**: {stats['insertions']}")
        md.append(f"- **Lines Deleted**: {stats['deletions']}")
        md.append(f"- **Commits Ahead**: {stats['commits_ahead']}")
        md.append(f"- **Commits Behind**: {stats['commits_behind']}\n")
        
        # Commits ahead
        if comparison['commits_ahead']:
            md.append(f"## Commits in {compare} but not in {base}\n")
            md.append(f"*{compare} is {stats['commits_ahead']} commit(s) ahead of {base}*\n")
            for commit in comparison['commits_ahead'][:10]:  # Limit to first 10
                md.append(f"- `{commit['hash']}` {commit['message']}")
            if len(comparison['commits_ahead']) > 10:
                md.append(f"\n*... and {len(comparison['commits_ahead']) - 10} more commits*")
            md.append("")
        
        # Commits behind
        if comparison['commits_behind']:
            md.append(f"## Commits in {base} but not in {compare}\n")
            md.append(f"*{compare} is {stats['commits_behind']} commit(s) behind {base}*\n")
            for commit in comparison['commits_behind'][:10]:  # Limit to first 10
                md.append(f"- `{commit['hash']}` {commit['message']}")
            if len(comparison['commits_behind']) > 10:
                md.append(f"\n*... and {len(comparison['commits_behind']) - 10} more commits*")
            md.append("")
        
        # File changes
        if comparison['files_added']:
            md.append("## Files Added\n")
            for filepath in sorted(comparison['files_added'])[:20]:
                md.append(f"- ✅ `{filepath}`")
            if len(comparison['files_added']) > 20:
                md.append(f"\n*... and {len(comparison['files_added']) - 20} more files*")
            md.append("")
        
        if comparison['files_deleted']:
            md.append("## Files Deleted\n")
            for filepath in sorted(comparison['files_deleted'])[:20]:
                md.append(f"- ❌ `{filepath}`")
            if len(comparison['files_deleted']) > 20:
                md.append(f"\n*... and {len(comparison['files_deleted']) - 20} more files*")
            md.append("")
        
        if comparison['files_modified']:
            md.append("## Files Modified\n")
            for filepath in sorted(comparison['files_modified'])[:20]:
                md.append(f"- 📝 `{filepath}`")
            if len(comparison['files_modified']) > 20:
                md.append(f"\n*... and {len(comparison['files_modified']) - 20} more files*")
            md.append("")
        
        return '\n'.join(md)
