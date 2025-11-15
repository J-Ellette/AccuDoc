"""
Breaking changes detection module for AccuDoc.

Analyzes code changes between versions to detect potential breaking changes:
- API signature changes (function/method signatures)
- Removed public functions/classes
- Changed return types
- Modified parameter requirements
- Semantic versioning violations
"""

import re
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
import subprocess
from collections import defaultdict


class BreakingChangesDetector:
    """Detects breaking changes between versions."""
    
    def __init__(self, repo_path: str):
        """
        Initialize breaking changes detector.
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.breaking_changes')
        
    def _run_git_command(self, args: List[str]) -> str:
        """Run a git command and return output."""
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
        except Exception as e:
            self.logger.error(f"Error running git command: {e}")
            return ""
    
    def _extract_python_signatures(self, code: str) -> Set[str]:
        """Extract Python function/class signatures from code."""
        signatures = set()
        
        # Extract class definitions
        class_pattern = r'^class\s+(\w+).*?:'
        for match in re.finditer(class_pattern, code, re.MULTILINE):
            signatures.add(f"class {match.group(1)}")
        
        # Extract function/method definitions
        func_pattern = r'^(?:async\s+)?def\s+(\w+)\s*\((.*?)\)'
        for match in re.finditer(func_pattern, code, re.MULTILINE):
            func_name = match.group(1)
            params = match.group(2)
            # Simplify parameters (remove defaults and type hints)
            params_simple = re.sub(r':\s*\w+', '', params)
            params_simple = re.sub(r'=\s*[^,)]+', '', params_simple)
            params_simple = ','.join([p.strip() for p in params_simple.split(',') if p.strip()])
            signatures.add(f"def {func_name}({params_simple})")
        
        return signatures
    
    def _extract_javascript_signatures(self, code: str) -> Set[str]:
        """Extract JavaScript function/class signatures from code."""
        signatures = set()
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, code):
            signatures.add(f"class {match.group(1)}")
        
        # Extract function declarations
        func_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\((.*?)\)'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            params = match.group(2).split(',')
            param_names = [p.strip().split('=')[0].strip() for p in params if p.strip()]
            signatures.add(f"function {func_name}({','.join(param_names)})")
        
        # Extract arrow functions assigned to const/let/var
        arrow_pattern = r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>'
        for match in re.finditer(arrow_pattern, code):
            func_name = match.group(1)
            params = match.group(2).split(',')
            param_names = [p.strip().split('=')[0].strip() for p in params if p.strip()]
            signatures.add(f"const {func_name}({','.join(param_names)})")
        
        return signatures
    
    def _get_file_content_at_ref(self, filepath: str, ref: str) -> Optional[str]:
        """Get file content at a specific git reference."""
        try:
            content = self._run_git_command(['show', f'{ref}:{filepath}'])
            return content if content else None
        except:
            return None
    
    def analyze_changes(self, from_ref: str, to_ref: str, file_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Analyze changes between two git references.
        
        Args:
            from_ref: Starting reference (tag, branch, commit)
            to_ref: Ending reference
            file_patterns: Optional list of file patterns to analyze (e.g., ['*.py', '*.js'])
            
        Returns:
            Dictionary with breaking changes analysis
        """
        if file_patterns is None:
            file_patterns = ['*.py', '*.js', '*.ts', '*.jsx', '*.tsx']
        
        # Get changed files
        diff_output = self._run_git_command([
            'diff', '--name-only', '--diff-filter=ADMR',
            f'{from_ref}..{to_ref}'
        ])
        
        if not diff_output:
            return {
                'status': 'no_changes',
                'message': 'No changes found between references'
            }
        
        changed_files = diff_output.split('\n')
        
        # Filter files by patterns
        relevant_files = []
        for filepath in changed_files:
            for pattern in file_patterns:
                ext = pattern.lstrip('*')
                if filepath.endswith(ext):
                    relevant_files.append(filepath)
                    break
        
        breaking_changes = {
            'removed_signatures': [],
            'modified_signatures': [],
            'added_signatures': [],
            'removed_files': [],
            'renamed_files': [],
            'summary': {
                'potential_breaking': 0,
                'safe_changes': 0,
                'files_analyzed': 0
            }
        }
        
        for filepath in relevant_files:
            old_content = self._get_file_content_at_ref(filepath, from_ref)
            new_content = self._get_file_content_at_ref(filepath, to_ref)
            
            # Check if file was deleted
            if old_content and not new_content:
                breaking_changes['removed_files'].append(filepath)
                breaking_changes['summary']['potential_breaking'] += 1
                continue
            
            # Skip if file is new
            if not old_content and new_content:
                continue
            
            # Analyze signatures based on file type
            if filepath.endswith('.py'):
                old_sigs = self._extract_python_signatures(old_content)
                new_sigs = self._extract_python_signatures(new_content)
            elif filepath.endswith(('.js', '.ts', '.jsx', '.tsx')):
                old_sigs = self._extract_javascript_signatures(old_content)
                new_sigs = self._extract_javascript_signatures(new_content)
            else:
                continue
            
            # Find removed and modified signatures
            removed = old_sigs - new_sigs
            added = new_sigs - old_sigs
            
            if removed:
                for sig in removed:
                    breaking_changes['removed_signatures'].append({
                        'file': filepath,
                        'signature': sig
                    })
                    breaking_changes['summary']['potential_breaking'] += 1
            
            if added:
                # Check if it's a modification (similar name but different params)
                for new_sig in added:
                    new_name = new_sig.split('(')[0]
                    for old_sig in removed:
                        old_name = old_sig.split('(')[0]
                        if old_name == new_name:
                            breaking_changes['modified_signatures'].append({
                                'file': filepath,
                                'old': old_sig,
                                'new': new_sig
                            })
                            break
            
            breaking_changes['summary']['files_analyzed'] += 1
        
        # Calculate safe changes
        breaking_changes['summary']['safe_changes'] = (
            breaking_changes['summary']['files_analyzed'] - 
            len(breaking_changes['removed_files']) -
            len(breaking_changes['removed_signatures']) -
            len(breaking_changes['modified_signatures'])
        )
        
        return breaking_changes
    
    def check_semantic_versioning(self, from_version: str, to_version: str, 
                                  changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if version bump follows semantic versioning based on changes.
        
        Args:
            from_version: Old version (e.g., "1.2.3")
            to_version: New version (e.g., "2.0.0")
            changes: Changes from analyze_changes()
            
        Returns:
            Semantic versioning compliance analysis
        """
        # Parse versions
        from_parts = self._parse_version(from_version)
        to_parts = self._parse_version(to_version)
        
        if not from_parts or not to_parts:
            return {'error': 'Invalid version format'}
        
        from_major, from_minor, from_patch = from_parts
        to_major, to_minor, to_patch = to_parts
        
        # Determine what changed
        major_bump = to_major > from_major
        minor_bump = to_major == from_major and to_minor > from_minor
        patch_bump = to_major == from_major and to_minor == from_minor and to_patch > from_patch
        
        # Determine if breaking changes exist
        has_breaking = (
            changes['summary']['potential_breaking'] > 0 or
            len(changes['removed_signatures']) > 0 or
            len(changes['modified_signatures']) > 0 or
            len(changes['removed_files']) > 0
        )
        
        result = {
            'from_version': from_version,
            'to_version': to_version,
            'version_bump': 'major' if major_bump else 'minor' if minor_bump else 'patch',
            'has_breaking_changes': has_breaking,
            'compliant': True,
            'recommendations': []
        }
        
        # Check compliance
        if has_breaking and not major_bump:
            result['compliant'] = False
            result['recommendations'].append(
                f"Breaking changes detected but version only bumped {result['version_bump']}. "
                "Should be major version bump (X.0.0)"
            )
        elif not has_breaking and major_bump:
            result['recommendations'].append(
                "Major version bump without detected breaking changes. "
                "Consider if this is intentional."
            )
        
        return result
    
    def _parse_version(self, version: str) -> Optional[Tuple[int, int, int]]:
        """Parse semantic version string."""
        version = version.lstrip('v')
        parts = version.split('.')
        try:
            if len(parts) >= 3:
                return (int(parts[0]), int(parts[1]), int(parts[2].split('-')[0]))
        except:
            pass
        return None
    
    def generate_report(self, changes: Dict[str, Any], 
                       semver_check: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate markdown report for breaking changes.
        
        Args:
            changes: Changes from analyze_changes()
            semver_check: Optional semantic versioning check results
            
        Returns:
            Markdown formatted report
        """
        md = []
        md.append("# Breaking Changes Report\n")
        
        if changes.get('status') == 'no_changes':
            return "# Breaking Changes Report\n\nNo changes detected."
        
        summary = changes['summary']
        md.append("## Summary\n")
        md.append(f"- **Files Analyzed**: {summary['files_analyzed']}")
        md.append(f"- **Potential Breaking Changes**: {summary['potential_breaking']}")
        md.append(f"- **Safe Changes**: {summary['safe_changes']}\n")
        
        # Semantic versioning compliance
        if semver_check:
            md.append("## Semantic Versioning Compliance\n")
            md.append(f"**Version**: {semver_check['from_version']} → {semver_check['to_version']}")
            md.append(f"**Bump Type**: {semver_check['version_bump']}")
            md.append(f"**Has Breaking Changes**: {'Yes' if semver_check['has_breaking_changes'] else 'No'}")
            
            if semver_check['compliant']:
                md.append(f"**Status**: ✅ Compliant")
            else:
                md.append(f"**Status**: ⚠️ Non-compliant")
            
            if semver_check.get('recommendations'):
                md.append("\n**Recommendations**:")
                for rec in semver_check['recommendations']:
                    md.append(f"- {rec}")
            md.append("")
        
        # Removed files
        if changes['removed_files']:
            md.append("## ❌ Removed Files (Breaking)\n")
            for filepath in changes['removed_files']:
                md.append(f"- `{filepath}`")
            md.append("")
        
        # Removed signatures
        if changes['removed_signatures']:
            md.append("## ❌ Removed Functions/Classes (Breaking)\n")
            files_grouped = defaultdict(list)
            for item in changes['removed_signatures']:
                files_grouped[item['file']].append(item['signature'])
            
            for filepath in sorted(files_grouped.keys()):
                md.append(f"\n**{filepath}**:")
                for sig in files_grouped[filepath]:
                    md.append(f"- `{sig}`")
            md.append("")
        
        # Modified signatures
        if changes['modified_signatures']:
            md.append("## ⚠️ Modified Signatures (Potentially Breaking)\n")
            files_grouped = defaultdict(list)
            for item in changes['modified_signatures']:
                files_grouped[item['file']].append((item['old'], item['new']))
            
            for filepath in sorted(files_grouped.keys()):
                md.append(f"\n**{filepath}**:")
                for old, new in files_grouped[filepath]:
                    md.append(f"- `{old}` → `{new}`")
            md.append("")
        
        # Recommendations
        md.append("## Recommendations\n")
        if summary['potential_breaking'] > 0:
            md.append("- **Review all breaking changes** before releasing")
            md.append("- **Update changelog** with breaking changes")
            md.append("- **Document migration guide** for users")
            md.append("- **Consider deprecation warnings** before removal")
        else:
            md.append("- No breaking changes detected")
            md.append("- Safe to release as minor or patch version")
        md.append("")
        
        return '\n'.join(md)
