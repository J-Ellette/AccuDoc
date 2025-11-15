"""
Memory optimization module for AccuDoc.

Provides efficient memory management for handling very large repositories:
- Streaming file processing
- Chunked reading for large files
- Memory-efficient data structures
- Garbage collection optimization
- Resource monitoring
"""

import gc
import logging
import sys
from typing import Iterator, Dict, Any, Optional, List
from pathlib import Path
import os

# Try to import psutil, but provide fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MemoryOptimizer:
    """Optimize memory usage for large repository scanning."""
    
    def __init__(self, max_memory_mb: int = 1024):
        """
        Initialize memory optimizer.
        
        Args:
            max_memory_mb: Maximum memory usage in MB before triggering optimization
        """
        self.max_memory_mb = max_memory_mb
        self.logger = logging.getLogger('accudoc.memory_optimizer')
        
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process(os.getpid())
        else:
            self.process = None
            self.logger.warning("psutil not available, memory monitoring will be limited")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage statistics.
        
        Returns:
            Dictionary with memory statistics in MB
        """
        if not PSUTIL_AVAILABLE or not self.process:
            # Fallback using sys.getsizeof for basic estimation
            return {
                'rss_mb': 0,
                'vms_mb': 0,
                'percent': 0.0,
                'note': 'psutil not available, memory stats unavailable'
            }
        
        memory_info = self.process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': self.process.memory_percent()
        }
    
    def should_optimize(self) -> bool:
        """
        Check if memory optimization should be triggered.
        
        Returns:
            True if memory usage exceeds threshold
        """
        usage = self.get_memory_usage()
        return usage['rss_mb'] > self.max_memory_mb
    
    def optimize(self) -> Dict[str, Any]:
        """
        Perform memory optimization.
        
        Returns:
            Dictionary with optimization results
        """
        before = self.get_memory_usage()
        
        # Force garbage collection
        collected = gc.collect()
        
        after = self.get_memory_usage()
        freed_mb = before['rss_mb'] - after['rss_mb']
        
        self.logger.info(f"Memory optimization: freed {freed_mb:.2f} MB, collected {collected} objects")
        
        return {
            'before_mb': before['rss_mb'],
            'after_mb': after['rss_mb'],
            'freed_mb': freed_mb,
            'objects_collected': collected
        }
    
    def stream_file_lines(self, filepath: Path, chunk_size: int = 8192) -> Iterator[str]:
        """
        Stream file lines efficiently without loading entire file into memory.
        
        Args:
            filepath: Path to file
            chunk_size: Size of chunks to read
            
        Yields:
            Individual lines from the file
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                buffer = ""
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        if buffer:
                            yield buffer
                        break
                    
                    buffer += chunk
                    lines = buffer.split('\n')
                    
                    # Yield all complete lines
                    for line in lines[:-1]:
                        yield line
                    
                    # Keep the incomplete line in buffer
                    buffer = lines[-1]
        except Exception as e:
            self.logger.error(f"Error streaming file {filepath}: {e}")
    
    def process_large_file(self, filepath: Path, processor, max_lines: Optional[int] = None) -> Any:
        """
        Process a large file with memory efficiency.
        
        Args:
            filepath: Path to file
            processor: Function to process each line
            max_lines: Maximum number of lines to process (None for all)
            
        Returns:
            Result from processor
        """
        line_count = 0
        
        for line in self.stream_file_lines(filepath):
            processor(line)
            line_count += 1
            
            if max_lines and line_count >= max_lines:
                break
            
            # Periodically check and optimize memory
            if line_count % 10000 == 0 and self.should_optimize():
                self.optimize()
        
        return line_count
    
    def batch_process_files(self, filepaths: List[Path], 
                          processor, batch_size: int = 100) -> Dict[str, Any]:
        """
        Process files in batches to manage memory.
        
        Args:
            filepaths: List of file paths
            processor: Function to process each file
            batch_size: Number of files to process before optimization
            
        Returns:
            Processing statistics
        """
        results = {
            'processed': 0,
            'failed': 0,
            'optimizations': 0
        }
        
        for i, filepath in enumerate(filepaths):
            try:
                processor(filepath)
                results['processed'] += 1
            except Exception as e:
                self.logger.error(f"Error processing {filepath}: {e}")
                results['failed'] += 1
            
            # Optimize every batch_size files
            if (i + 1) % batch_size == 0:
                if self.should_optimize():
                    self.optimize()
                    results['optimizations'] += 1
        
        # Final optimization
        if self.should_optimize():
            self.optimize()
            results['optimizations'] += 1
        
        return results


class StreamingDataCollector:
    """Collect data in a memory-efficient streaming manner."""
    
    def __init__(self, output_file: Optional[Path] = None):
        """
        Initialize streaming data collector.
        
        Args:
            output_file: Optional file to stream data to
        """
        self.output_file = output_file
        self.data_count = 0
        self.file_handle = None
        
        if output_file:
            self.file_handle = open(output_file, 'w', encoding='utf-8')
    
    def add(self, data: Dict[str, Any]) -> None:
        """
        Add data item in streaming fashion.
        
        Args:
            data: Data to add
        """
        if self.file_handle:
            import json
            self.file_handle.write(json.dumps(data) + '\n')
            self.file_handle.flush()
        
        self.data_count += 1
    
    def close(self) -> int:
        """
        Close the collector.
        
        Returns:
            Number of items collected
        """
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
        
        return self.data_count
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def optimize_for_large_repo(repo_path: str, max_memory_mb: int = 1024) -> Dict[str, Any]:
    """
    Configure optimal settings for scanning large repositories.
    
    Args:
        repo_path: Path to repository
        max_memory_mb: Maximum memory to use
        
    Returns:
        Optimization configuration
    """
    repo = Path(repo_path)
    
    # Estimate repository size
    total_size = sum(f.stat().st_size for f in repo.rglob('*') if f.is_file())
    total_size_mb = total_size / 1024 / 1024
    
    # Calculate optimal batch size based on repo size
    if total_size_mb < 100:
        batch_size = 1000
        chunk_size = 16384
    elif total_size_mb < 1000:
        batch_size = 500
        chunk_size = 8192
    else:
        batch_size = 100
        chunk_size = 4096
    
    config = {
        'repo_size_mb': total_size_mb,
        'batch_size': batch_size,
        'chunk_size': chunk_size,
        'max_memory_mb': max_memory_mb,
        'streaming_enabled': total_size_mb > 500,
        'gc_enabled': total_size_mb > 1000
    }
    
    # Configure garbage collection
    if config['gc_enabled']:
        gc.set_threshold(700, 10, 10)  # More aggressive GC
    
    return config


def get_system_resources() -> Dict[str, Any]:
    """
    Get available system resources.
    
    Returns:
        Dictionary with system resource information
    """
    if not PSUTIL_AVAILABLE:
        return {
            'total_memory_mb': 0,
            'available_memory_mb': 0,
            'memory_percent': 0,
            'cpu_count': os.cpu_count() or 1,
            'cpu_percent': 0,
            'note': 'psutil not available, resource stats limited'
        }
    
    memory = psutil.virtual_memory()
    
    return {
        'total_memory_mb': memory.total / 1024 / 1024,
        'available_memory_mb': memory.available / 1024 / 1024,
        'memory_percent': memory.percent,
        'cpu_count': psutil.cpu_count(),
        'cpu_percent': psutil.cpu_percent(interval=1)
    }
