"""
Comparison history module for AccuDoc.

Provides functionality to track and analyze how a repository has evolved:
- Compare multiple scan results
- Track metrics over time
- Generate evolution reports
- Visualize trends
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path


class ComparisonHistory:
    """Track and analyze repository evolution over time."""
    
    def __init__(self, database=None):
        """
        Initialize comparison history.
        
        Args:
            database: ProjectDatabase instance (optional)
        """
        self.database = database
        self.logger = logging.getLogger('accudoc.comparison_history')
    
    def compare_scans(self, scan1: Dict[str, Any], scan2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two scan results.
        
        Args:
            scan1: Earlier scan data
            scan2: Later scan data
            
        Returns:
            Comparison results
        """
        # Extract results
        results1 = json.loads(scan1.get('results', '{}'))
        results2 = json.loads(scan2.get('results', '{}'))
        
        comparison = {
            'scan1_id': scan1.get('scan_id'),
            'scan2_id': scan2.get('scan_id'),
            'scan1_date': scan1.get('scanned_at'),
            'scan2_date': scan2.get('scanned_at'),
            'changes': {}
        }
        
        # Compare file counts
        files1 = scan1.get('files_scanned', 0)
        files2 = scan2.get('files_scanned', 0)
        comparison['changes']['files'] = {
            'before': files1,
            'after': files2,
            'delta': files2 - files1,
            'percent_change': ((files2 - files1) / files1 * 100) if files1 > 0 else 0
        }
        
        # Compare other metrics if available
        for metric in ['loc', 'complexity', 'documentation_score']:
            if metric in results1 and metric in results2:
                val1 = results1[metric]
                val2 = results2[metric]
                comparison['changes'][metric] = {
                    'before': val1,
                    'after': val2,
                    'delta': val2 - val1,
                    'percent_change': ((val2 - val1) / val1 * 100) if val1 > 0 else 0
                }
        
        return comparison
    
    def track_evolution(self, project_id: str, metric: str = 'files_scanned') -> Dict[str, Any]:
        """
        Track evolution of a metric over time.
        
        Args:
            project_id: Project ID
            metric: Metric to track
            
        Returns:
            Evolution data
        """
        if not self.database:
            return {'error': 'Database not available'}
        
        scans = self.database.get_scans(project_id, limit=1000)
        
        evolution = {
            'project_id': project_id,
            'metric': metric,
            'data_points': [],
            'trend': None
        }
        
        for scan in reversed(scans):  # Oldest first
            value = scan.get(metric, 0)
            evolution['data_points'].append({
                'date': scan.get('scanned_at'),
                'value': value
            })
        
        # Calculate trend
        if len(evolution['data_points']) >= 2:
            first = evolution['data_points'][0]['value']
            last = evolution['data_points'][-1]['value']
            
            if first > 0:
                change_percent = ((last - first) / first) * 100
                if change_percent > 5:
                    evolution['trend'] = 'increasing'
                elif change_percent < -5:
                    evolution['trend'] = 'decreasing'
                else:
                    evolution['trend'] = 'stable'
            else:
                evolution['trend'] = 'new'
        
        return evolution
    
    def generate_evolution_report(self, project_id: str) -> str:
        """
        Generate evolution report for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Markdown formatted report
        """
        if not self.database:
            return "Database not available."
        
        project = self.database.get_project(project_id)
        if not project:
            return "Project not found."
        
        scans = self.database.get_scans(project_id, limit=100)
        
        md = []
        md.append(f"# Evolution Report: {project['name']}\n")
        md.append(f"**Repository**: {project['repo_path']}")
        md.append(f"**Total Scans**: {len(scans)}")
        md.append(f"**First Scan**: {scans[-1]['scanned_at'] if scans else 'N/A'}")
        md.append(f"**Last Scan**: {scans[0]['scanned_at'] if scans else 'N/A'}\n")
        
        if len(scans) >= 2:
            # Compare first and last scan
            comparison = self.compare_scans(scans[-1], scans[0])
            
            md.append("## Overall Changes\n")
            
            for metric, data in comparison['changes'].items():
                md.append(f"### {metric.replace('_', ' ').title()}")
                md.append(f"- **Before**: {data['before']}")
                md.append(f"- **After**: {data['after']}")
                md.append(f"- **Change**: {data['delta']:+} ({data['percent_change']:+.1f}%)\n")
            
            # Track evolution of key metrics
            md.append("## Metric Trends\n")
            
            for metric in ['files_scanned', 'duration_seconds']:
                evolution = self.track_evolution(project_id, metric)
                if evolution.get('trend'):
                    md.append(f"**{metric.replace('_', ' ').title()}**: {evolution['trend']}")
            
            md.append("")
        
        # Recent scans
        md.append("## Recent Scans\n")
        md.append("| Date | Files | Duration | Status |")
        md.append("|------|-------|----------|--------|")
        
        for scan in scans[:10]:
            date = scan['scanned_at'][:10]  # Just the date
            files = scan.get('files_scanned', 0)
            duration = scan.get('duration_seconds', 0)
            status = scan.get('status', 'unknown')
            md.append(f"| {date} | {files} | {duration:.1f}s | {status} |")
        
        md.append("")
        
        return '\n'.join(md)
    
    def find_regressions(self, project_id: str, threshold: float = 10.0) -> List[Dict[str, Any]]:
        """
        Find potential regressions in scan history.
        
        Args:
            project_id: Project ID
            threshold: Percentage threshold for regression detection
            
        Returns:
            List of detected regressions
        """
        if not self.database:
            return []
        
        scans = self.database.get_scans(project_id, limit=100)
        regressions = []
        
        for i in range(len(scans) - 1):
            current = scans[i]
            previous = scans[i + 1]
            
            comparison = self.compare_scans(previous, current)
            
            # Check for negative changes exceeding threshold
            for metric, data in comparison['changes'].items():
                if data['percent_change'] < -threshold:
                    regressions.append({
                        'metric': metric,
                        'scan_id': current['scan_id'],
                        'date': current['scanned_at'],
                        'change_percent': data['percent_change'],
                        'before': data['before'],
                        'after': data['after']
                    })
        
        return regressions
    
    def generate_timeline_data(self, project_id: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Generate timeline data for visualization.
        
        Args:
            project_id: Project ID
            metrics: List of metrics to include
            
        Returns:
            Timeline data suitable for charting
        """
        if not self.database:
            return {}
        
        scans = self.database.get_scans(project_id, limit=1000)
        
        timeline = {
            'project_id': project_id,
            'dates': [],
            'metrics': {metric: [] for metric in metrics}
        }
        
        for scan in reversed(scans):  # Oldest first
            timeline['dates'].append(scan['scanned_at'])
            
            for metric in metrics:
                value = scan.get(metric, 0)
                timeline['metrics'][metric].append(value)
        
        return timeline
    
    def export_history(self, project_id: str, output_file: Path) -> None:
        """
        Export complete comparison history to file.
        
        Args:
            project_id: Project ID
            output_file: Output file path
        """
        if not self.database:
            return
        
        project = self.database.get_project(project_id)
        scans = self.database.get_scans(project_id, limit=1000)
        comparisons = self.database.get_comparisons(project_id)
        
        # Generate evolution for key metrics
        evolutions = {}
        for metric in ['files_scanned', 'duration_seconds']:
            evolutions[metric] = self.track_evolution(project_id, metric)
        
        # Find regressions
        regressions = self.find_regressions(project_id)
        
        history = {
            'project': project,
            'total_scans': len(scans),
            'scans': scans[:50],  # Limit to recent 50
            'comparisons': comparisons[:20],  # Limit to recent 20
            'evolutions': evolutions,
            'regressions': regressions,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        
        self.logger.info(f"Exported history to {output_file}")
    
    def get_statistics_summary(self, project_id: str) -> Dict[str, Any]:
        """
        Get statistical summary of scan history.
        
        Args:
            project_id: Project ID
            
        Returns:
            Statistics summary
        """
        if not self.database:
            return {}
        
        scans = self.database.get_scans(project_id, limit=1000)
        
        if not scans:
            return {'error': 'No scans found'}
        
        # Calculate statistics
        file_counts = [s.get('files_scanned', 0) for s in scans]
        durations = [s.get('duration_seconds', 0) for s in scans]
        
        summary = {
            'total_scans': len(scans),
            'files_scanned': {
                'min': min(file_counts),
                'max': max(file_counts),
                'avg': sum(file_counts) / len(file_counts),
                'latest': file_counts[0]
            },
            'scan_duration': {
                'min': min(durations),
                'max': max(durations),
                'avg': sum(durations) / len(durations),
                'latest': durations[0]
            },
            'date_range': {
                'first': scans[-1]['scanned_at'],
                'last': scans[0]['scanned_at']
            }
        }
        
        return summary
