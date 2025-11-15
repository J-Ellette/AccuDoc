"""
Test suite for multi-repository documentation consistency dashboard.
"""

import unittest
import tempfile
import os
import shutil
import json
from pathlib import Path
from accudoc.multi_repo_dashboard import (
    MultiRepoDashboard, DashboardConfig, RepositoryAnalysis, ConsistencyGap
)


class TestMultiRepoDashboard(unittest.TestCase):
    """Test cases for MultiRepoDashboard."""
    
    def setUp(self):
        """Set up test repository data."""
        self.repo1 = {
            'name': 'Project Alpha',
            'path': '/test/alpha',
            'files_count': 120,
            'languages': {'Python': 80, 'JavaScript': 40},
            'statistics': {
                'total_lines': 12000,
                'code_lines': 8500,
                'comment_lines': 2500,
                'blank_lines': 1000
            },
            'dependencies': {
                'pip': [
                    {'name': 'flask', 'version': '2.0.0'},
                    {'name': 'requests', 'version': '2.28.0'}
                ]
            },
            'documentation': ['README.md', 'CONTRIBUTING.md', 'LICENSE'],
            'api_docs': [{'name': 'api1'}, {'name': 'api2'}],
            'code_examples': [{'file': 'example1.py'}, {'file': 'example2.py'}],
            'todos': [
                {'file': 'app.py', 'line': 1, 'type': 'TODO', 'comment': 'Test'}
            ],
            'license': 'MIT'
        }
        
        self.repo2 = {
            'name': 'Project Beta',
            'path': '/test/beta',
            'files_count': 80,
            'languages': {'Java': 60, 'Python': 20},
            'statistics': {
                'total_lines': 8000,
                'code_lines': 6000,
                'comment_lines': 1500,
                'blank_lines': 500
            },
            'dependencies': {
                'maven': [
                    {'name': 'junit', 'version': '5.0.0'}
                ]
            },
            'documentation': ['README.md'],
            'api_docs': [],
            'code_examples': [],
            'todos': [],
            'license': 'Apache-2.0'
        }
        
        self.repo3 = {
            'name': 'Project Gamma',
            'path': '/test/gamma',
            'files_count': 200,
            'languages': {'JavaScript': 120, 'TypeScript': 80},
            'statistics': {
                'total_lines': 20000,
                'code_lines': 15000,
                'comment_lines': 3000,
                'blank_lines': 2000
            },
            'dependencies': {
                'npm': [
                    {'name': 'react', 'version': '18.0.0'},
                    {'name': 'express', 'version': '4.18.0'}
                ]
            },
            'documentation': ['README.md', 'CONTRIBUTING.md', 'LICENSE', 'CHANGELOG.md', 'CODE_OF_CONDUCT.md'],
            'api_docs': [{'name': 'api1'}, {'name': 'api2'}, {'name': 'api3'}],
            'code_examples': [{'file': 'example1.js'}, {'file': 'example2.js'}, {'file': 'example3.js'}],
            'todos': [
                {'file': 'server.js', 'line': 10, 'type': 'TODO', 'comment': 'Improve'},
                {'file': 'app.js', 'line': 20, 'type': 'FIXME', 'comment': 'Bug'}
            ],
            'license': 'MIT'
        }
    
    def test_initialization(self):
        """Test dashboard initialization."""
        dashboard = MultiRepoDashboard()
        self.assertIsNotNone(dashboard)
        self.assertEqual(len(dashboard.repositories), 0)
        self.assertEqual(dashboard.config.style_guide, "google")
    
    def test_custom_config(self):
        """Test dashboard with custom configuration."""
        config = DashboardConfig(
            style_guide="microsoft",
            min_doc_coverage=80.0,
            min_completeness_score=70.0,
            check_consistency=False
        )
        dashboard = MultiRepoDashboard(config)
        self.assertEqual(dashboard.config.style_guide, "microsoft")
        self.assertEqual(dashboard.config.min_doc_coverage, 80.0)
        self.assertFalse(dashboard.config.check_consistency)
    
    def test_add_repository(self):
        """Test adding repositories."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1)
        
        self.assertEqual(len(dashboard.repositories), 1)
        self.assertEqual(dashboard.repositories[0].name, 'Project Alpha')
    
    def test_add_multiple_repositories(self):
        """Test adding multiple repositories."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        dashboard.add_repository(self.repo3, "Gamma")
        
        self.assertEqual(len(dashboard.repositories), 3)
        self.assertEqual(dashboard.repositories[0].name, 'Alpha')
        self.assertEqual(dashboard.repositories[1].name, 'Beta')
        self.assertEqual(dashboard.repositories[2].name, 'Gamma')
    
    def test_doc_coverage_analysis(self):
        """Test documentation coverage analysis."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1)
        
        repo = dashboard.repositories[0]
        self.assertIn('coverage_percentage', repo.doc_coverage)
        self.assertTrue(repo.doc_coverage['has_readme'])
        self.assertTrue(repo.doc_coverage['has_license'])
        self.assertTrue(repo.doc_coverage['has_contributing'])
    
    def test_completeness_score(self):
        """Test completeness score calculation."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1)
        
        repo = dashboard.repositories[0]
        self.assertIn('percentage', repo.completeness_score)
        self.assertIn('grade', repo.completeness_score)
        self.assertIn('details', repo.completeness_score)
        self.assertGreater(repo.completeness_score['percentage'], 0)
    
    def test_style_compliance(self):
        """Test style guide compliance checking."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1)
        
        repo = dashboard.repositories[0]
        self.assertIn('compliance_percentage', repo.style_compliance)
        self.assertIn('style_guide', repo.style_compliance)
        self.assertEqual(repo.style_compliance['style_guide'], 'Google Developer Documentation Style Guide')
    
    def test_consistency_analysis(self):
        """Test consistency analysis across repositories."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")  # Less complete
        dashboard.add_repository(self.repo3, "Gamma")  # Most complete
        
        gaps = dashboard.analyze_consistency()
        
        self.assertIsInstance(gaps, list)
        # Should find gaps since repo2 is missing several docs
        self.assertGreater(len(gaps), 0)
    
    def test_coverage_consistency_gaps(self):
        """Test detection of coverage consistency gaps."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        dashboard.add_repository(self.repo3, "Gamma")
        
        gaps = dashboard._check_coverage_consistency()
        
        # Should detect coverage inconsistency
        self.assertIsInstance(gaps, list)
    
    def test_completeness_consistency_gaps(self):
        """Test detection of completeness consistency gaps."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        dashboard.add_repository(self.repo3, "Gamma")
        
        gaps = dashboard._check_completeness_consistency()
        
        self.assertIsInstance(gaps, list)
    
    def test_structural_consistency_gaps(self):
        """Test detection of structural consistency gaps."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        
        gaps = dashboard._check_structural_consistency()
        
        # Should find missing CONTRIBUTING in Beta
        self.assertIsInstance(gaps, list)
        contributing_gaps = [g for g in gaps if 'CONTRIBUTING' in g.description]
        self.assertGreater(len(contributing_gaps), 0)
    
    def test_generate_analytics(self):
        """Test analytics generation."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        dashboard.add_repository(self.repo3, "Gamma")
        
        analytics = dashboard.generate_analytics()
        
        self.assertIn('summary', analytics)
        self.assertIn('trends', analytics)
        self.assertIn('rankings', analytics)
        self.assertIn('recommendations', analytics)
        self.assertEqual(analytics['total_repositories'], 3)
    
    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        
        summary = dashboard._calculate_summary_stats()
        
        self.assertIn('documentation_coverage', summary)
        self.assertIn('completeness_score', summary)
        self.assertIn('style_compliance', summary)
        self.assertIn('average', summary['documentation_coverage'])
        self.assertIn('min', summary['documentation_coverage'])
        self.assertIn('max', summary['documentation_coverage'])
    
    def test_rankings(self):
        """Test repository rankings."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        dashboard.add_repository(self.repo3, "Gamma")
        
        analytics = dashboard.generate_analytics()
        rankings = analytics['rankings']
        
        self.assertIn('by_coverage', rankings)
        self.assertIn('by_completeness', rankings)
        self.assertIn('by_compliance', rankings)
        self.assertIn('overall', rankings)
        
        # Check that rankings are sorted correctly
        overall = rankings['overall']
        self.assertEqual(len(overall), 3)
        for i in range(len(overall) - 1):
            self.assertGreaterEqual(overall[i]['score'], overall[i+1]['score'])
    
    def test_recommendations(self):
        """Test recommendation generation."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        
        analytics = dashboard.generate_analytics()
        recommendations = analytics['recommendations']
        
        self.assertIsInstance(recommendations, list)
        # Should have some recommendations
        self.assertGreater(len(recommendations), 0)
    
    def test_text_report_generation(self):
        """Test text format report generation."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        
        report = dashboard.generate_report('text')
        
        self.assertIsInstance(report, str)
        self.assertIn('MULTI-REPOSITORY DOCUMENTATION CONSISTENCY DASHBOARD', report)
        self.assertIn('Alpha', report)
        self.assertIn('Beta', report)
    
    def test_markdown_report_generation(self):
        """Test markdown format report generation."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        
        report = dashboard.generate_report('markdown')
        
        self.assertIsInstance(report, str)
        self.assertIn('# Multi-Repository Documentation Consistency Dashboard', report)
        self.assertIn('##', report)  # Should have headers
        self.assertIn('|', report)   # Should have tables
    
    def test_html_report_generation(self):
        """Test HTML format report generation."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        
        report = dashboard.generate_report('html')
        
        self.assertIsInstance(report, str)
        self.assertIn('<!DOCTYPE html>', report)
        self.assertIn('<html>', report)
        self.assertIn('</html>', report)
    
    def test_json_export(self):
        """Test JSON export."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        
        json_str = dashboard.export_to_json()
        
        self.assertIsInstance(json_str, str)
        data = json.loads(json_str)
        
        self.assertIn('dashboard_config', data)
        self.assertIn('repositories', data)
        self.assertIn('consistency_gaps', data)
        self.assertIn('analytics', data)
        self.assertEqual(len(data['repositories']), 2)
    
    def test_json_export_to_file(self):
        """Test JSON export to file."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'dashboard.json')
            dashboard.export_to_json(output_path)
            
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            self.assertIn('repositories', data)
    
    def test_score_to_grade(self):
        """Test score to grade conversion."""
        dashboard = MultiRepoDashboard()
        
        self.assertEqual(dashboard._score_to_grade(95), 'A')
        self.assertEqual(dashboard._score_to_grade(85), 'B')
        self.assertEqual(dashboard._score_to_grade(75), 'C')
        self.assertEqual(dashboard._score_to_grade(65), 'D')
        self.assertEqual(dashboard._score_to_grade(55), 'F')
    
    def test_consistency_gap_severity(self):
        """Test consistency gap severity levels."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        dashboard.add_repository(self.repo2, "Beta")
        
        gaps = dashboard.analyze_consistency()
        
        # Check that gaps have severity levels
        for gap in gaps:
            self.assertIn(gap.severity, ['critical', 'high', 'medium', 'low'])
    
    def test_missing_documentation_detection(self):
        """Test detection of missing documentation."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo2, "Beta")  # Has minimal docs
        
        repo = dashboard.repositories[0]
        missing = repo.doc_coverage['missing_docs']
        
        self.assertIsInstance(missing, list)
        # Should identify missing CONTRIBUTING
        self.assertTrue(any('CONTRIBUTING' in doc for doc in missing))
    
    def test_health_metrics_integration(self):
        """Test integration with health metrics."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1, "Alpha")
        
        repo = dashboard.repositories[0]
        
        self.assertIn('overall_health', repo.health_metrics)
        self.assertIn('documentation_coverage', repo.health_metrics)
        self.assertIn('code_quality', repo.health_metrics)
    
    def test_different_style_guides(self):
        """Test different style guides."""
        # Test Google style guide
        config_google = DashboardConfig(style_guide="google")
        dashboard_google = MultiRepoDashboard(config_google)
        self.assertIn('Google', dashboard_google.style_guide.name)
        
        # Test Microsoft style guide
        config_ms = DashboardConfig(style_guide="microsoft")
        dashboard_ms = MultiRepoDashboard(config_ms)
        self.assertIn('Microsoft', dashboard_ms.style_guide.name)
        
        # Test Plain Language guide
        config_plain = DashboardConfig(style_guide="plain")
        dashboard_plain = MultiRepoDashboard(config_plain)
        self.assertIn('Plain', dashboard_plain.style_guide.name)
    
    def test_no_repositories(self):
        """Test dashboard with no repositories."""
        dashboard = MultiRepoDashboard()
        
        report = dashboard.generate_report('text')
        self.assertIn('No repositories', report)
        
        gaps = dashboard.analyze_consistency()
        self.assertEqual(len(gaps), 0)
    
    def test_single_repository(self):
        """Test dashboard with single repository."""
        dashboard = MultiRepoDashboard()
        dashboard.add_repository(self.repo1)
        
        # Should not find consistency gaps with only 1 repo
        gaps = dashboard.analyze_consistency()
        self.assertEqual(len(gaps), 0)
    
    def test_membership_integration(self):
        """Test membership system integration."""
        from accudoc.membership import MembershipManager
        
        # Create a temporary membership database
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'membership.db'
            membership = MembershipManager(db_path)
            
            # Create a test user
            user = membership.create_user('testuser', 'test@example.com', 'password123')
            
            # Create dashboard with membership
            config = DashboardConfig(require_membership=True)
            dashboard = MultiRepoDashboard(config, membership)
            
            # Check access
            from accudoc.membership import Permission
            has_access = dashboard.check_access(user.user_id, Permission.READ)
            self.assertTrue(has_access)
            
            # Clean up
            membership.close()


def run_tests():
    """Run all tests with detailed output."""
    print("=" * 60)
    print("Testing Multi-Repository Documentation Dashboard")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMultiRepoDashboard)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
