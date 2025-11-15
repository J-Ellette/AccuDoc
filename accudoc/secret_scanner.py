"""
Secret scanning module for AccuDoc.

Detects potentially sensitive information in documentation that should
not be exposed publicly.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SecretMatch:
    """Represents a detected secret."""
    secret_type: str
    line_number: int
    context: str  # Surrounding text
    confidence: str  # high, medium, low
    suggestion: str


class SecretScanner:
    """Scans documentation for potentially exposed secrets."""
    
    # Patterns for various secret types
    PATTERNS = {
        'aws_access_key': {
            'pattern': r'AKIA[0-9A-Z]{16}',
            'name': 'AWS Access Key ID',
            'confidence': 'high',
            'suggestion': 'Remove AWS access key and use environment variables or AWS IAM roles'
        },
        'aws_secret_key': {
            'pattern': r'aws_secret_access_key\s*=\s*["\']?([A-Za-z0-9/+=]{40})["\']?',
            'name': 'AWS Secret Access Key',
            'confidence': 'high',
            'suggestion': 'Remove AWS secret key and use environment variables'
        },
        'github_token': {
            'pattern': r'gh[pousr]_[A-Za-z0-9_]{36,255}',
            'name': 'GitHub Personal Access Token',
            'confidence': 'high',
            'suggestion': 'Remove GitHub token and use GitHub Actions secrets or environment variables'
        },
        'generic_api_key': {
            'pattern': r'(?i)(api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*["\']([A-Za-z0-9_\-]{20,})["\']',
            'name': 'Generic API Key',
            'confidence': 'medium',
            'suggestion': 'Replace with placeholder like "YOUR_API_KEY" or use environment variables'
        },
        'password': {
            'pattern': r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']',
            'name': 'Password',
            'confidence': 'medium',
            'suggestion': 'Remove password and use environment variables or secure credential storage'
        },
        'private_key': {
            'pattern': r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
            'name': 'Private Key',
            'confidence': 'high',
            'suggestion': 'Remove private key immediately - this should never be in documentation'
        },
        'jwt_token': {
            'pattern': r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
            'name': 'JWT Token',
            'confidence': 'high',
            'suggestion': 'Remove JWT token and use example tokens or placeholders'
        },
        'slack_token': {
            'pattern': r'xox[baprs]-[0-9a-zA-Z]{10,72}',
            'name': 'Slack Token',
            'confidence': 'high',
            'suggestion': 'Remove Slack token and use environment variables'
        },
        'stripe_key': {
            'pattern': r'(?i)(sk|pk)_(test|live)_[0-9a-zA-Z]{24,}',
            'name': 'Stripe API Key',
            'confidence': 'high',
            'suggestion': 'Remove Stripe key and use environment variables'
        },
        'google_api_key': {
            'pattern': r'AIza[0-9A-Za-z_-]{35}',
            'name': 'Google API Key',
            'confidence': 'high',
            'suggestion': 'Remove Google API key and use environment variables or Google Cloud Secret Manager'
        },
        'facebook_token': {
            'pattern': r'EAACEdEose0cBA[0-9A-Za-z]+',
            'name': 'Facebook Access Token',
            'confidence': 'high',
            'suggestion': 'Remove Facebook token and use environment variables'
        },
        'connection_string': {
            'pattern': r'(?i)(mongodb|mysql|postgres|postgresql)://[^:]+:[^@]+@[^/]+',
            'name': 'Database Connection String',
            'confidence': 'high',
            'suggestion': 'Remove connection string with credentials and use environment variables'
        },
        'email': {
            'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'name': 'Email Address',
            'confidence': 'low',
            'suggestion': 'Consider if email should be public or use placeholder'
        },
    }
    
    # Exclude patterns - things that look like secrets but aren't
    FALSE_POSITIVES = [
        r'example@example\.com',
        r'user@domain\.com',
        r'your-api-key',
        r'YOUR_API_KEY',
        r'<API_KEY>',
        r'\$\{.*\}',  # Environment variable placeholders
        r'xxx+',  # Multiple x's used as placeholder
        r'000+',  # Multiple zeros
    ]
    
    def scan(self, content: str) -> List[SecretMatch]:
        """
        Scan content for potential secrets.
        
        Args:
            content: Text content to scan
            
        Returns:
            List of detected secrets
        """
        matches = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip if line looks like a false positive
            if self._is_false_positive(line):
                continue
            
            # Check each pattern
            for secret_id, secret_info in self.PATTERNS.items():
                pattern = secret_info['pattern']
                for match in re.finditer(pattern, line):
                    # Get context (surrounding text)
                    start = max(0, match.start() - 20)
                    end = min(len(line), match.end() + 20)
                    context = line[start:end]
                    
                    matches.append(SecretMatch(
                        secret_type=secret_info['name'],
                        line_number=line_num,
                        context=context,
                        confidence=secret_info['confidence'],
                        suggestion=secret_info['suggestion']
                    ))
        
        return matches
    
    def _is_false_positive(self, text: str) -> bool:
        """Check if text matches false positive patterns."""
        for pattern in self.FALSE_POSITIVES:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def format_report(self, matches: List[SecretMatch]) -> str:
        """
        Format scan results as a readable report.
        
        Args:
            matches: List of detected secrets
            
        Returns:
            Formatted report string
        """
        if not matches:
            return "✓ No secrets detected in documentation"
        
        report = [
            "⚠️  SECURITY WARNING: Potential secrets detected in documentation",
            "=" * 70,
            ""
        ]
        
        # Group by confidence level
        high_confidence = [m for m in matches if m.confidence == 'high']
        medium_confidence = [m for m in matches if m.confidence == 'medium']
        low_confidence = [m for m in matches if m.confidence == 'low']
        
        if high_confidence:
            report.append("HIGH CONFIDENCE (likely secrets):")
            report.append("-" * 70)
            for i, match in enumerate(high_confidence, 1):
                report.append(f"\n{i}. {match.secret_type}")
                report.append(f"   Line {match.line_number}: ...{match.context}...")
                report.append(f"   → {match.suggestion}")
            report.append("")
        
        if medium_confidence:
            report.append("MEDIUM CONFIDENCE (review recommended):")
            report.append("-" * 70)
            for i, match in enumerate(medium_confidence, 1):
                report.append(f"\n{i}. {match.secret_type}")
                report.append(f"   Line {match.line_number}: ...{match.context}...")
                report.append(f"   → {match.suggestion}")
            report.append("")
        
        if low_confidence:
            report.append("LOW CONFIDENCE (informational):")
            report.append("-" * 70)
            for i, match in enumerate(low_confidence, 1):
                report.append(f"\n{i}. {match.secret_type}")
                report.append(f"   Line {match.line_number}: ...{match.context}...")
                report.append(f"   → {match.suggestion}")
            report.append("")
        
        report.extend([
            "=" * 70,
            f"Total: {len(matches)} potential secret(s) found",
            "",
            "RECOMMENDATIONS:",
            "1. Review each detected item carefully",
            "2. Remove actual secrets and regenerate documentation",
            "3. Use environment variables or secure credential storage",
            "4. Consider using placeholders like 'YOUR_API_KEY' in examples",
            "5. Add secrets to .gitignore to prevent future commits",
        ])
        
        return "\n".join(report)
    
    def get_summary(self, matches: List[SecretMatch]) -> Dict[str, int]:
        """
        Get summary statistics of detected secrets.
        
        Args:
            matches: List of detected secrets
            
        Returns:
            Dictionary with counts by confidence level
        """
        return {
            'total': len(matches),
            'high': len([m for m in matches if m.confidence == 'high']),
            'medium': len([m for m in matches if m.confidence == 'medium']),
            'low': len([m for m in matches if m.confidence == 'low']),
        }


def scan_documentation(documentation: str) -> Tuple[List[SecretMatch], str]:
    """
    Convenience function to scan documentation for secrets.
    
    Args:
        documentation: Documentation content to scan
        
    Returns:
        Tuple of (matches, formatted_report)
    """
    scanner = SecretScanner()
    matches = scanner.scan(documentation)
    report = scanner.format_report(matches)
    return matches, report


class SensitiveDataFilter:
    """Filter and redact sensitive information from documentation."""
    
    def __init__(self, redaction_strategy: str = 'mask'):
        """
        Initialize sensitive data filter.
        
        Args:
            redaction_strategy: Strategy for redaction ('mask', 'remove', 'placeholder')
                - mask: Replace with asterisks (e.g., '********')
                - remove: Remove the entire line
                - placeholder: Replace with descriptive placeholder
        """
        self.redaction_strategy = redaction_strategy
        self.scanner = SecretScanner()
    
    def filter_documentation(self, documentation: str, 
                           min_confidence: str = 'medium') -> Tuple[str, List[SecretMatch]]:
        """
        Filter sensitive data from documentation.
        
        Args:
            documentation: Documentation content to filter
            min_confidence: Minimum confidence level to redact ('high', 'medium', 'low')
            
        Returns:
            Tuple of (filtered_documentation, detected_secrets)
        """
        # Scan for secrets
        matches = self.scanner.scan(documentation)
        
        # Filter by confidence level
        confidence_order = {'high': 3, 'medium': 2, 'low': 1}
        min_level = confidence_order.get(min_confidence, 2)
        
        secrets_to_redact = [
            m for m in matches 
            if confidence_order.get(m.confidence, 0) >= min_level
        ]
        
        if not secrets_to_redact:
            return documentation, []
        
        # Apply redaction strategy
        filtered_doc = self._apply_redaction(documentation, secrets_to_redact)
        
        return filtered_doc, secrets_to_redact
    
    def _apply_redaction(self, content: str, matches: List[SecretMatch]) -> str:
        """Apply redaction strategy to content."""
        lines = content.split('\n')
        
        # Group matches by line number
        line_matches = {}
        for match in matches:
            if match.line_number not in line_matches:
                line_matches[match.line_number] = []
            line_matches[match.line_number].append(match)
        
        # Process each line with matches
        for line_num in sorted(line_matches.keys(), reverse=True):
            if 1 <= line_num <= len(lines):
                line_idx = line_num - 1
                line = lines[line_idx]
                
                if self.redaction_strategy == 'remove':
                    # Remove the entire line
                    lines[line_idx] = f"[REDACTED: Sensitive data removed]"
                
                elif self.redaction_strategy == 'mask':
                    # Mask secrets in the line
                    filtered_line = self._mask_secrets_in_line(line, line_matches[line_num])
                    lines[line_idx] = filtered_line
                
                elif self.redaction_strategy == 'placeholder':
                    # Replace with placeholder
                    filtered_line = self._replace_with_placeholder(line, line_matches[line_num])
                    lines[line_idx] = filtered_line
        
        return '\n'.join(lines)
    
    def _mask_secrets_in_line(self, line: str, matches: List[SecretMatch]) -> str:
        """Mask secrets in a line with asterisks."""
        # Find all secret patterns in the line
        for secret_id, secret_info in self.scanner.PATTERNS.items():
            pattern = secret_info['pattern']
            
            def mask_match(match):
                # Mask the secret part, keep some context
                secret = match.group(0)
                if len(secret) > 8:
                    # Show first 4 and last 4 characters, mask the middle
                    return secret[:4] + '*' * (len(secret) - 8) + secret[-4:]
                else:
                    return '*' * len(secret)
            
            line = re.sub(pattern, mask_match, line)
        
        return line
    
    def _replace_with_placeholder(self, line: str, matches: List[SecretMatch]) -> str:
        """Replace secrets with descriptive placeholders."""
        # Create a mapping of secret types to placeholders
        placeholders = {
            'AWS Access Key ID': '<YOUR_AWS_ACCESS_KEY>',
            'AWS Secret Access Key': '<YOUR_AWS_SECRET_KEY>',
            'GitHub Personal Access Token': '<YOUR_GITHUB_TOKEN>',
            'Generic API Key': '<YOUR_API_KEY>',
            'Password': '<YOUR_PASSWORD>',
            'Private Key': '<YOUR_PRIVATE_KEY>',
            'JWT Token': '<YOUR_JWT_TOKEN>',
            'Slack Token': '<YOUR_SLACK_TOKEN>',
            'Stripe API Key': '<YOUR_STRIPE_KEY>',
            'Google API Key': '<YOUR_GOOGLE_API_KEY>',
            'Facebook Access Token': '<YOUR_FACEBOOK_TOKEN>',
            'Database Connection String': '<YOUR_DATABASE_URL>',
            'Email Address': '<EMAIL_ADDRESS>',
        }
        
        # Replace secrets with placeholders
        for secret_id, secret_info in self.scanner.PATTERNS.items():
            pattern = secret_info['pattern']
            secret_name = secret_info['name']
            placeholder = placeholders.get(secret_name, '<REDACTED>')
            
            line = re.sub(pattern, placeholder, line)
        
        return line


def filter_sensitive_data(documentation: str, 
                         strategy: str = 'mask',
                         min_confidence: str = 'medium') -> Tuple[str, List[SecretMatch], str]:
    """
    Convenience function to filter sensitive data from documentation.
    
    Args:
        documentation: Documentation content to filter
        strategy: Redaction strategy ('mask', 'remove', 'placeholder')
        min_confidence: Minimum confidence level to redact ('high', 'medium', 'low')
        
    Returns:
        Tuple of (filtered_documentation, detected_secrets, report)
    """
    filter_obj = SensitiveDataFilter(redaction_strategy=strategy)
    filtered_doc, secrets = filter_obj.filter_documentation(documentation, min_confidence)
    
    # Generate report
    scanner = SecretScanner()
    report = scanner.format_report(secrets)
    
    return filtered_doc, secrets, report
