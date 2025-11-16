"""
Analytics and insights engine for AccuDoc.

Tracks documentation usage, team productivity, aging analysis, and ROI metrics.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class PageView:
    """Documentation page view event."""
    page_path: str
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    duration_seconds: Optional[int] = None
    referrer: Optional[str] = None


@dataclass
class SearchQuery:
    """Documentation search query."""
    query: str
    timestamp: datetime
    results_count: int
    user_id: Optional[str] = None
    clicked_result: Optional[str] = None


@dataclass
class DocumentEdit:
    """Documentation edit event."""
    file_path: str
    timestamp: datetime
    user_id: str
    lines_added: int
    lines_removed: int
    commit_hash: Optional[str] = None


@dataclass
class AnalyticsSummary:
    """Summary of analytics data."""
    total_views: int
    unique_pages: int
    avg_session_duration: float
    most_viewed_pages: List[Tuple[str, int]]
    search_queries_count: int
    top_searches: List[Tuple[str, int]]
    total_edits: int
    active_contributors: int
    doc_age_days: float
    stale_docs: List[str]


class AnalyticsEngine:
    """Analytics and insights engine for documentation."""
    
    def __init__(self, db_path: str = 'accudoc_analytics.db'):
        """
        Initialize analytics engine.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Page views table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_path TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                user_id TEXT,
                session_id TEXT,
                duration_seconds INTEGER,
                referrer TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Search queries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                results_count INTEGER NOT NULL,
                user_id TEXT,
                clicked_result TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Document edits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                user_id TEXT NOT NULL,
                lines_added INTEGER NOT NULL,
                lines_removed INTEGER NOT NULL,
                commit_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Document metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_metadata (
                file_path TEXT PRIMARY KEY,
                created_at DATETIME,
                last_modified DATETIME,
                last_viewed DATETIME,
                view_count INTEGER DEFAULT 0,
                edit_count INTEGER DEFAULT 0,
                content_hash TEXT
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_views_timestamp ON page_views(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_views_page ON page_views(page_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_timestamp ON search_queries(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edits_timestamp ON document_edits(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edits_user ON document_edits(user_id)')
        
        conn.commit()
        conn.close()
    
    def track_page_view(self, view: PageView) -> int:
        """
        Track a page view event.
        
        Args:
            view: PageView event to track
        
        Returns:
            int: View ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO page_views (page_path, timestamp, user_id, session_id, duration_seconds, referrer)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            view.page_path,
            view.timestamp.isoformat(),
            view.user_id,
            view.session_id,
            view.duration_seconds,
            view.referrer
        ))
        
        view_id = cursor.lastrowid
        
        # Update document metadata
        cursor.execute('''
            INSERT INTO document_metadata (file_path, last_viewed, view_count)
            VALUES (?, ?, 1)
            ON CONFLICT(file_path) DO UPDATE SET
                last_viewed = excluded.last_viewed,
                view_count = view_count + 1
        ''', (view.page_path, view.timestamp.isoformat()))
        
        conn.commit()
        conn.close()
        
        return view_id
    
    def track_search(self, search: SearchQuery) -> int:
        """Track a search query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_queries (query, timestamp, results_count, user_id, clicked_result)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            search.query,
            search.timestamp.isoformat(),
            search.results_count,
            search.user_id,
            search.clicked_result
        ))
        
        search_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return search_id
    
    def track_edit(self, edit: DocumentEdit) -> int:
        """Track a document edit."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO document_edits (file_path, timestamp, user_id, lines_added, lines_removed, commit_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            edit.file_path,
            edit.timestamp.isoformat(),
            edit.user_id,
            edit.lines_added,
            edit.lines_removed,
            edit.commit_hash
        ))
        
        edit_id = cursor.lastrowid
        
        # Update document metadata
        cursor.execute('''
            INSERT INTO document_metadata (file_path, last_modified, edit_count)
            VALUES (?, ?, 1)
            ON CONFLICT(file_path) DO UPDATE SET
                last_modified = excluded.last_modified,
                edit_count = edit_count + 1
        ''', (edit.file_path, edit.timestamp.isoformat()))
        
        conn.commit()
        conn.close()
        
        return edit_id
    
    def get_most_viewed_pages(self, limit: int = 10, days: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Get most viewed documentation pages.
        
        Args:
            limit: Number of results
            days: Limit to last N days (None for all time)
        
        Returns:
            List of (page_path, view_count) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if days:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute('''
                SELECT page_path, COUNT(*) as views
                FROM page_views
                WHERE timestamp > ?
                GROUP BY page_path
                ORDER BY views DESC
                LIMIT ?
            ''', (since, limit))
        else:
            cursor.execute('''
                SELECT page_path, COUNT(*) as views
                FROM page_views
                GROUP BY page_path
                ORDER BY views DESC
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_search_insights(self, limit: int = 10, days: Optional[int] = None) -> Dict:
        """Get search query insights."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        time_filter = ''
        params = [limit]
        if days:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            time_filter = 'WHERE timestamp > ?'
            params.insert(0, since)
        
        # Top searches
        cursor.execute(f'''
            SELECT query, COUNT(*) as count
            FROM search_queries
            {time_filter}
            GROUP BY query
            ORDER BY count DESC
            LIMIT ?
        ''', params)
        top_searches = cursor.fetchall()
        
        # Searches with no results
        cursor.execute(f'''
            SELECT query, COUNT(*) as count
            FROM search_queries
            {time_filter}
            AND results_count = 0
            GROUP BY query
            ORDER BY count DESC
            LIMIT ?
        ''', params)
        zero_results = cursor.fetchall()
        
        # Click-through rate
        cursor.execute(f'''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN clicked_result IS NOT NULL THEN 1 ELSE 0 END) as clicked
            FROM search_queries
            {time_filter.replace('?', str(params[0])) if days else ''}
        ''')
        total, clicked = cursor.fetchone()
        ctr = (clicked / total * 100) if total > 0 else 0
        
        conn.close()
        
        return {
            'top_searches': top_searches,
            'zero_result_searches': zero_results,
            'click_through_rate': round(ctr, 2),
            'total_searches': total
        }
    
    def get_team_productivity(self, days: Optional[int] = 30) -> Dict:
        """
        Calculate team productivity metrics.
        
        Args:
            days: Number of days to analyze (default: 30)
        
        Returns:
            Dictionary with productivity metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        time_filter = ''
        params = []
        if days:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            time_filter = 'WHERE timestamp > ?'
            params = [since]
        
        # Active contributors
        cursor.execute(f'''
            SELECT COUNT(DISTINCT user_id) 
            FROM document_edits
            {time_filter}
        ''', params)
        active_contributors = cursor.fetchone()[0]
        
        # Top contributors
        cursor.execute(f'''
            SELECT user_id, 
                   COUNT(*) as edit_count,
                   SUM(lines_added) as lines_added,
                   SUM(lines_removed) as lines_removed
            FROM document_edits
            {time_filter}
            GROUP BY user_id
            ORDER BY edit_count DESC
            LIMIT 10
        ''', params)
        top_contributors = [
            {
                'user_id': row[0],
                'edits': row[1],
                'lines_added': row[2],
                'lines_removed': row[3],
                'net_lines': row[2] - row[3]
            }
            for row in cursor.fetchall()
        ]
        
        # Edits over time (daily)
        cursor.execute(f'''
            SELECT DATE(timestamp) as date, COUNT(*) as edits
            FROM document_edits
            {time_filter}
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', params)
        daily_edits = [(row[0], row[1]) for row in cursor.fetchall()]
        
        # Average review velocity (time between edits)
        cursor.execute(f'''
            SELECT file_path, timestamp
            FROM document_edits
            {time_filter}
            ORDER BY file_path, timestamp
        ''', params)
        
        edits_by_file = {}
        for file_path, timestamp in cursor.fetchall():
            if file_path not in edits_by_file:
                edits_by_file[file_path] = []
            edits_by_file[file_path].append(datetime.fromisoformat(timestamp))
        
        review_times = []
        for file_path, timestamps in edits_by_file.items():
            if len(timestamps) > 1:
                for i in range(1, len(timestamps)):
                    delta = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
                    review_times.append(delta)
        
        avg_review_hours = sum(review_times) / len(review_times) if review_times else 0
        
        conn.close()
        
        return {
            'active_contributors': active_contributors,
            'top_contributors': top_contributors,
            'daily_edit_activity': daily_edits,
            'avg_review_velocity_hours': round(avg_review_hours, 2)
        }
    
    def get_aging_analysis(self, stale_days: int = 90) -> Dict:
        """
        Analyze documentation aging and staleness.
        
        Args:
            stale_days: Days after which a doc is considered stale
        
        Returns:
            Dictionary with aging metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stale_cutoff = (datetime.now() - timedelta(days=stale_days)).isoformat()
        
        # Stale documents (not modified recently)
        cursor.execute('''
            SELECT file_path, last_modified, view_count
            FROM document_metadata
            WHERE last_modified < ? OR last_modified IS NULL
            ORDER BY last_modified ASC
        ''', (stale_cutoff,))
        stale_docs = [
            {
                'path': row[0],
                'last_modified': row[1],
                'views': row[2],
                'days_old': (datetime.now() - datetime.fromisoformat(row[1])).days if row[1] else None
            }
            for row in cursor.fetchall()
        ]
        
        # Average document age
        cursor.execute('''
            SELECT AVG(JULIANDAY('now') - JULIANDAY(last_modified))
            FROM document_metadata
            WHERE last_modified IS NOT NULL
        ''')
        avg_age = cursor.fetchone()[0] or 0
        
        # Documents never viewed
        cursor.execute('''
            SELECT file_path
            FROM document_metadata
            WHERE view_count = 0 OR last_viewed IS NULL
        ''')
        never_viewed = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'stale_documents': stale_docs,
            'stale_count': len(stale_docs),
            'average_age_days': round(avg_age, 1),
            'never_viewed': never_viewed,
            'never_viewed_count': len(never_viewed)
        }
    
    def get_summary(self, days: Optional[int] = 30) -> AnalyticsSummary:
        """Get comprehensive analytics summary."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        time_filter = ''
        params = []
        if days:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            time_filter = 'WHERE timestamp > ?'
            params = [since]
        
        # Total views
        cursor.execute(f'SELECT COUNT(*) FROM page_views {time_filter}', params)
        total_views = cursor.fetchone()[0]
        
        # Unique pages
        cursor.execute(f'SELECT COUNT(DISTINCT page_path) FROM page_views {time_filter}', params)
        unique_pages = cursor.fetchone()[0]
        
        # Average session duration
        cursor.execute(f'''
            SELECT AVG(duration_seconds)
            FROM page_views
            {time_filter}
            AND duration_seconds IS NOT NULL
        ''', params)
        avg_duration = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Get other metrics
        most_viewed = self.get_most_viewed_pages(10, days)
        search_insights = self.get_search_insights(10, days)
        aging = self.get_aging_analysis()
        productivity = self.get_team_productivity(days)
        
        return AnalyticsSummary(
            total_views=total_views,
            unique_pages=unique_pages,
            avg_session_duration=round(avg_duration, 1),
            most_viewed_pages=most_viewed,
            search_queries_count=search_insights['total_searches'],
            top_searches=search_insights['top_searches'],
            total_edits=sum(c['edits'] for c in productivity['top_contributors']),
            active_contributors=productivity['active_contributors'],
            doc_age_days=aging['average_age_days'],
            stale_docs=[d['path'] for d in aging['stale_documents'][:5]]
        )
    
    def export_analytics(self, output_path: str, format: str = 'json', days: Optional[int] = 30):
        """
        Export analytics data to file.
        
        Args:
            output_path: Output file path
            format: Export format (json, csv)
            days: Number of days to include
        """
        summary = self.get_summary(days)
        productivity = self.get_team_productivity(days)
        aging = self.get_aging_analysis()
        search_insights = self.get_search_insights(10, days)
        
        data = {
            'summary': asdict(summary),
            'productivity': productivity,
            'aging': aging,
            'search': search_insights,
            'generated_at': datetime.now().isoformat(),
            'period_days': days
        }
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'csv':
            import csv
            # Export most viewed pages to CSV
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Page', 'Views'])
                writer.writerows(summary.most_viewed_pages)


def calculate_roi_metrics(analytics: AnalyticsEngine, 
                          team_size: int,
                          avg_hourly_rate: float,
                          days: int = 30) -> Dict:
    """
    Calculate ROI metrics for documentation efforts.
    
    Args:
        analytics: AnalyticsEngine instance
        team_size: Number of team members
        avg_hourly_rate: Average hourly rate for team
        days: Analysis period
    
    Returns:
        Dictionary with ROI calculations
    """
    productivity = analytics.get_team_productivity(days)
    summary = analytics.get_summary(days)
    
    # Estimate time saved by documentation
    # Assume each page view saves 5 minutes of asking questions
    time_saved_minutes = summary.total_views * 5
    time_saved_hours = time_saved_minutes / 60
    value_saved = time_saved_hours * avg_hourly_rate
    
    # Estimate cost of creating/maintaining docs
    total_hours_spent = sum(c['edits'] for c in productivity['top_contributors']) * 0.5  # assume 30 min per edit
    cost_of_docs = total_hours_spent * avg_hourly_rate
    
    # ROI calculation
    roi_percentage = ((value_saved - cost_of_docs) / cost_of_docs * 100) if cost_of_docs > 0 else 0
    
    return {
        'time_saved_hours': round(time_saved_hours, 1),
        'value_saved_dollars': round(value_saved, 2),
        'cost_of_documentation': round(cost_of_docs, 2),
        'roi_percentage': round(roi_percentage, 1),
        'views_per_team_member': round(summary.total_views / team_size, 1) if team_size > 0 else 0,
        'documentation_usage_rate': round((summary.unique_pages / max(summary.stale_docs.__len__() + summary.unique_pages, 1)) * 100, 1)
    }
