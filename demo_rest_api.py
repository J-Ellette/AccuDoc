#!/usr/bin/env python3
"""
Demo script for REST API feature.
Shows how to use the AccuDoc REST API.
"""

import requests
import json
import time
import subprocess
import sys
import os


def demo_rest_api():
    """Demonstrate REST API feature."""
    print("=" * 70)
    print("AccuDoc - REST API Demo")
    print("=" * 70)
    print()
    
    # Check if Flask is available
    try:
        from accudoc.rest_api import is_flask_available
        if not is_flask_available():
            print("✗ Flask is not installed")
            print("Install it with: pip install flask flask-cors")
            return
    except ImportError:
        print("✗ Flask is not installed")
        print("Install it with: pip install flask flask-cors")
        return
    
    print("Note: This demo shows example API calls.")
    print("To actually test the API, run:")
    print("  python accudoc_cli.py api")
    print()
    print("Then in another terminal, use curl or a REST client to test endpoints.")
    print()
    
    # Show CLI usage
    print("=" * 70)
    print("Starting the API Server")
    print("=" * 70)
    print()
    print("# Start API server on default port (5000)")
    print("python accudoc_cli.py api")
    print()
    print("# Start on custom port")
    print("python accudoc_cli.py api --port 8080")
    print()
    print("# Start with debug mode")
    print("python accudoc_cli.py api --debug")
    print()
    print("# Bind to all interfaces")
    print("python accudoc_cli.py api --host 0.0.0.0 --port 5000")
    print()
    
    # Show example API calls
    print("=" * 70)
    print("Example API Calls (using curl)")
    print("=" * 70)
    print()
    
    print("# 1. Get API information")
    print("curl http://localhost:5000/")
    print()
    
    print("# 2. Health check")
    print("curl http://localhost:5000/health")
    print()
    
    print("# 3. Get API documentation")
    print("curl http://localhost:5000/api/docs")
    print()
    
    print("# 4. Scan a repository")
    print("curl -X POST http://localhost:5000/api/scan \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"path\": \"/path/to/repo\"}'")
    print()
    
    print("# 5. Generate documentation")
    print("curl -X POST http://localhost:5000/api/generate \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"scan_data\": {...}, \"language\": \"es\"}'")
    print()
    
    print("# 6. Export documentation (scan + generate)")
    print("curl -X POST http://localhost:5000/api/export \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"path\": \"/path/to/repo\", \"language\": \"en\"}'")
    print()
    
    print("# 7. Get health metrics")
    print("curl -X POST http://localhost:5000/api/health-metrics \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"path\": \"/path/to/repo\"}'")
    print()
    
    print("# 8. Get repository trends")
    print("curl -X POST http://localhost:5000/api/trends \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"path\": \"/path/to/repo\", \"period\": \"month\"}'")
    print()
    
    print("# 9. Compare repositories")
    print("curl -X POST http://localhost:5000/api/compare \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"repositories\": [\"repo1\", \"repo2\"]}'")
    print()
    
    print("# 10. Generate custom report")
    print("curl -X POST http://localhost:5000/api/custom-report \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"path\": \"/path/to/repo\", \"builtin\": \"executive\"}'")
    print()
    
    print("# 11. Export data")
    print("curl -X POST http://localhost:5000/api/data-export \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"path\": \"/path/to/repo\", \"format\": \"json\"}'")
    print()
    
    # Show Python examples
    print("=" * 70)
    print("Example API Calls (using Python requests)")
    print("=" * 70)
    print()
    
    print("import requests")
    print("import json")
    print()
    print("# Base URL")
    print("BASE_URL = 'http://localhost:5000'")
    print()
    print("# 1. Scan repository")
    print("response = requests.post(")
    print("    f'{BASE_URL}/api/scan',")
    print("    json={'path': '/path/to/repo'}")
    print(")")
    print("scan_data = response.json()['data']")
    print()
    print("# 2. Generate documentation")
    print("response = requests.post(")
    print("    f'{BASE_URL}/api/generate',")
    print("    json={")
    print("        'scan_data': scan_data,")
    print("        'language': 'es'")
    print("    }")
    print(")")
    print("docs = response.json()['content']")
    print()
    print("# 3. Get health metrics")
    print("response = requests.post(")
    print("    f'{BASE_URL}/api/health-metrics',")
    print("    json={'scan_data': scan_data}")
    print(")")
    print("health = response.json()['data']")
    print("print(f\"Overall score: {health['summary']['overall_score']}\")")
    print()
    
    # Show available endpoints
    print("=" * 70)
    print("Available API Endpoints")
    print("=" * 70)
    print()
    
    endpoints = {
        'GET /': 'API information',
        'GET /health': 'Health check',
        'GET /api/docs': 'API documentation (OpenAPI spec)',
        'POST /api/scan': 'Scan repository',
        'POST /api/generate': 'Generate documentation from scan data',
        'POST /api/export': 'Scan and generate documentation',
        'POST /api/health-metrics': 'Get repository health metrics',
        'POST /api/trends': 'Get repository trend analysis',
        'POST /api/compare': 'Compare multiple repositories',
        'POST /api/custom-report': 'Generate custom report',
        'POST /api/data-export': 'Export repository data'
    }
    
    for endpoint, description in endpoints.items():
        print(f"{endpoint:35s} - {description}")
    print()
    
    # Show features
    print("=" * 70)
    print("REST API Features")
    print("=" * 70)
    print()
    print("• RESTful design with JSON request/response")
    print("• CORS enabled for web clients")
    print("• Comprehensive error handling")
    print("• OpenAPI/Swagger documentation")
    print("• All AccuDoc features exposed via API:")
    print("  - Repository scanning")
    print("  - Documentation generation")
    print("  - Multi-language translation")
    print("  - Health metrics")
    print("  - Trend analysis")
    print("  - Repository comparisons")
    print("  - Custom reports")
    print("  - Data export")
    print()
    print("• Easy integration with:")
    print("  - Web applications")
    print("  - CI/CD pipelines")
    print("  - Monitoring tools")
    print("  - Custom automation scripts")
    print()
    
    # Show response format
    print("=" * 70)
    print("Example Response Format")
    print("=" * 70)
    print()
    print("Success response:")
    print(json.dumps({
        'success': True,
        'data': {
            'name': 'AccuDoc',
            'files_count': 100,
            'languages': {'Python': 80, 'JavaScript': 20}
        }
    }, indent=2))
    print()
    print("Error response:")
    print(json.dumps({
        'error': 'Missing required field: path'
    }, indent=2))
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("To start the API server:")
    print("  python accudoc_cli.py api")
    print()
    print("Then access the API at: http://localhost:5000")
    print("API documentation at: http://localhost:5000/api/docs")
    print()


if __name__ == '__main__':
    demo_rest_api()
