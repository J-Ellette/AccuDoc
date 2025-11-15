"""
Code quality metrics module for AccuDoc.

Analyzes code quality metrics including:
- Cyclomatic complexity
- Code maintainability index
- Lines of code metrics
- Code duplication detection
- Function/method length analysis
"""

import re
import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict, Counter


class CodeQualityAnalyzer:
    """Analyzes code quality metrics."""
    
    def __init__(self, repo_path: str):
        """
        Initialize code quality analyzer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.code_quality')
        
    def calculate_cyclomatic_complexity(self, code: str, language: str) -> int:
        """
        Calculate cyclomatic complexity for a function/file.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity
        
        if language == 'python':
            # Count decision points in Python
            keywords = ['if', 'elif', 'for', 'while', 'and', 'or', 'except', 'with']
            for keyword in keywords:
                # Use word boundaries to avoid matching substrings
                pattern = r'\b' + keyword + r'\b'
                complexity += len(re.findall(pattern, code))
        
        elif language in ['javascript', 'typescript']:
            # Count decision points in JavaScript/TypeScript
            keywords = ['if', 'for', 'while', 'case', '&&', '\\|\\|', '\\?', 'catch']
            for keyword in keywords:
                if keyword in ['&&', '\\|\\|', '\\?']:
                    complexity += len(re.findall(keyword, code))
                else:
                    pattern = r'\b' + keyword + r'\b'
                    complexity += len(re.findall(pattern, code))
        
        return complexity
    
    def calculate_maintainability_index(self, loc: int, complexity: int, 
                                       halstead_volume: float = None) -> float:
        """
        Calculate maintainability index (0-100, higher is better).
        
        Formula: MAX(0,(171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code))*100 / 171)
        
        Simplified when Halstead volume not available:
        MI = 171 - 0.23 * CC - 16.2 * ln(LOC)
        
        Args:
            loc: Lines of code
            complexity: Cyclomatic complexity
            halstead_volume: Optional Halstead volume
            
        Returns:
            Maintainability index (0-100)
        """
        if loc <= 0:
            return 100.0
        
        if halstead_volume:
            mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * complexity - 16.2 * math.log(loc)
        else:
            # Simplified formula
            mi = 171 - 0.23 * complexity - 16.2 * math.log(loc)
        
        # Normalize to 0-100
        mi = max(0, (mi * 100 / 171))
        return min(100, mi)
    
    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Analyze a single file for quality metrics.
        
        Args:
            filepath: Path to file
            
        Returns:
            Quality metrics dictionary
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Determine language
            ext = filepath.suffix
            language = self._get_language(ext)
            
            if not language:
                return None
            
            # Count lines
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Count non-empty, non-comment lines
            code_lines = 0
            comment_lines = 0
            blank_lines = 0
            
            in_multiline_comment = False
            
            for line in lines:
                stripped = line.strip()
                
                if not stripped:
                    blank_lines += 1
                    continue
                
                # Handle multi-line comments
                if language == 'python':
                    if '"""' in stripped or "'''" in stripped:
                        in_multiline_comment = not in_multiline_comment
                        comment_lines += 1
                        continue
                    elif in_multiline_comment:
                        comment_lines += 1
                        continue
                    elif stripped.startswith('#'):
                        comment_lines += 1
                        continue
                elif language in ['javascript', 'typescript']:
                    if '/*' in stripped:
                        in_multiline_comment = True
                        comment_lines += 1
                        continue
                    elif '*/' in stripped:
                        in_multiline_comment = False
                        comment_lines += 1
                        continue
                    elif in_multiline_comment:
                        comment_lines += 1
                        continue
                    elif stripped.startswith('//'):
                        comment_lines += 1
                        continue
                
                code_lines += 1
            
            # Calculate complexity
            complexity = self.calculate_cyclomatic_complexity(content, language)
            
            # Calculate maintainability index
            mi = self.calculate_maintainability_index(code_lines, complexity)
            
            # Determine quality rating
            if mi >= 85:
                rating = 'excellent'
            elif mi >= 65:
                rating = 'good'
            elif mi >= 40:
                rating = 'fair'
            else:
                rating = 'poor'
            
            return {
                'file': str(filepath.relative_to(self.repo_path)),
                'language': language,
                'metrics': {
                    'total_lines': total_lines,
                    'code_lines': code_lines,
                    'comment_lines': comment_lines,
                    'blank_lines': blank_lines,
                    'cyclomatic_complexity': complexity,
                    'maintainability_index': round(mi, 2),
                    'rating': rating
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {filepath}: {e}")
            return None
    
    def _get_language(self, ext: str) -> Optional[str]:
        """Get language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }
        return ext_map.get(ext)
    
    def analyze_directory(self, dirpath: Path = None, 
                         extensions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze all code files in a directory.
        
        Args:
            dirpath: Directory to analyze (defaults to repo root)
            extensions: File extensions to analyze
            
        Returns:
            List of file analysis results
        """
        if dirpath is None:
            dirpath = self.repo_path
        
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs']
        
        results = []
        
        for ext in extensions:
            for filepath in dirpath.rglob(f'*{ext}'):
                # Skip common directories
                if any(part in filepath.parts for part in ['node_modules', 'venv', '.venv', 'dist', 'build', '__pycache__']):
                    continue
                
                result = self.analyze_file(filepath)
                if result:
                    results.append(result)
        
        return results
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics from analysis results.
        
        Args:
            results: Results from analyze_directory()
            
        Returns:
            Summary statistics
        """
        if not results:
            return {}
        
        summary = {
            'total_files': len(results),
            'by_language': defaultdict(int),
            'by_rating': defaultdict(int),
            'totals': {
                'total_lines': 0,
                'code_lines': 0,
                'comment_lines': 0,
                'blank_lines': 0
            },
            'complexity': {
                'average': 0,
                'max': 0,
                'high_complexity_files': []
            },
            'maintainability': {
                'average': 0,
                'min': 100,
                'low_mi_files': []
            }
        }
        
        total_complexity = 0
        total_mi = 0
        
        for result in results:
            lang = result['language']
            metrics = result['metrics']
            rating = metrics['rating']
            
            summary['by_language'][lang] += 1
            summary['by_rating'][rating] += 1
            
            summary['totals']['total_lines'] += metrics['total_lines']
            summary['totals']['code_lines'] += metrics['code_lines']
            summary['totals']['comment_lines'] += metrics['comment_lines']
            summary['totals']['blank_lines'] += metrics['blank_lines']
            
            complexity = metrics['cyclomatic_complexity']
            mi = metrics['maintainability_index']
            
            total_complexity += complexity
            total_mi += mi
            
            # Track high complexity files
            if complexity > 10:
                summary['complexity']['high_complexity_files'].append({
                    'file': result['file'],
                    'complexity': complexity
                })
            
            # Track low maintainability files
            if mi < 65:
                summary['maintainability']['low_mi_files'].append({
                    'file': result['file'],
                    'mi': mi
                })
            
            # Update max/min
            summary['complexity']['max'] = max(summary['complexity']['max'], complexity)
            summary['maintainability']['min'] = min(summary['maintainability']['min'], mi)
        
        # Calculate averages
        summary['complexity']['average'] = round(total_complexity / len(results), 2)
        summary['maintainability']['average'] = round(total_mi / len(results), 2)
        
        # Sort high complexity files
        summary['complexity']['high_complexity_files'].sort(key=lambda x: x['complexity'], reverse=True)
        summary['maintainability']['low_mi_files'].sort(key=lambda x: x['mi'])
        
        return summary
    
    def generate_report(self, results: List[Dict[str, Any]], 
                       summary: Dict[str, Any] = None) -> str:
        """
        Generate markdown report from analysis.
        
        Args:
            results: Results from analyze_directory()
            summary: Optional pre-calculated summary
            
        Returns:
            Markdown formatted report
        """
        if not results:
            return "# Code Quality Report\n\nNo code files analyzed."
        
        if summary is None:
            summary = self.generate_summary(results)
        
        md = []
        md.append("# Code Quality Report\n")
        
        # Overview
        md.append("## Overview\n")
        md.append(f"**Files Analyzed**: {summary['total_files']}")
        md.append(f"**Total Lines**: {summary['totals']['total_lines']:,}")
        md.append(f"**Code Lines**: {summary['totals']['code_lines']:,}")
        md.append(f"**Comment Lines**: {summary['totals']['comment_lines']:,}")
        md.append(f"**Average Complexity**: {summary['complexity']['average']}")
        md.append(f"**Average Maintainability**: {summary['maintainability']['average']:.1f}/100\n")
        
        # Quality distribution
        md.append("## Quality Distribution\n")
        total = summary['total_files']
        for rating in ['excellent', 'good', 'fair', 'poor']:
            count = summary['by_rating'].get(rating, 0)
            pct = (count / total * 100) if total > 0 else 0
            icon = {'excellent': '🟢', 'good': '🟡', 'fair': '🟠', 'poor': '🔴'}[rating]
            md.append(f"- {icon} **{rating.title()}**: {count} files ({pct:.1f}%)")
        md.append("")
        
        # Language breakdown
        if summary['by_language']:
            md.append("## Languages\n")
            for lang, count in sorted(summary['by_language'].items(), key=lambda x: x[1], reverse=True):
                pct = (count / total * 100) if total > 0 else 0
                md.append(f"- **{lang.title()}**: {count} files ({pct:.1f}%)")
            md.append("")
        
        # High complexity files
        if summary['complexity']['high_complexity_files']:
            md.append("## ⚠️ High Complexity Files\n")
            md.append("*Files with cyclomatic complexity > 10*\n")
            md.append("| File | Complexity | Action |")
            md.append("|------|------------|--------|")
            
            for item in summary['complexity']['high_complexity_files'][:10]:
                complexity = item['complexity']
                action = "Refactor" if complexity > 20 else "Review"
                md.append(f"| {item['file']} | {complexity} | {action} |")
            
            if len(summary['complexity']['high_complexity_files']) > 10:
                md.append(f"\n*... and {len(summary['complexity']['high_complexity_files']) - 10} more files*")
            md.append("")
        
        # Low maintainability files
        if summary['maintainability']['low_mi_files']:
            md.append("## ⚠️ Low Maintainability Files\n")
            md.append("*Files with maintainability index < 65*\n")
            md.append("| File | MI Score | Status |")
            md.append("|------|----------|--------|")
            
            for item in summary['maintainability']['low_mi_files'][:10]:
                mi = item['mi']
                status = "Poor" if mi < 40 else "Fair"
                md.append(f"| {item['file']} | {mi:.1f} | {status} |")
            
            if len(summary['maintainability']['low_mi_files']) > 10:
                md.append(f"\n*... and {len(summary['maintainability']['low_mi_files']) - 10} more files*")
            md.append("")
        
        # Recommendations
        md.append("## Recommendations\n")
        
        avg_mi = summary['maintainability']['average']
        if avg_mi >= 85:
            md.append("- ✅ Excellent code maintainability overall")
        elif avg_mi >= 65:
            md.append("- 🟡 Good maintainability, but some files need attention")
        else:
            md.append("- ⚠️ Below average maintainability, refactoring recommended")
        
        if summary['complexity']['high_complexity_files']:
            md.append(f"- Refactor {len(summary['complexity']['high_complexity_files'])} high-complexity files")
        
        if summary['maintainability']['low_mi_files']:
            md.append(f"- Improve {len(summary['maintainability']['low_mi_files'])} low-maintainability files")
        
        comment_ratio = (summary['totals']['comment_lines'] / summary['totals']['code_lines'] * 100) if summary['totals']['code_lines'] > 0 else 0
        if comment_ratio < 10:
            md.append(f"- Consider adding more comments (current: {comment_ratio:.1f}%)")
        
        md.append("")
        
        return '\n'.join(md)
