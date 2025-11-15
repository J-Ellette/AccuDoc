"""
Trend Analysis module for AccuDoc.
Analyzes repository history to show how the project has grown over time.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import subprocess
import json
from pathlib import Path


class TrendAnalyzer:
    """Analyzes repository trends over time."""
    
    def __init__(self, repo_path: str):
        """
        Initialize trend analyzer.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
        self.trends = {}
    
    def analyze(self, period: str = 'all', intervals: int = 10) -> Dict:
        """
        Analyze repository trends over specified period.
        
        Args:
            period: Time period ('week', 'month', 'quarter', 'year', 'all')
            intervals: Number of data points to collect
            
        Returns:
            Dictionary containing trend data
        """
        # Get time range
        time_points = self._get_time_points(period, intervals)
        
        # Collect metrics at each time point
        trends = {
            'period': period,
            'intervals': intervals,
            'time_points': [],
            'commit_count': [],
            'file_count': [],
            'contributors': [],
            'lines_added': [],
            'lines_deleted': [],
            'languages': []
        }
        
        for time_point in time_points:
            trends['time_points'].append(time_point.isoformat())
            
            # Get commit count up to this time
            commit_count = self._get_commit_count(time_point)
            trends['commit_count'].append(commit_count)
            
            # Get file count at this time
            file_count = self._get_file_count(time_point)
            trends['file_count'].append(file_count)
            
            # Get unique contributors up to this time
            contributor_count = self._get_contributor_count(time_point)
            trends['contributors'].append(contributor_count)
            
            # Get lines added/deleted
            lines_data = self._get_lines_stats(time_point)
            trends['lines_added'].append(lines_data['added'])
            trends['lines_deleted'].append(lines_data['deleted'])
            
            # Get language distribution
            languages = self._get_language_distribution(time_point)
            trends['languages'].append(languages)
        
        # Calculate growth rates
        trends['growth_rates'] = self._calculate_growth_rates(trends)
        
        # Add summary statistics
        trends['summary'] = self._generate_summary(trends)
        
        self.trends = trends
        return trends
    
    def _get_time_points(self, period: str, intervals: int) -> List[datetime]:
        """Get time points for analysis."""
        now = datetime.now()
        
        if period == 'week':
            delta = timedelta(days=7)
        elif period == 'month':
            delta = timedelta(days=30)
        elif period == 'quarter':
            delta = timedelta(days=90)
        elif period == 'year':
            delta = timedelta(days=365)
        else:  # 'all'
            # Get first commit date
            first_commit = self._get_first_commit_date()
            if first_commit:
                delta = now - first_commit
            else:
                delta = timedelta(days=365)  # Default to 1 year
        
        # Generate time points
        time_points = []
        for i in range(intervals + 1):
            time_point = now - (delta * (intervals - i) / intervals)
            time_points.append(time_point)
        
        return time_points
    
    def _get_first_commit_date(self) -> Optional[datetime]:
        """Get date of first commit."""
        try:
            result = subprocess.run(
                ['git', 'log', '--reverse', '--format=%ct', '-n', '1'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                timestamp = int(result.stdout.strip())
                return datetime.fromtimestamp(timestamp)
        except Exception:
            pass
        return None
    
    def _get_commit_count(self, until_date: datetime) -> int:
        """Get number of commits up to a specific date."""
        try:
            date_str = until_date.strftime('%Y-%m-%d')
            result = subprocess.run(
                ['git', 'rev-list', '--count', '--all', f'--until={date_str}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except Exception:
            pass
        return 0
    
    def _get_file_count(self, at_date: datetime) -> int:
        """Get number of files at a specific date."""
        try:
            date_str = at_date.strftime('%Y-%m-%d')
            # Get commit hash at this date
            result = subprocess.run(
                ['git', 'rev-list', '-n', '1', f'--until={date_str}', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                commit_hash = result.stdout.strip()
                # Count files at that commit
                result = subprocess.run(
                    ['git', 'ls-tree', '-r', '--name-only', commit_hash],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        except Exception:
            pass
        return 0
    
    def _get_contributor_count(self, until_date: datetime) -> int:
        """Get number of unique contributors up to a specific date."""
        try:
            date_str = until_date.strftime('%Y-%m-%d')
            result = subprocess.run(
                ['git', 'shortlog', '-s', '-n', f'--until={date_str}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        except Exception:
            pass
        return 0
    
    def _get_lines_stats(self, until_date: datetime) -> Dict[str, int]:
        """Get lines added/deleted statistics up to a specific date."""
        try:
            date_str = until_date.strftime('%Y-%m-%d')
            result = subprocess.run(
                ['git', 'log', '--numstat', '--pretty=format:', f'--until={date_str}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                added = 0
                deleted = 0
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                added += int(parts[0]) if parts[0].isdigit() else 0
                                deleted += int(parts[1]) if parts[1].isdigit() else 0
                            except ValueError:
                                pass
                return {'added': added, 'deleted': deleted}
        except Exception:
            pass
        return {'added': 0, 'deleted': 0}
    
    def _get_language_distribution(self, at_date: datetime) -> Dict[str, int]:
        """Get language distribution at a specific date."""
        try:
            date_str = at_date.strftime('%Y-%m-%d')
            # Get commit hash at this date
            result = subprocess.run(
                ['git', 'rev-list', '-n', '1', f'--until={date_str}', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                commit_hash = result.stdout.strip()
                # Get files at that commit
                result = subprocess.run(
                    ['git', 'ls-tree', '-r', '--name-only', commit_hash],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    files = result.stdout.strip().split('\n')
                    languages = {}
                    for file in files:
                        ext = Path(file).suffix.lower()
                        if ext:
                            lang = self._ext_to_language(ext)
                            languages[lang] = languages.get(lang, 0) + 1
                    return languages
        except Exception:
            pass
        return {}
    
    def _ext_to_language(self, ext: str) -> str:
        """Convert file extension to language name."""
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.cs': 'C#',
            '.sh': 'Shell',
            '.md': 'Markdown',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
        }
        return ext_map.get(ext, 'Other')
    
    def _calculate_growth_rates(self, trends: Dict) -> Dict:
        """Calculate growth rates for metrics."""
        growth_rates = {}
        
        metrics = ['commit_count', 'file_count', 'contributors', 'lines_added']
        
        for metric in metrics:
            values = trends[metric]
            if len(values) >= 2 and values[0] > 0:
                growth = ((values[-1] - values[0]) / values[0]) * 100
                growth_rates[metric] = round(growth, 2)
            else:
                growth_rates[metric] = 0.0
        
        return growth_rates
    
    def _generate_summary(self, trends: Dict) -> Dict:
        """Generate summary statistics."""
        summary = {
            'period': trends['period'],
            'data_points': len(trends['time_points']),
            'total_commits': trends['commit_count'][-1] if trends['commit_count'] else 0,
            'total_files': trends['file_count'][-1] if trends['file_count'] else 0,
            'total_contributors': trends['contributors'][-1] if trends['contributors'] else 0,
            'total_lines_added': trends['lines_added'][-1] if trends['lines_added'] else 0,
            'total_lines_deleted': trends['lines_deleted'][-1] if trends['lines_deleted'] else 0,
        }
        
        # Average commits per interval
        if len(trends['commit_count']) >= 2:
            commits = trends['commit_count']
            avg_commits_per_interval = (commits[-1] - commits[0]) / max(len(commits) - 1, 1)
            summary['avg_commits_per_interval'] = round(avg_commits_per_interval, 2)
        
        # Most active languages
        if trends['languages'] and trends['languages'][-1]:
            languages = trends['languages'][-1]
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            summary['top_languages'] = dict(sorted_langs[:5])
        
        return summary
    
    def generate_report(self) -> str:
        """Generate text report of trends."""
        if not self.trends:
            return "No trend data available. Run analyze() first."
        
        lines = []
        lines.append("=" * 70)
        lines.append("TREND ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        summary = self.trends['summary']
        lines.append(f"Analysis Period: {self.trends['period'].upper()}")
        lines.append(f"Data Points: {summary['data_points']}")
        lines.append(f"Repository: {self.repo_path}")
        lines.append("")
        
        # Summary metrics
        lines.append("-" * 70)
        lines.append("SUMMARY METRICS")
        lines.append("-" * 70)
        lines.append(f"Total Commits: {summary['total_commits']}")
        lines.append(f"Total Files: {summary['total_files']}")
        lines.append(f"Total Contributors: {summary['total_contributors']}")
        lines.append(f"Lines Added: {summary['total_lines_added']:,}")
        lines.append(f"Lines Deleted: {summary['total_lines_deleted']:,}")
        
        if 'avg_commits_per_interval' in summary:
            lines.append(f"Avg Commits per Interval: {summary['avg_commits_per_interval']:.1f}")
        lines.append("")
        
        # Growth rates
        lines.append("-" * 70)
        lines.append("GROWTH RATES")
        lines.append("-" * 70)
        growth = self.trends['growth_rates']
        lines.append(f"Commits: {growth['commit_count']:+.1f}%")
        lines.append(f"Files: {growth['file_count']:+.1f}%")
        lines.append(f"Contributors: {growth['contributors']:+.1f}%")
        lines.append(f"Lines Added: {growth['lines_added']:+.1f}%")
        lines.append("")
        
        # Top languages
        if 'top_languages' in summary:
            lines.append("-" * 70)
            lines.append("TOP LANGUAGES (Current)")
            lines.append("-" * 70)
            for lang, count in summary['top_languages'].items():
                lines.append(f"  {lang}: {count} files")
            lines.append("")
        
        # Trend data table
        lines.append("-" * 70)
        lines.append("TREND DATA")
        lines.append("-" * 70)
        lines.append(f"{'Time Point':<20} {'Commits':<10} {'Files':<10} {'Contributors':<15}")
        lines.append("-" * 70)
        
        for i, time_point in enumerate(self.trends['time_points']):
            date = datetime.fromisoformat(time_point).strftime('%Y-%m-%d')
            commits = self.trends['commit_count'][i]
            files = self.trends['file_count'][i]
            contributors = self.trends['contributors'][i]
            lines.append(f"{date:<20} {commits:<10} {files:<10} {contributors:<15}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def export_to_json(self) -> Dict:
        """Export trends to JSON format."""
        return self.trends
    
    def export_to_csv(self, output_dir: str) -> List[str]:
        """Export trends to CSV files."""
        import csv
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        # Main trends CSV
        trends_file = output_path / 'trends.csv'
        with open(trends_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Time Point', 'Commits', 'Files', 'Contributors', 
                           'Lines Added', 'Lines Deleted'])
            
            for i, time_point in enumerate(self.trends['time_points']):
                date = datetime.fromisoformat(time_point).strftime('%Y-%m-%d')
                writer.writerow([
                    date,
                    self.trends['commit_count'][i],
                    self.trends['file_count'][i],
                    self.trends['contributors'][i],
                    self.trends['lines_added'][i],
                    self.trends['lines_deleted'][i]
                ])
        
        created_files.append(str(trends_file))
        
        # Summary CSV
        summary_file = output_path / 'trends_summary.csv'
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            
            summary = self.trends['summary']
            for key, value in summary.items():
                if key != 'top_languages':
                    writer.writerow([key.replace('_', ' ').title(), value])
        
        created_files.append(str(summary_file))
        
        return created_files
