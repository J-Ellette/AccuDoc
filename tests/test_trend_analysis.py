"""
Test suite for trend analysis feature.
"""

import unittest
import tempfile
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from accudoc.trend_analysis import TrendAnalyzer


class TestTrendAnalyzer(unittest.TestCase):
    """Test cases for TrendAnalyzer."""
    
    @classmethod
    def setUpClass(cls):
        """Set up a test git repository."""
        cls.test_repo = tempfile.mkdtemp()
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=cls.test_repo, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], 
                      cwd=cls.test_repo, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], 
                      cwd=cls.test_repo, capture_output=True)
        
        # Create some test commits
        for i in range(5):
            # Add a file
            test_file = os.path.join(cls.test_repo, f'file{i}.py')
            with open(test_file, 'w') as f:
                f.write(f'# Test file {i}\nprint("Hello {i}")\n')
            
            subprocess.run(['git', 'add', '.'], cwd=cls.test_repo, capture_output=True)
            subprocess.run(['git', 'commit', '-m', f'Commit {i}'], 
                          cwd=cls.test_repo, capture_output=True)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test repository."""
        if os.path.exists(cls.test_repo):
            shutil.rmtree(cls.test_repo)
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = TrendAnalyzer(self.test_repo)
        self.assertEqual(str(analyzer.repo_path), self.test_repo)
    
    def test_analyze_week(self):
        """Test analysis over week period."""
        analyzer = TrendAnalyzer(self.test_repo)
        trends = analyzer.analyze(period='week', intervals=5)
        
        self.assertIn('period', trends)
        self.assertEqual(trends['period'], 'week')
        self.assertIn('time_points', trends)
        self.assertIn('commit_count', trends)
        self.assertIn('file_count', trends)
        self.assertIn('contributors', trends)
    
    def test_analyze_month(self):
        """Test analysis over month period."""
        analyzer = TrendAnalyzer(self.test_repo)
        trends = analyzer.analyze(period='month', intervals=5)
        
        self.assertEqual(trends['period'], 'month')
        self.assertEqual(trends['intervals'], 5)
    
    def test_analyze_all(self):
        """Test analysis over all time."""
        analyzer = TrendAnalyzer(self.test_repo)
        trends = analyzer.analyze(period='all', intervals=5)
        
        self.assertEqual(trends['period'], 'all')
        self.assertGreaterEqual(len(trends['time_points']), 5)
    
    def test_time_points_generation(self):
        """Test time points generation."""
        analyzer = TrendAnalyzer(self.test_repo)
        time_points = analyzer._get_time_points('week', 5)
        
        self.assertEqual(len(time_points), 6)  # intervals + 1
        # Verify they're in order
        for i in range(len(time_points) - 1):
            self.assertLess(time_points[i], time_points[i+1])
    
    def test_first_commit_date(self):
        """Test getting first commit date."""
        analyzer = TrendAnalyzer(self.test_repo)
        first_commit = analyzer._get_first_commit_date()
        
        self.assertIsNotNone(first_commit)
        self.assertIsInstance(first_commit, datetime)
    
    def test_commit_count(self):
        """Test getting commit count."""
        analyzer = TrendAnalyzer(self.test_repo)
        count = analyzer._get_commit_count(datetime.now())
        
        self.assertGreaterEqual(count, 5)  # We created 5 commits
    
    def test_file_count(self):
        """Test getting file count."""
        analyzer = TrendAnalyzer(self.test_repo)
        count = analyzer._get_file_count(datetime.now())
        
        self.assertGreaterEqual(count, 5)  # We created 5 files
    
    def test_contributor_count(self):
        """Test getting contributor count."""
        analyzer = TrendAnalyzer(self.test_repo)
        count = analyzer._get_contributor_count(datetime.now())
        
        self.assertEqual(count, 1)  # One test contributor
    
    def test_lines_stats(self):
        """Test getting lines statistics."""
        analyzer = TrendAnalyzer(self.test_repo)
        stats = analyzer._get_lines_stats(datetime.now())
        
        self.assertIn('added', stats)
        self.assertIn('deleted', stats)
        self.assertGreater(stats['added'], 0)
    
    def test_language_distribution(self):
        """Test getting language distribution."""
        analyzer = TrendAnalyzer(self.test_repo)
        languages = analyzer._get_language_distribution(datetime.now())
        
        self.assertIn('Python', languages)
        self.assertGreaterEqual(languages['Python'], 5)
    
    def test_ext_to_language(self):
        """Test extension to language conversion."""
        analyzer = TrendAnalyzer(self.test_repo)
        
        self.assertEqual(analyzer._ext_to_language('.py'), 'Python')
        self.assertEqual(analyzer._ext_to_language('.js'), 'JavaScript')
        self.assertEqual(analyzer._ext_to_language('.java'), 'Java')
        self.assertEqual(analyzer._ext_to_language('.unknown'), 'Other')
    
    def test_growth_rates_calculation(self):
        """Test growth rates calculation."""
        analyzer = TrendAnalyzer(self.test_repo)
        
        # Create mock trends data
        trends = {
            'commit_count': [1, 2, 3, 4, 5],
            'file_count': [1, 2, 3, 4, 5],
            'contributors': [1, 1, 1, 1, 1],
            'lines_added': [10, 20, 30, 40, 50]
        }
        
        growth_rates = analyzer._calculate_growth_rates(trends)
        
        self.assertIn('commit_count', growth_rates)
        self.assertIn('file_count', growth_rates)
        self.assertEqual(growth_rates['commit_count'], 400.0)  # 400% growth
        self.assertEqual(growth_rates['file_count'], 400.0)
    
    def test_generate_summary(self):
        """Test summary generation."""
        analyzer = TrendAnalyzer(self.test_repo)
        analyzer.analyze(period='all', intervals=5)
        
        summary = analyzer.trends['summary']
        
        self.assertIn('period', summary)
        self.assertIn('total_commits', summary)
        self.assertIn('total_files', summary)
        self.assertIn('total_contributors', summary)
    
    def test_generate_report(self):
        """Test report generation."""
        analyzer = TrendAnalyzer(self.test_repo)
        analyzer.analyze(period='week', intervals=5)
        
        report = analyzer.generate_report()
        
        self.assertIn('TREND ANALYSIS REPORT', report)
        self.assertIn('SUMMARY METRICS', report)
        self.assertIn('GROWTH RATES', report)
        self.assertIn('TREND DATA', report)
    
    def test_export_to_json(self):
        """Test JSON export."""
        analyzer = TrendAnalyzer(self.test_repo)
        analyzer.analyze(period='week', intervals=3)
        
        data = analyzer.export_to_json()
        
        self.assertIsInstance(data, dict)
        self.assertIn('period', data)
        self.assertIn('time_points', data)
        self.assertIn('commit_count', data)
    
    def test_export_to_csv(self):
        """Test CSV export."""
        analyzer = TrendAnalyzer(self.test_repo)
        analyzer.analyze(period='week', intervals=3)
        
        output_dir = tempfile.mkdtemp()
        try:
            files = analyzer.export_to_csv(output_dir)
            
            self.assertGreater(len(files), 0)
            
            # Verify files exist
            for file_path in files:
                self.assertTrue(os.path.exists(file_path))
        finally:
            shutil.rmtree(output_dir)
    
    def test_analyze_without_git_repo(self):
        """Test analyzing non-git directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            analyzer = TrendAnalyzer(temp_dir)
            trends = analyzer.analyze(period='week', intervals=2)
            
            # Should still return structure even if empty
            self.assertIn('period', trends)
            self.assertIn('commit_count', trends)
        finally:
            shutil.rmtree(temp_dir)


def run_tests():
    """Run all tests and print results."""
    print("=" * 60)
    print("Testing Trend Analysis Feature")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTrendAnalyzer)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
