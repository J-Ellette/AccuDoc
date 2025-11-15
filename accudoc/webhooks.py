"""
Webhook support module for AccuDoc.

Provides webhook handlers for auto-updating documentation when
repository changes occur. Supports GitHub and GitLab webhooks.
"""

import json
import logging
import hmac
import hashlib
from typing import Dict, Optional, Any, Callable
from pathlib import Path


class WebhookHandler:
    """Base webhook handler for processing repository events."""
    
    def __init__(self, secret: Optional[str] = None):
        """
        Initialize webhook handler.
        
        Args:
            secret: Webhook secret for signature verification
        """
        self.secret = secret
        self.logger = logging.getLogger('accudoc.webhooks')
        self.handlers = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Type of event (e.g., 'push', 'pull_request')
            handler: Function to call when event occurs
        """
        self.handlers[event_type] = handler
        self.logger.info(f"Registered handler for event: {event_type}")
    
    def verify_signature(self, payload: bytes, signature: str, algorithm: str = 'sha256') -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: Request payload
            signature: Provided signature
            algorithm: Hash algorithm (default: sha256)
            
        Returns:
            True if signature is valid
        """
        if not self.secret:
            self.logger.warning("No secret configured, skipping signature verification")
            return True
        
        try:
            if algorithm == 'sha256':
                expected = hmac.new(
                    self.secret.encode(),
                    payload,
                    hashlib.sha256
                ).hexdigest()
            elif algorithm == 'sha1':
                expected = hmac.new(
                    self.secret.encode(),
                    payload,
                    hashlib.sha1
                ).hexdigest()
            else:
                self.logger.error(f"Unsupported algorithm: {algorithm}")
                return False
            
            return hmac.compare_digest(signature, expected)
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False
    
    def process_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook event.
        
        Args:
            event_type: Type of event
            payload: Event payload
            
        Returns:
            Processing result
        """
        if event_type not in self.handlers:
            self.logger.warning(f"No handler registered for event: {event_type}")
            return {
                'status': 'ignored',
                'message': f'No handler for event type: {event_type}'
            }
        
        try:
            handler = self.handlers[event_type]
            result = handler(payload)
            self.logger.info(f"Successfully processed {event_type} event")
            return {
                'status': 'success',
                'event_type': event_type,
                'result': result
            }
        except Exception as e:
            self.logger.error(f"Error processing {event_type} event: {e}")
            return {
                'status': 'error',
                'event_type': event_type,
                'error': str(e)
            }


class GitHubWebhook(WebhookHandler):
    """GitHub-specific webhook handler."""
    
    def verify_github_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify GitHub webhook signature.
        
        Args:
            payload: Request payload
            signature: X-Hub-Signature-256 header value
            
        Returns:
            True if signature is valid
        """
        if not signature.startswith('sha256='):
            return False
        
        signature = signature.replace('sha256=', '')
        return self.verify_signature(payload, signature, 'sha256')
    
    def parse_github_event(self, headers: Dict[str, str], payload: Dict[str, Any]) -> tuple:
        """
        Parse GitHub webhook event.
        
        Args:
            headers: Request headers
            payload: Request payload
            
        Returns:
            Tuple of (event_type, event_data)
        """
        event_type = headers.get('X-GitHub-Event', 'unknown')
        
        event_data = {
            'repository': payload.get('repository', {}).get('full_name', ''),
            'ref': payload.get('ref', ''),
            'sender': payload.get('sender', {}).get('login', ''),
        }
        
        if event_type == 'push':
            event_data.update({
                'commits': payload.get('commits', []),
                'head_commit': payload.get('head_commit', {}),
                'branch': payload.get('ref', '').replace('refs/heads/', '')
            })
        elif event_type == 'pull_request':
            pr = payload.get('pull_request', {})
            event_data.update({
                'action': payload.get('action', ''),
                'number': pr.get('number', 0),
                'title': pr.get('title', ''),
                'base_branch': pr.get('base', {}).get('ref', ''),
                'head_branch': pr.get('head', {}).get('ref', '')
            })
        elif event_type == 'release':
            release = payload.get('release', {})
            event_data.update({
                'action': payload.get('action', ''),
                'tag': release.get('tag_name', ''),
                'name': release.get('name', '')
            })
        
        return event_type, event_data


class GitLabWebhook(WebhookHandler):
    """GitLab-specific webhook handler."""
    
    def verify_gitlab_token(self, provided_token: str) -> bool:
        """
        Verify GitLab webhook token.
        
        Args:
            provided_token: X-Gitlab-Token header value
            
        Returns:
            True if token is valid
        """
        if not self.secret:
            self.logger.warning("No secret token configured")
            return True
        
        return hmac.compare_digest(provided_token, self.secret)
    
    def parse_gitlab_event(self, headers: Dict[str, str], payload: Dict[str, Any]) -> tuple:
        """
        Parse GitLab webhook event.
        
        Args:
            headers: Request headers
            payload: Request payload
            
        Returns:
            Tuple of (event_type, event_data)
        """
        event_type = headers.get('X-Gitlab-Event', 'unknown').lower().replace(' hook', '')
        
        event_data = {
            'project': payload.get('project', {}).get('path_with_namespace', ''),
            'user': payload.get('user_name', ''),
        }
        
        if event_type == 'push':
            event_data.update({
                'ref': payload.get('ref', ''),
                'commits': payload.get('commits', []),
                'branch': payload.get('ref', '').replace('refs/heads/', '')
            })
        elif event_type == 'merge_request':
            mr = payload.get('object_attributes', {})
            event_data.update({
                'action': mr.get('action', ''),
                'iid': mr.get('iid', 0),
                'title': mr.get('title', ''),
                'source_branch': mr.get('source_branch', ''),
                'target_branch': mr.get('target_branch', '')
            })
        elif event_type == 'tag_push':
            event_data.update({
                'ref': payload.get('ref', ''),
                'tag': payload.get('ref', '').replace('refs/tags/', '')
            })
        
        return event_type, event_data


def create_webhook_server_example() -> str:
    """
    Generate example code for a simple webhook server.
    
    Returns:
        Python code for a Flask-based webhook server
    """
    return '''
# Example Flask webhook server for AccuDoc
from flask import Flask, request, jsonify
import subprocess
import os
from accudoc.webhooks import GitHubWebhook, GitLabWebhook

app = Flask(__name__)

# Initialize webhook handlers
github_webhook = GitHubWebhook(secret=os.environ.get('GITHUB_WEBHOOK_SECRET'))
gitlab_webhook = GitLabWebhook(secret=os.environ.get('GITLAB_WEBHOOK_SECRET'))

# Register event handlers
def handle_push_event(payload):
    """Handle push events by regenerating documentation."""
    repo_path = payload.get('repository', '')
    branch = payload.get('branch', '')
    
    print(f"Push to {repo_path} on branch {branch}")
    
    # Run AccuDoc to regenerate documentation
    result = subprocess.run([
        'python', '/path/to/accudoc_cli.py', 'export',
        '/path/to/repo',
        '-o', '/path/to/output/README.md'
    ], capture_output=True, text=True)
    
    return {
        'documentation_updated': result.returncode == 0,
        'output': result.stdout
    }

def handle_pr_event(payload):
    """Handle pull request events."""
    print(f"PR #{payload.get('number')}: {payload.get('title')}")
    
    # Generate documentation for PR review
    # Implementation depends on your workflow
    return {'pr_documented': True}

# Register handlers
github_webhook.register_handler('push', handle_push_event)
github_webhook.register_handler('pull_request', handle_pr_event)
gitlab_webhook.register_handler('push', handle_push_event)
gitlab_webhook.register_handler('merge_request', handle_pr_event)

@app.route('/webhooks/github', methods=['POST'])
def github_webhook_endpoint():
    """GitHub webhook endpoint."""
    signature = request.headers.get('X-Hub-Signature-256', '')
    
    # Verify signature
    if not github_webhook.verify_github_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse event
    event_type, event_data = github_webhook.parse_github_event(
        dict(request.headers),
        request.json
    )
    
    # Process event
    result = github_webhook.process_event(event_type, event_data)
    
    return jsonify(result), 200

@app.route('/webhooks/gitlab', methods=['POST'])
def gitlab_webhook_endpoint():
    """GitLab webhook endpoint."""
    token = request.headers.get('X-Gitlab-Token', '')
    
    # Verify token
    if not gitlab_webhook.verify_gitlab_token(token):
        return jsonify({'error': 'Invalid token'}), 401
    
    # Parse event
    event_type, event_data = gitlab_webhook.parse_gitlab_event(
        dict(request.headers),
        request.json
    )
    
    # Process event
    result = gitlab_webhook.process_event(event_type, event_data)
    
    return jsonify(result), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''
