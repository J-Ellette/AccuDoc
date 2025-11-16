"""
Test suite for health dashboard feature.
"""

import unittest
from accudoc.health_dashboard import HealthMetrics, HealthDashboard


class TestHealthMetrics(unittest.TestCase):
    """Test cases for HealthMetrics."""
    
    def setUp(self):
        """Set up test repository info."""
        self.repo_info_good = {
            'name': 'GoodProject',
            'path': '/test/good',
            'files_count': 50,
            'documentation': ['README.md', 'CONTRIBUTING.md', 'LICENSE', 'CHANGELOG.md'],
            'api_docs': [{'name': 'main', 'type': 'function'}],
            'code_examples': [{'file': 'example.py'}],
            'todos': [],
            'dependencies': {'pip': [{'name': 'flask', 'version': '2.0.0'}]},
            'statistics': {
                'total_lines': 1000,
                'code_lines': 700,
                'comment_lines': 200,
                'blank_lines': 100
            },
            'config_files': ['setup.py', 'requirements.txt'],
            'license': 'MIT'
        }
        
        self.repo_info_poor = {
            'name': 'PoorProject',
            'path': '/test/poor',
            'files_count': 200,
            'documentation': [],
            'todos': [
                {'file': 'app.py', 'line': 1, 'type': 'TODO', 'comment': 'Fix this'},
                {'file': 'app.py', 'line': 2, 'type': 'FIXME', 'comment': 'Bug here'}
            ] * 10,  # 20 TODOs
            'dependencies': {},
            'statistics': {
                'total_lines': 2000,
                'code_lines': 1900,
                'comment_lines': 50,
                'blank_lines': 50
            },
            'license': 'Not found'
        }
    
    def test_initialization(self):
        """Test metrics initialization."""
        metrics = HealthMetrics(self.repo_info_good)
        self.assertIsNotNone(metrics.metrics)
        self.assertIn('overall_health', metrics.metrics)
    
    def test_doc_coverage_good(self):
        """Test documentation coverage for good project."""
        metrics = HealthMetrics(self.repo_info_good)
        doc_cov = metrics.metrics['documentation_coverage']
        
        self.assertGreaterEqual(doc_cov['score'], 70)
        self.assertIn('grade', doc_cov)
        self.assertIn('status', doc_cov)
        self.assertIn('reasons', doc_cov)
    
    def test_doc_coverage_poor(self):
        """Test documentation coverage for poor project."""
        metrics = HealthMetrics(self.repo_info_poor)
        doc_cov = metrics.metrics['documentation_coverage']
        
        self.assertLess(doc_cov['score'], 50)
        self.assertEqual(doc_cov['grade'], 'F')
    
    def test_code_quality_good(self):
        """Test code quality for good project."""
        metrics = HealthMetrics(self.repo_info_good)
        quality = metrics.metrics['code_quality']
        
        self.assertGreaterEqual(quality['score'], 70)
    
    def test_code_quality_poor(self):
        """Test code quality with many TODOs."""
        metrics = HealthMetrics(self.repo_info_poor)
        quality = metrics.metrics['code_quality']
        
        # Should be penalized for 20 TODOs
        self.assertLess(quality['score'], 70)
    
    def test_dependency_health_no_deps(self):
        """Test dependency health with no dependencies."""
        metrics = HealthMetrics(self.repo_info_poor)
        dep_health = metrics.metrics['dependency_health']
        
        # No dependencies should be excellent
        self.assertEqual(dep_health['score'], 100)
        self.assertEqual(dep_health['grade'], 'A')
    
    def test_dependency_health_with_deps(self):
        """Test dependency health with dependencies."""
        metrics = HealthMetrics(self.repo_info_good)
        dep_health = metrics.metrics['dependency_health']
        
        self.assertGreaterEqual(dep_health['score'], 70)
    
    def test_maintainability_good(self):
        """Test maintainability with good comment ratio."""
        metrics = HealthMetrics(self.repo_info_good)
        maint = metrics.metrics['maintainability']
        
        # 20% comment ratio should score well
        self.assertGreaterEqual(maint['score'], 75)
    
    def test_maintainability_poor(self):
        """Test maintainability with poor comment ratio."""
        metrics = HealthMetrics(self.repo_info_poor)
        maint = metrics.metrics['maintainability']
        
        # 2.5% comment ratio should score poorly
        self.assertLess(maint['score'], 75)
    
    def test_license_compliance_with_license(self):
        """Test license compliance with license present."""
        metrics = HealthMetrics(self.repo_info_good)
        license = metrics.metrics['license_compliance']
        
        self.assertEqual(license['score'], 100)
        self.assertEqual(license['grade'], 'A')
    
    def test_license_compliance_no_license(self):
        """Test license compliance without license."""
        metrics = HealthMetrics(self.repo_info_poor)
        license = metrics.metrics['license_compliance']
        
        self.assertEqual(license['score'], 50)
        self.assertIn('grade', license)
    
    def test_overall_health_calculation(self):
        """Test overall health score calculation."""
        metrics = HealthMetrics(self.repo_info_good)
        overall = metrics.metrics['overall_health']
        
        self.assertIn('score', overall)
        self.assertIn('grade', overall)
        self.assertIn('status', overall)
        self.assertIn('weights', overall)
        self.assertGreaterEqual(overall['score'], 0)
        self.assertLessEqual(overall['score'], 100)
    
    def test_score_to_grade(self):
        """Test score to grade conversion."""
        metrics = HealthMetrics(self.repo_info_good)
        
        self.assertEqual(metrics._score_to_grade(95), 'A')
        self.assertEqual(metrics._score_to_grade(80), 'B')
        self.assertEqual(metrics._score_to_grade(65), 'C')
        self.assertEqual(metrics._score_to_grade(50), 'D')
        self.assertEqual(metrics._score_to_grade(30), 'F')
    
    def test_score_to_status(self):
        """Test score to status conversion."""
        metrics = HealthMetrics(self.repo_info_good)
        
        self.assertEqual(metrics._score_to_status(95), 'Excellent')
        self.assertEqual(metrics._score_to_status(80), 'Good')
        self.assertEqual(metrics._score_to_status(65), 'Fair')
        self.assertEqual(metrics._score_to_status(50), 'Poor')
        self.assertEqual(metrics._score_to_status(30), 'Critical')
    
    def test_get_summary(self):
        """Test getting metrics summary."""
        metrics = HealthMetrics(self.repo_info_good)
        summary = metrics.get_summary()
        
        self.assertIn('overall_score', summary)
        self.assertIn('overall_grade', summary)
        self.assertIn('overall_status', summary)
        self.assertIn('documentation', summary)
        self.assertIn('code_quality', summary)
        self.assertIn('dependencies', summary)
        self.assertIn('maintainability', summary)
        self.assertIn('license', summary)


class TestHealthDashboard(unittest.TestCase):
    """Test cases for HealthDashboard."""
    
    def setUp(self):
        """Set up test repository info."""
        self.repo_info = {
            'name': 'TestProject',
            'path': '/test/project',
            'files_count': 50,
            'documentation': ['README.md'],
            'todos': [],
            'dependencies': {},
            'statistics': {
                'total_lines': 1000,
                'code_lines': 700,
                'comment_lines': 200
            },
            'license': 'MIT'
        }
    
    def test_initialization(self):
        """Test dashboard initialization."""
        dashboard = HealthDashboard(self.repo_info)
        self.assertIsNotNone(dashboard.metrics)
    
    def test_generate_text_dashboard(self):
        """Test generating text dashboard."""
        dashboard = HealthDashboard(self.repo_info)
        output = dashboard.generate_text_dashboard()
        
        self.assertIn('PROJECT HEALTH DASHBOARD', output)
        self.assertIn('OVERALL HEALTH', output)
        self.assertIn('DOCUMENTATION COVERAGE', output)
        self.assertIn('CODE QUALITY', output)
        self.assertIn('RECOMMENDATIONS', output)
    
    def test_progress_bar_creation(self):
        """Test progress bar creation."""
        dashboard = HealthDashboard(self.repo_info)
        
        bar = dashboard._create_progress_bar(50)
        self.assertIn('50%', bar)
        self.assertIn('[', bar)
        self.assertIn(']', bar)
        
        bar_full = dashboard._create_progress_bar(100)
        self.assertIn('100%', bar_full)
        
        bar_empty = dashboard._create_progress_bar(0)
        self.assertIn('0%', bar_empty)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        dashboard = HealthDashboard(self.repo_info)
        recommendations = dashboard._generate_recommendations()
        
        self.assertIsInstance(recommendations, list)
        # With good metrics, should have few or no recommendations
    
    def test_generate_recommendations_poor_project(self):
        """Test recommendations for poor project."""
        poor_repo = {
            'name': 'PoorProject',
            'path': '/test/poor',
            'documentation': [],
            'todos': [{'file': 'app.py', 'line': 1, 'type': 'TODO'}] * 15,
            'dependencies': {},
            'statistics': {
                'total_lines': 1000,
                'code_lines': 950,
                'comment_lines': 25
            },
            'license': 'Not found'
        }
        
        dashboard = HealthDashboard(poor_repo)
        recommendations = dashboard._generate_recommendations()
        
        self.assertGreater(len(recommendations), 0)
        # Should recommend adding documentation
        self.assertTrue(any('documentation' in r.lower() for r in recommendations))
    
    def test_export_to_dict(self):
        """Test exporting dashboard to dictionary."""
        dashboard = HealthDashboard(self.repo_info)
        data = dashboard.export_to_dict()
        
        self.assertIn('repository', data)
        self.assertIn('metrics', data)
        self.assertIn('summary', data)
        self.assertIn('recommendations', data)
        
        self.assertEqual(data['repository']['name'], 'TestProject')


def run_tests():
    """Run all tests and print results."""
    print("=" * 60)
    print("Testing Health Dashboard Feature")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestHealthMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthDashboard))
    
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
