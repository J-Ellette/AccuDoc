"""
Email reporting system for AccuDoc.

Sends generated documentation via email with attachments and formatting.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
import json


@dataclass
class EmailConfig:
    """Email configuration."""
    
    smtp_host: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    from_email: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmailConfig':
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def load_from_file(cls, config_file: str) -> 'EmailConfig':
        """Load from JSON config file."""
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls.from_dict(data)
    
    def save_to_file(self, config_file: str):
        """Save to JSON config file."""
        data = {
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'username': self.username,
            'password': self.password,
            'use_tls': self.use_tls,
            'from_email': self.from_email
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


class EmailReporter:
    """
    Email reporter for AccuDoc.
    
    Sends documentation reports via email with optional attachments.
    """
    
    def __init__(self, config: EmailConfig):
        """
        Initialize email reporter.
        
        Args:
            config: Email configuration
        """
        self.config = config
        self.from_email = config.from_email or config.username
    
    def send_report(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        html_body: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send documentation report via email.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text email body
            attachments: Optional list of file paths to attach
            html_body: Optional HTML email body
            cc_emails: Optional CC recipients
            bcc_emails: Optional BCC recipients
            
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    self._add_attachment(msg, file_path)
            
            # Combine all recipients
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            # Send email
            context = ssl.create_default_context()
            
            if self.config.use_tls:
                with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.config.username, self.config.password)
                    server.sendmail(self.from_email, all_recipients, msg.as_string())
            else:
                with smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port, context=context) as server:
                    server.login(self.config.username, self.config.password)
                    server.sendmail(self.from_email, all_recipients, msg.as_string())
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """
        Add file attachment to email.
        
        Args:
            msg: Email message
            file_path: Path to file to attach
        """
        path = Path(file_path)
        if not path.exists():
            return
        
        # Read file
        with open(path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        
        # Encode
        encoders.encode_base64(part)
        
        # Add header
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {path.name}'
        )
        
        msg.attach(part)
    
    def send_documentation_report(
        self,
        to_emails: List[str],
        repo_name: str,
        doc_file: str,
        scan_summary: Optional[Dict] = None,
        include_attachment: bool = True
    ) -> bool:
        """
        Send formatted documentation report.
        
        Args:
            to_emails: Recipients
            repo_name: Repository name
            doc_file: Path to documentation file
            scan_summary: Optional scan summary data
            include_attachment: Whether to attach the documentation
            
        Returns:
            True if sent successfully
        """
        # Create subject
        subject = f"AccuDoc Report: {repo_name}"
        
        # Create plain text body
        body_lines = [
            f"Documentation Report for {repo_name}",
            "=" * 60,
            "",
            "A new documentation report has been generated.",
            ""
        ]
        
        if scan_summary:
            body_lines.append("Summary:")
            if 'total_files' in scan_summary:
                body_lines.append(f"  - Total files: {scan_summary['total_files']}")
            if 'languages' in scan_summary:
                body_lines.append(f"  - Languages: {', '.join(scan_summary['languages'])}")
            if 'dependencies' in scan_summary:
                body_lines.append(f"  - Dependencies: {len(scan_summary.get('dependencies', []))}")
            body_lines.append("")
        
        if include_attachment:
            body_lines.append("The full documentation is attached to this email.")
        else:
            body_lines.append(f"Documentation file: {doc_file}")
        
        body_lines.extend([
            "",
            "---",
            "Generated by AccuDoc - Automated Repository Documentation Generator"
        ])
        
        body = "\n".join(body_lines)
        
        # Create HTML body
        html_lines = [
            "<html>",
            "<head><style>",
            "body { font-family: Arial, sans-serif; line-height: 1.6; }",
            ".header { background: #4CAF50; color: white; padding: 20px; }",
            ".content { padding: 20px; }",
            ".summary { background: #f5f5f5; padding: 15px; border-left: 4px solid #4CAF50; }",
            ".footer { color: #666; font-size: 12px; margin-top: 30px; }",
            "</style></head>",
            "<body>",
            f"<div class='header'><h1>Documentation Report: {repo_name}</h1></div>",
            "<div class='content'>",
            "<p>A new documentation report has been generated.</p>"
        ]
        
        if scan_summary:
            html_lines.append("<div class='summary'>")
            html_lines.append("<h3>Summary</h3>")
            html_lines.append("<ul>")
            if 'total_files' in scan_summary:
                html_lines.append(f"<li><strong>Total files:</strong> {scan_summary['total_files']}</li>")
            if 'languages' in scan_summary:
                html_lines.append(f"<li><strong>Languages:</strong> {', '.join(scan_summary['languages'])}</li>")
            if 'dependencies' in scan_summary:
                html_lines.append(f"<li><strong>Dependencies:</strong> {len(scan_summary.get('dependencies', []))}</li>")
            html_lines.append("</ul>")
            html_lines.append("</div>")
        
        if include_attachment:
            html_lines.append("<p>The full documentation is attached to this email.</p>")
        else:
            html_lines.append(f"<p><strong>Documentation file:</strong> {doc_file}</p>")
        
        html_lines.extend([
            "<div class='footer'>",
            "<p>Generated by AccuDoc - Automated Repository Documentation Generator</p>",
            "</div>",
            "</div>",
            "</body>",
            "</html>"
        ])
        
        html_body = "\n".join(html_lines)
        
        # Send email
        attachments = [doc_file] if include_attachment else None
        
        return self.send_report(
            to_emails=to_emails,
            subject=subject,
            body=body,
            html_body=html_body,
            attachments=attachments
        )


# Preset configurations for common email providers
PRESET_CONFIGS = {
    'gmail': {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_tls': True
    },
    'outlook': {
        'smtp_host': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'use_tls': True
    },
    'yahoo': {
        'smtp_host': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'use_tls': True
    },
    'office365': {
        'smtp_host': 'smtp.office365.com',
        'smtp_port': 587,
        'use_tls': True
    }
}


def create_email_config(
    provider: str,
    username: str,
    password: str,
    from_email: Optional[str] = None
) -> EmailConfig:
    """
    Create email config using preset provider settings.
    
    Args:
        provider: Email provider (gmail, outlook, yahoo, office365)
        username: Email username
        password: Email password or app password
        from_email: Optional from email address
        
    Returns:
        EmailConfig instance
    """
    if provider not in PRESET_CONFIGS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PRESET_CONFIGS.keys())}")
    
    preset = PRESET_CONFIGS[provider]
    return EmailConfig(
        smtp_host=preset['smtp_host'],
        smtp_port=preset['smtp_port'],
        username=username,
        password=password,
        use_tls=preset['use_tls'],
        from_email=from_email
    )
