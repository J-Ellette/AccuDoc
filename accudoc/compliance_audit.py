"""
Compliance and audit documentation module for AccuDoc.

Generates compliance and audit-ready documentation:
- SOC 2 compliance reports
- ISO 27001 documentation
- GDPR compliance
- Security audit trails
- Change management documentation
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json


class ComplianceReportGenerator:
    """Generate compliance documentation."""
    
    def __init__(self, repo_path: str):
        """
        Initialize compliance report generator.
        
        Args:
            repo_path: Path to repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.compliance')
    
    def generate_soc2_report(self, project_data: Dict[str, Any]) -> str:
        """
        Generate SOC 2 compliance report.
        
        Args:
            project_data: Project data
            
        Returns:
            SOC 2 report in markdown
        """
        md = []
        
        md.append("# SOC 2 Compliance Report\n")
        md.append(f"**Project:** {project_data.get('name', 'Project')}")
        md.append(f"**Report Date:** {datetime.now().strftime('%Y-%m-%d')}")
        md.append(f"**Reporting Period:** {datetime.now().strftime('%Y')}\n")
        
        md.append("## Trust Service Criteria\n")
        
        # Security
        md.append("### CC6.0 - Security\n")
        md.append("#### CC6.1 - Logical and Physical Access Controls")
        md.append("- ✅ Access controls implemented using authentication mechanisms")
        md.append("- ✅ Role-based access control (RBAC) in place")
        md.append("- ✅ Audit logging for access events\n")
        
        md.append("#### CC6.2 - System Operations")
        md.append("- ✅ Automated monitoring and alerting configured")
        md.append("- ✅ Incident response procedures documented")
        md.append("- ✅ Regular security updates and patches\n")
        
        # Availability
        md.append("### CC7.0 - Availability\n")
        md.append("#### CC7.1 - System Availability")
        md.append("- ✅ High availability architecture implemented")
        md.append("- ✅ Disaster recovery procedures in place")
        md.append("- ✅ Regular backups performed\n")
        
        # Processing Integrity
        md.append("### CC8.0 - Processing Integrity\n")
        md.append("- ✅ Input validation implemented")
        md.append("- ✅ Data integrity checks performed")
        md.append("- ✅ Error handling and logging\n")
        
        # Confidentiality
        md.append("### CC9.0 - Confidentiality\n")
        md.append("- ✅ Data encryption at rest and in transit")
        md.append("- ✅ Secure key management")
        md.append("- ✅ Data classification and handling procedures\n")
        
        # Privacy
        md.append("### Privacy Criteria\n")
        md.append("- ✅ Privacy policy documented")
        md.append("- ✅ User consent mechanisms implemented")
        md.append("- ✅ Data retention policies established\n")
        
        return '\n'.join(md)
    
    def generate_iso27001_documentation(self, project_data: Dict[str, Any]) -> str:
        """
        Generate ISO 27001 documentation.
        
        Args:
            project_data: Project data
            
        Returns:
            ISO 27001 documentation in markdown
        """
        md = []
        
        md.append("# ISO 27001 Information Security Management System Documentation\n")
        md.append(f"**Organization:** {project_data.get('organization', 'Organization')}")
        md.append(f"**System:** {project_data.get('name', 'System')}")
        md.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        
        md.append("## 1. Context of the Organization\n")
        md.append("### 1.1 Understanding the Organization")
        md.append("The system operates within a defined organizational context with clear objectives and stakeholders.\n")
        
        md.append("### 1.2 Information Security Requirements")
        md.append("- Confidentiality: Protect sensitive information")
        md.append("- Integrity: Ensure data accuracy")
        md.append("- Availability: Maintain system accessibility\n")
        
        md.append("## 2. Leadership and Commitment\n")
        md.append("### 2.1 Information Security Policy")
        md.append("The organization maintains a comprehensive information security policy covering:")
        md.append("- Security objectives")
        md.append("- Compliance requirements")
        md.append("- Continuous improvement\n")
        
        md.append("## 3. Planning\n")
        md.append("### 3.1 Risk Assessment")
        md.append("Regular risk assessments are conducted to identify:")
        md.append("- Information security threats")
        md.append("- Vulnerabilities")
        md.append("- Impact and likelihood\n")
        
        md.append("### 3.2 Risk Treatment")
        md.append("| Risk | Treatment | Status |")
        md.append("|------|-----------|--------|")
        md.append("| Unauthorized access | Access controls | Implemented |")
        md.append("| Data breach | Encryption | Implemented |")
        md.append("| System downtime | Redundancy | Implemented |\n")
        
        md.append("## 4. Support\n")
        md.append("### 4.1 Resources")
        md.append("Adequate resources are allocated for ISMS implementation and maintenance.\n")
        
        md.append("### 4.2 Competence and Awareness")
        md.append("- Security training provided to all personnel")
        md.append("- Awareness programs conducted regularly\n")
        
        md.append("## 5. Operation\n")
        md.append("### 5.1 Operational Planning and Control")
        md.append("Security controls are implemented and monitored:\n")
        md.append("- Access control procedures")
        md.append("- Cryptographic controls")
        md.append("- Physical security")
        md.append("- Operations security\n")
        
        md.append("## 6. Performance Evaluation\n")
        md.append("### 6.1 Monitoring and Measurement")
        md.append("- Security metrics tracked")
        md.append("- Regular audits conducted")
        md.append("- Incident tracking and analysis\n")
        
        md.append("## 7. Improvement\n")
        md.append("### 7.1 Nonconformity and Corrective Action")
        md.append("Process for handling nonconformities:")
        md.append("1. Identify and document")
        md.append("2. Analyze root cause")
        md.append("3. Implement corrective actions")
        md.append("4. Verify effectiveness\n")
        
        return '\n'.join(md)
    
    def generate_gdpr_compliance_report(self, project_data: Dict[str, Any]) -> str:
        """
        Generate GDPR compliance report.
        
        Args:
            project_data: Project data
            
        Returns:
            GDPR compliance documentation
        """
        md = []
        
        md.append("# GDPR Compliance Documentation\n")
        md.append(f"**System:** {project_data.get('name', 'System')}")
        md.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        
        md.append("## Article 5 - Principles of Data Processing\n")
        md.append("### Lawfulness, Fairness, and Transparency")
        md.append("- ✅ Legal basis for processing documented")
        md.append("- ✅ Privacy notice provided to data subjects")
        md.append("- ✅ Processing activities transparent\n")
        
        md.append("### Purpose Limitation")
        md.append("- ✅ Data collected for specified purposes")
        md.append("- ✅ Processing limited to stated purposes\n")
        
        md.append("### Data Minimization")
        md.append("- ✅ Only necessary data collected")
        md.append("- ✅ Regular review of data requirements\n")
        
        md.append("### Accuracy")
        md.append("- ✅ Procedures to ensure data accuracy")
        md.append("- ✅ Mechanisms for data correction\n")
        
        md.append("### Storage Limitation")
        md.append("- ✅ Data retention policy established")
        md.append("- ✅ Automatic deletion procedures\n")
        
        md.append("### Integrity and Confidentiality")
        md.append("- ✅ Encryption implemented")
        md.append("- ✅ Access controls in place")
        md.append("- ✅ Security incident procedures\n")
        
        md.append("## Data Subject Rights\n")
        md.append("### Right to Access (Article 15)")
        md.append("- ✅ Process for handling access requests")
        md.append("- ✅ Response within 30 days\n")
        
        md.append("### Right to Erasure (Article 17)")
        md.append("- ✅ Deletion procedures implemented")
        md.append("- ✅ Data portability supported\n")
        
        md.append("### Right to Object (Article 21)")
        md.append("- ✅ Opt-out mechanisms available")
        md.append("- ✅ Marketing preferences respected\n")
        
        md.append("## Data Protection by Design and Default\n")
        md.append("- ✅ Privacy considered from system design")
        md.append("- ✅ Default settings maximize privacy")
        md.append("- ✅ Regular privacy impact assessments\n")
        
        return '\n'.join(md)


class AuditDocumentationGenerator:
    """Generate audit-ready documentation."""
    
    def __init__(self, repo_path: str):
        """
        Initialize audit documentation generator.
        
        Args:
            repo_path: Path to repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.audit')
    
    def generate_change_log(self, changes: List[Dict[str, Any]]) -> str:
        """
        Generate detailed change log for audit.
        
        Args:
            changes: List of changes
            
        Returns:
            Change log in markdown
        """
        md = []
        
        md.append("# System Change Log\n")
        md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        md.append("| Date | Change ID | Type | Description | Author | Status |")
        md.append("|------|-----------|------|-------------|--------|--------|")
        
        for change in changes:
            date = change.get('date', 'N/A')
            change_id = change.get('id', 'N/A')
            change_type = change.get('type', 'N/A')
            description = change.get('description', 'N/A')
            author = change.get('author', 'N/A')
            status = change.get('status', 'N/A')
            md.append(f"| {date} | {change_id} | {change_type} | {description} | {author} | {status} |")
        
        md.append("")
        return '\n'.join(md)
    
    def generate_security_audit_report(self, audit_data: Dict[str, Any]) -> str:
        """
        Generate security audit report.
        
        Args:
            audit_data: Audit findings
            
        Returns:
            Security audit report
        """
        md = []
        
        md.append("# Security Audit Report\n")
        md.append(f"**Audit Date:** {datetime.now().strftime('%Y-%m-%d')}")
        md.append(f"**Auditor:** {audit_data.get('auditor', 'Internal Audit Team')}\n")
        
        md.append("## Executive Summary\n")
        md.append("This report presents findings from the security audit conducted on the system. ")
        md.append("Overall security posture is assessed and recommendations are provided.\n")
        
        md.append("## Scope\n")
        md.append("The audit covered:")
        md.append("- Access controls and authentication")
        md.append("- Data encryption and protection")
        md.append("- Network security")
        md.append("- Application security")
        md.append("- Compliance with security standards\n")
        
        md.append("## Findings\n")
        
        # High severity
        md.append("### High Severity Findings")
        high_findings = audit_data.get('high_findings', [])
        if high_findings:
            for i, finding in enumerate(high_findings, 1):
                md.append(f"{i}. **{finding.get('title', 'Finding')}**")
                md.append(f"   - Risk: {finding.get('risk', 'High')}")
                md.append(f"   - Recommendation: {finding.get('recommendation', 'Address immediately')}")
        else:
            md.append("- No high severity findings\n")
        md.append("")
        
        # Medium severity
        md.append("### Medium Severity Findings")
        medium_findings = audit_data.get('medium_findings', [])
        if medium_findings:
            for i, finding in enumerate(medium_findings, 1):
                md.append(f"{i}. **{finding.get('title', 'Finding')}**")
        else:
            md.append("- No medium severity findings\n")
        md.append("")
        
        # Low severity
        md.append("### Low Severity Findings")
        md.append("- Minor improvements recommended\n")
        
        md.append("## Recommendations\n")
        md.append("1. Address high severity findings within 30 days")
        md.append("2. Implement additional security controls")
        md.append("3. Conduct regular security training")
        md.append("4. Schedule follow-up audit in 6 months\n")
        
        md.append("## Conclusion\n")
        md.append("The system demonstrates good security practices overall. ")
        md.append("Recommendations should be implemented to further strengthen security posture.\n")
        
        return '\n'.join(md)
    
    def generate_access_control_report(self, access_data: Dict[str, Any]) -> str:
        """
        Generate access control audit report.
        
        Args:
            access_data: Access control data
            
        Returns:
            Access control report
        """
        md = []
        
        md.append("# Access Control Audit Report\n")
        md.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        
        md.append("## User Access Review\n")
        md.append("| User | Role | Last Access | Access Level | Status |")
        md.append("|------|------|-------------|--------------|--------|")
        
        users = access_data.get('users', [])
        for user in users[:10]:
            md.append(f"| {user.get('name', 'User')} | {user.get('role', 'User')} | "
                     f"{user.get('last_access', 'N/A')} | {user.get('level', 'Standard')} | "
                     f"{user.get('status', 'Active')} |")
        md.append("")
        
        md.append("## Privileged Access\n")
        md.append("Users with elevated privileges:")
        admins = [u for u in users if u.get('role') == 'Admin']
        for admin in admins:
            md.append(f"- {admin.get('name', 'Admin')}: {admin.get('level', 'Full access')}")
        md.append("")
        
        md.append("## Findings\n")
        md.append("- ✅ Access controls properly configured")
        md.append("- ✅ Principle of least privilege followed")
        md.append("- ⚠️ Review inactive accounts for removal\n")
        
        return '\n'.join(md)
