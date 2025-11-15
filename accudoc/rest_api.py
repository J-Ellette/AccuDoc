"""
REST API module for AccuDoc.
Exposes AccuDoc functionality via RESTful API.
"""

try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    CORS = None

from functools import wraps
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


def require_flask(func):
    """Decorator to check if Flask is available."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not FLASK_AVAILABLE:
            raise ImportError(
                "Flask is required for REST API functionality. "
                "Install it with: pip install flask flask-cors"
            )
        return func(*args, **kwargs)
    return wrapper


@require_flask
def create_app(config: Optional[Dict[str, Any]] = None):
    """
    Create and configure Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Default configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    app.config['JSON_SORT_KEYS'] = False
    
    # Apply custom configuration
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app)
    
    # Register routes
    register_routes(app)
    
    return app


def register_routes(app):
    """Register all API routes."""
    
    @app.route('/')
    def index():
        """API root - returns API info."""
        return jsonify({
            'name': 'AccuDoc REST API',
            'version': '1.0.0',
            'description': 'RESTful API for automated repository documentation',
            'endpoints': {
                'GET /': 'API information',
                'GET /health': 'API health check',
                'GET /api/docs': 'API documentation',
                'POST /api/scan': 'Scan repository',
                'POST /api/generate': 'Generate documentation',
                'POST /api/export': 'Export documentation',
                'POST /api/health-metrics': 'Get repository health metrics',
                'POST /api/trends': 'Get repository trends',
                'POST /api/compare': 'Compare repositories',
                'POST /api/custom-report': 'Generate custom report',
                'POST /api/data-export': 'Export repository data',
                'POST /api/collaborate/session': 'Create collaborative session',
                'POST /api/collaborate/session/<id>/join': 'Join session',
                'POST /api/collaborate/session/<id>/edit': 'Apply edit operation',
                'GET /api/collaborate/session/<id>/content': 'Get session content',
                'POST /api/collaborate/session/<id>/comment': 'Add comment',
                'POST /api/collaborate/session/<id>/suggest': 'Add suggestion',
                'POST /api/user/login': 'Authenticate user',
                'POST /api/user/create': 'Create new user'
            }
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'AccuDoc API'
        })
    
    @app.route('/api/docs')
    def api_docs():
        """API documentation endpoint."""
        return jsonify({
            'openapi': '3.0.0',
            'info': {
                'title': 'AccuDoc REST API',
                'version': '1.0.0',
                'description': 'RESTful API for automated repository documentation'
            },
            'paths': {
                '/api/scan': {
                    'post': {
                        'summary': 'Scan repository',
                        'requestBody': {
                            'required': True,
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'path': {'type': 'string', 'description': 'Repository path'}
                                        },
                                        'required': ['path']
                                    }
                                }
                            }
                        },
                        'responses': {
                            '200': {'description': 'Repository scan results'}
                        }
                    }
                },
                '/api/health-metrics': {
                    'post': {
                        'summary': 'Get repository health metrics',
                        'requestBody': {
                            'required': True,
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'path': {'type': 'string'},
                                            'scan_data': {'type': 'object'}
                                        }
                                    }
                                }
                            }
                        },
                        'responses': {
                            '200': {'description': 'Health metrics'}
                        }
                    }
                }
            }
        })
    
    @app.route('/api/scan', methods=['POST'])
    def scan_repository():
        """Scan a repository."""
        try:
            data = request.get_json()
            
            if not data or 'path' not in data:
                return jsonify({'error': 'Missing required field: path'}), 400
            
            repo_path = data['path']
            
            if not os.path.exists(repo_path):
                return jsonify({'error': f'Repository path not found: {repo_path}'}), 404
            
            # Import scanner
            from accudoc.scanner import RepositoryScanner
            
            scanner = RepositoryScanner(repo_path)
            scan_result = scanner.scan()
            
            return jsonify({
                'success': True,
                'data': scan_result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/generate', methods=['POST'])
    def generate_documentation():
        """Generate documentation from scan data."""
        try:
            data = request.get_json()
            
            if not data or 'scan_data' not in data:
                return jsonify({'error': 'Missing required field: scan_data'}), 400
            
            scan_data = data['scan_data']
            format_type = data.get('format', 'markdown')
            language = data.get('language', 'en')
            
            # Import generator and translator
            from accudoc.generator import DocumentGenerator
            
            generator = DocumentGenerator(scan_data)
            content = generator.generate_all()
            
            # Translate if needed
            if language != 'en':
                from accudoc.doc_translator import DocumentTranslator
                translator = DocumentTranslator(language)
                content = translator.translate(content)
            
            return jsonify({
                'success': True,
                'content': content
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/export', methods=['POST'])
    def export_documentation():
        """Export documentation to file."""
        try:
            data = request.get_json()
            
            if not data or 'path' not in data:
                return jsonify({'error': 'Missing required field: path'}), 400
            
            repo_path = data['path']
            format_type = data.get('format', 'markdown')
            language = data.get('language', 'en')
            
            # Import required modules
            from accudoc.scanner import RepositoryScanner
            from accudoc.generator import DocumentGenerator
            
            # Scan repository
            scanner = RepositoryScanner(repo_path)
            scan_data = scanner.scan()
            
            # Generate documentation
            generator = DocumentGenerator(scan_data)
            content = generator.generate_all()
            
            # Translate if needed
            if language != 'en':
                from accudoc.doc_translator import DocumentTranslator
                translator = DocumentTranslator(language)
                content = translator.translate(content)
            
            return jsonify({
                'success': True,
                'content': content,
                'scan_data': scan_data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health-metrics', methods=['POST'])
    def get_health_metrics():
        """Get repository health metrics."""
        try:
            data = request.get_json()
            
            # Get scan data from request or scan path
            if 'scan_data' in data:
                scan_data = data['scan_data']
            elif 'path' in data:
                from accudoc.scanner import RepositoryScanner
                scanner = RepositoryScanner(data['path'])
                scan_data = scanner.scan()
            else:
                return jsonify({'error': 'Missing scan_data or path'}), 400
            
            # Import health dashboard
            from accudoc.health_dashboard import HealthMetrics
            
            metrics = HealthMetrics(scan_data)
            
            format_type = data.get('format', 'json')
            
            if format_type == 'json':
                result = {
                    'metrics': metrics.get_metrics(),
                    'summary': metrics.get_summary()
                }
            else:
                from accudoc.health_dashboard import HealthDashboard
                dashboard = HealthDashboard(scan_data)
                result = dashboard.generate_text_dashboard()
            
            return jsonify({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/trends', methods=['POST'])
    def get_trends():
        """Get repository trend analysis."""
        try:
            data = request.get_json()
            
            if not data or 'path' not in data:
                return jsonify({'error': 'Missing required field: path'}), 400
            
            repo_path = data['path']
            period = data.get('period', 'month')
            intervals = data.get('intervals', 10)
            
            # Import trend analysis
            from accudoc.trend_analysis import TrendAnalyzer
            
            analyzer = TrendAnalyzer(repo_path)
            trends = analyzer.analyze(period=period, intervals=intervals)
            
            return jsonify({
                'success': True,
                'data': trends
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/compare', methods=['POST'])
    def compare_repositories():
        """Compare multiple repositories."""
        try:
            data = request.get_json()
            
            if not data or 'repositories' not in data:
                return jsonify({'error': 'Missing required field: repositories'}), 400
            
            repositories = data['repositories']
            names = data.get('names', [])
            
            if len(repositories) < 2:
                return jsonify({'error': 'At least 2 repositories required'}), 400
            
            # Import comparison
            from accudoc.comparison_reports import RepositoryComparison
            from accudoc.scanner import RepositoryScanner
            
            comparison = RepositoryComparison()
            
            # Add repositories
            for i, repo in enumerate(repositories):
                if isinstance(repo, str):
                    # Path to repository
                    if repo.endswith('.json'):
                        comparison.load_from_json(repo)
                    else:
                        scanner = RepositoryScanner(repo)
                        scan_data = scanner.scan()
                        name = names[i] if i < len(names) else None
                        comparison.add_repository(scan_data, name=name)
                else:
                    # Scan data object
                    name = names[i] if i < len(names) else None
                    comparison.add_repository(repo, name=name)
            
            # Perform comparison
            result = comparison.compare()
            
            return jsonify({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/custom-report', methods=['POST'])
    def generate_custom_report():
        """Generate custom report."""
        try:
            data = request.get_json()
            
            # Get scan data
            if 'scan_data' in data:
                scan_data = data['scan_data']
            elif 'path' in data:
                from accudoc.scanner import RepositoryScanner
                scanner = RepositoryScanner(data['path'])
                scan_data = scanner.scan()
            else:
                return jsonify({'error': 'Missing scan_data or path'}), 400
            
            # Import custom reports
            from accudoc.custom_reports import CustomReportGenerator, ReportTemplate
            
            generator = CustomReportGenerator(scan_data)
            
            # Get template
            if 'template' in data:
                template = ReportTemplate(data['template'])
            elif 'builtin' in data:
                template = generator.get_builtin_template(data['builtin'])
            else:
                template = generator.get_builtin_template('minimal')
            
            # Generate report
            report = generator.generate(template)
            
            return jsonify({
                'success': True,
                'report': report
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/data-export', methods=['POST'])
    def export_data():
        """Export repository data."""
        try:
            data = request.get_json()
            
            # Get scan data
            if 'scan_data' in data:
                scan_data = data['scan_data']
            elif 'path' in data:
                from accudoc.scanner import RepositoryScanner
                scanner = RepositoryScanner(data['path'])
                scan_data = scanner.scan()
            else:
                return jsonify({'error': 'Missing scan_data or path'}), 400
            
            # Import data export
            from accudoc.data_export import DataExporter
            
            exporter = DataExporter(scan_data)
            format_type = data.get('format', 'json')
            
            if format_type == 'json':
                # Return the repository data as JSON
                result = exporter.repo_info
            elif format_type == 'summary':
                result = exporter.generate_summary()
            else:
                return jsonify({'error': f'Unsupported format: {format_type}'}), 400
            
            return jsonify({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Collaborative endpoints
    @app.route('/api/collaborate/session', methods=['POST'])
    def create_collaborative_session():
        """Create a new collaborative session."""
        try:
            from accudoc.collaboration import CollaborationManager
            from accudoc.membership import MembershipManager
            from accudoc.project_database import ProjectDatabase
            
            data = request.json
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Verify authentication
            membership_mgr = MembershipManager()
            user_id = membership_mgr.verify_api_token(token) if token else None
            
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            # Create session
            collab_mgr = CollaborationManager()
            session = collab_mgr.create_session(
                project_id=data['project_id'],
                document_path=data['document_path'],
                created_by=user_id,
                initial_content=data.get('content', '')
            )
            
            # Add to project database
            db = ProjectDatabase()
            db.add_collaborative_session(
                session_id=session.session_id,
                project_id=data['project_id'],
                document_path=data['document_path'],
                created_by=user_id
            )
            
            collab_mgr.close()
            db.close()
            membership_mgr.close()
            
            return jsonify({
                'success': True,
                'session_id': session.session_id,
                'status': session.status.value
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/collaborate/session/<session_id>/join', methods=['POST'])
    def join_collaborative_session(session_id):
        """Join a collaborative session."""
        try:
            from accudoc.collaboration import CollaborationManager
            from accudoc.membership import MembershipManager
            
            data = request.json
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Verify authentication
            membership_mgr = MembershipManager()
            user_id = membership_mgr.verify_api_token(token) if token else None
            
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            user = membership_mgr.get_user(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Join session
            collab_mgr = CollaborationManager()
            result = collab_mgr.join_session(session_id, user_id, user.username)
            
            collab_mgr.close()
            membership_mgr.close()
            
            return jsonify({
                'success': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/collaborate/session/<session_id>/edit', methods=['POST'])
    def apply_collaborative_edit(session_id):
        """Apply an edit operation to a session."""
        try:
            from accudoc.collaboration import CollaborationManager
            from accudoc.membership import MembershipManager
            from accudoc.crdt import OperationType
            
            data = request.json
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Verify authentication
            membership_mgr = MembershipManager()
            user_id = membership_mgr.verify_api_token(token) if token else None
            
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            # Apply operation
            collab_mgr = CollaborationManager()
            operation = collab_mgr.apply_operation(
                session_id=session_id,
                user_id=user_id,
                op_type=OperationType(data['op_type']),
                position=data['position'],
                content=data.get('content', ''),
                length=data.get('length', 0)
            )
            
            collab_mgr.close()
            membership_mgr.close()
            
            if operation:
                return jsonify({
                    'success': True,
                    'op_id': operation.op_id
                })
            else:
                return jsonify({'error': 'Failed to apply operation'}), 400
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/collaborate/session/<session_id>/content', methods=['GET'])
    def get_session_content(session_id):
        """Get current content of a collaborative session."""
        try:
            from accudoc.collaboration import CollaborationManager
            from accudoc.membership import MembershipManager
            
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Verify authentication
            membership_mgr = MembershipManager()
            user_id = membership_mgr.verify_api_token(token) if token else None
            
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            # Get content
            collab_mgr = CollaborationManager()
            content = collab_mgr.get_session_content(session_id)
            
            collab_mgr.close()
            membership_mgr.close()
            
            if content is not None:
                return jsonify({
                    'success': True,
                    'content': content
                })
            else:
                return jsonify({'error': 'Session not found'}), 404
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/collaborate/session/<session_id>/comment', methods=['POST'])
    def add_session_comment(session_id):
        """Add a comment to a session."""
        try:
            from accudoc.collaboration import CollaborationManager
            from accudoc.membership import MembershipManager
            
            data = request.json
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Verify authentication
            membership_mgr = MembershipManager()
            user_id = membership_mgr.verify_api_token(token) if token else None
            
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            user = membership_mgr.get_user(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Add comment
            collab_mgr = CollaborationManager()
            comment_id = collab_mgr.add_comment(
                session_id=session_id,
                user_id=user_id,
                username=user.username,
                content=data['content'],
                position=data.get('position')
            )
            
            collab_mgr.close()
            membership_mgr.close()
            
            return jsonify({
                'success': True,
                'comment_id': comment_id
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/collaborate/session/<session_id>/suggest', methods=['POST'])
    def add_session_suggestion(session_id):
        """Add a change suggestion to a session."""
        try:
            from accudoc.collaboration import CollaborationManager
            from accudoc.membership import MembershipManager
            
            data = request.json
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Verify authentication
            membership_mgr = MembershipManager()
            user_id = membership_mgr.verify_api_token(token) if token else None
            
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            user = membership_mgr.get_user(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Add suggestion
            collab_mgr = CollaborationManager()
            suggestion_id = collab_mgr.add_suggestion(
                session_id=session_id,
                user_id=user_id,
                username=user.username,
                position=data['position'],
                suggested_text=data['suggested_text'],
                original_text=data.get('original_text'),
                reason=data.get('reason')
            )
            
            collab_mgr.close()
            membership_mgr.close()
            
            return jsonify({
                'success': True,
                'suggestion_id': suggestion_id
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/login', methods=['POST'])
    def user_login():
        """Authenticate a user and return API token."""
        try:
            from accudoc.membership import MembershipManager
            
            data = request.json
            membership_mgr = MembershipManager()
            
            # Authenticate user
            user = membership_mgr.authenticate_user(
                username=data['username'],
                password=data['password']
            )
            
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Create API token
            token = membership_mgr.create_api_token(
                user_id=user.user_id,
                name='API Access',
                expires_in_days=data.get('token_expires_days', 30)
            )
            
            membership_mgr.close()
            
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/create', methods=['POST'])
    def create_user():
        """Create a new user."""
        try:
            from accudoc.membership import MembershipManager, Role
            
            data = request.json
            membership_mgr = MembershipManager()
            
            # Create user
            user = membership_mgr.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                role=Role(data.get('role', 'viewer'))
            )
            
            membership_mgr.close()
            
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Register extended organization features
    try:
        from accudoc.rest_api_extended import register_extended_routes
        from accudoc.membership import MembershipManager
        
        membership_mgr = MembershipManager()
        register_extended_routes(app, membership_mgr)
    except ImportError:
        # Extended routes not available, skip
        pass


@require_flask
def run_server(host='127.0.0.1', port=5000, debug=False, config=None):
    """
    Run the API server.
    
    Args:
        host: Host address to bind to
        port: Port to listen on
        debug: Enable debug mode
        config: Optional configuration dictionary
    """
    app = create_app(config)
    app.run(host=host, port=port, debug=debug)


def is_flask_available():
    """Check if Flask is available."""
    return FLASK_AVAILABLE
