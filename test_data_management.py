"""
Test suite for Data Management features:
- Memory Optimization
- Progress Resume
- Project Database
- Comparison History
"""

import unittest
import tempfile
import shutil
import json
import time
from pathlib import Path
from accudoc.memory_optimizer import MemoryOptimizer, StreamingDataCollector, optimize_for_large_repo
from accudoc.progress_manager import ProgressManager
from accudoc.project_database import ProjectDatabase
from accudoc.comparison_history import ComparisonHistory


class TestMemoryOptimizer(unittest.TestCase):
    """Test memory optimization functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.optimizer = MemoryOptimizer(max_memory_mb=512)
    
    def test_get_memory_usage(self):
        """Test getting memory usage stats."""
        usage = self.optimizer.get_memory_usage()
        
        self.assertIn('rss_mb', usage)
        self.assertIn('vms_mb', usage)
        self.assertIsInstance(usage, dict)
    
    def test_optimize(self):
        """Test memory optimization."""
        result = self.optimizer.optimize()
        
        self.assertIn('before_mb', result)
        self.assertIn('after_mb', result)
        self.assertIn('freed_mb', result)
        self.assertIn('objects_collected', result)
    
    def test_stream_file_lines(self):
        """Test streaming file lines."""
        test_dir = tempfile.mkdtemp()
        try:
            test_file = Path(test_dir) / 'test.txt'
            test_file.write_text('line1\nline2\nline3\n')
            
            lines = list(self.optimizer.stream_file_lines(test_file))
            
            self.assertEqual(len(lines), 3)
            self.assertEqual(lines[0], 'line1')
            self.assertEqual(lines[2], 'line3')
        finally:
            shutil.rmtree(test_dir)
    
    def test_process_large_file(self):
        """Test processing large file."""
        test_dir = tempfile.mkdtemp()
        try:
            test_file = Path(test_dir) / 'large.txt'
            test_file.write_text('\n'.join([f'line{i}' for i in range(100)]))
            
            processed_lines = []
            def processor(line):
                processed_lines.append(line)
            
            count = self.optimizer.process_large_file(test_file, processor, max_lines=50)
            
            self.assertEqual(count, 50)
            self.assertEqual(len(processed_lines), 50)
        finally:
            shutil.rmtree(test_dir)
    
    def test_batch_process_files(self):
        """Test batch processing files."""
        test_dir = tempfile.mkdtemp()
        try:
            # Create test files
            files = []
            for i in range(10):
                f = Path(test_dir) / f'file{i}.txt'
                f.write_text(f'content{i}')
                files.append(f)
            
            processed = []
            def processor(filepath):
                processed.append(str(filepath))
            
            results = self.optimizer.batch_process_files(files, processor, batch_size=5)
            
            self.assertEqual(results['processed'], 10)
            self.assertEqual(results['failed'], 0)
        finally:
            shutil.rmtree(test_dir)


class TestStreamingDataCollector(unittest.TestCase):
    """Test streaming data collector."""
    
    def test_collect_data(self):
        """Test collecting data in streaming fashion."""
        test_dir = tempfile.mkdtemp()
        try:
            output_file = Path(test_dir) / 'data.jsonl'
            
            with StreamingDataCollector(output_file) as collector:
                collector.add({'id': 1, 'value': 'test1'})
                collector.add({'id': 2, 'value': 'test2'})
                count = collector.data_count
            
            self.assertEqual(count, 2)
            self.assertTrue(output_file.exists())
            
            # Verify data
            lines = output_file.read_text().strip().split('\n')
            self.assertEqual(len(lines), 2)
        finally:
            shutil.rmtree(test_dir)


class TestProgressManager(unittest.TestCase):
    """Test progress management."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.checkpoint_dir = Path(self.test_dir) / 'checkpoints'
        self.manager = ProgressManager(self.checkpoint_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_create_checkpoint(self):
        """Test creating checkpoint."""
        repo_path = '/test/repo'
        config = {'template': 'default'}
        
        checkpoint = self.manager.create_checkpoint(repo_path, config)
        
        self.assertIn('checkpoint_id', checkpoint)
        self.assertEqual(checkpoint['repo_path'], str(Path(repo_path).absolute()))
        self.assertEqual(checkpoint['status'], 'in_progress')
    
    def test_save_and_load_checkpoint(self):
        """Test saving and loading checkpoint."""
        repo_path = '/test/repo'
        config = {'template': 'default'}
        
        checkpoint = self.manager.create_checkpoint(repo_path, config)
        checkpoint_id = checkpoint['checkpoint_id']
        
        # Load it back
        loaded = self.manager.load_checkpoint(repo_path)
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['checkpoint_id'], checkpoint_id)
    
    def test_update_progress(self):
        """Test updating progress."""
        repo_path = '/test/repo'
        checkpoint = self.manager.create_checkpoint(repo_path, {})
        
        self.manager.update_progress('/test/file1.py', success=True)
        self.manager.update_progress('/test/file2.py', success=False)
        
        self.assertEqual(self.manager.current_checkpoint['statistics']['processed'], 1)
        self.assertEqual(self.manager.current_checkpoint['statistics']['failed'], 1)
    
    def test_mark_complete(self):
        """Test marking checkpoint as complete."""
        repo_path = '/test/repo'
        self.manager.create_checkpoint(repo_path, {})
        
        self.manager.mark_complete()
        
        self.assertEqual(self.manager.current_checkpoint['status'], 'complete')
        self.assertIn('completed_at', self.manager.current_checkpoint)
    
    def test_can_resume(self):
        """Test checking if scan can be resumed."""
        repo_path = '/test/repo'
        
        # No checkpoint yet
        self.assertFalse(self.manager.can_resume(repo_path))
        
        # Create in-progress checkpoint
        self.manager.create_checkpoint(repo_path, {})
        self.assertTrue(self.manager.can_resume(repo_path))
        
        # Mark complete
        self.manager.mark_complete()
        self.assertFalse(self.manager.can_resume(repo_path))
    
    def test_get_progress_percentage(self):
        """Test getting progress percentage."""
        repo_path = '/test/repo'
        checkpoint = self.manager.create_checkpoint(repo_path, {})
        
        checkpoint['statistics']['total_files'] = 100
        checkpoint['statistics']['processed'] = 50
        
        percentage = self.manager.get_progress_percentage()
        
        self.assertEqual(percentage, 50.0)


class TestProjectDatabase(unittest.TestCase):
    """Test project database."""
    
    def setUp(self):
        """Set up test database."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / 'test.db'
        self.db = ProjectDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_add_project(self):
        """Test adding a project."""
        repo_path = '/test/repo'
        project_id = self.db.add_project(repo_path, name='Test Project')
        
        self.assertIsNotNone(project_id)
        self.assertTrue(project_id.startswith('proj_'))
        
        # Retrieve project
        project = self.db.get_project(project_id)
        self.assertIsNotNone(project)
        self.assertEqual(project['name'], 'Test Project')
    
    def test_add_scan(self):
        """Test adding a scan."""
        project_id = self.db.add_project('/test/repo')
        
        scan_data = {
            'duration_seconds': 10.5,
            'files_scanned': 42,
            'files_changed': 5,
            'status': 'complete',
            'config': {'template': 'default'},
            'results': {'loc': 1000}
        }
        
        scan_id = self.db.add_scan(project_id, scan_data)
        
        self.assertIsNotNone(scan_id)
        self.assertTrue(scan_id.startswith('scan_'))
        
        # Retrieve scan
        scan = self.db.get_scan(scan_id)
        self.assertIsNotNone(scan)
        self.assertEqual(scan['files_scanned'], 42)
    
    def test_list_projects(self):
        """Test listing projects."""
        self.db.add_project('/test/repo1', name='Project 1')
        self.db.add_project('/test/repo2', name='Project 2')
        
        projects = self.db.list_projects()
        
        self.assertGreaterEqual(len(projects), 2)
    
    def test_get_scans(self):
        """Test getting scans for a project."""
        project_id = self.db.add_project('/test/repo')
        
        # Add multiple scans
        for i in range(3):
            self.db.add_scan(project_id, {
                'files_scanned': 10 + i,
                'status': 'complete'
            })
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        scans = self.db.get_scans(project_id)
        
        self.assertEqual(len(scans), 3)
    
    def test_add_comparison(self):
        """Test adding comparison."""
        project_id = self.db.add_project('/test/repo')
        scan1_id = self.db.add_scan(project_id, {'files_scanned': 10})
        scan2_id = self.db.add_scan(project_id, {'files_scanned': 15})
        
        changes = {
            'files_added': 5,
            'files_removed': 0
        }
        
        comparison_id = self.db.add_comparison(project_id, scan1_id, scan2_id, changes)
        
        self.assertIsNotNone(comparison_id)
        self.assertTrue(comparison_id.startswith('cmp_'))


class TestComparisonHistory(unittest.TestCase):
    """Test comparison history."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / 'test.db'
        self.db = ProjectDatabase(self.db_path)
        self.history = ComparisonHistory(self.db)
    
    def tearDown(self):
        """Clean up test environment."""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_compare_scans(self):
        """Test comparing two scans."""
        scan1 = {
            'scan_id': 'scan1',
            'scanned_at': '2025-01-01T00:00:00',
            'files_scanned': 10,
            'results': json.dumps({'loc': 1000})
        }
        
        scan2 = {
            'scan_id': 'scan2',
            'scanned_at': '2025-01-02T00:00:00',
            'files_scanned': 15,
            'results': json.dumps({'loc': 1500})
        }
        
        comparison = self.history.compare_scans(scan1, scan2)
        
        self.assertEqual(comparison['scan1_id'], 'scan1')
        self.assertEqual(comparison['scan2_id'], 'scan2')
        self.assertIn('changes', comparison)
        self.assertEqual(comparison['changes']['files']['delta'], 5)
    
    def test_track_evolution(self):
        """Test tracking evolution of a metric."""
        # Add project with multiple scans
        project_id = self.db.add_project('/test/repo')
        
        for i in range(5):
            self.db.add_scan(project_id, {
                'files_scanned': 10 + i * 2,
                'status': 'complete'
            })
            time.sleep(0.01)
        
        evolution = self.history.track_evolution(project_id, 'files_scanned')
        
        self.assertEqual(evolution['project_id'], project_id)
        self.assertEqual(evolution['metric'], 'files_scanned')
        self.assertEqual(len(evolution['data_points']), 5)
    
    def test_find_regressions(self):
        """Test finding regressions."""
        project_id = self.db.add_project('/test/repo')
        
        # Add scans with regression
        self.db.add_scan(project_id, {'files_scanned': 100})
        time.sleep(0.01)
        self.db.add_scan(project_id, {'files_scanned': 80})  # Regression
        
        regressions = self.history.find_regressions(project_id, threshold=10.0)
        
        self.assertGreater(len(regressions), 0)
        self.assertLess(regressions[0]['change_percent'], -10.0)
    
    def test_get_statistics_summary(self):
        """Test getting statistics summary."""
        project_id = self.db.add_project('/test/repo')
        
        for i in range(3):
            self.db.add_scan(project_id, {
                'files_scanned': 50 + i * 10,
                'duration_seconds': 5.0 + i
            })
            time.sleep(0.01)
        
        summary = self.history.get_statistics_summary(project_id)
        
        self.assertIn('total_scans', summary)
        self.assertEqual(summary['total_scans'], 3)
        self.assertIn('files_scanned', summary)
        self.assertIn('scan_duration', summary)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("AccuDoc Data Management Test Suite")
    print("Testing: Memory Optimization, Progress Resume, Database, History")
    print("=" * 60)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
