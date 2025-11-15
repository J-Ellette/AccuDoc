"""
Extended REST API for AccuDoc with microservice documentation endpoints.

Provides fine-grained API access to documentation sections with role-based
access control, rate limiting, and usage auditing.
"""

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from functools import wraps
import time
from collections import defaultdict
from typing import Dict, Any, Optional, Callable
import hashlib
import json

from accudoc.membership import MembershipManager, Permission
from accudoc.glossary import GlossaryManager
from accudoc.onboarding_generator import OnboardingGenerator
from accudoc.document_sharing import DocumentSharingManager
from accudoc.license_management import LicenseManagementToolkit


class RateLimiter:
    """Simple rate limiter for API endpoints."""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute per client
        """
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed for client.
        
        Args:
            client_id: Client identifier (IP, user ID, API token)
            
        Returns:
            True if request is allowed
        """
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True


def require_auth(membership_manager: MembershipManager):
    """Decorator to require authentication."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for API token in header
            token = request.headers.get('X-API-Token')
            
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Verify token
            user_id = membership_manager.verify_api_token(token)
            
            if not user_id:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add user_id to request context
            request.user_id = user_id
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_permission(membership_manager: MembershipManager, permission: Permission):
    """Decorator to require specific permission."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(request, 'user_id', None)
            
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get organization/project from request
            data = request.get_json() or {}
            org_id = data.get('organization_id') or data.get('project_id')
            
            if not org_id:
                return jsonify({'error': 'organization_id or project_id required'}), 400
            
            # Check permission
            if not membership_manager.check_permission(user_id, org_id, permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def rate_limit(limiter: RateLimiter):
    """Decorator to apply rate limiting."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP or user_id as client identifier
            client_id = getattr(request, 'user_id', None) or request.remote_addr
            
            if not limiter.is_allowed(client_id):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': limiter.requests_per_minute,
                    'window': '1 minute'
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def register_extended_routes(app, membership_manager: MembershipManager):
    """
    Register extended API routes.
    
    Args:
        app: Flask application
        membership_manager: Membership manager instance
    """
    # Initialize managers
    glossary_mgr = GlossaryManager(membership_manager=membership_manager)
    onboarding_mgr = OnboardingGenerator(membership_manager=membership_manager)
    sharing_mgr = DocumentSharingManager(membership_manager=membership_manager)
    license_mgr = LicenseManagementToolkit(membership_manager=membership_manager)
    
    # Initialize rate limiter (60 requests per minute by default)
    limiter = RateLimiter(requests_per_minute=60)
    
    # Glossary endpoints
    @app.route('/api/glossary/terms', methods=['GET'])
    @rate_limit(limiter)
    def get_glossary_terms():
        """Get glossary terms for organization."""
        org_id = request.args.get('organization_id')
        
        terms = glossary_mgr.get_terms(org_id)
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'term_id': t.term_id,
                    'term': t.term,
                    'definition': t.definition,
                    'preferred_usage': t.preferred_usage,
                    'category': t.category
                } for t in terms
            ]
        })
    
    @app.route('/api/glossary/terms', methods=['POST'])
    @rate_limit(limiter)
    @require_auth(membership_manager)
    @require_permission(membership_manager, Permission.WRITE)
    def add_glossary_term():
        """Add a new glossary term."""
        data = request.get_json()
        
        required_fields = ['term', 'definition', 'preferred_usage']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        term = glossary_mgr.add_term(
            term=data['term'],
            definition=data['definition'],
            preferred_usage=data['preferred_usage'],
            aliases=data.get('aliases'),
            deprecated_terms=data.get('deprecated_terms'),
            category=data.get('category'),
            organization_id=data.get('organization_id'),
            user_id=request.user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'term_id': term.term_id,
                'term': term.term
            }
        }), 201
    
    @app.route('/api/glossary/scan', methods=['POST'])
    @rate_limit(limiter)
    def scan_with_glossary():
        """Scan content for glossary violations."""
        data = request.get_json()
        
        if 'content' not in data:
            return jsonify({'error': 'Missing content field'}), 400
        
        violations = glossary_mgr.scan_content(
            content=data['content'],
            organization_id=data.get('organization_id')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'total_violations': len(violations),
                'violations': [
                    {
                        'term': v.term,
                        'preferred': v.preferred,
                        'line_number': v.line_number,
                        'severity': v.severity,
                        'category': v.category
                    } for v in violations
                ]
            }
        })
    
    # Onboarding endpoints
    @app.route('/api/onboarding/checklists', methods=['POST'])
    @rate_limit(limiter)
    @require_auth(membership_manager)
    def create_onboarding_checklist():
        """Create an onboarding checklist."""
        data = request.get_json()
        
        if 'repository_path' not in data or 'repo_info' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        checklist = onboarding_mgr.create_checklist(
            repository_path=data['repository_path'],
            repo_info=data['repo_info'],
            title=data.get('title'),
            organization_id=data.get('organization_id'),
            user_id=request.user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'checklist_id': checklist.checklist_id,
                'title': checklist.title,
                'total_steps': len(checklist.steps) if checklist.steps else 0,
                'total_time': checklist.total_time
            }
        }), 201
    
    @app.route('/api/onboarding/checklists/<checklist_id>', methods=['GET'])
    @rate_limit(limiter)
    def get_onboarding_checklist(checklist_id: str):
        """Get an onboarding checklist."""
        checklist = onboarding_mgr.get_checklist(checklist_id)
        
        if not checklist:
            return jsonify({'error': 'Checklist not found'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'checklist_id': checklist.checklist_id,
                'title': checklist.title,
                'description': checklist.description,
                'total_time': checklist.total_time,
                'steps': [
                    {
                        'step_id': s.step_id,
                        'title': s.title,
                        'description': s.description,
                        'category': s.category,
                        'required': s.required,
                        'estimated_time': s.estimated_time
                    } for s in (checklist.steps or [])
                ]
            }
        })
    
    @app.route('/api/onboarding/checklists/<checklist_id>/markdown', methods=['GET'])
    @rate_limit(limiter)
    def get_checklist_markdown(checklist_id: str):
        """Get checklist as markdown."""
        checklist = onboarding_mgr.get_checklist(checklist_id)
        
        if not checklist:
            return jsonify({'error': 'Checklist not found'}), 404
        
        markdown = onboarding_mgr.generate_markdown_guide(checklist)
        
        return jsonify({
            'success': True,
            'data': {
                'markdown': markdown
            }
        })
    
    # Document sharing endpoints
    @app.route('/api/sharing/share', methods=['POST'])
    @rate_limit(limiter)
    @require_auth(membership_manager)
    def share_document():
        """Share a document section."""
        data = request.get_json()
        
        required_fields = ['document_path', 'content']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        shared_doc = sharing_mgr.share_document_section(
            document_path=data['document_path'],
            content=data['content'],
            shared_by=request.user_id,
            section_id=data.get('section_id'),
            section_title=data.get('section_title'),
            shared_with=data.get('shared_with'),
            expires_in_days=data.get('expires_in_days'),
            watermark=data.get('watermark', False),
            download_limit=data.get('download_limit'),
            organization_id=data.get('organization_id')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'share_id': shared_doc.share_id,
                'access_token': shared_doc.access_token,
                'expires_at': shared_doc.expires_at,
                'access_url': f'/api/sharing/access/{shared_doc.access_token}'
            }
        }), 201
    
    @app.route('/api/sharing/access/<access_token>', methods=['GET'])
    @rate_limit(limiter)
    def access_shared_document(access_token: str):
        """Access a shared document."""
        shared_doc = sharing_mgr.get_shared_document(
            access_token=access_token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if not shared_doc:
            return jsonify({'error': 'Document not found or access expired'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'section_title': shared_doc.section_title,
                'content': shared_doc.content,
                'created_at': shared_doc.created_at,
                'download_count': shared_doc.download_count,
                'download_limit': shared_doc.download_limit
            }
        })
    
    @app.route('/api/sharing/shares/<share_id>/revoke', methods=['POST'])
    @rate_limit(limiter)
    @require_auth(membership_manager)
    def revoke_share(share_id: str):
        """Revoke a shared document."""
        try:
            success = sharing_mgr.revoke_share(share_id, request.user_id)
            
            if success:
                return jsonify({'success': True, 'message': 'Share revoked'})
            else:
                return jsonify({'error': 'Share not found'}), 404
                
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
    
    # License management endpoints
    @app.route('/api/license/headers', methods=['POST'])
    @rate_limit(limiter)
    @require_auth(membership_manager)
    @require_permission(membership_manager, Permission.WRITE)
    def create_copyright_header():
        """Create a copyright header template."""
        data = request.get_json()
        
        required_fields = ['organization', 'year', 'license_type']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        header = license_mgr.create_copyright_header(
            organization=data['organization'],
            year=data['year'],
            license_type=data['license_type'],
            file_patterns=data.get('file_patterns'),
            organization_id=data.get('organization_id'),
            user_id=request.user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'header_id': header.header_id,
                'header_text': header.header_text
            }
        }), 201
    
    @app.route('/api/license/headers/<header_id>/apply', methods=['POST'])
    @rate_limit(limiter)
    @require_auth(membership_manager)
    @require_permission(membership_manager, Permission.WRITE)
    def apply_copyright_headers(header_id: str):
        """Apply copyright headers to repository."""
        data = request.get_json()
        
        if 'repository_path' not in data:
            return jsonify({'error': 'Missing repository_path'}), 400
        
        results = license_mgr.bulk_apply_headers(
            repository_path=data['repository_path'],
            header_id=header_id
        )
        
        return jsonify({
            'success': True,
            'data': results
        })
    
    @app.route('/api/license/compliance', methods=['POST'])
    @rate_limit(limiter)
    def check_license_compliance():
        """Check license compliance for repository."""
        data = request.get_json()
        
        if 'repository_path' not in data:
            return jsonify({'error': 'Missing repository_path'}), 400
        
        results = license_mgr.check_license_compliance(data['repository_path'])
        
        return jsonify({
            'success': True,
            'data': results
        })
    
    @app.route('/api/license/attributions', methods=['POST'])
    @rate_limit(limiter)
    @require_auth(membership_manager)
    def add_attribution():
        """Add a third-party attribution."""
        data = request.get_json()
        
        required_fields = ['component_name', 'author', 'license']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        attribution = license_mgr.add_attribution(
            component_name=data['component_name'],
            author=data['author'],
            license=data['license'],
            source_url=data.get('source_url'),
            description=data.get('description'),
            required_notice=data.get('required_notice'),
            project_id=data.get('project_id')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'attribution_id': attribution.attribution_id
            }
        }), 201
    
    @app.route('/api/license/attributions/file', methods=['GET'])
    @rate_limit(limiter)
    def get_attribution_file():
        """Generate attribution file."""
        project_id = request.args.get('project_id')
        
        content = license_mgr.generate_attribution_file(project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'content': content
            }
        })
    
    return app
