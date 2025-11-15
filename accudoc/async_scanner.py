"""
Asynchronous scanning operations for AccuDoc.

Provides async wrappers for repository scanning to prevent UI blocking.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Callable, Any
from pathlib import Path


class AsyncScanner:
    """
    Asynchronous wrapper for repository scanning.
    
    Allows non-blocking scans in GUI and other async contexts.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize async scanner.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def scan_repository(
        self,
        repo_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Asynchronously scan a repository.
        
        Args:
            repo_path: Path to repository
            progress_callback: Optional progress callback
            
        Returns:
            Repository information dictionary
        """
        from accudoc.scanner import RepositoryScanner
        
        loop = asyncio.get_event_loop()
        
        def _scan():
            scanner = RepositoryScanner(repo_path, progress_callback=progress_callback)
            return scanner.scan()
        
        result = await loop.run_in_executor(self.executor, _scan)
        return result
    
    async def generate_documentation(
        self,
        repo_info: Dict,
        output_path: str,
        **kwargs
    ) -> str:
        """
        Asynchronously generate documentation.
        
        Args:
            repo_info: Repository information
            output_path: Output file path
            **kwargs: Additional generation options
            
        Returns:
            Path to generated documentation
        """
        from accudoc.generator import DocumentGenerator
        
        loop = asyncio.get_event_loop()
        
        def _generate():
            template = kwargs.get('template', 'default')
            generator = DocumentGenerator(repo_info, template=template)
            return generator.generate_and_export(output_path, **kwargs)
        
        result = await loop.run_in_executor(self.executor, _generate)
        return result
    
    async def scan_and_generate(
        self,
        repo_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> str:
        """
        Asynchronously scan and generate documentation.
        
        Args:
            repo_path: Path to repository
            output_path: Output file path
            progress_callback: Optional progress callback
            **kwargs: Additional generation options
            
        Returns:
            Path to generated documentation
        """
        # Scan repository
        repo_info = await self.scan_repository(repo_path, progress_callback)
        
        # Generate documentation
        result = await self.generate_documentation(repo_info, output_path, **kwargs)
        
        return result
    
    async def batch_scan(
        self,
        repo_paths: list,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Dict]:
        """
        Asynchronously scan multiple repositories.
        
        Args:
            repo_paths: List of repository paths
            progress_callback: Optional progress callback (repo_path, current, total)
            
        Returns:
            Dictionary mapping repo paths to scan results
        """
        results = {}
        total = len(repo_paths)
        
        for i, repo_path in enumerate(repo_paths, 1):
            if progress_callback:
                progress_callback(repo_path, i, total)
            
            try:
                result = await self.scan_repository(repo_path)
                results[repo_path] = result
            except Exception as e:
                results[repo_path] = {'error': str(e)}
        
        return results
    
    async def scan_with_timeout(
        self,
        repo_path: str,
        timeout: float,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Dict]:
        """
        Scan repository with timeout.
        
        Args:
            repo_path: Path to repository
            timeout: Timeout in seconds
            progress_callback: Optional progress callback
            
        Returns:
            Repository info or None if timeout
        """
        try:
            result = await asyncio.wait_for(
                self.scan_repository(repo_path, progress_callback),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return None
    
    def shutdown(self):
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.shutdown()


class AsyncEventManager:
    """
    Event-driven async operations manager.
    
    Allows subscribing to events during async operations.
    """
    
    def __init__(self):
        """Initialize event manager."""
        self.listeners: Dict[str, list] = {}
    
    def subscribe(self, event: str, callback: Callable):
        """
        Subscribe to an event.
        
        Args:
            event: Event name
            callback: Callback function
        """
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
    
    def unsubscribe(self, event: str, callback: Callable):
        """
        Unsubscribe from an event.
        
        Args:
            event: Event name
            callback: Callback function
        """
        if event in self.listeners:
            self.listeners[event].remove(callback)
    
    async def emit(self, event: str, *args, **kwargs):
        """
        Emit an event to all listeners.
        
        Args:
            event: Event name
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks
        """
        if event not in self.listeners:
            return
        
        tasks = []
        for callback in self.listeners[event]:
            if asyncio.iscoroutinefunction(callback):
                tasks.append(callback(*args, **kwargs))
            else:
                # Run sync callbacks in executor
                loop = asyncio.get_event_loop()
                tasks.append(loop.run_in_executor(None, callback, *args))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Convenience functions

async def async_scan(repo_path: str, **kwargs) -> Dict:
    """
    Convenience function for async repository scan.
    
    Args:
        repo_path: Repository path
        **kwargs: Additional options
        
    Returns:
        Repository information
    """
    async with AsyncScanner() as scanner:
        return await scanner.scan_repository(repo_path, **kwargs)


async def async_generate(repo_info: Dict, output_path: str, **kwargs) -> str:
    """
    Convenience function for async documentation generation.
    
    Args:
        repo_info: Repository information
        output_path: Output path
        **kwargs: Additional options
        
    Returns:
        Generated documentation path
    """
    async with AsyncScanner() as scanner:
        return await scanner.generate_documentation(repo_info, output_path, **kwargs)


async def async_export(repo_path: str, output_path: str, **kwargs) -> str:
    """
    Convenience function for async scan and export.
    
    Args:
        repo_path: Repository path
        output_path: Output path
        **kwargs: Additional options
        
    Returns:
        Generated documentation path
    """
    async with AsyncScanner() as scanner:
        return await scanner.scan_and_generate(repo_path, output_path, **kwargs)
