"""
Audit trail module for AccuDoc.

Logs all operations for security review and compliance purposes.
"""

import json
import logging
import datetime
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class AuditEntry:
    """Represents a single audit log entry."""
    timestamp: str
    operation: str
    user: str
    status: str  # success, failure, warning
    details: Dict[str, Any]
    duration_ms: Optional[float] = None
    error: Optional[str] = None


class AuditLogger:
    """Logs operations for audit trail."""
    
    def __init__(self, log_file: Optional[Path] = None, enabled: bool = True):
        """
        Initialize audit logger.
        
        Args:
            log_file: Path to audit log file (default: ~/.accudoc/audit.log)
            enabled: Whether audit logging is enabled
        """
        self.enabled = enabled
        
        if log_file is None:
            # Default to user's home directory
            home = Path.home()
            accudoc_dir = home / '.accudoc'
            accudoc_dir.mkdir(exist_ok=True)
            self.log_file = accudoc_dir / 'audit.log'
        else:
            self.log_file = Path(log_file)
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('accudoc.audit')
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup file logger for audit trail."""
        if not self.enabled:
            return
        
        # Create file handler
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_operation(self, operation: str, status: str = 'success',
                     details: Optional[Dict] = None,
                     duration_ms: Optional[float] = None,
                     error: Optional[str] = None):
        """
        Log an operation.
        
        Args:
            operation: Operation name (e.g., 'scan_repository', 'generate_docs')
            status: Operation status ('success', 'failure', 'warning')
            details: Additional details about the operation
            duration_ms: Operation duration in milliseconds
            error: Error message if operation failed
        """
        if not self.enabled:
            return
        
        # Get current user
        user = os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
        
        # Create audit entry
        entry = AuditEntry(
            timestamp=datetime.datetime.now().isoformat(),
            operation=operation,
            user=user,
            status=status,
            details=details or {},
            duration_ms=duration_ms,
            error=error
        )
        
        # Log to file
        log_message = self._format_entry(entry)
        
        if status == 'success':
            self.logger.info(log_message)
        elif status == 'failure':
            self.logger.error(log_message)
        else:  # warning
            self.logger.warning(log_message)
    
    def _format_entry(self, entry: AuditEntry) -> str:
        """Format audit entry as string."""
        parts = [
            f"Operation: {entry.operation}",
            f"User: {entry.user}",
            f"Status: {entry.status}",
        ]
        
        if entry.duration_ms:
            parts.append(f"Duration: {entry.duration_ms:.2f}ms")
        
        if entry.details:
            # Sanitize details (don't log sensitive info)
            safe_details = self._sanitize_details(entry.details)
            parts.append(f"Details: {json.dumps(safe_details)}")
        
        if entry.error:
            parts.append(f"Error: {entry.error}")
        
        return " | ".join(parts)
    
    def _sanitize_details(self, details: Dict) -> Dict:
        """Remove sensitive information from details."""
        safe_details = {}
        
        # Keys that might contain sensitive data
        sensitive_keys = [
            'password', 'token', 'api_key', 'secret', 'credential',
            'auth', 'private_key', 'app_password'
        ]
        
        for key, value in details.items():
            # Check if key contains sensitive terms
            if any(term in key.lower() for term in sensitive_keys):
                safe_details[key] = '[REDACTED]'
            elif isinstance(value, dict):
                safe_details[key] = self._sanitize_details(value)
            elif isinstance(value, str) and len(value) > 200:
                # Truncate very long strings
                safe_details[key] = value[:200] + '...'
            else:
                safe_details[key] = value
        
        return safe_details
    
    def get_recent_entries(self, count: int = 50) -> List[str]:
        """
        Get recent audit log entries.
        
        Args:
            count: Number of recent entries to return
            
        Returns:
            List of log entry strings
        """
        if not self.log_file.exists():
            return []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Return last 'count' lines
            return lines[-count:]
        except Exception as e:
            self.logger.error(f"Error reading audit log: {str(e)}")
            return []
    
    def export_to_json(self, output_file: Path, count: Optional[int] = None):
        """
        Export audit log to JSON format.
        
        Args:
            output_file: Output JSON file path
            count: Number of recent entries to export (None for all)
        """
        entries = self.get_recent_entries(count if count else 1000000)
        
        # Parse entries into structured format
        parsed_entries = []
        for entry_line in entries:
            try:
                # Extract timestamp and message
                parts = entry_line.split(' - ', 2)
                if len(parts) >= 3:
                    timestamp = parts[0]
                    level = parts[1]
                    message = parts[2].strip()
                    
                    parsed_entries.append({
                        'timestamp': timestamp,
                        'level': level,
                        'message': message
                    })
            except Exception:
                continue
        
        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_entries, f, indent=2)
    
    def export_to_csv(self, output_file: Path, count: Optional[int] = None):
        """
        Export audit log to CSV format.
        
        Args:
            output_file: Output CSV file path
            count: Number of recent entries to export (None for all)
        """
        import csv
        
        entries = self.get_recent_entries(count if count else 1000000)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Level', 'Message'])
            
            for entry_line in entries:
                try:
                    parts = entry_line.split(' - ', 2)
                    if len(parts) >= 3:
                        writer.writerow([parts[0], parts[1], parts[2].strip()])
                except Exception:
                    continue
    
    def clear_log(self):
        """Clear the audit log file."""
        if self.log_file.exists():
            self.log_file.unlink()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit log statistics.
        
        Returns:
            Dictionary with statistics
        """
        entries = self.get_recent_entries(count=1000000)
        
        stats = {
            'total_entries': len(entries),
            'by_level': {'INFO': 0, 'WARNING': 0, 'ERROR': 0},
            'by_operation': {},
            'log_file': str(self.log_file),
            'log_size_bytes': self.log_file.stat().st_size if self.log_file.exists() else 0
        }
        
        for entry in entries:
            # Count by level
            if 'INFO' in entry:
                stats['by_level']['INFO'] += 1
            elif 'WARNING' in entry:
                stats['by_level']['WARNING'] += 1
            elif 'ERROR' in entry:
                stats['by_level']['ERROR'] += 1
            
            # Try to extract operation name
            if 'Operation:' in entry:
                try:
                    op_part = entry.split('Operation:')[1].split('|')[0].strip()
                    if op_part:
                        stats['by_operation'][op_part] = stats['by_operation'].get(op_part, 0) + 1
                except Exception:
                    pass
        
        return stats


# Global audit logger instance
_global_logger: Optional[AuditLogger] = None


def get_audit_logger(log_file: Optional[Path] = None, 
                     enabled: bool = True) -> AuditLogger:
    """
    Get global audit logger instance.
    
    Args:
        log_file: Path to audit log file
        enabled: Whether audit logging is enabled
        
    Returns:
        AuditLogger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = AuditLogger(log_file=log_file, enabled=enabled)
    
    return _global_logger


def log_operation(operation: str, status: str = 'success',
                 details: Optional[Dict] = None,
                 duration_ms: Optional[float] = None,
                 error: Optional[str] = None):
    """
    Convenience function to log an operation using global logger.
    
    Args:
        operation: Operation name
        status: Operation status
        details: Operation details
        duration_ms: Duration in milliseconds
        error: Error message
    """
    logger = get_audit_logger()
    logger.log_operation(operation, status, details, duration_ms, error)
