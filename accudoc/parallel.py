"""
Parallel processing module for AccuDoc.

Provides multi-threaded scanning capabilities for improved performance
on large repositories.
"""

import concurrent.futures
import multiprocessing
import logging
from typing import List, Callable, Any, Dict, Optional
from pathlib import Path


class ParallelProcessor:
    """Handles parallel processing of repository files."""
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize parallel processor.
        
        Args:
            max_workers: Maximum number of worker threads. Defaults to CPU count.
        """
        self.max_workers = max_workers or min(32, (multiprocessing.cpu_count() or 1) + 4)
        self.logger = logging.getLogger('accudoc.parallel')
        
    def process_files(self, files: List[Path], processor_func: Callable, 
                     chunk_size: int = 10, progress_callback: Optional[Callable] = None) -> List[Any]:
        """
        Process files in parallel.
        
        Args:
            files: List of file paths to process
            processor_func: Function to process each file (must be picklable)
            chunk_size: Number of files per chunk for better performance
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of results from processing
        """
        results = []
        total = len(files)
        processed = 0
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(processor_func, file): file 
                    for file in files
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                        processed += 1
                        
                        # Report progress
                        if progress_callback and processed % chunk_size == 0:
                            progress_callback(f"Processed {processed}/{total} files")
                            
                    except Exception as e:
                        self.logger.error(f"Error processing {file}: {str(e)}")
                        results.append(None)
                        
        except Exception as e:
            self.logger.error(f"Parallel processing failed: {str(e)}")
            raise
        
        # Final progress update
        if progress_callback and processed > 0:
            progress_callback(f"Processed {processed}/{total} files")
        
        return results
    
    def process_items_batch(self, items: List[Any], processor_func: Callable,
                           progress_callback: Optional[Callable] = None) -> List[Any]:
        """
        Process items in batches for better performance.
        
        Args:
            items: List of items to process
            processor_func: Function to process each item
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of results
        """
        results = []
        total = len(items)
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(processor_func, item) for item in items]
                
                for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                    try:
                        result = future.result()
                        results.append(result)
                        
                        if progress_callback and i % 10 == 0:
                            progress_callback(f"Processed {i}/{total} items")
                            
                    except Exception as e:
                        self.logger.error(f"Error processing item: {str(e)}")
                        results.append(None)
                        
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            raise
        
        return results
    
    def map_parallel(self, func: Callable, items: List[Any], 
                    ordered: bool = True) -> List[Any]:
        """
        Map a function over items in parallel.
        
        Args:
            func: Function to apply to each item
            items: List of items
            ordered: Whether to preserve order of results
            
        Returns:
            List of results
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            if ordered:
                return list(executor.map(func, items))
            else:
                futures = [executor.submit(func, item) for item in items]
                return [future.result() for future in concurrent.futures.as_completed(futures)]


class ChunkProcessor:
    """Process large datasets in chunks to manage memory."""
    
    def __init__(self, chunk_size: int = 100):
        """
        Initialize chunk processor.
        
        Args:
            chunk_size: Number of items per chunk
        """
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('accudoc.chunks')
        
    def process_in_chunks(self, items: List[Any], processor_func: Callable,
                         progress_callback: Optional[Callable] = None) -> List[Any]:
        """
        Process items in chunks to manage memory usage.
        
        Args:
            items: List of items to process
            processor_func: Function to process each chunk
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of all results
        """
        all_results = []
        total_items = len(items)
        
        # Process in chunks
        for i in range(0, total_items, self.chunk_size):
            chunk = items[i:i + self.chunk_size]
            chunk_num = i // self.chunk_size + 1
            total_chunks = (total_items + self.chunk_size - 1) // self.chunk_size
            
            if progress_callback:
                progress_callback(f"Processing chunk {chunk_num}/{total_chunks}")
            
            try:
                results = processor_func(chunk)
                all_results.extend(results)
            except Exception as e:
                self.logger.error(f"Error processing chunk {chunk_num}: {str(e)}")
        
        return all_results
    
    @staticmethod
    def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
        """
        Split a list into chunks.
        
        Args:
            items: List to chunk
            chunk_size: Size of each chunk
            
        Returns:
            List of chunks
        """
        return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def parallel_file_processor(file_path: Path, analysis_func: Callable) -> Dict:
    """
    Process a single file (wrapper for parallel execution).
    
    Args:
        file_path: Path to file
        analysis_func: Function to analyze the file
        
    Returns:
        Analysis results
    """
    try:
        return {
            'file': str(file_path),
            'result': analysis_func(file_path),
            'success': True
        }
    except Exception as e:
        return {
            'file': str(file_path),
            'error': str(e),
            'success': False
        }
