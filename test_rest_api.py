"""
Test suite for REST API feature.
"""

import unittest
import json
import sys

# Check if Flask is available
try:
    from accudoc.rest_api import create_app, is_flask_available
    FLASK_AVAILABLE = is_flask_available()
except ImportError:
    FLASK_AVAILABLE = False


@unittest.skipIf(not FLASK_AVAILABLE, "Flask not available")
class TestRestAPI(unittest.TestCase):
    """Test cases for REST API."""
    
    def setUp(self):
        """Set up test client."""
        if FLASK_AVAILABLE:
            self.app = create_app({'TESTING': True})
            self.client = self.app.test_client()
    
    def test_index_endpoint(self):
        """Test index endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('name', data)
        self.assertIn('endpoints', data)
        self.assertEqual(data['name'], 'AccuDoc REST API')
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_api_docs_endpoint(self):
        """Test API documentation endpoint."""
        response = self.client.get('/api/docs')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('openapi', data)
        self.assertIn('paths', data)
    
    def test_scan_missing_path(self):
        """Test scan endpoint with missing path."""
        response = self.client.post(
            '/api/scan',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_scan_invalid_path(self):
        """Test scan endpoint with invalid path."""
        response = self.client.post(
            '/api/scan',
            data=json.dumps({'path': '/nonexistent/path'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_scan_valid_path(self):
        """Test scan endpoint with valid path."""
        response = self.client.post(
            '/api/scan',
            data=json.dumps({'path': '.'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_generate_missing_scan_data(self):
        """Test generate endpoint with missing scan data."""
        response = self.client.post(
            '/api/generate',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_generate_with_scan_data(self):
        """Test generate endpoint with scan data."""
        scan_data = {
            'name': 'TestProject',
            'path': '/test',
            'files_count': 10,
            'languages': {'Python': 10}
        }
        
        response = self.client.post(
            '/api/generate',
            data=json.dumps({'scan_data': scan_data}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('content', data)
    
    def test_export_missing_path(self):
        """Test export endpoint with missing path."""
        response = self.client.post(
            '/api/export',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_export_with_path(self):
        """Test export endpoint with path."""
        response = self.client.post(
            '/api/export',
            data=json.dumps({'path': '.'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('content', data)
        self.assertIn('scan_data', data)
    
    def test_health_metrics_missing_data(self):
        """Test health metrics endpoint with missing data."""
        response = self.client.post(
            '/api/health-metrics',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_health_metrics_with_scan_data(self):
        """Test health metrics endpoint with scan data."""
        scan_data = {
            'name': 'TestProject',
            'files_count': 100,
            'languages': {'Python': 70},
            'statistics': {
                'total_lines': 10000,
                'code_lines': 7000,
                'comment_lines': 2000
            },
            'dependencies': {},
            'documentation': ['README.md'],
            'todos': [],
            'license': 'MIT'
        }
        
        response = self.client.post(
            '/api/health-metrics',
            data=json.dumps({'scan_data': scan_data}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_trends_missing_path(self):
        """Test trends endpoint with missing path."""
        response = self.client.post(
            '/api/trends',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_compare_missing_repositories(self):
        """Test compare endpoint with missing repositories."""
        response = self.client.post(
            '/api/compare',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_compare_insufficient_repositories(self):
        """Test compare endpoint with insufficient repositories."""
        response = self.client.post(
            '/api/compare',
            data=json.dumps({'repositories': ['.']}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_custom_report_missing_data(self):
        """Test custom report endpoint with missing data."""
        response = self.client.post(
            '/api/custom-report',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_custom_report_with_scan_data(self):
        """Test custom report endpoint with scan data."""
        scan_data = {
            'name': 'TestProject',
            'path': '/test',
            'files_count': 10,
            'languages': {'Python': 10}
        }
        
        response = self.client.post(
            '/api/custom-report',
            data=json.dumps({'scan_data': scan_data}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('report', data)
    
    def test_data_export_missing_data(self):
        """Test data export endpoint with missing data."""
        response = self.client.post(
            '/api/data-export',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_data_export_with_scan_data(self):
        """Test data export endpoint with scan data."""
        scan_data = {
            'name': 'TestProject',
            'files_count': 10,
            'languages': {'Python': 10}
        }
        
        response = self.client.post(
            '/api/data-export',
            data=json.dumps({'scan_data': scan_data}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_404_endpoint(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)


def run_tests():
    """Run all tests and print results."""
    print("=" * 60)
    print("Testing REST API Feature")
    print("=" * 60)
    
    if not FLASK_AVAILABLE:
        print("\n⚠ Flask not available - skipping REST API tests")
        print("Install Flask with: pip install flask flask-cors")
        print("=" * 60)
        return 0
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRestAPI)
    
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
