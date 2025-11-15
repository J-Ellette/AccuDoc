"""
Scheduled scan system for AccuDoc.

Allows automatic scanning of repositories on a schedule.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
import time


class ScheduleType(Enum):
    """Types of schedules."""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class ScheduledScan:
    """Represents a scheduled scan configuration."""
    
    id: str
    repo_path: str
    schedule_type: str
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    output_path: Optional[str] = None
    options: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScheduledScan':
        """Create from dictionary."""
        return cls(**data)


class ScanScheduler:
    """
    Scheduler for automatic repository scans.
    
    Manages scheduled scans and executes them at specified intervals.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize scheduler.
        
        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = Path(config_dir or Path.home() / ".accudoc")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "schedules.json"
        self.schedules: Dict[str, ScheduledScan] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.running = False
        self.thread = None
        
        self._load_schedules()
    
    def _load_schedules(self):
        """Load schedules from config file."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for scan_id, scan_data in data.get('schedules', {}).items():
                    self.schedules[scan_id] = ScheduledScan.from_dict(scan_data)
    
    def _save_schedules(self):
        """Save schedules to config file."""
        data = {
            'schedules': {k: v.to_dict() for k, v in self.schedules.items()},
            'updated': datetime.now().isoformat()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _generate_id(self, repo_path: str) -> str:
        """Generate unique ID for a schedule."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"scan_{Path(repo_path).name}_{timestamp}"
    
    def _calculate_next_run(
        self,
        schedule_type: ScheduleType,
        last_run: Optional[datetime] = None,
        custom_interval: Optional[int] = None
    ) -> datetime:
        """
        Calculate next run time.
        
        Args:
            schedule_type: Type of schedule
            last_run: Last run time
            custom_interval: Custom interval in minutes
            
        Returns:
            Next run datetime
        """
        base_time = last_run or datetime.now()
        
        if schedule_type == ScheduleType.ONCE:
            return base_time
        elif schedule_type == ScheduleType.HOURLY:
            return base_time + timedelta(hours=1)
        elif schedule_type == ScheduleType.DAILY:
            return base_time + timedelta(days=1)
        elif schedule_type == ScheduleType.WEEKLY:
            return base_time + timedelta(weeks=1)
        elif schedule_type == ScheduleType.MONTHLY:
            return base_time + timedelta(days=30)
        elif schedule_type == ScheduleType.CUSTOM and custom_interval:
            return base_time + timedelta(minutes=custom_interval)
        else:
            return base_time + timedelta(days=1)  # Default to daily
    
    def add_schedule(
        self,
        repo_path: str,
        schedule_type: ScheduleType,
        output_path: Optional[str] = None,
        custom_interval: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> str:
        """
        Add a new scheduled scan.
        
        Args:
            repo_path: Repository path or URL
            schedule_type: Schedule type
            output_path: Optional output path for documentation
            custom_interval: Custom interval in minutes (for CUSTOM type)
            options: Additional scan options
            
        Returns:
            Schedule ID
        """
        scan_id = self._generate_id(repo_path)
        next_run = self._calculate_next_run(schedule_type, custom_interval=custom_interval)
        
        schedule = ScheduledScan(
            id=scan_id,
            repo_path=repo_path,
            schedule_type=schedule_type.value,
            next_run=next_run.isoformat(),
            output_path=output_path,
            options=options or {}
        )
        
        if custom_interval:
            schedule.options['custom_interval'] = custom_interval
        
        self.schedules[scan_id] = schedule
        self._save_schedules()
        
        return scan_id
    
    def remove_schedule(self, scan_id: str) -> bool:
        """
        Remove a scheduled scan.
        
        Args:
            scan_id: Schedule ID
            
        Returns:
            True if removed
        """
        if scan_id in self.schedules:
            del self.schedules[scan_id]
            self._save_schedules()
            return True
        return False
    
    def enable_schedule(self, scan_id: str):
        """Enable a schedule."""
        if scan_id in self.schedules:
            self.schedules[scan_id].enabled = True
            self._save_schedules()
    
    def disable_schedule(self, scan_id: str):
        """Disable a schedule."""
        if scan_id in self.schedules:
            self.schedules[scan_id].enabled = False
            self._save_schedules()
    
    def list_schedules(self, enabled_only: bool = False) -> List[ScheduledScan]:
        """
        List all schedules.
        
        Args:
            enabled_only: Only return enabled schedules
            
        Returns:
            List of ScheduledScans
        """
        schedules = list(self.schedules.values())
        if enabled_only:
            schedules = [s for s in schedules if s.enabled]
        return schedules
    
    def register_callback(self, scan_id: str, callback: Callable):
        """
        Register a callback for a specific scan.
        
        Args:
            scan_id: Schedule ID
            callback: Function to call with (repo_path, options) when scan runs
        """
        self.callbacks[scan_id] = callback
    
    def _run_scan(self, schedule: ScheduledScan):
        """
        Execute a scheduled scan.
        
        Args:
            schedule: ScheduledScan to execute
        """
        try:
            logging.info(f"Running scheduled scan: {schedule.id}")
            
            # Call registered callback if available
            if schedule.id in self.callbacks:
                callback = self.callbacks[schedule.id]
                callback(schedule.repo_path, schedule.options)
            else:
                # Default: use scanner and generator
                from accudoc.scanner import RepositoryScanner
                from accudoc.generator import DocumentGenerator
                
                scanner = RepositoryScanner(schedule.repo_path)
                repo_info = scanner.scan()
                
                generator = DocumentGenerator(repo_info)
                output_path = schedule.output_path or f"{schedule.repo_path}_docs.md"
                generator.generate_and_export(output_path)
            
            # Update schedule
            schedule.last_run = datetime.now().isoformat()
            
            # Calculate next run
            schedule_type = ScheduleType(schedule.schedule_type)
            custom_interval = schedule.options.get('custom_interval')
            next_run = self._calculate_next_run(
                schedule_type,
                datetime.now(),
                custom_interval
            )
            schedule.next_run = next_run.isoformat()
            
            self._save_schedules()
            
            logging.info(f"Scan completed. Next run: {schedule.next_run}")
            
        except Exception as e:
            logging.error(f"Error running scheduled scan {schedule.id}: {e}")
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        logging.info("Scheduler started")
        
        while self.running:
            try:
                now = datetime.now()
                
                # Check each schedule
                for schedule in self.schedules.values():
                    if not schedule.enabled:
                        continue
                    
                    if schedule.next_run:
                        next_run = datetime.fromisoformat(schedule.next_run)
                        if now >= next_run:
                            self._run_scan(schedule)
                
                # Sleep for 60 seconds before next check
                time.sleep(60)
                
            except Exception as e:
                logging.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
        
        logging.info("Scheduler stopped")
    
    def start(self):
        """Start the scheduler in a background thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.thread.start()
            logging.info("Scheduler thread started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            logging.info("Scheduler stopped")
    
    def get_status(self) -> Dict:
        """
        Get scheduler status.
        
        Returns:
            Status dictionary
        """
        return {
            'running': self.running,
            'total_schedules': len(self.schedules),
            'enabled_schedules': len([s for s in self.schedules.values() if s.enabled]),
            'schedules': [s.to_dict() for s in self.schedules.values()]
        }


def create_scheduler(config_dir: Optional[str] = None) -> ScanScheduler:
    """
    Create and return a ScanScheduler instance.
    
    Args:
        config_dir: Optional config directory
        
    Returns:
        ScanScheduler instance
    """
    return ScanScheduler(config_dir)
